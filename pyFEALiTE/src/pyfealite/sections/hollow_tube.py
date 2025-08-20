"""Hollow circular tube cross-section implementation."""

import numpy as np
from dataclasses import dataclass
from typing import Optional

from .base import CrossSectionBase
from ..materials.base import IMaterial


@dataclass
class HollowTubeDimensions:
    """Hollow tube dimensions."""
    outer_diameter: float  # Outer diameter (mm)
    wall_thickness: float  # Wall thickness (mm)
    
    def __post_init__(self):
        """Validate dimensions."""
        if self.outer_diameter <= 0:
            raise ValueError("Outer diameter must be positive")
        if self.wall_thickness <= 0:
            raise ValueError("Wall thickness must be positive")
        if self.wall_thickness >= self.outer_diameter / 2:
            raise ValueError("Wall thickness too large for outer diameter")
    
    @property
    def inner_diameter(self) -> float:
        """Inner diameter (mm)."""
        return self.outer_diameter - 2 * self.wall_thickness


class HollowTube(CrossSectionBase):
    """
    Hollow circular tube cross-section.
    
    Standard circular hollow sections (CHS) and custom tubes.
    Calculates all geometric properties analytically.
    
    Attributes:
        dimensions: Tube dimensions (outer diameter, wall thickness)
        material: Material properties
        label: Section label
    """
    
    # Standard CHS sections database (outer diameter x wall thickness in mm)
    STANDARD_SECTIONS = {
        # Small sizes
        'CHS26.9x2.3': HollowTubeDimensions(26.9, 2.3),
        'CHS33.7x2.3': HollowTubeDimensions(33.7, 2.3),
        'CHS42.4x2.6': HollowTubeDimensions(42.4, 2.6),
        'CHS48.3x2.6': HollowTubeDimensions(48.3, 2.6),
        'CHS60.3x2.9': HollowTubeDimensions(60.3, 2.9),
        'CHS76.1x2.9': HollowTubeDimensions(76.1, 2.9),
        'CHS88.9x3.2': HollowTubeDimensions(88.9, 3.2),
        'CHS101.6x3.6': HollowTubeDimensions(101.6, 3.6),
        'CHS114.3x3.6': HollowTubeDimensions(114.3, 3.6),
        
        # Medium sizes
        'CHS139.7x4.0': HollowTubeDimensions(139.7, 4.0),
        'CHS139.7x5.0': HollowTubeDimensions(139.7, 5.0),
        'CHS168.3x4.0': HollowTubeDimensions(168.3, 4.0),
        'CHS168.3x5.0': HollowTubeDimensions(168.3, 5.0),
        'CHS193.7x5.0': HollowTubeDimensions(193.7, 5.0),
        'CHS193.7x6.3': HollowTubeDimensions(193.7, 6.3),
        'CHS219.1x5.0': HollowTubeDimensions(219.1, 5.0),
        'CHS219.1x6.3': HollowTubeDimensions(219.1, 6.3),
        'CHS219.1x8.0': HollowTubeDimensions(219.1, 8.0),
        
        # Large sizes
        'CHS273.0x6.3': HollowTubeDimensions(273.0, 6.3),
        'CHS273.0x8.0': HollowTubeDimensions(273.0, 8.0),
        'CHS273.0x10.0': HollowTubeDimensions(273.0, 10.0),
        'CHS323.9x8.0': HollowTubeDimensions(323.9, 8.0),
        'CHS323.9x10.0': HollowTubeDimensions(323.9, 10.0),
        'CHS355.6x8.0': HollowTubeDimensions(355.6, 8.0),
        'CHS355.6x10.0': HollowTubeDimensions(355.6, 10.0),
        'CHS406.4x10.0': HollowTubeDimensions(406.4, 10.0),
        'CHS406.4x12.5': HollowTubeDimensions(406.4, 12.5),
        'CHS457.0x10.0': HollowTubeDimensions(457.0, 10.0),
        'CHS457.0x12.5': HollowTubeDimensions(457.0, 12.5),
        'CHS508.0x12.5': HollowTubeDimensions(508.0, 12.5),
        'CHS508.0x16.0': HollowTubeDimensions(508.0, 16.0),
    }
    
    def __init__(self, material: IMaterial, section_name: Optional[str] = None,
                 dimensions: Optional[HollowTubeDimensions] = None, label: str = ""):
        """
        Initialize hollow tube section.
        
        Args:
            material: Material properties
            section_name: Standard CHS section name (e.g., 'CHS219.1x6.3')
            dimensions: Custom dimensions (if not using standard)
            label: Section label
        """
        if section_name and section_name in self.STANDARD_SECTIONS:
            self.dimensions = self.STANDARD_SECTIONS[section_name]
            self.section_name = section_name
        elif dimensions:
            self.dimensions = dimensions
            self.section_name = f"CHS{dimensions.outer_diameter}x{dimensions.wall_thickness}"
        else:
            raise ValueError("Must specify either section_name or dimensions")
        
        super().__init__(material, label or self.section_name)
        
        # Calculate properties
        self._calculate_properties()
    
    def _calculate_properties(self) -> None:
        """Calculate all geometric properties analytically."""
        # Convert mm to m
        D = self.dimensions.outer_diameter / 1000.0  # Outer diameter
        t = self.dimensions.wall_thickness / 1000.0  # Wall thickness
        d = D - 2*t  # Inner diameter
        
        # Cross-sectional area
        self._area = np.pi/4 * (D**2 - d**2)
        
        # Moment of inertia (same for both axes due to circular symmetry)
        self._Iz = np.pi/64 * (D**4 - d**4)
        self._Iy = self._Iz
        
        # Torsional constant (polar moment of inertia)
        self._J = np.pi/32 * (D**4 - d**4)
        
        # Effective shear areas (for circular sections)
        # Approximate effective shear area for thin-walled tubes
        self._Ax = self.area * 0.5  # Conservative estimate
        self._Ay = self.area * 0.5  # Same for both directions
        
        # Section moduli
        self._Wx = self._Iz / (D/2)  # Elastic section modulus
        self._Wy = self._Wx  # Same for both axes
        
        # Radii of gyration
        self._rx = np.sqrt(self._Iz / self.area)
        self._ry = self._rx  # Same for both axes
        
        # Plastic section modulus (approximate)
        self._Zx = (D**3 - d**3) / 6
        self._Zy = self._Zx
    
    @property
    def area(self) -> float:
        """Cross-sectional area (m²)."""
        return self._area
    
    @property
    def Iz(self) -> float:
        """Moment of inertia about z-axis (m⁴)."""
        return self._Iz
    
    @property
    def Iy(self) -> float:
        """Moment of inertia about y-axis (m⁴)."""
        return self._Iy
    
    @property
    def J(self) -> float:
        """Torsional constant (polar moment of inertia) (m⁴)."""
        return self._J
    
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
    def outer_diameter(self) -> float:
        """Outer diameter (m)."""
        return self.dimensions.outer_diameter / 1000.0
    
    @property
    def inner_diameter(self) -> float:
        """Inner diameter (m)."""
        return self.dimensions.inner_diameter / 1000.0
    
    @property
    def wall_thickness(self) -> float:
        """Wall thickness (m)."""
        return self.dimensions.wall_thickness / 1000.0
    
    @property
    def diameter_to_thickness_ratio(self) -> float:
        """D/t ratio for slenderness checks."""
        return self.dimensions.outer_diameter / self.dimensions.wall_thickness
    
    def get_section_info(self) -> dict:
        """Get complete section information."""
        return {
            'name': self.section_name,
            'type': 'Hollow Tube (CHS)',
            'dimensions_mm': {
                'outer_diameter': self.dimensions.outer_diameter,
                'inner_diameter': self.dimensions.inner_diameter,
                'wall_thickness': self.dimensions.wall_thickness,
                'D_t_ratio': self.diameter_to_thickness_ratio
            },
            'properties': {
                'area_m2': self.area,
                'Iz_m4': self.Iz,
                'Iy_m4': self.Iy,
                'J_m4': self.J,
                'Wx_m3': self.Wx,
                'Wy_m3': self.Wy,
                'Zx_m3': self.Zx,
                'Zy_m3': self.Zy,
                'rx_m': self.rx,
                'ry_m': self.ry
            },
            'material': self.material.label
        }
    
    def check_local_buckling(self, fy: float) -> dict:
        """
        Check local buckling limits for the tube.
        
        Args:
            fy: Yield strength (Pa)
            
        Returns:
            Dictionary with buckling check results
        """
        E = self.material.elastic_modulus
        D_t = self.diameter_to_thickness_ratio
        
        # Slenderness parameter
        lambda_p = D_t / (E / fy) ** 0.5
        
        # Classification limits (simplified)
        compact_limit = 0.31 * (E / fy) ** 0.5
        noncompact_limit = 0.45 * (E / fy) ** 0.5
        
        if D_t <= compact_limit:
            classification = "Compact"
        elif D_t <= noncompact_limit:
            classification = "Non-compact"
        else:
            classification = "Slender"
        
        return {
            'D_t_ratio': D_t,
            'compact_limit': compact_limit,
            'noncompact_limit': noncompact_limit,
            'classification': classification,
            'lambda_p': lambda_p
        }
    
    @classmethod
    def list_standard_sections(cls) -> list[str]:
        """List all available standard CHS sections."""
        return sorted(cls.STANDARD_SECTIONS.keys())
    
    @classmethod
    def get_standard_dimensions(cls, section_name: str) -> HollowTubeDimensions:
        """Get dimensions for a standard section."""
        if section_name not in cls.STANDARD_SECTIONS:
            raise ValueError(f"Unknown section: {section_name}")
        return cls.STANDARD_SECTIONS[section_name]
    
    @classmethod
    def from_diameter_thickness(cls, material: IMaterial, outer_diameter: float,
                               wall_thickness: float, label: str = "") -> 'HollowTube':
        """
        Create hollow tube from diameter and thickness.
        
        Args:
            material: Material properties
            outer_diameter: Outer diameter (mm)
            wall_thickness: Wall thickness (mm)
            label: Section label
        """
        dimensions = HollowTubeDimensions(outer_diameter, wall_thickness)
        return cls(material, dimensions=dimensions, label=label)
    
    def __str__(self) -> str:
        """String representation."""
        return f"HollowTube({self.section_name}, {self.material.label})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"HollowTube(section_name='{self.section_name}', "
                f"material={self.material.label}, "
                f"D={self.outer_diameter*1000:.1f}mm, t={self.wall_thickness*1000:.1f}mm, "
                f"A={self.area:.2e} m²)")
