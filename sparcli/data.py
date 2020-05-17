import numpy as np


NAN = float("nan")
INF = float("inf")


def normalize(series: np.ndarray) -> np.ndarray:
    series = series.astype("float")
    input_is_finite = np.isfinite(series)
    rebased = series - series.min(initial=INF, where=input_is_finite)
    rebased_max = rebased.max(initial=-INF, where=input_is_finite)
    with np.errstate(divide="ignore", invalid="ignore"):
        scaled = np.true_divide(rebased, rebased_max)
    output_is_finite = np.isfinite(scaled)
    scaled[~output_is_finite] = 0.0
    scaled[~input_is_finite] = NAN
    return scaled


def compact(values: np.ndarray) -> np.ndarray:
    values = values.copy()
    odds = values[1::2]
    evens = values[:-1:2]
    nans = ~np.isfinite(odds)
    odds[nans] = evens[nans]
    nans = ~np.isfinite(evens)
    evens[nans] = odds[nans]
    return np.stack([odds, evens]).mean(axis=0)


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
    def __init__(self):
        self.mean = NAN
        self.size = 0
        self.real_size = 0

    def add(self, value):
        self.size += 1
        if not np.isfinite(value):
            pass
        elif not np.isfinite(self.mean):
            self.real_size += 1
            self.mean = value
        else:
            self.real_size += 1
            self.mean = self.mean + (value - self.mean) / self.real_size

    def empty(self):
        self.__init__()
