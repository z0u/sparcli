import pytest


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtestloop(session):
    yield
    disable_coverage_when_not_all_tests_were_run(session.config)


def disable_coverage_when_not_all_tests_were_run(config):
    plugin = config.pluginmanager.getplugin("_cov")
    if plugin and (config.option.keyword or config.option.file_or_dir):
        plugin.cov_total = None
