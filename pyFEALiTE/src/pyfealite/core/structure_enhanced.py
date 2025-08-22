"""
Enhanced Structure class with Plugin Architecture support.

This module extends the base Structure class with plugin-aware analysis capabilities
while maintaining backward compatibility with existing PyFEALiTE code.
"""

from typing import Optional, Dict, Any, List, Union
import numpy as np
from dataclasses import dataclass, field

# Import base structure
from .structure import Structure as BaseStructure

# Import plugin system
from ..plugins.base import AnalysisCapability
from ..plugins.registry import plugin_registry


@dataclass
class EnhancedStructure(BaseStructure):
    """
    Enhanced structure with plugin architecture support.
    
    This class extends the base Structure with:
    - Plugin-aware analysis methods
    - Automatic engine selection
    - 2D/3D capability detection
    - Unified analysis interface
    """
    
    # Plugin system integration
    _plugin_registry: Any = field(default=plugin_registry, init=False, repr=False)
    _last_results: Optional['AnalysisResults'] = field(default=None, init=False, repr=False)
    _analysis_dimension: str = field(default="2D", init=False, repr=False)  # "2D" or "3D"
    
    def solve(self, 
              analysis_type: str = "static",
              engine: Optional[str] = None,
              **kwargs) -> 'AnalysisResults':
        """
        Enhanced solve method using plugin architecture.
        
        Args:
            analysis_type: Type of analysis ("static", "modal", "p_delta", etc.)
            engine: Preferred engine/plugin name (optional)
            **kwargs: Additional analysis parameters
            
        Returns:
            AnalysisResults: Results from the selected plugin
            
        Examples:
            >>> structure = EnhancedStructure("My Frame")
            >>> # ... add nodes, elements, loads ...
            >>> 
            >>> # 2D static analysis (automatic core engine)
            >>> results = structure.solve("static")
            >>> 
            >>> # 3D analysis (automatic PyNite plugin if available)
            >>> structure.add_plate_element(...)  # Forces 3D mode
            >>> results = structure.solve("static")  # Uses 3D plugin
            >>> 
            >>> # Specific engine selection
            >>> results = structure.solve("static", engine="PyNite 3D")
        """
        
        # Map analysis type string to capability enum
        capability = self._map_analysis_type(analysis_type)
        
        # Auto-detect analysis dimension if not specified
        if capability == AnalysisCapability.STATIC_2D:
            if self._requires_3d_analysis():
                capability = AnalysisCapability.STATIC_3D
                self._analysis_dimension = "3D"
            else:
                self._analysis_dimension = "2D"
        
        # Display analysis info
        print(f"🏗️  Analyzing '{self.name}' - {capability.value}")
        print(f"📐 Analysis dimension: {self._analysis_dimension}")
        
        try:
            # Select appropriate plugin
            plugin = self._plugin_registry.select_best_plugin(
                structure=self,
                analysis_type=capability,
                preferred_plugin=engine
            )
            
            print(f"🔧 Selected engine: {plugin.metadata.name} v{plugin.metadata.version}")
            
            # Perform analysis
            results = plugin.analyze(self, capability, **kwargs)
            
            # Store results
            self._last_results = results
            self._analysis_status = "success"
            
            # Update legacy result storage for backward compatibility
            if hasattr(results, 'displacements') and results.displacements:
                self._displacements = results.displacements
            
            if hasattr(results, 'reactions') and results.reactions:
                self._reactions = results.reactions
            
            print(f"✅ Analysis completed successfully using {plugin.metadata.name}")
            
            return results
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            self._analysis_status = "failed"
            raise
    
    def get_available_analyses(self) -> Dict[str, List[str]]:
        """
        Get available analysis types by engine.
        
        Returns:
            Dict mapping plugin names to their capabilities
            
        Example:
            >>> structure.get_available_analyses()
            {
                'PyFEALiTE Core': ['static_2d', 'modal_2d', 'dynamic_2d'],
                'PyNite 3D': ['static_3d', 'modal_3d', 'p_delta', 'buckling']
            }
        """
        available = {}
        
        for plugin_name, plugin in self._plugin_registry.get_available_plugins().items():
            capabilities = [cap.value for cap in plugin.metadata.capabilities]
            available[plugin_name] = capabilities
        
        return available
    
    def check_analysis_requirements(self, analysis_type: str) -> Dict[str, Any]:
        """
        Check requirements for a specific analysis type.
        
        Args:
            analysis_type: Analysis type to check
            
        Returns:
            Dict with availability info and requirements
            
        Example:
            >>> info = structure.check_analysis_requirements("p_delta")
            >>> if not info['available']:
            >>>     print(info['install_command'])
        """
        capability = self._map_analysis_type(analysis_type)
        
        capable_plugins = self._plugin_registry.get_capable_plugins(self, capability)
        
        if capable_plugins:
            return {
                "available": True,
                "engines": [p.metadata.name for p in capable_plugins],
                "recommended": capable_plugins[0].metadata.name,
                "dimension": "3D" if "3d" in analysis_type else "2D"
            }
        else:
            # Find plugins that support this capability but can't handle structure
            all_plugins = self._plugin_registry.get_available_plugins().values()
            supporting_plugins = [
                p for p in all_plugins 
                if capability in p.metadata.capabilities
            ]
            
            if supporting_plugins:
                plugin = supporting_plugins[0]
                issues = plugin.validate_structure(self)
                
                return {
                    "available": False,
                    "issues": issues,
                    "required_plugin": plugin.metadata.name,
                    "install_command": self._get_install_command(plugin.metadata.dependencies)
                }
            else:
                available_types = []
                for plugin in all_plugins:
                    available_types.extend([cap.value for cap in plugin.metadata.capabilities])
                
                return {
                    "available": False,
                    "message": f"No plugin supports '{analysis_type}'",
                    "available_analyses": list(set(available_types))
                }
    
    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about all available plugins."""
        return self._plugin_registry.get_plugin_info()
    
    def validate_for_analysis(self, analysis_type: str) -> List[str]:
        """
        Validate structure for a specific analysis type.
        
        Args:
            analysis_type: Type of analysis to validate for
            
        Returns:
            List of validation issues (empty if valid)
        """
        capability = self._map_analysis_type(analysis_type)
        
        try:
            plugin = self._plugin_registry.select_best_plugin(self, capability)
            return plugin.validate_structure(self)
        except Exception as e:
            return [str(e)]
    
    # Convenience methods for specific analysis types
    def static_analysis(self, **kwargs):
        """Perform static analysis with auto-dimension detection."""
        return self.solve("static", **kwargs)
    
    def modal_analysis(self, num_modes: int = 10, **kwargs):
        """Perform modal analysis."""
        return self.solve("modal", num_modes=num_modes, **kwargs)
    
    def p_delta_analysis(self, **kwargs):
        """Perform P-Δ second-order analysis (requires 3D plugin)."""
        return self.solve("p_delta", **kwargs)
    
    def buckling_analysis(self, num_modes: int = 5, **kwargs):
        """Perform linear buckling analysis (requires 3D plugin)."""
        return self.solve("buckling", num_modes=num_modes, **kwargs)
    
    def dynamic_analysis(self, ground_motion: np.ndarray, dt: float = 0.01, **kwargs):
        """Perform dynamic time-history analysis."""
        return self.solve("dynamic", ground_motion=ground_motion, dt=dt, **kwargs)
    
    # 3D capability detection methods
    def _requires_3d_analysis(self) -> bool:
        """Auto-detect if 3D analysis is needed."""
        
        # Check for 3D elements
        for element in self.elements:
            if hasattr(element, 'element_type'):
                element_type = getattr(element, 'element_type', '').lower()
                if ('plate' in element_type or 
                    'shell' in element_type or 
                    '3d' in element_type):
                    return True
        
        # Check for out-of-plane loads
        for element in self.elements:
            for load in getattr(element, 'loads', []):
                if hasattr(load, 'Fz') and abs(getattr(load, 'Fz', 0)) > 1e-9:
                    return True
                if hasattr(load, 'Mx') and abs(getattr(load, 'Mx', 0)) > 1e-9:
                    return True
                if hasattr(load, 'My') and abs(getattr(load, 'My', 0)) > 1e-9:
                    return True
        
        # Check for 3D node coordinates
        for node in self.nodes:
            if hasattr(node, 'z') and abs(getattr(node, 'z', 0)) > 1e-9:
                return True
        
        return False
    
    def force_3d_mode(self) -> None:
        """Force structure into 3D analysis mode."""
        self._analysis_dimension = "3D"
        print("🌐 Structure set to 3D analysis mode")
    
    def force_2d_mode(self) -> None:
        """Force structure into 2D analysis mode."""
        self._analysis_dimension = "2D"
        print("📐 Structure set to 2D analysis mode")
    
    # Utility methods
    def _map_analysis_type(self, analysis_type: str) -> AnalysisCapability:
        """Map string to analysis capability enum."""
        
        # Handle dimension-specific mapping
        if self._analysis_dimension == "3D":
            dimension_mapping = {
                "static": AnalysisCapability.STATIC_3D,
                "modal": AnalysisCapability.MODAL_3D,
                "dynamic": AnalysisCapability.DYNAMIC_3D
            }
        else:  # 2D
            dimension_mapping = {
                "static": AnalysisCapability.STATIC_2D,
                "modal": AnalysisCapability.MODAL_2D,
                "dynamic": AnalysisCapability.DYNAMIC_2D
            }
        
        # Full mapping including specific types
        full_mapping = {
            **dimension_mapping,
            "static_2d": AnalysisCapability.STATIC_2D,
            "static_3d": AnalysisCapability.STATIC_3D,
            "modal_2d": AnalysisCapability.MODAL_2D,
            "modal_3d": AnalysisCapability.MODAL_3D,
            "dynamic_2d": AnalysisCapability.DYNAMIC_2D,
            "dynamic_3d": AnalysisCapability.DYNAMIC_3D,
            "p_delta": AnalysisCapability.P_DELTA,
            "buckling": AnalysisCapability.BUCKLING,
            "nonlinear": AnalysisCapability.NONLINEAR,
            "plates": AnalysisCapability.PLATES,
            "shells": AnalysisCapability.SHELLS,
            "optimization": AnalysisCapability.OPTIMIZATION
        }
        
        if analysis_type not in full_mapping:
            available = list(full_mapping.keys())
            raise ValueError(
                f"Unknown analysis type '{analysis_type}'. "
                f"Available types: {available}"
            )
        
        return full_mapping[analysis_type]
    
    def _get_install_command(self, dependencies: List[str]) -> str:
        """Generate install command for missing dependencies."""
        
        if any("PyNite" in dep for dep in dependencies):
            return "pip install pyfealite[3d]"
        elif any("nonlinear" in dep.lower() for dep in dependencies):
            return "pip install pyfealite[nonlinear]"
        elif any("ai" in dep.lower() or "optim" in dep.lower() for dep in dependencies):
            return "pip install pyfealite[ai]"
        else:
            return f"pip install {' '.join(dependencies)}"
    
    # Backward compatibility methods
    def solve_legacy(self) -> None:
        """Legacy solve method for backward compatibility."""
        print("⚠️  Using legacy solve method. Consider using solve('static') instead.")
        return super().solve()
    
    def get_last_results(self) -> Optional['AnalysisResults']:
        """Get results from last analysis."""
        return self._last_results


# Create alias for backward compatibility
Structure = EnhancedStructure


# Convenience function for creating structures
def create_structure(name: str = "Structure") -> Structure:
    """
    Create a new enhanced structure.
    
    Args:
        name: Structure name
        
    Returns:
        New Structure instance with plugin support
    """
    return Structure(name=name)


# Plugin-aware solve function
def solve_structure(structure: Structure, 
                   analysis_type: str = "static",
                   **kwargs) -> 'AnalysisResults':
    """
    Solve structure using plugin architecture.
    
    Args:
        structure: Structure to analyze
        analysis_type: Type of analysis
        **kwargs: Analysis parameters
        
    Returns:
        Analysis results
    """
    return structure.solve(analysis_type=analysis_type, **kwargs)