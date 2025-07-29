import logging
from typing import Callable, Any, Optional, TypeVar, Union, Tuple, Type

from decorpack.logger import log, LOG_LEVEL
from decorpack.wrapper_utils import enable_async


def try_except(
        func: Optional[Callable] = None,
        *,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        finally_callable: Optional[Callable[[], Any]] = None,
        error_callable: Optional[Callable[[], Any]] = None,
        logs: bool = True,
) -> Callable:
    """
    Decorator to catch exceptions in a function (supports sync and async).

    Usage:
        @try_except
        def foo(...):
            ...

        @try_except()
        async def bar(...):
            ...

    :param func: Function to decorate. If None, returns a decorator.
    :param exceptions: Exception(s) to catch.
    :param finally_callable: Optional callable to execute in finally.
    :param error_callable: Optional callable to execute on error.
    :param logs: Whether to log errors and callbacks.
    """
    R = TypeVar("R")

    def _try_except_function(fn: Callable[..., R], *args, **kwargs) -> Optional[R]:
        try:

            return fn(*args, **kwargs)

        except exceptions as e:

            message = f"{fn.__name__}: {e.__class__.__name__}: {e}"
            if logs:
                log.error(message, exc_info=LOG_LEVEL <= logging.DEBUG)
            if error_callable:
                if logs:
                    log.debug(f"calling {error_callable.__name__} from {fn.__name__}")
                return error_callable()
            return None

        finally:

            if finally_callable:
                finally_callable()
                if logs:
                    log.debug(f"{finally_callable.__name__} executed from {fn.__name__}")

    wrapper = enable_async(_try_except_function)
    if func is None:
        return wrapper
    return wrapper(func)
