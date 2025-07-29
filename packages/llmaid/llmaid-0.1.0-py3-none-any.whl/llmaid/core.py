"""
Core LLMAid implementation.

This module contains the main LLMAid class that handles configuration,
prompt templating, and completion requests.
"""

import os
import re
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from pathlib import Path

from .client import LLMClient


class LLMAid:
    """
    Main LLMAid class for handling LLM completions with prompt templating.
    """

    def __init__(
        self,
        __version__: str = "0.1.0",
        # Connection parameters
        base_url: Optional[str] = None,
        secret: Optional[str] = None,
        model: Optional[str] = None,
        # Prompting parameters
        prompt_template_dir: Optional[Union[str, Path]] = None,
        strict_template: Optional[bool] = None,
        strict_context_length: Optional[bool] = None,
        # Resilience parameters
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        max_timeout: int = 60,
        # Generation parameters
        context_length: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        logit_bias: Optional[Dict[int, int]] = None,
        user: Optional[str] = None,
        model_parameter: Optional[Dict[str, Any]] = None,
        # Internal parameters (used for cloning)
        _prompt_template: Optional[str] = None,
    ):
        """
        Initialize an LLMAid instance.

        Args:
            base_url: Backend URL (defaults to environment var or http://127.0.0.1:17434)
            secret: Auth token (defaults to environment var or None)
            model: Model name (defaults to environment var or mistral-large-v0.1)
            prompt_template_dir: Directory containing prompt templates
            strict_template: Whether to require exact placeholder match
            strict_context_length: Whether to raise if max context length exceeded
            max_retries: Maximum retry attempts
            backoff_factor: Base seconds for exponential backoff
            max_timeout: Timeout in seconds for LLM calls
            context_length: Max context length for provider
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            top_p: Nucleus sampling fraction
            frequency_penalty: Penalize new token frequency
            presence_penalty: Penalize token presence
            stop: Stop sequence(s)
            logit_bias: OpenAI logit bias map
            user: User identifier
            model_parameter: Free-form dict for provider-specific parameters
            _prompt_template: Internal prompt template (used for cloning)
        """
        # Load from environment variables with fallbacks
        self.base_url = base_url or os.getenv(
            "LLMAID_BASE_URL", "http://127.0.0.1:17434"
        )
        self.secret = secret or os.getenv("LLMAID_SECRET")
        self.model = model or os.getenv("LLMAID_MODEL", "mistral-large-v0.1")

        # Prompt configuration
        self.prompt_template_dir = (
            Path(prompt_template_dir) if prompt_template_dir else None
        )
        self.strict_template = (
            strict_template
            if strict_template is not None
            else self._parse_bool_env("LLMAID_STRICT_TEMPLATE", True)
        )
        self.strict_context_length = (
            strict_context_length if strict_context_length is not None else True
        )

        # Resilience
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_timeout = max_timeout

        # Generation parameters - check env vars with type conversion
        self.context_length = context_length or self._parse_int_env(
            "LLMAID_CONTEXT_LENGTH", 8192
        )
        self.temperature = temperature or self._parse_float_env("LLMAID_TEMPERATURE")
        self.max_tokens = max_tokens or self._parse_int_env("LLMAID_MAX_TOKENS")
        self.top_p = top_p or self._parse_float_env("LLMAID_TOP_P")
        self.frequency_penalty = frequency_penalty or self._parse_float_env(
            "LLMAID_FREQUENCY_PENALTY"
        )
        self.presence_penalty = presence_penalty or self._parse_float_env(
            "LLMAID_PRESENCE_PENALTY"
        )
        self.stop = stop
        self.logit_bias = logit_bias
        self.user = user
        self.model_parameter = model_parameter or {}

        # Internal state
        self._prompt_template = _prompt_template or ""

    def _parse_bool_env(self, var_name: str, default: bool) -> bool:
        """Parse boolean environment variable."""
        value = os.getenv(var_name)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _parse_int_env(
        self, var_name: str, default: Optional[int] = None
    ) -> Optional[int]:
        """Parse integer environment variable."""
        value = os.getenv(var_name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _parse_float_env(
        self, var_name: str, default: Optional[float] = None
    ) -> Optional[float]:
        """Parse float environment variable."""
        value = os.getenv(var_name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def prompt_template(
        self, *templates: Union[str, Path], strict_template: Optional[bool] = None
    ) -> "LLMAid":
        """
        Configure the prompt template stack for this instance.

        Args:
            *templates: Template strings or file paths to concatenate
            strict_template: Override strict template setting for this clone

        Returns:
            LLMAid: New instance with updated prompt template
        
        Raises:
            FileNotFoundError: If a template path appears to be a file but doesn't exist
        """
        # Concatenate all templates
        template_parts = []
        for template in templates:
            # Handle different input types
            if isinstance(template, str):
                # Check if string looks like a file path
                if self._looks_like_file_path(template):
                    # Convert to Path and process as file
                    template = Path(template)
                else:
                    # Use as literal template string
                    template_parts.append(template)
                    continue
            
            if isinstance(template, Path):
                # Handle as file path
                content = self._load_template_file(template)
                template_parts.append(content)
                continue
            
            # Unsupported type
            raise TypeError(f"Template must be str or Path, got {type(template).__name__}")

        # Join with double newlines
        combined_template = "\n\n".join(template_parts)

        # Create new instance with updated template
        clone_kwargs = {"_prompt_template": combined_template}
        if strict_template is not None:
            clone_kwargs["strict_template"] = strict_template
        
        return self._clone(**clone_kwargs)

    def system_prompt(self, *templates: Union[str, Path], **kwargs) -> "LLMAid":
        """Alias for prompt_template for OpenAI SDK compatibility."""
        return self.prompt_template(*templates, **kwargs)

    def completion(self, *args: str, **kwargs: Any) -> str:
        """
        Perform synchronous completion.

        Args:
            *args: Positional arguments to append to prompt
            **kwargs: Template variables only

        Returns:
            str: The completion response
        """
        # Render the prompt with template variables
        prompt = self._render_prompt(*args, **kwargs)
        
        # Validate context length if configured
        prompt = self._validate_context(prompt)
        
        # Create HTTP client and make request
        client = LLMClient(
            base_url=self.base_url,
            secret=self.secret,
            max_retries=self.max_retries,
            backoff_factor=self.backoff_factor,
            max_timeout=self.max_timeout
        )
        
        # Use instance generation parameters
        generation_params = self._get_generation_params()
        return client.completion(prompt, self.model, **generation_params)

    async def acompletion(self, *args: str, **kwargs: Any) -> str:
        """
        Perform asynchronous completion.

        Args:
            *args: Positional arguments to append to prompt
            **kwargs: Template variables only

        Returns:
            str: The completion response
        """
        # Render the prompt with template variables
        prompt = self._render_prompt(*args, **kwargs)
        
        # Validate context length if configured
        prompt = self._validate_context(prompt)
        
        # Create HTTP client and make request
        client = LLMClient(
            base_url=self.base_url,
            secret=self.secret,
            max_retries=self.max_retries,
            backoff_factor=self.backoff_factor,
            max_timeout=self.max_timeout
        )
        
        # Use instance generation parameters
        generation_params = self._get_generation_params()
        return await client.acompletion(prompt, self.model, **generation_params)

    async def stream(self, *args: str, **kwargs: Any) -> AsyncIterator[str]:
        """
        Perform streaming completion.

        Args:
            *args: Positional arguments to append to prompt
            **kwargs: Template variables only

        Yields:
            str: Response tokens as they arrive
        """
        # Render the prompt with template variables
        prompt = self._render_prompt(*args, **kwargs)
        
        # Validate context length if configured
        prompt = self._validate_context(prompt)
        
        # Create HTTP client and make streaming request
        client = LLMClient(
            base_url=self.base_url,
            secret=self.secret,
            max_retries=self.max_retries,
            backoff_factor=self.backoff_factor,
            max_timeout=self.max_timeout
        )
        
        # Use instance generation parameters
        generation_params = self._get_generation_params()
        async for token in client.stream(prompt, self.model, **generation_params):
            yield token

    def _get_generation_params(self) -> Dict[str, Any]:
        """
        Get generation parameters from instance configuration.
        
        Returns:
            Dict containing generation parameters set on this instance
        """
        params = {}
        
        # Add non-None generation parameters
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.frequency_penalty is not None:
            params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty is not None:
            params["presence_penalty"] = self.presence_penalty
        if self.stop is not None:
            params["stop"] = self.stop
        if self.logit_bias is not None:
            params["logit_bias"] = self.logit_bias
        if self.user is not None:
            params["user"] = self.user
            
        return params

    def _render_prompt(self, *args: str, **kwargs: Any) -> str:
        """
        Render the prompt template with given arguments.

        Args:
            *args: Positional arguments to append
            **kwargs: Template variables

        Returns:
            str: Rendered prompt
            
        Raises:
            TemplateMismatchError: If strict_template=True and placeholders don't match
        """
        # Start with template
        prompt = self._prompt_template

        # Template validation logic
        if self.strict_template:
            self._validate_template_placeholders(prompt, kwargs)

        # Template replacement using regex to handle spaces around placeholders
        for key, value in kwargs.items():
            # Pattern matches {{ key }} with optional spaces
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            prompt = re.sub(pattern, str(value), prompt)

        # Append positional arguments
        if args:
            if prompt:
                prompt += "\n" + "\n".join(args)
            else:
                prompt = "\n".join(args)

        return prompt

    def _validate_template_placeholders(self, template: str, provided_kwargs: Dict[str, Any]) -> None:
        """
        Validate that template placeholders match provided arguments when strict_template=True.
        
        Args:
            template: The template string to validate
            provided_kwargs: The keyword arguments provided for template rendering
            
        Raises:
            TemplateMismatchError: If placeholders don't match provided arguments
        """
        from .exceptions import TemplateMismatchError
        
        # Extract all placeholders from template using regex
        # This pattern matches {{ placeholder_name }} with optional spaces
        placeholder_pattern = r'\{\{\s*(\w+)\s*\}\}'
        required_placeholders = set(re.findall(placeholder_pattern, template))
        provided_placeholders = set(provided_kwargs.keys())
        
        # Check for missing placeholders
        missing_placeholders = required_placeholders - provided_placeholders
        # Check for extra placeholders
        extra_placeholders = provided_placeholders - required_placeholders
        
        if missing_placeholders or extra_placeholders:
            error_parts = []
            
            if missing_placeholders:
                missing_list = ', '.join(f'"{p}"' for p in sorted(missing_placeholders))
                error_parts.append(f"Missing required placeholders: {missing_list}")
            
            if extra_placeholders:
                extra_list = ', '.join(f'"{p}"' for p in sorted(extra_placeholders))
                error_parts.append(f"Unexpected placeholders: {extra_list}")
            
            error_message = ". ".join(error_parts)
            raise TemplateMismatchError(error_message)

    def _validate_context(self, prompt: str) -> str:
        """
        Validate prompt length based on context_length settings.
        
        Args:
            prompt: The rendered prompt to validate
            
        Returns:
            str: The validated prompt (unchanged if strict_context_length=False)
            
        Raises:
            ContextLengthExceededError: If strict_context_length=True and prompt exceeds limit
        """
        from .exceptions import ContextLengthExceededError
        
        if self.context_length is None:
            return prompt
        
        # Improved token estimation - still rough but more accurate than pure char/4
        estimated_tokens = self._estimate_tokens(prompt)
        
        if estimated_tokens <= self.context_length:
            return prompt
            
        if self.strict_context_length:
            raise ContextLengthExceededError(
                f"Prompt length ({estimated_tokens} tokens) exceeds context_length limit ({self.context_length} tokens). "
                f"Set strict_context_length=False to allow sending full context to provider."
            )
        
        # Log warning about large context but send full prompt to provider
        logging.warning(
            f"Context length is too large: {estimated_tokens} tokens exceeds "
            f"context_length limit of {self.context_length} tokens. "
            f"Sending full context to provider."
        )
        
        return prompt

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count with poor accuracy, but cheap to compute.
        
        This is still a rough approximation but considers:
        - Word boundaries (spaces split tokens)
        - Punctuation (often separate tokens)
        - CJK characters (typically 1 char = 1+ tokens)
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            int: Estimated token count
        """
        if not text:
            return 0
            
        # Count different character types
        word_chars = 0
        cjk_chars = 0
        punctuation_chars = 0
        whitespace_chars = 0
        
        for char in text:
            if char.isspace():
                whitespace_chars += 1
            elif char.isalnum():
                # Check if CJK (Chinese, Japanese, Korean)
                if ord(char) >= 0x4E00:  # Basic CJK ideographs and beyond
                    cjk_chars += 1
                else:
                    word_chars += 1
            else:
                punctuation_chars += 1
        
        # Estimation rules based on empirical observations:
        # - English words: ~4.5 chars per token on average
        # - CJK characters: ~1.3 chars per token (subword tokenization)
        # - Punctuation: often separate tokens
        # - Whitespace: doesn't count toward tokens but affects word boundaries
        
        # Count approximate word tokens (split by spaces, adjusted for character density)
        words = len(text.split())
        word_tokens = max(words, word_chars // 4)  # At least 1 token per word, but account for longer words
        
        # CJK characters often get tokenized more aggressively
        cjk_tokens = int(cjk_chars * 1.3)
        
        # Punctuation often becomes separate tokens
        punct_tokens = punctuation_chars
        
        # Final estimation with some buffering for safety
        estimated = word_tokens + cjk_tokens + punct_tokens
        
        # Add 10% buffer for tokenization overhead and ensure minimum
        return max(int(estimated * 1.1), len(text) // 6)  # Never less than char/6

    def _clone(self, **overrides: Any) -> "LLMAid":
        """
        Create a clone of this instance with specified overrides.

        Args:
            **overrides: Parameters to override in the clone

        Returns:
            LLMAid: New instance with merged configuration
        """
        # Get current configuration
        config = {
            "base_url": self.base_url,
            "secret": self.secret,
            "model": self.model,
            "prompt_template_dir": self.prompt_template_dir,
            "strict_template": self.strict_template,
            "strict_context_length": self.strict_context_length,
            "max_retries": self.max_retries,
            "backoff_factor": self.backoff_factor,
            "max_timeout": self.max_timeout,
            "context_length": self.context_length,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop,
            "logit_bias": self.logit_bias,
            "user": self.user,
            "model_parameter": (
                self.model_parameter.copy() if self.model_parameter else {}
            ),
            "_prompt_template": self._prompt_template,
        }

        # Apply overrides
        config.update(overrides)

        return LLMAid(**config)

    def __call__(self, **overrides: Any) -> "LLMAid":
        """
        Callable clone operator - create a clone with merged settings.

        Args:
            **overrides: Configuration overrides

        Returns:
            LLMAid: New instance with merged configuration

        Raises:
            ConfigurationError: If invalid parameters are provided
        """
        # Import here to avoid circular imports
        from .exceptions import ConfigurationError
        
        # Valid parameter names based on __init__ signature
        valid_params = {
            "base_url",
            "secret",
            "model",
            "prompt_template_dir",
            "strict_template",
            "strict_context_length",
            "max_retries",
            "backoff_factor",
            "max_timeout",
            "context_length",
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "logit_bias",
            "user",
            "model_parameter",
            "_prompt_template",
        }
        
        # Check for invalid parameters
        invalid_params = set(overrides.keys()) - valid_params
        if invalid_params:
            invalid_list = ", ".join(sorted(invalid_params))
            raise ConfigurationError(f"Invalid parameter(s): {invalid_list}")
        
        return self._clone(**overrides)

    def _looks_like_file_path(self, template_str: str) -> bool:
        """
        Determine if a string looks like it should be treated as a file path.
        
        Args:
            template_str: The string to analyze
            
        Returns:
            bool: True if the string looks like a file path
        """
        # Conservative approach - only treat as file if:
        # 1. Contains path separators (/ or \), OR
        # 2. Has a recognized file extension AND doesn't look like a template string
        
        # If it contains template placeholders, treat as literal template
        if '{{' in template_str and '}}' in template_str:
            return False
            
        # If it looks like descriptive text (spaces, multiple words), treat as literal
        if ' ' in template_str.strip():
            # Check if it's a simple sentence or description
            words = template_str.strip().split()
            if len(words) > 1:
                # If it has multiple words, likely a description/sentence
                # unless it's a clear file path with separators
                if '/' not in template_str and '\\' not in template_str:
                    return False
        
        if '/' in template_str or '\\' in template_str:
            return True
            
        # Check for file extension
        path_obj = Path(template_str)
        if '.' in path_obj.name:  # Has a dot in filename (not just path)
            extension = path_obj.suffix.lower()
            # Only treat as file if it has a recognized template extension
            recognized_extensions = {
                '.txt', '.md', '.json', '.yaml', '.yml', '.xml', 
                '.csv', '.tsv', '.template', '.prompt', '.tmpl'
            }
            return extension in recognized_extensions
            
        return False

    def _load_template_file(self, path: Path) -> str:
        """
        Load and validate a template file.
        
        Args:
            path: Path object to the template file
            
        Returns:
            str: Content of the template file
            
        Raises:
            FileNotFoundError: If file doesn't exist in any candidate location
            ValueError: If file fails safety validation
        """
        # Build candidate paths to try
        candidate_paths = []
        
        if path.is_absolute():
            # For absolute paths, validate they're within allowed directories
            self._validate_path_access(path)
            candidate_paths = [path]
        else:
            # Relative path - try multiple locations
            if self.prompt_template_dir:
                candidate_path = self.prompt_template_dir / path
                # Resolve to check for traversal attempts
                resolved_path = candidate_path.resolve()
                self._validate_path_access(resolved_path)
                candidate_paths.append(resolved_path)
            
            # Fallback to current directory
            candidate_path = Path.cwd() / path
            resolved_path = candidate_path.resolve()
            self._validate_path_access(resolved_path)
            candidate_paths.append(resolved_path)
        
        # Try each candidate path
        for candidate_path in candidate_paths:
            if candidate_path.exists():
                # Validate safety before reading
                self._validate_template_file_safety(candidate_path)
                
                try:
                    with open(candidate_path, "r", encoding="utf-8") as f:
                        return f.read()
                except (IOError, OSError, UnicodeDecodeError) as e:
                    # If this was the last candidate, re-raise
                    if candidate_path == candidate_paths[-1]:
                        raise FileNotFoundError(f"Could not read template file: {path}") from e
                    continue  # Try next candidate
        
        # No candidate path worked
        raise FileNotFoundError(f"Template file not found: {path}")

    def _validate_path_access(self, file_path: Path) -> None:
        """
        Validate that a file path is within allowed directories only.
        
        Args:
            file_path: Path to validate (can be relative or absolute)
            
        Raises:
            ValueError: If path is outside allowed directories
        """
        try:
            resolved_path = file_path.resolve()
            
            # Always apply strict directory validation for all paths
            # This ensures no file can be accessed outside the allowed hierarchy
            self._validate_directory_access(resolved_path)
            
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid file path: {e}")

    def _validate_directory_access(self, resolved_path: Path) -> None:
        """
        Validate that a resolved path is within allowed directories.
        
        Args:
            resolved_path: The resolved path to validate
            
        Raises:
            ValueError: If path is outside allowed directories
        """
        # Allowed base directories
        allowed_dirs = []
        
        # Add prompt template directory if configured
        if self.prompt_template_dir:
            allowed_dirs.append(self.prompt_template_dir.resolve())
        
        # Add current working directory
        allowed_dirs.append(Path.cwd().resolve())
        
        # Check if the resolved path is within any allowed directory
        for allowed_dir in allowed_dirs:
            try:
                resolved_path.relative_to(allowed_dir)
                return  # Path is within an allowed directory
            except ValueError:
                continue  # Not within this directory, try next
        
        # If we get here, path is not within any allowed directory
        raise ValueError(f"Access denied: path outside allowed directories: {resolved_path}")

    def _validate_template_file_safety(self, file_path: Path) -> None:
        """
        Validate that a file is safe to read as a template.
        
        Args:
            file_path: Path to the file to validate
            
        Raises:
            ValueError: If the file fails safety checks with specific reason
        """
        MAX_FILE_SIZE = 64 * 1024  # 64KB limit for template files (very generous for prompts)
        ALLOWED_EXTENSIONS = {
            '.txt', '.md', '.json', '.yaml', '.yml', '.xml', 
            '.csv', '.tsv', '.template', '.prompt', '.tmpl', ''  # Allow no extension
        }
        ALLOWED_MIME_TYPES = {
            'text/plain', 'text/markdown', 'text/x-markdown',
            'application/json', 'text/json',
            'application/yaml', 'text/yaml', 'application/x-yaml', 'text/x-yaml',
            'application/xml', 'text/xml',
            'text/csv', 'application/csv',
            'text/tab-separated-values',
            'application/octet-stream',  # Generic binary that might be text
            'inode/x-empty'  # Empty files
        }
        
        try:
            # Basic path validation
            if not file_path.is_file():
                raise ValueError(f"Path is not a regular file: {file_path}")
            
            # Check file extension
            extension = file_path.suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError(f"File extension '{extension}' not allowed for templates")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                raise ValueError("Template file is empty - this can lead to confusing behavior")
            if file_size > MAX_FILE_SIZE:
                raise ValueError(f"Template file too large: {file_size} bytes (max {MAX_FILE_SIZE})")
            
            # Check MIME type using file content
            mime_type = self._get_file_mime_type(file_path)
            if mime_type and not any(mime_type.startswith(allowed) for allowed in ALLOWED_MIME_TYPES):
                raise ValueError(f"File MIME type '{mime_type}' not allowed for templates")
            
            # Check if file appears to be text by reading a small sample
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(min(1024, file_size))  # Read up to 1KB sample
                
                # Try to decode as UTF-8
                sample.decode('utf-8')
                
                # Check for null bytes (binary file indicator)
                if b'\x00' in sample:
                    raise ValueError("File appears to be binary (contains null bytes)")
                
                # Check for excessive control characters (potential binary)
                control_chars = sum(1 for b in sample if b < 32 and b not in (9, 10, 13))  # Allow tab, LF, CR
                if len(sample) > 0 and control_chars / len(sample) > 0.1:  # More than 10% control chars
                    raise ValueError("File contains excessive control characters")
                    
            except UnicodeDecodeError:
                raise ValueError("File is not valid UTF-8 text")
            
        except (OSError, IOError) as e:
            raise ValueError(f"Cannot access file: {e}")

    def _get_file_mime_type(self, file_path: Path) -> str:
        """
        Get the MIME type of a file using Python's built-in tools.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: MIME type or 'application/octet-stream' if cannot be determined
        """
        import mimetypes
        
        try:
            # Use mimetypes module - works well for most cases based on file extension
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                return mime_type
                
            # Fallback: try to determine if it's text by reading a small sample
            try:
                file_size = file_path.stat().st_size
                if file_size == 0:
                    return 'inode/x-empty'  # Empty files get special MIME type
                    
                with open(file_path, 'rb') as f:
                    sample = f.read(min(1024, file_size))
                
                # Try to decode as UTF-8
                sample.decode('utf-8')
                
                # If successful and no null bytes, likely text
                if b'\x00' not in sample:
                    return 'text/plain'
                else:
                    return 'application/octet-stream'
                    
            except (UnicodeDecodeError, OSError):
                return 'application/octet-stream'
                
        except Exception:
            return 'application/octet-stream'
