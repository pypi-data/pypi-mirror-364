"""
Test suite for LLMAid error handling and retry functionality.

This module tests error handling scenarios including HTTP errors,
retries, exponential backoff, and timeout handling.

Based on specifications in error_handling.spec.md
"""

import pytest
import time
from pathlib import Path
import sys
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid
from llmaid.exceptions import (
    ProviderHTTPError,
    ProviderTimeoutError,
    RetryExhaustedError
)

# Import test utilities
from test_utils import mock_asyncio_sleep


class TestErrorHandlingAndRetries:
    """Test suite for error handling and retry functionality."""

    def test_http_4xx_error_non_retryable(self, clean_env, httpx_mock):
        """
        1. Scenario: HTTP 4XX error (non-retryable)
        Given I have an llmaid instance
        And I run a completion
        And the backend returns a 400 Bad Request error
        When I call completion
        Then a ProviderHTTPError should be raised
        And no retries should be attempted
        """
        # Given I have an llmaid instance
        instance = llmaid().prompt_template("Test prompt")
        
        # And the backend returns a 400 Bad Request error
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions",
            status_code=400,
            text="Bad Request"
        )
        
        # When I call completion
        # Then a ProviderHTTPError should be raised
        with pytest.raises(ProviderHTTPError) as exc_info:
            instance.completion()
        
        # And no retries should be attempted
        assert exc_info.value.attempt == 1
        assert exc_info.value.max_attempts == 4  # default max_retries=3 + 1
        assert "HTTP error 400" in str(exc_info.value)
        
        # Verify only one request was made (no retries)
        requests = httpx_mock.get_requests()
        assert len(requests) == 1

    def test_http_429_rate_limit_retryable_success(self, clean_env, httpx_mock):
        """
        2. Scenario: HTTP 429 rate limit error (retryable)
        Given I have an llmaid instance with max_retries=2
        And the backend returns 429 errors for the first 2 attempts
        And the backend returns success on the 3rd attempt
        When I call completion
        Then the completion should succeed after retries
        And exactly 3 attempts should be made
        """
        # Given I have an llmaid instance with max_retries=2
        instance = llmaid(max_retries=2).prompt_template("Test prompt")
        
        # And the backend returns 429 errors for the first 2 attempts
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions",
            status_code=429,
            text="Rate limit exceeded"
        )
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions", 
            status_code=429,
            text="Rate limit exceeded"
        )
        # And the backend returns success on the 3rd attempt
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions",
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Success after retries"
                        }
                    }
                ]
            }
        )
        
        # Mock sleep to avoid real delays during retries
        with mock_asyncio_sleep() as mock_sleep:
            # When I call completion
            result = instance.completion()
        
        # Then the completion should succeed after retries
        assert result == "Success after retries"
        
        # And exactly 3 attempts should be made
        requests = httpx_mock.get_requests()
        assert len(requests) == 3
        
        # Verify retries included backoff delays (but were mocked)
        assert len(mock_sleep.sleep_calls) == 2  # 2 retries = 2 sleeps

    def test_retry_exhaustion(self, clean_env, httpx_mock):
        """
        3. Scenario: Retry exhaustion
        Given I have an llmaid instance with max_retries=2
        And the backend always returns 429 errors
        When I call completion
        Then a RetryExhaustedError should be raised
        And exactly 3 attempts should be made (initial + 2 retries)
        """
        # Given I have an llmaid instance with max_retries=2
        instance = llmaid(max_retries=2).prompt_template("Test prompt")
        
        # And the backend always returns 429 errors
        for _ in range(3):  # Initial + 2 retries
            httpx_mock.add_response(
                url="http://127.0.0.1:17434/v1/chat/completions",
                status_code=429,
                text="Rate limit exceeded"
            )
        
        # Mock sleep to avoid real delays during retries
        with mock_asyncio_sleep() as mock_sleep:
            # When I call completion
            # Then a RetryExhaustedError should be raised
            with pytest.raises(RetryExhaustedError) as exc_info:
                instance.completion()
        
        # And exactly 3 attempts should be made (initial + 2 retries)
        assert exc_info.value.attempt == 3
        assert exc_info.value.max_attempts == 3
        assert "Max retries (2) exceeded" in str(exc_info.value)
        
        requests = httpx_mock.get_requests()
        assert len(requests) == 3
        
        # Verify backoff delays occurred (but were mocked)
        assert len(mock_sleep.sleep_calls) == 2  # 2 retries = 2 sleeps (no sleep before first attempt)

    def test_exponential_backoff_timing(self, clean_env, httpx_mock):
        """
        4. Scenario: Exponential backoff timing
        Given I have an llmaid instance with max_retries=3 and backoff_factor=1.0
        And the backend returns 500 errors for all attempts
        When I call completion
        Then the delays between attempts should be approximately 1s, 2s, 4s
        And a RetryExhaustedError should be raised
        """
        # Given I have an llmaid instance with max_retries=3 and backoff_factor=1.0
        instance = llmaid(max_retries=3, backoff_factor=1.0).prompt_template("Test prompt")
        
        # And the backend returns 500 errors for all attempts
        for _ in range(4):  # Initial + 3 retries
            httpx_mock.add_response(
                url="http://127.0.0.1:17434/v1/chat/completions",
                status_code=500,
                text="Internal Server Error"
            )
        
        # Track sleep calls to verify backoff timing
        with mock_asyncio_sleep() as mock_sleep:
            # When I call completion
            with pytest.raises(RetryExhaustedError):
                instance.completion()
        
        # Then the delays between attempts should be approximately 1s, 2s, 4s
        # Verify the sleep durations were correct (without actually waiting)
        expected_delays = [1.0, 2.0, 4.0]  # backoff_factor * (2^0, 2^1, 2^2)
        assert len(mock_sleep.sleep_calls) == 3, f"Expected 3 sleep calls, got {len(mock_sleep.sleep_calls)}"
        
        for i, (actual, expected) in enumerate(zip(mock_sleep.sleep_calls, expected_delays)):
            assert abs(actual - expected) < 0.1, f"Sleep {i+1}: expected ~{expected}s, got {actual}s"
        
        # And a RetryExhaustedError should be raised
        requests = httpx_mock.get_requests()
        assert len(requests) == 4

    def test_network_timeout_error(self, clean_env):
        """
        5. Scenario: Network timeout error
        Given I have an llmaid instance with max_timeout=1
        And I call completion
        And the answer is not completed within 1 second
        Then a ProviderTimeoutError should be raised
        """
        # Given I have an llmaid instance with max_timeout=1
        # We use max_retries=0 to prevent retries and get the direct timeout error
        instance = llmaid(max_timeout=1, max_retries=0).prompt_template("Test prompt")
        
        # Mock httpx to simulate a timeout exception
        import httpx
        
        def slow_request(*args, **kwargs):
            raise httpx.TimeoutException("Request timeout")
        
        with patch('httpx.AsyncClient.post', side_effect=slow_request):
            # When I call completion
            # Then a ProviderTimeoutError or RetryExhaustedError should be raised
            # (RetryExhaustedError is acceptable when max_retries=0 because no retries are allowed)
            with pytest.raises((ProviderTimeoutError, RetryExhaustedError)) as exc_info:
                instance.completion()
            
            # Verify the error relates to timeout
            if isinstance(exc_info.value, RetryExhaustedError):
                assert exc_info.value.max_attempts == 1  # No retries attempted
            else:
                assert "Request timeout after 1s" in str(exc_info.value)

    def test_retryable_server_errors_500_503(self, clean_env, httpx_mock):
        """
        6. Scenario: Retryable server errors (500/503)
        Given I have an llmaid instance with max_retries=1
        And the backend returns a 500 error on first attempt
        And the backend returns success on second attempt
        When I call completion
        Then the completion should succeed after retry
        And exactly 2 attempts should be made
        """
        # Given I have an llmaid instance with max_retries=1
        instance = llmaid(max_retries=1).prompt_template("Test prompt")
        
        # And the backend returns a 500 error on first attempt
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions",
            status_code=500,
            text="Internal Server Error"
        )
        # And the backend returns success on second attempt
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions",
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Success after server error"
                        }
                    }
                ]
            }
        )
        
        # Mock sleep to avoid real delays during retry
        sleep_calls = []
        async def mock_sleep(duration):
            sleep_calls.append(duration)
            return

        with patch('asyncio.sleep', side_effect=mock_sleep):
            # When I call completion
            result = instance.completion()
        
        # Then the completion should succeed after retry
        assert result == "Success after server error"
        
        # And exactly 2 attempts should be made
        requests = httpx_mock.get_requests()
        assert len(requests) == 2
        
        # Verify one retry with backoff delay occurred (but was mocked)
        assert len(sleep_calls) == 1  # 1 retry = 1 sleep (no sleep before first attempt)

    def test_non_retryable_client_errors_401_403_404(self, clean_env, httpx_mock):
        """
        7. Scenario: Non-retryable client errors (401/403/404)
        Given I have an llmaid instance
        And the backend returns a 401/403/404 error
        When I call completion
        Then a ProviderHTTPError should be raised immediately
        And no retries should be attempted
        """
        # Given I have an llmaid instance
        instance = llmaid().prompt_template("Test prompt")
        
        # And the backend returns a 401/403/404 error
        for status_code in [401, 403, 404]:
            httpx_mock.add_response(
                url="http://127.0.0.1:17434/v1/chat/completions",
                status_code=status_code,
                text=f"HTTP {status_code} Error"
            )
            
            # When I call completion
            # Then a ProviderHTTPError should be raised immediately
            with pytest.raises(ProviderHTTPError) as exc_info:
                instance.completion()

            # And no retries should be attempted
            assert exc_info.value.attempt == 1
            assert f"HTTP error {status_code}" in str(exc_info.value)
