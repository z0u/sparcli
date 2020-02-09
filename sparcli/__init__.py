import atexit

from . import services


_controller = None


def get_controller():
    global _controller
    if not _controller:
        atexit.register(cleanup)
        renderer = services.Renderer()
        _controller = services.Controller(renderer)
        _controller.start()
    return _controller


def cleanup():
    global _controller
    if _controller:
        _controller.stop()
        _controller.join()
        _controller = None


def sparcli():
    return services.Sparcli(get_controller().event_queue)
