import atexit
import threading

import sparcli.render
import sparcli.context
import sparcli.controller


_controller = None
_controller_lock = threading.Lock()


def get_controller():
    global _controller
    with _controller_lock:
        if not _controller:
            atexit.register(cleanup)
            renderer = sparcli.render.Renderer()
            _controller = sparcli.controller.Controller(renderer)
            _controller.start()
    return _controller


def cleanup():
    global _controller
    with _controller_lock:
        if _controller:
            _controller.stop()
            _controller.join()
            _controller = None


def ctx():
    controller = get_controller()
    return sparcli.context.SparcliContext(controller.event_queue)


def gen(iterable, name):
    with ctx() as context:
        for value in iterable:
            context.record(**{name: value})
            yield value
