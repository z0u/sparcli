from collections import defaultdict
from contextlib import AbstractContextManager
import queue
import threading

from . import data


try:
    Queue = queue.SimpleQueue
except AttributeError:
    Queue = queue.Queue


class Sparcli(AbstractContextManager):
    def __init__(self, event_queue):
        self.emit = event_queue.put

    def record(self, **variables):
        self.emit(("data_produced", self, variables))

    def register(self):
        pass

    def unregister(self):
        self.emit(("producer_stopped", self))

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.unregister()


class Variable:
    def __init__(self):
        self.references = set()
        self.series = data.CompactingSeries(30)

    @property
    def is_live(self):
        return len(self.references) > 0

    def reference(self, reference):
        self.references.add(reference)

    def dereference(self, reference):
        self.references.discard(reference)


class Controller(threading.Thread):
    def __init__(self, renderer):
        super().__init__(daemon=True)
        self.event_queue = Queue()
        self.renderer = renderer
        self.variables = defaultdict(Variable)

    def stop(self):
        self.event_queue.put(("stopped",))

    def run(self):
        while True:
            try:
                event = self.event_queue.get(timeout=0.1)
                topic = event[0]
                data = event[1:]
            except queue.Empty:
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
            else:
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
        self.variables = defaultdict(Variable, {
            name: variable
            for name, variable in self.variables.items()
            if variable.is_live
        })
