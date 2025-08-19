"""Base material class and related definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MaterialType(Enum):
    """Material type enumeration."""
    STEEL = "steel"
    CONCRETE = "concrete"
    ALUMINUM = "aluminum"
    WOOD = "wood"
    COMPOSITE = "composite"


@dataclass
class Material(ABC):
    """
    Abstract base class for material properties.
    
    Attributes:
        E: Young's modulus (elastic modulus)
        label: Material identifier/name
        material_type: Type of material
    """
    E: float
    label: str = ""
    material_type: MaterialType = MaterialType.STEEL
    
    def __post_init__(self) -> None:
        """Validate material properties."""
        if self.E <= 0:
            raise ValueError("Young's modulus must be positive")
    
    @property
    @abstractmethod
    def G(self) -> float:
        """Shear modulus."""
        pass
    
    @property
    @abstractmethod 
    def density(self) -> float:
        """Material density."""
        pass
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}('{self.label}', E={self.E})"