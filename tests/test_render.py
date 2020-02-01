import pytest

import sparcli.render


@pytest.mark.parametrize("values,expected", [
    (range(9), " ▁▂▃▄▅▆▇█"),
    ([], ""),
])
def test_that_normalized_series_renders_as_vertical_bars(values, expected):
    series = [x / 8 for x in values]
    output = sparcli.render.render_as_verical_bars(series)
    assert expected == output


def test_that_missing_values_render_as_dots():
    series = [None, None]
    output = sparcli.render.render_as_verical_bars(series)
    assert ".." == output
