"""Point load implementations."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
import numpy as np

from .base import Load, LoadDirection, LoadCase

if TYPE_CHECKING:
    from ..core.element import FrameElement2D
    from ..core.node import Node2D


class PointLoad(Load):
    """
    Point load applied to an element at a specific location.
    
    Attributes:
        load_case: Associated load case
        Fx: Force in X direction
        Fy: Force in Y direction
        Mz: Moment about Z axis
        distance: Distance from start node (0 to element.length)
        direction: Load coordinate system
        label: Load identifier
    """
    
    def __init__(self, load_case: LoadCase, Fx: float, Fy: float, Mz: float = 0.0, 
                 distance: float = 0.0, direction: LoadDirection = LoadDirection.GLOBAL, label: str = ""):
        super().__init__(load_case, direction, label)
        self.Fx = Fx
        self.Fy = Fy
        self.Mz = Mz
        self.distance = distance
        self._validate()
    
    def _validate(self) -> None:
        """Validate point load parameters."""
        if self.distance < 0:
            raise ValueError("Distance must be non-negative")
    
    
    def get_equivalent_nodal_forces(self, element: 'FrameElement2D') -> np.ndarray:
        """
        Calculate equivalent nodal forces using virtual work principle.
        
        For a point load at distance 'a' from start:
        - R1y = P * b/L (where b = L - a)
        - R2y = P * a/L
        - M1 = P * a * b^2 / L^2
        - M2 = -P * a^2 * b / L^2
        """
        if self.distance > element.length:
            raise ValueError(f"Load distance {self.distance} exceeds element length {element.length}")
        
        L = element.length
        a = self.distance
        b = L - a
        
        # Initialize forces array [Fx1, Fy1, Mz1, Fx2, Fy2, Mz2]
        forces = np.zeros(6)
        
        if L == 0:
            return forces
        
        # Axial force distribution (uniform)
        forces[0] = -self.Fx * b / L  # Start node
        forces[3] = -self.Fx * a / L  # End node
        
        # Transverse force and moment distribution
        if abs(self.Fy) > 1e-12:
            forces[1] = -self.Fy * b / L
            forces[4] = -self.Fy * a / L
            
            # Fixed end moments due to transverse load
            if a > 1e-12 and b > 1e-12:  # Avoid division by zero
                forces[2] = -self.Fy * a * b * b / (L * L)
                forces[5] = self.Fy * a * a * b / (L * L)
        
        # Applied moment distribution
        if abs(self.Mz) > 1e-12:
            forces[2] += -self.Mz * b / L
            forces[5] += -self.Mz * a / L
        
        # Transform to global coordinates if needed
        return self.transform_to_global(forces, element)
    
    def __str__(self) -> str:
        return (f"PointLoad('{self.label}', F=({self.Fx}, {self.Fy}), "
                f"M={self.Mz}, d={self.distance})")


class NodalLoad(Load):
    """
    Load applied directly to a node.
    
    Attributes:
        load_case: Associated load case
        node: Target node
        Fx: Force in X direction
        Fy: Force in Y direction
        Mz: Moment about Z axis
        direction: Load coordinate system
        label: Load identifier
    """
    
    def __init__(self, load_case: LoadCase, node: 'Node2D', Fx: float, Fy: float, 
                 Mz: float = 0.0, direction: LoadDirection = LoadDirection.GLOBAL, label: str = ""):
        super().__init__(load_case, direction, label)
        self.node = node
        self.Fx = Fx
        self.Fy = Fy
        self.Mz = Mz
    
    def get_equivalent_nodal_forces(self, element: 'FrameElement2D') -> np.ndarray:
        """
        Get equivalent nodal forces for nodal loads.
        
        Note: Nodal loads are typically handled directly by the structure
        rather than through elements, but this method is provided for
        completeness.
        """
        forces = np.zeros(6)
        
        if self.node == element.start_node:
            forces[0] = self.Fx
            forces[1] = self.Fy
            forces[2] = self.Mz
        elif self.node == element.end_node:
            forces[3] = self.Fx
            forces[4] = self.Fy
            forces[5] = self.Mz
        
        # Nodal loads are typically already in global coordinates
        # but still apply transformation if specified as local
        return self.transform_to_global(forces, element)
    
    def get_force_vector(self) -> np.ndarray:
        """Get force vector for direct application to global force vector."""
        return np.array([self.Fx, self.Fy, self.Mz])
    
    def __str__(self) -> str:
        return (f"NodalLoad('{self.label}', node='{self.node.label}', "
                f"F=({self.Fx}, {self.Fy}), M={self.Mz})")