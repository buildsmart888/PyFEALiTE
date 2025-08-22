"""
Analysis Results Classes

This module defines classes for storing and managing analysis results
from different plugins and analysis types.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
import numpy as np


@dataclass
class AnalysisResults:
    """
    Container for analysis results from any plugin.
    
    This class provides a unified interface for storing results from
    different analysis types and engines while maintaining flexibility
    for plugin-specific data.
    """
    
    # Core result information
    analysis_type: str
    status: str  # "success", "failed", "warning"
    engine: str  # Name of plugin that performed analysis
    
    # Common structural analysis results
    displacements: Optional[Dict] = None
    reactions: Optional[Dict] = None
    internal_forces: Optional[Dict] = None
    
    # Modal analysis results
    frequencies: Optional[np.ndarray] = None
    periods: Optional[np.ndarray] = None
    mode_shapes: Optional[np.ndarray] = None
    modal_masses: Optional[np.ndarray] = None
    mass_participation: Optional[np.ndarray] = None
    
    # Dynamic analysis results
    time: Optional[np.ndarray] = None
    displacement: Optional[np.ndarray] = None
    velocity: Optional[np.ndarray] = None
    acceleration: Optional[np.ndarray] = None
    base_shear: Optional[np.ndarray] = None
    
    # Specialized analysis results
    p_delta_effects: Optional[Dict] = None
    buckling_modes: Optional[np.ndarray] = None
    buckling_factors: Optional[np.ndarray] = None
    
    # Metadata and additional information
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize result object after creation."""
        if self.metadata is None:
            self.metadata = {}
    
    def add_warning(self, message: str) -> None:
        """Add a warning message to the results."""
        self.warnings.append(message)
    
    def add_error(self, message: str) -> None:
        """Add an error message to the results."""
        self.errors.append(message)
        if self.status != "failed":
            self.status = "warning"
    
    def has_warnings(self) -> bool:
        """Check if results have warnings."""
        return len(self.warnings) > 0
    
    def has_errors(self) -> bool:
        """Check if results have errors."""
        return len(self.errors) > 0
    
    def is_successful(self) -> bool:
        """Check if analysis was successful."""
        return self.status == "success"
    
    def get_max_displacement(self) -> Optional[float]:
        """Get maximum displacement magnitude."""
        if self.displacements is None:
            return None
        
        max_disp = 0.0
        for disp_array in self.displacements.values():
            if isinstance(disp_array, np.ndarray):
                max_disp = max(max_disp, np.max(np.abs(disp_array)))
            elif isinstance(disp_array, dict):
                for node_disp in disp_array.values():
                    if isinstance(node_disp, np.ndarray):
                        max_disp = max(max_disp, np.max(np.abs(node_disp)))
        
        return max_disp
    
    def get_max_reaction(self) -> Optional[float]:
        """Get maximum reaction magnitude."""
        if self.reactions is None:
            return None
        
        max_reaction = 0.0
        for reaction_data in self.reactions.values():
            if isinstance(reaction_data, dict):
                for node_reaction in reaction_data.values():
                    if isinstance(node_reaction, np.ndarray):
                        max_reaction = max(max_reaction, np.max(np.abs(node_reaction)))
            elif isinstance(reaction_data, np.ndarray):
                max_reaction = max(max_reaction, np.max(np.abs(reaction_data)))
        
        return max_reaction
    
    def get_summary(self) -> str:
        """Get a summary string of the analysis results."""
        summary = [
            f"Analysis: {self.analysis_type}",
            f"Engine: {self.engine}",
            f"Status: {self.status}"
        ]
        
        if self.displacements is not None:
            max_disp = self.get_max_displacement()
            if max_disp is not None:
                summary.append(f"Max displacement: {max_disp:.6f}")
        
        if self.reactions is not None:
            max_reaction = self.get_max_reaction()
            if max_reaction is not None:
                summary.append(f"Max reaction: {max_reaction:.2f}")
        
        if self.frequencies is not None:
            summary.append(f"Frequencies: {len(self.frequencies)} modes")
            if len(self.frequencies) > 0:
                summary.append(f"First frequency: {self.frequencies[0]:.3f} Hz")
        
        if len(self.warnings) > 0:
            summary.append(f"Warnings: {len(self.warnings)}")
        
        if len(self.errors) > 0:
            summary.append(f"Errors: {len(self.errors)}")
        
        return "\n".join(summary)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for serialization."""
        result_dict = {
            'analysis_type': self.analysis_type,
            'status': self.status,
            'engine': self.engine,
            'metadata': self.metadata,
            'warnings': self.warnings,
            'errors': self.errors
        }
        
        # Add numpy arrays and other data as needed
        if self.displacements is not None:
            result_dict['has_displacements'] = True
        
        if self.reactions is not None:
            result_dict['has_reactions'] = True
        
        if self.frequencies is not None:
            result_dict['frequencies'] = self.frequencies.tolist()
        
        if self.periods is not None:
            result_dict['periods'] = self.periods.tolist()
        
        return result_dict
    
    def save_to_file(self, filename: str) -> None:
        """Save results to file (basic implementation)."""
        import json
        
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'AnalysisResults':
        """Load results from file (basic implementation)."""
        import json
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Basic reconstruction - would need more sophisticated handling
        # for numpy arrays and complex data structures
        return cls(
            analysis_type=data['analysis_type'],
            status=data['status'],
            engine=data['engine'],
            metadata=data.get('metadata', {}),
            warnings=data.get('warnings', []),
            errors=data.get('errors', [])
        )