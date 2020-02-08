from contextlib import AbstractContextManager

from . import data
from . import render


contexts = []


class Sparcli(AbstractContextManager):
    def __init__(self):
        self.series = {}

    def record(self, **variables):
        for name, value in variables.items():
            if name not in self.series:
                self.series[name] = data.CompactingSeries(30)
            self.series[name].add(value)
        for name, series in self.series.items():
            print(name, render.render_as_verical_bars(series.values))

    def register(self):
        contexts.append(self)

    def unregister(self):
        contexts.remove(self)

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.unregister()
