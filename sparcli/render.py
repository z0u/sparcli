import numpy as np


COLUMNS = np.array([c for c in "▁▂▃▄▅▆▇█"])


def render_as_verical_bars(normalized_series: np.ndarray) -> str:
    indices = (normalized_series * len(COLUMNS)).astype(int).clip(0, len(COLUMNS))
    return "".join(COLUMNS[indices])
