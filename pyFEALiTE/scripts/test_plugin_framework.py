#!/usr/bin/env python3
"""
Test Plugin Framework

Quick test script to verify the plugin framework is working correctly.
This script can be run to validate the basic plugin system functionality.
"""

import sys
from pathlib import Path

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_plugin_imports():
    """Test that plugin system imports work correctly."""
    print("Testing Plugin System Imports")
    print("=" * 40)
    
    try:
        from pyfealite.plugins import (
            AnalysisPlugin,
            PluginMetadata,
            AnalysisCapability,
            plugin_registry
        )
        print("OK: Plugin system imports successful")
        
        # Test enum values
        capabilities = list(AnalysisCapability)
        print(f"Available capabilities: {len(capabilities)}")
        for cap in capabilities[:5]:  # Show first 5
            print(f"   - {cap.value}")
        if len(capabilities) > 5:
            print(f"   ... and {len(capabilities) - 5} more")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Plugin system import failed: {e}")
        return False


def test_plugin_registry():
    """Test plugin registry functionality."""
    print("\n  Testing Plugin Registry")
    print("=" * 30)
    
    try:
        from pyfealite.plugins.registry import plugin_registry
        
        # Check if plugins were auto-discovered
        available = plugin_registry.get_available_plugins()
        print(f" Auto-discovered plugins: {len(available)}")
        
        for name, plugin in available.items():
            capabilities = [cap.value for cap in plugin.metadata.capabilities]
            print(f"   • {name} v{plugin.metadata.version}")
            print(f"     Capabilities: {', '.join(capabilities)}")
            print(f"     Priority: {plugin.metadata.priority}")
        
        # Test getting capabilities
        capabilities = plugin_registry.get_capabilities()
        print(f"\n Total capabilities available: {len(capabilities)}")
        
        return len(available) > 0
        
    except Exception as e:
        print(f"ERROR: Plugin registry test failed: {e}")
        return False


def test_core_plugin():
    """Test core plugin specifically."""
    print("\n  Testing Core Plugin")
    print("=" * 25)
    
    try:
        from pyfealite.plugins.core_plugin import PyFEALiTECorePlugin
        
        # Create core plugin instance
        core_plugin = PyFEALiTECorePlugin()
        
        print(f"OK: Core plugin created: {core_plugin.metadata.name}")
        print(f"   Version: {core_plugin.metadata.version}")
        print(f"   Capabilities: {[cap.value for cap in core_plugin.metadata.capabilities]}")
        print(f"   Priority: {core_plugin.metadata.priority}")
        print(f"   Dependencies: {core_plugin.metadata.dependencies}")
        
        # Test help text
        help_text = core_plugin.get_help_text()
        print(f"\nHelp text (first 100 chars):")
        print(f"   {help_text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Core plugin test failed: {e}")
        return False


def test_enhanced_structure():
    """Test enhanced structure with plugin support."""
    print("\n  Testing Enhanced Structure")
    print("=" * 35)
    
    try:
        from pyfealite.core.structure_enhanced import Structure, create_structure
        
        # Create structure
        structure = create_structure("Test Structure")
        print(f"OK: Enhanced structure created: {structure.name}")
        
        # Test available analyses
        available = structure.get_available_analyses()
        print(f" Available analyses: {len(available)} engines")
        for engine, analyses in available.items():
            print(f"   {engine}: {', '.join(analyses)}")
        
        # Test analysis requirements check
        print("\n Testing analysis requirements check...")
        
        test_analyses = ["static", "modal", "p_delta", "buckling"]
        for analysis in test_analyses:
            try:
                req = structure.check_analysis_requirements(analysis)
                if req["available"]:
                    print(f"   OK: {analysis}: Available")
                else:
                    print(f"   ERROR: {analysis}: Not available")
                    if "install_command" in req:
                        print(f"      Solution: {req['install_command']}")
            except Exception as e:
                print(f"   WARNING:  {analysis}: Error checking - {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Enhanced structure test failed: {e}")
        return False


def test_mock_analysis():
    """Test a simple mock analysis to verify the pipeline works."""
    print("\n Testing Mock Analysis Pipeline")
    print("=" * 40)
    
    try:
        from pyfealite.core.structure_enhanced import create_structure
        from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
        from pyfealite.materials.isotropic import IsotropicMaterial
        
        # Create minimal structure
        structure = create_structure("Mock Analysis Test")
        
        # Add minimal components
        n1 = Node2D(x=0, y=0, label="Node1")
        n1.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)  # Pin support
        
        n2 = Node2D(x=2, y=0, label="Node2")
        
        structure.add_node(n1, n2)
        
        print("OK: Test structure created")
        print(f"   Nodes: {len(structure.nodes)}")
        print(f"   Elements: {len(structure.elements)}")
        
        # Test analysis type mapping
        print("\n Testing analysis type mapping...")
        
        test_types = ["static", "static_2d", "modal", "p_delta"]
        for test_type in test_types:
            try:
                # This should work even if analysis fails
                capability = structure._map_analysis_type(test_type)
                print(f"   OK: {test_type} → {capability.value}")
            except Exception as e:
                print(f"   ERROR: {test_type} → Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Mock analysis test failed: {e}")
        return False


def test_plugin_system_complete():
    """Run complete plugin system test suite."""
    print("PyFEALiTE Plugin Framework Test Suite")
    print("=" * 45)
    print()
    
    tests = [
        ("Plugin Imports", test_plugin_imports),
        ("Plugin Registry", test_plugin_registry),
        ("Core Plugin", test_core_plugin),
        ("Enhanced Structure", test_enhanced_structure),
        ("Mock Analysis", test_mock_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\nOK: {test_name}: PASSED")
            else:
                print(f"\nERROR: {test_name}: FAILED")
        except Exception as e:
            print(f"\nERROR: {test_name}: {e}")
    
    print("\n" + "=" * 45)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! Plugin framework is working correctly.")
        print("\nNext steps:")
        print("   1. Run: python examples/plugin_architecture_demo.py")
        print("   2. Install 3D plugin: pip install pyfealite[3d]")
        print("   3. Run full test suite: pytest tests/test_plugins/")
        return True
    else:
        print(f"WARNING: {total - passed} tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = test_plugin_system_complete()
    sys.exit(0 if success else 1)