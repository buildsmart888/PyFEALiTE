"""Load classes for structural analysis."""

from .base import Load, LoadDirection, LoadCase, LoadType
from .point_load import PointLoad, NodalLoad
from .distributed_load import UniformLoad, TrapezoidalLoad

__all__ = [
    "Load",
    "LoadDirection", 
    "LoadCase",
    "LoadType",
    "PointLoad",
    "NodalLoad",
    "UniformLoad", 
    "TrapezoidalLoad",
]