"""
Global Plugin Registry

This module provides the global plugin registry instance that is used
throughout PyFEALiTE for plugin management.
"""

from .base import PluginRegistry

# Global plugin registry instance
plugin_registry = PluginRegistry()

# Export for convenience
__all__ = ['plugin_registry']