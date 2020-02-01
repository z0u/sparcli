from numbers import Real
from typing import Optional, Sequence

import numpy as np


def normalize(series: np.ndarray) -> np.ndarray:
    if series.size == 0:
        return np.array([], dtype=float)
    rebased = series - series.min()
    with np.errstate(divide='ignore', invalid='ignore'):
        scaled = np.true_divide(rebased, rebased.max())
        scaled[ ~ np.isfinite(scaled)] = 0
    return scaled
