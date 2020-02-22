import threading
import time

import sparcli
from sparcli import controller_factory, _Main


def test_that_it_can_be_used_as_a_context_manager(mocker):
    controller = mocker.MagicMock(sparcli.controller.Controller, autospec=True)()
    main = mocker.patch.object(sparcli, "_main", autospec=True)
    main.get_controller.return_value = controller
    SparcliContext = mocker.patch("sparcli.context.SparcliContext", autospec=True)

    with sparcli.ctx() as ctx:
        ctx.record({})

    assert SparcliContext.return_value.__exit__.called


def test_that_it_can_wrap_an_iterable(mocker):
    ctx = mocker.patch("sparcli.ctx", autospec=True).return_value
    ctx = ctx.__enter__.return_value
    numbers = [1, 2, 3]

    output = list(sparcli.gen(numbers, "x"))

    assert numbers == output
    ctx.record.assert_any_call(x=1)
    ctx.record.assert_any_call(x=2)
    ctx.record.assert_any_call(x=3)


def test_that_controller_is_configured(mocker):
    renderer = mocker.patch("sparcli.render.Renderer", autospec=True)()
    Controller = mocker.patch("sparcli.controller.Controller", autospec=True)

    controller_factory()

    Controller.assert_called_with(renderer)


def run_concurrently(function, n):
    threads = [threading.Thread(None, function) for _ in range(n)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def test_that_only_one_controller_can_exist(mocker):
    main = _Main(threading.Lock())
    controller = mocker.MagicMock(sparcli.controller.Controller, autospec=True)()
    mocker.patch.object(sparcli, "controller_factory", return_value=controller)
    atexit = mocker.patch("atexit.register", autospec=True)
    controller.start.side_effect = lambda: time.sleep(0.1)

    run_concurrently(main.get_controller, 2)

    assert controller.start.call_count == 1
    atexit.assert_called_once_with(main.cleanup)


def test_that_controller_is_cleaned_up_on_exit(mocker):
    controller = mocker.MagicMock(sparcli.controller.Controller, autospec=True)()
    main = _Main(threading.Lock())
    main.controller = controller
    controller.stop.side_effect = lambda: time.sleep(0.1)

    run_concurrently(main.cleanup, 2)

    assert controller.stop.call_count == 1
    assert main.controller is None
