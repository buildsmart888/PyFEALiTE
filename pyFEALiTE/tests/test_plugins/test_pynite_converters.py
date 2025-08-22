"""Unit tests for PyNite plugin converters (don't require PyNite).

Covers node, element, dist-load conversion and springs.
"""
import pytest

from pyfealite.plugins.pynite import converters


class DummyNode:
    def __init__(self, label, x, y):
        self.label = label
        self.x = x
        self.y = y


class DummyElement:
    def __init__(self, label, start, end, A=None, Iz=None, E=None, length=None):
        self.label = label
        self.start_node = start
        self.end_node = end
        class CS:
            pass
        if A is not None or Iz is not None or E is not None:
            cs = CS()
            cs.A = A
            cs.Iz = Iz
            class Mat:
                pass
            cs.material = Mat()
            cs.material.E = E
            self.cross_section = cs
        if length is not None:
            self.length = length


class DummySpring:
    def __init__(self, node_label, kx=0.0, ky=0.0, kr=0.0):
        self.node = type("N", (), {"label": node_label})()
        self.k_axial = kx
        self.k_shear = ky
        self.k_rot = kr


def test_node_conversion():
    n = DummyNode("N1", 0.0, 2.0)
    d = converters.node_pyfealite_to_pynite(n)
    assert d["name"] == "N1"
    assert d["x"] == 0.0
    assert d["y"] == 2.0


def test_element_conversion():
    n1 = DummyNode("N1", 0.0, 0.0)
    n2 = DummyNode("N2", 3.0, 0.0)
    el = DummyElement("E1", n1, n2, A=0.01, Iz=1e-6, E=210e9)
    d = converters.element_pyfealite_to_pynite(el)
    assert d["node_i"] == "N1"
    assert d["node_j"] == "N2"
    assert abs(d["A"] - 0.01) < 1e-12
    assert abs(d["E"] - 210e9) < 1e-6


def test_dist_load_equivalents_vertical():
    n1 = DummyNode("N1", 0.0, 0.0)
    n2 = DummyNode("N2", 4.0, 0.0)
    el = DummyElement("E1", n1, n2, length=4.0)
    res = converters.dist_load_to_nodal_equivalents(el, w=2.0, direction="vertical")
    # total vertical load = wL = 8N -> half each
    assert abs(res["node_i_load"][1] - 4.0) < 1e-12
    assert abs(res["node_j_load"][1] - 4.0) < 1e-12


def test_spring_conversion():
    s = DummySpring("N1", kx=1000.0, ky=2000.0, kr=300.0)
    res = converters.spring_to_pynite(s)
    assert res["node"] == "N1"
    assert res["k_axial"] == 1000.0
    assert res["k_shear"] == 2000.0
    assert res["k_rot"] == 300.0


if __name__ == "__main__":
    pytest.main([__file__])
