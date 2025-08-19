"""Circular cross-section implementation."""

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .base import CrossSection

if TYPE_CHECKING:
    from ..materials.base import Material


class CircularSection(CrossSection):
    """
    Circular cross-section.
    
    Attributes:
        material: Material properties  
        diameter: Diameter of the circle
        label: Section identifier
    """
    
    def __init__(self, material: 'Material', diameter: float, label: str = ""):
        super().__init__(material, label)
        self.diameter = diameter
        self._validate()
    
    def _validate(self) -> None:
        """Validate circular section properties."""
        if self.diameter <= 0:
            raise ValueError("Diameter must be positive")
    
    @property
    def radius(self) -> float:
        """Radius of the circle."""
        return self.diameter / 2
    
    @property
    def A(self) -> float:
        """Cross-sectional area: π * d² / 4"""
        return math.pi * self.diameter**2 / 4
    
    @property
    def Iz(self) -> float:
        """Moment of inertia about Z-axis: π * d⁴ / 64"""
        return math.pi * self.diameter**4 / 64
    
    @property
    def Iy(self) -> float:
        """Moment of inertia about Y-axis: π * d⁴ / 64"""
        return math.pi * self.diameter**4 / 64
    
    @property
    def Az(self) -> float:
        """Shear area: 9/10 * A for circular sections"""
        return 9/10 * self.A
    
    @property
    def Ay(self) -> float:
        """Shear area: 9/10 * A for circular sections"""
        return 9/10 * self.A
    
    @property
    def J(self) -> float:
        """Polar moment of inertia: π * d⁴ / 32"""
        return math.pi * self.diameter**4 / 32
    
    @property
    def section_modulus(self) -> float:
        """Section modulus: π * d³ / 32"""
        return math.pi * self.diameter**3 / 32
    
    def __str__(self) -> str:
        """String representation."""
        return (f"CircularSection('{self.label}', "
                f"d={self.diameter}, A={self.A:.2e})")


class HollowCircularSection(CrossSection):
    """
    Hollow circular cross-section (tube).
    
    Attributes:
        material: Material properties
        outer_diameter: Outer diameter
        inner_diameter: Inner diameter
        label: Section identifier
    """
    
    def __init__(self, material: 'Material', outer_diameter: float, inner_diameter: float, label: str = ""):
        super().__init__(material, label)
        self.outer_diameter = outer_diameter
        self.inner_diameter = inner_diameter
        self._validate()
    
    def _validate(self) -> None:
        """Validate hollow circular section properties."""
        if self.outer_diameter <= 0:
            raise ValueError("Outer diameter must be positive")
        if self.inner_diameter < 0:
            raise ValueError("Inner diameter must be non-negative")
        if self.inner_diameter >= self.outer_diameter:
            raise ValueError("Inner diameter must be less than outer diameter")
    
    @property
    def A(self) -> float:
        """Cross-sectional area: π * (Do² - Di²) / 4"""
        return math.pi * (self.outer_diameter**2 - self.inner_diameter**2) / 4
    
    @property
    def Iz(self) -> float:
        """Moment of inertia: π * (Do⁴ - Di⁴) / 64"""
        return math.pi * (self.outer_diameter**4 - self.inner_diameter**4) / 64
    
    @property
    def Iy(self) -> float:
        """Moment of inertia: π * (Do⁴ - Di⁴) / 64"""
        return math.pi * (self.outer_diameter**4 - self.inner_diameter**4) / 64
    
    @property
    def J(self) -> float:
        """Polar moment of inertia: π * (Do⁴ - Di⁴) / 32"""
        return math.pi * (self.outer_diameter**4 - self.inner_diameter**4) / 32
    
    @property
    def section_modulus(self) -> float:
        """Section modulus."""
        return self.Iz / (self.outer_diameter / 2)
    
    def __str__(self) -> str:
        """String representation."""
        return (f"HollowCircularSection('{self.label}', "
                f"Do={self.outer_diameter}, Di={self.inner_diameter}, A={self.A:.2e})")