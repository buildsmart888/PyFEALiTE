"""
PyFEALiTE Plugin System

This module provides the plugin architecture for extending PyFEALiTE with 
additional analysis capabilities while maintaining a clean, focused core.

Key Components:
- AnalysisPlugin: Abstract base class for all plugins
- PluginRegistry: Central registry for plugin management
- AnalysisCapability: Enum for supported analysis types
- PluginMetadata: Plugin information and requirements

Example:
    >>> from pyfealite.plugins import plugin_registry
    >>> available = plugin_registry.get_available_capabilities()
    >>> print(available)
    ['static_2d', 'modal_2d', 'static_3d', 'p_delta']
"""

from .base import (
    AnalysisPlugin,
    PluginMetadata,
    AnalysisCapability,
    PluginRegistry,
    PluginError
)

from .registry import plugin_registry

# Auto-discover and register plugins
plugin_registry.discover_plugins()

__all__ = [
    'AnalysisPlugin',
    'PluginMetadata', 
    'AnalysisCapability',
    'PluginRegistry',
    'PluginError',
    'plugin_registry'
]

# Plugin system version
__version__ = "2.0.0"