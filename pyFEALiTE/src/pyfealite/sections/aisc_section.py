"""AISC Steel Section integration using steelpy library."""

import numpy as np
from typing import Optional, Dict, List, Union, Any
from dataclasses import dataclass
import warnings

try:
    from steelpy import aisc
    STEELPY_AVAILABLE = True
except ImportError:
    STEELPY_AVAILABLE = False
    aisc = None
    warnings.warn(
        "steelpy not available. Install with: pip install steelpy",
        ImportWarning
    )

from .base import CrossSection
from ..materials.base import Material


@dataclass
class AISCDimensions:
    """AISC section dimensions and properties."""
    name: str
    weight: float  # lb/ft
    area: float    # in²
    d: float       # Overall depth, in
    bf: Optional[float] = None  # Flange width, in
    tw: Optional[float] = None  # Web thickness, in
    tf: Optional[float] = None  # Flange thickness, in
    Ix: float = 0.0  # Moment of inertia about x-axis, in⁴
    Iy: float = 0.0  # Moment of inertia about y-axis, in⁴
    Zx: float = 0.0  # Plastic section modulus about x-axis, in³
    Zy: float = 0.0  # Plastic section modulus about y-axis, in³
    Sx: float = 0.0  # Elastic section modulus about x-axis, in³
    Sy: float = 0.0  # Elastic section modulus about y-axis, in³
    rx: float = 0.0  # Radius of gyration about x-axis, in
    ry: float = 0.0  # Radius of gyration about y-axis, in
    J: float = 0.0   # Torsional constant, in⁴
    Cw: Optional[float] = None  # Warping constant, in⁶
    
    def __post_init__(self):
        """Validate dimensions."""
        if self.area <= 0:
            raise ValueError("Area must be positive")
        if self.d <= 0:
            raise ValueError("Depth must be positive")


class AISCSection(CrossSection):
    """
    AISC Steel Section using steelpy database.
    
    Provides access to complete AISC steel section database including:
    - W shapes (Wide flange beams)
    - HSS shapes (Hollow structural sections)
    - Pipe sections
    - Angle sections (L shapes)
    - Channel sections (C, MC shapes)
    - Tee sections (WT, MT, ST shapes)
    
    All properties are automatically converted from imperial to SI units.
    """
    
    # Available section types in steelpy
    SECTION_TYPES = {
        'W': 'W_shapes',        # Wide flange beams
        'M': 'M_shapes',        # Miscellaneous beams
        'S': 'S_shapes',        # Standard beams
        'HP': 'HP_shapes',      # Bearing pile sections
        'C': 'C_shapes',        # American standard channels
        'MC': 'MC_shapes',      # Miscellaneous channels
        'HSS': 'HSS_shapes',    # Hollow structural sections (round)
        'HSS_R': 'HSS_R_shapes',# Hollow structural sections (rectangular)
        'PIPE': 'PIPE_shapes',  # Pipe sections
        'L': 'L_shapes',        # Single angles
        'DBL_L': 'DBL_L_shapes',# Double angles
        'WT': 'WT_shapes',      # Structural tees cut from W shapes
        'MT': 'MT_shapes',      # Structural tees cut from M shapes
        'ST': 'ST_shapes',      # Structural tees cut from S shapes
    }
    
    def __init__(self, section_name: str, material: Material, label: str = ""):
        """
        Initialize AISC section.
        
        Args:
            material: Material properties
            section_name: AISC section name (e.g., 'W12X26', 'HSS6X6X1/4')
            label: Section label
        """
        if not STEELPY_AVAILABLE:
            raise ImportError("steelpy library is required for AISC sections")
        
        self.section_name = section_name
        self.aisc_section = self._get_aisc_section(section_name)
        
        # Extract dimensions and properties
        self.dimensions = self._extract_dimensions()
        
        super().__init__(material, label or section_name)
        
        # Convert properties to SI units
        self._convert_to_si_units()
    
    def _get_aisc_section(self, section_name: str) -> Any:
        """Get AISC section object from steelpy."""
        # Determine section type from name
        section_type = self._determine_section_type(section_name)
        
        if section_type not in self.SECTION_TYPES:
            raise ValueError(f"Unknown section type for {section_name}")
        
        # Get the appropriate shape collection
        shape_collection = getattr(aisc, self.SECTION_TYPES[section_type])
        
        # Handle special naming conventions
        normalized_name = self._normalize_section_name(section_name)
        
        try:
            return getattr(shape_collection, normalized_name)
        except AttributeError:
            # Try to find similar sections
            available_sections = [name for name in dir(shape_collection) 
                                if not name.startswith('_')]
            raise ValueError(f"Section {section_name} not found. "
                           f"Available {section_type} sections: {available_sections[:10]}...")
    
    def _determine_section_type(self, section_name: str) -> str:
        """Determine section type from section name."""
        upper_name = section_name.upper()
        
        # Check each section type pattern
        if upper_name.startswith('W'):
            return 'W'
        elif upper_name.startswith('M'):
            return 'M'
        elif upper_name.startswith('S'):
            return 'S'
        elif upper_name.startswith('HP'):
            return 'HP'
        elif upper_name.startswith('C') and not upper_name.startswith('CHS'):
            return 'MC' if 'MC' in upper_name else 'C'
        elif upper_name.startswith('HSS') and 'X' in upper_name:
            # Rectangular HSS have multiple X's, round HSS have diameter
            return 'HSS_R' if upper_name.count('X') >= 2 else 'HSS'
        elif upper_name.startswith('PIPE'):
            return 'PIPE'
        elif upper_name.startswith('L'):
            return 'DBL_L' if 'DBL' in upper_name or 'DOUBLE' in upper_name else 'L'
        elif upper_name.startswith('WT'):
            return 'WT'
        elif upper_name.startswith('MT'):
            return 'MT'
        elif upper_name.startswith('ST'):
            return 'ST'
        else:
            raise ValueError(f"Cannot determine section type for {section_name}")
    
    def _normalize_section_name(self, section_name: str) -> str:
        """Normalize section name for steelpy attribute access."""
        # Replace special characters with underscores
        normalized = section_name.replace('-', '_').replace('.', '_').replace('/', '_')
        
        # Handle fractions and special cases
        normalized = normalized.replace('1_2', '1_2')  # 1/2 -> 1_2
        normalized = normalized.replace('1_4', '1_4')  # 1/4 -> 1_4
        normalized = normalized.replace('3_4', '3_4')  # 3/4 -> 3_4
        normalized = normalized.replace('3_8', '3_8')  # 3/8 -> 3_8
        normalized = normalized.replace('5_8', '5_8')  # 5/8 -> 5_8
        normalized = normalized.replace('7_8', '7_8')  # 7/8 -> 7_8
        
        return normalized
    
    def _extract_dimensions(self) -> AISCDimensions:
        """Extract dimensions from AISC section."""
        section = self.aisc_section
        
        return AISCDimensions(
            name=self.section_name,
            weight=getattr(section, 'weight', 0.0),
            area=getattr(section, 'area', 0.0),
            d=getattr(section, 'd', 0.0),
            bf=getattr(section, 'bf', None),
            tw=getattr(section, 'tw', None),
            tf=getattr(section, 'tf', None),
            Ix=getattr(section, 'Ix', 0.0),
            Iy=getattr(section, 'Iy', 0.0),
            Zx=getattr(section, 'Zx', 0.0),
            Zy=getattr(section, 'Zy', 0.0),
            Sx=getattr(section, 'Sx', 0.0),
            Sy=getattr(section, 'Sy', 0.0),
            rx=getattr(section, 'rx', 0.0),
            ry=getattr(section, 'ry', 0.0),
            J=getattr(section, 'J', 0.0),
            Cw=getattr(section, 'Cw', None),
        )
    
    def _convert_to_si_units(self) -> None:
        """Convert imperial units to SI units."""
        # Conversion factors
        IN_TO_M = 0.0254          # inches to meters
        IN2_TO_M2 = IN_TO_M**2    # square inches to square meters  
        IN3_TO_M3 = IN_TO_M**3    # cubic inches to cubic meters
        IN4_TO_M4 = IN_TO_M**4    # fourth power inches to m⁴
        IN6_TO_M6 = IN_TO_M**6    # sixth power inches to m⁶
        
        # Convert area properties
        self._area = self.dimensions.area * IN2_TO_M2
        
        # Convert moment of inertia
        self._Iz = self.dimensions.Ix * IN4_TO_M4  # Strong axis (about z in 2D)
        self._Iy = self.dimensions.Iy * IN4_TO_M4  # Weak axis (about y in 2D)
        
        # Convert section moduli  
        self._Wx = self.dimensions.Sx * IN3_TO_M3  # Elastic section modulus
        self._Wy = self.dimensions.Sy * IN3_TO_M3
        self._Zx = self.dimensions.Zx * IN3_TO_M3  # Plastic section modulus
        self._Zy = self.dimensions.Zy * IN3_TO_M3
        
        # Convert radii of gyration
        self._rx = self.dimensions.rx * IN_TO_M
        self._ry = self.dimensions.ry * IN_TO_M
        
        # Convert torsional properties
        self._J = self.dimensions.J * IN4_TO_M4
        
        # Convert warping constant if available
        if self.dimensions.Cw is not None:
            self._Cw = self.dimensions.Cw * IN6_TO_M6
        else:
            self._Cw = 0.0
        
        # Convert geometric dimensions
        self._depth = self.dimensions.d * IN_TO_M
        self._width = (self.dimensions.bf * IN_TO_M) if self.dimensions.bf else 0.0
        self._web_thickness = (self.dimensions.tw * IN_TO_M) if self.dimensions.tw else 0.0
        self._flange_thickness = (self.dimensions.tf * IN_TO_M) if self.dimensions.tf else 0.0
        
        # Effective shear areas (approximate)
        if hasattr(self.aisc_section, 'Aw'):
            # Use web area if available
            self._Ay = getattr(self.aisc_section, 'Aw', 0.0) * IN2_TO_M2
        else:
            # Approximate for wide flange sections
            if self.dimensions.tw and self.dimensions.d:
                self._Ay = self.dimensions.d * self.dimensions.tw * IN2_TO_M2
            else:
                self._Ay = self._area * 0.9  # Conservative estimate
        
        self._Ax = self._area * 0.9  # Conservative estimate for horizontal shear
    
    @property
    def area(self) -> float:
        """Cross-sectional area (m²)."""
        return self._area
    
    @property
    def Iz(self) -> float:
        """Moment of inertia about strong axis (m⁴)."""
        return self._Iz
    
    @property
    def Iy(self) -> float:
        """Moment of inertia about weak axis (m⁴)."""
        return self._Iy
    
    @property
    def J(self) -> float:
        """Torsional constant (m⁴)."""
        return self._J
    
    @property
    def Cw(self) -> float:
        """Warping constant (m⁶)."""
        return self._Cw
    
    @property
    def Ax(self) -> float:
        """Effective shear area in x-direction (m²)."""
        return self._Ax
    
    @property
    def Ay(self) -> float:
        """Effective shear area in y-direction (m²)."""
        return self._Ay
    
    @property
    def Wx(self) -> float:
        """Elastic section modulus about x-axis (m³)."""
        return self._Wx
    
    @property
    def Wy(self) -> float:
        """Elastic section modulus about y-axis (m³)."""
        return self._Wy
    
    @property
    def Zx(self) -> float:
        """Plastic section modulus about x-axis (m³)."""
        return self._Zx
    
    @property
    def Zy(self) -> float:
        """Plastic section modulus about y-axis (m³)."""
        return self._Zy
    
    @property
    def rx(self) -> float:
        """Radius of gyration about x-axis (m)."""
        return self._rx
    
    @property
    def ry(self) -> float:
        """Radius of gyration about y-axis (m)."""
        return self._ry
    
    @property
    def depth(self) -> float:
        """Overall depth (m)."""
        return self._depth
    
    @property
    def width(self) -> float:
        """Flange width (m)."""
        return self._width
    
    @property
    def web_thickness(self) -> float:
        """Web thickness (m)."""
        return self._web_thickness
    
    @property
    def flange_thickness(self) -> float:
        """Flange thickness (m)."""
        return self._flange_thickness
    
    @property
    def weight_per_length(self) -> float:
        """Weight per unit length (kg/m)."""
        # Convert lb/ft to kg/m
        LB_FT_TO_KG_M = 1.48816  # conversion factor
        return self.dimensions.weight * LB_FT_TO_KG_M
    
    def get_section_info(self) -> Dict[str, Any]:
        """Get complete section information."""
        return {
            'name': self.section_name,
            'type': 'AISC Steel Section',
            'steelpy_available': STEELPY_AVAILABLE,
            'dimensions_imperial': {
                'weight_lb_ft': self.dimensions.weight,
                'area_in2': self.dimensions.area,
                'd_in': self.dimensions.d,
                'bf_in': self.dimensions.bf,
                'tw_in': self.dimensions.tw,
                'tf_in': self.dimensions.tf,
            },
            'properties_si': {
                'area_m2': self.area,
                'Iz_m4': self.Iz,
                'Iy_m4': self.Iy,
                'J_m4': self.J,
                'Cw_m6': self.Cw,
                'Wx_m3': self.Wx,
                'Wy_m3': self.Wy,
                'Zx_m3': self.Zx,
                'Zy_m3': self.Zy,
                'rx_m': self.rx,
                'ry_m': self.ry,
                'depth_m': self.depth,
                'width_m': self.width,
                'weight_kg_m': self.weight_per_length,
            },
            'material': self.material.label
        }
    
    @classmethod
    def list_available_sections(cls, section_type: str = 'W') -> List[str]:
        """
        List available sections of specified type.
        
        Args:
            section_type: Section type ('W', 'HSS', 'PIPE', etc.)
            
        Returns:
            List of available section names
        """
        if not STEELPY_AVAILABLE:
            return []
        
        if section_type not in cls.SECTION_TYPES:
            return []
        
        shape_collection = getattr(aisc, cls.SECTION_TYPES[section_type])
        return [name for name in dir(shape_collection) if not name.startswith('_')]
    
    @classmethod
    def search_sections(cls, section_type: str = 'W', criteria: Optional[Dict] = None,
                       sort_by: str = 'weight') -> Dict[str, Any]:
        """
        Search and filter sections based on criteria.
        
        Args:
            section_type: Section type to search
            criteria: Filter criteria (e.g., {'d': {'min': 12, 'max': 18}})
            sort_by: Property to sort by
            
        Returns:
            Dictionary of filtered sections
        """
        if not STEELPY_AVAILABLE:
            return {}
        
        if section_type not in cls.SECTION_TYPES:
            return {}
        
        shape_collection = getattr(aisc, cls.SECTION_TYPES[section_type])
        
        if criteria:
            return shape_collection.filter(criteria, sort_by=sort_by)
        else:
            # Return all sections as dictionary
            sections = {}
            for name in cls.list_available_sections(section_type):
                try:
                    sections[name] = getattr(shape_collection, name)
                except AttributeError:
                    continue
            return sections
    
    @classmethod
    def get_section_properties(cls, section_name: str) -> Optional[Dict[str, Any]]:
        """
        Get properties of a specific section without creating instance.
        
        Args:
            section_name: AISC section name
            
        Returns:
            Dictionary of section properties
        """
        if not STEELPY_AVAILABLE:
            return None
        
        try:
            temp_section = cls._get_aisc_section_static(section_name)
            properties = {}
            
            # Extract all available properties
            for attr in dir(temp_section):
                if not attr.startswith('_') and not callable(getattr(temp_section, attr)):
                    properties[attr] = getattr(temp_section, attr)
            
            return properties
        except (ValueError, AttributeError):
            return None
    
    @classmethod
    def _get_aisc_section_static(cls, section_name: str) -> Any:
        """Static method to get AISC section."""
        # Determine section type
        section_type = cls._determine_section_type_static(section_name)
        shape_collection = getattr(aisc, cls.SECTION_TYPES[section_type])
        normalized_name = cls._normalize_section_name_static(section_name)
        return getattr(shape_collection, normalized_name)
    
    @classmethod
    def _determine_section_type_static(cls, section_name: str) -> str:
        """Static version of section type determination."""
        upper_name = section_name.upper()
        
        if upper_name.startswith('W'):
            return 'W'
        elif upper_name.startswith('HSS') and upper_name.count('X') >= 2:
            return 'HSS_R'
        elif upper_name.startswith('HSS'):
            return 'HSS'
        elif upper_name.startswith('PIPE'):
            return 'PIPE'
        elif upper_name.startswith('L'):
            return 'L'
        elif upper_name.startswith('C'):
            return 'C'
        else:
            return 'W'  # Default
    
    @classmethod
    def _normalize_section_name_static(cls, section_name: str) -> str:
        """Static version of name normalization."""
        return section_name.replace('-', '_').replace('.', '_').replace('/', '_')
    
    def __str__(self) -> str:
        """String representation."""
        return f"AISCSection({self.section_name}, {self.material.label})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"AISCSection(section_name='{self.section_name}', "
                f"material={self.material.label}, "
                f"A={self.area:.2e} m², Iz={self.Iz:.2e} m⁴)")
