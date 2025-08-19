"""
PyFEALiTE - Python Finite Element Analysis Library

A Python port of FEALiTE2D for 2D structural analysis including:
- Frame, beam, and truss elements
- Various load types and combinations
- Support for different boundary conditions
- Visualization and export capabilities
"""

__version__ = "0.1.0"
__author__ = "PyFEALiTE Team"

from .core.node import Node2D
from .core.element import FrameElement2D
from .core.structure import Structure
from .materials.isotropic import IsotropicMaterial
from .sections.rectangular import RectangularSection
from .sections.circular import CircularSection
from .loads.base import LoadCase, LoadType

# Optional imports - import submodules for organized access
# Users can import like: from pyfealite.visualization import plot_structure
# or: from pyfealite.utils.export import export_to_json

__all__ = [
    "Node2D",
    "FrameElement2D", 
    "Structure",
    "IsotropicMaterial",
    "RectangularSection",
    "CircularSection",
    "LoadCase",
    "LoadType",
]