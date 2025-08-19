"""Material property classes."""

from .base import Material, MaterialType
from .isotropic import IsotropicMaterial

__all__ = [
    "Material",
    "MaterialType", 
    "IsotropicMaterial",
]