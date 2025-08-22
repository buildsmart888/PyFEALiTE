"""Integration tests that exercise the PyNite adapter when PyNite is installed.

These tests are skipped automatically if `pynite` cannot be imported.
"""
import importlib
import pytest


pytest.importorskip("PyNite", reason="PyNite not installed; skipping integration tests")

from pyfealite.plugins.pynite import adapter
from pyfealite.core.node import Node2D
from pyfealite.core.element import FrameElement2D
from pyfealite.core.structure import Structure


def test_adapter_runs_simple_model():
    # Build a tiny two-node single-element structure
    n1 = Node2D(0.0, 0.0, "N1")
    n2 = Node2D(1.0, 0.0, "N2")

    # Minimal cross-section stub
    class _CS:
        A = 1.0
        Iz = 1.0
        material = type("M", (), {"E": 200e9})

    elem = FrameElement2D(n1, n2, _CS(), "E1")

    s = Structure("test")
    s.add_node(n1, n2)
    s.add_element(elem)

    res = adapter.run_pynite_static(s, None)
    assert isinstance(res, dict)
    # New adapters return {'results': AnalysisResults, 'legacy': {...}}
    if "results" in res:
        ar = res["results"]
        # AnalysisResults should expose internal_forces as a dict (may be empty)
        assert hasattr(ar, "internal_forces")
        assert isinstance(ar.internal_forces, dict)
    else:
        # fallback legacy dict
        assert "summary" in res
        assert "member_forces" in res
