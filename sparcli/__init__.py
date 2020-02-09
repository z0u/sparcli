import atexit
import threading

from . import render
from . import services


_controller = None
_controller_lock = threading.Lock()


def get_controller():
    global _controller
    with _controller_lock:
        if not _controller:
            atexit.register(cleanup)
            renderer = render.Renderer()
            _controller = services.Controller(renderer)
            _controller.start()
    return _controller


def cleanup():
    global _controller
    with _controller_lock:
        if _controller:
            _controller.stop()
            _controller.join()
            _controller = None


def context():
    return services.Sparcli(get_controller().event_queue)


def gen(iterable, name):
    with context() as ctx:
        for value in iterable:
            ctx.record(**{name: value})
            yield value
