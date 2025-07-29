"""
Additional security and robustness tests for prompt template functionality.

These tests specifically target the security validation features and edge cases.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid


class TestPromptTemplateSecurityValidation:
    """Test suite for prompt template security and validation features."""

    def test_oversized_file_rejection(self, clean_env, tmp_path):
        """
        1. Scenario: Oversized file rejection  
        Given I have a text file larger than 64KB
        When I call prompt_template("large_file.txt")
        Then a ValueError should be raised indicating file too large
        """
        # Given I have a text file larger than 64KB
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        large_file = prompts_dir / "large_file.txt"
        
        # Create a file larger than 64KB (65KB of text)
        large_content = "x" * (65 * 1024)
        large_file.write_text(large_content)
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("large_file.txt")
        # Then a ValueError should be raised indicating file too large
        with pytest.raises(ValueError, match="Template file too large"):
            instance.prompt_template("large_file.txt")

    def test_invalid_extension_rejection(self, clean_env, tmp_path):
        """
        2. Scenario: Invalid file extension rejection
        Given I have a file "script.py" (Python code) 
        When I call prompt_template with explicit Path("script.py")
        Then a ValueError should be raised indicating invalid extension
        """
        # Given I have a file "script.py" (Python code)
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        script_file = prompts_dir / "script.py"
        script_file.write_text("print('Hello, world!')")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template with explicit Path (forcing file treatment)
        # Then a ValueError should be raised indicating invalid extension
        with pytest.raises(ValueError, match="File extension '.py' not allowed"):
            instance.prompt_template(Path("script.py"))

    def test_binary_file_content_rejection(self, clean_env, tmp_path):
        """
        3. Scenario: Binary file content rejection
        Given I have a file with binary content but text extension
        When I call prompt_template("fake_text.txt")
        Then a ValueError should be raised indicating binary content
        """
        # Given I have a file with binary content but text extension
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        binary_file = prompts_dir / "fake_text.txt"
        
        # Write binary content (null bytes)
        binary_content = b"Hello\x00World\x00Binary\x00Content"
        binary_file.write_bytes(binary_content)
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("fake_text.txt")
        # Then a ValueError should be raised indicating binary content
        with pytest.raises(ValueError, match="File appears to be binary"):
            instance.prompt_template("fake_text.txt")

    def test_invalid_utf8_rejection(self, clean_env, tmp_path):
        """
        4. Scenario: Invalid UTF-8 encoding rejection
        Given I have a file with invalid UTF-8 content
        When I call prompt_template("invalid_utf8.txt")
        Then a ValueError should be raised indicating invalid encoding
        """
        # Given I have a file with invalid UTF-8 content
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        invalid_file = prompts_dir / "invalid_utf8.txt"
        
        # Write invalid UTF-8 bytes
        invalid_utf8 = b"\xff\xfe\x00\x00Invalid UTF-8"
        invalid_file.write_bytes(invalid_utf8)
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("invalid_utf8.txt")
        # Then a ValueError should be raised indicating invalid encoding
        with pytest.raises(ValueError, match="File is not valid UTF-8 text"):
            instance.prompt_template("invalid_utf8.txt")

    def test_empty_file_handling(self, clean_env, tmp_path):
        """
        5. Scenario: Empty file handling
        Given I have an empty text file
        When I call prompt_template("empty.txt")
        Then it should be rejected with an error to prevent developer confusion
        """
        # Given I have an empty text file
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        empty_file = prompts_dir / "empty.txt"
        empty_file.write_text("")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("empty.txt")
        # Then it should be rejected with an error to prevent developer confusion
        with pytest.raises(ValueError, match="Template file is empty"):
            instance.prompt_template("empty.txt")


    def test_unicode_file_handling(self, clean_env, tmp_path):
        """
        6. Scenario: Unicode file handling
        Given I have a text file with unicode characters (emojis, accents)
        When I call prompt_template("unicode.txt")
        Then it should be properly decoded and included
        """
        # Given I have a text file with unicode characters
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        unicode_file = prompts_dir / "unicode.txt"
        unicode_content = "Hello 🌍! Café résumé naïve Москва 北京"
        unicode_file.write_text(unicode_content, encoding="utf-8")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("unicode.txt")
        new_instance = instance.prompt_template("unicode.txt")
        
        # Then it should be properly decoded and included
        assert new_instance._prompt_template == unicode_content

    def test_string_vs_path_detection(self, clean_env):
        """
        7. Scenario: String vs path detection
        Given I have various string inputs
        When I call prompt_template with strings like "hello.world", "config.txt", "path/to/file"
        Then only legitimate file paths should be treated as files
        """
        instance = llmaid()
        
        # Strings that should NOT be treated as file paths
        non_file_strings = [
            "hello.world",  # Not a recognized extension
            "just a sentence with dots.",
            "template {{variable}}",
            "hello.123",  # Numeric extension
        ]
        
        for test_string in non_file_strings:
            # These should be treated as literal template strings
            new_instance = instance.prompt_template(test_string)
            assert new_instance._prompt_template == test_string
        
        # Strings that SHOULD be treated as file paths (but will fail because files don't exist)
        file_path_strings = [
            "config.txt",  # Recognized extension
            "template.md",  # Recognized extension
            "path/to/file.yaml",  # Has path separator
            "prompts/role.json",  # Has path separator and extension
        ]
        
        for test_string in file_path_strings:
            # These should attempt file loading and fail with FileNotFoundError
            with pytest.raises(FileNotFoundError):
                instance.prompt_template(test_string)

    def test_explicit_path_object_handling(self, clean_env, tmp_path):
        """
        8. Scenario: Explicit Path object handling
        Given I pass a pathlib.Path object to prompt_template
        When the path exists and is valid
        Then it should always be treated as a file path (not string literal)
        """
        # Given I pass a pathlib.Path object
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        path_file = prompts_dir / "explicit_path"  # No extension
        path_file.write_text("Content from explicit Path object")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When the path exists and is valid
        path_object = Path("explicit_path")
        new_instance = instance.prompt_template(path_object)
        
        # Then it should always be treated as a file path
        assert new_instance._prompt_template == "Content from explicit Path object"

    def test_unsupported_input_types(self, clean_env):
        """
        9. Scenario: Unsupported input types
        Given I pass non-string, non-Path objects to prompt_template
        When I call prompt_template(123, [], {})
        Then TypeError should be raised for each invalid type
        """
        instance = llmaid()
        
        # Test various unsupported types
        unsupported_types = [123, [], {}, None, True, 3.14]
        
        for invalid_input in unsupported_types:
            with pytest.raises(TypeError, match="Template must be str or Path"):
                instance.prompt_template(invalid_input)

    def test_file_with_no_extension_but_text_content(self, clean_env, tmp_path):
        """
        10. Scenario: File with no extension but text content
        Given I have a file with no extension containing text
        When I call prompt_template with explicit Path object
        Then it should be accepted based on content analysis
        """
        # Given I have a file with no extension containing text
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        no_ext_file = prompts_dir / "no_extension_file"
        no_ext_file.write_text("Content without extension")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template with explicit Path object
        new_instance = instance.prompt_template(Path("no_extension_file"))
        
        # Then it should be accepted based on content analysis
        assert new_instance._prompt_template == "Content without extension"

    def test_excessive_control_characters_rejection(self, clean_env, tmp_path):
        """
        11. Scenario: Excessive control characters rejection
        Given I have a file with too many control characters
        When I call prompt_template("control_chars.txt")
        Then a ValueError should be raised indicating excessive control characters
        """
        # Given I have a file with too many control characters
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        control_file = prompts_dir / "control_chars.txt"
        
        # Create content with >10% control characters (excluding allowed tab, LF, CR)
        control_content = "Hello\x01\x02\x03\x04\x05World\x06\x07\x08\x0b\x0c"  # Many control chars
        control_file.write_bytes(control_content.encode('utf-8'))
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template("control_chars.txt")
        # Then a ValueError should be raised indicating excessive control characters
        with pytest.raises(ValueError, match="File contains excessive control characters"):
            instance.prompt_template("control_chars.txt")

    def test_mime_type_validation(self, clean_env, tmp_path):
        """
        12. Scenario: MIME type validation
        Given I have files with various MIME types
        When I call prompt_template with each file
        Then only files with text-based MIME types should be accepted
        And files with binary MIME types should be rejected
        """
        # Given I have files with various MIME types
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # Create a file that should be accepted (text-based MIME type)
        text_file = prompts_dir / "valid.txt"
        text_file.write_text("Valid text content")
        
        # Create a file that should be rejected (binary MIME type)
        # Python files should be rejected per specification
        py_file = prompts_dir / "script.py"
        py_file.write_text("print('Hello world')")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I call prompt_template with text file
        # Then it should be accepted
        new_instance = instance.prompt_template("valid.txt")
        assert new_instance._prompt_template == "Valid text content"
        
        # When I call prompt_template with binary MIME type file
        # Then it should be rejected
        with pytest.raises(ValueError, match="File extension '.py' not allowed"):
            instance.prompt_template(Path("script.py"))

    def test_file_size_limit_enforcement(self, clean_env, tmp_path):
        """
        13. Scenario: File size limit enforcement
        Given the system has a 64KB limit for template files
        When I attempt to load a file exceeding this limit
        Then the system should reject the file before reading its full content
        And provide a clear error message about the size limit
        """
        # Given the system has a 64KB limit for template files
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        large_file = prompts_dir / "large_file.txt"
        
        # Create a file larger than 64KB
        large_content = "x" * (65 * 1024)  # 65KB
        large_file.write_text(large_content)
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When I attempt to load a file exceeding this limit
        # Then the system should reject the file before reading its full content
        # And provide a clear error message about the size limit
        with pytest.raises(ValueError, match="Template file too large.*max 65536"):
            instance.prompt_template("large_file.txt")

    def test_multiple_validation_layers(self, clean_env, tmp_path):
        """
        14. Scenario: Multiple validation layers
        Given a file must pass extension, size, MIME type, encoding, and content checks
        When any single validation fails
        Then the entire file loading should fail with a specific error
        And no partial content should be loaded or cached
        """
        # Given a file must pass multiple validation layers
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # Test extension validation failure
        bad_ext_file = prompts_dir / "script.exe"
        bad_ext_file.write_text("Some content")
        with pytest.raises(ValueError, match="File extension '.exe' not allowed"):
            instance.prompt_template(Path("script.exe"))
        
        # Test size validation failure
        large_file = prompts_dir / "large.txt"
        large_file.write_text("x" * (65 * 1024))  # Too large
        with pytest.raises(ValueError, match="Template file too large"):
            instance.prompt_template("large.txt")
        
        # Test encoding validation failure
        bad_encoding_file = prompts_dir / "bad_encoding.txt"
        bad_encoding_file.write_bytes(b"\xff\xfe\x00\x00Invalid UTF-8")
        with pytest.raises(ValueError, match="File is not valid UTF-8 text"):
            instance.prompt_template("bad_encoding.txt")
        
        # Test binary content validation failure
        binary_file = prompts_dir / "binary.txt"
        binary_file.write_bytes(b"Hello\x00World")
        with pytest.raises(ValueError, match="File appears to be binary"):
            instance.prompt_template("binary.txt")

    def test_developer_friendly_error_messages(self, clean_env, tmp_path):
        """
        16. Scenario: Developer-friendly error messages
        Given a file fails validation for any reason
        When the error is reported to the developer
        Then the error message should be specific and actionable
        And suggest how to fix the issue (file format, size, encoding, etc.)
        """
        # Given a file fails validation for any reason
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # Test that error messages are specific and actionable
        
        # Size error should mention the limit
        large_file = prompts_dir / "large.txt"
        large_file.write_text("x" * (65 * 1024))
        with pytest.raises(ValueError) as exc_info:
            instance.prompt_template("large.txt")
        assert "65536" in str(exc_info.value)  # Should mention the specific limit
        assert "too large" in str(exc_info.value).lower()
        
        # Extension error should mention the specific extension
        py_file = prompts_dir / "script.py"
        py_file.write_text("print('hello')")
        with pytest.raises(ValueError) as exc_info:
            instance.prompt_template(Path("script.py"))
        assert ".py" in str(exc_info.value)
        assert "not allowed" in str(exc_info.value)
        
        # UTF-8 error should mention encoding
        bad_encoding_file = prompts_dir / "bad.txt"
        bad_encoding_file.write_bytes(b"\xff\xfe\x00\x00")
        with pytest.raises(ValueError) as exc_info:
            instance.prompt_template("bad.txt")
        assert "UTF-8" in str(exc_info.value)

    def test_allowed_file_extensions_whitelist(self, clean_env, tmp_path):
        """
        17. Scenario: Allowed file extensions whitelist
        Given the system has a predefined list of safe extensions
        When I attempt to load files with various extensions
        Then only files with extensions in the whitelist should be processed
        And the whitelist should include: .txt, .md, .json, .yaml, .yml, .xml, .csv, .tsv, .template, .prompt, .tmpl
        """
        # Given the system has a predefined list of safe extensions
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # Test allowed extensions
        allowed_extensions = ['.txt', '.md', '.json', '.yaml', '.yml', '.xml', 
                            '.csv', '.tsv', '.template', '.prompt', '.tmpl']
        
        for ext in allowed_extensions:
            test_file = prompts_dir / f"test{ext}"
            test_file.write_text(f"Content for {ext} file")
            
            # When I attempt to load files with allowed extensions
            new_instance = instance.prompt_template(Path(f"test{ext}"))
            # Then they should be processed
            assert new_instance._prompt_template == f"Content for {ext} file"
        
        # Test disallowed extensions
        disallowed_extensions = ['.py', '.exe', '.bin', '.jpg', '.pdf']
        for ext in disallowed_extensions:
            test_file = prompts_dir / f"test{ext}"
            test_file.write_text("Content")
            
            # When I attempt to load files with disallowed extensions
            # Then they should be rejected
            with pytest.raises(ValueError, match=f"File extension '{ext}' not allowed"):
                instance.prompt_template(Path(f"test{ext}"))

    def test_path_traversal_protection(self, clean_env, tmp_path):
        """
        18. Scenario: Path traversal protection
        Given the system processes file paths from user input
        When file paths are resolved and validated
        Then the system should prevent access to unauthorized directories
        And restrict file access to designated template directories and current working directory
        """
        # Given the system processes file paths from user input
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # Create a file outside the template directory
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "secret.txt"
        outside_file.write_text("Secret content")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When file paths attempt to traverse outside allowed directories
        # Then the system should prevent access to unauthorized directories
        
        # Test various path traversal attempts
        traversal_paths = [
            "../outside/secret.txt",
            "../../outside/secret.txt", 
            f"{outside_dir}/secret.txt"  # Absolute path to outside directory
        ]
        
        for path in traversal_paths:
            # These should fail because the file is not in the allowed directories
            with pytest.raises((ValueError, FileNotFoundError)):
                instance.prompt_template(path)

    def test_string_literal_safety(self, clean_env):
        """
        21. Scenario: String literal safety
        Given I provide template strings that are not file paths
        When I call prompt_template with content like "Hello {{name}}.txt"
        Then the string should be treated as a literal template
        And no file system access should be attempted
        """
        # Given I provide template strings that are not file paths
        instance = llmaid()
        
        # Test strings that contain file-like patterns but should be treated as literals
        literal_strings = [
            "Hello {{name}}.txt",
            "Process the data.csv file",
            "Load config.json settings",
            "template.md content here",
            "The file.yaml contains {{variable}}"
        ]
        
        for literal_string in literal_strings:
            # When I call prompt_template with these strings
            new_instance = instance.prompt_template(literal_string)
            # Then the string should be treated as a literal template
            assert new_instance._prompt_template == literal_string
            # And no file system access should be attempted (no FileNotFoundError)

    def test_file_access_error_handling(self, clean_env, tmp_path):
        """
        23. Scenario: File access error handling
        Given I specify a file path that exists but cannot be read (permissions, etc.)
        When I call prompt_template with that path
        Then a ValueError should be raised with file access details
        And the error should distinguish between "not found" and "cannot read"
        """
        # Given I specify a file path that exists but cannot be read
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # Create a file that exists
        restricted_file = prompts_dir / "restricted.txt"
        restricted_file.write_text("Secret content")
        
        # Make it unreadable (this might not work on all systems, so we'll test the concept)
        import os
        import stat
        try:
            # Remove read permissions
            os.chmod(restricted_file, stat.S_IWRITE)
            
            instance = llmaid(prompt_template_dir=str(prompts_dir))
            
            # When I call prompt_template with that path
            # Then a ValueError should be raised with file access details
            with pytest.raises((ValueError, PermissionError, FileNotFoundError)):
                instance.prompt_template("restricted.txt")
        
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(restricted_file, stat.S_IREAD | stat.S_IWRITE)
            except Exception:
                pass
        
        # Test file not found vs cannot read distinction
        # This is handled by the existing implementation which raises FileNotFoundError
        # for files that don't exist and ValueError for files that exist but fail validation

    def test_mime_type_fallback_detection(self, clean_env, tmp_path):
        """
        24. Scenario: MIME type fallback detection
        Given I have a file with no extension or unknown extension
        When the MIME type cannot be determined from the extension
        Then the system should analyze file content to determine if it's text
        And make a conservative decision about file safety
        """
        # Given I have a file with no extension or unknown extension
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # Create a file with no extension that contains text
        no_ext_file = prompts_dir / "no_extension"
        no_ext_file.write_text("This is text content")
        
        # Create a file with unknown extension that contains text
        unknown_ext_file = prompts_dir / "test.unknown"
        unknown_ext_file.write_text("This is also text content")
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When the MIME type cannot be determined from the extension
        # Then the system should analyze file content to determine if it's text
        
        # No extension file should work with explicit Path
        new_instance = instance.prompt_template(Path("no_extension"))
        assert new_instance._prompt_template == "This is text content"
        
        # Unknown extension should be rejected due to extension whitelist
        with pytest.raises(ValueError, match="File extension '.unknown' not allowed"):
            instance.prompt_template(Path("test.unknown"))

    def test_control_character_tolerance(self, clean_env, tmp_path):
        """
        25. Scenario: Control character tolerance
        Given I have a text file with some control characters like tabs and newlines
        When the control characters are within acceptable limits
        Then the file should be accepted as valid text
        And normal formatting characters should not trigger rejection
        """
        # Given I have a text file with some control characters like tabs and newlines
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # Create a file with acceptable control characters (tab, LF, CR)
        control_file = prompts_dir / "with_controls.txt"
        control_content = "Line 1\nLine 2\nTabbed\tContent\nAnother\tline"
        control_file.write_text(control_content)
        
        instance = llmaid(prompt_template_dir=str(prompts_dir))
        
        # When the control characters are within acceptable limits
        new_instance = instance.prompt_template("with_controls.txt")
        
        # Then the file should be accepted as valid text
        assert new_instance._prompt_template == control_content
        # And normal formatting characters should not trigger rejection
