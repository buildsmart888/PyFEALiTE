"""Rectangular cross-section implementation."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from .base import CrossSection

if TYPE_CHECKING:
    from ..materials.base import Material


class RectangularSection(CrossSection):
    """
    Rectangular cross-section.
    
    Attributes:
        material: Material properties
        width: Width of the rectangle (b)
        height: Height of the rectangle (h)
        label: Section identifier
    """
    
    def __init__(self, material: 'Material', width: float, height: float, label: str = ""):
        super().__init__(material, label)
        self.width = width
        self.height = height
        self._validate()
    
    def _validate(self) -> None:
        """Validate rectangular section properties."""
        if self.width <= 0:
            raise ValueError("Width must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")
    
    @property
    def A(self) -> float:
        """Cross-sectional area: b * h"""
        return self.width * self.height
    
    @property
    def Iz(self) -> float:
        """Moment of inertia about Z-axis: b * h³ / 12"""
        return self.width * self.height**3 / 12
    
    @property
    def Iy(self) -> float:
        """Moment of inertia about Y-axis: h * b³ / 12"""
        return self.height * self.width**3 / 12
    
    @property
    def Az(self) -> float:
        """Shear area in Z direction: 5/6 * A"""
        return 5/6 * self.A
    
    @property
    def Ay(self) -> float:
        """Shear area in Y direction: 5/6 * A"""
        return 5/6 * self.A
    
    @property
    def J(self) -> float:
        """Torsional constant for rectangle."""
        # Simplified torsional constant for rectangle
        a = max(self.width, self.height)
        b = min(self.width, self.height)
        
        if a / b >= 10:
            # For very thin rectangles
            return a * b**3 / 3
        else:
            # General formula approximation
            alpha = 0.14 * (1 - 0.63 * b/a + 0.052 * (b/a)**5)
            return alpha * a * b**3
    
    @property
    def section_modulus_z(self) -> float:
        """Section modulus about Z-axis: Iz / (h/2)"""
        return self.Iz / (self.height / 2)
    
    @property
    def section_modulus_y(self) -> float:
        """Section modulus about Y-axis: Iy / (b/2)"""
        return self.Iy / (self.width / 2)
    
    def __str__(self) -> str:
        """String representation."""
        return (f"RectangularSection('{self.label}', "
                f"{self.width}x{self.height}, A={self.A:.2e})")