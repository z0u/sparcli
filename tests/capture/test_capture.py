import subprocess
import sys
from textwrap import dedent

import pytest

import sparcli.capture.capture


@pytest.fixture
def mute_capture(mocker):
    mocker.patch("sparcli.capture.capture.os", autospec=True)
    mocker.patch(
        "sparcli.capture.capture.os.pipe",
        autospec=True,
        return_value=(mocker.MagicMock(int), mocker.MagicMock(int)),
    )
    platform = mocker.MagicMock()
    capture_fd = mocker.MagicMock(int)
    yield sparcli.capture.capture.PipeCapture(platform, capture_fd)


def test_that_capture_raises_error_if_already_started(mute_capture):
    mute_capture.start()
    with pytest.raises(IOError) as error:
        mute_capture.start()
    assert "Already capturing" in str(error.value)


def test_that_close_raises_error_if_not_started(mute_capture):
    with pytest.raises(IOError) as error:
        mute_capture.close()
    assert "Not capturing" in str(error.value)
