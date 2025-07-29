import logging
from typing import Callable, Any, Optional, TypeVar, Union, Tuple, Type
from functools import wraps

from decorpack.logger import log, LOG_LEVEL


def try_except(
        _func=None,
        *,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        finally_callable: Optional[Callable[[], Any]] = None,
        error_callable: Optional[Callable[[], Any]] = None,
        logs: Optional[bool] = True,
) -> Callable:
    """
    Decorator to catch exceptions in a function.

    :param _func: The function to decorate.
    :param exceptions: Exception or tuple of exceptions to catch. Default catches all exceptions.
    :param finally_callable: Optional parameterless callable to execute in finally.
    :param error_callable: Optional parameterless callable to execute when an error is caught.
    :param logs: Enable or not logging.
    :return: The wrapper function.
    """
    R = TypeVar("R")

    def decorator_func(func: Callable[..., R]) -> Callable[..., Optional[R]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[R]:
            def handle_exception(e: Exception) -> Optional[R]:
                message = f"{func.__name__}: {e.__class__.__name__}: {e}"

                if logs:
                    log.error(message, exc_info=LOG_LEVEL <= logging.DEBUG)
                if error_callable:
                    if logs:
                        log.debug(f"calling {error_callable.__name__} from {func.__name__}")
                    return error_callable()
                return None

            def handle_finally() -> None:
                if finally_callable:
                    finally_callable()
                    if logs:
                        log.debug(
                            f"{finally_callable.__name__} executed from {func.__name__}"
                        )

            try:
                return func(*args, **kwargs)
            except exceptions as e:
                return handle_exception(e)
            finally:
                handle_finally()

        return wrapper

    if _func is None:
        return decorator_func
    else:
        return decorator_func(_func)
