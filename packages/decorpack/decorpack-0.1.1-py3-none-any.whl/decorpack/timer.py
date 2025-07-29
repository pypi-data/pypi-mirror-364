from time import perf_counter
from functools import wraps

from decorpack.logger import log


def timer(func: callable) -> callable:
    """
    Decorator to measure the execution time of a function.
    :param func: function to measure the execution time of
    :return: wrapper function that measures the execution time of the function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        log.debug(f"{func.__name__}: {end - start} seconds")
        return result

    return wrapper
