import subprocess
import sys
from textwrap import dedent

import pytest

import sparcli.capture


@pytest.mark.feature
@pytest.mark.parametrize("fd_name", ["stdout", "stderr"])
def test_that_outputs_are_captured(capfd, fd_name):
    program = dedent(
        f"""
        import sys
        import sparcli.capture
        file = getattr(sys, "{fd_name}")
        with sparcli.capture.make_capture("{fd_name}", "pipe") as cap:
            file.write("2")
            cap.write(b"1")
            file.write("3")
        """
    )

    subprocess.run([sys.executable, "-c", program], timeout=5.0, check=True)

    out, err = capfd.readouterr()
    outputs = {"stdout": out, "stderr": err}
    assert outputs[fd_name] == "123"


@pytest.mark.feature
@pytest.mark.parametrize("fd_name", ["stdout", "stderr"])
def test_that_subprocess_outputs_are_captured(capfd, fd_name):
    program = dedent(
        f"""
        import sys
        import subprocess
        import sparcli.capture
        def run(program):
            subprocess.run([sys.executable, "-c", program], check=True)
        with sparcli.capture.make_capture("{fd_name}", "pipe") as cap:
            run("import sys; sys.{fd_name}.write('2')")
            cap.write(b"1")
            run("import sys; sys.{fd_name}.write('3')")
        """
    )

    subprocess.run([sys.executable, "-c", program], timeout=5.0, check=True)

    out, err = capfd.readouterr()
    outputs = {"stdout": out, "stderr": err}
    assert outputs[fd_name] == "123"


@pytest.fixture
def mute_capture(mocker):
    mocker.patch.object(sparcli.capture, "os", autospec=True)
    target_file = mocker.MagicMock()
    capture_file = mocker.MagicMock()
    yield sparcli.capture.RedirectCapture(target_file, capture_file)


def test_that_capture_raises_error_if_already_started(mute_capture):
    mute_capture.start()

    with pytest.raises(IOError) as error:
        mute_capture.start()

    assert "Already capturing" in str(error.value)


def test_that_close_raises_error_if_not_started(mute_capture):
    with pytest.raises(IOError) as error:
        mute_capture.close()
    assert "Not capturing" in str(error.value)
