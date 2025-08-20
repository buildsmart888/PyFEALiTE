"""
PyFEALiTE - Python Finite Element Analysis Library

A comprehensive Python port of FEALiTE2D for 2D structural analysis including:
- Frame, beam, truss, and spring elements
- Advanced cross-sections (IPE, Hollow Tubes, Custom)
- Various load types and combinations (Dead, Live, Wind, Seismic)
- Support displacement loads and load combinations
- Professional visualization and DXF export capabilities
- Enhanced post-processing and reporting
"""

__version__ = "1.0.0"
__author__ = "PyFEALiTE Team"

# Core components
from .core.node import Node2D
from .core.element import FrameElement2D
from .core.spring_element import SpringElement2D, SpringProperties
from .core.structure import Structure
from .core.enums import DOF, LoadDirection, SupportType, ElementType

# Materials
from .materials.isotropic import IsotropicMaterial

# Cross-sections
from .sections.rectangular import RectangularSection
from .sections.circular import CircularSection
from .sections.ipe_section import IPESection, IPEDimensions
from .sections.hollow_tube import HollowTube, HollowTubeDimensions
from .sections.generic_2d import Generic2DSection
from .sections.aisc_section import AISCSection, AISCDimensions

# Loads
from .loads.base import LoadCase, LoadType
from .loads.point_load import PointLoad, NodalLoad
from .loads.distributed_load import UniformLoad, TrapezoidalLoad
from .loads.support_displacement import SupportDisplacementLoad
# from .loads.load_case import LoadCaseContainer as LoadCaseManager  # Not available
from .loads.load_combination import LoadCombination, LoadCombinationManager

# Analysis
from .analysis.post_processor import EnhancedPostProcessor

# Export
# from .export.dxf_exporter import DXFExporter, DXFExportSettings, export_structure_to_dxf  # Temporarily disabled

__all__ = [
    # Core
    "Node2D",
    "FrameElement2D",
    "SpringElement2D", 
    "SpringProperties",
    "Structure",
    "DOF",
    "LoadDirection",
    "SupportType",
    "ElementType",
    
    # Materials
    "IsotropicMaterial",
    
    # Sections
    "RectangularSection",
    "CircularSection",
    "IPESection",
    "IPEDimensions", 
    "HollowTube",
    "HollowTubeDimensions",
    "Generic2DSection",
    "AISCSection",
    "AISCDimensions",
    
    # Loads
    "LoadCase",
    "LoadType",
    "PointLoad",
    "NodalLoad",
    "UniformLoad",
    "TrapezoidalLoad",
    "SupportDisplacementLoad",
    "LoadCaseManager",
    "LoadCombination", 
    "LoadCombinationManager",
    
    # Analysis
    "EnhancedPostProcessor",
    
    # Export
    "DXFExporter",
    "DXFExportSettings",
    "export_structure_to_dxf"
]