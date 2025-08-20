"""Generic 2D cross-section with arbitrary properties."""

from typing import Optional
from .base import CrossSection
from ..materials.base import IMaterial


class Generic2DSection(CrossSection):
    """
    Generic 2D cross-section with user-defined properties.
    
    Allows specification of any geometric properties directly.
    Useful for custom sections or preliminary analysis.
    
    Attributes:
        area: Cross-sectional area (m²)
        Iz: Moment of inertia about strong axis (m⁴)
        Iy: Moment of inertia about weak axis (m⁴)  
        J: Torsional constant (m⁴)
        Ax: Effective shear area in x-direction (m²)
        Ay: Effective shear area in y-direction (m²)
        material: Material properties
        label: Section label
    """
    
    def __init__(self, 
                 material: IMaterial,
                 area: float,
                 Iz: float,
                 Iy: Optional[float] = None,
                 J: Optional[float] = None,
                 Ax: Optional[float] = None,
                 Ay: Optional[float] = None,
                 label: str = "Generic2D"):
        """
        Initialize generic 2D section.
        
        Args:
            material: Material properties
            area: Cross-sectional area (m²)
            Iz: Moment of inertia about strong axis (m⁴)
            Iy: Moment of inertia about weak axis (m⁴), defaults to Iz
            J: Torsional constant (m⁴), defaults to Iz + Iy
            Ax: Effective shear area in x-direction (m²), defaults to area
            Ay: Effective shear area in y-direction (m²), defaults to area
            label: Section label
        """
        super().__init__(material, label)
        
        if area <= 0:
            raise ValueError("Area must be positive")
        if Iz <= 0:
            raise ValueError("Moment of inertia Iz must be positive")
        
        self._area = area
        self._Iz = Iz
        self._Iy = Iy if Iy is not None else Iz
        self._J = J if J is not None else (self._Iz + self._Iy)
        self._Ax = Ax if Ax is not None else area
        self._Ay = Ay if Ay is not None else area
        
        # Calculate derived properties
        import numpy as np
        self._rx = np.sqrt(self._Iz / self._area)  # Radius of gyration about x-axis
        self._ry = np.sqrt(self._Iy / self._area)  # Radius of gyration about y-axis
    
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
    def rx(self) -> float:
        """Radius of gyration about x-axis (m)."""
        return self._rx
    
    @property
    def ry(self) -> float:
        """Radius of gyration about y-axis (m)."""
        return self._ry
    
    def update_properties(self,
                         area: Optional[float] = None,
                         Iz: Optional[float] = None,
                         Iy: Optional[float] = None,
                         J: Optional[float] = None,
                         Ax: Optional[float] = None,
                         Ay: Optional[float] = None) -> None:
        """
        Update section properties.
        
        Args:
            area: New cross-sectional area (m²)
            Iz: New moment of inertia about strong axis (m⁴)
            Iy: New moment of inertia about weak axis (m⁴)
            J: New torsional constant (m⁴)
            Ax: New effective shear area in x-direction (m²)
            Ay: New effective shear area in y-direction (m²)
        """
        if area is not None:
            if area <= 0:
                raise ValueError("Area must be positive")
            self._area = area
            
        if Iz is not None:
            if Iz <= 0:
                raise ValueError("Moment of inertia Iz must be positive")
            self._Iz = Iz
            
        if Iy is not None:
            self._Iy = Iy
            
        if J is not None:
            self._J = J
            
        if Ax is not None:
            self._Ax = Ax
            
        if Ay is not None:
            self._Ay = Ay
        
        # Recalculate derived properties
        import numpy as np
        self._rx = np.sqrt(self._Iz / self._area)
        self._ry = np.sqrt(self._Iy / self._area)
    
    def get_section_info(self) -> dict:
        """Get complete section information."""
        return {
            'name': self.label,
            'type': 'Generic 2D',
            'properties': {
                'area_m2': self.area,
                'Iz_m4': self.Iz,
                'Iy_m4': self.Iy,
                'J_m4': self.J,
                'Ax_m2': self.Ax,
                'Ay_m2': self.Ay,
                'rx_m': self.rx,
                'ry_m': self.ry
            },
            'material': self.material.label
        }
    
    @classmethod
    def from_circular_properties(cls, material: IMaterial, diameter: float, 
                                label: str = "Generic2D") -> 'Generic2DSection':
        """
        Create generic section with circular properties.
        
        Args:
            material: Material properties
            diameter: Diameter (m)
            label: Section label
        """
        import numpy as np
        
        area = np.pi * diameter**2 / 4
        I = np.pi * diameter**4 / 64
        J = np.pi * diameter**4 / 32
        A_shear = area * 0.9  # Effective shear area for circular sections
        
        return cls(material, area, I, I, J, A_shear, A_shear, label)
    
    @classmethod
    def from_rectangular_properties(cls, material: IMaterial, width: float, height: float,
                                   label: str = "Generic2D") -> 'Generic2DSection':
        """
        Create generic section with rectangular properties.
        
        Args:
            material: Material properties
            width: Width (m)
            height: Height (m)
            label: Section label
        """
        area = width * height
        Iz = width * height**3 / 12  # Strong axis (about z-axis)
        Iy = height * width**3 / 12  # Weak axis (about y-axis)
        
        # Torsional constant for rectangle (approximate)
        if width >= height:
            a, b = width/2, height/2
        else:
            a, b = height/2, width/2
        J = (2*a) * (2*b)**3 * (16/3 - 3.36*(2*b)/(2*a) * (1 - (2*b)**4/(12*(2*a)**4)))
        
        # Effective shear areas
        Ax = area * 5/6  # For rectangular sections
        Ay = area * 5/6
        
        return cls(material, area, Iz, Iy, J, Ax, Ay, label)
    
    def scale_properties(self, scale_factor: float) -> None:
        """
        Scale all section properties by a factor.
        
        Args:
            scale_factor: Factor to scale properties
        """
        if scale_factor <= 0:
            raise ValueError("Scale factor must be positive")
        
        self._area *= scale_factor**2
        self._Iz *= scale_factor**4
        self._Iy *= scale_factor**4
        self._J *= scale_factor**4
        self._Ax *= scale_factor**2
        self._Ay *= scale_factor**2
        
        # Radii of gyration scale by linear factor
        self._rx *= scale_factor
        self._ry *= scale_factor
    
    def __str__(self) -> str:
        """String representation."""
        return f"Generic2DSection({self.label}, {self.material.label})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"Generic2DSection(material={self.material.label}, "
                f"A={self.area:.2e} m², Iz={self.Iz:.2e} m⁴, "
                f"Iy={self.Iy:.2e} m⁴, label='{self.label}')")
