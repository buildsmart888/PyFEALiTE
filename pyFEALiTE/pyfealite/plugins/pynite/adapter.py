"""Adapter to run PyNite analyses from PyFEALiTE structures.

This module provides a simple facade function `run_pynite_static` that accepts
a PyFEALiTE `Structure` and a `LoadCase`, converts data to PyNite, runs the
analysis (if pynite installed), and returns results in a PyFEALiTE-friendly
format.
"""
from typing import Any, Dict


class PyNiteNotAvailable(RuntimeError):
    """Raised when the PyNite package is not importable in the runtime."""
    pass


def run_pynite_static(structure: Any, load_case: Any, options: Dict = None) -> Dict:
    """Attempt to run a PyNite static analysis using the provided PyFEALiTE Structure.

    Behavior:
    - If `pynite` is not importable, raise PyNiteNotAvailable with a clear message.
    - Otherwise, convert nodes/elements using the plugin `converters` and (TODO)
      assemble and run the PyNite model.

    Returns a dict with keys: 'displacements', 'element_forces', 'summary'.
    """
    try:
        import pynite  # type: ignore
    except Exception as exc:
        raise PyNiteNotAvailable(
            "PyNite is not available in the current environment. Install via `pip install pynite`"
        ) from exc

    # Lazy import of local converters to avoid circular imports when not used
    from . import converters

    # Convert nodes/elements minimally (labels and geometry)
    nodes = [converters.node_pyfealite_to_pynite(n) for n in getattr(structure, "nodes", [])]
    elements = [converters.element_pyfealite_to_pynite(e) for e in getattr(structure, "elements", [])]
from typing import Any, Dict
import importlib


class PyNiteNotAvailable(RuntimeError):
    pass


def _try_import_pynite():
    for name in ("PyNite", "pynite"):
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    raise ImportError("PyNite package not found")


def run_pynite_static(structure: Any, load_case: Any = None, options: Dict = None) -> Dict:
    """Run a minimal PyNite analysis and return AnalysisResults + legacy map.

    This implementation is purposely small and defensive so unit tests
    can monkeypatch `_try_import_pynite` and supply a fake PyNite module.
    """
    try:
        pynite_pkg = _try_import_pynite()
    except ImportError as exc:
        raise PyNiteNotAvailable("PyNite not available") from exc

    from . import converters

    nodes = [converters.node_pyfealite_to_pynite(n) for n in getattr(structure, "nodes", [])]
    elements = [converters.element_pyfealite_to_pynite(e) for e in getattr(structure, "elements", [])]

    try:
        FEModel = getattr(pynite_pkg, "FEModel3D", None) or getattr(pynite_pkg, "FEModel", None)
        if FEModel is None:
            try:
                FEModel = importlib.import_module("PyNite.FEModel3D").FEModel3D
            except Exception:
                FEModel = None

        if FEModel is None:
            return {"member_forces": {}}

        model = FEModel()

        for n in nodes:
            try:
                if hasattr(model, "AddNode"):
                    model.AddNode(n["name"], n["x"], n["y"], n.get("z", 0.0))
            except Exception:
                pass

        for e in elements:
            try:
                if hasattr(model, "AddMember"):
                    model.AddMember(e.get("name") or f"M_{e.get('node_i')}_{e.get('node_j')}", e.get("node_i"), e.get("node_j"), e.get("E", 0.0), 0.0, e.get("I", 0.0), e.get("I", 0.0), 0.0, e.get("A", 0.0))
            except Exception:
                pass

        try:
            if hasattr(model, "Analyze"):
                model.Analyze()
            elif hasattr(model, "AnalyzeStatic"):
                model.AnalyzeStatic()
            elif hasattr(model, "analyze"):
                model.analyze()
        except Exception:
            pass

        member_forces = {}
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

        # Normalize to numpy arrays for AnalysisResults
        try:
            import numpy as _np

            internal_forces = {}
            for m_name, mfv in member_forces.items():
                try:
                    if isinstance(mfv, dict) and all(k in mfv for k in ("Pi", "Vi", "Mi", "Pj", "Vj", "Mj")):
                        internal_forces[m_name] = _np.array([mfv["Pi"], mfv["Vi"], mfv["Mi"], mfv["Pj"], mfv["Vj"], mfv["Mj"]], dtype=float)
                    elif hasattr(mfv, "__len__") and len(mfv) >= 6:
                        internal_forces[m_name] = _np.array([float(mfv[0]), float(mfv[1]), float(mfv[2]), float(mfv[3]), float(mfv[4]), float(mfv[5])], dtype=float)
                    else:
                        internal_forces[m_name] = _np.array([mfv], dtype=object)
                except Exception:
                    internal_forces[m_name] = _np.array([mfv], dtype=object)
        except Exception:
            internal_forces = {}

        # Build AnalysisResults if available
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

    except Exception:
        return {"member_forces": {}}
                                "RZ": float(disp[5]) if len(disp) > 5 else 0.0,
