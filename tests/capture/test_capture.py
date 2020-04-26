import pytest

import sparcli.capture.capture


@pytest.fixture
def mute_capture(mocker, mock_system):
    platform = mocker.patch("sparcli.capture.platform_base.Platform", autospec=True)()
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


def test_that_blocking_read_is_handled_gracefully(mocker, mute_capture, mock_system):
    mock_system.os.read.side_effect = BlockingIOError
    print(mock_system.os.read)
    mute_capture.start()
    mute_capture.flush()
    assert not mock_system.os.write.called
