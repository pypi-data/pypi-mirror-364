#!/usr/bin/env python3
"""
Integration tests for update functionality.

Tests the complete update flow including version checking, downloading, and installation.
"""
import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock EnhancedConsole before importing modules that use it
sys.modules['ui'] = MagicMock()
sys.modules['ui'].EnhancedConsole = MagicMock()

from update_manager import UpdateManager, check_and_notify_update
from version import __version__, is_newer_version


class TestUpdateIntegration:
    """Integration tests for update functionality."""
    
    @pytest.mark.asyncio
    async def test_check_and_notify_update(self):
        """Test the background update check and notification."""
        # Mock update check to return an available update
        mock_update_info = {
            "version": "1.5.1",
            "release_notes": "New features"
        }
        
        # Mock the console print method to capture output
        printed_messages = []
        mock_console = MagicMock()
        mock_console.print = lambda msg: printed_messages.append(msg)
        
        with patch('update_manager.UpdateManager.check_for_updates', return_value=mock_update_info):
            with patch('update_manager.EnhancedConsole', return_value=mock_console):
                await check_and_notify_update()
                
                # Check that notification was printed
                assert len(printed_messages) >= 2
                assert any("Update available" in msg for msg in printed_messages)
                assert any("1.5.1" in msg for msg in printed_messages)
                assert any("cogzia --update" in msg for msg in printed_messages)
    
    @pytest.mark.asyncio
    async def test_check_and_notify_no_update(self, capsys):
        """Test background check when no update is available."""
        with patch('update_manager.UpdateManager.check_for_updates', return_value=None):
            await check_and_notify_update()
            
            # Should produce no output
            captured = capsys.readouterr()
            assert captured.out == ""
    
    @pytest.mark.asyncio
    async def test_check_and_notify_error_handling(self, capsys):
        """Test that errors in background check are handled silently."""
        with patch('update_manager.UpdateManager.check_for_updates', side_effect=Exception("Network error")):
            # Should not raise exception
            await check_and_notify_update()
            
            # Should produce no output
            captured = capsys.readouterr()
            assert captured.out == ""
    
    @pytest.mark.asyncio
    async def test_update_channels(self):
        """Test different update channels."""
        # Test stable channel
        stable_manager = UpdateManager(channel="stable")
        assert stable_manager.channel == "stable"
        # The URL is constructed when checking for updates, not in base URL
        
        # Test alpha channel
        alpha_manager = UpdateManager(channel="alpha")
        assert alpha_manager.channel == "alpha"
        # The URL is constructed when checking for updates, not in base URL
    
    @pytest.mark.asyncio
    async def test_version_comparison_scenarios(self):
        """Test various version comparison scenarios."""
        test_cases = [
            # (remote, local, expected)
            ("1.5.1", "1.5.0", True),   # Patch update
            ("1.6.0", "1.5.0", True),   # Minor update
            ("2.0.0", "1.5.0", True),   # Major update
            ("1.5.0", "1.5.0", False),  # Same version
            ("1.4.9", "1.5.0", False),  # Older version
            ("v1.5.1", "1.5.0", True),  # With v prefix
            ("1.5.0-alpha", "1.5.0", False),  # Alpha suffix (invalid)
        ]
        
        for remote, local, expected in test_cases:
            result = is_newer_version(remote, local)
            assert result == expected, f"Failed for {remote} vs {local}"
    
    @pytest.mark.asyncio
    async def test_backup_directory_creation(self):
        """Test that backup directory is created properly."""
        manager = UpdateManager()
        
        # Backup directory should be created on init
        assert manager.backup_dir.exists()
        assert manager.backup_dir.is_dir()
        assert str(manager.backup_dir).endswith(".cogzia/backups")
    
    def test_user_data_preservation_flow(self):
        """Test the complete user data preservation flow."""
        manager = UpdateManager()
        
        # Create test data
        auth_dir = Path.home() / ".cogzia"
        auth_dir.mkdir(exist_ok=True)
        
        test_token = '{"token": "test_preserve_restore"}'
        token_file = auth_dir / "auth_token.json"
        
        try:
            # Write test data
            token_file.write_text(test_token)
            
            # Preserve data
            preserved = manager.preserve_user_data()
            assert "auth_token" in preserved
            
            # Delete original file
            token_file.unlink()
            assert not token_file.exists()
            
            # Restore data
            manager.restore_user_data(preserved)
            
            # Verify restoration
            assert token_file.exists()
            assert token_file.read_text() == test_token
            
        finally:
            # Clean up
            token_file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_update_manifest_validation(self):
        """Test validation of update manifest structure."""
        manager = UpdateManager()
        
        # Valid manifest
        valid_manifest = {
            "version": "1.5.1",
            "release_date": "2025-07-23",
            "channel": "stable"
        }
        
        # Test with mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = valid_manifest
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await manager.check_for_updates()
            
            # Should return manifest for newer version
            assert result is not None
            assert result["version"] == "1.5.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])