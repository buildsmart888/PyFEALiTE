"""Base cross-section class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..materials.base import Material


@dataclass
class CrossSection(ABC):
    """
    Abstract base class for cross-section properties.
    
    All cross-sections must define the geometric properties
    needed for structural analysis.
    """
    material: 'Material'
    label: str = ""
    
    @property
    @abstractmethod
    def A(self) -> float:
        """Cross-sectional area."""
        pass
    
    @property 
    @abstractmethod
    def Iz(self) -> float:
        """Moment of inertia about major axis."""
        pass
    
    @property
    @abstractmethod
    def Iy(self) -> float:
        """Moment of inertia about minor axis."""
        pass
    
    @property
    def Az(self) -> float:
        """Shear area in Z direction (typically 5/6 * A for rectangles)."""
        return self.A  # Default implementation
    
    @property
    def Ay(self) -> float:
        """Shear area in Y direction."""
        return self.A  # Default implementation
    
    @property
    def J(self) -> float:
        """Torsional constant."""
        return self.Iz + self.Iy  # Simplified for circular sections
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}('{self.label}', A={self.A:.2e})"