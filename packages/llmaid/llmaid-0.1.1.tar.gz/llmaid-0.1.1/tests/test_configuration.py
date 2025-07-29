"""
Test suite for LLMAid configuration and instantiation functionality.

This module tests the configuration system including environment variable
handling, parameter overrides, type conversion, and default values.

Based on specifications in configuration.spec.md
"""

import os
from pathlib import Path
import sys
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid


class TestConfiguration:
    """Test suite for configuration and instantiation functionality."""

    def test_default_instantiation_with_environment_variables(self, clean_env):
        """
        1. Scenario: Default instantiation with environment variables
        Given the environment variable LLMAID_BASE_URL is set to "http://localhost:8080"
        And the environment variable LLMAID_SECRET is set to "test-secret"
        And the environment variable LLMAID_MODEL is set to "test-model"
        When I create an llmaid instance with no parameters
        Then the instance should have base_url "http://localhost:8080"
        And the instance should have secret "test-secret"
        And the instance should have model "test-model"
        """
        # Given environment variables are set
        with patch.dict(os.environ, {
            "LLMAID_BASE_URL": "http://localhost:8080",
            "LLMAID_SECRET": "test-secret",
            "LLMAID_MODEL": "test-model"
        }):
            # When I create an llmaid instance with no parameters
            instance = llmaid()
            
            # Then the instance should have the expected values
            assert instance.base_url == "http://localhost:8080"
            assert instance.secret == "test-secret"
            assert instance.model == "test-model"

    def test_constructor_parameter_overrides_environment_variables(self, clean_env):
        """
        2. Scenario: Constructor parameter overrides environment variables
        Given the environment variable LLMAID_BASE_URL is set to "http://localhost:8080"
        And the environment variable LLMAID_MODEL is set to "env-model"
        When I create an llmaid instance with base_url="http://custom:9000" and model="custom-model"
        Then the instance should have base_url "http://custom:9000"
        And the instance should have model "custom-model"
        """
        # Given environment variables are set
        with patch.dict(os.environ, {
            "LLMAID_BASE_URL": "http://localhost:8080",
            "LLMAID_MODEL": "env-model"
        }):
            # When I create an llmaid instance with overrides
            instance = llmaid(base_url="http://custom:9000", model="custom-model")
            
            # Then the instance should have the override values
            assert instance.base_url == "http://custom:9000"
            assert instance.model == "custom-model"

    def test_default_values_when_no_environment_variables_are_set(self, clean_env):
        """
        3. Scenario: Default values when no environment variables are set
        Given no LLMAID environment variables are set
        When I create an llmaid instance with no parameters
        Then the instance should have base_url "http://127.0.0.1:17434"
        And the instance should have secret None
        And the instance should have model "mistral-large-v0.1"
        And the instance should have prompt_template_dir None
        And the instance should have strict_template True
        """
        # Given no environment variables are set (clean_env fixture ensures this)
        # When I create an llmaid instance with no parameters
        instance = llmaid()
        
        # Then the instance should have default values
        assert instance.base_url == "http://127.0.0.1:17434"
        assert instance.secret is None
        assert instance.model == "mistral-large-v0.1"
        assert instance.prompt_template_dir is None
        assert instance.strict_template is True

    def test_generation_parameters_configuration(self, clean_env):
        """
        4. Scenario: Generation parameters configuration
        Given no environment variables are set
        When I create an llmaid instance with temperature=0.8, max_tokens=100, top_p=0.9
        Then the instance should have temperature 0.8
        And the instance should have max_tokens 100
        And the instance should have top_p 0.9
        """
        # Given no environment variables are set (clean_env fixture ensures this)
        # When I create an llmaid instance with generation parameters
        instance = llmaid(temperature=0.8, max_tokens=100, top_p=0.9)
        
        # Then the instance should have the specified values
        assert instance.temperature == 0.8
        assert instance.max_tokens == 100
        assert instance.top_p == 0.9

    def test_model_parameters_configuration(self, clean_env):
        """
        5. Scenario: Model parameters configuration
        Given no environment variables are set
        When I create an llmaid instance with model_parameter={"custom_param": "value"}
        Then the instance should have model_parameter containing {"custom_param": "value"}
        """
        # Given no environment variables are set (clean_env fixture ensures this)
        # When I create an llmaid instance with model parameters
        instance = llmaid(model_parameter={"custom_param": "value"})
        
        # Then the instance should have the model parameter
        assert instance.model_parameter == {"custom_param": "value"}

    def test_environment_variable_type_conversion(self, clean_env):
        """
        6. Scenario: Environment variable type conversion
        Given the environment variable LLMAID_STRICT_TEMPLATE is set to "false"
        And the environment variable LLMAID_TEMPERATURE is set to "0.7"
        And the environment variable LLMAID_MAX_TOKENS is set to "200"
        When I create an llmaid instance with no parameters
        Then the instance should have strict_template False
        And the instance should have temperature 0.7
        And the instance should have max_tokens 200
        """
        # Given environment variables are set with string values
        with patch.dict(os.environ, {
            "LLMAID_STRICT_TEMPLATE": "false",
            "LLMAID_TEMPERATURE": "0.7",
            "LLMAID_MAX_TOKENS": "200"
        }):
            # When I create an llmaid instance with no parameters
            instance = llmaid()
            
            # Then the instance should have correctly converted types
            assert instance.strict_template is False
            assert instance.temperature == 0.7
            assert instance.max_tokens == 200
