import subprocess
import sys
from textwrap import dedent

import pytest

import sparcli.capture


@pytest.fixture
def run_py():
    def run(program):
        proc_info = subprocess.run(
            [sys.executable, "-c", program], capture_output=True, text=True, timeout=5.0
        )
        print(proc_info.stdout)
        print(proc_info.stderr, sys.stderr)
        return proc_info

    return run


@pytest.mark.parametrize("fd_name", ["stdout", "stderr"])
def test_that_subprocess_outputs_are_captured(run_py, fd_name):
    program = dedent(
        f"""
        import sys
        import sparcli.capture
        with sparcli.capture.make_fd_capture("{fd_name}") as cap:
            file = getattr(sys, "{fd_name}")
            file.write("2")
            cap.write_original("1")
            file.write("3")
        """
    )

    proc_info = run_py(program)

    assert proc_info.returncode == 0
    assert getattr(proc_info, fd_name) == "123"


@pytest.mark.parametrize("fd_name", ["stdout", "stderr"])
def test_that_current_process_outputs_are_captured(capfd, fd_name):
    with sparcli.capture.make_fd_capture(fd_name) as cap:
        file = getattr(sys, fd_name)
        file.write("2")
        cap.write_original("1")
        file.write("3")

    out, err = capfd.readouterr()
    outputs = {"stdout": out, "stderr": err}
    assert outputs[fd_name] == "123"
