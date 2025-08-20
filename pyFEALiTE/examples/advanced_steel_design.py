"""
Advanced Steel Design Example with AISC Sections
==============================================

This example demonstrates advanced steel design capabilities using
PyFEALiTE with AISC steel sections through steelpy integration.

Features demonstrated:
- Steel section selection and optimization
- Multiple load combinations (LRFD)
- Deflection checks and capacity calculations
- Design summary reports
- Visualization of results

Requirements:
- steelpy library: pip install steelpy
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings

# PyFEALiTE imports
from pyfealite import (
    Structure, Node, FrameElement, 
    LoadCase, LoadCombination,
    PointLoad, UniformLoad,
    FixedSupport, PinnedSupport
)

from pyfealite.sections import (
    AISCSection, SteelDesignHelper, SteelGrade, 
    create_steel_material, STEELPY_AVAILABLE
)

def main():
    """Main steel design example."""
    
    if not STEELPY_AVAILABLE:
        print("⚠️  steelpy library not available")
        print("   Install with: pip install steelpy")
        print("   Running limited example without AISC sections...")
        run_limited_example()
        return
    
    print("🔧 Advanced Steel Design Example with AISC Sections")
    print("=" * 60)
    
    # Create design helper
    design_helper = SteelDesignHelper()
    
    # Example building parameters
    building_params = {
        'bay_width': 9.0,      # 9m bay width
        'floor_height': 4.0,   # 4m floor height  
        'num_floors': 3,       # 3-story building
        'dead_load': 5000,     # 5 kN/m (includes self-weight)
        'live_load': 3000,     # 3 kN/m
        'wind_load': 1500      # 1.5 kN/m lateral
    }
    
    # 1. Beam Design Example
    print("\n1. BEAM DESIGN EXAMPLE")
    print("-" * 30)
    
    beam_design_example(design_helper, building_params)
    
    # 2. Column Design Example  
    print("\n2. COLUMN DESIGN EXAMPLE")
    print("-" * 30)
    
    column_design_example(design_helper, building_params)
    
    # 3. Complete Frame Analysis
    print("\n3. COMPLETE FRAME ANALYSIS")
    print("-" * 30)
    
    frame_analysis_example(design_helper, building_params)
    
    print("\n✅ Steel design example completed successfully!")
    

def beam_design_example(design_helper, params):
    """Demonstrate beam design with AISC sections."""
    
    span = params['bay_width']
    dead_load = params['dead_load']
    live_load = params['live_load']
    total_service = dead_load + live_load
    
    # LRFD load combination: 1.2D + 1.6L
    factored_load = 1.2 * dead_load + 1.6 * live_load
    
    print(f"Span: {span} m")
    print(f"Service loads: Dead = {dead_load} N/m, Live = {live_load} N/m")
    print(f"Factored load: {factored_load} N/m")
    
    # Get beam recommendations
    recommendations = design_helper.recommend_beam_section(
        span=span,
        total_load=factored_load,
        steel_grade=SteelGrade.A992
    )
    
    if not recommendations:
        print("❌ No suitable sections found")
        return
    
    print(f"\n📊 Top 5 Recommended Beam Sections:")
    print("-" * 80)
    print(f"{'Section':<12} {'Weight':<8} {'Depth':<8} {'Flex':<8} {'Defl':<8} {'Max':<8} {'Eff':<8}")
    print(f"{'Name':<12} {'lb/ft':<8} {'in':<8} {'Util':<8} {'Util':<8} {'Util':<8} {'%':<8}")
    print("-" * 80)
    
    for i, rec in enumerate(recommendations[:5]):
        print(f"{rec['section_name']:<12} "
              f"{rec['weight_lb_ft']:<8.1f} "
              f"{rec['depth_in']:<8.1f} "
              f"{rec['flexure_utilization']:<8.2f} "
              f"{rec['deflection_utilization']:<8.2f} "
              f"{rec['max_utilization']:<8.2f} "
              f"{rec['efficiency']*100:<8.1f}")
    
    # Analyze selected section
    selected = recommendations[0]
    section_name = selected['section_name']
    
    print(f"\n🔍 Detailed Analysis for {section_name}:")
    print("-" * 40)
    
    try:
        # Create AISC section
        steel_material = create_steel_material("A992", f"Steel A992")
        aisc_section = AISCSection(section_name, steel_material)
        
        # Deflection check
        deflection_check = design_helper.check_beam_deflection(
            section=aisc_section,
            span=span,
            load=total_service,  # Use service load for deflection
            limit_ratio=240      # L/240 limit
        )
        
        # Capacity calculation
        capacity = design_helper.calculate_beam_capacity(
            section=aisc_section,
            steel_grade=SteelGrade.A992
        )
        
        print(f"Section properties:")
        print(f"  - Weight: {aisc_section.weight_per_length:.1f} kg/m")
        print(f"  - Area: {aisc_section.area*1e4:.1f} cm²")
        print(f"  - Ix: {aisc_section.Iz*1e8:.0f} cm⁴")
        print(f"  - Sx: {aisc_section.Sz*1e6:.0f} cm³")
        print(f"  - Zx: {aisc_section.Zz*1e6:.0f} cm³")
        
        print(f"\nDeflection check:")
        print(f"  - Max deflection: {deflection_check['max_deflection_mm']:.1f} mm")
        print(f"  - Limit (L/240): {deflection_check['limit_mm']:.1f} mm")
        print(f"  - Ratio: {deflection_check['ratio']:.2f}")
        print(f"  - Status: {'✅ PASS' if deflection_check['passes'] else '❌ FAIL'}")
        
        print(f"\nFlexural capacity:")
        print(f"  - φMn: {capacity['phi_Mn_kNm']:.0f} kN⋅m")
        print(f"  - Required: {factored_load * span**2 / 8 / 1000:.0f} kN⋅m")
        print(f"  - Utilization: {(factored_load * span**2 / 8) / (capacity['phi_Mn_kNm'] * 1000):.2f}")
        
    except Exception as e:
        print(f"❌ Error analyzing section: {e}")


def column_design_example(design_helper, params):
    """Demonstrate column design with AISC sections."""
    
    height = params['floor_height'] * params['num_floors']
    
    # Estimate column loads (tributary area method)
    tributary_area = (params['bay_width'] / 2) * (params['bay_width'] / 2)  # Corner column
    dead_load_per_floor = params['dead_load'] * tributary_area
    live_load_per_floor = params['live_load'] * tributary_area
    
    total_dead = dead_load_per_floor * params['num_floors']
    total_live = live_load_per_floor * params['num_floors']
    
    # LRFD combination: 1.2D + 1.6L
    factored_axial = 1.2 * total_dead + 1.6 * total_live
    
    print(f"Column height: {height} m")
    print(f"Tributary area: {tributary_area:.1f} m²")
    print(f"Total loads: Dead = {total_dead/1000:.0f} kN, Live = {total_live/1000:.0f} kN")
    print(f"Factored axial load: {factored_axial/1000:.0f} kN")
    
    # Get column recommendations
    recommendations = design_helper.recommend_column_section(
        length=height,
        axial_load=factored_axial,
        k_factor=1.0,  # Pinned-pinned
        steel_grade=SteelGrade.A992
    )
    
    if not recommendations:
        print("❌ No suitable sections found")
        return
    
    print(f"\n📊 Recommended Column Sections:")
    print("-" * 90)
    print(f"{'Section':<15} {'Type':<8} {'Weight':<8} {'Area':<8} {'KL/r':<8} {'Util':<8}")
    print(f"{'Name':<15} {'':<8} {'lb/ft':<8} {'in²':<8} {'max':<8} {'%':<8}")
    print("-" * 90)
    
    for rec in recommendations[:8]:
        print(f"{rec['section_name']:<15} "
              f"{rec['type']:<8} "
              f"{rec['weight_lb_ft']:<8.1f} "
              f"{rec['area_in2']:<8.1f} "
              f"{rec['max_slenderness']:<8.0f} "
              f"{rec['area_utilization']*100:<8.1f}")


def frame_analysis_example(design_helper, params):
    """Complete frame analysis with optimized steel sections."""
    
    print("Setting up 2D moment frame analysis...")
    
    # Create structure
    structure = Structure()
    
    # Materials
    steel_material = create_steel_material("A992", "Steel A992")
    
    # Use recommended sections
    try:
        # Beam section (from previous analysis)
        beam_section = AISCSection("W18X35", steel_material)  # Typical light beam
        column_section = AISCSection("W12X65", steel_material)  # Typical column
        
        print(f"Using sections: Beam={beam_section.section_name}, Column={column_section.section_name}")
        
    except Exception:
        # Fallback to generic sections if AISC not available
        from pyfealite.sections import RectangularSection
        beam_section = RectangularSection(0.3, 0.6, steel_material, "Beam")
        column_section = RectangularSection(0.3, 0.3, steel_material, "Column")
        print("Using generic rectangular sections")
    
    # Geometry
    bay_width = params['bay_width']
    floor_height = params['floor_height']
    
    # Create nodes (2-bay, 2-story frame)
    nodes = {}
    node_id = 1
    
    for floor in range(3):  # 0=base, 1=2nd floor, 2=roof
        y = floor * floor_height
        for bay in range(3):  # 3 columns
            x = bay * bay_width
            nodes[f"N{floor}{bay}"] = structure.add_node(Node(node_id, x, y))
            node_id += 1
    
    # Add elements
    element_id = 1
    
    # Columns
    for bay in range(3):
        for floor in range(2):
            bottom_node = nodes[f"N{floor}{bay}"]
            top_node = nodes[f"N{floor+1}{bay}"]
            structure.add_element(FrameElement(
                element_id, bottom_node, top_node, column_section, f"Col{floor+1}{bay+1}"
            ))
            element_id += 1
    
    # Beams
    for floor in range(1, 3):  # 2nd floor and roof
        for bay in range(2):  # 2 bays
            left_node = nodes[f"N{floor}{bay}"]
            right_node = nodes[f"N{floor}{bay+1}"]
            structure.add_element(FrameElement(
                element_id, left_node, right_node, beam_section, f"Beam{floor}{bay+1}"
            ))
            element_id += 1
    
    # Supports (pinned at base)
    for bay in range(3):
        base_node = nodes[f"N0{bay}"]
        structure.add_support(PinnedSupport(base_node))
    
    # Load cases
    dead_case = LoadCase("Dead Load")
    live_case = LoadCase("Live Load")
    wind_case = LoadCase("Wind Load")
    
    # Dead loads on beams
    for floor in range(1, 3):
        for bay in range(2):
            beam_element = None
            for element in structure.elements.values():
                if element.label == f"Beam{floor}{bay+1}":
                    beam_element = element
                    break
            
            if beam_element:
                dead_case.add_load(UniformLoad(
                    beam_element, 0, -params['dead_load'], "global"
                ))
                live_case.add_load(UniformLoad(
                    beam_element, 0, -params['live_load'], "global"
                ))
    
    # Wind loads (lateral on columns)
    wind_per_floor = params['wind_load'] * floor_height
    for floor in range(1, 3):
        left_node = nodes[f"N{floor}0"]
        wind_case.add_load(PointLoad(left_node, wind_per_floor, 0))
    
    # Load combinations
    combinations = [
        LoadCombination("1.4D", [("Dead Load", 1.4)]),
        LoadCombination("1.2D+1.6L", [("Dead Load", 1.2), ("Live Load", 1.6)]),
        LoadCombination("1.2D+1.0L+1.0W", [("Dead Load", 1.2), ("Live Load", 1.0), ("Wind Load", 1.0)])
    ]
    
    # Add to structure
    structure.add_load_case(dead_case)
    structure.add_load_case(live_case)
    structure.add_load_case(wind_case)
    
    for combo in combinations:
        structure.add_load_combination(combo)
    
    print(f"Frame model: {len(structure.nodes)} nodes, {len(structure.elements)} elements")
    
    # Analyze
    print("Running structural analysis...")
    try:
        structure.analyze(combinations[1].name)  # Analyze 1.2D+1.6L
        
        # Get results summary
        results = structure.get_analysis_results()
        
        print(f"\n📊 Analysis Results Summary:")
        print("-" * 40)
        print(f"Max displacement: {max(abs(d.uy) for d in results.displacements.values())*1000:.1f} mm")
        
        # Find critical beam moments
        beam_moments = []
        for element_id, forces in results.forces.items():
            element = structure.elements[element_id]
            if "Beam" in element.label:
                max_moment = max(abs(forces.mz_i), abs(forces.mz_j))
                beam_moments.append((element.label, max_moment/1000))  # Convert to kN⋅m
        
        beam_moments.sort(key=lambda x: x[1], reverse=True)
        print(f"Critical beam moments:")
        for label, moment in beam_moments[:3]:
            print(f"  {label}: {moment:.0f} kN⋅m")
        
        # Check beam capacity if using AISC sections
        if STEELPY_AVAILABLE and hasattr(beam_section, 'section_name'):
            try:
                capacity = design_helper.calculate_beam_capacity(
                    beam_section, steel_grade=SteelGrade.A992
                )
                max_moment_knm = beam_moments[0][1] if beam_moments else 0
                utilization = max_moment_knm / capacity['phi_Mn_kNm'] if capacity['phi_Mn_kNm'] > 0 else 0
                
                print(f"\nBeam capacity check:")
                print(f"  Design moment capacity: {capacity['phi_Mn_kNm']:.0f} kN⋅m")
                print(f"  Max applied moment: {max_moment_knm:.0f} kN⋅m") 
                print(f"  Utilization ratio: {utilization:.2f}")
                print(f"  Status: {'✅ OK' if utilization < 1.0 else '❌ Overstressed'}")
                
            except Exception as e:
                print(f"Could not check beam capacity: {e}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


def run_limited_example():
    """Run limited example without steelpy."""
    print("\n🔧 Limited Steel Design Example (No AISC Database)")
    print("=" * 60)
    
    # Create generic steel material
    from pyfealite.materials import IsotropicMaterial
    steel = IsotropicMaterial(
        elastic_modulus=200e9,  # 200 GPa
        poisson_ratio=0.3,
        density=7850,           # kg/m³
        yield_strength=345e6,   # 345 MPa (A992)
        ultimate_strength=450e6, # 450 MPa
        label="Steel A992"
    )
    
    # Show steel properties
    print(f"Steel material properties:")
    print(f"  - Yield strength: {steel.yield_strength/1e6:.0f} MPa")
    print(f"  - Elastic modulus: {steel.elastic_modulus/1e9:.0f} GPa")
    print(f"  - Density: {steel.density:.0f} kg/m³")
    
    # Basic beam design calculation
    span = 9.0  # m
    load = 8000  # N/m (factored)
    max_moment = load * span**2 / 8  # N⋅m
    
    required_section_modulus = max_moment / (0.9 * steel.yield_strength)  # m³
    
    print(f"\nBasic beam design:")
    print(f"  - Span: {span} m")
    print(f"  - Load: {load} N/m")
    print(f"  - Max moment: {max_moment/1000:.0f} kN⋅m")
    print(f"  - Required section modulus: {required_section_modulus*1e6:.0f} cm³")
    
    print(f"\n💡 Install steelpy for complete AISC section database:")
    print(f"   pip install steelpy")


if __name__ == "__main__":
    # Suppress warnings for cleaner output
    warnings.filterwarnings("ignore")
    
    main()
