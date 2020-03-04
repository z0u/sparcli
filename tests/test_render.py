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


@pytest.fixture
def capture(mocker):
    capture = mocker.patch("sparcli.capture.CaptureManager", autospec=True)("fd")
    yield capture


def test_that_renderer_draws_variables(mocker, capture):
    render = mocker.patch("sparcli.render.render_as_vertical_bars", autospec=True)
    mocker.patch("sparcli.data", autospec=True)
    renderer = sparcli.render.Renderer(capture)
    variables = {"a": mocker.MagicMock(), "b": mocker.MagicMock()}

    renderer.draw(variables)

    assert render.called
    assert capture.write_out.called
    assert renderer.height == len(variables)


def test_that_renderer_captures_output(mocker, capture):
    renderer = sparcli.render.Renderer(capture)
    renderer.start()
    assert capture.start_global_capturing.called


def test_that_renderer_releases_output(mocker, capture):
    renderer = sparcli.render.Renderer(capture)
    renderer.close()
    assert capture.stop_global_capturing.called
