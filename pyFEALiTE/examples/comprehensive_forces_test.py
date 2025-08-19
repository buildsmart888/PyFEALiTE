#!/usr/bin/env python3
"""
การทดสอบระบบแสดงผลแรงภายในที่ได้รับการปรับปรุงครบถ้วน
Comprehensive test of enhanced internal forces visualization system.

ปรับปรุงตามข้อเสนอแนะ:
1. ตรวจสอบทิศทางลูกศรตาม LoadDirection.Global
2. แสดงแรง -50kN และแรงทุกประเภทพร้อม load case
3. ปรับปรุงกราฟแรงภายในพร้อมสเกลที่เหมาะสม  
4. เพิ่มข้อมูล material/section ใน analysis summary
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


def create_test_frame_with_comprehensive_loads():
    """สร้างโครงสร้างสำหรับทดสอบการแสดงผลแรงครบถ้วน"""
    
    structure = Structure(name="Comprehensive Test Frame")
    
    # Materials - หลายวัสดุเพื่อทดสอบ summary
    steel = IsotropicMaterial(
        E=200000,  # MPa
        nu=0.3,
        density_value=7850,
        label="Steel S355"
    )
    
    concrete = IsotropicMaterial(
        E=30000,   # MPa  
        nu=0.2,
        density_value=2400,
        label="Concrete C25"
    )
    
    # Sections - หลายหน้าตัดเพื่อทดสอบ summary
    steel_section = RectangularSection(
        material=steel,
        width=0.30,
        height=0.50,
        label="Steel_30x50"
    )
    
    concrete_section = RectangularSection(
        material=concrete,
        width=0.25,
        height=0.40,
        label="Concrete_25x40"
    )
    
    # Nodes
    n1 = Node2D(x=0.0, y=0.0, label="n1", restraints=[True, True, True])   # Fixed
    n2 = Node2D(x=6.0, y=0.0, label="n2", restraints=[True, True, False])  # Pin  
    n3 = Node2D(x=0.0, y=4.0, label="n3", restraints=[False, False, False]) # Free
    n4 = Node2D(x=6.0, y=4.0, label="n4", restraints=[False, False, False]) # Free
    
    nodes = [n1, n2, n3, n4]
    for node in nodes:
        structure.add_node(node)
        node.loads = []
    
    # Elements with different materials/sections
    e1 = FrameElement2D(n1, n3, concrete_section, "e1")  # Column - concrete
    e2 = FrameElement2D(n2, n4, concrete_section, "e2")  # Column - concrete  
    e3 = FrameElement2D(n3, n4, steel_section, "e3")     # Beam - steel
    
    elements = [e1, e2, e3]
    for element in elements:
        structure.add_element(element)
        element.loads = []
    
    # Load Case
    load_case = LoadCase("Test Load")
    structure.add_load_case(load_case)
    
    # === ทดสอบแรงทุกประเภทตาม LoadDirection.Global ===
    
    # 1. Nodal Load - แรง -50kN (ลง) ที่ n3
    load_n3_vertical = NodalLoad(
        load_case=load_case,
        node=n3,
        Fx=0.0,
        Fy=-50.0,  # -50kN แรงลง (Global Y direction)
        Mz=0.0
    )
    n3.loads.append(load_n3_vertical)
    
    # 2. Nodal Load - แรงแนวนอน 30kN (ขวา) ที่ n4
    load_n4_horizontal = NodalLoad(
        load_case=load_case,
        node=n4,
        Fx=30.0,   # 30kN แรงขวา (Global X direction)
        Fy=0.0,
        Mz=15.0    # 15 kN⋅m โมเมนต์
    )
    n4.loads.append(load_n4_horizontal)
    
    # 3. Uniform Load - แรงกระจายสม่ำเสมอบนคาน
    uniform_load_beam = UniformLoad(
        load_case=load_case,
        wx=0.0,     # ไม่มีแรงแนวนอน
        wy=-20.0,   # 20 kN/m แรงลง (Global Y direction)
        label="BeamUniformLoad"
    )
    e3.loads.append(uniform_load_beam)
    
    # 4. Trapezoidal Load - แรงกระจายแบบสามเหลี่ยมบนเสา e1
    trap_load_column = TrapezoidalLoad(
        load_case=load_case,
        wx1=5.0, wy1=0.0,    # เริ่มต้น: 5 kN/m แนวนอน
        wx2=15.0, wy2=0.0,   # สิ้นสุด: 15 kN/m แนวนอน (Global X direction)
        start_distance=0.5,   # เริ่มที่ 0.5m
        end_distance=3.5,     # สิ้นสุดที่ 3.5m
        label="ColumnTrapLoad"
    )
    e1.loads.append(trap_load_column)
    
    return structure


def main():
    print("=" * 70)
    print("PyFEALiTE - Comprehensive Internal Forces Visualization Test")
    print("การทดสอบระบบแสดงผลแรงภายในที่ปรับปรุงครบถ้วน")
    print("=" * 70)
    
    structure = create_test_frame_with_comprehensive_loads()
    
    print(f"\\nStructure: {structure.name}")
    print(f"Nodes: {len(structure.nodes)}")
    print(f"Elements: {len(structure.elements)}")
    
    # นับแรงทั้งหมด
    total_loads = 0
    nodal_loads = 0
    element_loads = 0
    
    for node in structure.nodes:
        if hasattr(node, 'loads'):
            nodal_loads += len(node.loads)
            total_loads += len(node.loads)
    
    for element in structure.elements:
        if hasattr(element, 'loads'):
            element_loads += len(element.loads)
            total_loads += len(element.loads)
    
    print(f"Total Loads: {total_loads} (Nodal: {nodal_loads}, Element: {element_loads})")
    
    print("\\n📋 Load Details (LoadDirection.Global):")
    print("  1. n3: -50.0 kN ↓ (Vertical Load)")
    print("  2. n4: 30.0 kN → + 15.0 kN⋅m ↻")
    print("  3. e3: 20.0 kN/m ↓ (Uniform)")
    print("  4. e1: 5-15 kN/m → (Trapezoidal)")
    
    print("\\n🏗️ Materials & Sections:")
    print("  • e1, e2: Concrete C25, 25×40 cm")
    print("  • e3: Steel S355, 30×50 cm")
    
    print("\\n🎯 สร้างกราฟแสดงผลแรงภายในแบบครบถ้วน...")
    
    # สร้างกราฟด้วยพารามิเตอร์ที่ปรับปรุง
    fig = plot_structure_with_internal_forces(
        structure=structure,
        load_case=structure.load_cases[0],
        nfd_scale=0.020,          # NFD Scale (ปรับให้เหมาะสม)
        sfd_scale=0.025,          # SFD Scale (ปรับให้เหมาะสม)
        bmd_scale=0.012,          # BMD Scale (ปรับให้เหมาะสม)
        displacement_scale=150.0, # Displacement Scale
        diagram_offset=6.0,       # Diagrams Horizontal Offsets
        title="Comprehensive Internal Forces Test - Enhanced Visualization",
        figsize=(26, 18),         # ขนาดใหญ่สำหรับรายละเอียด
        save_as="comprehensive_forces_enhanced.png"
    )
    
    import matplotlib.pyplot as plt
    plt.show()
    
    print("\\n✅ การทดสอบเสร็จสมบูรณ์!")
    print("📁 ไฟล์ที่สร้าง: comprehensive_forces_enhanced.png")
    
    print("\\n🎯 คุณสมบัติที่ได้รับการปรับปรุง:")
    print("  ✅ ทิศทางลูกศรตาม LoadDirection.Global")
    print("  ✅ แสดงแรง -50kN และแรงทุกประเภทพร้อม load case")
    print("  ✅ กราฟแรงภายในพร้อมสเกลที่เหมาะสม")
    print("  ✅ แสดงค่า max/min ของแต่ละชิ้นส่วน")
    print("  ✅ ข้อมูล material/section ใน analysis summary")
    
    print("\\n📊 การแสดงผลในกราฟ 2×3:")
    print("  1. Structure with Loads - ลูกศรและค่าแรงตาม Global")
    print("  2. Normal Force Diagram - สีและค่า max/min แต่ละชิ้นส่วน")
    print("  3. Shear Force Diagram - สีและค่า max/min แต่ละชิ้นส่วน")
    print("  4. Bending Moment Diagram - สีและค่า max/min แต่ละชิ้นส่วน")
    print("  5. Displacement Diagram - รูปเดิม vs เสียรูป")
    print("  6. Analysis Summary - รวมข้อมูล material และ section")


if __name__ == "__main__":
    main()
