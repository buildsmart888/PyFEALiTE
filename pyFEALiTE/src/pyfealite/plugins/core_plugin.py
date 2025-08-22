"""
Core PyFEALiTE Plugin

This plugin wraps the existing PyFEALiTE 2D analysis capabilities
in the new plugin architecture.
"""

from typing import List
import numpy as np

from .base import (
    AnalysisPlugin, 
    PluginMetadata, 
    AnalysisCapability,
    track_analysis_performance
)


class PyFEALiTECorePlugin(AnalysisPlugin):
    """
    Core PyFEALiTE 2D analysis engine plugin.
    
    This plugin provides the native PyFEALiTE 2D structural analysis
    capabilities including static analysis, modal analysis, and 
    advanced visualization features.
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="PyFEALiTE Core",
            version="2.0.0",
            description="Native 2D structural analysis engine with professional visualization",
            author="PyFEALiTE Team",
            capabilities=[
                AnalysisCapability.STATIC_2D,
                AnalysisCapability.MODAL_2D,
                AnalysisCapability.DYNAMIC_2D
            ],
            dependencies=[],  # Core has no external dependencies
            min_pyfealite_version="2.0.0",
            priority=100,  # Highest priority for 2D analysis
            homepage="https://github.com/pyfealite/pyfealite"
        )
    
    def can_analyze(self, structure, analysis_type: AnalysisCapability) -> bool:
        """Check if core engine can handle analysis."""
        
        # Core engine handles 2D analyses
        supported = {
            AnalysisCapability.STATIC_2D,
            AnalysisCapability.MODAL_2D,
            AnalysisCapability.DYNAMIC_2D
        }
        
        if analysis_type not in supported:
            return False
        
        # Check if structure is purely 2D
        return self._is_2d_structure(structure)
    
    def validate_structure(self, structure) -> List[str]:
        """Validate structure for core engine."""
        issues = []
        
        # Check for 3D elements
        for element in structure.elements:
            if hasattr(element, 'element_type'):
                element_type = getattr(element, 'element_type', '').lower()
                if 'plate' in element_type or 'shell' in element_type:
                    issues.append(
                        f"Element {element.label} is a 3D element (type: {element_type}). "
                        f"Install 3D plugin: pip install pyfealite[3d]"
                    )
        
        # Check for out-of-plane loads
        for element in structure.elements:
            for load in getattr(element, 'loads', []):
                # Check for Z-direction forces
                if hasattr(load, 'Fz') and abs(getattr(load, 'Fz', 0)) > 1e-9:
                    issues.append(
                        f"Out-of-plane force (Fz={load.Fz}) on element {element.label}. "
                        f"Requires 3D analysis: pip install pyfealite[3d]"
                    )
                
                # Check for X/Y moments (out-of-plane)
                if hasattr(load, 'Mx') and abs(getattr(load, 'Mx', 0)) > 1e-9:
                    issues.append(
                        f"Out-of-plane moment (Mx={load.Mx}) on element {element.label}. "
                        f"Requires 3D analysis: pip install pyfealite[3d]"
                    )
                
                if hasattr(load, 'My') and abs(getattr(load, 'My', 0)) > 1e-9:
                    issues.append(
                        f"Out-of-plane moment (My={load.My}) on element {element.label}. "
                        f"Requires 3D analysis: pip install pyfealite[3d]"
                    )
        
        # Check nodes for 3D coordinates
        for node in structure.nodes:
            if hasattr(node, 'z') and abs(getattr(node, 'z', 0)) > 1e-9:
                issues.append(
                    f"Node {node.label} has non-zero Z coordinate (z={node.z}). "
                    f"Consider 3D analysis: pip install pyfealite[3d]"
                )
        
        return issues
    
    @track_analysis_performance
    def analyze(self, structure, analysis_type: AnalysisCapability, **kwargs):
        """Perform analysis using core engine."""
        
        if analysis_type == AnalysisCapability.STATIC_2D:
            return self._static_analysis(structure, **kwargs)
        elif analysis_type == AnalysisCapability.MODAL_2D:
            return self._modal_analysis(structure, **kwargs)
        elif analysis_type == AnalysisCapability.DYNAMIC_2D:
            return self._dynamic_analysis(structure, **kwargs)
        else:
            raise ValueError(f"Core plugin does not support {analysis_type.value}")
    
    def _static_analysis(self, structure, **kwargs):
        """Static analysis using native PyFEALiTE solver."""
        
        # Use existing solve method
        structure.solve()
        
        # Create analysis results object
        from ..analysis.results import AnalysisResults
        
        return AnalysisResults(
            analysis_type="static_2d",
            displacements=structure._displacements,
            reactions=structure._reactions,
            status="success",
            engine="PyFEALiTE Core",
            metadata={
                'solver': 'Direct sparse solver (SciPy)',
                'dof_count': structure.get_total_dof() if hasattr(structure, 'get_total_dof') else 'unknown',
                'elements': len(structure.elements),
                'nodes': len(structure.nodes),
                'load_cases': len(structure.load_cases)
            }
        )
    
    def _modal_analysis(self, structure, **kwargs):
        """Modal analysis using PyFEALiTE dynamics module."""
        
        try:
            from ..dynamics.modal_analysis import ModalAnalyzer
            
            num_modes = kwargs.get('num_modes', 10)
            
            analyzer = ModalAnalyzer(structure)
            modal_results = analyzer.solve_eigenvalue_problem(num_modes=num_modes)
            
            from ..analysis.results import AnalysisResults
            
            return AnalysisResults(
                analysis_type="modal_2d",
                frequencies=modal_results.frequencies,
                periods=modal_results.periods,
                mode_shapes=modal_results.mode_shapes,
                modal_masses=modal_results.modal_masses,
                status="success",
                engine="PyFEALiTE Core",
                metadata={
                    'num_modes': num_modes,
                    'frequency_range': f"{modal_results.frequencies.min():.2f} - {modal_results.frequencies.max():.2f} Hz",
                    'period_range': f"{modal_results.periods.min():.3f} - {modal_results.periods.max():.3f} sec"
                }
            )
            
        except ImportError:
            raise ImportError(
                "Modal analysis requires dynamics module. "
                "This feature is not yet implemented in the core plugin."
            )
    
    def _dynamic_analysis(self, structure, **kwargs):
        """Dynamic analysis using PyFEALiTE dynamics module."""
        
        try:
            from ..dynamics.time_history import TimeHistoryAnalyzer
            
            ground_motion = kwargs.get('ground_motion')
            dt = kwargs.get('dt', 0.01)
            
            if ground_motion is None:
                raise ValueError("Dynamic analysis requires ground_motion parameter")
            
            analyzer = TimeHistoryAnalyzer(structure)
            results = analyzer.newmark_integration(ground_motion, dt)
            
            from ..analysis.results import AnalysisResults
            
            return AnalysisResults(
                analysis_type="dynamic_2d",
                time=results.time,
                displacement=results.displacement,
                velocity=results.velocity,
                acceleration=results.acceleration,
                base_shear=results.base_shear,
                status="success",
                engine="PyFEALiTE Core",
                metadata={
                    'time_steps': len(results.time),
                    'dt': dt,
                    'duration': results.time[-1],
                    'max_base_shear': np.max(np.abs(results.base_shear))
                }
            )
            
        except ImportError:
            raise ImportError(
                "Dynamic analysis requires dynamics module. "
                "This feature is not yet implemented in the core plugin."
            )
    
    def _is_2d_structure(self, structure) -> bool:
        """Check if structure is purely 2D."""
        
        # Check for 3D elements
        for element in structure.elements:
            if hasattr(element, 'element_type'):
                element_type = getattr(element, 'element_type', '').lower()
                if ('3d' in element_type or 
                    'plate' in element_type or 
                    'shell' in element_type):
                    return False
        
        # Check for out-of-plane loads
        for element in structure.elements:
            for load in getattr(element, 'loads', []):
                if (hasattr(load, 'Fz') and abs(getattr(load, 'Fz', 0)) > 1e-9):
                    return False
                if (hasattr(load, 'Mx') and abs(getattr(load, 'Mx', 0)) > 1e-9):
                    return False  
                if (hasattr(load, 'My') and abs(getattr(load, 'My', 0)) > 1e-9):
                    return False
        
        # Check for non-planar nodes
        for node in structure.nodes:
            if hasattr(node, 'z') and abs(getattr(node, 'z', 0)) > 1e-9:
                return False
        
        return True
    
    def get_analysis_info(self, analysis_type: AnalysisCapability):
        """Get detailed information about analysis types."""
        
        info = super().get_analysis_info(analysis_type)
        
        if analysis_type == AnalysisCapability.STATIC_2D:
            info.update({
                "description": "2D static linear analysis with sparse matrix solver",
                "parameters": {
                    "tolerance": "Convergence tolerance (default: 1e-12)",
                    "max_iterations": "Maximum iterations (default: 1000)"
                },
                "requirements": [
                    "2D frame/beam/truss elements only",
                    "In-plane loading only", 
                    "Linear materials and geometry"
                ]
            })
        
        elif analysis_type == AnalysisCapability.MODAL_2D:
            info.update({
                "description": "2D modal analysis with eigenvalue solver",
                "parameters": {
                    "num_modes": "Number of modes to extract (default: 10)",
                    "mass_type": "Mass matrix type: 'consistent' or 'lumped' (default: 'consistent')"
                },
                "requirements": [
                    "Material density must be defined",
                    "Structure must have mass",
                    "Stable structure (no mechanisms)"
                ]
            })
        
        elif analysis_type == AnalysisCapability.DYNAMIC_2D:
            info.update({
                "description": "2D dynamic time-history analysis",
                "parameters": {
                    "ground_motion": "Ground acceleration array [g]",
                    "dt": "Time step [sec] (default: 0.01)",
                    "damping_ratio": "Modal damping ratio (default: 0.05)"
                },
                "requirements": [
                    "Ground motion time series",
                    "Material properties including density",
                    "Appropriate time step for analysis"
                ]
            })
        
        return info