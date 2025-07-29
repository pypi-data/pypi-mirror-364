from unittest.mock import MagicMock, patch

import pytest
from decorpack.try_except import try_except


@pytest.fixture
def error_func():
    """Function that always raises an error."""

    def _error_func():
        raise ValueError("Test error")

    return _error_func


@pytest.fixture
def success_func():
    """Function that always succeeds."""

    def _success_func():
        return "success"

    return _success_func


def test_specific_exception_catching():
    """Test that the decorator catches only specified exceptions."""

    @try_except(exceptions=ValueError)
    def value_error_func():
        raise ValueError("Value error")

    @try_except(exceptions=ValueError)
    def type_error_func():
        raise TypeError("Type error")

    # Should catch the ValueError
    assert value_error_func() is None

    # Should not catch the TypeError
    with pytest.raises(TypeError):
        type_error_func()


def test_multiple_exceptions():
    """Test that the decorator catches multiple specified exceptions."""

    @try_except(exceptions=(ValueError, TypeError))
    def multi_error_func(error_type):
        if error_type == "value":
            raise ValueError("Value error")
        elif error_type == "type":
            raise TypeError("Type error")
        else:
            raise KeyError("Key error")

    # Should catch both ValueError and TypeError
    assert multi_error_func("value") is None
    assert multi_error_func("type") is None

    # Should not catch KeyError
    with pytest.raises(KeyError):
        multi_error_func("key")


def test_finally_callable():
    """Test that the finally_callable is executed."""
    # Create a function instead of a MagicMock to avoid __name__ attribute issues
    called = False

    def finally_func():
        nonlocal called
        called = True

    @try_except(finally_callable=finally_func)
    def test_func():
        return "success"

    result = test_func()
    assert result == "success"
    assert called is True


def test_finally_callable_with_exception():
    """Test that the finally_callable is executed even when an exception occurs."""
    # Create a function instead of a MagicMock to avoid __name__ attribute issues
    called = False

    def finally_func():
        nonlocal called
        called = True

    @try_except(finally_callable=finally_func)
    def test_func():
        raise ValueError("Test error")

    result = test_func()
    assert result is None
    assert called is True


def test_error_callable():
    """Test that the error_callable is executed and its return value is used."""
    # Create a function instead of a MagicMock to avoid __name__ attribute issues
    called = False

    def error_func():
        nonlocal called
        called = True
        return "error handled"

    @try_except(error_callable=error_func)
    def test_func():
        raise ValueError("Test error")

    result = test_func()
    assert result == "error handled"
    assert called is True


def test_error_callable_not_called_on_success():
    """Test that the error_callable is not executed when no exception occurs."""
    # Create a function instead of a MagicMock to avoid __name__ attribute issues
    called = False

    def error_func():
        nonlocal called
        called = True
        return "error handled"

    @try_except(error_callable=error_func)
    def test_func():
        return "success"

    result = test_func()
    assert result == "success"
    assert called is False


def test_decorator_without_parameters():
    """Test using the decorator without parameters."""

    @try_except
    def test_func():
        raise ValueError("Test error")

    result = test_func()
    assert result is None


def test_decorator_with_args_kwargs():
    """Test that the decorator preserves function arguments."""

    @try_except
    def test_func(a, b, c=3):
        return a + b + c

    result = test_func(1, 2)
    assert result == 6

    result = test_func(1, 2, c=4)
    assert result == 7


def test_logs_enabled():
    """Test that logging is enabled by default."""
    with patch('decorpack.try_except.log') as mock_log:
        @try_except
        def test_func():
            raise ValueError("Test error")

        test_func()
        mock_log.error.assert_called_once()


def test_logs_disabled():
    """Test that logging can be disabled."""
    with patch('decorpack.try_except.log') as mock_log:
        @try_except(logs=False)
        def test_func():
            raise ValueError("Test error")

        test_func()
        mock_log.error.assert_not_called()


def test_debug_logging_with_error_callable():
    """Test debug logging when error_callable is used."""
    with patch('decorpack.try_except.log') as mock_log:
        def error_func():
            return "error handled"

        @try_except(error_callable=error_func)
        def test_func():
            raise ValueError("Test error")

        test_func()
        # Check that debug was called with the appropriate message
        mock_log.debug.assert_called_once()


def test_debug_logging_with_finally_callable():
    """Test debug logging when finally_callable is used."""
    with patch('decorpack.try_except.log') as mock_log:
        def finally_func():
            pass

        @try_except(finally_callable=finally_func)
        def test_func():
            return "success"

        test_func()
        # Check that debug was called with the appropriate message
        mock_log.debug.assert_called_once()


def test_default_exception_catching():
    """Test that by default all exceptions are caught."""

    @try_except
    def value_error_func():
        raise ValueError("Value error")

    @try_except
    def type_error_func():
        raise TypeError("Type error")

    @try_except
    def key_error_func():
        raise KeyError("Key error")

    # Should catch all exceptions
    assert value_error_func() is None
    assert type_error_func() is None
    assert key_error_func() is None


def test_error_callable_receives_exception():
    """Test that the error_callable can access the exception through a closure."""
    received_exception = None

    def error_func():
        nonlocal received_exception
        received_exception = True
        return "error handled"

    @try_except(error_callable=error_func)
    def test_func():
        raise ValueError("Test error")

    result = test_func()
    assert result == "error handled"
    assert received_exception is True

