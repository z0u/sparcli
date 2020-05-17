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
    def __init__(self, max_size: int, max_scale: int = 1000, initial_scale: int = 1):
        if max_size < 2 or max_size % 2 != 0:
            raise ValueError("max_size must be a multiple of 2")
        if not max_scale > 0:  # pragma: no-cover
            raise ValueError("max_scale must be positive")
        self.max_size = max_size
        self.max_scale = max_scale
        self.scale = initial_scale
        self.scale_exp = 1 << (initial_scale - 1)
        self.head = StableBucket()
        self.tail = np.array([], dtype=np.float32)

    @property
    def values(self):
        if self.head.size == 0:
            return np.copy(self.tail)
        return np.append(self.tail, self.weighted_head)[-self.max_size + 1 :]

    @property
    def weighted_head(self):
        values = [self.tail[-1], self.head.mean]
        weights = [self.scale_exp, self.head.size]
        return np.average(values, weights=weights)

    def add(self, value):
        self.head.add(value)
        if self.head.size < self.scale_exp:
            return
        self.tail = np.append(self.tail, self.head.mean)
        self.head.empty()
        if self.tail.size < self.max_size:
            return
        if self.scale < self.max_scale:
            self.tail = compact(self.tail)
            self.scale += 1
            self.scale_exp = 1 << (self.scale - 1)
        else:
            self.tail = self.tail[1:]


class StableBucket:
    mean: float
    size: int

    def __init__(self, mean: float = 0.0, size: int = 0):
        self.mean = mean
        self.size = size

    def add(self, value):
        size = self.size + 1
        self.mean = self.mean + (value - self.mean) / size
        self.size = size

    def empty(self):
        self.mean = 0.0
        self.size = 0
