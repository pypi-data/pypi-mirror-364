"""
LLMAid exception hierarchy.

This module defines all custom exceptions used by LLMAid.
"""

from typing import Any


class LLMAidError(Exception):
    """Base exception for all LLMAid errors."""

    def __init__(
        self,
        message: str,
        attempt: int = 1,
        max_attempts: int = 1,
        last_response: Any = None,
    ):
        super().__init__(message)
        self.attempt = attempt
        self.max_attempts = max_attempts
        self.last_response = last_response


class ConfigurationError(LLMAidError):
    """Raised when invalid configuration parameters are provided."""

    pass


class TemplateMismatchError(LLMAidError):
    """Raised when template placeholders don't match provided arguments."""

    pass


class ProviderError(LLMAidError):
    """Base class for errors from LLM providers."""

    pass


class ProviderHTTPError(ProviderError):
    """HTTP 4XX/5XX errors that are non-retryable."""

    pass


class ProviderRateLimitError(ProviderError):
    """HTTP 429 rate limit errors (retryable)."""

    pass


class ProviderTimeoutError(ProviderError):
    """Network or HTTP timeout errors (retryable)."""

    pass


class RetryExhaustedError(LLMAidError):
    """Raised when max_retries is exceeded."""

    pass


class ContextLengthExceededError(LLMAidError):
    """Raised when prompt exceeds max context length and strict_context_length=True."""

    pass
