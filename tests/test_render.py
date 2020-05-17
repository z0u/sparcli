import numpy as np
import pytest

import sparcli.render


@pytest.mark.parametrize(
    "values,expected",
    [
        (np.array([]), ""),
        (np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype="float") / 7, "▁▂▃▄▅▆▇█"),
        (np.array([0, float("nan"), 0.5]), "▁ ▄"),
    ],
)
def test_that_normalized_series_renders_as_vertical_bars(values, expected):
    output = sparcli.render.render_as_vertical_bars(values)
    assert expected == output


@pytest.fixture
def capture(mocker):
    yield mocker.patch("sparcli.capture.capture.MultiCapture", autospec=True)(
        None, None
    )


@pytest.fixture
def renderer(mocker, capture):
    mocker.patch("sparcli.data", autospec=True)
    yield sparcli.render.Renderer(capture.write_out, capture)


def test_that_renderer_draws_variables(mocker, renderer, capture):
    render = mocker.patch("sparcli.render.render_as_vertical_bars", autospec=True)
    variables = {"a": mocker.MagicMock(), "b": mocker.MagicMock()}

    renderer.draw(variables)

    assert render.called
    assert capture.flush.called
    assert capture.write_out.called
    assert renderer.height == len(variables)


def test_that_renderer_captures_output(mocker, renderer, capture):
    renderer.start()
    assert capture.start.called


def test_that_renderer_releases_output(mocker, renderer, capture):
    renderer.close()
    assert capture.close.called
