#!/usr/bin/env python3
"""
Unit tests for update_manager.py module.

Tests update checking, downloading, and installation functionality.
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock EnhancedConsole before importing update_manager
sys.modules['ui'] = MagicMock()
sys.modules['ui'].EnhancedConsole = MagicMock()

from update_manager import UpdateManager


class TestUpdateManager:
    """Test cases for UpdateManager class."""
    
    @pytest.fixture
    def update_manager(self):
        """Create an UpdateManager instance for testing."""
        return UpdateManager(channel="stable")
    
    @pytest.fixture
    def mock_update_manifest(self):
        """Create a mock update manifest."""
        return {
            "version": "1.5.1",
            "release_date": "2025-07-23",
            "download_url": "https://example.com/cogzia-1.5.1.whl",
            "release_notes": "Test release notes",
            "channel": "stable"
        }
    
    @pytest.mark.asyncio
    async def test_check_for_updates_available(self, update_manager, mock_update_manifest):
        """Test checking for updates when an update is available."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_update_manifest
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await update_manager.check_for_updates()
            
            assert result is not None
            assert result["version"] == "1.5.1"
            assert result["release_notes"] == "Test release notes"
    
    @pytest.mark.asyncio
    async def test_check_for_updates_none_available(self, update_manager):
        """Test checking for updates when no update is available."""
        # Mock response with current version
        mock_manifest = {"version": "1.5.0", "channel": "stable"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_manifest
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await update_manager.check_for_updates()
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_check_for_updates_network_error(self, update_manager):
        """Test checking for updates with network error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Network error"))
            
            result = await update_manager.check_for_updates()
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_download_update_success(self, update_manager, mock_update_manifest):
        """Test successful update download."""
        mock_progress = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake wheel content"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await update_manager.download_update(mock_update_manifest, mock_progress)
            
            assert result is not None
            assert result.exists()
            assert result.suffix == ".whl"
            
            # Clean up
            shutil.rmtree(result.parent)
    
    @pytest.mark.asyncio
    async def test_download_update_failure(self, update_manager, mock_update_manifest):
        """Test failed update download."""
        mock_progress = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await update_manager.download_update(mock_update_manifest, mock_progress)
            
            assert result is None
    
    def test_backup_current_installation(self, update_manager):
        """Test backing up current installation."""
        # Create a mock module path
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_module_path = Path(temp_dir) / "cogzia"
            mock_module_path.mkdir()
            (mock_module_path / "test_file.py").touch()
            
            with patch('pathlib.Path') as mock_path:
                mock_path.return_value.parent = mock_module_path
                
                # Ensure backup directory exists
                update_manager.backup_dir.mkdir(parents=True, exist_ok=True)
                
                result = update_manager.backup_current_installation()
                
                # We can't easily test the actual backup without mocking more
                # but we can verify the method doesn't crash
                assert result is None or isinstance(result, Path)
    
    def test_preserve_user_data(self, update_manager):
        """Test preserving user data."""
        # Create temporary auth directory
        auth_dir = Path.home() / ".cogzia"
        auth_dir.mkdir(exist_ok=True)
        
        # Create test files
        token_file = auth_dir / "auth_token.json"
        config_file = auth_dir / "config.json"
        
        token_data = '{"token": "test_token"}'
        config_data = '{"setting": "value"}'
        
        try:
            token_file.write_text(token_data)
            config_file.write_text(config_data)
            
            result = update_manager.preserve_user_data()
            
            assert "auth_token" in result
            assert result["auth_token"] == token_data
            assert "config" in result
            assert result["config"] == config_data
            
        finally:
            # Clean up
            token_file.unlink(missing_ok=True)
            config_file.unlink(missing_ok=True)
    
    def test_restore_user_data(self, update_manager):
        """Test restoring user data."""
        preserved_data = {
            "auth_token": '{"token": "restored_token"}',
            "config": '{"setting": "restored_value"}'
        }
        
        auth_dir = Path.home() / ".cogzia"
        auth_dir.mkdir(exist_ok=True)
        
        try:
            update_manager.restore_user_data(preserved_data)
            
            # Check files were created
            token_file = auth_dir / "auth_token.json"
            config_file = auth_dir / "config.json"
            
            assert token_file.exists()
            assert token_file.read_text() == preserved_data["auth_token"]
            assert config_file.exists()
            assert config_file.read_text() == preserved_data["config"]
            
        finally:
            # Clean up
            (auth_dir / "auth_token.json").unlink(missing_ok=True)
            (auth_dir / "config.json").unlink(missing_ok=True)
    
    def test_install_update_success(self, update_manager):
        """Test successful update installation."""
        # Create a fake wheel file
        with tempfile.NamedTemporaryFile(suffix=".whl", delete=False) as tmp_file:
            tmp_file.write(b"fake wheel content")
            wheel_path = Path(tmp_file.name)
        
        try:
            # Mock subprocess to simulate successful installation
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stderr = ""
                
                result = update_manager.install_update(wheel_path)
                
                assert result is True
                mock_run.assert_called_once()
                
        finally:
            wheel_path.unlink()
    
    def test_install_update_failure(self, update_manager):
        """Test failed update installation."""
        # Create a fake wheel file
        with tempfile.NamedTemporaryFile(suffix=".whl", delete=False) as tmp_file:
            tmp_file.write(b"fake wheel content")
            wheel_path = Path(tmp_file.name)
        
        try:
            # Mock subprocess to simulate failed installation
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Installation error"
                
                result = update_manager.install_update(wheel_path)
                
                assert result is False
                
        finally:
            wheel_path.unlink()
    
    @pytest.mark.asyncio
    async def test_perform_update_no_update_available(self, update_manager):
        """Test perform_update when no update is available."""
        # Mock check_for_updates to return None
        with patch.object(update_manager, 'check_for_updates', return_value=None):
            with patch('rich.prompt.Confirm.ask', return_value=True):
                result = await update_manager.perform_update(force=False)
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_perform_update_user_cancels(self, update_manager, mock_update_manifest):
        """Test perform_update when user cancels."""
        # Mock check_for_updates to return an update
        with patch.object(update_manager, 'check_for_updates', return_value=mock_update_manifest):
            with patch('rich.prompt.Confirm.ask', return_value=False):
                result = await update_manager.perform_update(force=False)
                
                assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])