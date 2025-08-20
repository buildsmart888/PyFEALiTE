"""Base classes for PyFEALiTE core elements."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .node import Node2D
    from ..materials.base import IMaterial
    from ..sections.base import CrossSection


class ElementBase(ABC):
    """
    Abstract base class for all structural elements.
    
    This defines the common interface that all elements (frame, spring, truss, etc.)
    must implement.
    """
    
    def __init__(self, 
                 start_node: 'Node2D',
                 end_node: 'Node2D',
                 label: str = ""):
        """
        Initialize base element.
        
        Args:
            start_node: Starting node of the element
            end_node: Ending node of the element
            label: Element identifier/name
        """
        self.start_node = start_node
        self.end_node = end_node
        self.label = label
        self._id: Optional[int] = None
        
    @property
    def id(self) -> Optional[int]:
        """Get element ID."""
        return self._id
    
    @id.setter
    def id(self, value: int) -> None:
        """Set element ID."""
        self._id = value
    
    @property
    def nodes(self) -> List['Node2D']:
        """Get all nodes of the element."""
        return [self.start_node, self.end_node]
    
    @abstractmethod
    def length(self) -> float:
        """
        Calculate element length.
        
        Returns:
            Element length
        """
        pass
    
    @abstractmethod
    def local_stiffness_matrix(self) -> np.ndarray:
        """
        Get local stiffness matrix.
        
        Returns:
            Local stiffness matrix
        """
        pass
    
    @abstractmethod
    def global_stiffness_matrix(self) -> np.ndarray:
        """
        Get global stiffness matrix.
        
        Returns:
            Global stiffness matrix in global coordinates
        """
        pass
    
    @abstractmethod
    def transformation_matrix(self) -> np.ndarray:
        """
        Get transformation matrix from local to global coordinates.
        
        Returns:
            Transformation matrix
        """
        pass
    
    def angle(self) -> float:
        """
        Calculate element angle with respect to global X-axis.
        
        Returns:
            Angle in radians
        """
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return np.arctan2(dy, dx)
    
    def direction_cosines(self) -> tuple[float, float]:
        """
        Calculate direction cosines.
        
        Returns:
            (cos_x, cos_y) direction cosines
        """
        length = self.length()
        if length == 0:
            return 0.0, 0.0
        
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        
        return dx / length, dy / length
    
    def __repr__(self) -> str:
        """String representation of element."""
        return f"{self.__class__.__name__}(label='{self.label}', start={self.start_node.label}, end={self.end_node.label})"


class StructuralElement(ElementBase):
    """
    Base class for structural elements (frame, truss) that have material and section properties.
    """
    
    def __init__(self,
                 start_node: 'Node2D',
                 end_node: 'Node2D',
                 cross_section: 'CrossSection',
                 material: Optional['IMaterial'] = None,
                 label: str = ""):
        """
        Initialize structural element.
        
        Args:
            start_node: Starting node
            end_node: Ending node
            cross_section: Cross section properties
            material: Material properties (optional)
            label: Element identifier
        """
        super().__init__(start_node, end_node, label)
        self.cross_section = cross_section
        self.material = material
    
    def length(self) -> float:
        """Calculate element length."""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return np.sqrt(dx**2 + dy**2)


class ConnectivityElement(ElementBase):
    """
    Base class for connectivity elements (springs, links) that connect nodes.
    """
    
    def __init__(self,
                 start_node: 'Node2D',
                 end_node: 'Node2D',
                 properties: Any,
                 label: str = ""):
        """
        Initialize connectivity element.
        
        Args:
            start_node: Starting node
            end_node: Ending node
            properties: Element properties
            label: Element identifier
        """
        super().__init__(start_node, end_node, label)
        self.properties = properties
    
    def length(self) -> float:
        """Calculate element length."""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return np.sqrt(dx**2 + dy**2)
