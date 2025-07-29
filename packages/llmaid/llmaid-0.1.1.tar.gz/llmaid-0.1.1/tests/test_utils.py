"""
Test utilities for LLMAid test suite.

This module provides common test helpers, mocks, and utilities
that can be shared across different test files.
"""

from typing import List
from unittest.mock import patch
from contextlib import contextmanager


class MockSleep:
    """
    A mock for asyncio.sleep that records call durations without actually sleeping.
    
    This is useful for testing retry logic, backoff timing, and other time-dependent
    behavior without waiting for real time to pass.
    """
    
    def __init__(self):
        self.sleep_calls: List[float] = []
    
    async def __call__(self, duration: float) -> None:
        """
        Mock sleep function that records the duration but doesn't actually sleep.
        
        Args:
            duration: The sleep duration that would have been used
        """
        self.sleep_calls.append(duration)
        # Don't actually sleep, just record the duration
        return
    
    def reset(self) -> None:
        """Reset the recorded sleep calls."""
        self.sleep_calls.clear()
    
    @property
    def call_count(self) -> int:
        """Get the number of sleep calls made."""
        return len(self.sleep_calls)
    
    @property
    def total_time(self) -> float:
        """Get the total time that would have been slept."""
        return sum(self.sleep_calls)


@contextmanager
def mock_asyncio_sleep():
    """
    Context manager that mocks asyncio.sleep and returns a MockSleep instance.
    
    Usage:
        with mock_asyncio_sleep() as mock_sleep:
            # Code that calls asyncio.sleep
            some_function_with_retries()
            
            # Verify sleep behavior
            assert mock_sleep.call_count == 3
            assert mock_sleep.sleep_calls == [1.0, 2.0, 4.0]
    
    Returns:
        MockSleep: The mock sleep instance for inspecting calls
    """
    mock_sleep = MockSleep()
    
    with patch('asyncio.sleep', mock_sleep):
        yield mock_sleep


@contextmanager 
def mock_time_sleep():
    """
    Context manager that mocks time.sleep and returns a MockSleep instance.
    
    Usage:
        with mock_time_sleep() as mock_sleep:
            # Code that calls time.sleep 
            some_function_with_retries()
            
            # Verify sleep behavior
            assert mock_sleep.call_count == 3
            assert mock_sleep.sleep_calls == [1.0, 2.0, 4.0]
    
    Returns:
        MockSleep: The mock sleep instance for inspecting calls
    """
    mock_sleep = MockSleep()
    
    def sync_sleep(duration: float) -> None:
        """Synchronous mock sleep that records duration."""
        mock_sleep.sleep_calls.append(duration)
        # Don't actually sleep, just record the duration
        return
    
    with patch('time.sleep', sync_sleep):
        yield mock_sleep
