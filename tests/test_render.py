import sys

import numpy as np
import pytest

import sparcli.render


@pytest.mark.parametrize(
    "values,expected", [([0, 1, 2, 3, 4, 5, 6, 7], "▁▂▃▄▅▆▇█"), ([], ""),]
)
def test_that_normalized_series_renders_as_vertical_bars(values, expected):
    values = np.array(values) / 7
    output = sparcli.render.render_as_vertical_bars(values)
    assert expected == output


def test_that_renderer_draws_variables(mocker):
    render = mocker.patch("sparcli.render.render_as_vertical_bars", autospec=True)
    mocker.patch("sparcli.data", autospec=True)
    renderer = sparcli.render.Renderer()
    renderer.write = mocker.MagicMock(sys.stdout.write)
    variables = {"a": mocker.MagicMock(), "b": mocker.MagicMock()}

    renderer.draw(variables)

    assert render.called
    assert renderer.write.called
    assert renderer.height == len(variables)
