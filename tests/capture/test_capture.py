import pytest

import sparcli.capture.capture


@pytest.fixture
def mock_os(mocker):
    mock_os = mocker.patch.object(sparcli.capture.capture, "os")
    mock_os.close = mocker.MagicMock("sparcli.capture.os_facade.close", autospec=True)
    mock_os.dup = mocker.MagicMock(
        "sparcli.capture.os_facade.dup",
        autospec=True,
        return_value=mocker.MagicMock(int),
    )
    mock_os.dup2 = mocker.MagicMock(
        "sparcli.capture.os_facade.dup2",
        autospec=True,
        return_value=mocker.MagicMock(int),
    )
    mock_os.pipe = mocker.MagicMock(
        "sparcli.capture.os_facade.pipe",
        autospec=True,
        return_value=(mocker.MagicMock(int), mocker.MagicMock(int)),
    )
    mock_os.read = mocker.MagicMock(
        "sparcli.capture.os_facade.read",
        autospec=True,
        return_value=mocker.MagicMock(b""),
    )
    mock_os.write = mocker.MagicMock(
        "sparcli.capture.os_facade.write",
        autospec=True,
        return_value=mocker.MagicMock(int),
    )
    yield mock_os


@pytest.fixture
def mute_capture(mocker, mock_os):
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


def test_that_blocking_read_is_handled_gracefully(mocker, mute_capture, mock_os):
    mock_os.read.side_effect = BlockingIOError
    mute_capture.start()
    mute_capture.flush()
    assert not mock_os.write.called
