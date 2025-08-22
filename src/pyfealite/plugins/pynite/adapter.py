"""Test-friendly PyNite adapter for PyFEALiTE.

This module provides a very small, defensive adapter used by the test
package. It intentionally avoids heavy dependencies and allows tests to
monkeypatch `_try_import_pynite` to provide a fake PyNite-like object.
"""

from typing import Any, Dict
import importlib


class PyNiteNotAvailable(RuntimeError):
    """Raised when the PyNite package is not importable in the runtime."""


def _try_import_pynite():
    """Try a few likely import names for PyNite and return the module.

    Raises ImportError if none are available.
    """
    for name in ("PyNite", "pynite"):
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    raise ImportError("PyNite package not found")


def run_pynite_static(structure: Any, load_case: Any = None, options: Dict = None) -> Dict:
    """Run a PyNite static analysis for the provided PyFEALiTE `structure`.

    The function is intentionally best-effort: when PyNite is absent it
    raises PyNiteNotAvailable; when PyNite is present but APIs differ the
    adapter will try several call patterns and return what it can.

    Return value (best-effort):
      - {"results": AnalysisResults(...), "legacy": {...}} when AnalysisResults
        can be constructed and numpy is available.
      - otherwise a simple mapping with member_forces.
    """
    try:
        pynite_pkg = _try_import_pynite()
    except ImportError as exc:
        raise PyNiteNotAvailable("PyNite not installed") from exc

    # Late import to avoid circular import during tests
    from . import converters

    nodes = [converters.node_pyfealite_to_pynite(n) for n in getattr(structure, "nodes", [])]
    elements = [converters.element_pyfealite_to_pynite(e) for e in getattr(structure, "elements", [])]

    # Resolve an FEModel class (API varies)
    FEModelCls = None
    try:
        try:
            FEModelCls = importlib.import_module("PyNite.FEModel3D").FEModel3D
        except Exception:
            FEModelCls = getattr(pynite_pkg, "FEModel3D", None) or getattr(pynite_pkg, "FEModel", None)
    except Exception:
        FEModelCls = None

    if FEModelCls is None:
        # Nothing to do without an FEModel class
        return {"member_forces": {}}

    # Instantiate model (best-effort)
    try:
        model = FEModelCls()
    except Exception:
        return {"member_forces": {}}

    # Add nodes
    for n in nodes:
        try:
            if hasattr(model, "AddNode"):
                model.AddNode(n["name"], n["x"], n["y"], n.get("z", 0.0))
        except Exception:
            pass

    # Add members
    for e in elements:
        try:
            if hasattr(model, "AddMember"):
                model.AddMember(
                    e.get("name") or f"M_{e.get('node_i')}_{e.get('node_j')}",
                    e.get("node_i"),
                    e.get("node_j"),
                    e.get("E", 0.0),
                    0.0,
                    e.get("I", 0.0),
                    e.get("I", 0.0),
                    0.0,
                    e.get("A", 0.0),
                )
        except Exception:
            pass

    # Apply simple nodal loads if present
    for node_obj in getattr(structure, "nodes", []):
        for load in getattr(node_obj, "loads", []):
            Fx = getattr(load, "Fx", getattr(load, "fx", 0.0)) or 0.0
            Fy = getattr(load, "Fy", getattr(load, "fy", 0.0)) or 0.0
            Fz = getattr(load, "Fz", getattr(load, "fz", 0.0)) or 0.0
            try:
                if hasattr(model, "AddNodeLoad"):
                    model.AddNodeLoad(node_obj.label, Fx, Fy, Fz)
            except Exception:
                pass

    # Run analysis (try several method names)
    try:
        if hasattr(model, "Analyze"):
            model.Analyze()
        elif hasattr(model, "AnalyzeStatic"):
            model.AnalyzeStatic()
        elif hasattr(model, "analyze"):
            model.analyze()
    except Exception:
        pass

    # Collect member forces
    member_forces: Dict[str, Any] = {}
    for e in elements:
        name = e.get("name") or f"M_{e.get('node_i')}_{e.get('node_j')}"
        try:
            if hasattr(model, "GetMemberForces"):
                mf = model.GetMemberForces(name)
            elif hasattr(model, "GetMemberEndForces"):
                mf = model.GetMemberEndForces(name)
            else:
                mf = None
            if mf is not None:
                member_forces[name] = mf
        except Exception:
            pass

    # Normalize internal forces to numpy arrays when possible
    internal_forces = {}
    try:
        import numpy as _np

        for m_name, mfv in member_forces.items():
            try:
                if isinstance(mfv, dict) and all(k in mfv for k in ("Pi", "Vi", "Mi", "Pj", "Vj", "Mj")):
                    internal_forces[m_name] = _np.array([
                        mfv["Pi"], mfv["Vi"], mfv["Mi"], mfv["Pj"], mfv["Vj"], mfv["Mj"],
                    ], dtype=float)
                elif hasattr(mfv, "__len__") and len(mfv) >= 6:
                    internal_forces[m_name] = _np.array([
                        float(mfv[0]), float(mfv[1]), float(mfv[2]), float(mfv[3]), float(mfv[4]), float(mfv[5]),
                    ], dtype=float)
                else:
                    internal_forces[m_name] = _np.array([mfv], dtype=object)
            except Exception:
                internal_forces[m_name] = _np.array([mfv], dtype=object)
    except Exception:
        internal_forces = {}

    # Try to build AnalysisResults
    try:
        from ...analysis.results import AnalysisResults

        ar = AnalysisResults(
            analysis_type="static",
            status="success",
            engine="pynite",
            displacements={},
            reactions={},
            internal_forces=internal_forces,
            metadata={"n_nodes": len(nodes), "n_elements": len(elements)},
        )
        return {"results": ar, "legacy": {"member_forces": member_forces}}
    except Exception:
        return {"member_forces": member_forces}
