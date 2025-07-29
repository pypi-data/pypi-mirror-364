"""
Test suite for LLMAid prompt template functionality.

This module tests the prompt template management features including
inline templates, file-based templates, template concatenation,
and template validation.

Based on specifications in prompt_template.spec.md
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid

# Import the helpers from conftest
from conftest import mock_openai_api_completion


class TestPromptTemplateManagement:
    """Test suite for prompt template management functionality."""

    def test_basic_inline_prompt_template(self, clean_env):
        """
        1. Scenario: Basic inline prompt template
        Given I have an llmaid instance
        When I call prompt_template("You are a {{role}} machine, only say {{action}}!")
        Then I should get a new llmaid instance
        And the new instance should have the prompt template "You are a {{role}} machine, only say {{action}}!"
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # When I call prompt_template("You are a {{role}} machine, only say {{action}}!")
        new_instance = instance.prompt_template("You are a {{role}} machine, only say {{action}}!")
        
        # Then I should get a new llmaid instance
        assert new_instance is not instance
        assert isinstance(new_instance, type(instance))
        
        # And the new instance should have the prompt template "You are a {{role}} machine, only say {{action}}!"
        assert new_instance._prompt_template == "You are a {{role}} machine, only say {{action}}!"

    def test_multiple_inline_templates_concatenation(self, clean_env):
        """
        2. Scenario: Multiple inline templates concatenation
        Given I have an llmaid instance
        When I call prompt_template("First part", "Second part", "Third part")
        Then I should get a new llmaid instance
        And the new instance should have the prompt template "First part\n\nSecond part\n\nThird part"
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # When I call prompt_template("First part", "Second part", "Third part")
        new_instance = instance.prompt_template("First part", "Second part", "Third part")
        
        # Then I should get a new llmaid instance
        assert new_instance is not instance
        assert isinstance(new_instance, type(instance))
        
        # And the new instance should have the prompt template "First part\n\nSecond part\n\nThird part"
        expected_template = "First part\n\nSecond part\n\nThird part"
        assert new_instance._prompt_template == expected_template

    def test_file_based_prompt_template(self, clean_env, tmp_path):
        """
        3. Scenario: File-based prompt template
        Given I have a file "test_prompt.txt" containing "You are a helpful {{role}}"
        And I have an llmaid instance with prompt_template_dir="./prompts"
        When I call prompt_template("test_prompt.txt")
        Then I should get a new llmaid instance
        And the new instance should have its prompt template set to the file content "You are a helpful {{role}}"
        """
        # Given I have a file "test_prompt.txt" containing "You are a helpful {{role}}"
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_file = prompts_dir / "test_prompt.txt"
        test_file.write_text("You are a helpful {{role}}")
        
        # And I have an llmaid instance with prompt_template_dir="./prompts"
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("test_prompt.txt")
        new_instance = instance.prompt_template("test_prompt.txt")
        
        # Then I should get a new llmaid instance
        assert new_instance is not instance
        assert isinstance(new_instance, type(instance))
        
        # And the new instance should have its prompt template set to the file content "You are a helpful {{role}}"
        assert new_instance._prompt_template == "You are a helpful {{role}}"

    def test_mixed_inline_and_file_templates(self, clean_env, tmp_path):
        """
        4. Scenario: Mixed inline and file templates
        Given I have a file "role.txt" containing "You are a {{role}}"
        And I have an llmaid instance with prompt_template_dir="./prompts"
        When I call prompt_template("role.txt", "Additional instructions: {{instructions}}")
        Then I should get a new llmaid instance
        And the templates should be concatenated with two newlines
        """
        # Given I have a file "role.txt" containing "You are a {{role}}"
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        role_file = prompts_dir / "role.txt"
        role_file.write_text("You are a {{role}}")
        
        # And I have an llmaid instance with prompt_template_dir="./prompts"
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("role.txt", "Additional instructions: {{instructions}}")
        new_instance = instance.prompt_template("role.txt", "Additional instructions: {{instructions}}")
        
        # Then I should get a new llmaid instance
        assert new_instance is not instance
        assert isinstance(new_instance, type(instance))
        
        # And the templates should be concatenated with two newlines
        expected_template = "You are a {{role}}\n\nAdditional instructions: {{instructions}}"
        assert new_instance._prompt_template == expected_template

    def test_system_prompt_alias(self, clean_env):
        """
        5. Scenario: System prompt alias
        Given I have an llmaid instance
        When I call system_prompt("You are a {{role}} assistant")
        Then I should get a new llmaid instance
        And the behavior should be identical to calling prompt_template
        """
        # Given I have an llmaid instance
        instance = llmaid()
        
        # When I call system_prompt("You are a {{role}} assistant")
        system_instance = instance.system_prompt("You are a {{role}} assistant")
        
        # Then I should get a new llmaid instance
        assert system_instance is not instance
        assert isinstance(system_instance, type(instance))
        
        # And the behavior should be identical to calling prompt_template
        prompt_instance = instance.prompt_template("You are a {{role}} assistant")
        assert system_instance._prompt_template == prompt_instance._prompt_template

    def test_strict_template_override(self, clean_env):
        """
        6. Scenario: Strict template override
        Given I have an llmaid instance with strict_template=True
        When I call prompt_template("Hello {{name}}", strict_template=False)
        Then the new instance should have strict_template False
        """
        # Given I have an llmaid instance with strict_template=True
        instance = llmaid(strict_template=True)
        
        # When I call prompt_template("Hello {{name}}", strict_template=False)
        new_instance = instance.prompt_template("Hello {{name}}", strict_template=False)
        
        # Then the new instance should have strict_template False
        assert new_instance.strict_template is False
        assert new_instance._prompt_template == "Hello {{name}}"

    def test_absolute_path_template_loading(self, clean_env, tmp_path):
        """
        7. Scenario: Absolute path template loading (within allowed directories)
        Given I have a file at an absolute path within the current working directory
        When I call prompt_template with that absolute path
        Then the file should be loaded directly
        """
        # Change to the temp directory so it's within our allowed directory
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Given I have a file at an absolute path within the current working directory
            abs_file = tmp_path / "prompt.txt"
            abs_file.write_text("Hello {{name}}")
            
            # Create instance with a different prompt_template_dir
            instance = llmaid(prompt_template_dir=str(tmp_path / "different_dir"))
            
            # When I call prompt_template with the absolute path
            new_instance = instance.prompt_template(str(abs_file))
            
            # Then the file should be loaded directly
            assert new_instance._prompt_template == "Hello {{name}}"
        
        finally:
            os.chdir(original_cwd)

    def test_relative_path_fallback_to_current_directory(self, clean_env, tmp_path):
        """
        8. Scenario: Relative path fallback to current directory
        Given I have an llmaid instance with no prompt_template_dir set
        And I have a file "local_prompt.txt" in the current directory
        When I call prompt_template("local_prompt.txt")
        Then the file should be loaded from the current directory
        """
        # Given I have an llmaid instance with no prompt_template_dir set
        instance = llmaid(prompt_template_dir=None)
        
        # And I have a file "local_prompt.txt" in the current directory
        current_dir = Path.cwd()
        local_file = current_dir / "local_prompt.txt"
        try:
            local_file.write_text("Local content {{var}}")
            
            # When I call prompt_template("local_prompt.txt")
            new_instance = instance.prompt_template("local_prompt.txt")
            
            # Then the file should be loaded from the current directory
            assert new_instance._prompt_template == "Local content {{var}}"
        finally:
            # Clean up
            if local_file.exists():
                local_file.unlink()

    def test_multiple_file_concatenation(self, clean_env, tmp_path):
        """
        9. Scenario: Multiple file concatenation
        Given I have files "part1.txt" and "part2.txt" in prompt directory
        And "part1.txt" contains "You are a {{role}}"
        And "part2.txt" contains "Task: {{task}}"
        When I call prompt_template("part1.txt", "part2.txt")
        Then the resulting template should be "You are a {{role}}\n\nTask: {{task}}"
        """
        # Given I have files "part1.txt" and "part2.txt" in prompt directory
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        part1_file = prompts_dir / "part1.txt"
        part2_file = prompts_dir / "part2.txt"
        
        # And "part1.txt" contains "You are a {{role}}"
        part1_file.write_text("You are a {{role}}")
        
        # And "part2.txt" contains "Task: {{task}}"
        part2_file.write_text("Task: {{task}}")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("part1.txt", "part2.txt")
        new_instance = instance.prompt_template("part1.txt", "part2.txt")
        
        # Then the resulting template should be "You are a {{role}}\n\nTask: {{task}}"
        expected_template = "You are a {{role}}\n\nTask: {{task}}"
        assert new_instance._prompt_template == expected_template

    def test_mixed_file_and_inline_templates(self, clean_env, tmp_path):
        """
        10. Scenario: Mixed file and inline templates
        Given I have file "role.txt" containing "You are a {{role}}"
        When I call prompt_template("role.txt", "Additional: {{note}}")
        Then the file content and inline text should be concatenated
        """
        # Given I have file "role.txt" containing "You are a {{role}}"
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        role_file = prompts_dir / "role.txt"
        role_file.write_text("You are a {{role}}")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("role.txt", "Additional: {{note}}")
        new_instance = instance.prompt_template("role.txt", "Additional: {{note}}")
        
        # Then the file content and inline text should be concatenated
        expected_template = "You are a {{role}}\n\nAdditional: {{note}}"
        assert new_instance._prompt_template == expected_template

    def test_nested_directory_template_loading(self, clean_env, tmp_path):
        """
        11. Scenario: Nested directory template loading
        Given I have "prompts/roles/scientist.txt" containing "You are a scientist"
        And prompt_template_dir is set to "prompts"
        When I call prompt_template("roles/scientist.txt")
        Then the file should be loaded successfully
        """
        # Given I have "prompts/roles/scientist.txt" containing "You are a scientist"
        prompts_dir = tmp_path / "prompts"
        roles_dir = prompts_dir / "roles"
        roles_dir.mkdir(parents=True)
        scientist_file = roles_dir / "scientist.txt"
        scientist_file.write_text("You are a scientist")
        
        # And prompt_template_dir is set to "prompts"
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("roles/scientist.txt")
        new_instance = instance.prompt_template("roles/scientist.txt")
        
        # Then the file should be loaded successfully
        assert new_instance._prompt_template == "You are a scientist"

    def test_template_file_not_found(self, clean_env, tmp_path):
        """
        12. Scenario: Template file not found
        Given prompt_template_dir is set to "prompts"
        And "nonexistent.txt" does not exist
        When I call prompt_template("nonexistent.txt")
        Then a FileNotFoundError should be raised
        """
        # Given prompt_template_dir is set to "prompts"
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # And "nonexistent.txt" does not exist
        # (implicit - file doesn't exist)
        
        # When I call prompt_template("nonexistent.txt")
        # Then a FileNotFoundError should be raised
        with pytest.raises(FileNotFoundError):
            instance.prompt_template("nonexistent.txt")

    def test_chat_history_through_templating(self, clean_env, httpx_mock):
        """
        13. Scenario: Chat history through templating
        Given I have a prompt template with {{chat_history}} and {{user_input}} placeholders
        And I have existing chat history "User: Hi\nAssistant: Hello"
        When I call completion with chat_history="User: Hi\nAssistant: Hello" and user_input="How are you?"
        Then the template should be rendered with both parameters
        And the completion should consider the chat context
        """
        # Given I have a prompt template with {{chat_history}} and {{user_input}} placeholders
        template = "Context:\n{{chat_history}}\n\nUser: {{user_input}}\nAssistant:"
        instance = llmaid().prompt_template(template)
        
        # Mock the HTTP response
        mock_openai_api_completion(httpx_mock, "I'm doing well, thank you!")
        
        # And I have existing chat history "User: Hi\nAssistant: Hello"
        chat_history = "User: Hi\nAssistant: Hello"
        
        # When I call completion with chat_history and user_input
        result = instance.completion(chat_history=chat_history, user_input="How are you?")
        
        # Then the template should be rendered with both parameters
        # And the completion should consider the chat context
        assert isinstance(result, str)
        assert result == "I'm doing well, thank you!"
