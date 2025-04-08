import contextlib
import linecache
import logging
import os
import queue
import shutil
import sys
import threading
import time
import warnings
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, TextIO

import arrow
import structlog
from filelock import AcquireReturnProxy, FileLock, Timeout
from rich.columns import Columns
from rich.console import Console, ConsoleRenderable, RenderResult, group
from rich.scope import render_scope
from rich.syntax import Syntax
from rich.text import Text
from rich.traceback import Frame, PathHighlighter, Stack, Traceback

from utils.msgspec import msgspec_jsoner


class LogMsgspecJsonRenderer:
    def __call__(self, logger, name: str, event_dict: dict[str, Any]) -> str:  # noqa: ARG002
        return msgspec_jsoner.encode(event_dict).decode('utf-8')


# ---------------- Rich Exception Formatter ----------------
type EXC_INFO = tuple[type[BaseException], BaseException, TracebackType]
type ColorSystem = Literal['auto', 'standard', '256', 'truecolor', 'windows']


class ClanTraceback(Traceback):
    @group()
    def _render_stack(self, stack: Stack) -> RenderResult:
        path_highlighter = PathHighlighter()
        theme = self.theme

        def read_code(filename: str) -> str:
            return ''.join(linecache.getlines(filename))

        def render_locals(_frame: Frame) -> Iterable[ConsoleRenderable]:
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

            if os.path.exists(frame.filename):  # noqa: PTH110
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
    max_frames: int = 100
    width: int | None = None

    def __call__(self, sio: TextIO, exc_info: EXC_INFO) -> None:
        if self.width is None:
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


def _init_time_format(when: RotateWhen):
    match when.lower():
        case 'month':
            return 'YYYY-MM'
        case 'day':
            return 'YYYY-MM-DD'
        case 'hour':
            return 'YYYY-MM-DD-HH'
        case 'minute':
            return 'YYYY-MM-DD-HH-mm'
        case 'second':
            return 'YYYY-MM-DD-HH-mm-ss'
        case _:
            raise ValueError(f'Invalid when value: {when}')


class SharedThreadedTimeRotatingHandler(logging.Handler):
    # 共享线程对象
    _shared_thread: threading.Thread | None = None
    # 存储所有处理器实例的集合
    _handlers: set['SharedThreadedTimeRotatingHandler'] = set()
    _handlers_lock: threading.Lock = threading.Lock()
    # 停止事件，用于控制线程的停止
    _stop_event = threading.Event()
    # 线程等待时间
    _wait_time = 0.1

    def __init__(
        self,
        file_name: Path | str,
        backup_count: int = 0,
        mode: str = 'a',
        encoding='utf-8',
        time_zone: arrow.arrow.TZ_EXPR | None = None,
        when: RotateWhen = 'day',
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
        self.time_format = _init_time_format(when)
        self.queue = queue.SimpleQueue()

        # 将当前实例添加到处理器集合中
        with self.__class__._handlers_lock:
            self.__class__._handlers.add(self)

    def __str__(self):
        return f'<{self.__class__.__name__} {self.file_stem}>'

    def __repr__(self):
        return str(self)

    def __hash__(self) -> int:
        # 使用对象的id作为哈希值
        return hash(id(self))

    @classmethod
    def _new_thread(cls):
        # 创建并启动新的共享线程
        cls._stop_event.clear()
        cls._shared_thread = threading.Thread(
            target=cls._write_logs_wrapper,
            daemon=True,
        )
        cls._shared_thread.start()

    @classmethod
    def _write_logs_wrapper(cls):
        # 包装写日志方法，减少缩进
        while not cls._stop_event.is_set():
            time.sleep(cls._wait_time)
            with cls._handlers_lock:
                cls._write_logs()

    @classmethod
    def _write_logs(cls):
        # 主要的日志写入逻辑
        for handler in cls._handlers:
            try:
                handler.delete_old_logs()
                if handler.queue.empty():
                    continue
                file_path, lock_file = handler.file_and_lock
                with (
                    FileLockWithoutLog(lock_file, timeout=cls._wait_time * 10),
                    file_path.open(handler.mode, encoding=handler.encoding) as file,
                    contextlib.suppress(queue.Empty, OSError),
                ):
                    while True:
                        file.write(handler.format(handler.queue.get_nowait()) + '\n')
            except Exception:
                print(sys.exc_info())
                handler.log_exception(sys.exc_info())

    @classmethod
    def _check_thread(cls):
        # 检查并确保共享线程正在运行
        if not cls._shared_thread or not cls._shared_thread.is_alive():
            cls._new_thread()

    @property
    def file_and_lock(self):
        # 获取当前日志文件和对应的锁文件路径
        file_name = f'{self.file_stem}.{arrow.now(tz=self.time_zone).format(self.time_format)}.log'
        return self.file_path / file_name, self.file_path / f'.{file_name}.lock'

    def emit(self, record: logging.LogRecord):
        # 发射日志记录到队列
        if isinstance(record.msg, dict) and record.msg.get('exc_info') is True:
            record.msg['exc_info'] = sys.exc_info()
        self.queue.put(record)
        self._check_thread()

    def log_exception(self, exc_info):
        # 记录异常信息到单独的错误日志文件
        error_log_file = self.file_path / f'_log.{arrow.now().format(self.time_format)}.log'
        lock_file = error_log_file.with_name(f'.{error_log_file.name}.lock')
        with (
            FileLockWithoutLog(lock_file),
            error_log_file.open('a', encoding='utf-8') as file,
            contextlib.suppress(OSError),
        ):
            file.write(
                f'{arrow.now(tz=self.time_zone).format("YYYY-MM-DD HH:mm:ss")} '
                f'handler {self.file_and_lock[0]} 写入异常\n',
            )
            format_exception_to_io(file, exc_info)

    def delete_old_logs(self):
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

    def close(self):
        # 关闭处理器，等待队列清空并从处理器集合中移除
        while self in self.__class__._handlers and not self.queue.empty():
            time.sleep(0.1)
        if self in self.__class__._handlers:
            with self.__class__._handlers_lock:
                self.__class__._handlers.remove(self)
        if not self.__class__._handlers:
            self.__class__._stop_event.set()
        super().close()

    def __del__(self):
        self.close()


# ---------------- FileLockWithoutLog ----------------
# 删除可能造成死锁的日志调用
class FileLockWithoutLog(FileLock):
    def acquire(
        self,
        timeout: float | None = None,
        poll_interval: float = 0.05,
        *,
        poll_intervall: float | None = None,
        blocking: bool | None = None,
    ) -> AcquireReturnProxy:
        if timeout is None:
            timeout = self._context.timeout

        if blocking is None:
            blocking = self._context.blocking

        if poll_intervall is not None:
            msg = 'use poll_interval instead of poll_intervall'
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            poll_interval = poll_intervall

        # Increment the number right at the beginning. We can still undo it, if something fails.
        self._context.lock_counter += 1

        lock_filename = self.lock_file
        start_time = time.perf_counter()
        try:
            while True:
                if not self.is_locked:
                    self._acquire()
                if self.is_locked:
                    break
                if blocking is False:
                    raise Timeout(lock_filename)  # noqa: TRY301
                if 0 <= timeout < time.perf_counter() - start_time:
                    raise Timeout(lock_filename)  # noqa: TRY301
                time.sleep(poll_interval)
        except BaseException:  # Something did go wrong, so decrement the counter.
            self._context.lock_counter = max(0, self._context.lock_counter - 1)
            raise
        return AcquireReturnProxy(lock=self)

    def release(self, force: bool = False) -> None:
        if self.is_locked:
            self._context.lock_counter -= 1
            if self._context.lock_counter == 0 or force:
                self._release()
                self._context.lock_counter = 0
