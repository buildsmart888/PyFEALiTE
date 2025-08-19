"""Frame element implementation for 2D structural analysis."""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from enum import Enum
import numpy as np

from .node import Node2D

if TYPE_CHECKING:
    from ..sections.base import CrossSection
    from .structure import Structure


class EndRelease(Enum):
    """Element end release conditions."""
    NO_RELEASE = "no_release"
    START_RELEASE = "start_release"
    END_RELEASE = "end_release"
    FULL_RELEASE = "full_release"


@dataclass
class FrameElement2D:
    """
    2D Frame element with 3 DOF per node (UX, UY, RZ).
    
    Attributes:
        start_node: Starting node
        end_node: Ending node
        cross_section: Cross-section properties
        label: Element identifier
        end_release: End release conditions
        parent_structure: Reference to parent structure
    """
    start_node: Node2D
    end_node: Node2D
    cross_section: 'CrossSection'
    label: str
    end_release: EndRelease = EndRelease.NO_RELEASE
    parent_structure: Optional['Structure'] = None
    
    # Private attributes for caching matrices
    _local_stiffness_matrix: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _transformation_matrix: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _global_stiffness_matrix: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    
    def __post_init__(self) -> None:
        """Initialize element after creation."""
        if self.length <= 0:
            raise ValueError("Element length must be positive")
    
    @property
    def length(self) -> float:
        """Element length."""
        return self.start_node.distance_to(self.end_node)
    
    @property
    def nodes(self) -> List[Node2D]:
        """List of element nodes."""
        return [self.start_node, self.end_node]
    
    @property
    def angle(self) -> float:
        """Element angle in radians from global X-axis."""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return np.arctan2(dy, dx)
    
    @property
    def direction_cosines(self) -> tuple[float, float]:
        """Direction cosines (cos θ, sin θ)."""
        L = self.length
        cos_theta = (self.end_node.x - self.start_node.x) / L
        sin_theta = (self.end_node.y - self.start_node.y) / L
        return cos_theta, sin_theta
    
    @property
    def transformation_matrix(self) -> np.ndarray:
        """6x6 transformation matrix from local to global coordinates."""
        if self._transformation_matrix is None:
            self._transformation_matrix = self._compute_transformation_matrix()
        return self._transformation_matrix
    
    def _compute_transformation_matrix(self) -> np.ndarray:
        """Compute the coordinate transformation matrix."""
        c, s = self.direction_cosines
        
        # 3x3 transformation matrix for each node
        T3 = np.array([
            [c, s, 0],
            [-s, c, 0], 
            [0, 0, 1]
        ])
        
        # 6x6 transformation matrix
        T = np.zeros((6, 6))
        T[0:3, 0:3] = T3
        T[3:6, 3:6] = T3
        
        return T
    
    @property
    def local_stiffness_matrix(self) -> np.ndarray:
        """6x6 local stiffness matrix."""
        if self._local_stiffness_matrix is None:
            self._local_stiffness_matrix = self._compute_local_stiffness_matrix()
        return self._local_stiffness_matrix
    
    def _compute_local_stiffness_matrix(self) -> np.ndarray:
        """Compute local stiffness matrix based on end release conditions."""
        if self.end_release == EndRelease.NO_RELEASE:
            return self._local_stiffness_no_release()
        elif self.end_release == EndRelease.START_RELEASE:
            return self._local_stiffness_start_release()
        elif self.end_release == EndRelease.END_RELEASE:
            return self._local_stiffness_end_release()
        elif self.end_release == EndRelease.FULL_RELEASE:
            return self._local_stiffness_full_release()
        else:
            raise ValueError(f"Unknown end release: {self.end_release}")
    
    def _local_stiffness_no_release(self) -> np.ndarray:
        """Local stiffness matrix with no releases."""
        L = self.length
        E = self.cross_section.material.E
        A = self.cross_section.A
        I = self.cross_section.Iz
        
        EA_L = E * A / L
        EI_L = E * I / L
        EI_L2 = E * I / (L * L)
        EI_L3 = E * I / (L * L * L)
        
        k = np.zeros((6, 6))
        
        # Axial terms
        k[0, 0] = EA_L
        k[0, 3] = -EA_L
        k[3, 0] = -EA_L
        k[3, 3] = EA_L
        
        # Bending terms
        k[1, 1] = 12 * EI_L3
        k[1, 2] = 6 * EI_L2
        k[1, 4] = -12 * EI_L3
        k[1, 5] = 6 * EI_L2
        
        k[2, 1] = 6 * EI_L2
        k[2, 2] = 4 * EI_L
        k[2, 4] = -6 * EI_L2
        k[2, 5] = 2 * EI_L
        
        k[4, 1] = -12 * EI_L3
        k[4, 2] = -6 * EI_L2
        k[4, 4] = 12 * EI_L3
        k[4, 5] = -6 * EI_L2
        
        k[5, 1] = 6 * EI_L2
        k[5, 2] = 2 * EI_L
        k[5, 4] = -6 * EI_L2
        k[5, 5] = 4 * EI_L
        
        return k
    
    def _local_stiffness_start_release(self) -> np.ndarray:
        """Local stiffness matrix with moment release at start."""
        L = self.length
        E = self.cross_section.material.E
        A = self.cross_section.A
        I = self.cross_section.Iz
        
        EA_L = E * A / L
        EI_L = E * I / L
        EI_L2 = E * I / (L * L)
        EI_L3 = E * I / (L * L * L)
        
        k = np.zeros((6, 6))
        
        # Axial terms (unchanged)
        k[0, 0] = EA_L
        k[0, 3] = -EA_L
        k[3, 0] = -EA_L
        k[3, 3] = EA_L
        
        # Modified bending terms for start release
        k[1, 1] = 3 * EI_L3
        k[1, 4] = -3 * EI_L3
        k[1, 5] = 3 * EI_L2
        
        k[4, 1] = -3 * EI_L3
        k[4, 4] = 3 * EI_L3
        k[4, 5] = -3 * EI_L2
        
        k[5, 1] = 3 * EI_L2
        k[5, 4] = -3 * EI_L2
        k[5, 5] = 3 * EI_L
        
        return k
    
    def _local_stiffness_end_release(self) -> np.ndarray:
        """Local stiffness matrix with moment release at end."""
        L = self.length
        E = self.cross_section.material.E
        A = self.cross_section.A
        I = self.cross_section.Iz
        
        EA_L = E * A / L
        EI_L = E * I / L
        EI_L2 = E * I / (L * L)
        EI_L3 = E * I / (L * L * L)
        
        k = np.zeros((6, 6))
        
        # Axial terms (unchanged)
        k[0, 0] = EA_L
        k[0, 3] = -EA_L
        k[3, 0] = -EA_L
        k[3, 3] = EA_L
        
        # Modified bending terms for end release
        k[1, 1] = 3 * EI_L3
        k[1, 2] = 3 * EI_L2
        k[1, 4] = -3 * EI_L3
        
        k[2, 1] = 3 * EI_L2
        k[2, 2] = 3 * EI_L
        k[2, 4] = -3 * EI_L2
        
        k[4, 1] = -3 * EI_L3
        k[4, 2] = -3 * EI_L2
        k[4, 4] = 3 * EI_L3
        
        return k
    
    def _local_stiffness_full_release(self) -> np.ndarray:
        """Local stiffness matrix with moment releases at both ends (truss)."""
        L = self.length
        E = self.cross_section.material.E
        A = self.cross_section.A
        
        EA_L = E * A / L
        
        k = np.zeros((6, 6))
        
        # Only axial terms for truss element
        k[0, 0] = EA_L
        k[0, 3] = -EA_L
        k[3, 0] = -EA_L
        k[3, 3] = EA_L
        
        return k
    
    @property
    def global_stiffness_matrix(self) -> np.ndarray:
        """6x6 global stiffness matrix."""
        if self._global_stiffness_matrix is None:
            T = self.transformation_matrix
            K_local = self.local_stiffness_matrix
            self._global_stiffness_matrix = T.T @ K_local @ T
        return self._global_stiffness_matrix
    
    def get_dof_numbers(self) -> List[int]:
        """Get global DOF numbers for this element."""
        dofs = []
        dofs.extend(self.start_node.coord_numbers)
        dofs.extend(self.end_node.coord_numbers)
        return dofs
    
    def clear_cached_matrices(self) -> None:
        """Clear cached matrices (call when properties change)."""
        self._local_stiffness_matrix = None
        self._transformation_matrix = None
        self._global_stiffness_matrix = None
    
    def __str__(self) -> str:
        """String representation."""
        return (f"FrameElement2D('{self.label}', {self.start_node.label}->{self.end_node.label}, "
                f"L={self.length:.2f}, release={self.end_release.value})")
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"FrameElement2D(start_node={self.start_node.label}, "
                f"end_node={self.end_node.label}, label='{self.label}', "
                f"length={self.length:.3f}, end_release={self.end_release})")