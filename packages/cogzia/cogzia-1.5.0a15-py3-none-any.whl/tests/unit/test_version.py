#!/usr/bin/env python3
"""
Unit tests for version.py module.

Tests version tracking and comparison functionality.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from version import __version__, parse_version, is_newer_version, get_version_string


class TestVersion:
    """Test cases for version module."""
    
    def test_version_constants(self):
        """Test that version constants are properly defined."""
        assert __version__ == "1.5.0"
        assert get_version_string() == "Cogzia Alpha v1.5.0"
    
    def test_parse_version_valid(self):
        """Test parsing valid version strings."""
        # Test standard version
        assert parse_version("1.5.0") == (1, 5, 0)
        
        # Test with 'v' prefix
        assert parse_version("v1.5.0") == (1, 5, 0)
        
        # Test with extra parts (should only take first 3)
        assert parse_version("1.5.0.1") == (1, 5, 0)
        
        # Test single digit versions
        assert parse_version("2.0.0") == (2, 0, 0)
        
        # Test double digit versions
        assert parse_version("10.20.30") == (10, 20, 30)
    
    def test_parse_version_invalid(self):
        """Test parsing invalid version strings."""
        # Invalid formats should return (0, 0, 0)
        assert parse_version("invalid") == (0, 0, 0)
        assert parse_version("") == (0, 0, 0)
        assert parse_version("a.b.c") == (0, 0, 0)
        assert parse_version("1.2.x") == (0, 0, 0)
    
    def test_is_newer_version(self):
        """Test version comparison logic."""
        # Test newer versions
        assert is_newer_version("1.5.1", "1.5.0") is True
        assert is_newer_version("1.6.0", "1.5.0") is True
        assert is_newer_version("2.0.0", "1.5.0") is True
        
        # Test older versions
        assert is_newer_version("1.4.9", "1.5.0") is False
        assert is_newer_version("1.5.0", "1.5.0") is False
        assert is_newer_version("0.9.0", "1.5.0") is False
        
        # Test with current version
        assert is_newer_version("1.5.1") is True  # Uses __version__ as local
        assert is_newer_version("1.5.0") is False
        assert is_newer_version("1.4.9") is False
        
        # Test with v prefix
        assert is_newer_version("v1.5.1", "v1.5.0") is True
        assert is_newer_version("v1.5.0", "1.5.0") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])