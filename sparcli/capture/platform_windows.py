"""
set_nonblocking: CC BY-SA 4.0
Copyright (c) 2015 Anatoly Techtonik, HarryJohnston
https://stackoverflow.com/a/34504971/320036

apply_workarounds: MIT
Copyright (c) 2004-2020 Holger Krekel and others
https://github.com/pytest-dev/pytest/blob/1df593f97890245a8eaaa89444a3ba7bada2a3b0/src/_pytest/capture.py
"""
import io

from .system import ctypes, msvcrt, os, sys
from .platform_base import Platform


class WindowsPlatform(Platform):
    def set_nonblocking(self, read_fd: int):
        lpword = ctypes.wintypes.POINTER(ctypes.wintypes.DWORD)
        pipe_nowait = ctypes.wintypes.DWORD(0x00000001)

        SetNamedPipeHandleState = ctypes.windll.kernel32.SetNamedPipeHandleState
        SetNamedPipeHandleState.argtypes = [
            ctypes.wintypes.HANDLE,
            lpword,
            lpword,
            lpword,
        ]
        SetNamedPipeHandleState.restype = ctypes.wintypes.BOOL
        handle = msvcrt.get_osfhandle(read_fd)
        res = ctypes.windll.kernel32.SetNamedPipeHandleState(
            handle, ctypes.byref(pipe_nowait), None, None
        )
        if res == 0:
            error: IOError = ctypes.WinError()
            raise error

    def apply_workarounds(self):  # pragma: no-cover
        _py36_windowsconsoleio_workaround(sys.stdout)
        _colorama_workaround()
        _readline_workaround()


def _colorama_workaround():  # pragma: no-cover
    """
    Ensure colorama is imported so that it attaches to the correct stdio
    handles on Windows.

    colorama uses the terminal on import time. So if something does the
    first import of colorama while I/O capture is active, colorama will
    fail in various ways.
    """
    try:
        import colorama  # noqa: F401
    except ImportError:
        pass


def _readline_workaround():  # pragma: no-cover
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
    try:
        import readline  # noqa: F401
    except ImportError:
        pass


def _py36_windowsconsoleio_workaround(stream):  # pragma: no-cover
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
    if sys.version_info[:2] < (3, 6) or hasattr(sys, "pypy_version_info"):
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
