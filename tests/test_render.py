import numpy as np
import pytest

import sparcli.render


NAN = float("nan")


@pytest.mark.parametrize(
    "values,expected",
    [
        (np.array([], dtype=float), ""),
        (np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=float) / 7, "▁▂▃▄▅▆▇█"),
        (np.array([0, NAN, 0.5]), "▁ ▄"),
    ],
)
def test_that_normalized_series_renders_as_vertical_bars(values, expected):
    output = sparcli.render.render_as_vertical_bars(values)
    assert expected == output


@pytest.mark.parametrize(
    "values,width,expected",
    [
        ([], 0, []),
        ([], 4, [NAN, NAN, NAN, NAN]),
        ([1], 1, [1]),
        ([1], 4, [1, NAN, NAN, NAN]),
        ([1, 2, 3], 2, [1, 3]),
        ([1, 2, 3, 4], 3, [1, 2.5, 4]),
        (list(range(100)), 4, [0, 33, 66, 99]),
    ],
)
def test_that_resampled_series_fits_width(values, width, expected, allclose):
    values = np.array(values, dtype=float)
    expected = np.array(expected, dtype=float)

    resampled = sparcli.render.resample(values, width)

    assert allclose(expected, resampled)


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
    resample = mocker.patch("sparcli.render.resample", autospec=True)
    variables = {"a": mocker.MagicMock(), "b": mocker.MagicMock()}

    renderer.draw(variables)

    assert render.called
    assert resample.called
    assert capture.flush.called
    assert capture.write_out.called
    assert renderer.height == len(variables)


def test_that_renderer_captures_output(mocker, renderer, capture):
    renderer.start()
    assert capture.start.called


def test_that_renderer_releases_output(mocker, renderer, capture):
    renderer.close()
    assert capture.close.called
