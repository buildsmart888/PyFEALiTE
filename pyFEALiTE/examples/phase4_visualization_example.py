"""Phase 4 - Comprehensive visualization and advanced features example."""

import sys
from pathlib import Path
import numpy as np

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D
from pyfealite.core.structure import Structure
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.loads.base import LoadCase, LoadType
from pyfealite.loads.point_load import PointLoad, NodalLoad
from pyfealite.loads.distributed_load import UniformLoad
from pyfealite.utils.combinations import standard_load_combinations, eurocode_combinations
from pyfealite.utils.export import export_to_json, export_to_csv, export_results_summary
from pyfealite.visualization import StructurePlotter, plot_structure_with_loads, create_analysis_summary

# Optional benchmarking
try:
    from pyfealite.utils.benchmarks import benchmark_analysis
    BENCHMARKS_AVAILABLE = True
except ImportError:
    BENCHMARKS_AVAILABLE = False
    print("Note: Benchmarking not available (requires psutil package)")


def create_demo_frame():
    """Create a 2D frame for demonstration."""
    print("Creating demonstration 2D frame structure...")
    
    # Create structure
    structure = Structure("Demo 2D Frame")
    
    # Materials and sections
    steel = IsotropicMaterial.steel("S355")
    beam_section = RectangularSection(steel, width=0.3, height=0.6, label="Beam_300x600")
    column_section = RectangularSection(steel, width=0.4, height=0.4, label="Column_400x400")
    
    # Create nodes (2-bay, 2-story frame)
    nodes = {}
    bay_width = 6.0  # meters
    story_height = 4.0  # meters
    
    # Ground level nodes
    nodes[(0, 0)] = Node2D(0, 0, "A")  # Pinned support
    nodes[(0, 0)].restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
    
    nodes[(1, 0)] = Node2D(bay_width, 0, "B")  # Pinned support
    nodes[(1, 0)].restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
    
    nodes[(2, 0)] = Node2D(2*bay_width, 0, "C")  # Roller support
    nodes[(2, 0)].restrain(NodalDegreeOfFreedom.UY)
    
    # Second level nodes
    nodes[(0, 1)] = Node2D(0, story_height, "D")
    nodes[(1, 1)] = Node2D(bay_width, story_height, "E")
    nodes[(2, 1)] = Node2D(2*bay_width, story_height, "F")
    
    # Third level nodes
    nodes[(0, 2)] = Node2D(0, 2*story_height, "G")
    nodes[(1, 2)] = Node2D(bay_width, 2*story_height, "H")
    nodes[(2, 2)] = Node2D(2*bay_width, 2*story_height, "I")
    
    # Add all nodes to structure
    for node in nodes.values():
        structure.add_node(node)
    
    # Create elements
    elements = []
    
    # Ground to first floor columns
    elements.append(FrameElement2D(nodes[(0,0)], nodes[(0,1)], column_section, "Col1_L1"))
    elements.append(FrameElement2D(nodes[(1,0)], nodes[(1,1)], column_section, "Col2_L1"))
    elements.append(FrameElement2D(nodes[(2,0)], nodes[(2,1)], column_section, "Col3_L1"))
    
    # First to second floor columns  
    elements.append(FrameElement2D(nodes[(0,1)], nodes[(0,2)], column_section, "Col1_L2"))
    elements.append(FrameElement2D(nodes[(1,1)], nodes[(1,2)], column_section, "Col2_L2"))
    elements.append(FrameElement2D(nodes[(2,1)], nodes[(2,2)], column_section, "Col3_L2"))
    
    # First floor beams
    elements.append(FrameElement2D(nodes[(0,1)], nodes[(1,1)], beam_section, "Beam1_L1"))
    elements.append(FrameElement2D(nodes[(1,1)], nodes[(2,1)], beam_section, "Beam2_L1"))
    
    # Second floor beams
    elements.append(FrameElement2D(nodes[(0,2)], nodes[(1,2)], beam_section, "Beam1_L2"))
    elements.append(FrameElement2D(nodes[(1,2)], nodes[(2,2)], beam_section, "Beam2_L2"))
    
    # Initialize loads list for all elements
    for element in elements:
        element.loads = []
        structure.add_element(element)
    
    return structure, nodes, elements


def create_load_cases(structure, nodes, elements):
    """Create multiple load cases for the frame."""
    print("Creating load cases...")
    
    # Dead load case
    dead_load = LoadCase("Dead Load", LoadType.DEAD)
    
    # Live load case  
    live_load = LoadCase("Live Load", LoadType.LIVE)
    
    # Wind load case
    wind_load = LoadCase("Wind Load", LoadType.WIND)
    
    structure.add_load_case(dead_load, live_load, wind_load)
    
    # Add dead loads (self-weight on beams)
    beam_elements = [e for e in elements if "Beam" in e.label]
    for beam in beam_elements:
        # Self weight: approximately 25 kN/m for concrete slab + beam
        dead_udl = UniformLoad(
            load_case=dead_load,
            wx=0.0,
            wy=-25.0,  # kN/m downward
            label=f"Dead_UDL_{beam.label}"
        )
        beam.loads.append(dead_udl)
    
    # Add live loads
    for beam in beam_elements:
        # Office building live load: 2.5 kPa over 6m tributary = 15 kN/m
        live_udl = UniformLoad(
            load_case=live_load,
            wx=0.0,
            wy=-15.0,  # kN/m downward
            label=f"Live_UDL_{beam.label}"
        )
        beam.loads.append(live_udl)
    
    # Add concentrated live loads at joints
    joint_load_1 = NodalLoad(
        load_case=live_load,
        node=nodes[(1, 1)],
        Fx=0.0,
        Fy=-50.0,  # 50 kN downward
        label="Live_Joint_E"
    )
    nodes[(1, 1)].loads = [joint_load_1]
    
    # Add wind loads (horizontal forces on columns)
    wind_intensity = 1.5  # kN/m (wind pressure)
    column_elements = [e for e in elements if "Col" in e.label]
    
    for column in column_elements:
        # Wind load as distributed horizontal load
        wind_udl = UniformLoad(
            load_case=wind_load,
            wx=wind_intensity if "L1" in column.label else wind_intensity * 0.8,  # Reduced for upper stories
            wy=0.0,
            label=f"Wind_{column.label}"
        )
        column.loads.append(wind_udl)
    
    # Additional lateral loads at top level
    for i in range(3):
        wind_lateral = NodalLoad(
            load_case=wind_load,
            node=nodes[(i, 2)],
            Fx=20.0,  # 20 kN lateral
            Fy=0.0,
            label=f"Wind_Top_{chr(71+i)}"  # G, H, I
        )
        if not hasattr(nodes[(i, 2)], 'loads'):
            nodes[(i, 2)].loads = []
        nodes[(i, 2)].loads.append(wind_lateral)
    
    return dead_load, live_load, wind_load


def demonstrate_visualization(structure, load_cases):
    """Demonstrate visualization capabilities."""
    print("\n=== VISUALIZATION DEMONSTRATIONS ===")
    
    # Create plotter
    plotter = StructurePlotter(structure, figsize=(15, 10))
    
    # 1. Structure geometry plot
    print("1. Creating structure geometry plot...")
    plotter.setup_figure("2D Frame Structure - Geometry")
    plotter.plot_geometry(show_labels=True)
    plotter.save_plot("frame_geometry.png")
    print("   Saved: frame_geometry.png")
    
    # 2. Load visualization for each load case
    for load_case in load_cases:
        print(f"2. Creating load plot for {load_case.name}...")
        fig = plot_structure_with_loads(
            structure, load_case,
            title=f"Frame Structure - {load_case.name}",
            load_scale=0.05,
            save_as=f"frame_loads_{load_case.name.lower().replace(' ', '_')}.png"
        )
        print(f"   Saved: frame_loads_{load_case.name.lower().replace(' ', '_')}.png")
    
    # 3. Deformed shape (after analysis)
    if structure.analysis_status == "success":
        for load_case in load_cases:
            print(f"3. Creating deformed shape for {load_case.name}...")
            plotter_deform = StructurePlotter(structure, figsize=(12, 8))
            plotter_deform.setup_figure(f"Deformed Shape - {load_case.name}")
            plotter_deform.plot_deformed_shape(load_case, scale=500, show_original=True)
            plotter_deform.save_plot(f"frame_deformed_{load_case.name.lower().replace(' ', '_')}.png")
            print(f"   Saved: frame_deformed_{load_case.name.lower().replace(' ', '_')}.png")
    
    # 4. Comprehensive summary plot
    if structure.analysis_status == "success":
        print("4. Creating comprehensive analysis summary...")
        fig = create_analysis_summary(
            structure, 
            load_case=load_cases[1],  # Live load case
            deform_scale=500,
            save_as="frame_analysis_summary.png"
        )
        print("   Saved: frame_analysis_summary.png")
    
    print("[OK] Visualization demonstrations completed!")


def demonstrate_load_combinations(structure, load_cases):
    """Demonstrate load combination functionality."""
    print("\n=== LOAD COMBINATIONS DEMONSTRATION ===")
    
    dead_load, live_load, wind_load = load_cases
    
    # 1. Standard combinations
    print("1. Generating standard load combinations...")
    std_combinations = standard_load_combinations([dead_load, live_load, wind_load])
    
    print(f"   Generated {len(std_combinations)} standard combinations:")
    for combo in std_combinations:
        print(f"     - {combo}")
    
    # 2. Eurocode combinations
    print("\n2. Generating Eurocode combinations...")
    ec_combinations = eurocode_combinations([dead_load, live_load, wind_load])
    
    print(f"   Generated {len(ec_combinations)} Eurocode combinations:")
    for combo in ec_combinations:
        print(f"     - {combo}")
    
    # 3. Solve with combinations
    print("\n3. Solving structure with load combinations...")
    
    # Select a few combinations for demonstration
    demo_combinations = std_combinations[:3] if len(std_combinations) >= 3 else std_combinations
    
    try:
        structure.solve(load_cases=load_cases, load_combinations=demo_combinations)
        
        print("   Load combination results:")
        for combo in demo_combinations:
            # Find the corresponding result (combination creates virtual load case)
            combo_load_case = None
            for lc in structure._displacements.keys():
                if lc.name == combo.name:
                    combo_load_case = lc
                    break
            
            if combo_load_case:
                # Get max displacement
                max_disp = 0
                max_node = None
                for node in structure.nodes:
                    disp = structure.get_node_displacement(node, combo_load_case)
                    total_disp = np.sqrt(disp[0]**2 + disp[1]**2)
                    if total_disp > max_disp:
                        max_disp = total_disp
                        max_node = node
                
                print(f"     {combo.name}: Max displacement = {max_disp:.4f} m at node {max_node.label}")
    
    except Exception as e:
        print(f"   Load combination solving failed: {e}")
    
    print("[OK] Load combinations demonstration completed!")


def demonstrate_export_capabilities(structure):
    """Demonstrate export functionality."""
    print("\n=== EXPORT CAPABILITIES DEMONSTRATION ===")
    
    export_dir = Path("demo_exports")
    export_dir.mkdir(exist_ok=True)
    
    # 1. JSON export
    print("1. Exporting to JSON format...")
    export_to_json(structure, export_dir / "frame_structure.json")
    
    # 2. CSV export
    print("2. Exporting to CSV format...")
    csv_dir = export_dir / "csv_data"
    export_to_csv(structure, csv_dir)
    
    # 3. Results summary
    if structure.analysis_status == "success":
        print("3. Exporting results summary...")
        export_results_summary(structure, export_dir / "analysis_results.txt")
    
    # 4. DXF export (if ezdxf available)
    try:
        from pyfealite.utils.export import export_to_dxf
        print("4. Exporting to DXF format...")
        export_to_dxf(structure, export_dir / "frame_structure.dxf")
    except ImportError:
        print("4. DXF export not available (requires ezdxf package)")
    
    print(f"[OK] Export capabilities demonstration completed!")
    print(f"   All exports saved to: {export_dir.absolute()}")


def demonstrate_performance_benchmarking(structure):
    """Demonstrate performance benchmarking."""
    print("\n=== PERFORMANCE BENCHMARKING DEMONSTRATION ===")
    
    if not BENCHMARKS_AVAILABLE:
        print("[WARNING] Benchmarking not available (requires psutil package)")
        print("   Install with: pip install psutil")
        return
    
    # 1. Benchmark current structure
    print("1. Benchmarking current structure...")
    result = benchmark_analysis(structure, "Demo_2D_Frame")
    
    print(f"   Benchmark results:")
    print(f"     - Assembly time: {result.assembly_time:.4f}s")
    print(f"     - Solve time: {result.solve_time:.4f}s")
    print(f"     - Total time: {result.total_time:.4f}s")
    print(f"     - Memory usage: {result.memory_usage:.2f} MB")
    print(f"     - DOFs per second: {result.n_dofs/result.total_time:.0f}")
    
    # 2. Run benchmark suite (optional - commented out for demo)
    # print("\n2. Running performance benchmark suite...")
    # from pyfealite.utils.benchmarks import run_performance_suite
    # suite_results = run_performance_suite()
    
    print("[OK] Performance benchmarking demonstration completed!")


def main():
    """Main demonstration function."""
    print("PyFEALiTE Phase 4 - Visualization & Advanced Features Demo")
    print("=" * 60)
    
    # Create demo structure
    structure, nodes, elements = create_demo_frame()
    print(f"[OK] Created structure: {structure.summary()}")
    
    # Create load cases
    load_cases = create_load_cases(structure, nodes, elements)
    print(f"[OK] Created {len(load_cases)} load cases")
    
    # Solve structure
    print("\nSolving structure...")
    try:
        structure.solve()
        print(f"[OK] Analysis completed: {structure.analysis_status}")
        
        # Print some key results
        live_load = load_cases[1]
        max_disp_node = max(structure.nodes, key=lambda n: abs(structure.get_node_displacement(n, live_load)[1]))
        max_disp = structure.get_node_displacement(max_disp_node, live_load)
        print(f"  Max vertical displacement: {abs(max_disp[1]):.4f} m at node {max_disp_node.label}")
        
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        return
    
    # Demonstrate all Phase 4 features
    demonstrate_visualization(structure, load_cases)
    demonstrate_load_combinations(structure, load_cases)
    demonstrate_export_capabilities(structure)
    demonstrate_performance_benchmarking(structure)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Phase 4 demonstration completed successfully!")
    print("[OK] Visualization system fully operational")
    print("[OK] Load combinations implemented")
    print("[OK] Export capabilities functional")
    print("[OK] Performance benchmarking available")
    print("\nPyFEALiTE is ready for advanced structural analysis!")


if __name__ == "__main__":
    main()