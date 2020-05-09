import pytest

import sparcli.capture.platform_windows


def test_that_failure_raises_exception(mocker, mock_system):
    mock_system.ctypes.windll.kernel32.SetNamedPipeHandleState.return_value = 0
    read_fd = mocker.MagicMock(int)
    platform = sparcli.capture.platform_windows.WindowsPlatform()

    with pytest.raises(OSError):
        platform.set_nonblocking(read_fd)
