"""Distributed load implementations."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
import numpy as np

from .base import Load, LoadDirection, LoadCase

if TYPE_CHECKING:
    from ..core.element import FrameElement2D


class UniformLoad(Load):
    """
    Uniformly distributed load over element length or portion.
    
    Attributes:
        load_case: Associated load case
        wx: Distributed force per unit length in X direction
        wy: Distributed force per unit length in Y direction
        start_distance: Start position from element start (default: 0)
        end_distance: End position from element start (default: full length)
        direction: Load coordinate system
        label: Load identifier
    """
    
    def __init__(self, load_case: LoadCase, wx: float, wy: float, 
                 start_distance: float = 0.0, end_distance: float = -1.0,
                 direction: LoadDirection = LoadDirection.GLOBAL, label: str = ""):
        super().__init__(load_case, direction, label)
        self.wx = wx
        self.wy = wy
        self.start_distance = start_distance
        self.end_distance = end_distance
        self._validate()
    
    def _validate(self) -> None:
        """Validate uniform load parameters."""
        if self.start_distance < 0:
            raise ValueError("Start distance must be non-negative")
        if self.end_distance >= 0 and self.end_distance <= self.start_distance:
            raise ValueError("End distance must be greater than start distance")
    
    def get_equivalent_nodal_forces(self, element: 'FrameElement2D') -> np.ndarray:
        """
        Calculate equivalent nodal forces for uniform distributed load.
        
        For uniform load w over length L:
        - R1y = R2y = w*L/2
        - M1 = -w*L²/12
        - M2 = +w*L²/12
        """
        L = element.length
        start = self.start_distance
        end = self.end_distance if self.end_distance > 0 else L
        
        if start >= L or end > L:
            raise ValueError("Load distances exceed element length")
        
        # Load length and position
        load_length = end - start
        load_center = start + load_length / 2
        
        # Distance from element center to load center
        element_center = L / 2
        e = load_center - element_center
        
        # Total loads
        Px_total = self.wx * load_length
        Py_total = self.wy * load_length
        
        # Initialize forces array [Fx1, Fy1, Mz1, Fx2, Fy2, Mz2]
        forces = np.zeros(6)
        
        # Axial load distribution
        forces[0] = -Px_total / 2
        forces[3] = -Px_total / 2
        
        # Transverse load distribution
        if abs(self.wy) > 1e-12:
            forces[1] = -Py_total / 2
            forces[4] = -Py_total / 2
            
            # Moments due to eccentricity
            forces[2] += Py_total * e
            forces[5] += -Py_total * e
            
            # Additional moments for partial loading
            if load_length < L:
                # More complex calculation for partial distributed loads
                a = start
                b = end
                L2 = L * L
                
                # Fixed end moments for partial uniform load
                if a > 1e-12:  # Load doesn't start at beginning
                    M1_partial = -Py_total * (L2 - 6*a*L + 6*a*a) / (12*L)
                    M2_partial = Py_total * a * (2*L - 3*a) / (12*L)
                else:  # Load starts at beginning
                    M1_partial = -self.wy * b * b * (6*L*L - 8*L*b + 3*b*b) / (12*L*L)
                    M2_partial = self.wy * b * b * b / (12*L)
                
                forces[2] = M1_partial
                forces[5] = M2_partial
            else:
                # Full length uniform load
                M_uniform = self.wy * L * L / 12
                forces[2] = -M_uniform
                forces[5] = M_uniform
        
        return self.transform_to_global(forces, element)
    
    def __str__(self) -> str:
        return (f"UniformLoad('{self.label}', w=({self.wx}, {self.wy}), "
                f"span={self.start_distance}-{self.end_distance})")


class TrapezoidalLoad(Load):
    """
    Trapezoidally distributed load over element length or portion.
    
    Attributes:
        load_case: Associated load case
        wx1: Distributed force per unit length in X at start
        wy1: Distributed force per unit length in Y at start
        wx2: Distributed force per unit length in X at end
        wy2: Distributed force per unit length in Y at end
        start_distance: Start position from element start (default: 0)
        end_distance: End position from element start (default: full length)
        direction: Load coordinate system
        label: Load identifier
    """
    
    def __init__(self, load_case: LoadCase, wx1: float, wy1: float, 
                 wx2: float, wy2: float, start_distance: float = 0.0, 
                 end_distance: float = -1.0, direction: LoadDirection = LoadDirection.GLOBAL, label: str = ""):
        super().__init__(load_case, direction, label)
        self.wx1 = wx1
        self.wy1 = wy1
        self.wx2 = wx2
        self.wy2 = wy2
        self.start_distance = start_distance
        self.end_distance = end_distance
        self._validate()
    
    def _validate(self) -> None:
        """Validate trapezoidal load parameters."""
        if self.start_distance < 0:
            raise ValueError("Start distance must be non-negative")
        if self.end_distance >= 0 and self.end_distance <= self.start_distance:
            raise ValueError("End distance must be greater than start distance")
    
    def get_equivalent_nodal_forces(self, element: 'FrameElement2D') -> np.ndarray:
        """
        Calculate equivalent nodal forces for trapezoidal distributed load.
        
        Trapezoidal load is decomposed into:
        1. Uniform component: (w1 + w2) / 2
        2. Triangular component: (w2 - w1)
        """
        L = element.length
        start = self.start_distance
        end = self.end_distance if self.end_distance > 0 else L
        
        if start >= L or end > L:
            raise ValueError("Load distances exceed element length")
        
        load_length = end - start
        
        # Decompose into uniform and triangular parts
        w_uniform_x = (self.wx1 + self.wx2) / 2
        w_uniform_y = (self.wy1 + self.wy2) / 2
        
        w_triangular_x = self.wx2 - self.wx1
        w_triangular_y = self.wy2 - self.wy1
        
        forces = np.zeros(6)
        
        # Uniform component (acts at center of loaded length)
        if abs(w_uniform_x) > 1e-12 or abs(w_uniform_y) > 1e-12:
            uniform_load = UniformLoad(
                wx=w_uniform_x,
                wy=w_uniform_y,
                start_distance=start,
                end_distance=end,
                load_case=self.load_case,
                direction=self.direction,
                label=f"{self.label}_uniform"
            )
            forces += uniform_load.get_equivalent_nodal_forces(element)
        
        # Triangular component
        if abs(w_triangular_x) > 1e-12 or abs(w_triangular_y) > 1e-12:
            # Triangular load equivalent nodal forces
            # For triangular load increasing from 0 to w over length L:
            # R1 = w*L/3, R2 = 2*w*L/3
            # M1 = -w*L²/20, M2 = w*L²/30
            
            Px_tri = w_triangular_x * load_length
            Py_tri = w_triangular_y * load_length
            
            # Reactions (triangular load centroid at 2/3 from start)
            forces[0] += -Px_tri / 3
            forces[3] += -2 * Px_tri / 3
            
            forces[1] += -Py_tri / 3
            forces[4] += -2 * Py_tri / 3
            
            # Moments for triangular load
            if abs(w_triangular_y) > 1e-12:
                L_tri_sq = load_length * load_length
                forces[2] += -w_triangular_y * L_tri_sq / 20
                forces[5] += w_triangular_y * L_tri_sq / 30
        
        return self.transform_to_global(forces, element)
    
    def __str__(self) -> str:
        return (f"TrapezoidalLoad('{self.label}', "
                f"w1=({self.wx1}, {self.wy1}), w2=({self.wx2}, {self.wy2}), "
                f"span={self.start_distance}-{self.end_distance})")
    
    def to_uniform_load(self) -> UniformLoad:
        """Convert to equivalent uniform load (average intensity)."""
        avg_wx = (self.wx1 + self.wx2) / 2
        avg_wy = (self.wy1 + self.wy2) / 2
        
        return UniformLoad(
            wx=avg_wx,
            wy=avg_wy,
            start_distance=self.start_distance,
            end_distance=self.end_distance,
            load_case=self.load_case,
            direction=self.direction,
            label=f"{self.label}_equivalent"
        )