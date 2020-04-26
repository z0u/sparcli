from . import capture
from . import platform_posix
from . import platform_windows
from .system import os


__all__ = ["init", "make_multi_capture"]


def init():
    get_platform().apply_workarounds()


def make_multi_capture(stdout: bool, stderr: bool) -> capture.MultiCapture:
    out_cap = make_capture("stdout", "pipe" if stdout else "none")
    err_cap = make_capture("stderr", "pipe" if stderr else "none")
    return capture.MultiCapture(out_cap, err_cap)


def make_capture(stream_name: str, method: str):
    file_descriptor = {"stdout": 1, "stderr": 2}[stream_name]
    if method == "pipe":
        return capture.PipeCapture(get_platform(), file_descriptor)
    elif method == "none":
        return capture.NoCapture(file_descriptor)
    raise ValueError(f"No such capture method {method}")


def get_platform():
    if os.name == "nt":
        return platform_windows.WindowsPlatform()
    elif os.name == "posix":
        return platform_posix.PosixPlatform()
    raise NotImplementedError(f"Unsupported platform: {os.name}")
