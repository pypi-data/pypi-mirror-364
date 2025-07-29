"""
Test suite for LLMAid template validation functionality.

This module tests the template validation features including
strict template validation, placeholder mismatch detection,
and error handling for template validation scenarios.

Based on specifications in template_validation.spec.md
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid
from llmaid.exceptions import TemplateMismatchError

# Import the helpers from conftest
from conftest import mock_openai_api_completion


class TestTemplateValidation:
    """Test suite for template validation functionality."""

    def test_strict_template_with_missing_placeholders(self, clean_env, httpx_mock):
        """
        1. Scenario: Strict template with missing placeholders
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}, you are {{role}}"
        When I call completion with only name="John"
        Then a TemplateMismatchError should be raised
        And the error should indicate missing placeholder "role"
        And no backend call should be made
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}, you are {{role}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}, you are {{role}}")
        
        # Set up mock but verify it's never called
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            json={"choices": [{"text": "Should not be called"}]},
            is_optional=True
        )
        
        # When I call completion with only name="John"
        # Then a TemplateMismatchError should be raised
        with pytest.raises(TemplateMismatchError) as exc_info:
            instance.completion(name="John")
        
        # And the error should indicate missing placeholder "role"
        assert "role" in str(exc_info.value)
        assert "missing" in str(exc_info.value).lower()
        
        # And no backend call should be made
        assert len(httpx_mock.get_requests()) == 0

    def test_strict_template_with_extra_placeholders(self, clean_env, httpx_mock):
        """
        2. Scenario: Strict template with extra placeholders
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}"
        When I call completion with name="John" and extra="parameter"
        Then a TemplateMismatchError should be raised
        And the error should indicate unexpected placeholder "extra"
        And no backend call should be made
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}")
        
        # Set up mock but verify it's never called
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            json={"choices": [{"text": "Should not be called"}]},
            is_optional=True
        )
        
        # When I call completion with name="John" and extra="parameter"
        # Then a TemplateMismatchError should be raised
        with pytest.raises(TemplateMismatchError) as exc_info:
            instance.completion(name="John", extra="parameter")
        
        # And the error should indicate unexpected placeholder "extra"
        assert "extra" in str(exc_info.value)
        assert "unexpected" in str(exc_info.value).lower() or "unknown" in str(exc_info.value).lower()
        
        # And no backend call should be made
        assert len(httpx_mock.get_requests()) == 0

    def test_non_strict_template_with_missing_placeholders(self, clean_env, httpx_mock):
        """
        3. Scenario: Non-strict template with missing placeholders
        Given I have an llmaid instance with strict_template=False
        And a prompt template "Hello {{name}}, you are {{role}}"
        When I call completion with only name="John"
        Then the completion should succeed
        And "{{role}}" should remain unreplaced in the final prompt
        And no backend call should be made
        """
        # Given I have an llmaid instance with strict_template=False
        # And a prompt template "Hello {{name}}, you are {{role}}"
        instance = llmaid(strict_template=False).prompt_template("Hello {{name}}, you are {{role}}")
        
        # Mock the backend response
        mock_openai_api_completion(httpx_mock, "Response with unreplaced template")
        
        # When I call completion with only name="John"
        result = instance.completion(name="John")
        
        # Then the completion should succeed
        assert isinstance(result, str)
        assert result == "Response with unreplaced template"
        
        # And "{{role}}" should remain unreplaced in the final prompt
        # Verify the request was made with the expected prompt
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_json = requests[0].read().decode()
        assert "Hello John, you are {{role}}" in request_json

    def test_non_strict_template_with_extra_placeholders(self, clean_env, httpx_mock):
        """
        4. Scenario: Non-strict template with extra placeholders
        Given I have an llmaid instance with strict_template=False
        And a prompt template "Hello {{name}}"
        When I call completion with name="John" and extra="parameter"
        Then the completion should succeed
        And the extra parameter should be ignored
        """
        # Given I have an llmaid instance with strict_template=False
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=False).prompt_template("Hello {{name}}")
        
        # Mock the backend response
        mock_openai_api_completion(httpx_mock, "Response with extra ignored")
        
        # When I call completion with name="John" and extra="parameter"
        result = instance.completion(name="John", extra="parameter")
        
        # Then the completion should succeed
        assert isinstance(result, str)
        assert result == "Response with extra ignored"
        
        # And the extra parameter should be ignored
        # Verify the request was made with the expected prompt (only name replaced)
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_json = requests[0].read().decode()
        assert "Hello John" in request_json
        assert "parameter" not in request_json

    def test_happy_path_with_all_placeholders(self, clean_env, httpx_mock):
        """
        5. Scenario: Happy path with all placeholders
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}, you are {{role}}"
        When I call completion with name="John" and role="Developer"
        Then the completion should succeed
        And the final prompt should be "Hello John, you are Developer"
        And the backend should receive the rendered prompt
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}, you are {{role}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}, you are {{role}}")
        
        # Mock the backend response
        mock_openai_api_completion(httpx_mock, "Success response")
        
        # When I call completion with name="John" and role="Developer"
        result = instance.completion(name="John", role="Developer")
        
        # Then the completion should succeed
        assert isinstance(result, str)
        assert result == "Success response"
        
        # And the final prompt should be "Hello John, you are Developer"
        # And the backend should receive the rendered prompt
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_json = requests[0].read().decode()
        assert "Hello John, you are Developer" in request_json

    def test_template_mismatch_before_backend_call(self, clean_env, httpx_mock):
        """
        6. Scenario: Template mismatch before backend call
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}"
        When I call completion with role="assistant" (wrong placeholder)
        Then a TemplateMismatchError should be raised
        And no backend call should be made
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}")
        
        # Set up mock but verify it's never called
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            json={"choices": [{"text": "Should not be called"}]},
            is_optional=True
        )
        
        # When I call completion with role="assistant" (wrong placeholder)
        # Then a TemplateMismatchError should be raised
        with pytest.raises(TemplateMismatchError) as exc_info:
            instance.completion(role="assistant")
        
        # The error should indicate both missing "name" and unexpected "role"
        error_msg = str(exc_info.value).lower()
        assert "name" in error_msg
        assert "role" in error_msg
        
        # And no backend call should be made
        assert len(httpx_mock.get_requests()) == 0

    def test_async_completion_with_strict_template_validation(self, clean_env, httpx_mock):
        """
        7. Scenario: Async completion with strict template validation
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}"
        When I call acompletion with role="assistant" (wrong placeholder)
        Then a TemplateMismatchError should be raised
        And no backend call should be made
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}")
        
        # Set up mock but verify it's never called
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            json={"choices": [{"text": "Should not be called"}]},
            is_optional=True
        )
        
        # When I call acompletion with role="assistant" (wrong placeholder)
        # Then a TemplateMismatchError should be raised
        import asyncio
        
        async def test_async():
            with pytest.raises(TemplateMismatchError) as exc_info:
                await instance.acompletion(role="assistant")
            
            # The error should indicate both missing "name" and unexpected "role"
            error_msg = str(exc_info.value).lower()
            assert "name" in error_msg
            assert "role" in error_msg
            return True
        
        # Run the async test
        result = asyncio.run(test_async())
        assert result
        
        # And no backend call should be made
        assert len(httpx_mock.get_requests()) == 0

    def test_async_completion_with_valid_placeholders(self, clean_env, httpx_mock):
        """
        8. Scenario: Async completion with valid placeholders
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}"
        When I call acompletion with name="Alice"
        Then the completion should succeed
        And the backend should receive the rendered prompt "Hello Alice"
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}")
        
        # Mock the backend response
        mock_openai_api_completion(httpx_mock, "Async success response")
        
        # When I call acompletion with name="Alice"
        import asyncio
        
        async def test_async():
            result = await instance.acompletion(name="Alice")
            return result
        
        result = asyncio.run(test_async())
        
        # Then the completion should succeed
        assert isinstance(result, str)
        assert result == "Async success response"
        
        # And the backend should receive the rendered prompt "Hello Alice"
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_json = requests[0].read().decode()
        assert "Hello Alice" in request_json

    def test_streaming_completion_with_strict_template_validation(self, clean_env, httpx_mock):
        """
        9. Scenario: Streaming completion with strict template validation
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}"
        When I call stream with role="assistant" (wrong placeholder)
        Then a TemplateMismatchError should be raised
        And no backend call should be made
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}")
        
        # Set up mock but verify it's never called
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/completions",
            json={"choices": [{"text": "Should not be called"}]},
            is_optional=True
        )
        
        # When I call stream with role="assistant" (wrong placeholder)
        # Then a TemplateMismatchError should be raised
        import asyncio
        
        async def test_streaming():
            with pytest.raises(TemplateMismatchError) as exc_info:
                async for chunk in instance.stream(role="assistant"):
                    # Should not get here
                    assert False, "Should not receive any chunks"
            
            # The error should indicate both missing "name" and unexpected "role"
            error_msg = str(exc_info.value).lower()
            assert "name" in error_msg
            assert "role" in error_msg
            return True
        
        # Run the async test
        result = asyncio.run(test_streaming())
        assert result
        
        # And no backend call should be made
        assert len(httpx_mock.get_requests()) == 0

    def test_streaming_completion_with_valid_placeholders(self, clean_env, httpx_mock):
        """
        10. Scenario: Streaming completion with valid placeholders
        Given I have an llmaid instance with strict_template=True
        And a prompt template "Hello {{name}}"
        When I call stream with name="Bob"
        Then the streaming should succeed
        And the backend should receive the rendered prompt "Hello Bob"
        """
        # Given I have an llmaid instance with strict_template=True
        # And a prompt template "Hello {{name}}"
        instance = llmaid(strict_template=True).prompt_template("Hello {{name}}")
        
        # Import the streaming mock helper from conftest
        from conftest import mock_openai_api_streaming
        
        # Mock the backend streaming response
        mock_openai_api_streaming(httpx_mock, ["Stream", " chunk", " test"])
        
        # When I call stream with name="Bob"
        import asyncio
        
        async def test_streaming():
            chunks = []
            async for chunk in instance.stream(name="Bob"):
                chunks.append(chunk)
            return chunks
        
        chunks = asyncio.run(test_streaming())
        
        # Then the streaming should succeed
        assert isinstance(chunks, list)
        assert len(chunks) == 3
        assert chunks == ["Stream", " chunk", " test"]
        
        # And the backend should receive the rendered prompt "Hello Bob"
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_json = requests[0].read().decode()
        assert "Hello Bob" in request_json
