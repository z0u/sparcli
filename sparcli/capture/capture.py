from .system import os


class Capture:
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError


class PipeCapture(Capture):
    BUFFER_SIZE = 4096

    def __init__(self, platform, target_fd: int):
        self.platform = platform
        self.target_fd = target_fd
        self.true_fd = target_fd
        self.pipe_out_fd = self.pipe_in_fd = None

    def start(self):
        if self.true_fd != self.target_fd:
            raise IOError(f"Already capturing FD {self.target_fd}")
        self.true_fd = os.dup(self.target_fd)
        self.pipe_out_fd, self.pipe_in_fd = os.pipe()
        self.platform.set_nonblocking(self.pipe_out_fd)
        os.dup2(self.pipe_in_fd, self.target_fd)

    def close(self):
        if self.true_fd == self.target_fd:
            raise IOError(f"Not capturing FD {self.target_fd}")
        os.dup2(self.true_fd, self.target_fd)
        os.close(self.pipe_in_fd)
        self.flush()
        os.close(self.true_fd)
        os.close(self.pipe_out_fd)
        self.true_fd = self.target_fd
        self.pipe_out_fd = self.pipe_in_fd = None

    def flush(self):
        while True:
            try:
                data = os.read(self.pipe_out_fd, self.BUFFER_SIZE)
            except BlockingIOError:
                break
            if not data:
                break
            os.write(self.true_fd, data)

    def write(self, data):
        if isinstance(data, str):
            data = data.encode("utf8")
        os.write(self.true_fd, data)


class NoCapture(Capture):
    def __init__(self, target_fd):
        self.target_fd = target_fd

    def start(self):
        pass

    def close(self):
        pass

    def flush(self):
        pass

    def write(self, data):
        os.write(self.target_fd, data)


class MultiCapture:
    def __init__(self, out_cap, err_cap):
        self.out_cap = out_cap
        self.err_cap = err_cap

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        self.out_cap.start()
        self.err_cap.start()

    def close(self):
        self.out_cap.close()
        self.err_cap.close()

    def flush(self):
        self.out_cap.flush()
        self.err_cap.flush()

    def write_out(self, data):
        self.out_cap.write(data)

    def write_err(self, data):
        self.err_cap.write(data)
