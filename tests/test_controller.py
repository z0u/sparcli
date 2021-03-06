import pytest

import sparcli.controller


@pytest.fixture
def renderer(mocker):
    yield mocker.patch("sparcli.render.Renderer", autospec=True)(None, None)


@pytest.fixture
def controller(mocker, renderer):
    mocker.patch.object(sparcli.controller, "deque", autospec=True)
    yield sparcli.controller.Controller(renderer)


def test_that_stop_emits_event(mocker, controller):
    controller.stop()
    controller.event_queue.append.assert_called_once_with(("controller_stopped",))


def test_that_run_dispatches_to_methods(mocker, renderer, controller, effector):
    mocker.patch.object(controller, "data_produced", autospec=True)
    mocker.patch.object(controller, "producer_stopped", autospec=True)
    producer = mocker.Mock()
    controller.event_queue.popleft.side_effect = effector(
        [
            ("data_produced", producer, {"x": 1.0}),
            ("producer_stopped", producer),
            IndexError,
            ("controller_stopped",),
        ]
    )

    controller.run()

    assert renderer.close.called
    assert renderer.draw.called
    controller.data_produced.assert_called_once_with(producer, {"x": 1.0})
    controller.producer_stopped.assert_called_once_with(producer)


def test_that_data_is_written_to_variables(mocker, controller):
    producer = mocker.Mock()
    mocker.patch("sparcli.controller.Variable", autospec=True)
    variable = controller.variables["x"]

    controller.data_produced(producer, {"x": 2})

    variable.reference.assert_called_once_with(producer)
    variable.series.add.assert_called_once_with(2)


def test_that_old_references_are_cleaned_up(mocker, controller):
    producer = mocker.Mock()
    mocker.patch("sparcli.data.CompactingSeries")
    variable = sparcli.controller.Variable()
    variable.reference(producer)
    controller.variables["x"] = variable

    controller.producer_stopped(producer)

    assert not variable.is_live
    assert not controller.variables
