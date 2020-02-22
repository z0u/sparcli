import sys

import numpy as np

import sparcli.data


COLUMNS = np.array([c for c in "▁▂▃▄▅▆▇█"])


def render_as_vertical_bars(normalized_series: np.ndarray) -> str:
    upper_index = len(COLUMNS) - 1
    indices = (normalized_series * upper_index).astype(int).clip(0, upper_index)
    return "".join(COLUMNS[indices])


class Renderer:
    def __init__(self):
        self.height = 0
        self.write = sys.stdout.write

    def draw(self, variables):
        self.clear()
        name_width = max((len(name) for name in variables), default=0)
        for name, variable in variables.items():
            values = sparcli.data.normalize(variable.series.values)
            name = name.rjust(name_width)
            bars = render_as_vertical_bars(values)
            self.write(f"{name} {bars}\n")
        self.height = len(variables)

    def clear(self):
        self.write("\x1b[1A\x1b[2K" * self.height)
        self.height = 0
