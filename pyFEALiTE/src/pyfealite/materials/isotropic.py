"""Isotropic material implementation."""

from dataclasses import dataclass
from .base import Material, MaterialType


@dataclass
class IsotropicMaterial(Material):
    """
    Isotropic material with uniform properties in all directions.
    
    Attributes:
        E: Young's modulus
        nu: Poisson's ratio
        density_value: Material density
        alpha: Thermal expansion coefficient
        gamma: Unit weight
        label: Material name
        material_type: Type of material
    """
    nu: float = 0.2  # Poisson's ratio
    density_value: float = 0.0  # Material density
    alpha: float = 0.0  # Thermal expansion coefficient
    gamma: float = 0.0  # Unit weight
    
    def __post_init__(self) -> None:
        """Validate isotropic material properties."""
        super().__post_init__()
        
        if not (-1 < self.nu < 0.5):
            raise ValueError("Poisson's ratio must be between -1 and 0.5")
        
        if self.density_value < 0:
            raise ValueError("Density must be non-negative")
            
        if self.gamma < 0:
            raise ValueError("Unit weight must be non-negative")
    
    @property
    def G(self) -> float:
        """Shear modulus calculated from E and nu."""
        return self.E / (2 * (1 + self.nu))
    
    @property
    def density(self) -> float:
        """Material density."""
        return self.density_value
    
    @property
    def bulk_modulus(self) -> float:
        """Bulk modulus."""
        return self.E / (3 * (1 - 2 * self.nu))
    
    @classmethod
    def steel(cls, label: str = "Steel") -> 'IsotropicMaterial':
        """Create typical steel material."""
        return cls(
            E=200e9,  # Pa
            nu=0.3,
            density_value=7850,  # kg/m³
            alpha=12e-6,  # /°C
            gamma=78.5e3,  # N/m³
            label=label,
            material_type=MaterialType.STEEL
        )
    
    @classmethod
    def concrete(cls, label: str = "Concrete") -> 'IsotropicMaterial':
        """Create typical concrete material."""
        return cls(
            E=30e9,  # Pa
            nu=0.2,
            density_value=2400,  # kg/m³
            alpha=10e-6,  # /°C
            gamma=24e3,  # N/m³
            label=label,
            material_type=MaterialType.CONCRETE
        )
    
    @classmethod
    def aluminum(cls, label: str = "Aluminum") -> 'IsotropicMaterial':
        """Create typical aluminum material."""
        return cls(
            E=70e9,  # Pa
            nu=0.33,
            density_value=2700,  # kg/m³
            alpha=23e-6,  # /°C
            gamma=26.5e3,  # N/m³
            label=label,
            material_type=MaterialType.ALUMINUM
        )