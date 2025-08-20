"""Spring element implementation for PyFEALiTE."""

from typing import Optional, List, Dict, Set
import numpy as np
from dataclasses import dataclass

from .base import ElementBase
from ..core.node import Node2D
from ..loads.base import LoadCase, ILoad
from ..materials.base import IMaterial


@dataclass
class SpringProperties:
    """Spring properties for SpringElement2D."""
    K: float = 0.0  # Longitudinal spring stiffness [force/length]
    Kr: float = 0.0  # Rotational spring stiffness [force.length/radians]
    
    def __post_init__(self):
        """Validate spring properties."""
        if self.K < 0:
            raise ValueError("Longitudinal stiffness K must be non-negative")
        if self.Kr < 0:
            raise ValueError("Rotational stiffness Kr must be non-negative")


class SpringElement2D(ElementBase):
    """
    Represents a spring element/fictitious bar in 2D space.
    
    Spring elements have spring stiffness and 2 DOF at each node.
    Springs may be longitudinal or rotational.
    
    Attributes:
        start_node: Start node of the spring
        end_node: End node of the spring  
        properties: Spring properties (K, Kr)
        label: Element label/name
    """
    
    def __init__(self, start_node: Node2D, end_node: Node2D, 
                 properties: SpringProperties, label: str = ""):
        """
        Initialize SpringElement2D.
        
        Args:
            start_node: Start node
            end_node: End node
            properties: Spring properties
            label: Element label
        """
        super().__init__(start_node, end_node, label)
        self.properties = properties
        self.loads: List[ILoad] = []
        self.global_end_forces: Dict[LoadCase, np.ndarray] = {}
        self.additional_mesh_points: Set[float] = set()
        
        # Initialize matrices
        self._local_stiffness_matrix: Optional[np.ndarray] = None
        self._global_stiffness_matrix: Optional[np.ndarray] = None
        self._transformation_matrix: Optional[np.ndarray] = None
        
    @property
    def length(self) -> float:
        """Calculate element length."""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return np.sqrt(dx**2 + dy**2)
    
    @property
    def angle(self) -> float:
        """Calculate element angle from horizontal (radians)."""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return np.arctan2(dy, dx)
    
    def initialize(self) -> None:
        """Initialize element matrices."""
        self._calculate_transformation_matrix()
        self._calculate_local_stiffness_matrix()
        self._calculate_global_stiffness_matrix()
    
    def _calculate_transformation_matrix(self) -> None:
        """Calculate transformation matrix from local to global coordinates."""
        cos_theta = np.cos(self.angle)
        sin_theta = np.sin(self.angle)
        
        # 6x6 transformation matrix for 2D spring (3 DOF per node)
        T = np.zeros((6, 6))
        
        # First node (DOF 0,1,2)
        T[0, 0] = cos_theta    # UX local to UX global
        T[0, 1] = sin_theta    # UX local to UY global
        T[1, 0] = -sin_theta   # UY local to UX global  
        T[1, 1] = cos_theta    # UY local to UY global
        T[2, 2] = 1.0          # RZ local to RZ global
        
        # Second node (DOF 3,4,5)
        T[3, 3] = cos_theta    # UX local to UX global
        T[3, 4] = sin_theta    # UX local to UY global
        T[4, 3] = -sin_theta   # UY local to UX global
        T[4, 4] = cos_theta    # UY local to UY global
        T[5, 5] = 1.0          # RZ local to RZ global
        
        self._transformation_matrix = T
    
    def _calculate_local_stiffness_matrix(self) -> None:
        """Calculate local stiffness matrix for spring element."""
        K = self.properties.K    # Longitudinal stiffness
        Kr = self.properties.Kr  # Rotational stiffness
        
        # 6x6 local stiffness matrix (3 DOF per node)
        k_local = np.zeros((6, 6))
        
        # Longitudinal spring stiffness (DOF 0 and 3)
        if K > 0:
            k_local[0, 0] = K     # Start node UX
            k_local[3, 3] = K     # End node UX
            k_local[0, 3] = -K    # Coupling
            k_local[3, 0] = -K    # Coupling
        
        # Rotational spring stiffness (DOF 2 and 5)
        if Kr > 0:
            k_local[2, 2] = Kr    # Start node RZ
            k_local[5, 5] = Kr    # End node RZ
            k_local[2, 5] = -Kr   # Coupling
            k_local[5, 2] = -Kr   # Coupling
        
        # No transverse stiffness for springs
        # (DOF 1 and 4 remain zero)
        
        self._local_stiffness_matrix = k_local
    
    def _calculate_global_stiffness_matrix(self) -> None:
        """Calculate global stiffness matrix."""
        if self._transformation_matrix is None or self._local_stiffness_matrix is None:
            raise RuntimeError("Must initialize transformation and local stiffness matrices first")
        
        T = self._transformation_matrix
        k_local = self._local_stiffness_matrix
        
        # K_global = T^T * K_local * T
        self._global_stiffness_matrix = T.T @ k_local @ T
    
    @property
    def local_stiffness_matrix(self) -> np.ndarray:
        """Get local stiffness matrix."""
        if self._local_stiffness_matrix is None:
            self.initialize()
        return self._local_stiffness_matrix.copy()
    
    @property
    def global_stiffness_matrix(self) -> np.ndarray:
        """Get global stiffness matrix."""
        if self._global_stiffness_matrix is None:
            self.initialize()
        return self._global_stiffness_matrix.copy()
    
    @property
    def transformation_matrix(self) -> np.ndarray:
        """Get transformation matrix."""
        if self._transformation_matrix is None:
            self.initialize()
        return self._transformation_matrix.copy()
    
    def get_element_forces(self, displacements: np.ndarray) -> np.ndarray:
        """
        Calculate element internal forces from global displacements.
        
        Args:
            displacements: Global nodal displacements [6x1]
            
        Returns:
            Local element forces [6x1]
        """
        if self._transformation_matrix is None or self._local_stiffness_matrix is None:
            self.initialize()
        
        # Transform global displacements to local
        local_displacements = self._transformation_matrix @ displacements
        
        # Calculate local forces
        local_forces = self._local_stiffness_matrix @ local_displacements
        
        return local_forces
    
    def get_axial_force(self, displacements: np.ndarray) -> float:
        """Get axial force in spring."""
        forces = self.get_element_forces(displacements)
        return forces[0]  # Axial force at start node
    
    def get_moment(self, displacements: np.ndarray) -> tuple[float, float]:
        """Get moments at start and end nodes."""
        forces = self.get_element_forces(displacements)
        return forces[2], forces[5]  # Moments at start and end nodes
    
    def get_spring_displacement(self, displacements: np.ndarray) -> float:
        """Get relative displacement across spring."""
        local_displacements = self._transformation_matrix @ displacements
        return local_displacements[3] - local_displacements[0]  # End - Start
    
    def __str__(self) -> str:
        """String representation."""
        return f"SpringElement2D('{self.label}', K={self.properties.K:.2e}, Kr={self.properties.Kr:.2e})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"SpringElement2D(start_node={self.start_node.label}, "
                f"end_node={self.end_node.label}, "
                f"K={self.properties.K:.2e}, Kr={self.properties.Kr:.2e}, "
                f"label='{self.label}')")
