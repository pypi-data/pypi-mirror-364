import asyncio

import pytest
from decorpack.wrapper_utils import enable_async


def test_sync_wrapper_preserves_name_and_result():
    # Simple runner that just calls the function
    def runner(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    decorator = enable_async(runner)

    @decorator
    def multiply(x, y):
        """Multiply two numbers"""
        return x * y

    # Check result
    assert multiply(3, 4) == 12
    # Check name and docstring are preserved
    assert multiply.__name__ == "multiply"
    assert multiply.__doc__ == "Multiply two numbers"


def test_async_wrapper_preserves_name_and_result():
    # Runner that just calls the function
    def runner(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    decorator = enable_async(runner)

    @decorator
    async def add(x, y):
        """Add two numbers asynchronously"""
        return x + y

    # Run the coroutine using asyncio.run
    result = asyncio.run(add(5, 7))
    assert result == 12
    # Check metadata preservation
    assert add.__name__ == "add"
    assert add.__doc__ == "Add two numbers asynchronously"


def test_runner_invoked_for_sync():
    calls = []

    def runner(fn, *args, **kwargs):
        calls.append(fn.__name__)
        return fn(*args, **kwargs)

    decorator = enable_async(runner)

    @decorator
    def subtract(a, b):
        return a - b

    assert subtract(10, 4) == 6
    assert calls == ['subtract']


def test_runner_invoked_for_async():
    calls = []

    def runner(fn, *args, **kwargs):
        calls.append(fn.__name__)
        return fn(*args, **kwargs)

    decorator = enable_async(runner)

    @decorator
    async def subtract(a, b):
        return a - b

    result = asyncio.run(subtract(10, 4))
    assert result == 6
    assert calls == ['subtract']


def test_sync_exception_propagates():
    def runner(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    decorator = enable_async(runner)

    @decorator
    def will_fail():
        raise ValueError("sync error")

    with pytest.raises(ValueError):
        will_fail()


def test_async_exception_propagates():
    def runner(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    decorator = enable_async(runner)

    @decorator
    async def will_fail():
        raise RuntimeError("async error")

    with pytest.raises(RuntimeError):
        asyncio.run(will_fail())
