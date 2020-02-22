import atexit
import threading

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


def controller_factory():
    renderer = sparcli.render.Renderer()
    return sparcli.controller.Controller(renderer)


class _Main:
    def __init__(self, lock):
        self.controller = None
        self.controller_lock = lock

    def get_controller(self):
        with self.controller_lock:
            if not self.controller:
                atexit.register(self.cleanup)
                self.controller = controller_factory()
                self.controller.start()
        return self.controller

    def cleanup(self):
        with self.controller_lock:
            if not self.controller:
                return
            self.controller.stop()
            self.controller.join()
            self.controller = None


_main = _Main(threading.Lock())
