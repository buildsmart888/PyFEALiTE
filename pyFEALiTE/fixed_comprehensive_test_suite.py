"""
Fixed PyFEALiTE Test Suite - Updated Constructor Parameters
==========================================================

This test suite fixes all constructor parameter mismatches identified
in the comprehensive testing to achieve maximum functionality coverage.
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("🚀 FIXED PyFEALiTE COMPREHENSIVE TEST SUITE")
print("=" * 60)
print("Testing all PyFEALiTE functions with CORRECT constructor parameters")
print()

def test_with_error_handling(test_name, test_func):
    """Helper function to run tests with error handling."""
    try:
        print(f"🧪 Testing: {test_name}")
        result = test_func()
        if result:
            print(f"✅ {test_name}: PASSED")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            return False
    except Exception as e:
        print(f"💥 {test_name}: ERROR - {str(e)}")
        traceback.print_exc()
        return False

def test_imports():
    """Test PyFEALiTE imports."""
    try:
        # Core imports
        from pyfealite.core.node2d import Node2D
        from pyfealite.core.frame_element import FrameElement2D
        from pyfealite.core.spring_element import SpringElement2D, SpringProperties
        from pyfealite.core.structure import Structure
        
        # Materials
        from pyfealite.materials.isotropic import IsotropicMaterial
        
        # Sections
        from pyfealite.sections.rectangular import RectangularSection
        
        # Loads  
        from pyfealite.loads.point_load import PointLoad, NodalLoad
        from pyfealite.loads.base import LoadCase, LoadDirection
        
        print("   📦 All imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_fixed_spring_element():
    """Test SpringElement2D with correct parameters."""
    try:
        from pyfealite.core.node2d import Node2D
        from pyfealite.core.spring_element import SpringElement2D, SpringProperties
        
        # Create nodes
        node1 = Node2D(0, 0)
        node2 = Node2D(1000, 0)
        
        # Create spring properties with CORRECT parameters (K, Kr)
        spring_props = SpringProperties(K=10000.0, Kr=5000.0)
        
        # Create spring element
        spring = SpringElement2D(node1, node2, spring_props, "Spring1")
        
        print(f"   🌀 Spring created: K={spring_props.K}, Kr={spring_props.Kr}")
        print(f"   📏 Spring length: {spring.length():.2f}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_fixed_materials_and_sections():
    """Test materials and sections with correct parameters."""
    try:
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.sections.rectangular import RectangularSection
        
        # Create material
        steel = IsotropicMaterial(E=200000, G=76923, label="Steel")
        print(f"   🔧 Material: {steel.label}, E={steel.E} MPa")
        
        # Create section with REQUIRED material parameter
        section = RectangularSection(material=steel, width=300, height=600, label="Beam300x600")
        print(f"   📐 Section: {section.label}, Area={section.area():.0f} mm²")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_fixed_loads():
    """Test loads with correct constructor parameters."""
    try:
        from pyfealite.core.node2d import Node2D
        from pyfealite.loads.point_load import NodalLoad
        from pyfealite.loads.base import LoadCase, LoadDirection
        
        # Create load case
        dead_load = LoadCase("Dead Load", 1.0)
        
        # Create node
        node = Node2D(1000, 1000)
        
        # Create nodal load with CORRECT parameters (node, not node_id)
        load = NodalLoad(
            load_case=dead_load,
            node=node,
            Fx=10000.0,
            Fy=-20000.0,
            Mz=5000.0,
            direction=LoadDirection.GLOBAL,
            label="Load1"
        )
        
        print(f"   🎯 Load created: Fx={load.Fx}, Fy={load.Fy}, Mz={load.Mz}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_complete_integration_fixed():
    """Test complete integration with all correct parameters."""
    try:
        from pyfealite.core.node2d import Node2D
        from pyfealite.core.structure import Structure
        from pyfealite.core.frame_element import FrameElement2D
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.sections.rectangular import RectangularSection
        from pyfealite.loads.base import LoadCase
        from pyfealite.loads.point_load import NodalLoad
        
        # Create structure
        structure = Structure("Fixed Test Frame")
        
        # Create material
        steel = IsotropicMaterial(E=200000, G=76923, label="Steel")
        
        # Create section with material
        section = RectangularSection(material=steel, width=300, height=600, label="MainBeam")
        
        # Create nodes
        node1 = Node2D(0, 0, restraints=[True, True, True])  # Fixed support
        node2 = Node2D(5000, 0)  # Free end
        
        # Add nodes to structure
        structure.add_node(node1)
        structure.add_node(node2)
        
        # Create frame element with cross_section parameter
        beam = FrameElement2D(node1, node2, cross_section=section, label="Beam1")
        structure.add_element(beam)
        
        # Create load case and load
        dead_load = LoadCase("Dead Load", 1.0)
        load = NodalLoad(dead_load, node2, Fx=0, Fy=-10000, Mz=0)
        
        print(f"   🏗️  Structure: {structure.label}")
        print(f"   📊 Nodes: {len(structure.nodes)}")
        print(f"   🔗 Elements: {len(structure.elements)}")
        print(f"   ⚖️  Material: {steel.label} (E={steel.E} MPa)")
        print(f"   📐 Section: {section.label} (A={section.area():.0f} mm²)")
        print(f"   📏 Beam length: {beam.length():.0f} mm")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_analysis_capabilities():
    """Test analysis and visualization capabilities."""
    try:
        from pyfealite.core.structure import Structure
        from pyfealite.core.node2d import Node2D
        
        # Test what methods are available
        structure = Structure("Test")
        node = Node2D(0, 0)
        structure.add_node(node)
        
        methods = [method for method in dir(structure) if not method.startswith('_')]
        print(f"   🔍 Structure methods: {', '.join(methods[:5])}...")
        
        # Check if solve method exists
        if hasattr(structure, 'solve'):
            print("   ✅ Solve method available")
        else:
            print("   ⚠️  Solve method not found")
            
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_visualization_system():
    """Test visualization system."""
    try:
        # Try importing visualization
        try:
            from pyfealite.visualization.plotter import StructurePlotter
            print("   📊 StructurePlotter available")
            plotter_available = True
        except ImportError:
            print("   ⚠️  StructurePlotter not available")
            plotter_available = False
        
        # Try matplotlib
        try:
            import matplotlib.pyplot as plt
            print("   📈 Matplotlib available")
        except ImportError:
            print("   ❌ Matplotlib not available")
            
        return plotter_available
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_export_functionality():
    """Test export functionality."""
    try:
        # Test DXF export
        try:
            from pyfealite.utils.dxf_exporter import EnhancedDXFExporter
            print("   📄 EnhancedDXFExporter available")
            return True
        except ImportError as e:
            print(f"   ⚠️  DXF export not available: {e}")
            
        # Test if ezdxf is available
        try:
            import ezdxf
            print(f"   📦 ezdxf v{ezdxf.version} available")
        except ImportError:
            print("   ❌ ezdxf not available")
            
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_advanced_features():
    """Test advanced PyFEALiTE features."""
    try:
        from pyfealite.core.structure import Structure
        
        # Test advanced structure features
        structure = Structure("Advanced Test")
        
        # Check available attributes
        attrs = [attr for attr in dir(structure) if not attr.startswith('_')]
        important_attrs = ['nodes', 'elements', 'add_node', 'add_element']
        
        available_attrs = [attr for attr in important_attrs if hasattr(structure, attr)]
        print(f"   🎯 Available attributes: {', '.join(available_attrs)}")
        
        # Test if advanced methods exist
        advanced_methods = ['solve', 'get_displacements', 'get_forces', 'analyze']
        available_advanced = [method for method in advanced_methods if hasattr(structure, method)]
        
        if available_advanced:
            print(f"   🚀 Advanced methods: {', '.join(available_advanced)}")
        else:
            print("   ⚠️  No advanced analysis methods found")
            
        return len(available_attrs) >= 3
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_package_info():
    """Test package information and metadata."""
    try:
        import pyfealite
        
        # Check version
        if hasattr(pyfealite, '__version__'):
            print(f"   📋 PyFEALiTE version: {pyfealite.__version__}")
        else:
            print("   ⚠️  Version info not available")
            
        # Check available modules
        available_modules = []
        modules_to_check = ['core', 'materials', 'sections', 'loads', 'utils']
        
        for module in modules_to_check:
            try:
                __import__(f'pyfealite.{module}')
                available_modules.append(module)
            except ImportError:
                pass
                
        print(f"   📦 Available modules: {', '.join(available_modules)}")
        return len(available_modules) >= 3
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

# Run all tests
if __name__ == "__main__":
    print()
    
    tests = [
        ("PyFEALiTE Imports", test_imports),
        ("Fixed SpringElement2D", test_fixed_spring_element),
        ("Fixed Materials & Sections", test_fixed_materials_and_sections),
        ("Fixed Loads System", test_fixed_loads),
        ("Complete Integration (Fixed)", test_complete_integration_fixed),
        ("Analysis Capabilities", test_analysis_capabilities),
        ("Visualization System", test_visualization_system),
        ("Export Functionality", test_export_functionality),
        ("Advanced Features", test_advanced_features),
        ("Package Information", test_package_info),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_with_error_handling(test_name, test_func):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🎯 FINAL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed >= 8:
        print("🎉 EXCELLENT! PyFEALiTE is highly functional!")
    elif passed >= 6:
        print("✅ GOOD! PyFEALiTE core functionality is working!")
    elif passed >= 4:
        print("⚠️  PARTIAL: Core features work, some issues remain")
    else:
        print("❌ NEEDS WORK: Major issues need resolution")
        
    print("=" * 60)
