import inspect

import pytest

import sparcli.capture.system as facade


@pytest.fixture(autouse=True)
def mock_system(mocker):
    """Prevent accidental real system calls"""
    patch_children(mocker, facade.ctypes)
    patch_children(mocker, facade.fcntl)
    patch_children(mocker, facade.msvcrt)
    patch_children(mocker, facade.os)
    patch_children(mocker, facade.sys)

    facade.ctypes.WinError.return_value = OSError()
    facade.os.dup.return_value = mocker.Mock(int)
    facade.os.dup2.return_value = mocker.Mock(int)
    facade.os.pipe.return_value = (mocker.Mock(int), mocker.Mock(int))
    facade.os.read.return_value = mocker.Mock(b"")
    facade.os.write.return_value = mocker.Mock(int)
    yield facade


def patch_children(mocker, ob):
    """Patch the members of the actual object."""
    for name, member in inspect.getmembers(ob):
        if name.startswith("__"):
            continue
        mocker.patch.object(ob, name)
