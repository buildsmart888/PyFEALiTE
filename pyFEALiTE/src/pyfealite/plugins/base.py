"""
Plugin System Base Classes

This module defines the core interfaces and base classes for the PyFEALiTE 
plugin architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Set
import time
import functools
from pathlib import Path


class AnalysisCapability(Enum):
    """Analysis capabilities that plugins can provide."""
    
    # 2D Capabilities
    STATIC_2D = "static_2d"
    MODAL_2D = "modal_2d"
    DYNAMIC_2D = "dynamic_2d"
    
    # 3D Capabilities  
    STATIC_3D = "static_3d"
    MODAL_3D = "modal_3d"
    DYNAMIC_3D = "dynamic_3d"
    
    # Advanced Analysis
    P_DELTA = "p_delta"
    BUCKLING = "buckling"
    NONLINEAR = "nonlinear"
    
    # Specialized Elements
    PLATES = "plates"
    SHELLS = "shells"
    CABLES = "cables"
    
    # Optimization & AI
    OPTIMIZATION = "optimization"
    AI_DESIGN = "ai_design"


@dataclass
class PluginMetadata:
    """Plugin metadata and requirements."""
    
    name: str
    version: str
    description: str
    author: str
    capabilities: List[AnalysisCapability]
    dependencies: List[str]
    min_pyfealite_version: str
    priority: int = 50  # Higher = preferred (0-100)
    license: str = "MIT"
    homepage: Optional[str] = None
    
    def __post_init__(self):
        """Validate metadata."""
        if not self.name:
            raise ValueError("Plugin name cannot be empty")
        
        if not self.capabilities:
            raise ValueError("Plugin must declare at least one capability")
        
        if not 0 <= self.priority <= 100:
            raise ValueError("Priority must be between 0 and 100")


class PluginError(Exception):
    """Plugin-related errors."""
    pass


class AnalysisPlugin(ABC):
    """
    Abstract base class for all analysis plugins.
    
    This interface defines the contract that all plugins must implement
    to integrate with the PyFEALiTE analysis system.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Plugin metadata and capabilities.
        
        Returns:
            PluginMetadata: Information about this plugin
        """
        pass
    
    @abstractmethod
    def can_analyze(self, structure: 'Structure', 
                   analysis_type: AnalysisCapability) -> bool:
        """
        Check if plugin can handle this analysis.
        
        Args:
            structure: Structure to analyze
            analysis_type: Type of analysis requested
            
        Returns:
            bool: True if plugin can handle this analysis
        """
        pass
    
    @abstractmethod
    def validate_structure(self, structure: 'Structure') -> List[str]:
        """
        Validate structure compatibility.
        
        Args:
            structure: Structure to validate
            
        Returns:
            List[str]: List of validation issues (empty if valid)
        """
        pass
    
    @abstractmethod
    def analyze(self, structure: 'Structure',
               analysis_type: AnalysisCapability,
               **kwargs) -> 'AnalysisResults':
        """
        Perform structural analysis.
        
        Args:
            structure: Structure to analyze
            analysis_type: Type of analysis to perform
            **kwargs: Analysis-specific parameters
            
        Returns:
            AnalysisResults: Analysis results
            
        Raises:
            PluginError: If analysis fails
        """
        pass
    
    def get_analysis_info(self, analysis_type: AnalysisCapability) -> Dict[str, Any]:
        """
        Get information about a specific analysis type.
        
        Args:
            analysis_type: Analysis type to get info for
            
        Returns:
            Dict containing analysis information
        """
        return {
            "supported": analysis_type in self.metadata.capabilities,
            "description": f"{analysis_type.value} analysis",
            "parameters": {},
            "requirements": []
        }
    
    def get_help_text(self) -> str:
        """
        Get help text for this plugin.
        
        Returns:
            str: Human-readable help text
        """
        capabilities_str = ", ".join([cap.value for cap in self.metadata.capabilities])
        
        return f"""
Plugin: {self.metadata.name} v{self.metadata.version}
Description: {self.metadata.description}
Author: {self.metadata.author}
Capabilities: {capabilities_str}
Dependencies: {', '.join(self.metadata.dependencies) if self.metadata.dependencies else 'None'}
Priority: {self.metadata.priority}
""".strip()


def track_analysis_performance(func):
    """
    Decorator to track analysis performance metrics.
    
    This decorator automatically tracks:
    - Analysis duration
    - Success/failure rates
    - Plugin usage statistics
    """
    @functools.wraps(func)
    def wrapper(self, structure, analysis_type, **kwargs):
        plugin_name = self.metadata.name
        start_time = time.time()
        
        try:
            # Log analysis start
            print(f"Starting {analysis_type.value} analysis with {plugin_name}")
            
            # Perform analysis
            result = func(self, structure, analysis_type, **kwargs)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log success
            print(f"OK: {plugin_name} completed {analysis_type.value} in {duration:.2f}s")
            
            # Add metadata to results
            if hasattr(result, 'metadata'):
                result.metadata.update({
                    'analysis_duration': duration,
                    'plugin_name': plugin_name,
                    'plugin_version': self.metadata.version
                })
            
            return result
            
        except Exception as e:
            # Calculate duration even for failures
            duration = time.time() - start_time
            
            # Log failure
            print(f"ERROR: {plugin_name} failed {analysis_type.value} after {duration:.2f}s: {str(e)}")
            
            # Re-raise with plugin context
            raise PluginError(f"{plugin_name} analysis failed: {str(e)}") from e
    
    return wrapper


class PluginRegistry:
    """
    Central registry for managing analysis plugins.
    
    The registry handles plugin discovery, registration, validation,
    and selection for analysis tasks.
    """
    
    def __init__(self):
        self._plugins: Dict[str, AnalysisPlugin] = {}
        self._capabilities_map: Dict[AnalysisCapability, List[AnalysisPlugin]] = {}
        self._loaded_plugins: Set[str] = set()
    
    def register_plugin(self, plugin: AnalysisPlugin) -> None:
        """
        Register a plugin with the registry.
        
        Args:
            plugin: Plugin instance to register
            
        Raises:
            PluginError: If plugin validation fails
        """
        metadata = plugin.metadata
        
        # Validate plugin
        self._validate_plugin(plugin)
        
        # Check for name conflicts
        if metadata.name in self._plugins:
            existing_version = self._plugins[metadata.name].metadata.version
            if metadata.version != existing_version:
                print(f"WARNING: Replacing {metadata.name} v{existing_version} with v{metadata.version}")
        
        # Register plugin
        self._plugins[metadata.name] = plugin
        self._loaded_plugins.add(metadata.name)
        
        # Update capabilities map
        for capability in metadata.capabilities:
            if capability not in self._capabilities_map:
                self._capabilities_map[capability] = []
            
            # Remove existing instance if present
            self._capabilities_map[capability] = [
                p for p in self._capabilities_map[capability] 
                if p.metadata.name != metadata.name
            ]
            
            # Add new instance
            self._capabilities_map[capability].append(plugin)
        
        print(f"OK: Registered plugin: {metadata.name} v{metadata.version}")
    
    def _validate_plugin(self, plugin: AnalysisPlugin) -> None:
        """Validate plugin before registration."""
        metadata = plugin.metadata
        
        # Check required attributes
        if not hasattr(plugin, 'analyze'):
            raise PluginError(f"Plugin {metadata.name} missing analyze method")
        
        if not hasattr(plugin, 'can_analyze'):
            raise PluginError(f"Plugin {metadata.name} missing can_analyze method")
        
        if not hasattr(plugin, 'validate_structure'):
            raise PluginError(f"Plugin {metadata.name} missing validate_structure method")
        
        # Check dependencies (basic check)
        missing_deps = self._check_dependencies(metadata.dependencies)
        if missing_deps:
            print(f"WARNING: Plugin {metadata.name} has missing dependencies: {missing_deps}")
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check if dependencies are available."""
        missing = []
        
        for dep in dependencies:
            try:
                # Try to import the dependency
                if '=' in dep:
                    # Handle versioned dependencies like "PyNite>=1.0.15"
                    package_name = dep.split('=')[0].split('<')[0].split('>')[0]
                else:
                    package_name = dep
                
                __import__(package_name.replace('-', '_'))
                
            except ImportError:
                missing.append(dep)
        
        return missing
    
    def discover_plugins(self) -> None:
        """
        Auto-discover plugins in the plugins directory.
        
        This method looks for plugin modules and automatically
        registers any AnalysisPlugin subclasses found.
        """
        import pkgutil
        import importlib
        import inspect
        
        try:
            # Import the plugins package
            import pyfealite.plugins as plugins_package
            
            # Iterate through plugin modules
            for importer, modname, ispkg in pkgutil.iter_modules(plugins_package.__path__):
                if modname.startswith('_') or modname in ['base', 'registry']:
                    continue
                
                try:
                    # Import the plugin module
                    module = importlib.import_module(f'pyfealite.plugins.{modname}')
                    
                    # Look for plugin classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, AnalysisPlugin) and 
                            obj != AnalysisPlugin):
                            
                            # Instantiate and register plugin
                            try:
                                plugin_instance = obj()
                                self.register_plugin(plugin_instance)
                            except Exception as e:
                                print(f"WARNING: Failed to instantiate plugin {name}: {e}")
                
                except ImportError as e:
                    print(f"WARNING: Plugin module {modname} not available: {e}")
                except Exception as e:
                    print(f"WARNING: Error loading plugin module {modname}: {e}")
        
        except ImportError:
            print("WARNING: Plugins package not found - plugin discovery skipped")
    
    def get_plugin(self, name: str) -> Optional[AnalysisPlugin]:
        """Get plugin by name."""
        return self._plugins.get(name)
    
    def get_available_plugins(self) -> Dict[str, AnalysisPlugin]:
        """Get all available plugins."""
        return self._plugins.copy()
    
    def get_capabilities(self) -> List[AnalysisCapability]:
        """Get all available analysis capabilities."""
        return list(self._capabilities_map.keys())
    
    def get_capable_plugins(self, structure: 'Structure',
                           analysis_type: AnalysisCapability) -> List[AnalysisPlugin]:
        """
        Get plugins capable of handling the analysis.
        
        Args:
            structure: Structure to analyze
            analysis_type: Type of analysis
            
        Returns:
            List of capable plugins, sorted by priority
        """
        if analysis_type not in self._capabilities_map:
            return []
        
        capable = []
        
        for plugin in self._capabilities_map[analysis_type]:
            if plugin.can_analyze(structure, analysis_type):
                # Validate structure compatibility
                issues = plugin.validate_structure(structure)
                if not issues:
                    capable.append(plugin)
        
        # Sort by priority (higher first)
        return sorted(capable, key=lambda p: p.metadata.priority, reverse=True)
    
    def select_best_plugin(self, structure: 'Structure',
                          analysis_type: AnalysisCapability,
                          preferred_plugin: Optional[str] = None) -> AnalysisPlugin:
        """
        Select the best plugin for analysis.
        
        Args:
            structure: Structure to analyze
            analysis_type: Type of analysis
            preferred_plugin: Preferred plugin name (optional)
            
        Returns:
            Best plugin for the analysis
            
        Raises:
            PluginError: If no suitable plugin found
        """
        # Try preferred plugin first
        if preferred_plugin and preferred_plugin in self._plugins:
            plugin = self._plugins[preferred_plugin]
            if plugin.can_analyze(structure, analysis_type):
                issues = plugin.validate_structure(structure)
                if not issues:
                    return plugin
                else:
                    raise PluginError(
                        f"Preferred plugin {preferred_plugin} validation failed: {issues}"
                    )
        
        # Find capable plugins
        capable = self.get_capable_plugins(structure, analysis_type)
        
        if not capable:
            available_capabilities = [cap.value for cap in self.get_capabilities()]
            available_plugins = list(self._plugins.keys())
            
            raise PluginError(
                f"No plugin available for {analysis_type.value}.\n"
                f"Available capabilities: {available_capabilities}\n"
                f"Available plugins: {available_plugins}\n"
                f"Try: pip install pyfealite[3d] for 3D capabilities"
            )
        
        return capable[0]  # Highest priority plugin
    
    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered plugins."""
        info = {}
        
        for name, plugin in self._plugins.items():
            metadata = plugin.metadata
            info[name] = {
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'capabilities': [cap.value for cap in metadata.capabilities],
                'dependencies': metadata.dependencies,
                'priority': metadata.priority,
                'homepage': metadata.homepage
            }
        
        return info
    
    def get_installation_help(self, analysis_type: AnalysisCapability) -> str:
        """Get help for installing plugins that support an analysis type."""
        
        # Check if any registered plugin supports this (but may be unavailable)
        supporting_plugins = []
        for plugin in self._plugins.values():
            if analysis_type in plugin.metadata.capabilities:
                supporting_plugins.append(plugin)
        
        if supporting_plugins:
            plugin = supporting_plugins[0]
            deps = plugin.metadata.dependencies

            # Handle versioned/package strings like 'PyNite>=1.0.15' or 'pynite'
            if any('pynite' in (d or '').lower() for d in deps):
                return "Install 3D capabilities: pip install pyfealite[3d]"
            elif any('nonlinear' in (d or '').lower() for d in deps):
                return "Install nonlinear: pip install pyfealite[nonlinear]"
            else:
                # Fall back to a simple pip install instruction
                return f"Install dependencies: pip install {' '.join(deps)}"
        else:
            return f"No plugin available for {analysis_type.value}"