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
