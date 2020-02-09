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
        name_width = max((len(name) for name in variables), default=0)
        for name, variable in variables.items():
            values = normalize(variable.series.values)
            name = name.rjust(name_width)
            bars = render_as_verical_bars(values)
            print(f"{name} {bars}")
        self.height = len(variables)

    def clear(self):
        sys.stdout.write("\x1b[1A\x1b[2K" * self.height)
        self.height = 0
