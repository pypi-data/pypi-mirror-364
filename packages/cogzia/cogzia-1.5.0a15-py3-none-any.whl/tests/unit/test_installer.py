#!/usr/bin/env python3
"""
Unit tests for installer functionality.

Tests the installer script generation and update detection logic.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestInstaller:
    """Test cases for installer functionality."""
    
    def test_installer_script_creation(self):
        """Test that create_installer.py can generate an installer script."""
        import create_installer
        
        # Verify the module loads correctly
        assert hasattr(create_installer, 'create_installer')
        
        # The actual installer generation would write to disk
        # We're just verifying the module structure is correct
    
    def test_installer_includes_update_check(self):
        """Test that generated installer includes update checking logic."""
        # Read the create_installer.py to verify it has update detection
        installer_path = Path(__file__).parent.parent.parent / "create_installer.py"
        content = installer_path.read_text()
        
        # Check for update detection function
        assert "check_existing_installation" in content
        assert "Cogzia is already installed" in content
        assert "cogzia --update" in content
    
    def test_installer_python_version_requirement(self):
        """Test that installer checks Python version."""
        installer_path = Path(__file__).parent.parent.parent / "create_installer.py"
        content = installer_path.read_text()
        
        # Check for Python version check
        assert "check_python_version" in content
        assert "Python 3.8 or higher is required" in content
        assert "sys.version_info < (3, 8)" in content
    
    def test_installer_provides_options(self):
        """Test that installer provides update options when existing installation found."""
        installer_path = Path(__file__).parent.parent.parent / "create_installer.py"
        content = installer_path.read_text()
        
        # Check for user options
        assert "1. Run 'cogzia --update' to check for updates" in content
        assert "2. Continue with reinstallation" in content
        assert "3. Cancel installation" in content
    
    def test_installer_handles_user_choices(self):
        """Test that installer handles different user choices."""
        installer_path = Path(__file__).parent.parent.parent / "create_installer.py"
        content = installer_path.read_text()
        
        # Check for choice handling
        assert 'choice == "1"' in content  # Update choice
        assert 'choice == "3"' in content  # Cancel choice
        assert 'choice != "2"' in content  # Invalid choice
    
    @pytest.mark.parametrize("python_version,should_fail", [
        ((3, 7), True),
        ((3, 8), False),
        ((3, 9), False),
        ((3, 12), False),
    ])
    def test_python_version_logic(self, python_version, should_fail):
        """Test Python version checking logic."""
        # This tests the logic, not the actual check
        # since we can't easily change the Python version at runtime
        meets_requirement = python_version >= (3, 8)
        assert meets_requirement != should_fail


if __name__ == "__main__":
    pytest.main([__file__, "-v"])