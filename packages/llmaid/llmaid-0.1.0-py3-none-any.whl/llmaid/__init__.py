"""
LLMAid - A zero-dependency wrapper that turns any OpenAI-compatible endpoint into a one-liner.

This module provides the main LLMAid class and factory function for creating instances.
"""

from .core import LLMAid
from .exceptions import (
    LLMAidError,
    ConfigurationError,
    TemplateMismatchError,
    ProviderError,
    ProviderHTTPError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    RetryExhaustedError,
)


# Main factory function - this is what users import and call
def llmaid(**config):
    """
    Create a new LLMAid instance with the given configuration.

    Args:
        **config: Configuration options for the LLMAid instance

    Returns:
        LLMAid: A configured LLMAid instance
    """
    return LLMAid(**config)


# Export the main interface
__all__ = [
    "llmaid",
    "LLMAid",
    "LLMAidError",
    "ConfigurationError",
    "TemplateMismatchError",
    "ProviderError",
    "ProviderHTTPError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "RetryExhaustedError",
]
