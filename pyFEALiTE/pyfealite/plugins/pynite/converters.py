"""Converters between PyFEALiTE data models and PyNite.

Start here: implement translations for nodes, elements, loads, sections and
materials. Keep conversions unit-consistent (SI: N, m, rad).
"""
from typing import Any, Dict


def node_pyfealite_to_pynite(node: Any) -> Dict:
    """Convert a PyFEALiTE Node2D/Node3D to a PyNite node dict.

    This is a minimal placeholder. Implement full mapping later.
    """
    return {
        "name": getattr(node, "label", getattr(node, "name", "N")),
        "x": float(getattr(node, "x", 0.0)),
        "y": float(getattr(node, "y", 0.0)),
        "z": float(getattr(node, "z", 0.0) if hasattr(node, "z") else 0.0),
    }


def element_pyfealite_to_pynite(element: Any) -> Dict:
    """Convert a PyFEALiTE frame element to a PyNite element descriptor.

    Placeholder: map node references and section properties.
    """
    return {
        "name": getattr(element, "label", None),
        "node_i": getattr(element, "node_i", None),
        "node_j": getattr(element, "node_j", None),
        "E": getattr(getattr(element, "material", None), "E", None),
        "A": getattr(getattr(element, "cross_section", None), "A", None),
        "I": getattr(getattr(element, "cross_section", None), "I", None),
    }


def loads_pyfealite_to_pynite(load: Any) -> Dict:
    """Convert PyFEALiTE loads to PyNite load descriptors.

    Placeholder implementation.
    """
    return {
        "node": getattr(load, "node", None),
        "Fx": getattr(load, "Fx", 0.0),
        "Fy": getattr(load, "Fy", 0.0),
        "Fz": getattr(load, "Fz", 0.0),
        "Mx": getattr(load, "Mx", 0.0),
        "My": getattr(load, "My", 0.0),
        "Mz": getattr(load, "Mz", 0.0),
    }


# TODO: implement round-trip converters and unit tests
