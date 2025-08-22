"""Converters between PyFEALiTE data models and PyNite.

Start here: implement translations for nodes, elements, loads, sections and
materials. Keep conversions unit-consistent (SI: N, m, rad).
"""
from typing import Any, Dict


def node_pyfealite_to_pynite(node: Any) -> Dict:
    """Convert a PyFEALiTE Node2D to a PyNite-like node dict.

    Uses the `Node2D` API discovered in the codebase: attributes `label`, `x`, `y`.
    Keeps z=0.0 for 2D models.
    """
    name = getattr(node, "label", getattr(node, "name", None)) or "N"
    x = float(getattr(node, "x", 0.0))
    y = float(getattr(node, "y", 0.0))
    z = float(getattr(node, "z", 0.0) if hasattr(node, "z") else 0.0)

    return {"name": name, "x": x, "y": y, "z": z}


def element_pyfealite_to_pynite(element: Any) -> Dict:
    """Convert a FrameElement2D to a PyNite-like element descriptor.

    Uses discovered API: `start_node`, `end_node`, `label`, `cross_section` with
    `A` and `Iz` (mapped to I). Material E is read from cross_section.material.E.
    The returned dict uses node names (labels) for lightweight assembly.
    """
    name = getattr(element, "label", None)
    start = getattr(element, "start_node", None)
    end = getattr(element, "end_node", None)

    cs = getattr(element, "cross_section", None)
    A = getattr(cs, "A", None) if cs is not None else None
    I = getattr(cs, "Iz", None) if cs is not None else None
    E = None
    if cs is not None and getattr(cs, "material", None) is not None:
        E = getattr(cs.material, "E", None)

    return {
        "name": name,
        "node_i": getattr(start, "label", None) if start is not None else None,
        "node_j": getattr(end, "label", None) if end is not None else None,
        "E": E,
        "A": A,
        "I": I,
    }


def element_releases_to_pynite(element: Any) -> Dict:
    """Extract end-release information from a FrameElement2D.

    Returns a dict with boolean flags for releases at i/j for axial, shear, and
    moment releases as keys: ri_axial, ri_shear, ri_moment, rj_axial, ...
    If the element does not expose releases, returns all False.
    """
    releases = getattr(element, "end_release", None) or {}
    ri = None
    rj = None
    if isinstance(releases, dict):
        ri = releases.get("i")
        rj = releases.get("j")
    elif isinstance(releases, (list, tuple)) and len(releases) >= 2:
        ri, rj = releases[0], releases[1]

    def _flag(release_part, key):
        try:
            return bool(getattr(release_part, key))
        except Exception:
            try:
                return bool(release_part.get(key))
            except Exception:
                return False

    flags = {
        "ri_axial": _flag(ri, "axial") if ri is not None else False,
        "ri_shear": _flag(ri, "shear") if ri is not None else False,
        "ri_moment": _flag(ri, "moment") if ri is not None else False,
        "rj_axial": _flag(rj, "axial") if rj is not None else False,
        "rj_shear": _flag(rj, "shear") if rj is not None else False,
        "rj_moment": _flag(rj, "moment") if rj is not None else False,
    }

    return flags


def loads_pyfealite_to_pynite(load: Any) -> Dict:
    """Convert PyFEALiTE loads to a dict describing nodal loads.

    This is intentionally minimal: extract nodal load components where present.
    """
    return {
        "node": getattr(load, "node", None),
        "Fx": float(getattr(load, "Fx", getattr(load, "fx", 0.0))),
        "Fy": float(getattr(load, "Fy", getattr(load, "fy", 0.0))),
        "Fz": float(getattr(load, "Fz", getattr(load, "fz", 0.0))),
        "Mx": float(getattr(load, "Mx", getattr(load, "mx", 0.0))),
        "My": float(getattr(load, "My", getattr(load, "my", 0.0))),
        "Mz": float(getattr(load, "Mz", getattr(load, "mz", 0.0))),
    }


def dist_load_to_nodal_equivalents(element: Any, w: float, direction: str = "vertical") -> Dict:
    """Convert a uniform distributed load on a 2D frame element to equivalent
    nodal loads (simple approximate conversion for 2-node beam):

    - direction: 'vertical' or 'axial'
    - w: load per length (N/m)

    Returns dict with keys: node_i_load, node_j_load where each is (Fx,Fy,Mz)
    """
    L = getattr(element, "length", None)
    if L is None:
        start = getattr(element, "start_node", None)
        end = getattr(element, "end_node", None)
        if start is not None and end is not None:
            dx = getattr(end, "x", 0.0) - getattr(start, "x", 0.0)
            dy = getattr(end, "y", 0.0) - getattr(start, "y", 0.0)
            L = (dx * dx + dy * dy) ** 0.5
        else:
            L = 1.0

    if direction.lower().startswith("v"):
        Fy_i = w * L / 2.0
        Fy_j = w * L / 2.0
        Mz_i = -w * L * L / 12.0
        Mz_j = w * L * L / 12.0
        return {"node_i_load": (0.0, Fy_i, Mz_i), "node_j_load": (0.0, Fy_j, Mz_j)}
    else:
        Fx_i = w * L / 2.0
        Fx_j = w * L / 2.0
        return {"node_i_load": (Fx_i, 0.0, 0.0), "node_j_load": (Fx_j, 0.0, 0.0)}


def spring_to_pynite(spring: Any) -> Dict:
    """Convert a PyFEALiTE spring support to a PyNite-like representation.

    Expected spring object has attributes: node (label or Node), k_axial, k_shear,
    k_rot (rotational). Returns a dict with node label and stiffness components.
    """
    node = getattr(spring, "node", None)
    node_label = getattr(node, "label", None) if node is not None else node
    return {
        "node": node_label,
        "k_axial": float(getattr(spring, "k_axial", getattr(spring, "kx", 0.0))),
        "k_shear": float(getattr(spring, "k_shear", getattr(spring, "ky", 0.0))),
        "k_rot": float(getattr(spring, "k_rot", getattr(spring, "kr", 0.0))),
    }


# Note: full converters (element releases, distributed loads, springs, etc.)
# will be implemented in follow-up commits. Unit tests will be provided to
# validate mappings and unit consistency.


def element_pointload_to_nodal_equivalents(point_load: Any, element: Any) -> Dict:
    """Convert a PointLoad (applied on an element) to equivalent nodal loads.

    If the point_load has `get_equivalent_nodal_forces(element)` use that.
    Otherwise, fall back to a simple distribution by distance.
    Returns dict with node_i_load and node_j_load tuples (Fx,Fy,Mz).
    """
    try:
        if hasattr(point_load, "get_equivalent_nodal_forces"):
            forces = point_load.get_equivalent_nodal_forces(element)
            if hasattr(forces, "__len__") and len(forces) >= 6:
                return {"node_i_load": (float(forces[0]), float(forces[1]), float(forces[2])), "node_j_load": (float(forces[3]), float(forces[4]), float(forces[5]))}
    except Exception:
        pass

    L = getattr(element, "length", None)
    if L is None:
        start = getattr(element, "start_node", None)
        end = getattr(element, "end_node", None)
        if start is not None and end is not None:
            dx = getattr(end, "x", 0.0) - getattr(start, "x", 0.0)
            dy = getattr(end, "y", 0.0) - getattr(start, "y", 0.0)
            L = (dx * dx + dy * dy) ** 0.5
        else:
            L = 1.0

    a = float(getattr(point_load, "distance", L / 2.0))
    b = max(L - a, 0.0)
    Fx = float(getattr(point_load, "Fx", getattr(point_load, "fx", 0.0)))
    Fy = float(getattr(point_load, "Fy", getattr(point_load, "fy", 0.0)))
    Mz = float(getattr(point_load, "Mz", getattr(point_load, "mz", 0.0)))

    Fx_i = -Fx * b / L if L else 0.0
    Fx_j = -Fx * a / L if L else 0.0
    Fy_i = -Fy * b / L if L else 0.0
    Fy_j = -Fy * a / L if L else 0.0
    Mz_i = -Fy * a * b * b / (L * L) if L and a > 0 and b > 0 else 0.0
    Mz_j = Fy * a * a * b / (L * L) if L and a > 0 and b > 0 else 0.0

    Mz_i += -Mz * b / L if L else 0.0
    Mz_j += -Mz * a / L if L else 0.0

    return {"node_i_load": (Fx_i, Fy_i, Mz_i), "node_j_load": (Fx_j, Fy_j, Mz_j)}
