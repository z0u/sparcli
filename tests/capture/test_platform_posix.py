import sparcli.capture.platform_posix


def test_that_set_nonblocking_sets_file_attribute(mocker, mock_system):
    read_fd = mocker.MagicMock(int)
    platform = sparcli.capture.platform_posix.PosixPlatform()
    platform.set_nonblocking(read_fd)
    assert mock_system.fcntl.fcntl.call_args[0][0] == read_fd
