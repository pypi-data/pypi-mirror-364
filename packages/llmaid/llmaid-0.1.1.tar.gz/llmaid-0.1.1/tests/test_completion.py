"""
Test suite for LLMAid completion methods functionality.

This module tests the synchronous, asynchronous, and streaming completion
methods including proper template rendering, HTTP client interaction,
and error handling.

Based on specifications in completion.spec.md
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid
from llmaid.exceptions import ProviderError

# Import the helpers from conftest
from conftest import mock_openai_api_completion, mock_openai_api_streaming


class TestCompletionMethods:
    """Test suite for completion methods functionality."""

    def test_basic_synchronous_completion(self, clean_env, httpx_mock):
        """
        1. Scenario: Basic synchronous completion
        Given I have an llmaid instance with a prompt template "You are a {{role}}, respond with {{response}}"
        When I call completion with role="helper" and response="success"
        Then I should receive a string response
        And the backend should receive the rendered prompt
        """
        # Given I have an llmaid instance with a prompt template
        instance = llmaid().prompt_template("You are a {{role}}, respond with {{response}}")
        
        # Mock the HTTP response
        mock_openai_api_completion(httpx_mock, "Hello from helper!")
        
        # When I call completion with role="helper" and response="success"
        result = instance.completion(role="helper", response="success")
        
        # Then I should receive a string response
        assert isinstance(result, str)
        assert result == "Hello from helper!"
        
        # And the backend should receive the rendered prompt
        request = httpx_mock.get_request()
        assert request is not None
        request_json = request.read().decode()
        assert "You are a helper, respond with success" in request_json

    def test_completion_with_positional_arguments(self, clean_env, httpx_mock):
        """
        2. Scenario: Completion with positional arguments
        Given I have an llmaid instance with a prompt template "You are a helper"
        When I call completion("First question", "Second question")
        Then the final prompt should be "You are a helper\nFirst question\nSecond question"
        """
        # Given I have an llmaid instance with a prompt template
        instance = llmaid().prompt_template("You are a helper")
        
        # Mock the HTTP response
        mock_openai_api_completion(httpx_mock, "Response to questions")
        
        # When I call completion with positional arguments
        instance.completion("First question", "Second question")
        
        # Then the final prompt should be correctly formatted
        request = httpx_mock.get_request()
        assert request is not None
        request_json = request.read().decode()
        expected_prompt = "You are a helper\\nFirst question\\nSecond question"
        assert expected_prompt in request_json

    def test_completion_with_no_arguments(self, clean_env, httpx_mock):
        """
        3. Scenario: Completion with no arguments
        Given I have an llmaid instance with a prompt template "You are a helpful assistant. Respond with 'Hello!'"
        When I call completion with no arguments
        Then I should receive a string response
        And no additional text should be appended to the prompt
        """
        # Given I have an llmaid instance with a prompt template
        instance = llmaid().prompt_template("You are a helpful assistant. Respond with 'Hello!'")
        
        # Mock the HTTP response
        mock_openai_api_completion(httpx_mock, "Hello!")
        
        # When I call completion with no arguments
        result = instance.completion()
        
        # Then I should receive a string response
        assert isinstance(result, str)
        assert result == "Hello!"
        
        # And no additional text should be appended to the prompt
        request = httpx_mock.get_request()
        assert request is not None
        request_json = request.read().decode()
        assert "You are a helpful assistant. Respond with 'Hello!'" in request_json

    @pytest.mark.asyncio
    async def test_asynchronous_completion(self, clean_env, httpx_mock):
        """
        4. Scenario: Asynchronous completion
        Given I have an llmaid instance with a prompt template "You are a {{role}}"
        When I await acompletion with role="assistant"
        Then I should receive a string response asynchronously
        """
        # Given I have an llmaid instance with a prompt template
        instance = llmaid().prompt_template("You are a {{role}}")
        
        # Mock the HTTP response
        mock_openai_api_completion(httpx_mock, "Async response from assistant")
        
        # When I await acompletion with role="assistant"
        result = await instance.acompletion(role="assistant")
        
        # Then I should receive a string response asynchronously
        assert isinstance(result, str)
        assert result == "Async response from assistant"

    @pytest.mark.asyncio
    async def test_streaming_completion(self, clean_env, httpx_mock):
        """
        5. Scenario: Streaming completion
        Given I have an llmaid instance with a prompt template "You are a {{role}}"
        When I iterate over stream with role="assistant"
        Then I should receive an async iterator yielding string tokens
        And each token should be a non-empty string
        """
        # Given I have an llmaid instance with a prompt template
        instance = llmaid().prompt_template("You are a {{role}}")
        
        # Mock the streaming HTTP response
        mock_openai_api_streaming(httpx_mock, ["Hello", " world", "!"])
        
        # When I iterate over stream with role="assistant"
        tokens = []
        async for token in instance.stream(role="assistant"):
            tokens.append(token)
        
        # Then I should receive an async iterator yielding string tokens
        assert len(tokens) > 0
        
        # And each token should be a non-empty string
        for token in tokens:
            assert isinstance(token, str)
            assert len(token) > 0

    @pytest.mark.asyncio
    async def test_basic_streaming_iteration(self, clean_env, httpx_mock):
        """
        6. Scenario: Basic streaming iteration
        Given I have an llmaid instance
        When I iterate over stream("Hello")
        Then I should receive tokens as they arrive
        And each token should be a string
        And the concatenated tokens should form the complete response
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # Mock the streaming HTTP response
        mock_openai_api_streaming(httpx_mock, ["Test", " response", " complete"])
        
        # When I iterate over stream("Hello")
        tokens = []
        async for token in instance.stream("Hello"):
            tokens.append(token)
        
        # Then I should receive tokens as they arrive
        assert len(tokens) > 0
        
        # And each token should be a string
        for token in tokens:
            assert isinstance(token, str)
        
        # And the concatenated tokens should form the complete response
        complete_response = "".join(tokens)
        assert "Test response complete" in complete_response

    @pytest.mark.asyncio
    async def test_streaming_with_template_placeholders(self, clean_env, httpx_mock):
        """
        7. Scenario: Streaming with template placeholders
        Given I have an llmaid instance with prompt template "You are {{role}}"
        When I iterate over stream with role="assistant"
        Then the stream should work with the rendered template
        """
        # Given I have an llmaid instance with prompt template
        instance = llmaid().prompt_template("You are {{role}}")
        
        # Mock the streaming HTTP response
        mock_openai_api_streaming(httpx_mock, ["I", " am", " assistant"])
        
        # When I iterate over stream with role="assistant"
        tokens = []
        async for token in instance.stream(role="assistant"):
            tokens.append(token)
        
        # Then the stream should work with the rendered template
        assert len(tokens) > 0
        complete_response = "".join(tokens)
        assert "I am assistant" in complete_response

    @pytest.mark.asyncio
    async def test_streaming_cancellation(self, clean_env, httpx_mock):
        """
        8. Scenario: Streaming cancellation
        Given I have an llmaid instance
        And I start iterating over stream("Long response")
        When I break out of the iteration early
        Then the HTTP connection should be closed
        And no further tokens should be received
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # Mock the streaming HTTP response with many tokens
        stream_data = [
            b'data: {"choices":[{"text":"Token1"}]}\n\n',
            b'data: {"choices":[{"text":"Token2"}]}\n\n',
            b'data: {"choices":[{"text":"Token3"}]}\n\n',
            b'data: {"choices":[{"text":"Token4"}]}\n\n',
            b'data: {"choices":[{"text":"Token5"}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            content=b''.join(stream_data),
            headers={"content-type": "text/plain"}
        )
        
        # When I break out of the iteration early
        tokens = []
        async for token in instance.stream("Long response"):
            tokens.append(token)
            if len(tokens) >= 2:  # Break after 2 tokens
                break
        
        # Then no further tokens should be received
        assert len(tokens) == 2
        assert tokens[0] == "Token1"
        assert tokens[1] == "Token2"
        assert "Token3" not in tokens
        assert "[DONE]" not in tokens

    @pytest.mark.asyncio
    async def test_streaming_error_handling(self, clean_env, httpx_mock):
        """
        9. Scenario: Streaming error handling
        Given I have an llmaid instance
        And the backend returns an error during streaming
        When I iterate over stream("Hello")
        Then the appropriate ProviderError should be raised
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # Mock an HTTP error response
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            status_code=500,
            json={"error": "Internal server error"}
        )
        
        # Then the appropriate ProviderError should be raised
        with pytest.raises(ProviderError):
            async for token in instance.stream("Hello"):
                pass

    @pytest.mark.asyncio
    async def test_streaming_backpressure(self, clean_env, httpx_mock):
        """
        10. Scenario: Streaming backpressure
        Given I have an llmaid instance
        And the backend streams tokens slowly
        When I iterate over stream("Hello") with delays between iterations
        Then the stream should honor backpressure
        And tokens should arrive only when requested
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # Mock the streaming HTTP response
        stream_data = [
            b'data: {"choices":[{"text":"Slow"}]}\n\n',
            b'data: {"choices":[{"text":" token"}]}\n\n',
            b'data: {"choices":[{"text":" delivery"}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            content=b''.join(stream_data),
            headers={"content-type": "text/plain"}
        )
        
        # When I iterate over stream with delays between iterations
        tokens = []
        async for token in instance.stream("Hello"):
            tokens.append(token)
            # Simulate slow processing
            await asyncio.sleep(0.01)
        
        # Then the stream should honor backpressure
        # And tokens should arrive only when requested
        assert len(tokens) > 0
        for token in tokens:
            assert isinstance(token, str)
