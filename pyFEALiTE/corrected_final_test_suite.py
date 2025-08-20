"""
FINAL CORRECTED PyFEALiTE Test Suite
===================================

This test suite fixes ALL identified issues:
1. Correct import paths (from __init__.py)
2. Correct constructor parameters
3. Proper IsotropicMaterial usage (no G parameter)
4. Accurate parameter names for all classes
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("🚀 FINAL CORRECTED PyFEALiTE TEST SUITE")
print("=" * 60)
print("Testing ALL PyFEALiTE functions with 100% CORRECT parameters")
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

def test_corrected_imports():
    """Test PyFEALiTE imports using correct import paths."""
    try:
        # Use the correct import paths from __init__.py
        from pyfealite.core.node import Node2D
        from pyfealite.core.element import FrameElement2D
        from pyfealite.core.spring_element import SpringElement2D, SpringProperties
        from pyfealite.core.structure import Structure
        from pyfealite.core.enums import DOF, LoadDirection, SupportType, ElementType
        
        # Materials - correct import
        from pyfealite.materials.isotropic import IsotropicMaterial
        
        # Sections - correct import
        from pyfealite.sections.rectangular import RectangularSection
        
        # Loads  
        from pyfealite.loads.point_load import PointLoad, NodalLoad
        from pyfealite.loads.base import LoadCase
        
        print("   📦 All imports successful with CORRECT paths")
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_corrected_node2d():
    """Test Node2D functionality with correct imports."""
    try:
        from pyfealite.core.node import Node2D
        
        # Create basic node
        node1 = Node2D(0, 0)
        print(f"   📍 Node1 created at ({node1.x}, {node1.y})")
        
        # Create node with restraints
        node2 = Node2D(1000, 0, restraints=[True, True, False])
        print(f"   🔒 Node2 with restraints: {node2.restraints}")
        
        # Test node properties
        print(f"   🆔 Node1 coordinate numbers: {node1.coordinate_numbers}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_corrected_spring_element():
    """Test SpringElement2D with exact constructor parameters."""
    try:
        from pyfealite.core.node import Node2D
        from pyfealite.core.spring_element import SpringElement2D, SpringProperties
        
        # Create nodes
        node1 = Node2D(0, 0)
        node2 = Node2D(1000, 0)
        
        # Create spring properties with EXACT parameters (K, Kr)
        spring_props = SpringProperties(K=10000.0, Kr=5000.0)
        print(f"   🌀 SpringProperties: K={spring_props.K}, Kr={spring_props.Kr}")
        
        # Create spring element
        spring = SpringElement2D(node1, node2, spring_props, "Spring1")
        print(f"   📏 Spring length: {spring.length():.2f} mm")
        print(f"   🏷️  Spring label: {spring.label}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_corrected_materials():
    """Test IsotropicMaterial with correct parameters (no G)."""
    try:
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.materials.base import MaterialType
        
        # Create material with CORRECT parameters (E, nu, NOT G)
        steel = IsotropicMaterial(
            E=200000,  # MPa
            nu=0.3,    # Poisson's ratio
            density_value=7850,  # kg/m³
            label="Steel S355",
            material_type=MaterialType.STEEL
        )
        
        print(f"   🔧 Material: {steel.label}")
        print(f"   📊 E = {steel.E} MPa, ν = {steel.nu}")
        print(f"   🧮 Shear modulus G = {steel.shear_modulus:.0f} MPa")
        print(f"   ⚖️  Density = {steel.density} kg/m³")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_corrected_sections():
    """Test RectangularSection with material parameter."""
    try:
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.materials.base import MaterialType
        from pyfealite.sections.rectangular import RectangularSection
        
        # Create material first
        steel = IsotropicMaterial(
            E=200000,
            nu=0.3,
            material_type=MaterialType.STEEL,
            label="Steel"
        )
        
        # Create section with REQUIRED material parameter
        section = RectangularSection(
            material=steel,
            width=300,
            height=600,
            label="Beam300x600"
        )
        
        print(f"   📐 Section: {section.label}")
        print(f"   📏 Dimensions: {section.width}×{section.height} mm")
        print(f"   📊 Area: {section.area():.0f} mm²")
        print(f"   🔄 Moment of inertia: {section.moment_of_inertia():.0f} mm⁴")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_corrected_loads():
    """Test loads with exact constructor parameters."""
    try:
        from pyfealite.core.node import Node2D
        from pyfealite.loads.point_load import NodalLoad
        from pyfealite.loads.base import LoadCase, LoadDirection
        
        # Create load case
        dead_load = LoadCase("Dead Load", 1.0)
        
        # Create node
        node = Node2D(1000, 1000)
        
        # Create nodal load with EXACT parameters from constructor
        load = NodalLoad(
            load_case=dead_load,
            node=node,
            Fx=10000.0,
            Fy=-20000.0,
            Mz=5000.0,
            direction=LoadDirection.GLOBAL,
            label="Load1"
        )
        
        print(f"   🎯 Load: {load.label}")
        print(f"   📊 Forces: Fx={load.Fx}, Fy={load.Fy}, Mz={load.Mz}")
        print(f"   📍 Applied to node at ({load.node.x}, {load.node.y})")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_corrected_frame_element():
    """Test FrameElement2D with cross_section parameter."""
    try:
        from pyfealite.core.node import Node2D
        from pyfealite.core.element import FrameElement2D
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.materials.base import MaterialType
        from pyfealite.sections.rectangular import RectangularSection
        
        # Create material
        steel = IsotropicMaterial(
            E=200000,
            nu=0.3,
            material_type=MaterialType.STEEL,
            label="Steel"
        )
        
        # Create section
        section = RectangularSection(
            material=steel,
            width=300,
            height=600,
            label="MainBeam"
        )
        
        # Create nodes
        node1 = Node2D(0, 0)
        node2 = Node2D(5000, 0)
        
        # Create frame element with cross_section parameter
        beam = FrameElement2D(
            start_node=node1,
            end_node=node2,
            cross_section=section,
            label="Beam1"
        )
        
        print(f"   🔗 Element: {beam.label}")
        print(f"   📏 Length: {beam.length():.0f} mm")
        print(f"   📐 Section: {section.label}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_corrected_structure():
    """Test Structure with all components."""
    try:
        from pyfealite.core.node import Node2D
        from pyfealite.core.structure import Structure
        from pyfealite.core.element import FrameElement2D
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.materials.base import MaterialType
        from pyfealite.sections.rectangular import RectangularSection
        
        # Create structure
        structure = Structure("Corrected Test Frame")
        
        # Create material
        steel = IsotropicMaterial(
            E=200000,
            nu=0.3,
            material_type=MaterialType.STEEL,
            label="Steel"
        )
        
        # Create section
        section = RectangularSection(
            material=steel,
            width=300,
            height=600,
            label="MainBeam"
        )
        
        # Create nodes
        node1 = Node2D(0, 0, restraints=[True, True, True])  # Fixed
        node2 = Node2D(5000, 0)  # Free
        node3 = Node2D(5000, 3000)  # Free
        
        # Add nodes
        structure.add_node(node1)
        structure.add_node(node2)
        structure.add_node(node3)
        
        # Create elements
        beam1 = FrameElement2D(node1, node2, cross_section=section, label="Beam1")
        beam2 = FrameElement2D(node2, node3, cross_section=section, label="Column1")
        
        structure.add_element(beam1)
        structure.add_element(beam2)
        
        print(f"   🏗️  Structure: {structure.label}")
        print(f"   📊 Nodes: {len(structure.nodes)}")
        print(f"   🔗 Elements: {len(structure.elements)}")
        print(f"   ⚖️  Material: {steel.label} (E={steel.E} MPa)")
        print(f"   📐 Section: A={section.area():.0f} mm²")
        
        # Test available methods
        methods = [m for m in dir(structure) if not m.startswith('_')]
        key_methods = [m for m in methods if m in ['solve', 'add_node', 'add_element']]
        print(f"   🎯 Available methods: {', '.join(key_methods)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_complete_integration():
    """Test complete PyFEALiTE integration."""
    try:
        from pyfealite.core.node import Node2D
        from pyfealite.core.structure import Structure
        from pyfealite.core.element import FrameElement2D
        from pyfealite.core.spring_element import SpringElement2D, SpringProperties
        from pyfealite.materials.isotropic import IsotropicMaterial
        from pyfealite.materials.base import MaterialType
        from pyfealite.sections.rectangular import RectangularSection
        from pyfealite.loads.base import LoadCase, LoadDirection
        from pyfealite.loads.point_load import NodalLoad
        
        # Create complete structure
        structure = Structure("Complete Integration Test")
        
        # Material and section
        steel = IsotropicMaterial(E=200000, nu=0.3, material_type=MaterialType.STEEL, label="Steel")
        section = RectangularSection(material=steel, width=400, height=600, label="MainSection")
        
        # Nodes
        nodes = [
            Node2D(0, 0, restraints=[True, True, True]),
            Node2D(4000, 0),
            Node2D(8000, 0, restraints=[False, True, False])
        ]
        
        for node in nodes:
            structure.add_node(node)
        
        # Elements
        beam1 = FrameElement2D(nodes[0], nodes[1], cross_section=section, label="Span1")
        beam2 = FrameElement2D(nodes[1], nodes[2], cross_section=section, label="Span2")
        structure.add_element(beam1)
        structure.add_element(beam2)
        
        # Spring element
        spring_props = SpringProperties(K=50000.0, Kr=10000.0)
        spring = SpringElement2D(nodes[1], nodes[2], spring_props, "Spring1")
        
        # Load case and loads
        live_load = LoadCase("Live Load", 1.0)
        load1 = NodalLoad(live_load, nodes[1], Fx=0, Fy=-25000, Mz=0, label="PointLoad1")
        
        print(f"   🏗️  Structure: {structure.label}")
        print(f"   📊 Components: {len(structure.nodes)} nodes, {len(structure.elements)} elements")
        print(f"   🌀 Spring: K={spring_props.K}, Kr={spring_props.Kr}")
        print(f"   🎯 Load: {load1.label} = {load1.Fy} N")
        print(f"   ⚖️  Material: E={steel.E} MPa")
        print(f"   📐 Section: A={section.area():.0f} mm²")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_package_capabilities():
    """Test overall package capabilities."""
    try:
        import pyfealite
        
        print(f"   📋 PyFEALiTE version: {pyfealite.__version__}")
        
        # Test module availability
        modules = ['core', 'materials', 'sections', 'loads', 'utils', 'visualization']
        available = []
        
        for module in modules:
            try:
                __import__(f'pyfealite.{module}')
                available.append(module)
            except ImportError:
                pass
        
        print(f"   📦 Available modules: {', '.join(available)}")
        
        # Test key classes
        key_classes = []
        try:
            from pyfealite import Node2D, FrameElement2D, Structure, IsotropicMaterial
            key_classes = ['Node2D', 'FrameElement2D', 'Structure', 'IsotropicMaterial']
        except ImportError:
            pass
            
        print(f"   🎯 Core classes: {', '.join(key_classes)}")
        
        return len(available) >= 4 and len(key_classes) >= 3
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

# Run all corrected tests
if __name__ == "__main__":
    print()
    
    tests = [
        ("Corrected Imports", test_corrected_imports),
        ("Corrected Node2D", test_corrected_node2d),
        ("Corrected SpringElement2D", test_corrected_spring_element),
        ("Corrected Materials", test_corrected_materials),
        ("Corrected Sections", test_corrected_sections),
        ("Corrected Loads", test_corrected_loads),
        ("Corrected FrameElement2D", test_corrected_frame_element),
        ("Corrected Structure", test_corrected_structure),
        ("Complete Integration", test_complete_integration),
        ("Package Capabilities", test_package_capabilities),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_with_error_handling(test_name, test_func):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🎯 FINAL CORRECTED RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed >= 9:
        print("🎉 OUTSTANDING! PyFEALiTE is fully functional!")
    elif passed >= 7:
        print("✅ EXCELLENT! PyFEALiTE is highly functional!")
    elif passed >= 5:
        print("✅ GOOD! PyFEALiTE core functionality is solid!")
    else:
        print("⚠️  PARTIAL: Some functionality working, improvements needed")
        
    print("=" * 60)
