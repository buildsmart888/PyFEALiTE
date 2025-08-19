"""Node2D class for 2D structural analysis."""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from enum import IntEnum
import numpy as np

if TYPE_CHECKING:
    from .structure import Structure


class NodalDegreeOfFreedom(IntEnum):
    """Enumeration for nodal degrees of freedom."""
    UX = 0  # Translation in X direction
    UY = 1  # Translation in Y direction  
    RZ = 2  # Rotation about Z axis


@dataclass
class Node2D:
    """
    Represents a 2D structural node with coordinates and boundary conditions.
    
    Attributes:
        x: X coordinate
        y: Y coordinate
        label: Node identifier/name
        restraints: List of boolean restraints for [UX, UY, RZ]
        coord_numbers: Global coordinate numbers for DOF
        parent_structure: Reference to parent structure
    """
    x: float
    y: float
    label: str
    restraints: List[bool] = field(default_factory=lambda: [False, False, False])
    coord_numbers: List[int] = field(default_factory=list)
    parent_structure: Optional['Structure'] = None
    
    def __post_init__(self) -> None:
        """Initialize coordinate numbers list if empty."""
        if not self.coord_numbers:
            self.coord_numbers = [0, 0, 0]
    
    def is_restrained(self, dof: NodalDegreeOfFreedom) -> bool:
        """
        Check if a degree of freedom is restrained.
        
        Args:
            dof: Degree of freedom to check
            
        Returns:
            True if the DOF is restrained
        """
        return self.restraints[dof]
    
    def restrain(self, *dofs: NodalDegreeOfFreedom) -> None:
        """
        Restrain specified degrees of freedom.
        
        Args:
            *dofs: Variable number of DOFs to restrain
        """
        for dof in dofs:
            self.restraints[dof] = True
    
    def release(self, *dofs: NodalDegreeOfFreedom) -> None:
        """
        Release specified degrees of freedom.
        
        Args:
            *dofs: Variable number of DOFs to release
        """
        for dof in dofs:
            self.restraints[dof] = False
    
    def distance_to(self, other: 'Node2D') -> float:
        """
        Calculate distance to another node.
        
        Args:
            other: Another node
            
        Returns:
            Euclidean distance between nodes
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    @property
    def is_free(self) -> bool:
        """Check if node has any free degrees of freedom."""
        return not all(self.restraints)
    
    @property
    def dof_count(self) -> int:
        """Number of free degrees of freedom."""
        return sum(not restrained for restrained in self.restraints)
    
    @property  
    def coordinates(self) -> np.ndarray:
        """Node coordinates as numpy array."""
        return np.array([self.x, self.y])
    
    def __str__(self) -> str:
        """String representation of the node."""
        restraint_str = "".join("R" if r else "F" for r in self.restraints)
        return f"Node2D('{self.label}', x={self.x}, y={self.y}, restraints={restraint_str})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Node2D(x={self.x}, y={self.y}, label='{self.label}', "
                f"restraints={self.restraints})")
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another node."""
        if not isinstance(other, Node2D):
            return False
        return (self.x == other.x and 
                self.y == other.y and 
                self.label == other.label)
    
    def __hash__(self) -> int:
        """Hash function for using nodes in sets/dictionaries."""
        return hash((self.x, self.y, self.label))