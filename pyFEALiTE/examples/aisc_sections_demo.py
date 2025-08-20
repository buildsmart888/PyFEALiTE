"""
Example: AISC Steel Sections Integration with PyFEALiTE

This example demonstrates how to use the comprehensive AISC steel section database
from steelpy library integrated with PyFEALiTE for structural analysis.

Requirements:
    pip install steelpy

Features:
- Complete AISC section database (W, HSS, Pipe, Angles, Channels, Tees)
- Automatic unit conversion from imperial to SI
- Section search and filtering capabilities
- Professional steel design integration
"""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from pyfealite import *
    from pyfealite.sections.aisc_section import AISCSection, AISCDimensions
    print("✅ PyFEALiTE imported successfully")
except ImportError as e:
    print(f"❌ Error importing PyFEALiTE: {e}")
    sys.exit(1)

def demonstrate_aisc_sections():
    """Demonstrate AISC section capabilities."""
    print("\n" + "="*60)
    print("🏗️  AISC STEEL SECTIONS INTEGRATION DEMO")
    print("="*60)
    
    # Check if steelpy is available
    try:
        from steelpy import aisc
        print("✅ steelpy library is available")
    except ImportError:
        print("❌ steelpy not installed. Install with: pip install steelpy")
        print("   This demo will show the integration structure anyway.")
        return
    
    # Create material
    steel = IsotropicMaterial.steel_a992()
    print(f"📊 Material: {steel.label}")
    
    print("\n" + "-"*50)
    print("1️⃣  WIDE FLANGE BEAM SECTIONS")
    print("-"*50)
    
    try:
        # Create W12x26 beam section
        w_beam = AISCSection(steel, "W12X26", "Main Beam")
        
        print(f"Section: {w_beam.section_name}")
        print(f"Area: {w_beam.area:.4f} m²")
        print(f"Iz (Strong axis): {w_beam.Iz:.2e} m⁴")
        print(f"Iy (Weak axis): {w_beam.Iy:.2e} m⁴")
        print(f"Depth: {w_beam.depth:.3f} m")
        print(f"Width: {w_beam.width:.3f} m")
        print(f"Weight: {w_beam.weight_per_length:.1f} kg/m")
        
        # Show complete section info
        info = w_beam.get_section_info()
        print(f"\nImperial Properties:")
        print(f"  Weight: {info['dimensions_imperial']['weight_lb_ft']:.1f} lb/ft")
        print(f"  Area: {info['dimensions_imperial']['area_in2']:.2f} in²")
        print(f"  Depth: {info['dimensions_imperial']['d_in']:.1f} in")
        
    except Exception as e:
        print(f"Error creating W-section: {e}")
    
    print("\n" + "-"*50)
    print("2️⃣  HOLLOW STRUCTURAL SECTIONS (HSS)")
    print("-"*50)
    
    try:
        # Rectangular HSS
        hss_rect = AISCSection(steel, "HSS12X8X1/2", "HSS Column")
        print(f"Rectangular HSS: {hss_rect.section_name}")
        print(f"Area: {hss_rect.area:.4f} m²")
        print(f"Torsional constant J: {hss_rect.J:.2e} m⁴")
        
        # Round HSS  
        hss_round = AISCSection(steel, "HSS6.000X0.500", "Round HSS")
        print(f"\nRound HSS: {hss_round.section_name}")
        print(f"Area: {hss_round.area:.4f} m²")
        print(f"Iz = Iy: {hss_round.Iz:.2e} m⁴")
        
    except Exception as e:
        print(f"Error creating HSS sections: {e}")
    
    print("\n" + "-"*50)
    print("3️⃣  SECTION SEARCH AND FILTERING")
    print("-"*50)
    
    try:
        # List available W sections
        w_sections = AISCSection.list_available_sections('W')
        print(f"Available W sections: {len(w_sections)} total")
        print(f"First 10: {w_sections[:10]}")
        
        # Search for beams with specific criteria
        criteria = {
            'd': {'min': 12, 'max': 18},    # Depth between 12-18 inches
            'Ix': {'min': 500}              # Moment of inertia > 500 in⁴
        }
        
        filtered_sections = AISCSection.search_sections('W', criteria, sort_by='weight')
        print(f"\nFiltered W sections (d=12-18\", Ix>500): {len(filtered_sections)} found")
        
        # Show first few results
        for i, (name, section) in enumerate(list(filtered_sections.items())[:5]):
            print(f"  {name}: d={section.d:.1f}\", Ix={section.Ix:.0f} in⁴, {section.weight:.1f} lb/ft")
        
    except Exception as e:
        print(f"Error in section search: {e}")
    
    print("\n" + "-"*50)
    print("4️⃣  STRUCTURAL ANALYSIS WITH AISC SECTIONS")
    print("-"*50)
    
    try:
        # Create a simple frame with AISC sections
        structure = Structure()
        
        # Nodes
        n1 = Node2D(0, 0, "Support A")
        n2 = Node2D(6, 0, "Support B") 
        n3 = Node2D(3, 4, "Ridge")
        
        structure.add_node(n1)
        structure.add_node(n2)
        structure.add_node(n3)
        
        # Create AISC sections
        beam_section = AISCSection(steel, "W14X30", "Beam")
        column_section = AISCSection(steel, "W12X40", "Column")
        
        # Elements with AISC sections
        beam = FrameElement2D(n1, n2, beam_section, "Beam")
        col1 = FrameElement2D(n1, n3, column_section, "Left Column")
        col2 = FrameElement2D(n2, n3, column_section, "Right Column")
        
        structure.add_element(beam)
        structure.add_element(col1)
        structure.add_element(col2)
        
        print(f"✅ Created frame with AISC sections:")
        print(f"  Beam: {beam_section.section_name} (A={beam_section.area:.4f} m²)")
        print(f"  Columns: {column_section.section_name} (A={column_section.area:.4f} m²)")
        
        # Add supports
        n1.add_support(ux=True, uy=True, rz=False)  # Pin
        n2.add_support(ux=True, uy=True, rz=False)  # Pin
        
        # Add loads
        load_case = "LIVE"
        uniform_load = UniformLoad(col1, 10000, LoadDirection.Y, load_case, "Live Load")
        structure.add_load(uniform_load)
        
        print(f"  Added live load: {uniform_load.magnitude/1000:.0f} kN/m")
        
        # Analyze
        print(f"  Structure ready for analysis with {len(structure.elements)} AISC elements")
        
    except Exception as e:
        print(f"Error in structural analysis setup: {e}")
    
    print("\n" + "-"*50)
    print("5️⃣  SECTION TYPE COVERAGE")
    print("-"*50)
    
    section_types = AISCSection.SECTION_TYPES
    print("Available AISC section types:")
    for abbrev, full_name in section_types.items():
        try:
            count = len(AISCSection.list_available_sections(abbrev))
            print(f"  {abbrev:6} ({full_name:15}): {count:3d} sections")
        except:
            print(f"  {abbrev:6} ({full_name:15}): N/A")
    
    print("\n" + "="*60)
    print("✅ AISC Steel Sections Integration Demo Complete!")
    print("   - Complete AISC database integration")
    print("   - Automatic imperial to SI conversion") 
    print("   - Section search and filtering")
    print("   - Seamless PyFEALiTE integration")
    print("="*60)

if __name__ == "__main__":
    demonstrate_aisc_sections()
