import fcntl
import os


def set_nonblocking(read_fd):
    old_flags = fcntl.fcntl(read_fd, fcntl.F_GETFL)
    fcntl.fcntl(read_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)


def apply_workarounds():
    pass
