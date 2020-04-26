"""Facade over system calls to allow strict mocking."""
import ctypes as ctypes_
import fcntl as fcntl_
import os as os_
import sys as sys_

try:
    import msvcrt as msvcrt_
except ImportError:
    msvcrt_ = None


class ctypes:
    byref = ctypes_.byref
    try:
        WinError = ctypes_.WinError
        windll = ctypes_.windll
        wintypes = ctypes_.wintypes
    except AttributeError:
        WinError = None
        windll = None
        wintypes = None


class fcntl:
    fcntl = fcntl_.fcntl
    F_GETFL = fcntl_.F_GETFL
    F_SETFL = fcntl_.F_SETFL


class msvcrt:
    if msvcrt_:
        get_osfhandle = msvcrt_.get_osfhandle
    else:
        get_osfhandle = None


class os:
    O_NONBLOCK = os_.O_NONBLOCK
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
