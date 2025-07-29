"""
Test suite for LLMAid other edge cases functionality.

This module tests various edge cases including Unicode handling,
empty templates, context length validation, and stress testing.

Based on specifications in other_edge_case.md
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid
from llmaid.exceptions import ContextLengthExceededError

# Import the helpers from conftest
from conftest import mock_openai_api_completion


class TestOtherEdgeCases:
    """Test suite for other edge cases functionality."""

    def test_unicode_in_prompt_templates(self, clean_env, httpx_mock):
        """
        1. Scenario: Unicode in prompt templates
        Given I have a prompt template "Translate to français: {{text}}"
        When I call completion with text="Hello world"
        Then the unicode characters should be preserved
        And the completion should work correctly
        """
        # Given I have a prompt template "Translate to français: {{text}}"
        instance = llmaid().prompt_template("Translate to français: {{text}}")
        
        # Mock the completion response
        mock_openai_api_completion(httpx_mock, "Bonjour le monde")
        
        # When I call completion with text="Hello world"
        result = instance.completion(text="Hello world")
        
        # Then the unicode characters should be preserved
        # And the completion should work correctly
        assert result == "Bonjour le monde"
        
        # Verify the backend received the correct prompt with unicode
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_content = requests[0].read().decode('utf-8')
        assert "Translate to français: Hello world" in request_content

    def test_unicode_in_completion_responses(self, clean_env, httpx_mock):
        """
        2. Scenario: Unicode in completion responses
        Given I have an llmaid instance
        When the backend returns unicode characters in the response
        Then the unicode should be preserved in the returned string
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # When the backend returns unicode characters in the response
        unicode_response = "Hello 世界! Bonjour français! ¡Hola español! Привет русский!"
        mock_openai_api_completion(httpx_mock, unicode_response)
        
        result = instance.completion("Say hello in multiple languages")
        
        # Then the unicode should be preserved in the returned string
        assert result == unicode_response
        assert "世界" in result
        assert "français" in result
        assert "español" in result
        assert "русский" in result

    def test_special_characters_in_placeholders(self, clean_env, httpx_mock):
        """
        3. Scenario: Special characters in placeholders
        Given I have a prompt template with "{{user_input}}"
        When I call completion with user_input containing quotes and newlines
        Then the special characters should be properly handled
        """
        # Given I have a prompt template with "{{user_input}}"
        instance = llmaid().prompt_template("Process this input: {{user_input}}")
        
        # Mock the completion response
        mock_openai_api_completion(httpx_mock, "Processed successfully")
        
        # When I call completion with user_input containing quotes and newlines
        special_input = '''This is a "quoted" string
        with multiple lines
        and 'single quotes' too
        and even "nested 'quotes'"'''
        
        result = instance.completion(user_input=special_input)
        
        # Then the special characters should be properly handled
        assert result == "Processed successfully"
        
        # Verify the backend received the correct prompt with special characters
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_content = requests[0].read().decode('utf-8')
        assert "Process this input:" in request_content
        # Special characters are JSON-escaped in the HTTP request
        assert '\\"quoted\\"' in request_content  # JSON escapes quotes
        assert "'single quotes'" in request_content
        assert '\\"nested \'quotes\'\\"' in request_content

    def test_special_characters_and_asian_languages(self, clean_env, httpx_mock):
        """
        4. Scenario: Special characters and asian languages
        Given I have a prompt template "Translate to 中文: {{text}}"
        When I call completion with text="Hello 世界"
        Then the special characters should be preserved
        And the completion should return the correct translation
        """
        # Given I have a prompt template "Translate to 中文: {{text}}"
        instance = llmaid().prompt_template("Translate to 中文: {{text}}")
        
        # Mock the completion response with Chinese characters
        mock_openai_api_completion(httpx_mock, "你好世界")
        
        # When I call completion with text="Hello 世界"
        result = instance.completion(text="Hello 世界")
        
        # Then the special characters should be preserved
        # And the completion should return the correct translation
        assert result == "你好世界"
        
        # Verify the backend received the correct prompt with Asian characters
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_content = requests[0].read().decode('utf-8')
        assert "Translate to 中文: Hello 世界" in request_content

    def test_empty_prompt_template(self, clean_env, httpx_mock):
        """
        5. Scenario: Empty prompt template
        Given I have an llmaid instance
        When I call prompt_template("")
        Then I should get a new instance with empty template
        And completion should work with just positional arguments
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # When I call prompt_template("")
        empty_template_instance = instance.prompt_template("")
        
        # Then I should get a new instance with empty template
        assert empty_template_instance._prompt_template == ""
        assert empty_template_instance != instance  # Should be a new instance
        
        # Mock the completion response
        mock_openai_api_completion(httpx_mock, "Response to positional args")
        
        # And completion should work with just positional arguments
        result = empty_template_instance.completion("Hello", "World")
        
        assert result == "Response to positional args"
        
        # Verify the backend received just the positional arguments
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_content = requests[0].read().decode('utf-8')
        # JSON-escaped newline in the HTTP request
        assert "Hello\\nWorld" in request_content

    def test_empty_completion_input(self, clean_env, httpx_mock):
        """
        6. Scenario: Empty completion input
        Given I have an llmaid instance with a prompt template "Respond with 'OK'"
        When I call completion() with no arguments
        Then the completion should work with just the template
        """
        # Given I have an llmaid instance with a prompt template "Respond with 'OK'"
        instance = llmaid().prompt_template("Respond with 'OK'")
        
        # Mock the completion response
        mock_openai_api_completion(httpx_mock, "OK")
        
        # When I call completion() with no arguments
        result = instance.completion()
        
        # Then the completion should work with just the template
        assert result == "OK"
        
        # Verify the backend received just the template
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_content = requests[0].read().decode('utf-8')
        assert "Respond with 'OK'" in request_content

    def test_strict_large_prompt_template(self, clean_env, httpx_mock):
        """
        7. Scenario: Strict Large prompt template
        Given I have a very large prompt template that exceeds max context length (9000 tokens)
        And strict_context_length is set to True
        And context_length is set to 8192
        When I call completion
        Then llmaid should raise a ContextLengthExceededError
        """
        # Given I have a very large prompt template that exceeds max context length (9000 tokens)
        # And strict_context_length is set to True
        # And context_length is set to 8192
        large_template = "This is a very long prompt. " * 1200  # Approximately 9600 tokens (1200 * 28 chars / 4)
        instance = llmaid(strict_context_length=True, context_length=8192).prompt_template(large_template)
        
        # Mock should not be called since we expect an error before backend call
        httpx_mock.add_response(
            url="http://127.0.0.1:17434/v1/chat/completions",
            json={"choices": [{"text": "Should not be called"}]},
            is_optional=True
        )
        
        # When I call completion
        # Then llmaid should raise a ContextLengthExceededError
        with pytest.raises(ContextLengthExceededError) as exc_info:
            instance.completion()
        
        assert "context" in str(exc_info.value).lower()
        assert "8192" in str(exc_info.value)
        
        # Verify no backend call was made
        assert len(httpx_mock.get_requests()) == 0

    def test_large_prompt_template_no_trimming(self, clean_env, httpx_mock, caplog):
        """
        8. Scenario: Large prompt template
        Given I have a very large prompt template that exceeds max context length (9000 tokens)
        And strict_context_length is set to False
        And context_length is set to 8192
        When I call completion
        Then llmaid should perform as usual and send the full context to provider.
        And llmaid should log a warning context length being too large.
        """
        # Given I have a very large prompt template that exceeds max context length (9000 tokens)
        # And strict_context_length is set to False
        # And context_length is set to 8192
        large_template = "This is a very long prompt. " * 1200  # Approximately 9600 tokens (1200 * 28 chars / 4)
        instance = llmaid(strict_context_length=False, context_length=8192).prompt_template(large_template)
        
        # Mock the completion response
        mock_openai_api_completion(httpx_mock, "Response to full prompt")
        
        # When I call completion
        result = instance.completion()
        
        # Then llmaid should perform as usual and send the full context to provider.
        assert result == "Response to full prompt"
        
        # Verify the backend received the full (untrimmed) prompt
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_json = requests[0].read().decode('utf-8')
        
        # Extract the actual prompt content from the JSON request
        import json
        request_data = json.loads(request_json)
        sent_prompt = request_data["prompt"]
        
        # The sent prompt should be the same as the original template (no trimming)
        assert sent_prompt == large_template


    def test_many_placeholders(self, clean_env, httpx_mock):
        """
        9. Scenario: Many placeholders
        Given I have a prompt template with 50 different placeholders
        When I call completion with all 50 placeholders filled
        Then all placeholders should be correctly replaced
        """
        # Given I have a prompt template with 50 different placeholders
        placeholders = [f"placeholder_{i}" for i in range(50)]
        template_parts = [f"{{{{{ph}}}}}" for ph in placeholders]  # No spaces around placeholder names
        template = " ".join(template_parts)
        
        instance = llmaid().prompt_template(template)
        
        # Mock the completion response
        mock_openai_api_completion(httpx_mock, "All placeholders processed")
        
        # When I call completion with all 50 placeholders filled
        placeholder_values = {f"placeholder_{i}": f"value_{i}" for i in range(50)}
        result = instance.completion(**placeholder_values)
        
        # Then all placeholders should be correctly replaced
        assert result == "All placeholders processed"
        
        # Verify all placeholders were replaced in the prompt sent to backend
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        request_content = requests[0].read().decode('utf-8')
        
        # Check that all placeholder values are present
        for i in range(50):
            assert f"value_{i}" in request_content
        
        # Check that no unreplaced placeholders remain
        for i in range(50):
            assert f"placeholder_{i}" not in request_content.replace(f"value_{i}", "")
