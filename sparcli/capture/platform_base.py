class Platform:
    def set_nonblocking(self, read_fd):
        raise NotImplementedError(
            "Non-blocking capture not impelemented on this platform"
        )

    def apply_workarounds(self):
        pass
