import queue as queue_module

import pytest

import sparcli.controller
import sparcli.render


@pytest.fixture
def queue(mocker):
    mocker.patch.dict(
        queue_module.__dict__,
        {"Empty": queue_module.Empty, "SimpleQueue": mocker.MagicMock()},
        clear=True,
    )
    yield queue_module.SimpleQueue.return_value


@pytest.fixture
def blocking_queue(mocker):
    mocker.patch.dict(
        queue_module.__dict__,
        {"Empty": queue_module.Empty, "Queue": mocker.MagicMock()},
        clear=True,
    )
    yield queue_module.Queue.return_value


@pytest.fixture
def renderer(mocker):
    yield mocker.MagicMock(sparcli.render.Renderer)


def test_that_event_queue_falls_back_to_blocking_queue(
    mocker, blocking_queue, renderer
):
    controller = sparcli.controller.Controller(renderer)
    assert controller.event_queue == blocking_queue


def test_that_stop_emits_event(mocker, queue, renderer):
    controller = sparcli.controller.Controller(renderer)
    controller.stop()
    queue.put.assert_called_once_with(("stopped",))


def test_that_run_dispatches_to_methods(mocker, queue, renderer, effector):
    controller = sparcli.controller.Controller(renderer)
    mocker.patch.object(controller, "data_produced", autospec=True)
    mocker.patch.object(controller, "producer_stopped", autospec=True)
    producer = mocker.Mock()
    queue.get.side_effect = effector(
        [
            ("data_produced", producer, {}),
            ("producer_stopped", producer),
            queue_module.Empty,
            ("stopped",),
        ]
    )

    controller.run()

    assert renderer.clear.called
    assert renderer.draw.called
    controller.data_produced.assert_called_once_with(producer, {})
    controller.producer_stopped.assert_called_once_with(producer)


def test_that_data_is_written_to_variables(mocker, queue, renderer):
    mocker.patch("sparcli.data.CompactingSeries")
    variable = sparcli.controller.Variable()
    mocker.patch("sparcli.controller.Variable").return_value = variable
    producer = mocker.Mock()
    controller = sparcli.controller.Controller(renderer)

    controller.data_produced(producer, {"x": 2})

    assert variable.references == {producer}
    variable.series.add.assert_called_once_with(2)


def test_that_old_references_are_cleaned_up(mocker, queue, renderer):
    producer = mocker.Mock()
    controller = sparcli.controller.Controller(renderer)
    mocker.patch("sparcli.data.CompactingSeries")
    variable = sparcli.controller.Variable()
    variable.reference(producer)
    controller.variables["x"] = variable

    controller.producer_stopped(producer)

    assert not variable.references
    assert not controller.variables
