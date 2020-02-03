import numpy as np


def normalize(series: np.ndarray) -> np.ndarray:
    if series.size == 0:
        return np.array([], dtype=np.float32)
    rebased = series - series.min()
    with np.errstate(divide="ignore", invalid="ignore"):
        scaled = np.true_divide(rebased, rebased.max())
        scaled[~np.isfinite(scaled)] = 0
    return scaled


def compact(values: np.ndarray) -> np.ndarray:
    return np.stack([values[1::2], values[:-1:2]]).mean(axis=0)


class CompactingSeries:
    def __init__(self, max_size: int):
        if max_size < 2 or max_size % 2 != 0:
            raise ValueError("max_size must be a multiple of 2")
        self._values = np.array([], dtype=np.float32)
        self.max_size = max_size
        self.scale = 1
        self.final_bucket = StableBucket()

    @property
    def values(self):
        if self.final_bucket.size == 0:
            return np.copy(self._values)
        return np.append(self._values, self.final_bucket.mean)

    def add(self, value):
        self.final_bucket.add(value)
        if self.final_bucket.size == self.scale:
            self._values = np.append(self._values, self.final_bucket.mean)
            self.final_bucket.__init__()
            if self._values.size == self.max_size:
                self._values = compact(self._values)
                self.scale *= 2

    def add_all(self, values):
        for value in values:
            self.add(value)


class StableBucket:
    def __init__(self, mean: float = 0.0, size: int = 0):
        self.mean = mean
        self.size = size

    def add(self, value):
        size = self.size + 1
        self.mean = self.mean + (value - self.mean) / size
        self.size = size
