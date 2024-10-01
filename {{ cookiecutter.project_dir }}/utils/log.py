import contextlib
import linecache
import logging
import os
import queue
import shutil
import sys
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, TextIO

import arrow
import msgspec
import rich
import structlog
from filelock import FileLock
from rich.columns import Columns
from rich.console import Console, ConsoleRenderable, RenderResult, group
from rich.scope import render_scope
from rich.syntax import Syntax
from rich.text import Text
from rich.traceback import Traceback


class LogMsgspecJsonRenderer:
    def __call__(self, logger, name: str, event_dict: dict[str, Any]) -> str:  # noqa: ARG002
        return msgspec.json.encode(event_dict).decode('utf-8')


# ---------------- Rich Exception Formatter ----------------

type EXC_INFO = tuple[type[BaseException], BaseException, TracebackType]
type ColorSystem = Literal['auto', 'standard', '256', 'truecolor', 'windows']


class ClanTraceback(Traceback):
    @group()
    def _render_stack(self, stack: rich.traceback.Stack) -> RenderResult:  # type: ignore
        path_highlighter = rich.traceback.PathHighlighter()  # type: ignore
        theme = self.theme

        def read_code(filename: str) -> str:
            """Read files, and cache results on filename.

            Args:
                filename (str): Filename to read

            Returns:
                str: Contents of file
            """
            return ''.join(linecache.getlines(filename))

        def render_locals(_frame: rich.traceback.Frame) -> Iterable[ConsoleRenderable]:  # type: ignore
            if _frame.locals:
                yield render_scope(
                    _frame.locals,
                    title='locals',
                    indent_guides=self.indent_guides,
                    max_length=self.locals_max_length,
                    max_string=self.locals_max_string,
                )

        exclude_frames: range | None = None
        if self.max_frames != 0:
            exclude_frames = range(len(stack.frames) - self.max_frames + 1)

        excluded = False
        for frame_index, frame in enumerate(stack.frames):
            if exclude_frames and frame_index in exclude_frames:
                excluded = True
                continue

            if excluded:
                assert exclude_frames is not None
                yield Text(
                    f'\n... {len(exclude_frames)} frames hidden ...',
                    justify='center',
                    style='traceback.error',
                )
                excluded = False

            first = frame_index == 0
            frame_filename = frame.filename
            suppressed = any(frame_filename.startswith(path) for path in self.suppress)

            if os.path.exists(frame.filename):
                text = Text.assemble(
                    path_highlighter(Text(frame.filename, style='pygments.string')),
                    (':', 'pygments.text'),
                    (str(frame.lineno), 'pygments.number'),
                    ' in ',
                    (frame.name, 'pygments.function'),
                    style='pygments.text',
                )
            else:
                text = Text.assemble(
                    'in ',
                    (frame.name, 'pygments.function'),
                    (':', 'pygments.text'),
                    (str(frame.lineno), 'pygments.number'),
                    style='pygments.text',
                )
            if not frame.filename.startswith('<') and not first:
                yield ''
            yield text
            if frame.filename.startswith('<'):
                yield from render_locals(frame)
                continue
            if not suppressed:
                try:
                    code = read_code(frame.filename)
                    if not code:
                        # code may be an empty string if the file doesn't exist, OR
                        # if the traceback filename is generated dynamically
                        continue
                    lexer_name = self._guess_lexer(frame.filename, code)
                    syntax = Syntax(
                        code,
                        lexer_name,
                        theme=theme,
                        line_numbers=True,
                        line_range=(
                            frame.lineno - self.extra_lines,
                            frame.lineno + self.extra_lines,
                        ),
                        highlight_lines={frame.lineno},
                        word_wrap=self.word_wrap,
                        code_width=self.code_width,
                        indent_guides=self.indent_guides,
                        dedent=False,
                    )
                    yield ''
                except Exception as error:
                    yield Text.assemble(
                        (f'\n{error}', 'traceback.error'),
                    )
                else:
                    yield (
                        Columns(
                            [
                                syntax,
                                *render_locals(frame),
                            ],
                            padding=1,
                        )
                        if frame.locals
                        else syntax
                    )


@dataclass
class ClanRichTracebackFormatter(structlog.dev.RichTracebackFormatter):
    color_system: ColorSystem = 'auto'
    highlight: bool = False
    max_frames: int = 3

    def __call__(self, sio: TextIO, exc_info: EXC_INFO) -> None:  # type: ignore
        if self.width == -1:
            self.width, _ = shutil.get_terminal_size((80, 0))

        sio.write('\n')
        Console(
            file=sio,
            color_system=self.color_system,
            width=self.width,
            highlight=self.highlight,
        ).print(
            ClanTraceback.from_exception(
                *exc_info,
                show_locals=self.show_locals,
                max_frames=self.max_frames,
                theme=self.theme,
                word_wrap=self.word_wrap,
                extra_lines=self.extra_lines,
                width=self.width,
                indent_guides=self.indent_guides,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                locals_hide_dunder=self.locals_hide_dunder,
                locals_hide_sunder=self.locals_hide_sunder,
                suppress=self.suppress,
            ),
        )


# ---------------- Log Handler ----------------

type RotateWhen = Literal['month', 'day', 'hour', 'minute', 'second']
format_exception_to_io = ClanRichTracebackFormatter()


class ThreadedTimeRotatingHandler(logging.Handler):
    def __init__(
        self,
        file_name: Path | str,
        backup_count: int = 0,
        mode: str = 'a',
        encoding='utf-8',
        time_zone: arrow.arrow.TZ_EXPR | None = None,
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

        self.queue = queue.SimpleQueue()
        self.exception_queue = queue.SimpleQueue()
        self.stop_event = threading.Event()
        self._new_thread()

    def __str__(self):
        return f'<{self.__class__.__name__} {self.file_stem}>'

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

    def _new_thread(self):
        self.write_thread = threading.Thread(target=self._write_logs_wrapper, daemon=True)
        self.write_thread.start()

    @property
    def _file_and_lock(self):
        file_name = f'{self.file_stem}.{arrow.now(tz=self.time_zone).format(self.time_format)}.log'
        return self.file_path / file_name, self.file_path / f'.{file_name}.lock'

    def emit(self, record: logging.LogRecord):
        if isinstance(record.msg, dict) and record.msg.get('exc_info') is True:
            record.msg['exc_info'] = sys.exc_info()
        self.queue.put(record)
        self._check_thread()

    def _log_exception(self, exc_info):
        error_log_file = self.file_path / f'_log.{arrow.now().format(self.time_format)}.log'
        lock_file = error_log_file.with_name(f'.{error_log_file.name}.lock')
        with (
            FileLock(lock_file),
            error_log_file.open('a', encoding='utf-8') as file,
            contextlib.suppress(OSError),
        ):
            file.write(f"{arrow.now(tz=self.time_zone).format('YYYY-MM-DD HH:mm:ss')} log handler 写入线程异常\n")
            format_exception_to_io(file, exc_info)

    def _check_thread(self):
        if not self.write_thread.is_alive():
            with contextlib.suppress(queue.Empty):
                while True:
                    exception_info = self.exception_queue.get_nowait()
                    self._log_exception(exception_info)
            self.stop_event.clear()  # noqa
            self._new_thread()

    def _delete_old_logs(self):
        def unlink_paths(paths: list[Path]):
            for path in paths:
                with contextlib.suppress(OSError):
                    path.unlink()

        # 删除过时的锁文件
        lock_files = list(self.file_path.glob(f'.{self.file_stem}.*.log.lock'))
        if len(lock_files) > 1:
            lock_files.sort(key=lambda x: x.name)
            unlink_paths(lock_files[:-1])

        if self.backup_count <= 0:
            return

        # 收集所有匹配的日志文件
        log_files = list(self.file_path.glob(f'{self.file_stem}.*.log'))
        # 如果文件数量不超过备份数量，无需删除
        if len(log_files) > self.backup_count:
            # 按文件名排序（这里假设文件名中的日期/时间部分可以直接用于排序）
            log_files.sort(key=lambda x: x.name)

            # 删除最旧的文件，直到文件数量等于 backup_count
            unlink_paths(log_files[: -self.backup_count])

    def _write_logs_wrapper(self):
        try:
            self._write_logs()
        except Exception:  # noqa
            self.exception_queue.put(sys.exc_info())

    def _write_logs(self):
        while not self.stop_event.is_set() or not self.queue.empty():
            try:
                time.sleep(self.wait_time)
                self._delete_old_logs()
                if self.queue.empty():
                    continue
                file_path, lock_file = self._file_and_lock
                with (
                    FileLock(lock_file, timeout=5),
                    file_path.open(self.mode, encoding=self.encoding) as file,
                    contextlib.suppress(queue.Empty, OSError),
                ):
                    while True:
                        file.write(self.format(self.queue.get_nowait()) + '\n')
            except Exception:
                self._log_exception(sys.exc_info())

    def flush(self):
        pass

    def close(self):
        self.stop_event.set()
        self.write_thread.join()
        super().close()

    def __del__(self):
        self.close()
