from collections import defaultdict, deque
import threading
import time

import sparcli.data


class Controller(threading.Thread):
    def __init__(self, renderer):
        super().__init__(daemon=True)
        self.event_queue = deque()
        self.renderer = renderer
        self.variables = defaultdict(lambda: Variable())

    def stop(self):
        self.event_queue.append(("stopped",))

    def run(self):
        while True:
            try:
                event = self.event_queue.popleft()
                topic = event[0]
                data = event[1:]
            except IndexError:
                time.sleep(0.1)
                topic = None
                data = tuple()

            if topic is None:
                pass
            elif topic == "data_produced":
                self.data_produced(*data)
            elif topic == "producer_stopped":
                self.producer_stopped(*data)
            elif topic == "stopped":
                self.renderer.clear()
                break
            else:  # pragma: no-cover
                raise ValueError(f"Unknown event {topic}")

            self.renderer.draw(self.variables)

    def data_produced(self, producer, variables: dict):
        for name, value in variables.items():
            variable = self.variables[name]
            variable.reference(producer)
            variable.series.add(value)

    def producer_stopped(self, producer):
        for variable in self.variables.values():
            variable.dereference(producer)
        self.garbage_collect()

    def garbage_collect(self):
        self.variables = defaultdict(
            Variable,
            {
                name: variable
                for name, variable in self.variables.items()
                if variable.is_live
            },
        )


class Variable:
    def __init__(self):
        self.references = set()
        self._series = sparcli.data.CompactingSeries(30)

    @property
    def series(self):
        return self._series

    @property
    def is_live(self):
        return len(self.references) > 0

    def reference(self, reference):
        self.references.add(reference)

    def dereference(self, reference):
        self.references.discard(reference)
