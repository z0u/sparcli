from .system import fcntl, os
from .platform_base import Platform


class PosixPlatform(Platform):
    def set_nonblocking(self, read_fd):
        old_flags = fcntl.fcntl(read_fd, fcntl.F_GETFL)
        fcntl.fcntl(read_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
