"""Basic tests for PyNite plugin skeleton.

These are minimal smoke tests to validate module imports and basic API
existence. Implement full unit tests after converter/adapter logic is added.
"""
import importlib


def test_import_pynite_plugin():
    mod = importlib.import_module("pyfealite.plugins.pynite")
    assert hasattr(mod, "converters")
    assert hasattr(mod, "adapter")


def test_run_pynite_static_callable():
    adapter = importlib.import_module("pyfealite.plugins.pynite.adapter")
    assert hasattr(adapter, "run_pynite_static")


def test_run_pynite_raises_when_missing():
    """If PyNite isn't installed, the adapter should raise PyNiteNotAvailable."""
    adapter = importlib.import_module("pyfealite.plugins.pynite.adapter")
    PyNiteNotAvailable = getattr(adapter, "PyNiteNotAvailable")

    class DummyStruct:
        nodes = []
        elements = []

    try:
        adapter.run_pynite_static(DummyStruct(), None)
    except Exception as e:
        assert isinstance(e, PyNiteNotAvailable)
    else:
        # If no exception, that's acceptable only if the adapter implements
        # the run path; in that case ensure the return shape is as expected.
        res = adapter.run_pynite_static(DummyStruct(), None)
        assert isinstance(res, dict)
        assert "summary" in res
