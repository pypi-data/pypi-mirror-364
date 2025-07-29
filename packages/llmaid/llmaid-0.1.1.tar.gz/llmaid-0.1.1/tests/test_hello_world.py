"""
Hello World test for LLMAid - Basic functionality verification.

This test serves as the foundation for the LLMAid testing architecture,
verifying that the basic import and instantiation works correctly.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmaid import llmaid
from llmaid.core import LLMAid


class TestHelloWorld:
    """Basic hello world tests to verify the testing infrastructure."""

    def test_can_import_llmaid(self):
        """Test that we can import the llmaid module successfully."""
        # This test verifies that our module structure is correct
        assert llmaid is not None
        instance = llmaid()
        assert instance is not None
        assert isinstance(instance, LLMAid)


if __name__ == "__main__":
    # Allow running tests directly with python
    pytest.main([__file__, "-v"])
