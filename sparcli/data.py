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
    if values.size % 2 != 0:
        raise ValueError("Can't compact a series with an odd length.")
    return np.stack([values[1::2], values[:-1:2]]).mean(axis=0)
