"""Complete structural analysis example with PyFEALiTE."""

import sys
from pathlib import Path
import numpy as np

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D, EndRelease
from pyfealite.core.structure import Structure
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.loads.base import LoadCase, LoadType
from pyfealite.loads.point_load import PointLoad, NodalLoad
from pyfealite.loads.distributed_load import UniformLoad


def main():
    """Demonstrate complete structural analysis."""
    print("PyFEALiTE - Complete Structural Analysis")
    print("=" * 45)
    
    # Create structure
    structure = Structure("Simply Supported Beam")
    
    # Create material and section
    steel = IsotropicMaterial.steel("S355")
    section = RectangularSection(
        material=steel,
        width=0.2,
        height=0.4,
        label="200x400"
    )
    
    print(f"\n1. Structure: {structure}")
    print(f"   Material: {steel.label}, E = {steel.E/1e9:.0f} GPa")
    print(f"   Section: {section.label}, A = {section.A:.4f} m^2, I = {section.Iz:.2e} m^4")
    
    # Create nodes
    n1 = Node2D(x=0.0, y=0.0, label="Support_A")
    n2 = Node2D(x=3.0, y=0.0, label="Mid")
    n3 = Node2D(x=6.0, y=0.0, label="Support_B")
    
    # Apply boundary conditions
    n1.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)  # Pinned
    n3.restrain(NodalDegreeOfFreedom.UY)  # Roller
    
    # Add nodes to structure
    structure.add_node(n1, n2, n3)
    
    print(f"\n2. Nodes:")
    for node in structure.nodes:
        restraints = "".join("R" if r else "F" for r in node.restraints)
        print(f"   {node.label}: ({node.x}, {node.y}) [{restraints}] - {node.dof_count} free DOFs")
    
    # Create elements
    beam1 = FrameElement2D(
        start_node=n1,
        end_node=n2,
        cross_section=section,
        label="Beam_1-2"
    )
    
    beam2 = FrameElement2D(
        start_node=n2,
        end_node=n3,
        cross_section=section,
        label="Beam_2-3"
    )
    
    # Add elements to structure
    structure.add_element(beam1, beam2)
    
    print(f"\n3. Elements:")
    for element in structure.elements:
        print(f"   {element.label}: {element.start_node.label}->{element.end_node.label}, "
              f"L={element.length:.2f} m")
    
    # Create load cases
    dead_load = LoadCase("Dead Load", LoadType.DEAD)
    live_load = LoadCase("Live Load", LoadType.LIVE)
    
    structure.add_load_case(dead_load, live_load)
    
    # Add loads to elements (need to add loads attribute to elements)
    beam1.loads = []
    beam2.loads = []
    
    # Dead loads: Self weight (simplified)
    dead_intensity = -section.A * steel.density_value * 9.81 / 1000  # kN/m
    beam1.loads.append(UniformLoad(
        load_case=dead_load,
        wx=0.0,
        wy=dead_intensity,
        label="Self_weight_1"
    ))
    beam2.loads.append(UniformLoad(
        load_case=dead_load,
        wx=0.0,
        wy=dead_intensity,
        label="Self_weight_2"
    ))
    
    # Live loads
    beam1.loads.append(PointLoad(
        load_case=live_load,
        Fx=0.0,
        Fy=-50.0,  # 50 kN downward
        distance=1.5,  # At mid-span
        label="Point_load_50kN"
    ))
    
    beam2.loads.append(UniformLoad(
        load_case=live_load,
        wx=0.0,
        wy=-20.0,  # 20 kN/m downward
        label="UDL_20kN/m"
    ))
    
    # Add nodal loads
    n2.loads = [NodalLoad(
        load_case=live_load,
        node=n2,
        Fx=10.0,  # 10 kN horizontal
        Fy=0.0,
        label="Horizontal_10kN"
    )]
    
    print(f"\n4. Load Cases:")
    for lc in structure.load_cases:
        print(f"   {lc}")
    
    print(f"\n5. Loads:")
    total_loads = 0
    for element in structure.elements:
        for load in element.loads:
            print(f"   {load}")
            total_loads += 1
    for node in structure.nodes:
        for load in getattr(node, 'loads', []):
            print(f"   {load}")
            total_loads += 1
    print(f"   Total: {total_loads} loads")
    
    print(f"\n6. Structure Summary:")
    print(f"   {structure.summary()}")
    
    # Solve structure
    print(f"\n7. Analysis:")
    try:
        structure.solve()
        
        print(f"   Status: {structure.analysis_status}")
        
        # Display results
        print(f"\n8. Results:")
        
        for load_case in structure.load_cases:
            print(f"\n   Load Case: {load_case.name}")
            print(f"   Displacements:")
            
            for node in structure.nodes:
                disp = structure.get_node_displacement(node, load_case)
                print(f"     {node.label}: Ux={disp[0]:.2e} m, Uy={disp[1]:.2e} m, Rz={disp[2]:.2e} rad")
            
            print(f"   Reactions:")
            for node in structure.nodes:
                if not node.is_free:
                    reaction = structure.get_node_reaction(node, load_case)
                    print(f"     {node.label}: Rx={reaction[0]:.2f} kN, Ry={reaction[1]:.2f} kN, Mz={reaction[2]:.2f} kN.m")
        
        # Check equilibrium
        print(f"\n9. Equilibrium Check:")
        for load_case in structure.load_cases:
            total_reaction_y = sum(structure.get_node_reaction(node, load_case)[1] 
                                 for node in structure.nodes if not node.is_free)
            print(f"   {load_case.name}: Sum of vertical reactions = {total_reaction_y:.2f} kN")
        
        print("\n[OK] Complete analysis successful!")
        
    except Exception as e:
        print(f"   Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()