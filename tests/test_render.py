import numpy as np
import pytest

import sparcli.render


@pytest.mark.parametrize("values,expected", [
    (range(8), "▁▂▃▄▅▆▇█"),
    ([], ""),
])
def test_that_normalized_series_renders_as_vertical_bars(values, expected):
    series = np.array(values) / 8
    output = sparcli.render.render_as_verical_bars(series)
    assert expected == output
