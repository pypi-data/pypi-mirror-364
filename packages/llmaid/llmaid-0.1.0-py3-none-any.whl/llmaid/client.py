"""
HTTP client for LLMAid completion requests.

This module handles all HTTP communication with LLM providers,
including synchronous, asynchronous, and streaming requests.
"""

import json
import asyncio
from typing import AsyncIterator, Dict, Any, Optional
import httpx

from .exceptions import (
    ProviderError, 
    ProviderHTTPError, 
    ProviderRateLimitError, 
    ProviderTimeoutError,
    RetryExhaustedError
)


class LLMClient:
    """HTTP client for LLM completions with retry and error handling."""
    
    def __init__(
        self,
        base_url: str,
        secret: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        max_timeout: int = 60,
    ):
        """
        Initialize LLM HTTP client.
        
        Args:
            base_url: Base URL for the LLM API
            secret: Authentication token
            max_retries: Maximum number of retry attempts
            backoff_factor: Base seconds for exponential backoff
            max_timeout: Timeout in seconds for requests
        """
        self.base_url = base_url.rstrip('/')
        self.secret = secret
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_timeout = max_timeout
        
        # Build headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "LLMAid/0.1.0"
        }
        if self.secret:
            self.headers["Authorization"] = f"Bearer {self.secret}"
    
    def _build_request_body(
        self, 
        prompt: str, 
        model: str,
        stream: bool = False,
        **generation_params: Any
    ) -> Dict[str, Any]:
        """
        Build the request body for OpenAI-compatible API.
        
        Args:
            prompt: The rendered prompt text
            model: Model name to use
            stream: Whether to enable streaming
            **generation_params: Additional generation parameters
            
        Returns:
            Dict containing the request body
        """
        body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": stream
        }
        
        # Add generation parameters if provided
        for param, value in generation_params.items():
            if value is not None:
                body[param] = value
                
        return body
    
    def _handle_error_response(self, response: httpx.Response, attempt: int = 1) -> None:
        """
        Handle HTTP error responses and raise appropriate exceptions.
        
        Args:
            response: The HTTP response object
            attempt: Current attempt number
            
        Raises:
            ProviderRateLimitError: For 429 rate limit errors (retryable)
            ProviderHTTPError: For 4XX client errors (non-retryable)
            ProviderError: For 5XX server errors (retryable, but not timeout/rate-limit specific)
        """
        if response.status_code == 429:
            raise ProviderRateLimitError(
                f"Rate limit exceeded (HTTP {response.status_code})",
                attempt=attempt,
                max_attempts=self.max_retries + 1,
                last_response=response
            )
        elif 400 <= response.status_code < 500:
            # 4XX client errors are non-retryable
            raise ProviderHTTPError(
                f"HTTP error {response.status_code}: {response.text}",
                attempt=attempt,
                max_attempts=self.max_retries + 1,
                last_response=response
            )
        elif 500 <= response.status_code < 600:
            # 5XX server errors are retryable
            raise ProviderError(
                f"Server error {response.status_code}: {response.text}",
                attempt=attempt,
                max_attempts=self.max_retries + 1,
                last_response=response
            )
        else:
            # Other status codes (shouldn't happen but handle gracefully)
            raise ProviderHTTPError(
                f"HTTP error {response.status_code}: {response.text}",
                attempt=attempt,
                max_attempts=self.max_retries + 1,
                last_response=response
            )

    def _handle_exception(self, exception: Exception, attempt: int) -> Exception:
        """
        Convert raw exceptions to appropriate LLMAid exceptions with friendly messages.
        
        Args:
            exception: The raw exception that occurred
            attempt: Current attempt number
            
        Returns:
            Exception: The appropriate LLMAid exception to raise or store
        """
        if isinstance(exception, httpx.TimeoutException):
            return ProviderTimeoutError(
                f"Request timeout after {self.max_timeout}s",
                attempt=attempt,
                max_attempts=self.max_retries + 1
            )
        elif isinstance(exception, (httpx.ConnectError, httpx.NetworkError)):
            return ProviderError(
                f"Network error: {str(exception)}",
                attempt=attempt,
                max_attempts=self.max_retries + 1
            )
        elif isinstance(exception, (ProviderError, ProviderHTTPError, ProviderRateLimitError, ProviderTimeoutError)):
            # Already an LLMAid exception, return as-is
            return exception
        else:
            # Unexpected exception, wrap it
            return ProviderError(
                f"Unexpected error: {str(exception)}",
                attempt=attempt,
                max_attempts=self.max_retries + 1
            )
    
    def _should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception is retryable.
        
        Args:
            exception: The exception that occurred
            
        Returns:
            bool: True if the exception is retryable
        """
        return isinstance(exception, (
            ProviderRateLimitError,
            ProviderTimeoutError,
            ProviderError,  # General provider errors (5XX server errors)
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError
        )) and not isinstance(exception, ProviderHTTPError)  # Exclude non-retryable HTTP errors
    
    async def _retry_with_backoff(self, attempt: int) -> None:
        """
        Wait with exponential backoff before retrying.
        
        Args:
            attempt: Current attempt number (1-based)
        """
        if attempt > 1:
            wait_time = self.backoff_factor * (2 ** (attempt - 2))
            await asyncio.sleep(wait_time)
    
    def completion(
        self, 
        prompt: str, 
        model: str,
        **generation_params: Any
    ) -> str:
        """
        Perform synchronous completion request.
        
        Args:
            prompt: The rendered prompt text
            model: Model name to use
            **generation_params: Additional generation parameters
            
        Returns:
            str: The completion response text
            
        Raises:
            ProviderError: For API errors
            RetryExhaustedError: When max retries exceeded
        """
        return asyncio.run(self.acompletion(prompt, model, **generation_params))
    
    async def acompletion(
        self, 
        prompt: str, 
        model: str,
        **generation_params: Any
    ) -> str:
        """
        Perform asynchronous completion request.
        
        Args:
            prompt: The rendered prompt text
            model: Model name to use
            **generation_params: Additional generation parameters
            
        Returns:
            str: The completion response text
            
        Raises:
            ProviderError: For API errors
            RetryExhaustedError: When max retries exceeded
        """
        url = f"{self.base_url}/v1/chat/completions"
        body = self._build_request_body(prompt, model, stream=False, **generation_params)
        
        last_exception = None
        
        for attempt in range(1, self.max_retries + 2):  # +1 for initial attempt
            try:
                await self._retry_with_backoff(attempt)
                
                async with httpx.AsyncClient(timeout=self.max_timeout) as client:
                    response = await client.post(url, json=body, headers=self.headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        self._handle_error_response(response, attempt)
                        
            except Exception as e:
                # Convert all exceptions to appropriate LLMAid exceptions
                last_exception = self._handle_exception(e, attempt)
                
                if not self._should_retry(last_exception):
                    # Non-retryable error, raise immediately
                    raise last_exception
                elif attempt > self.max_retries:
                    # Retryable but exceeded max attempts, break to raise RetryExhaustedError
                    break
        
        # If we've exhausted retries
        raise RetryExhaustedError(
            f"Max retries ({self.max_retries}) exceeded",
            attempt=self.max_retries + 1,
            max_attempts=self.max_retries + 1,
            last_response=getattr(last_exception, 'last_response', None)
        )
    
    async def stream(
        self, 
        prompt: str, 
        model: str,
        **generation_params: Any
    ) -> AsyncIterator[str]:
        """
        Perform streaming completion request.
        
        Args:
            prompt: The rendered prompt text
            model: Model name to use
            **generation_params: Additional generation parameters
            
        Yields:
            str: Response tokens as they arrive
            
        Raises:
            ProviderError: For API errors
        """
        url = f"{self.base_url}/v1/chat/completions"
        body = self._build_request_body(prompt, model, stream=True, **generation_params)
        
        try:
            async with httpx.AsyncClient(timeout=self.max_timeout) as client:
                async with client.stream("POST", url, json=body, headers=self.headers) as response:
                    if response.status_code != 200:
                        # Read the response body for error details
                        await response.aread()
                        self._handle_error_response(response)
                    
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                # Skip malformed JSON lines
                                continue
                                
        except httpx.TimeoutException:
            raise ProviderTimeoutError(
                f"Streaming request timeout after {self.max_timeout}s"
            )
        except (httpx.ConnectError, httpx.NetworkError) as e:
            raise ProviderError(f"Network error during streaming: {str(e)}")
        except Exception as e:
            if not isinstance(e, ProviderError):
                raise ProviderError(f"Unexpected error during streaming: {str(e)}")
            raise e
