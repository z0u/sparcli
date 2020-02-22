from contextlib import AbstractContextManager


class SparcliContext(AbstractContextManager):
    def __init__(self, event_queue):
        self.emit = event_queue.put

    def record(self, **variables):
        self.emit(("data_produced", self, variables))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.emit(("producer_stopped", self))
