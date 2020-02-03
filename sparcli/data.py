import numpy as np


def normalize(series: np.ndarray) -> np.ndarray:
    if series.size == 0:
        return np.array([], dtype=float)
    rebased = series - series.min()
    with np.errstate(divide="ignore", invalid="ignore"):
        scaled = np.true_divide(rebased, rebased.max())
        scaled[~np.isfinite(scaled)] = 0
    return scaled


def compact(values: np.ndarray) -> np.ndarray:
    return np.stack([values[1::2], values[:-1:2]]).mean(axis=0)


class CompactingSeries:
    def __init__(self, values, max_size: int):
        self.values = np.array(values, dtype=float)
        if max_size < 2 or max_size % 2 != 0:
            raise ValueError("max_size must be a multiple of 2")
        self.max_size = max_size

    def append(self, value):
        values = np.append(self.values, value)
        if values.size == self.max_size:
            values = compact(values)
        self.values = values


class StableBucket:
    def __init__(self, mean: float = 0.0, size: int = 0):
        self.mean = mean
        self.size = size

    def add(self, value):
        size = self.size + 1
        self.mean = self.mean + (value - self.mean) / size
        self.size = size
