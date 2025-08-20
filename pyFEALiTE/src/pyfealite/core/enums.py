"""Enumerations for PyFEALiTE."""

from enum import Enum, IntEnum


class DOF(IntEnum):
    """Degrees of freedom for 2D analysis."""
    UX = 0  # Translation in X direction
    UY = 1  # Translation in Y direction  
    RZ = 2  # Rotation about Z axis


class LoadDirection(Enum):
    """Load direction enumeration."""
    X = "X"
    Y = "Y"
    Z = "Z"
    LOCAL_X = "LOCAL_X"
    LOCAL_Y = "LOCAL_Y"
    LOCAL_Z = "LOCAL_Z"


class SupportType(Enum):
    """Support type enumeration."""
    PIN = "PIN"
    FIXED = "FIXED"
    ROLLER_X = "ROLLER_X"
    ROLLER_Y = "ROLLER_Y"
    FREE = "FREE"


class ElementType(Enum):
    """Element type enumeration."""
    FRAME = "FRAME"
    SPRING = "SPRING"
    TRUSS = "TRUSS"


class LoadType(Enum):
    """Load type enumeration."""
    POINT = "POINT"
    UNIFORM = "UNIFORM"
    TRIANGULAR = "TRIANGULAR"
    TRAPEZOIDAL = "TRAPEZOIDAL"
    NODAL = "NODAL"
    SUPPORT_DISPLACEMENT = "SUPPORT_DISPLACEMENT"


class AnalysisType(Enum):
    """Analysis type enumeration."""
    STATIC = "STATIC"
    MODAL = "MODAL"
    DYNAMIC = "DYNAMIC"
    BUCKLING = "BUCKLING"


class MaterialType(Enum):
    """Material type enumeration."""
    STEEL = "STEEL"
    CONCRETE = "CONCRETE"
    ALUMINUM = "ALUMINUM"
    TIMBER = "TIMBER"
    GENERIC = "GENERIC"


class UnitsSystem(Enum):
    """Units system enumeration."""
    SI = "SI"          # m, kg, s, N, Pa
    METRIC = "METRIC"  # mm, kg, s, N, MPa
    IMPERIAL = "IMPERIAL"  # ft, lb, s, lbf, psi
