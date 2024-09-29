import contextlib
import logging
import queue
import threading
import time
from pathlib import Path
from typing import Literal

import arrow
from arrow.arrow import TZ_EXPR
from filelock import FileLock

RotateWhen = Literal['month', 'day', 'hour', 'minute', 'second']


class DayRotateHandlerWithThread(logging.Handler):
    def __init__(
        self,
        file_name: Path | str,
        backup_count: int = 0,
        mode: str = 'a',
        encoding='utf-8',
        time_zone: TZ_EXPR | None = None,
        when: RotateWhen = 'day',
        wait_time: float = 0.1,
    ):
        super().__init__()
        file_name = Path(file_name).absolute()
        self.file_path = file_name.parent
        self.file_stem = file_name.stem
        self.mode = mode
        self.backup_count = backup_count
        self.encoding = encoding
        self.time_zone = time_zone
        self.when = when
        self._init_time_format()
        self.wait_time = wait_time

        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.write_thread = threading.Thread(target=self._write_logs, daemon=True)
        self.write_thread.start()

    def _init_time_format(self):
        match self.when.lower():
            case 'month':
                self.time_format = 'YYYY-MM'
            case 'day':
                self.time_format = 'YYYY-MM-DD'
            case 'hour':
                self.time_format = 'YYYY-MM-DD-HH'
            case 'minute':
                self.time_format = 'YYYY-MM-DD-HH-mm'
            case 'second':
                self.time_format = 'YYYY-MM-DD-HH-mm-ss'
            case _:
                raise ValueError(f'Invalid when value: {self.when}')

    @property
    def _file_and_lock(self):
        file_name = f'{self.file_stem}.{arrow.now(tz=self.time_zone).format(self.time_format)}.log'
        return self.file_path / file_name, self.file_path / (file_name + '.lock')

    def emit(self, record: logging.LogRecord):
        self.queue.put(record)

    def _delete_old_logs(self):
        if self.backup_count <= 0:
            return

        log_files = []
        log_prefix = f'{self.file_stem}.'
        # 收集所有匹配的日志文件
        try:
            for file in self.file_path.iterdir():
                if file.is_file() and file.name.startswith(log_prefix) and file.suffix == '.log':
                    log_files.append(file)  # noqa: PERF401
        except OSError:
            return

        # 如果文件数量不超过备份数量，无需删除
        if len(log_files) <= self.backup_count:
            return

        # 按文件名排序（这里假设文件名中的日期/时间部分可以直接用于排序）
        log_files.sort(key=lambda x: x.name)

        # 删除最旧的文件，直到文件数量等于 backup_count
        for file in log_files[: -self.backup_count]:
            lock_file = file.with_name(file.name + '.lock')
            with contextlib.suppress(OSError):
                file.unlink()

            # 删除对应的锁文件
            if lock_file.exists():
                with contextlib.suppress(OSError):
                    lock_file.unlink()

    def _write_logs(self):
        while not self.stop_event.is_set() or not self.queue.empty():
            time.sleep(self.wait_time)
            self._delete_old_logs()
            if self.queue.empty():
                continue
            file_path, lock_file = self._file_and_lock
            with (
                FileLock(lock_file),
                file_path.open(self.mode, encoding=self.encoding) as file,
                contextlib.suppress(queue.Empty, OSError),
            ):
                while True:
                    file.write(self.format(self.queue.get_nowait()) + '\n')

    def flush(self):
        pass

    def close(self):
        self.stop_event.set()
        self.write_thread.join()
        super().close()

    def __del__(self):
        self.close()
