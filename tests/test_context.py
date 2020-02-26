import collections

import pytest

import sparcli.context


@pytest.fixture
def queue(mocker):
    yield mocker.MagicMock(collections.deque)()


@pytest.fixture
def context(queue):
    yield sparcli.context.SparcliContext(queue)


def test_that_context_emits_data_produced_event(context, queue):
    context.record(x=1)
    queue.append.assert_called_with(("data_produced", context, {"x": 1}))


def test_that_context_emits_producer_stopped_event(context, queue):
    context.__exit__(None, None, None)
    queue.append.assert_called_with(("producer_stopped", context))
