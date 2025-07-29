"""
Hestia DBeaver Connector Package

A plugin for Hestia that provides DBeaver database integration.
"""

from .dbeaver_plugin import register_with_hestia, DBeaverConfigDialog

__version__ = "0.1.0"
__author__ = "Hestia Development Team"

__all__ = ["register_with_hestia", "DBeaverConfigDialog"] 