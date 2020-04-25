import subprocess
import sys
from textwrap import dedent

import pytest


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
