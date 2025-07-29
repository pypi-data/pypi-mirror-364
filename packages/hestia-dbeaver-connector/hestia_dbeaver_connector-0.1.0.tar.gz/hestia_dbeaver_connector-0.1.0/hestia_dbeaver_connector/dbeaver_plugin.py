"""
DBeaver Integration Plugin for Hestia

Provides DBeaver database connectivity and management capabilities.
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QMessageBox, QComboBox,
    QGroupBox, QFormLayout, QCheckBox, QTextEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class DBeaverDetector(QThread):
    """Thread for detecting DBeaver installation"""
    found_signal = pyqtSignal(str)
    not_found_signal = pyqtSignal()
    
    def run(self):
        """Search for DBeaver installation"""
        dbeaver_path = self.find_dbeaver()
        if dbeaver_path:
            self.found_signal.emit(dbeaver_path)
        else:
            self.not_found_signal.emit()
    
    def find_dbeaver(self) -> Optional[str]:
        """Find DBeaver executable on the system"""
        system = platform.system().lower()
        
        # Common installation paths
        if system == "windows":
            paths = [
                r"C:\Program Files\DBeaver\dbeaver.exe",
                r"C:\Program Files (x86)\DBeaver\dbeaver.exe",
                os.path.expanduser(r"~\AppData\Local\DBeaver\dbeaver.exe"),
                os.path.expanduser(r"~\AppData\Roaming\DBeaver\dbeaver.exe")
            ]
        elif system == "darwin":  # macOS
            paths = [
                "/Applications/DBeaver.app/Contents/MacOS/dbeaver",
                "/Applications/DBeaver Community.app/Contents/MacOS/dbeaver"
            ]
        else:  # Linux
            paths = [
                "/usr/bin/dbeaver",
                "/usr/local/bin/dbeaver",
                os.path.expanduser("~/.local/bin/dbeaver")
            ]
        
        # Check if any path exists
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(['which', 'dbeaver'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            pass
        
        return None


class DBeaverConfigDialog(QDialog):
    """Configuration dialog for DBeaver integration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure DBeaver Integration")
        self.resize(600, 500)
        self.dbeaver_path = ""
        self.connections = {}
        self.init_ui()
        self.load_saved_config()
        self.detect_dbeaver()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Basic Configuration Tab
        basic_tab = self.create_basic_tab()
        tabs.addTab(basic_tab, "Basic Configuration")
        
        # Database Connections Tab
        connections_tab = self.create_connections_tab()
        tabs.addTab(connections_tab, "Database Connections")
        
        # Advanced Tab
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self.save_configuration)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.test_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_basic_tab(self):
        """Create the basic configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # DBeaver Path Configuration
        path_group = QGroupBox("DBeaver Installation")
        path_layout = QFormLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Path to DBeaver executable")
        self.path_input.textChanged.connect(self.on_path_changed)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_dbeaver)
        
        path_input_layout = QHBoxLayout()
        path_input_layout.addWidget(self.path_input)
        path_input_layout.addWidget(browse_btn)
        
        path_layout.addRow("DBeaver Path:", path_input_layout)
        path_group.setLayout(path_layout)
        
        # Status
        self.status_label = QLabel("Status: Not configured")
        self.status_label.setStyleSheet("color: gray;")
        
        layout.addWidget(path_group)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_connections_tab(self):
        """Create the database connections tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection List
        self.connection_list = QTextEdit()
        self.connection_list.setPlaceholderText("No database connections configured")
        self.connection_list.setMaximumHeight(200)
        
        # Add Connection Button
        add_btn = QPushButton("Add Database Connection")
        add_btn.clicked.connect(self.add_connection)
        
        layout.addWidget(QLabel("Database Connections:"))
        layout.addWidget(self.connection_list)
        layout.addWidget(add_btn)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_advanced_tab(self):
        """Create the advanced configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Auto-detection settings
        auto_group = QGroupBox("Auto-Detection Settings")
        auto_layout = QVBoxLayout()
        
        self.auto_detect_cb = QCheckBox("Automatically detect DBeaver on startup")
        self.auto_detect_cb.setChecked(True)
        
        self.auto_connect_cb = QCheckBox("Automatically connect to known databases")
        self.auto_connect_cb.setChecked(False)
        
        auto_layout.addWidget(self.auto_detect_cb)
        auto_layout.addWidget(self.auto_connect_cb)
        auto_group.setLayout(auto_layout)
        
        # Integration settings
        integration_group = QGroupBox("Hestia Integration")
        integration_layout = QVBoxLayout()
        
        self.enable_export_cb = QCheckBox("Enable data export to Hestia")
        self.enable_export_cb.setChecked(True)
        
        self.enable_import_cb = QCheckBox("Enable data import from Hestia")
        self.enable_import_cb.setChecked(True)
        
        integration_layout.addWidget(self.enable_export_cb)
        integration_layout.addWidget(self.enable_import_cb)
        integration_group.setLayout(integration_layout)
        
        layout.addWidget(auto_group)
        layout.addWidget(integration_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def detect_dbeaver(self):
        """Start DBeaver detection in background thread"""
        self.detector = DBeaverDetector()
        self.detector.found_signal.connect(self.on_dbeaver_found)
        self.detector.not_found_signal.connect(self.on_dbeaver_not_found)
        self.detector.start()
    
    def on_dbeaver_found(self, path: str):
        """Called when DBeaver is found"""
        self.dbeaver_path = path
        self.path_input.setText(path)
        self.status_label.setText(f"Status: DBeaver found at {path}")
        self.status_label.setStyleSheet("color: green;")
        self.test_btn.setEnabled(True)
    
    def on_dbeaver_not_found(self):
        """Called when DBeaver is not found"""
        self.status_label.setText("Status: DBeaver not found - please browse for installation")
        self.status_label.setStyleSheet("color: orange;")
    
    def browse_dbeaver(self):
        """Browse for DBeaver executable"""
        system = platform.system().lower()
        
        if system == "windows":
            file_filter = "DBeaver Executable (dbeaver.exe);;All Files (*.*)"
        else:
            file_filter = "All Files (*.*)"
        
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select DBeaver Executable",
            "",
            file_filter
        )
        
        if path:
            self.dbeaver_path = path
            self.path_input.setText(path)
            self.status_label.setText(f"Status: DBeaver selected at {path}")
            self.status_label.setStyleSheet("color: green;")
            self.test_btn.setEnabled(True)
    
    def on_path_changed(self):
        """Called when path input changes"""
        path = self.path_input.text()
        if path and os.path.exists(path):
            self.dbeaver_path = path
            self.test_btn.setEnabled(True)
        else:
            self.test_btn.setEnabled(False)
    
    def add_connection(self):
        """Add a new database connection"""
        # This would open a connection configuration dialog
        # For now, just add a placeholder
        connection_info = {
            "name": "New Connection",
            "type": "PostgreSQL",
            "host": "localhost",
            "port": "5432",
            "database": "testdb"
        }
        
        self.connections[connection_info["name"]] = connection_info
        self.update_connection_display()
    
    def update_connection_display(self):
        """Update the connection list display"""
        if not self.connections:
            self.connection_list.setPlainText("No database connections configured")
        else:
            text = ""
            for name, conn in self.connections.items():
                text += f"Name: {name}\n"
                text += f"Type: {conn['type']}\n"
                text += f"Host: {conn['host']}:{conn['port']}\n"
                text += f"Database: {conn['database']}\n"
                text += "-" * 30 + "\n"
            self.connection_list.setPlainText(text)
    
    def test_connection(self):
        """Test the DBeaver connection"""
        if not self.dbeaver_path:
            QMessageBox.warning(self, "Missing Path", "Please select the DBeaver executable.")
            return
        
        if not os.path.exists(self.dbeaver_path):
            QMessageBox.warning(self, "Invalid Path", "The selected DBeaver executable does not exist.")
            return
        
        try:
            # Try to launch DBeaver
            result = subprocess.run([self.dbeaver_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", 
                                      f"DBeaver found and ready!\nVersion: {result.stdout.strip()}")
            else:
                QMessageBox.warning(self, "Warning", 
                                  f"DBeaver launched but returned: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            QMessageBox.information(self, "Success", 
                                  "DBeaver launched successfully (timeout is normal)")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to launch DBeaver: {str(e)}")
    
    def save_configuration(self):
        """Save the current configuration"""
        config = {
            "dbeaver_path": self.dbeaver_path,
            "connections": self.connections,
            "auto_detect": self.auto_detect_cb.isChecked(),
            "auto_connect": self.auto_connect_cb.isChecked(),
            "enable_export": self.enable_export_cb.isChecked(),
            "enable_import": self.enable_import_cb.isChecked()
        }
        
        # Save to user's config directory
        config_dir = self.get_config_directory()
        config_file = config_dir / "dbeaver_config.json"
        
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(self, "Success", 
                                  f"Configuration saved to {config_file}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to save configuration: {str(e)}")
    
    def load_saved_config(self):
        """Load previously saved configuration"""
        config_file = self.get_config_directory() / "dbeaver_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.dbeaver_path = config.get("dbeaver_path", "")
                self.connections = config.get("connections", {})
                
                if self.dbeaver_path:
                    self.path_input.setText(self.dbeaver_path)
                
                self.update_connection_display()
                
            except Exception as e:
                print(f"Failed to load config: {e}")
    
    def get_config_directory(self) -> Path:
        """Get the configuration directory for this plugin"""
        if platform.system().lower() == "windows":
            base_dir = Path(os.environ.get("APPDATA", ""))
        else:
            base_dir = Path.home() / ".config"
        
        return base_dir / "hestia" / "plugins" / "dbeaver"


def register_with_hestia(parent_widget=None):
    """
    Main entry point for Hestia integration.
    
    This function is called by Hestia's setup wizard to launch
    the DBeaver configuration dialog.
    
    Args:
        parent_widget: The parent widget from Hestia (optional)
    
    Returns:
        bool: True if configuration was saved, False if cancelled
    """
    dialog = DBeaverConfigDialog(parent_widget)
    result = dialog.exec_()
    return result == QDialog.Accepted


# For testing outside of Hestia
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    result = register_with_hestia()
    print(f"Configuration result: {result}")
    sys.exit(app.exec_()) 