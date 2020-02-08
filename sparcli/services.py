from collections import defaultdict
from contextlib import AbstractContextManager

from . import data
from . import render


class Sparcli(AbstractContextManager):
    def __init__(self):
        self.contributions = set()

    def record(self, **variables):
        for name in variables:
            if name not in self.contributions:
                variable_set[name].incref()
                self.contributions.add(name)
        for name, value in variables.items():
            variable_set[name].series.add(value)
        for name, variable in variable_set.variables.items():
            print(name, render.render_as_verical_bars(variable.series.values))

    def register(self):
        pass

    def unregister(self):
        for name in self.contributions:
            variable_set[name].decref()
        variable_set.garbage_collect()

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.unregister()


class Variable:
    def __init__(self):
        self.references = 0
        self.series = data.CompactingSeries(30)

    def incref(self):
        self.references += 1

    def decref(self):
        self.references -= 1


class VariableSet:
    def __init__(self):
        self.variables = defaultdict(Variable)

    def __getitem__(self, name):
        return self.variables[name]

    def garbage_collect(self):
        self.variables = {
            name: variable
            for name, variable in self.variables.items()
            if variable.references > 0
        }


variable_set = VariableSet()
