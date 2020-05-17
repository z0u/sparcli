import numpy as np
import pytest


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_sessionstart(session):
    disable_coverage_when_not_all_tests_were_run(session.config)
    yield


def disable_coverage_when_not_all_tests_were_run(config):
    if not config.pluginmanager.has_plugin("_cov"):
        return
    if (
        config.option.collectonly
        or (config.option.file_or_dir and "tests" not in config.option.file_or_dir)
        or (config.option.keyword or config.option.markexpr)
    ):
        config.pluginmanager.unregister(name="_cov")


@pytest.fixture
def effector():
    """
    Creates a function that returns the next item from a sequence each time it
    is called. If the item is an exception, it will be raised. For use with
    Mock.side_effect to simulate a mixture of successful calls and exceptions.
    """

    def effector_(sequence):
        iterator = iter(sequence)

        def materialize(*args, **kwargs):
            item = next(iterator)
            if type(item) == type and issubclass(item, Exception):
                raise item
            if isinstance(item, Exception):
                raise item
            return item

        return materialize

    return effector_


@pytest.fixture
def allclose():
    def allclose(expected, actual):
        expected = np.array(expected)
        actual = np.array(actual)
        if len(expected) != len(actual):
            return False
        if not np.all(np.isfinite(expected) == np.isfinite(actual)):
            return False
        return np.allclose(expected[np.isfinite(expected)], actual[np.isfinite(actual)])

    return allclose
