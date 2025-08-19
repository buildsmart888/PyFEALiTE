#!/usr/bin/env python3
"""
ตัวอย่างการใช้งานฟังก์ชันพล็อตแสดงผลแรงภายในใหม่
Simple test of new internal forces plotting functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyfealite.core.structure import Structure
from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.loads.point_load import NodalLoad
from pyfealite.loads.distributed_load import UniformLoad
from pyfealite.loads.base import LoadCase
from pyfealite.visualization.structure_plot import plot_structure_with_internal_forces


def create_simple_frame():
    """สร้างโครงสร้างง่าย ๆ สำหรับทดสอบ"""
    
    structure = Structure(name="Simple 2D Frame")
    
    # Material
    steel = IsotropicMaterial(
        E=200000,  # MPa
        nu=0.3,
        density_value=7850,
        label="Steel"
    )
    
    # Section
    section = RectangularSection(
        material=steel,
        width=0.3,
        height=0.4,
        label="Rect_30x40"
    )
    
    # Nodes
    n1 = Node2D(x=0.0, y=0.0, label="n1", restraints=[True, True, True])  # Fixed
    n2 = Node2D(x=6.0, y=0.0, label="n2", restraints=[True, True, True])  # Fixed
    n3 = Node2D(x=0.0, y=4.0, label="n3", restraints=[False, False, False])  # Free
    n4 = Node2D(x=6.0, y=4.0, label="n4", restraints=[False, False, False])  # Free
    
    nodes = [n1, n2, n3, n4]
    for node in nodes:
        structure.add_node(node)
        node.loads = []
    
    # Elements
    e1 = FrameElement2D(n1, n3, section, "e1")  # Left column
    e2 = FrameElement2D(n2, n4, section, "e2")  # Right column  
    e3 = FrameElement2D(n3, n4, section, "e3")  # Beam
    
    elements = [e1, e2, e3]
    for element in elements:
        structure.add_element(element)
        element.loads = []
    
    # Load Case
    load_case = LoadCase("Test Load")
    structure.add_load_case(load_case)
    
    # Loads
    # Point load at node 3
    nodal_load = NodalLoad(
        load_case=load_case,
        node=n3,
        Fx=0.0,
        Fy=-50.0,  # 50kN down
        Mz=0.0
    )
    n3.loads.append(nodal_load)
    
    # Uniform load on beam
    uniform_load = UniformLoad(
        load_case=load_case,
        wx=0.0,
        wy=-20.0,  # 20 kN/m down
        label="BeamLoad"
    )
    e3.loads.append(uniform_load)
    
    return structure


def main():
    print("=" * 50)
    print("PyFEALiTE - Simple Internal Forces Test")
    print("=" * 50)
    
    structure = create_simple_frame()
    
    print(f"Structure: {structure.name}")
    print(f"Nodes: {len(structure.nodes)}")
    print(f"Elements: {len(structure.elements)}")
    
    # Test the new plotting function
    print("\\nCreating internal forces plot...")
    
    fig = plot_structure_with_internal_forces(
        structure=structure,
        load_case=structure.load_cases[0],
        nfd_scale=0.02,
        sfd_scale=0.02,
        bmd_scale=0.02,
        displacement_scale=100.0,  # เพิ่ม displacement scale
        diagram_offset=5.0,
        title="Simple Frame - Internal Forces Test",
        figsize=(24, 16),  # เพิ่มขนาดสำหรับ layout 2x3
        save_as="simple_internal_forces_test_updated.png"
    )
    
    import matplotlib.pyplot as plt
    plt.show()
    
    print("✅ Test completed!")
    print("📁 Saved: simple_internal_forces_test_updated.png")


if __name__ == "__main__":
    main()
