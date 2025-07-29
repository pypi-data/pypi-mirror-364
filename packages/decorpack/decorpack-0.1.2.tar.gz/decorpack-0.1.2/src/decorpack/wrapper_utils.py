import inspect
from functools import wraps


def enable_async(runner):
    """
    Given a runner function that takes (fn, *args, **kwargs) and executes it,
    returns a decorator that wraps both sync and async functions.

    :param runner: Callable(fn, *args, **kwargs) -> result or coroutine
    :return: decorator for functions
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await runner(func, *args, **kwargs)
            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return runner(func, *args, **kwargs)

        return sync_wrapper

    return decorator
