"""
stdio capturing mechanism.

    https://github.com/pytest-dev/pytest/blob/1df593f97890245a8eaaa89444a3ba7bada2a3b0/src/_pytest/capture.py
"""
import io
import os
import sys
from tempfile import TemporaryFile
from typing import IO, Optional


def apply_workarounds(method: str):
    if method == "fd":
        _py36_windowsconsoleio_workaround(sys.stdout)
    _colorama_workaround()
    _readline_workaround()


def factory(method: str) -> "MultiCapture":
    capture_factory = capture_factories[method]
    return MultiCapture(capture_factory("stdout"), capture_factory("stderr"))
    # return MultiCapture(capture_factory("stdout"), NoCapture())


def make_fd_capture(name: str):
    target_file = getattr(sys, name)
    capture_file = create_capture_file_for(target_file)
    return RedirectCapture(target_file, capture_file)


def make_null_capture(target_fd: int):
    return NoCapture(target_fd)


capture_factories = {
    "fd": make_fd_capture,
    "no": make_null_capture,
}


class MultiCapture:
    out: "Capture"
    err: "Capture"

    def __init__(self, out, err):
        self.out = out
        self.err = err

    def __repr__(self):
        return f"<MultiCapture out={self.out} err={self.err}>"

    def start(self):
        self.out.start()
        self.err.start()

    def close(self):
        self.out.close()
        self.err.close()

    def suspend(self, in_=False):
        self.out.suspend()
        self.err.suspend()

    def resume(self):
        self.out.resume()
        self.err.resume()

    def flush(self):
        self.out.flush()
        self.err.flush()

    def write_out(self, data):
        self.out.write_original(data)


class Capture:
    def start(self):
        pass

    def close(self):
        pass

    def suspend(self):
        pass

    def resume(self):
        pass

    def flush(self):
        pass

    def write_original(self, data):
        pass


class NoCapture(Capture):
    pass


def create_capture_file_for(target_file):
    newlines = target_file.newlines if hasattr(target_file, "newlines") else ""
    return TemporaryFile(
        target_file.mode if "+" in target_file.mode else target_file.mode + "+",
        encoding=target_file.encoding,
        newline=newlines,
    )


def dup_file(target_file):
    original_fd = os.dup(target_file.fileno())
    newlines = target_file.newlines if hasattr(target_file, "newlines") else ""
    return os.fdopen(
        original_fd,
        mode=target_file.mode,
        encoding=target_file.encoding,
        errors=target_file.errors,
        newline=newlines,
    )


class RedirectCapture(Capture):
    """
    Capture using OS-level file redirection.
    """

    target_file: IO
    original_file: Optional[IO]
    capture_file: IO

    def __init__(self, target_file, capture_file):
        self.target_file = target_file
        self.original_file = None
        self.capture_file = capture_file

    def __repr__(self):
        return f"<RedirectCapture {self.target_file.fileno()}>"

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        if self.original_file is not None:
            raise IOError(f"Already capturing {self}")
        self.original_file = dup_file(self.target_file)
        self.resume()

    def close(self):
        if self.original_file is None:
            raise IOError(f"Not capturing {self}")
        self.suspend()
        self.flush()
        self.original_file.close()
        self.original_file = None
        self.capture_file.close()

    def suspend(self):
        os.dup2(self.original_file.fileno(), self.target_file.fileno())

    def resume(self):
        os.dup2(self.capture_file.fileno(), self.target_file.fileno())

    def flush(self):
        self.capture_file.seek(0)
        data = self.capture_file.read()
        self.capture_file.seek(0)
        self.capture_file.truncate()
        self.original_file.write(data)

    def write_original(self, data):
        self.original_file.write(data)


def _colorama_workaround():
    """
    Ensure colorama is imported so that it attaches to the correct stdio
    handles on Windows.

    colorama uses the terminal on import time. So if something does the
    first import of colorama while I/O capture is active, colorama will
    fail in various ways.
    """
    if sys.platform.startswith("win32"):
        try:
            import colorama  # noqa: F401
        except ImportError:
            pass


def _readline_workaround():
    """
    Ensure readline is imported so that it attaches to the correct stdio
    handles on Windows.

    Pdb uses readline support where available--when not running from the Python
    prompt, the readline module is not imported until running the pdb REPL.

    This is a problem for pyreadline, which is often used to implement readline
    support on Windows, as it does not attach to the correct handles for stdout
    and/or stdin if they have been redirected by the RedirectCapture mechanism.  This
    workaround ensures that readline is imported before I/O capture is setup so
    that it can attach to the actual stdin/out for the console.

    See https://github.com/pytest-dev/pytest/pull/1281
    """
    if sys.platform.startswith("win32"):
        try:
            import readline  # noqa: F401
        except ImportError:
            pass


def _py36_windowsconsoleio_workaround(stream):
    """
    Python 3.6 implemented unicode console handling for Windows. This works
    by reading/writing to the raw console handle using
    ``{Read,Write}ConsoleW``.

    The problem is that we are going to ``dup2`` over the stdio file
    descriptors when doing ``RedirectCapture`` and this will ``CloseHandle`` the
    handles used by Python to write to the console. Though there is still some
    weirdness and the console handle seems to only be closed randomly and not
    on the first call to ``CloseHandle``, or maybe it gets reopened with the
    same handle value when we suspend capturing.

    The workaround in this case will reopen stdio with a different fd which
    also means a different handle by replicating the logic in
    "Py_lifecycle.c:initstdio/create_stdio".

    :param stream: in practice ``sys.stdout`` or ``sys.stderr``, but given
        here as parameter for unittesting purposes.

    See https://github.com/pytest-dev/py/issues/103
    """
    if (
        not sys.platform.startswith("win32")
        or sys.version_info[:2] < (3, 6)
        or hasattr(sys, "pypy_version_info")
    ):
        return

    # bail out if ``stream`` doesn't seem like a proper ``io`` stream (#2666)
    if not hasattr(stream, "buffer"):
        return

    buffered = hasattr(stream.buffer, "raw")
    raw_stdout = stream.buffer.raw if buffered else stream.buffer

    if not isinstance(raw_stdout, io._WindowsConsoleIO):
        return

    def _reopen_stdio(f, mode):
        if not buffered and mode[0] == "w":
            buffering = 0
        else:
            buffering = -1

        return io.TextIOWrapper(
            open(os.dup(f.fileno()), mode, buffering),
            f.encoding,
            f.errors,
            f.newlines,
            f.line_buffering,
        )

    sys.stdin = _reopen_stdio(sys.stdin, "rb")
    sys.stdout = _reopen_stdio(sys.stdout, "wb")
    sys.stderr = _reopen_stdio(sys.stderr, "wb")
