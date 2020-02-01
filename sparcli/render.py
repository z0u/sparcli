from .data import Series


COLUMNS = " ▁▂▃▄▅▆▇█"


def render_as_verical_bars(normalized_series: Series) -> str:
    indices = [
        int(max(0, min(x * 8, 8))) if x is not None else None
        for x in normalized_series]
    return "".join(
        COLUMNS[i] if i is not None else "."
        for i in indices)
