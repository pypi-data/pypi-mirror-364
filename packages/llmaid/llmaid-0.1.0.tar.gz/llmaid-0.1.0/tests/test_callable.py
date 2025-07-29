"""
Test suite for LLMAid callable clone operator functionality.

This module tests the ability to create clones of LLMAid instances with
parameter overrides using the callable interface.

Based on specifications in callable.spec.md
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid, ConfigurationError
from llmaid.core import LLMAid


class TestCallableCloneOperator:
    """Test suite for callable clone operator functionality."""

    def test_basic_parameter_override(self, clean_env):
        """
        1. Scenario: Basic parameter override
        Given I have an llmaid instance with model="original-model" and temperature=0.5
        When I call the instance with model="new-model"
        Then I should get a new llmaid instance
        And the new instance should have model "new-model"
        And the new instance should have temperature 0.5
        And the original instance should remain unchanged
        """
        # Given I have an llmaid instance with model="original-model" and temperature=0.5
        original = llmaid(model="original-model", temperature=0.5)
        
        # When I call the instance with model="new-model"
        new_instance = original(model="new-model")
        
        # Then I should get a new llmaid instance
        assert new_instance is not None
        assert isinstance(new_instance, LLMAid)
        assert new_instance is not original  # Different objects
        
        # And the new instance should have model "new-model"
        assert new_instance.model == "new-model"
        
        # And the new instance should have temperature 0.5
        assert new_instance.temperature == 0.5
        
        # And the original instance should remain unchanged
        assert original.model == "original-model"
        assert original.temperature == 0.5

    def test_multiple_parameter_override(self, clean_env):
        """
        2. Scenario: Multiple parameter override
        Given I have an llmaid instance with model="original" and temperature=0.5
        When I call the instance with model="new", temperature=0.8, max_tokens=100
        Then the new instance should have all the new parameters
        And the original instance should remain unchanged
        """
        # Given I have an llmaid instance with model="original" and temperature=0.5
        original = llmaid(model="original", temperature=0.5)
        
        # When I call the instance with model="new", temperature=0.8, max_tokens=100
        new_instance = original(model="new", temperature=0.8, max_tokens=100)
        
        # Then the new instance should have all the new parameters
        assert new_instance.model == "new"
        assert new_instance.temperature == 0.8
        assert new_instance.max_tokens == 100
        
        # And the original instance should remain unchanged
        assert original.model == "original"
        assert original.temperature == 0.5
        assert original.max_tokens is None  # Should be default/None

    def test_generation_knob_override(self, clean_env):
        """
        3. Scenario: Generation knob override
        Given I have an llmaid instance with temperature=0.2
        When I call the instance with temperature=0.9, top_p=0.8
        Then the new instance should have temperature 0.9
        And the new instance should have top_p 0.8
        """
        # Given I have an llmaid instance with temperature=0.2
        original = llmaid(temperature=0.2)
        
        # When I call the instance with temperature=0.9, top_p=0.8
        new_instance = original(temperature=0.9, top_p=0.8)
        
        # Then the new instance should have temperature 0.9
        assert new_instance.temperature == 0.9
        
        # And the new instance should have top_p 0.8
        assert new_instance.top_p == 0.8
        
        # Verify original is unchanged
        assert original.temperature == 0.2
        assert original.top_p is None

    def test_model_parameter_override(self, clean_env):
        """
        4. Scenario: Model parameter override
        Given I have an llmaid instance with model_parameter={"param1": "value1"}
        When I call the instance with model_parameter={"param2": "value2"}
        Then the new instance should have model_parameter {"param2": "value2"}
        """
        # Given I have an llmaid instance with model_parameter={"param1": "value1"}
        original = llmaid(model_parameter={"param1": "value1"})
        
        # When I call the instance with model_parameter={"param2": "value2"}
        new_instance = original(model_parameter={"param2": "value2"})
        
        # Then the new instance should have model_parameter {"param2": "value2"}
        assert new_instance.model_parameter == {"param2": "value2"}
        
        # Verify original is unchanged
        assert original.model_parameter == {"param1": "value1"}

    def test_invalid_parameter_in_clone(self, clean_env):
        """
        5. Scenario: Invalid parameter in clone
        Given I have an llmaid instance
        When I call the instance with invalid_parameter="value"
        Then a ConfigurationError should be raised
        """
        # Given I have an llmaid instance
        original = llmaid()
        
        # When I call the instance with invalid_parameter="value"
        # Then a ConfigurationError should be raised
        with pytest.raises(ConfigurationError) as exc_info:
            original(invalid_parameter="value")
        
        # Verify the error message contains information about the invalid parameter
        assert "invalid_parameter" in str(exc_info.value).lower()

    def test_mixed_valid_and_invalid_parameters(self, clean_env):
        """
        6. Scenario: Mixed valid and invalid parameters
        Given I have an llmaid instance with model="test-model"
        When I call the instance with temperature=0.8, invalid_param="value", another_invalid="test"
        Then a ConfigurationError should be raised
        And the error message should contain the invalid parameter names
        """
        # Given I have an llmaid instance with model="test-model"
        original = llmaid(model="test-model")
        
        # When I call the instance with temperature=0.8, invalid_param="value", another_invalid="test"
        # Then a ConfigurationError should be raised
        with pytest.raises(ConfigurationError) as exc_info:
            original(temperature=0.8, invalid_param="value", another_invalid="test")
        
        # And the error message should contain the invalid parameter names
        error_msg = str(exc_info.value).lower()
        assert "invalid_param" in error_msg
        assert "another_invalid" in error_msg

    def test_no_parameters_clone(self, clean_env):
        """
        7. Scenario: No parameters clone
        Given I have an llmaid instance with model="test-model" and temperature=0.7
        When I call the instance with no parameters
        Then I should get a new llmaid instance
        And the new instance should have identical configuration
        And the instances should be different objects
        """
        # Given I have an llmaid instance with model="test-model" and temperature=0.7
        original = llmaid(model="test-model", temperature=0.7)
        
        # When I call the instance with no parameters
        clone = original()
        
        # Then I should get a new llmaid instance
        assert clone is not None
        assert isinstance(clone, LLMAid)
        
        # And the instances should be different objects
        assert clone is not original
        
        # And the new instance should have identical configuration
        assert clone.model == original.model
        assert clone.temperature == original.temperature

    def test_clone_preserves_all_settings(self, clean_env):
        """
        8. Scenario: Clone preserves all settings
        Given I have an llmaid instance with multiple configuration parameters
        When I call the instance overriding only a few parameters
        Then the new instance should have the overridden values
        And all other parameters should be preserved from the original
        """
        # Given I have an llmaid instance with multiple configuration parameters
        original = llmaid(
            base_url="https://test.com",
            secret="test-secret",
            model="test-model",
            temperature=0.5,
            max_tokens=200,
            top_p=0.9,
            max_retries=5,
            backoff_factor=2.0,
            max_timeout=30,
        )
        
        # When I call the instance overriding only a few parameters
        clone = original(model="new-model", temperature=0.8)
        
        # Then the new instance should have the overridden values
        assert clone.model == "new-model"
        assert clone.temperature == 0.8
        
        # And all other parameters should be preserved from the original
        assert clone.base_url == original.base_url
        assert clone.secret == original.secret
        assert clone.max_tokens == original.max_tokens
        assert clone.top_p == original.top_p
        assert clone.max_retries == original.max_retries
        assert clone.backoff_factor == original.backoff_factor
        assert clone.max_timeout == original.max_timeout

    def test_clone_with_prompt_template(self, clean_env):
        """
        9. Scenario: Clone with prompt template
        Given I have an llmaid instance with a prompt template
        When I call the instance with model override
        Then the new instance should preserve the prompt template
        And the new instance should have the overridden model
        """
        # Given I have an llmaid instance with a prompt template
        original = llmaid(model="test-model")
        templated = original.prompt_template("Hello {{name}}!")
        
        # When I call the instance with model override
        clone = templated(model="new-model")
        
        # Then the new instance should preserve the prompt template
        assert clone._prompt_template == templated._prompt_template
        
        # And the new instance should have the overridden model
        assert clone.model == "new-model"
        assert templated.model == "test-model"

    def test_chained_cloning(self, clean_env):
        """
        10. Scenario: Chained cloning
        Given I have a base llmaid instance
        When I create multiple sequential clones with different overrides
        Then each clone should inherit from its immediate parent
        And each clone should be independent of others
        And the base instance should remain unchanged
        """
        # Given I have a base llmaid instance
        base = llmaid(model="base-model", temperature=0.2)
        
        # When I create multiple sequential clones with different overrides
        clone1 = base(temperature=0.5)
        clone2 = clone1(model="new-model", max_tokens=100)
        clone3 = clone2(top_p=0.8)
        
        # Then each clone should inherit from its immediate parent
        # And each clone should be independent of others
        # And the base instance should remain unchanged
        
        # Base instance unchanged
        assert base.model == "base-model"
        assert base.temperature == 0.2
        assert base.max_tokens is None
        assert base.top_p is None
        
        # Clone1 inherits from base with temperature override
        assert clone1.model == "base-model"  # Inherited
        assert clone1.temperature == 0.5    # Overridden
        assert clone1.max_tokens is None
        assert clone1.top_p is None
        
        # Clone2 inherits from clone1 with model and max_tokens override
        assert clone2.model == "new-model"   # Overridden
        assert clone2.temperature == 0.5    # Inherited from clone1
        assert clone2.max_tokens == 100     # Overridden
        assert clone2.top_p is None
        
        # Clone3 inherits from clone2 with top_p override
        assert clone3.model == "new-model"   # Inherited from clone2
        assert clone3.temperature == 0.5    # Inherited from clone2
        assert clone3.max_tokens == 100     # Inherited from clone2
        assert clone3.top_p == 0.8          # Overridden


if __name__ == "__main__":
    # Allow running tests directly with python
    pytest.main([__file__, "-v"])
