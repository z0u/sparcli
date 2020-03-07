"""
stdio capturing mechanism.

    https://github.com/pytest-dev/pytest/blob/1df593f97890245a8eaaa89444a3ba7bada2a3b0/src/_pytest/capture.py
"""
import collections
import io
import os
import sys
from io import UnsupportedOperation
from tempfile import TemporaryFile
from typing import BinaryIO, Iterable


patchsysdict = {0: "stdin", 1: "stdout", 2: "stderr"}


def apply_workarounds(method: str):
    if method == "fd":
        _py36_windowsconsoleio_workaround(sys.stdout)
    _colorama_workaround()
    _readline_workaround()


def factory(method: str) -> "MultiCapture":
    if method == "fd":
        return MultiCapture(out=True, err=True, capture_factory=FDCapture)
    elif method == "sys":
        return MultiCapture(out=True, err=True, capture_factory=SysCapture)
    elif method == "no":
        return MultiCapture(out=False, err=False, in_=False)
    raise ValueError("unknown capturing method: {!r}".format(method))


def safe_text_dupfile(f, mode, default_encoding="UTF8"):
    """
    Return an open text file object that's a duplicate of f on the
    FD-level if possible.
    """
    encoding = getattr(f, "encoding", None)
    try:
        fd = f.fileno()
    except Exception:
        if "b" not in getattr(f, "mode", "") and hasattr(f, "encoding"):
            # we seem to have a text stream, let's just use it
            return f
    else:
        newfd = os.dup(fd)
        if "b" not in mode:
            mode += "b"
        f = os.fdopen(newfd, mode, 0)  # no buffering
    return EncodedFile(f, encoding or default_encoding)


class EncodedFile:
    errors = "strict"  # possibly needed by py3 code (issue555)

    def __init__(self, buffer: BinaryIO, encoding: str) -> None:
        self.buffer = buffer
        self.encoding = encoding

    def __repr__(self):
        return f"<EncodedFile buffer={self.buffer} encoding={self.encoding}>"

    def write(self, s: str) -> int:
        if not isinstance(s, str):
            raise TypeError(
                "write() argument must be str, not {}".format(type(s).__name__)
            )
        return self.buffer.write(s.encode(self.encoding, "replace"))

    def writelines(self, lines: Iterable[str]) -> None:
        self.buffer.writelines(x.encode(self.encoding, "replace") for x in lines)

    @property
    def name(self) -> str:
        """Ensure that file.name is a string."""
        return repr(self.buffer)

    @property
    def mode(self) -> str:
        return self.buffer.mode.replace("b", "")

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "buffer"), name)


CaptureResult = collections.namedtuple("CaptureResult", ["out", "err"])


class MultiCapture:
    out: "Capture"
    err: "Capture"
    in_: "Capture"
    _in_suspended: bool

    def __init__(self, out=True, err=True, in_=True, capture_factory=None):
        self.in_ = capture_factory(0) if in_ else NoCapture()
        self.out = capture_factory(1) if out else NoCapture()
        self.err = capture_factory(2) if err else NoCapture()
        self._in_suspended = False

    def __repr__(self):
        return "<MultiCapture out={!r} err={!r} in_={!r} _in_suspended={!r}>".format(
            self.out, self.err, self.in_, self._in_suspended,
        )

    def start(self):
        self.in_.start()
        self.out.start()
        self.err.start()

    def flush(self):
        self.out.write_immediately(self.out.snap())
        self.err.write_immediately(self.err.snap())

    def suspend(self, in_=False):
        self.out.suspend()
        self.err.suspend()
        if in_ and self.in_:
            self.in_.suspend()
            self._in_suspended = True

    def resume(self):
        self.out.resume()
        self.err.resume()
        if self._in_suspended:
            self.in_.resume()
            self._in_suspended = False

    def stop(self):
        self.out.done()
        self.err.done()
        self.in_.done()

    def write_out(self, data):
        self.out.write_immediately(data)


class Capture:
    def start(self):
        pass

    def done(self):
        pass

    def suspend(self):
        pass

    def resume(self):
        pass

    def snap(self):
        return b""


class NoCapture(Capture):
    pass


class FDCaptureBinary(Capture):
    """
    Capture IO to/from a given os-level filedescriptor.
    snap() produces `bytes`
    """

    def __init__(self, targetfd, tmpfile=None):
        self.targetfd = targetfd
        try:
            self.targetfd_save = os.dup(self.targetfd)
        except OSError:
            self.start = lambda: None
            self.done = lambda: None
        else:
            self.start = self._start
            self.done = self._done
            if targetfd == 0:
                assert not tmpfile, "cannot set tmpfile with stdin"
                tmpfile = open(os.devnull, "r")
                self.syscapture = SysCapture(targetfd)
            else:
                if tmpfile is None:
                    f = TemporaryFile()
                    with f:
                        tmpfile = safe_text_dupfile(f, mode="wb+")
                if targetfd in patchsysdict:
                    self.syscapture = SysCapture(targetfd, tmpfile)
                else:
                    self.syscapture = NoCapture()
            self.tmpfile = tmpfile
            self.tmpfile_fd = tmpfile.fileno()

    def __repr__(self):
        return "<{} {} oldfd={} tmpfile={}>".format(
            self.__class__.__name__,
            self.targetfd,
            getattr(self, "targetfd_save", "<UNSET>"),
            hasattr(self, "tmpfile") and repr(self.tmpfile) or "<UNSET>",
        )

    def _start(self):
        """ Start capturing on targetfd using memorized tmpfile. """
        try:
            os.fstat(self.targetfd_save)
        except (AttributeError, OSError):
            raise ValueError("saved filedescriptor not valid anymore")
        os.dup2(self.tmpfile_fd, self.targetfd)
        self.syscapture.start()

    def snap(self):
        # TODO: Lock file.
        self.tmpfile.seek(0)
        res = self.tmpfile.read()
        self.tmpfile.seek(0)
        self.tmpfile.truncate()
        return res

    def _done(self):
        # Stop capturing, restore streams.
        targetfd_save = self.__dict__.pop("targetfd_save")
        os.dup2(targetfd_save, self.targetfd)
        os.close(targetfd_save)
        self.syscapture.done()
        self.tmpfile.close()

    def suspend(self):
        self.syscapture.suspend()
        os.dup2(self.targetfd_save, self.targetfd)

    def resume(self):
        self.syscapture.resume()
        os.dup2(self.tmpfile_fd, self.targetfd)

    def write_immediately(self, data):
        if isinstance(data, str):
            data = data.encode("utf8")  # XXX use encoding of original stream
        os.write(self.targetfd_save, data)


class FDCapture(FDCaptureBinary):
    """
    Capture IO to/from a given os-level filedescriptor.
    snap() produces text.
    """

    def snap(self):
        res = super().snap()
        enc = getattr(self.tmpfile, "encoding", None)
        if enc and isinstance(res, bytes):
            res = str(res, enc, "replace")
        return res


class CaptureIO(io.TextIOWrapper):
    def __init__(self) -> None:
        super().__init__(io.BytesIO(), encoding="UTF-8", newline="", write_through=True)

    def getvalue(self) -> str:
        return self.buffer.getvalue().decode("UTF-8")


class SysCaptureBinary:
    def __init__(self, fd, tmpfile=None):
        name = patchsysdict[fd]
        self._old = getattr(sys, name)
        self.name = name
        if tmpfile is None:
            if name == "stdin":
                tmpfile = DontReadFromInput()
            else:
                tmpfile = CaptureIO()
        self.tmpfile = tmpfile

    def __repr__(self):
        return "<{} {} _old={} tmpfile={!r}>".format(
            self.__class__.__name__,
            self.name,
            hasattr(self, "_old") and repr(self._old) or "<UNSET>",
            self.tmpfile,
        )

    def start(self):
        setattr(sys, self.name, self.tmpfile)

    def snap(self):
        res = self.tmpfile.buffer.getvalue()
        self.tmpfile.seek(0)
        self.tmpfile.truncate()
        return res

    def done(self):
        setattr(sys, self.name, self._old)
        del self._old
        self.tmpfile.close()

    def suspend(self):
        setattr(sys, self.name, self._old)

    def resume(self):
        setattr(sys, self.name, self.tmpfile)

    def write_immediately(self, data):
        self._old.write(data)
        self._old.flush()


class SysCapture(SysCaptureBinary):
    def snap(self):
        res = self.tmpfile.getvalue()
        self.tmpfile.seek(0)
        self.tmpfile.truncate()
        return res


class DontReadFromInput:
    encoding = None

    def read(self, *args):
        raise IOError("read from stdin while output is captured")

    readline = read
    readlines = read
    __next__ = read

    def __iter__(self):
        return self

    def fileno(self):
        raise UnsupportedOperation("redirected stdin is pseudofile, has no fileno()")

    def isatty(self):
        return False

    def close(self):
        pass

    @property
    def buffer(self):
        return self


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
    and/or stdin if they have been redirected by the FDCapture mechanism.  This
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
    descriptors when doing ``FDCapture`` and this will ``CloseHandle`` the
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
