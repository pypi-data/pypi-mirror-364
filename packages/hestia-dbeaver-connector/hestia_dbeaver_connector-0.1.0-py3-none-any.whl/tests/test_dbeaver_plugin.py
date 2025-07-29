"""
Tests for the DBeaver plugin functionality.
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from hestia_dbeaver_connector.dbeaver_plugin import (
    DBeaverDetector, 
    DBeaverConfigDialog,
    register_with_hestia
)


class TestDBeaverDetector:
    """Test the DBeaver detection functionality."""
    
    def test_find_dbeaver_windows(self):
        """Test DBeaver detection on Windows."""
        detector = DBeaverDetector()
        
        with patch('platform.system', return_value='Windows'):
            with patch('os.path.exists') as mock_exists:
                # Mock that DBeaver exists at a common path
                mock_exists.return_value = True
                
                result = detector.find_dbeaver()
                assert result is not None
                assert "dbeaver.exe" in result
    
    def test_find_dbeaver_linux(self):
        """Test DBeaver detection on Linux."""
        detector = DBeaverDetector()
        
        with patch('platform.system', return_value='Linux'):
            with patch('subprocess.run') as mock_run:
                # Mock successful which command
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "/usr/bin/dbeaver\n"
                
                result = detector.find_dbeaver()
                assert result == "/usr/bin/dbeaver"
    
    def test_find_dbeaver_not_found(self):
        """Test when DBeaver is not found."""
        detector = DBeaverDetector()
        
        with patch('platform.system', return_value='Linux'):
            with patch('os.path.exists', return_value=False):
                with patch('subprocess.run') as mock_run:
                    mock_run.side_effect = FileNotFoundError()
                    
                    result = detector.find_dbeaver()
                    assert result is None


class TestDBeaverConfigDialog:
    """Test the configuration dialog."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "hestia" / "plugins" / "dbeaver"
            config_dir.mkdir(parents=True, exist_ok=True)
            yield config_dir
    
    def test_dialog_initialization(self, qtbot):
        """Test that the dialog initializes correctly."""
        dialog = DBeaverConfigDialog()
        qtbot.addWidget(dialog)
        
        assert dialog.windowTitle() == "Configure DBeaver Integration"
        assert dialog.path_input is not None
        assert dialog.test_btn is not None
    
    def test_save_configuration(self, qtbot, temp_config_dir):
        """Test saving configuration."""
        dialog = DBeaverConfigDialog()
        qtbot.addWidget(dialog)
        
        # Set some test values
        dialog.dbeaver_path = "/test/path/dbeaver"
        dialog.path_input.setText("/test/path/dbeaver")
        
        # Mock the config directory
        with patch.object(dialog, 'get_config_directory', return_value=temp_config_dir):
            # Trigger save
            qtbot.mouseClick(dialog.save_btn, Qt.LeftButton)
            
            # Check that config file was created
            config_file = temp_config_dir / "dbeaver_config.json"
            assert config_file.exists()
            
            # Check config contents
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            assert config["dbeaver_path"] == "/test/path/dbeaver"
    
    def test_load_saved_config(self, qtbot, temp_config_dir):
        """Test loading saved configuration."""
        # Create a test config file
        config_file = temp_config_dir / "dbeaver_config.json"
        test_config = {
            "dbeaver_path": "/test/path/dbeaver",
            "connections": {"test": {"host": "localhost"}},
            "auto_detect": True,
            "auto_connect": False,
            "enable_export": True,
            "enable_import": True
        }
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Create dialog and mock config directory
        with patch.object(DBeaverConfigDialog, 'get_config_directory', return_value=temp_config_dir):
            dialog = DBeaverConfigDialog()
            qtbot.addWidget(dialog)
            
            # Check that config was loaded
            assert dialog.dbeaver_path == "/test/path/dbeaver"
            assert dialog.connections == {"test": {"host": "localhost"}}
            assert dialog.path_input.text() == "/test/path/dbeaver"


class TestRegisterWithHestia:
    """Test the main registration function."""
    
    def test_register_with_hestia_no_parent(self, qtbot):
        """Test registration without parent widget."""
        with patch('hestia_dbeaver_connector.dbeaver_plugin.DBeaverConfigDialog') as mock_dialog:
            mock_dialog.return_value.exec_.return_value = 1  # Accepted
            
            result = register_with_hestia()
            assert result is True
    
    def test_register_with_hestia_with_parent(self, qtbot):
        """Test registration with parent widget."""
        parent = MagicMock()
        
        with patch('hestia_dbeaver_connector.dbeaver_plugin.DBeaverConfigDialog') as mock_dialog:
            mock_dialog.return_value.exec_.return_value = 0  # Rejected
            
            result = register_with_hestia(parent)
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__]) 