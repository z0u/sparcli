from numbers import Real
from typing import Optional, Sequence


Series = Sequence[Optional[Real]]


def normalize(series: Series) -> Series:
    reals = [x for x in series if x is not None]
    smallest = min(reals, default=1)
    largest = max(reals, default=1)
    scale = largest - smallest
    if scale == 0:
        return [0.5 if x is not None else None for x in series]
    return [
        (x - smallest) / scale if x is not None else None
        for x in series
    ]
