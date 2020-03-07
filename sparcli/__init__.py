import atexit
import threading

import sparcli.capture
import sparcli.context
import sparcli.controller
import sparcli.render


__all__ = ["ctx", "gen"]


def ctx():
    controller = _main.get_controller()
    return sparcli.context.SparcliContext(controller.event_queue)


def gen(iterable, name):
    with ctx() as context:
        for value in iterable:
            context.record(**{name: value})
            yield value


CAPTURE_METHOD = "fd"


def _controller_factory():
    capture = sparcli.capture.factory(CAPTURE_METHOD)
    renderer = sparcli.render.Renderer(capture)
    return sparcli.controller.Controller(renderer)


class _Main:
    def __init__(self, lock):
        self.controller = None
        self.initialized = False
        self.controller_lock = lock

    def get_controller(self):
        with self.controller_lock:
            if not self.initialized:
                self.initialize()
            if not self.controller:
                self.build()
        return self.controller

    def cleanup(self):
        with self.controller_lock:
            if self.controller:
                self.tear_down()

    def initialize(self):
        sparcli.capture.apply_workarounds(CAPTURE_METHOD)
        self.initialized = True

    def build(self):
        atexit.register(self.cleanup)
        self.controller = _controller_factory()
        self.controller.start()

    def tear_down(self):
        self.controller.stop()
        self.controller.join()
        self.controller = None


_main = _Main(threading.Lock())
