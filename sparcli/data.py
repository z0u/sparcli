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
        self.max_size = max_size
        self.scale = 1
        self.head = StableBucket()
        self.tail = np.array([], dtype=np.float32)

    @property
    def values(self):
        if self.head.size == 0:
            return np.copy(self.tail)
        head = self.head.mean
        if self.tail.size != 0:
            values = [self.tail[-1], head]
            weights = [self.scale, self.head.size]
            head = np.average(values, weights=weights)
        return np.append(self.tail, head)

    def add(self, value):
        self.head.add(value)
        if self.head.size == self.scale:
            self.tail = np.append(self.tail, self.head.mean)
            self.head.__init__()
            if self.tail.size == self.max_size:
                self.tail = compact(self.tail)
                self.scale *= 2


class StableBucket:
    def __init__(self, mean: float = 0.0, size: int = 0):
        self.mean = mean
        self.size = size

    def add(self, value):
        size = self.size + 1
        self.mean = self.mean + (value - self.mean) / size
        self.size = size
