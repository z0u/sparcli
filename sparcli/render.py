import numpy as np

import sparcli.data


COLUMNS = np.array([c for c in " ▁▂▃▄▅▆▇█"])


def render_as_vertical_bars(normalized_series: np.ndarray) -> str:
    """
    Convert a series with values between 0 and 1 into a chart. Values that are less
    than 0 will be rendered as blank space.
    """
    # astype(int).clip implicitly converts NaN values to bottom of range.
    upper_index = len(COLUMNS) - 2
    texture_coordinates = (normalized_series * upper_index) + 1
    indices = texture_coordinates.astype(int).clip(0, upper_index + 1)
    return "".join(COLUMNS[indices])


# Escape sequences
# https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences
# Control sequence introducer
CSI = "\x1b["
# Terminal output sequences
# https://en.wikipedia.org/wiki/ANSI_escape_code#Terminal_output_sequences
CURSOR_UP = f"{CSI}1A"
CLEAR_LINE = f"{CSI}2K"


class Renderer:
    def __init__(self, write, capture):
        self.height = 0
        self.capture = capture
        self.write = write

    def start(self):
        self.capture.start()

    def close(self):
        self.capture.close()

    def draw(self, variables):
        self.clear()
        self.capture.flush()
        name_width = max((len(name) for name in variables), default=0)
        for name, variable in variables.items():
            values = sparcli.data.normalize(variable.series.values)
            name = name.rjust(name_width)
            bars = render_as_vertical_bars(values)
            self.write(f"{name} {bars}\n")
        self.height = len(variables)

    def clear(self):
        self.write(f"{CURSOR_UP}{CLEAR_LINE}" * self.height)
        self.height = 0
