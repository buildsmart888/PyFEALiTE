"""European I-beam (IPE) cross-section implementation."""

import numpy as np
from dataclasses import dataclass
from typing import Optional

from .base import CrossSectionBase
from ..materials.base import IMaterial


@dataclass
class IPEDimensions:
    """IPE section dimensions."""
    h: float      # Total height of the section (mm)
    b: float      # Flange width (mm)
    tw: float     # Web thickness (mm)
    tf: float     # Flange thickness (mm)
    r: float      # Fillet radius (mm)
    
    def __post_init__(self):
        """Validate dimensions."""
        if any(dim <= 0 for dim in [self.h, self.b, self.tw, self.tf, self.r]):
            raise ValueError("All dimensions must be positive")
        if self.tf >= self.h/2:
            raise ValueError("Flange thickness too large for section height")
        if self.tw >= self.b:
            raise ValueError("Web thickness too large for flange width")


class IPESection(CrossSectionBase):
    """
    European I-beam (IPE) cross-section.
    
    Standard IPE sections according to European standards.
    Calculates all geometric properties automatically.
    
    Attributes:
        dimensions: IPE dimensions (h, b, tw, tf, r)
        material: Material properties
        label: Section label
    """
    
    # Standard IPE section database (dimensions in mm)
    STANDARD_SECTIONS = {
        'IPE80': IPEDimensions(h=80, b=46, tw=3.8, tf=5.2, r=5),
        'IPE100': IPEDimensions(h=100, b=55, tw=4.1, tf=5.7, r=7),
        'IPE120': IPEDimensions(h=120, b=64, tw=4.4, tf=6.3, r=7),
        'IPE140': IPEDimensions(h=140, b=73, tw=4.7, tf=6.9, r=7),
        'IPE160': IPEDimensions(h=160, b=82, tw=5.0, tf=7.4, r=9),
        'IPE180': IPEDimensions(h=180, b=91, tw=5.3, tf=8.0, r=9),
        'IPE200': IPEDimensions(h=200, b=100, tw=5.6, tf=8.5, r=12),
        'IPE220': IPEDimensions(h=220, b=110, tw=5.9, tf=9.2, r=12),
        'IPE240': IPEDimensions(h=240, b=120, tw=6.2, tf=9.8, r=15),
        'IPE270': IPEDimensions(h=270, b=135, tw=6.6, tf=10.2, r=15),
        'IPE300': IPEDimensions(h=300, b=150, tw=7.1, tf=10.7, r=15),
        'IPE330': IPEDimensions(h=330, b=160, tw=7.5, tf=11.5, r=18),
        'IPE360': IPEDimensions(h=360, b=170, tw=8.0, tf=12.7, r=18),
        'IPE400': IPEDimensions(h=400, b=180, tw=8.6, tf=13.5, r=21),
        'IPE450': IPEDimensions(h=450, b=190, tw=9.4, tf=14.6, r=21),
        'IPE500': IPEDimensions(h=500, b=200, tw=10.2, tf=16.0, r=21),
        'IPE550': IPEDimensions(h=550, b=210, tw=11.1, tf=17.2, r=24),
        'IPE600': IPEDimensions(h=600, b=220, tw=12.0, tf=19.0, r=24),
    }
    
    def __init__(self, material: IMaterial, section_name: Optional[str] = None,
                 dimensions: Optional[IPEDimensions] = None, label: str = ""):
        """
        Initialize IPE section.
        
        Args:
            material: Material properties
            section_name: Standard IPE section name (e.g., 'IPE200')
            dimensions: Custom dimensions (if not using standard)
            label: Section label
        """
        if section_name and section_name in self.STANDARD_SECTIONS:
            self.dimensions = self.STANDARD_SECTIONS[section_name]
            self.section_name = section_name
        elif dimensions:
            self.dimensions = dimensions
            self.section_name = "Custom"
        else:
            raise ValueError("Must specify either section_name or dimensions")
        
        super().__init__(material, label or self.section_name)
        
        # Calculate properties
        self._calculate_properties()
    
    def _calculate_properties(self) -> None:
        """Calculate all geometric properties."""
        d = self.dimensions
        
        # Convert mm to m for calculations
        h = d.h / 1000.0
        b = d.b / 1000.0
        tw = d.tw / 1000.0
        tf = d.tf / 1000.0
        r = d.r / 1000.0
        
        # Cross-sectional area
        A_web = (h - 2*tf) * tw
        A_flanges = 2 * b * tf
        A_fillets = 4 * (r**2 * (np.pi/4 - 1))  # Approximate
        self._area = A_web + A_flanges + A_fillets
        
        # Moment of inertia about strong axis (Iz)
        # Web contribution
        Iz_web = tw * (h - 2*tf)**3 / 12
        
        # Flange contributions
        y_flange = (h - tf) / 2  # Distance from centroid to flange centroid
        Iz_flanges = 2 * (b * tf**3 / 12 + b * tf * y_flange**2)
        
        # Approximate fillet contribution (simplified)
        Iz_fillets = 4 * (r**4 * 0.055)  # Empirical factor
        
        self._Iz = Iz_web + Iz_flanges + Iz_fillets
        
        # Moment of inertia about weak axis (Iy)
        Iy_web = (h - 2*tf) * tw**3 / 12
        Iy_flanges = 2 * tf * b**3 / 12
        Iy_fillets = 4 * (r**4 * 0.055)  # Empirical factor
        
        self._Iy = Iy_web + Iy_flanges + Iy_fillets
        
        # Torsional constant (approximate)
        # Simplified formula for thin-walled sections
        self._J = (2 * b * tf**3 + (h - 2*tf) * tw**3) / 3
        
        # Shear areas (approximate)
        self._Ax = self.area * 0.9  # Effective area for shear
        self._Ay = (h - 2*tf) * tw  # Web area for major axis shear
        
        # Section moduli
        self._Wx = self._Iz / (h/2)  # Elastic section modulus about x-axis
        self._Wy = self._Iy / (b/2)  # Elastic section modulus about y-axis
        
        # Radii of gyration
        self._rx = np.sqrt(self._Iz / self.area)
        self._ry = np.sqrt(self._Iy / self.area)
    
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
    def rx(self) -> float:
        """Radius of gyration about x-axis (m)."""
        return self._rx
    
    @property
    def ry(self) -> float:
        """Radius of gyration about y-axis (m)."""
        return self._ry
    
    @property
    def height(self) -> float:
        """Total section height (m)."""
        return self.dimensions.h / 1000.0
    
    @property
    def width(self) -> float:
        """Flange width (m)."""
        return self.dimensions.b / 1000.0
    
    @property
    def web_thickness(self) -> float:
        """Web thickness (m)."""
        return self.dimensions.tw / 1000.0
    
    @property
    def flange_thickness(self) -> float:
        """Flange thickness (m)."""
        return self.dimensions.tf / 1000.0
    
    def get_section_info(self) -> dict:
        """Get complete section information."""
        return {
            'name': self.section_name,
            'type': 'IPE',
            'dimensions_mm': {
                'h': self.dimensions.h,
                'b': self.dimensions.b, 
                'tw': self.dimensions.tw,
                'tf': self.dimensions.tf,
                'r': self.dimensions.r
            },
            'properties': {
                'area_m2': self.area,
                'Iz_m4': self.Iz,
                'Iy_m4': self.Iy,
                'J_m4': self.J,
                'Wx_m3': self.Wx,
                'Wy_m3': self.Wy,
                'rx_m': self.rx,
                'ry_m': self.ry
            },
            'material': self.material.label
        }
    
    @classmethod
    def list_standard_sections(cls) -> list[str]:
        """List all available standard IPE sections."""
        return sorted(cls.STANDARD_SECTIONS.keys())
    
    @classmethod
    def get_standard_dimensions(cls, section_name: str) -> IPEDimensions:
        """Get dimensions for a standard section."""
        if section_name not in cls.STANDARD_SECTIONS:
            raise ValueError(f"Unknown section: {section_name}")
        return cls.STANDARD_SECTIONS[section_name]
    
    def __str__(self) -> str:
        """String representation."""
        return f"IPESection({self.section_name}, {self.material.label})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"IPESection(section_name='{self.section_name}', "
                f"material={self.material.label}, "
                f"A={self.area:.2e} m², Iz={self.Iz:.2e} m⁴)")
