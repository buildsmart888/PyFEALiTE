#!/usr/bin/env python3
"""
ตัวอย่างการสร้างกราฟแสดงผลแรงภายในแบบเดียวกับ C# FEALiTE2D
Example of creating internal force diagrams similar to C# FEALiTE2D output.

Features:
- Structure geometry with loads and dimensions
- Normal Force Diagram (NFD) with colors
- Shear Force Diagram (SFD) with colors  
- Bending Moment Diagram (BMD) with colors
- Max/Min values display
- Customizable scale factors
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyfealite.core.structure import Structure
from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.loads.point_load import PointLoad, NodalLoad
from pyfealite.loads.distributed_load import UniformLoad, TrapezoidalLoad
from pyfealite.loads.base import LoadCase
from pyfealite.visualization.structure_plot import plot_structure_with_internal_forces


def create_detailed_structure():
    """สร้างโครงสร้างตามตัวอย่าง C# FEALiTE2D"""
    
    # สร้าง Structure
    structure = Structure(name="2D Frame - Internal Forces Analysis")
    
    # สร้าง Material - Steel
    steel = IsotropicMaterial(
        E=30000,  # MPa (30 GPa)
        nu=0.2,
        density_value=7850,  # kg/m³
        label="Steel"
    )
    
    # สร้าง Cross Section - สี่เหลี่ยม 0.25x0.5 m
    section = RectangularSection(
        material=steel,
        width=0.25,  # m
        height=0.50,  # m
        label="Rect_25x50"
    )
    
    # สร้าง Nodes ตามพิกัดที่ถูกต้อง
    print("สร้าง Nodes...")
    n1 = Node2D(x=0.0, y=0.0, label="n1", restraints=[True, True, False])  # Pin support
    n2 = Node2D(x=9.0, y=0.0, label="n2", restraints=[False, True, False])  # Roller support
    n3 = Node2D(x=0.0, y=6.0, label="n3", restraints=[False, False, False])  # Free
    n4 = Node2D(x=9.0, y=6.0, label="n4", restraints=[False, False, False])  # Free  
    n5 = Node2D(x=0.0, y=12.0, label="n5", restraints=[False, False, False])  # Free
    
    nodes = [n1, n2, n3, n4, n5]
    for node in nodes:
        structure.add_node(node)
        node.loads = []  # Initialize loads list
    
    # สร้าง Elements
    print("สร้าง Elements...")
    e1 = FrameElement2D(n1, n3, section, "e1")  # เสาซ้าย ล่าง
    e2 = FrameElement2D(n2, n4, section, "e2")  # เสาขวา
    e3 = FrameElement2D(n3, n5, section, "e3")  # เสาซ้าย บน
    e4 = FrameElement2D(n3, n4, section, "e4")  # คาน
    e5 = FrameElement2D(n5, n4, section, "e5")  # คานเอียง
    
    elements = [e1, e2, e3, e4, e5]
    for element in elements:
        structure.add_element(element)
        element.loads = []  # Initialize loads list
    
    # สร้าง Load Cases
    dead_load = LoadCase("Dead Load")
    live_load = LoadCase("Live Load") 
    wind_load = LoadCase("Wind Load")
    
    structure.add_load_case(dead_load)
    structure.add_load_case(live_load)
    structure.add_load_case(wind_load)
    
    # เพิ่ม Loads
    print("เพิ่ม Loads...")
    
    # Dead Load Case  
    # แทน Support Displacement Load ด้วย NodalLoad ที่ n2 (แรงเทียบเท่า)
    equiv_force = NodalLoad(
        load_case=dead_load,
        node=n2,
        Fx=2.5,  # แรงเทียบเท่า 2.5kN ในแนว X
        Fy=0.0,
        Mz=0.0
    )
    n2.loads.append(equiv_force)
    
    # Point Load 40kN ที่ n5 ในทิศ UY (ลง)
    point_load_n5 = NodalLoad(
        load_case=dead_load,
        node=n5,
        Fx=0.0,
        Fy=-40.0,  # 40kN ลง
        Mz=0.0
    )
    n5.loads.append(point_load_n5)
    
    # Point Load 80kN ที่ n3 ในทิศ UY (ลง)  
    point_load_n3 = NodalLoad(
        load_case=dead_load,
        node=n3,
        Fx=0.0,
        Fy=-80.0,  # 80kN ลง
        Mz=0.0
    )
    n3.loads.append(point_load_n3)
    
    # Moment 7.5 kN.m ที่ n3
    moment_n3 = NodalLoad(
        load_case=dead_load,
        node=n3,
        Fx=0.0,
        Fy=0.0,
        Mz=7.5  # 7.5 kN.m
    )
    n3.loads.append(moment_n3)
    
    # Trapezoidal Load บน e4 (15 kN/m ถึง 7 kN/m)
    trap_load_e4 = TrapezoidalLoad(
        load_case=dead_load,
        wx1=0.0, wy1=-15.0,    # เริ่มต้น: 15 kN/m ลง
        wx2=0.0, wy2=-7.0,     # สิ้นสุด: 7 kN/m ลง
        start_distance=0.9,     # เริ่มที่ 0.9m จากจุดเริ่ม
        end_distance=6.3,       # สิ้นสุดที่ 6.3m จากจุดเริ่ม  
        label="TrapLoad_e4"
    )
    e4.loads.append(trap_load_e4)
    
    # Uniform Load บน e5 (12 kN/m)
    uniform_load_e5 = UniformLoad(
        load_case=dead_load,
        wx=0.0, wy=-12.0,  # 12 kN/m ลง
        label="UniformLoad_e5"
    )
    e5.loads.append(uniform_load_e5)
    
    print(f"โครงสร้างสร้างเสร็จแล้ว:")
    print(f"- จำนวน Nodes: {len(structure.nodes)}")
    print(f"- จำนวน Elements: {len(structure.elements)}")
    print(f"- จำนวน Load Cases: {len(structure.load_cases)}")
    
    # นับ loads ทั้งหมด
    total_loads = 0
    for node in structure.nodes:
        if hasattr(node, 'loads'):
            total_loads += len(node.loads)
    for element in structure.elements:
        if hasattr(element, 'loads'):
            total_loads += len(element.loads)
    print(f"- จำนวน Loads: {total_loads}")
    
    return structure


def main():
    """ฟังก์ชันหลักสำหรับสร้างและพล็อตกราฟแรงภายใน"""
    
    print("=" * 60)
    print("PyFEALiTE - Detailed Internal Forces Plot Example")
    print("ตัวอย่างการสร้างกราฟแสดงผลแรงภายในแบบละเอียด")
    print("=" * 60)
    
    # สร้างโครงสร้าง
    structure = create_detailed_structure()
    
    # สร้างกราฟแสดงผลแรงภายในแบบละเอียด
    print("\nสร้างกราฟแสดงผลแรงภายใน...")
    
    # ใช้พารามิเตอร์ตามที่ระบุ
    fig = plot_structure_with_internal_forces(
        structure=structure,
        load_case=structure.load_cases[0],  # Dead Load
        nfd_scale=0.01,                     # NFD Scale Factor
        sfd_scale=0.01,                     # SFD Scale Factor  
        bmd_scale=0.01,                     # BMD Scale Factor
        displacement_scale=1.0,             # Displacement Scale Factor
        diagram_offset=10.0,                # Diagrams Horizontal Offsets
        title="PyFEALiTE - Structural Analysis with Internal Forces",
        figsize=(20, 16),
        save_as="detailed_internal_forces_analysis.png"
    )
    
    # แสดงกราฟ
    import matplotlib.pyplot as plt
    plt.show()
    
    print("\n✅ สร้างกราฝแสดงผลแรงภายในเสร็จสิ้น!")
    print("📁 ไฟล์ที่สร้าง: detailed_internal_forces_analysis.png")
    print("\nคุณสมบัติของกราฟ:")
    print("- Structure Geometry with Loads and Dimensions")
    print("- Normal Force Diagram (NFD) with colors and max/min values")
    print("- Shear Force Diagram (SFD) with colors and max/min values") 
    print("- Bending Moment Diagram (BMD) with colors and max/min values")
    print("- Scale factors: NFD=0.01, SFD=0.01, BMD=0.01")
    print("- Displacement scale: 1.0")
    print("- Diagram offset: 10.0")


if __name__ == "__main__":
    main()
