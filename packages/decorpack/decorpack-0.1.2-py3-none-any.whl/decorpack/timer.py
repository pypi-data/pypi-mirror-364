import time
from typing import Callable, Optional

from decorpack.logger import log
from decorpack.wrapper_utils import enable_async


def timer(func: Optional[Callable] = None):
    """
    Decorator to measure execution time of a function (supports sync and async).

    Usage:
        @timer
        def foo(...):
            ...

        @timer()
        async def bar(...):
            ...
    """

    def _timer_function(fn, *args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        log.debug(f"{fn.__name__} took {elapsed:.6f} seconds")
        return result

    wrapper = enable_async(_timer_function)
    if func is None:
        return wrapper
    return wrapper(func)
