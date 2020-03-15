import os

from . import capture

if os.name == "nt":
    from . import windows as platform
elif os.name == "posix":
    from . import posix as platform
else:
    platform = None


__all__ = ["init", "make_multi_capture"]


def init():
    if platform:
        platform.apply_workarounds()


def make_multi_capture(stdout: bool, stderr: bool) -> capture.MultiCapture:
    out_cap = make_capture("stdout", "pipe" if stdout else "none")
    err_cap = make_capture("stderr", "pipe" if stderr else "none")
    return capture.MultiCapture(out_cap, err_cap)


def make_capture(stream_name: str, method: str):
    file_descriptor = {"stdout": 1, "stderr": 2}[stream_name]
    if method == "pipe":
        if not platform:
            raise NotImplementedError(f"Can't capture {stream_name} on this platform")
        return capture.PipeCapture(platform, file_descriptor)
    return capture.NoCapture(file_descriptor)
