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
        sparcli.capture.init()
        with sparcli.capture.make_capture("{fd_name}", "pipe") as cap:
            file.write("2")
            file.flush()
            cap.write(b"1")
            file.write("3")
        """
    )

    subprocess.run([sys.executable, "-c", program], timeout=5.0, check=True)

    out, err = capfd.readouterr()
    outputs = {"stdout": out, "stderr": err}
    assert outputs[fd_name] == "123"


@pytest.mark.feature
def test_that_multiple_outputs_are_captured(capfd):
    program = dedent(
        f"""
        import sys
        import sparcli.capture
        sparcli.capture.init()
        with sparcli.capture.make_multi_capture(True, True) as cap:
            sys.stdout.write("b")
            sys.stdout.flush()
            sys.stderr.write("y")
            sys.stderr.flush()
            cap.write_out(b"a")
            cap.write_err(b"x")
        """
    )

    subprocess.run([sys.executable, "-c", program], timeout=5.0, check=True)

    out, err = capfd.readouterr()
    assert out == "ab"
    assert err == "xy"


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
        sparcli.capture.init()
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


@pytest.mark.feature
@pytest.mark.parametrize("fd_name", ["stdout", "stderr"])
def test_that_nocapture_outputs_are_not_captured(capfd, fd_name):
    program = dedent(
        f"""
        import sys
        import sparcli.capture
        file = getattr(sys, "{fd_name}")
        sparcli.capture.init()
        with sparcli.capture.make_capture("{fd_name}", "none") as cap:
            file.write("1")
            file.flush()
            cap.write(b"2")
            file.write("3")
        """
    )

    subprocess.run([sys.executable, "-c", program], timeout=5.0, check=True)

    out, err = capfd.readouterr()
    outputs = {"stdout": out, "stderr": err}
    assert outputs[fd_name] == "123"


@pytest.mark.parametrize(
    "name,clazz_name", [("nt", "WindowsPlatform"), ("posix", "PosixPlatform")]
)
def test_that_platforms_are_instantiated(mocker, mock_system, name, clazz_name):
    mock_system.os.name = name
    platform = sparcli.capture.get_platform()
    assert type(platform).__name__ == clazz_name


def test_that_unknown_capture_raises_error():
    with pytest.raises(ValueError) as error:
        sparcli.capture.make_capture("stdout", "unknown")
    assert "capture" in str(error.value).lower()
