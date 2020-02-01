import pytest

import sparcli.render


@pytest.mark.parametrize("values,text", [
    (range(9), " ▁▂▃▄▅▆▇█"),
    ([], ""),
])
def test_that_normalized_series_renders_as_vertical_bars(values, text):
    series = [x / 8 for x in values]

    output = sparcli.render.render_as_verical_bars(series)

    assert text == output
