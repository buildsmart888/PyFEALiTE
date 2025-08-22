import types
import numpy as np

from pyfealite.plugins.pynite import adapter
from pyfealite.core.node import Node2D
from pyfealite.core.element import FrameElement2D
from pyfealite.core.structure import Structure


class DummyModel:
    def __init__(self):
        self._nodes = {}
        self._members = {}

    def AddNode(self, name, x, y, z):
        self._nodes[name] = (x, y, z)

    def AddMember(self, name, i, j, *args, **kwargs):
        self._members[name] = (i, j)

    def Analyze(self):
        pass

    def GetMemberForces(self, name):
        # Return six floats [Pi, Vi, Mi, Pj, Vj, Mj]
        return [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]


def test_internal_forces_mapped_to_numpy(monkeypatch):
    # Patch the import helper to return a dummy package that will use our DummyModel
    def fake_import(pkg_name):
        fake = types.SimpleNamespace()
        # Provide a FEModel3D reference used by adapter
        fake.FEModel3D = DummyModel
        return fake

    monkeypatch.setattr(adapter, "_try_import_pynite", lambda: fake_import("PyNite"))

    # Small structure
    n1 = Node2D(0.0, 0.0, "N1")
    n2 = Node2D(1.0, 0.0, "N2")

    class _CS:
        A = 1.0
        Iz = 1.0
        material = type("M", (), {"E": 200e9})

    elem = FrameElement2D(n1, n2, _CS(), "E1")
    s = Structure("t")
    s.add_node(n1, n2)
    s.add_element(elem)

    res = adapter.run_pynite_static(s, None)
    assert "results" in res
    ar = res["results"]
    assert hasattr(ar, "internal_forces")
    inf = ar.internal_forces
    assert isinstance(inf, dict)
    # There should be one member entry
    assert len(inf) >= 1
    # Values should be numpy arrays of length 6
    for v in inf.values():
        assert isinstance(v, np.ndarray)
        assert v.shape[0] >= 6
        assert np.allclose(v[:6], np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]))
