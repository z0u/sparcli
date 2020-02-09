import sys

import numpy as np

from .data import normalize

COLUMNS = np.array([c for c in "▁▂▃▄▅▆▇█"])


def render_as_verical_bars(normalized_series: np.ndarray) -> str:
    upper_index = len(COLUMNS) - 1
    indices = (normalized_series * upper_index).astype(int).clip(0, upper_index)
    return "".join(COLUMNS[indices])


class Renderer:
    def __init__(self):
        self.height = 0

    def draw(self, variables):
        self.clear()
        for name, variable in variables.items():
            values = normalize(variable.series.values)
            print(name, render_as_verical_bars(values))
        self.height = len(variables)

    def clear(self):
        sys.stdout.write("\x1b[1A\x1b[2K" * self.height)
        self.height = 0
