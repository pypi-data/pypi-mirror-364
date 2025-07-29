"""
Test suite for LLMAid client base URL handling functionality.

This module tests that different base URL formats are properly normalized
and result in correct endpoint URLs being called.

Based on specifications in client.spec.md
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid
from llmaid.client import LLMClient


class TestClientBaseURLHandling:
    """Test suite for client base URL handling functionality."""

    @pytest.mark.parametrize("base_url,expected_url", [
        # Standard OpenRouter base URL with /api/v1
        ("https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1/completions"),
        # OpenRouter base URL with /api/v1/ trailing slash
        ("https://openrouter.ai/api/v1/", "https://openrouter.ai/api/v1/completions"),
        # OpenRouter base URL with /api/ trailing slash
        ("https://openrouter.ai/api/", "https://openrouter.ai/api/completions"),
        # OpenRouter base URL with root / trailing slash
        ("https://openrouter.ai/", "https://openrouter.ai/completions"),
        # OpenRouter base URL without trailing slash
        ("https://openrouter.ai", "https://openrouter.ai/completions"),
        # OpenAI-style base URL
        ("https://api.openai.com/v1", "https://api.openai.com/v1/completions"),
        # Custom provider base URL normalization
        ("https://custom-provider.com/api/v2/", "https://custom-provider.com/api/v2/completions"),
    ])
    def test_base_url_normalization_sync(self, httpx_mock, base_url, expected_url):
        """
        Test that various base URL formats result in correct endpoint URLs for sync completion.
        
        Given I create an llmaid client with different base_url formats
        When I make a completion request
        Then the HTTP request should be sent to the correct normalized URL
        """
        # Mock the completion endpoint response
        httpx_mock.add_response(
            url=expected_url,
            json={
                "choices": [
                    {
                        "text": "Test completion response"
                    }
                ]
            }
        )
        
        # Given I create an llmaid client with the base_url
        instance = llmaid(
            base_url=base_url,
            secret="test-secret",
            model="test-model"
        )
        
        # When I make a completion request
        result = instance.completion("Test prompt")
        
        # Then the HTTP request should be sent to the correct URL
        assert result == "Test completion response"
        
        # Verify the mock was called with the expected URL
        request = httpx_mock.get_request()
        assert str(request.url) == expected_url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("base_url,expected_url", [
        ("https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1/completions"),
        ("https://openrouter.ai/api/v1/", "https://openrouter.ai/api/v1/completions"),
        ("https://api.openai.com/v1", "https://api.openai.com/v1/completions"),
    ])
    async def test_base_url_normalization_async(self, httpx_mock, base_url, expected_url):
        """
        Test that various base URL formats result in correct endpoint URLs for async completion.
        
        Given I create an llmaid client with different base_url formats
        When I make an async completion request
        Then the HTTP request should be sent to the correct normalized URL
        """
        # Mock the completion endpoint response
        httpx_mock.add_response(
            url=expected_url,
            json={
                "choices": [
                    {
                        "text": "Test async completion response"
                    }
                ]
            }
        )
        
        # Given I create an llmaid client with the base_url
        instance = llmaid(
            base_url=base_url,
            secret="test-secret",
            model="test-model"
        )
        
        # When I make an async completion request
        result = await instance.acompletion("Test prompt")
        
        # Then the HTTP request should be sent to the correct URL
        assert result == "Test async completion response"
        
        # Verify the mock was called with the expected URL
        request = httpx_mock.get_request()
        assert str(request.url) == expected_url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("base_url,expected_url", [
        ("https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1/completions"),
        ("https://openrouter.ai/api/v1/", "https://openrouter.ai/api/v1/completions"),
    ])
    async def test_base_url_normalization_streaming(self, httpx_mock, base_url, expected_url):
        """
        Test that various base URL formats result in correct endpoint URLs for streaming completion.
        
        Given I create an llmaid client with different base_url formats
        When I make a streaming completion request
        Then the HTTP request should be sent to the correct normalized URL
        """
        # Mock the streaming completion endpoint response
        stream_data = [
            b'data: {"choices":[{"text":"Hello"}]}\n\n',
            b'data: {"choices":[{"text":" world"}]}\n\n',
            b'data: {"choices":[{"text":"!"}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        
        httpx_mock.add_response(
            url=expected_url,
            content=b''.join(stream_data),
            headers={"content-type": "text/plain"}
        )
        
        # Given I create an llmaid client with the base_url
        instance = llmaid(
            base_url=base_url,
            secret="test-secret",
            model="test-model"
        )
        
        # When I make a streaming completion request
        tokens = []
        async for token in instance.stream("Test prompt"):
            tokens.append(token)
        
        # Then the HTTP request should be sent to the correct URL
        assert tokens == ["Hello", " world", "!"]
        
        # Verify the mock was called with the expected URL
        request = httpx_mock.get_request()
        assert str(request.url) == expected_url

    def test_trailing_slash_removal(self):
        """
        Test that trailing slashes are properly removed from base URLs.
        
        Given I create an llmaid client with any base_url ending with "/"
        When the client normalizes the base URL
        Then the trailing slash should be removed before appending endpoints
        And the final URL should not contain double slashes
        """
        test_cases = [
            ("https://example.com/", "https://example.com"),
            ("https://example.com/api/", "https://example.com/api"),
            ("https://example.com/api/v1/", "https://example.com/api/v1"),
            ("https://example.com", "https://example.com"),  # No trailing slash
        ]
        
        for input_url, expected_normalized in test_cases:
            client = LLMClient(base_url=input_url, secret="test-secret")
            assert client.base_url == expected_normalized
            
            # Verify that appending endpoints doesn't create double slashes
            full_url = f"{client.base_url}/completions"
            assert "//" not in full_url.replace("https://", "").replace("http://", "")

    def test_request_body_format(self, httpx_mock):
        """
        Test that the request body uses the correct completions format.
        
        Given I create an llmaid client
        When I make a completion request
        Then the request body should use 'prompt' field instead of 'messages' array
        """
        # Mock the completion response
        httpx_mock.add_response(
            url="https://api.openai.com/v1/completions",
            json={
                "choices": [
                    {
                        "text": "Test response"
                    }
                ]
            }
        )
        
        # Given I create an llmaid client
        instance = llmaid(
            base_url="https://api.openai.com/v1",
            secret="test-secret",
            model="test-model"
        )
        
        # When I make a completion request
        result = instance.completion("Test prompt")
        
        # Then the request should succeed
        assert result == "Test response"
        
        # And the request body should have the correct format
        request = httpx_mock.get_request()
        request_body = request.read()
        import json
        body_data = json.loads(request_body)
        
        # Should use prompt field, not messages
        assert "prompt" in body_data
        assert "messages" not in body_data
        assert body_data["prompt"] == "Test prompt"
        assert body_data["model"] == "test-model"
        assert body_data["stream"] is False
