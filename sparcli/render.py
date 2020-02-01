from typing import Sequence


COLUMNS = " ▁▂▃▄▅▆▇█"


def render_as_verical_bars(normalized_series: Sequence[float]) -> str:
    indices = [int(max(0, min(x * 8, 8))) for x in normalized_series]
    return "".join(COLUMNS[i] for i in indices)
