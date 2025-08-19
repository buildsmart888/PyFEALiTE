"""Base classes for loads and load cases."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ..core.element import FrameElement2D


class LoadDirection(Enum):
    """Load direction enumeration."""
    GLOBAL = "global"
    LOCAL = "local"


class LoadType(Enum):
    """Load type enumeration for load cases."""
    DEAD = "dead"
    LIVE = "live"
    WIND = "wind"
    SEISMIC = "seismic"
    SNOW = "snow"
    TEMPERATURE = "temperature"
    OTHER = "other"


@dataclass
class LoadCase:
    """
    Represents a load case containing multiple loads.
    
    Attributes:
        name: Load case identifier
        load_type: Type of loading
        factor: Load factor for combinations
        description: Optional description
    """
    name: str
    load_type: LoadType = LoadType.OTHER
    factor: float = 1.0
    description: str = ""
    
    def __str__(self) -> str:
        return f"LoadCase('{self.name}', {self.load_type.value})"
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LoadCase):
            return False
        return self.name == other.name


class LoadCombination:
    """
    Represents a combination of load cases with factors.
    
    Example:
        combo = LoadCombination("Ultimate")
        combo.add(dead_case, 1.2)
        combo.add(live_case, 1.6)
    """
    
    def __init__(self, name: str):
        self.name = name
        self._combinations: Dict[LoadCase, float] = {}
    
    def add(self, load_case: LoadCase, factor: float) -> None:
        """Add a load case with factor to the combination."""
        self._combinations[load_case] = factor
    
    def remove(self, load_case: LoadCase) -> None:
        """Remove a load case from the combination."""
        self._combinations.pop(load_case, None)
    
    def get_factor(self, load_case: LoadCase) -> float:
        """Get factor for a specific load case."""
        return self._combinations.get(load_case, 0.0)
    
    @property
    def load_cases(self) -> Dict[LoadCase, float]:
        """Dictionary of load cases and their factors."""
        return self._combinations.copy()
    
    def __iter__(self):
        """Iterate over load case-factor pairs."""
        return iter(self._combinations.items())
    
    def __str__(self) -> str:
        cases = [f"{lc.name}x{factor}" for lc, factor in self._combinations.items()]
        return f"LoadCombination('{self.name}': {', '.join(cases)})"


@dataclass
class Load(ABC):
    """
    Abstract base class for all loads.
    
    Attributes:
        load_case: Associated load case
        direction: Load coordinate system (global or local)
        label: Load identifier
    """
    load_case: LoadCase
    direction: LoadDirection = LoadDirection.GLOBAL
    label: str = ""
    
    @abstractmethod
    def get_equivalent_nodal_forces(self, element: 'FrameElement2D') -> np.ndarray:
        """
        Get equivalent nodal forces for this load on an element.
        
        Args:
            element: The element this load acts on
            
        Returns:
            6-element array of forces [Fx1, Fy1, Mz1, Fx2, Fy2, Mz2]
        """
        pass
    
    def transform_to_global(self, forces_local: np.ndarray, element: 'FrameElement2D') -> np.ndarray:
        """Transform forces from local to global coordinates."""
        if self.direction == LoadDirection.GLOBAL:
            return forces_local
        else:
            # Transform from local to global using element transformation matrix
            T = element.transformation_matrix
            return T.T @ forces_local
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}('{self.label}', {self.direction.value})"