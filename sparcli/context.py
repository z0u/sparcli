class SparcliContext:
    def __init__(self, event_queue):
        self.emit = event_queue.append

    def record(self, **variables):
        self.emit(("data_produced", self, variables))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.close()

    def close(self):
        self.emit(("producer_stopped", self))
