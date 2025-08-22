#!/usr/bin/env python3
"""
PyFEALiTE Plugin Architecture Demo

This example demonstrates the new plugin-based architecture in PyFEALiTE v2.0,
showing how the system automatically selects appropriate engines for analysis.

Features demonstrated:
- Automatic plugin discovery
- 2D vs 3D analysis detection
- Plugin capability checking
- Unified analysis interface
- Error handling and suggestions
"""

import numpy as np
from pathlib import Path
import sys

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pyfealite.core.structure_enhanced import Structure, create_structure
    from pyfealite.core.node import Node2D
    from pyfealite.core.element import FrameElement2D
    from pyfealite.materials.isotropic import IsotropicMaterial
    from pyfealite.sections.rectangular import RectangularSection
    from pyfealite.loads.base import LoadCase
    from pyfealite.loads.point_load import PointLoad
    from pyfealite.plugins.registry import plugin_registry
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the PyFEALiTE root directory")
    sys.exit(1)


def demo_plugin_discovery():
    """Demonstrate plugin discovery and capabilities."""
    
    print("🔌 Plugin Architecture Demo")
    print("=" * 50)
    
    # Show available plugins
    available_plugins = plugin_registry.get_available_plugins()
    print(f"📦 Available Plugins ({len(available_plugins)}):")
    
    for name, plugin in available_plugins.items():
        capabilities = [cap.value for cap in plugin.metadata.capabilities]
        print(f"  • {name} v{plugin.metadata.version}")
        print(f"    Capabilities: {', '.join(capabilities)}")
        print(f"    Priority: {plugin.metadata.priority}")
        print()
    
    # Show available analysis types
    capabilities = plugin_registry.get_capabilities()
    print(f"🎯 Available Analysis Types ({len(capabilities)}):")
    for cap in capabilities:
        print(f"  • {cap.value}")
    print()


def demo_2d_analysis():
    """Demonstrate 2D analysis with automatic core plugin selection."""
    
    print("📐 2D Analysis Demo")
    print("=" * 30)
    
    # Create simple 2D frame
    structure = create_structure("2D Frame Example")
    
    # Create nodes
    n1 = Node2D(x=0, y=0, label="Support A")
    n1.restrain("UX", "UY")  # Pin support
    
    n2 = Node2D(x=4, y=0, label="Support B") 
    n2.restrain("UY")  # Roller support
    
    n3 = Node2D(x=2, y=3, label="Apex")
    
    structure.add_node(n1, n2, n3)
    
    # Create elements
    steel = IsotropicMaterial.steel()
    section = RectangularSection(steel, width=0.3, height=0.5)
    
    beam1 = FrameElement2D(n1, n3, section, label="Left Rafter")
    beam2 = FrameElement2D(n3, n2, section, label="Right Rafter")
    
    structure.add_element(beam1, beam2)
    
    # Add loads
    load_case = LoadCase("Snow Load")
    point_load = PointLoad(load_case, Fx=0, Fy=-25, distance=1.5)  # 25 kN down
    beam1.loads = [point_load]
    
    structure.add_load_case(load_case)
    
    print(f"🏗️  Created structure: {structure.name}")
    print(f"   Nodes: {len(structure.nodes)}")
    print(f"   Elements: {len(structure.elements)}")
    print(f"   Load cases: {len(structure.load_cases)}")
    print()
    
    # Check what analyses are available
    print("🔍 Checking available analyses...")
    available = structure.get_available_analyses()
    for engine, analyses in available.items():
        print(f"  {engine}: {', '.join(analyses)}")
    print()
    
    # Perform static analysis
    print("🧮 Performing static analysis...")
    try:
        results = structure.solve("static")
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Engine used: {results.engine}")
        print(f"   Analysis type: {results.analysis_type}")
        
        # Show some results
        if hasattr(results, 'displacements') and results.displacements:
            max_disp = 0
            for disp_array in results.displacements.values():
                max_disp = max(max_disp, np.max(np.abs(disp_array)))
            print(f"   Max displacement: {max_disp:.4f} m")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    print()


def demo_3d_capability_check():
    """Demonstrate 3D capability checking and helpful error messages."""
    
    print("🌐 3D Capability Check Demo")
    print("=" * 35)
    
    structure = create_structure("3D Frame Example")
    
    # Create a simple frame that could benefit from 3D analysis
    n1 = Node2D(x=0, y=0, label="Base")
    n1.restrain("UX", "UY", "RZ")
    
    n2 = Node2D(x=0, y=3, label="Top")
    
    structure.add_node(n1, n2)
    
    steel = IsotropicMaterial.steel()
    section = RectangularSection(steel, width=0.4, height=0.4)
    column = FrameElement2D(n1, n2, section, label="Column")
    
    structure.add_element(column)
    
    # Check P-Δ analysis capability
    print("🔍 Checking P-Δ analysis capability...")
    requirements = structure.check_analysis_requirements("p_delta")
    
    if requirements["available"]:
        print(f"✅ P-Δ analysis available!")
        print(f"   Engines: {', '.join(requirements['engines'])}")
        print(f"   Recommended: {requirements['recommended']}")
    else:
        print("❌ P-Δ analysis not available")
        if "install_command" in requirements:
            print(f"   Solution: {requirements['install_command']}")
        if "issues" in requirements:
            print("   Issues:")
            for issue in requirements["issues"]:
                print(f"     • {issue}")
    
    print()
    
    # Check buckling analysis
    print("🔍 Checking buckling analysis capability...")
    buckling_req = structure.check_analysis_requirements("buckling")
    
    if buckling_req["available"]:
        print("✅ Buckling analysis available!")
    else:
        print("❌ Buckling analysis not available")
        if "install_command" in buckling_req:
            print(f"   Solution: {buckling_req['install_command']}")
    
    print()


def demo_analysis_validation():
    """Demonstrate structure validation for different analysis types."""
    
    print("🔍 Analysis Validation Demo")
    print("=" * 35)
    
    structure = create_structure("Validation Example")
    
    # Create structure with potential 3D characteristics
    n1 = Node2D(x=0, y=0, label="Base")
    n1.restrain("UX", "UY")
    
    n2 = Node2D(x=4, y=0, label="End")
    
    structure.add_node(n1, n2)
    
    steel = IsotropicMaterial.steel()
    section = RectangularSection(steel, width=0.3, height=0.5)
    beam = FrameElement2D(n1, n2, section, label="Beam")
    
    structure.add_element(beam)
    
    # Test validation for different analysis types
    analysis_types = ["static", "modal", "p_delta", "buckling"]
    
    for analysis_type in analysis_types:
        print(f"🔍 Validating for {analysis_type} analysis...")
        
        issues = structure.validate_for_analysis(analysis_type)
        
        if not issues:
            print(f"✅ Structure valid for {analysis_type} analysis")
        else:
            print(f"⚠️  Validation issues for {analysis_type}:")
            for issue in issues:
                print(f"     • {issue}")
        print()


def demo_convenience_methods():
    """Demonstrate convenience analysis methods."""
    
    print("🎯 Convenience Methods Demo")
    print("=" * 35)
    
    # Create simple cantilever beam
    structure = create_structure("Cantilever Beam")
    
    n1 = Node2D(x=0, y=0, label="Fixed")
    n1.restrain("UX", "UY", "RZ")  # Fixed support
    
    n2 = Node2D(x=3, y=0, label="Free")
    
    structure.add_node(n1, n2)
    
    steel = IsotropicMaterial.steel()
    section = RectangularSection(steel, width=0.2, height=0.4)
    beam = FrameElement2D(n1, n2, section, label="Cantilever")
    
    structure.add_element(beam)
    
    # Add tip load
    load_case = LoadCase("Point Load")
    tip_load = PointLoad(load_case, Fx=0, Fy=-10, distance=3.0)
    beam.loads = [tip_load]
    
    structure.add_load_case(load_case)
    
    print(f"🏗️  Created cantilever beam structure")
    print()
    
    # Try convenience methods
    print("🧮 Testing convenience methods...")
    
    try:
        # Static analysis
        static_results = structure.static_analysis()
        print(f"✅ Static analysis: {static_results.engine}")
        
    except Exception as e:
        print(f"❌ Static analysis failed: {e}")
    
    # Modal analysis would require material density
    print("⚠️  Modal analysis requires material density (not set in this example)")
    
    # P-Δ analysis (will likely fail without 3D plugin)
    try:
        p_delta_results = structure.p_delta_analysis()
        print(f"✅ P-Δ analysis: {p_delta_results.engine}")
    except Exception as e:
        print(f"❌ P-Δ analysis not available: {e}")
    
    print()


def demo_plugin_info():
    """Demonstrate getting detailed plugin information."""
    
    print("📊 Plugin Information Demo")
    print("=" * 35)
    
    info = plugin_registry.get_plugin_info()
    
    for plugin_name, plugin_info in info.items():
        print(f"🔌 {plugin_name}")
        print(f"   Version: {plugin_info['version']}")
        print(f"   Author: {plugin_info['author']}")
        print(f"   Description: {plugin_info['description']}")
        print(f"   Capabilities: {', '.join(plugin_info['capabilities'])}")
        
        if plugin_info['dependencies']:
            print(f"   Dependencies: {', '.join(plugin_info['dependencies'])}")
        
        print(f"   Priority: {plugin_info['priority']}")
        
        if plugin_info.get('homepage'):
            print(f"   Homepage: {plugin_info['homepage']}")
        
        print()


def main():
    """Main demo function."""
    
    print("🚀 PyFEALiTE Plugin Architecture Demo")
    print("=====================================")
    print()
    
    try:
        # Run all demos
        demo_plugin_discovery()
        demo_2d_analysis()
        demo_3d_capability_check()
        demo_analysis_validation()
        demo_convenience_methods()
        demo_plugin_info()
        
        print("🎉 Plugin Architecture Demo Complete!")
        print()
        print("💡 Next Steps:")
        print("   • Install 3D capabilities: pip install pyfealite[3d]")
        print("   • Try the GUI interface: python -m pyfealite.gui")
        print("   • Explore the web platform: python -m pyfealite.web")
        print("   • Check documentation: https://pyfealite.readthedocs.io")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()