"""Facade over system calls to allow strict mocking."""
import ctypes as ctypes_
import os as os_
import sys as sys_


if os_.name == "nt":
    fcntl_ = None
    import ctypes.wintypes
    import msvcrt as msvcrt_
else:
    import fcntl as fcntl_
    msvcrt_ = None


class ctypes:
    byref = ctypes_.byref
    POINTER = getattr(ctypes_, "POINTER", None)
    WinError = getattr(ctypes_, "WinError", None)
    windll = getattr(ctypes_, "windll", None)
    wintypes = getattr(ctypes_, "wintypes", None)


class fcntl:
    fcntl = getattr(fcntl_, "fcntl", None)
    F_GETFL = getattr(fcntl_, "F_GETFL", None)
    F_SETFL = getattr(fcntl_, "F_SETFL", None)


class msvcrt:
    get_osfhandle = getattr(msvcrt_, "get_osfhandle", None)


class os:
    O_NONBLOCK = getattr(os_, "O_NONBLOCK", None)
    close = os_.close
    dup = os_.dup
    dup2 = os_.dup2
    name = os_.name
    pipe = os_.pipe
    read = os_.read
    write = os_.write


class sys:
    platform = sys_.platform
    stdin = sys_.stdin
    stdout = sys_.stdout
    stderr = sys_.stderr
    version_info = sys_.version_info

    if hasattr(sys_, "pypy_version_info"):
        pypy_version_info = sys_.pypy_version_info


# Hide implementation.
del ctypes_, fcntl_, msvcrt_, os_, sys_
