#!/usr/bin/env python3
"""
ตัวอย่างการใช้งานฟังก์ชันพล็อตใหม่พร้อม displacement และการแสดงแรงที่ถูกต้อง
Enhanced internal forces plotting with proper displacement and load visualization.
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
from pyfealite.loads.distributed_load import UniformLoad, TrapezoidalLoad
from pyfealite.loads.base import LoadCase
from pyfealite.visualization.structure_plot import plot_structure_with_internal_forces


def create_enhanced_frame():
    """สร้างโครงสร้างที่มีแรงหลากหลายเพื่อทดสอบการแสดงผล"""
    
    structure = Structure(name="Enhanced Test Frame")
    
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
        width=0.25,
        height=0.40,
        label="Rect_25x40"
    )
    
    # Nodes - สร้าง portal frame ที่ซับซ้อนขึ้น
    n1 = Node2D(x=0.0, y=0.0, label="n1", restraints=[True, True, True])   # Fixed base left
    n2 = Node2D(x=8.0, y=0.0, label="n2", restraints=[True, True, False])  # Pin base right
    n3 = Node2D(x=0.0, y=5.0, label="n3", restraints=[False, False, False]) # Free
    n4 = Node2D(x=8.0, y=5.0, label="n4", restraints=[False, False, False]) # Free
    n5 = Node2D(x=4.0, y=8.0, label="n5", restraints=[False, False, False]) # Peak
    
    nodes = [n1, n2, n3, n4, n5]
    for node in nodes:
        structure.add_node(node)
        node.loads = []  # Initialize loads list
    
    # Elements
    e1 = FrameElement2D(n1, n3, section, "e1")  # Left column
    e2 = FrameElement2D(n2, n4, section, "e2")  # Right column  
    e3 = FrameElement2D(n3, n4, section, "e3")  # Beam
    e4 = FrameElement2D(n3, n5, section, "e4")  # Left rafter
    e5 = FrameElement2D(n4, n5, section, "e5")  # Right rafter
    
    elements = [e1, e2, e3, e4, e5]
    for element in elements:
        structure.add_element(element)
        element.loads = []  # Initialize loads list
    
    # Load Case
    load_case = LoadCase("Ultimate Load")
    structure.add_load_case(load_case)
    
    # Various Loads เพื่อทดสอบการแสดงผล
    
    # 1. Concentrated loads at nodes
    load_n3_vertical = NodalLoad(
        load_case=load_case,
        node=n3,
        Fx=0.0,
        Fy=-100.0,  # 100kN downward
        Mz=0.0
    )
    n3.loads.append(load_n3_vertical)
    
    load_n4_horizontal = NodalLoad(
        load_case=load_case,
        node=n4,
        Fx=30.0,   # 30kN rightward
        Fy=0.0,
        Mz=0.0
    )
    n4.loads.append(load_n4_horizontal)
    
    load_n5_moment = NodalLoad(
        load_case=load_case,
        node=n5,
        Fx=0.0,
        Fy=0.0,
        Mz=25.0    # 25 kN⋅m moment
    )
    n5.loads.append(load_n5_moment)
    
    # 2. Uniform distributed load on beam
    uniform_load_e3 = UniformLoad(
        load_case=load_case,
        wx=0.0,
        wy=-15.0,  # 15 kN/m downward on beam
        label="BeamUniformLoad"
    )
    e3.loads.append(uniform_load_e3)
    
    # 3. Trapezoidal load on left rafter
    trap_load_e4 = TrapezoidalLoad(
        load_case=load_case,
        wx1=0.0, wy1=-8.0,   # Start: 8 kN/m 
        wx2=0.0, wy2=-12.0,  # End: 12 kN/m
        start_distance=0.5,   # Start 0.5m from beginning
        end_distance=4.0,     # End 4.0m from beginning
        label="RafterTrapLoad"
    )
    e4.loads.append(trap_load_e4)
    
    # 4. Uniform load on right rafter
    uniform_load_e5 = UniformLoad(
        load_case=load_case,
        wx=0.0,
        wy=-10.0,  # 10 kN/m perpendicular to rafter
        label="RafterUniformLoad"
    )
    e5.loads.append(uniform_load_e5)
    
    return structure


def main():
    print("=" * 60)
    print("PyFEALiTE - Enhanced Internal Forces Visualization")
    print("การแสดงผลแรงภายในที่ครบถ้วนพร้อม displacement")
    print("=" * 60)
    
    structure = create_enhanced_frame()
    
    print(f"\\nStructure: {structure.name}")
    print(f"Nodes: {len(structure.nodes)}")
    print(f"Elements: {len(structure.elements)}")
    
    # Count total loads
    total_loads = 0
    for node in structure.nodes:
        if hasattr(node, 'loads'):
            total_loads += len(node.loads)
    for element in structure.elements:
        if hasattr(element, 'loads'):
            total_loads += len(element.loads)
    print(f"Total Loads: {total_loads}")
    
    print("\\nLoad Details:")
    print("- Nodal loads: 100kN↓ at n3, 30kN→ at n4, 25kN⋅m at n5")
    print("- Beam uniform load: 15 kN/m on e3")
    print("- Rafter trapezoidal load: 8-12 kN/m on e4")
    print("- Rafter uniform load: 10 kN/m on e5")
    
    # Create enhanced visualization
    print("\\nสร้างกราฟแสดงผลแรงภายในแบบครบถ้วน...")
    
    fig = plot_structure_with_internal_forces(
        structure=structure,
        load_case=structure.load_cases[0],
        nfd_scale=0.015,          # NFD Scale Factor
        sfd_scale=0.020,          # SFD Scale Factor  
        bmd_scale=0.008,          # BMD Scale Factor
        displacement_scale=200.0, # Displacement Scale Factor (เพิ่มขึ้นเพื่อให้เห็นชัดเจน)
        diagram_offset=8.0,       # Diagrams Horizontal Offsets
        title="Enhanced Frame - Internal Forces with Displacement",
        figsize=(24, 16),         # ขนาดใหญ่สำหรับ 2×3 layout
        save_as="enhanced_internal_forces_complete.png"
    )
    
    import matplotlib.pyplot as plt
    plt.show()
    
    print("\\n✅ การแสดงผลเสร็จสมบูรณ์!")
    print("📁 ไฟล์ที่สร้าง: enhanced_internal_forces_complete.png")
    print("\\n🎯 คุณสมบัติที่แสดง:")
    print("  1. Structure Geometry - แสดงลูกศรและค่าแรงที่ใส่")
    print("  2. Normal Force Diagram (NFD) - พร้อมสีและค่า max/min")
    print("  3. Shear Force Diagram (SFD) - พร้อมสีและค่า max/min") 
    print("  4. Bending Moment Diagram (BMD) - ทุกชิ้นส่วน พร้อมสีและค่า max/min")
    print("  5. Displacement Diagram - แสดงรูปร่างเดิมและหลังเสียรูป")
    print("  6. Analysis Summary - สรุปผลการวิเคราะห์")
    print("\\n📊 Scale Factors ที่ใช้:")
    print(f"  - NFD Scale: 0.015")
    print(f"  - SFD Scale: 0.020")
    print(f"  - BMD Scale: 0.008")
    print(f"  - Displacement Scale: 200.0")
    print(f"  - Diagram Offset: 8.0")


if __name__ == "__main__":
    main()
