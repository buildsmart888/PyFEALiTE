"""
PyFEALiTE - Quick Start Example
เทียบเท่ากับตัวอย่าง C# ใน README

ตัวอย่างนี้สาธิตการสร้างโครงสร้าง 2D frame ที่เหมือนกับตัวอย่างใน C# README
โดยใช้ PyFEALiTE Python library

โครงสร้าง:
- กรอบ 2 ชั้น ขนาด 9m x 12m
- 5 nodes: 2 base supports (ยึดแน่น), 3 nodes ชั้นบน  
- 5 elements: เสา 2 ต้น, คาน 2 เส้น, สมาชิกเอียง 1 เส้น
- โหลดหลายประเภท: point loads, distributed loads, nodal loads

หน่วย: kN, m
"""

import sys
from pathlib import Path

# เพิ่ม src path สำหรับ development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import PyFEALiTE modules
from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D
from pyfealite.core.structure import Structure
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.loads.base import LoadCase, LoadType
from pyfealite.loads.point_load import NodalLoad
from pyfealite.loads.distributed_load import UniformLoad


def สร้างโครงสร้าง():
    """สร้างโครงสร้างเทียบเท่า C# README example"""
    
    print("สร้างโครงสร้าง PyFEALiTE - ตัวอย่าง README")
    print("=" * 50)
    
    # 1. สร้าง Structure
    structure = Structure("โครงสร้าง_README_Example")
    
    # 2. สร้าง Material (เหล็ก)
    เหล็ก = IsotropicMaterial(
        E=30e6,              # Young's modulus = 30 GPa (kN/m²)
        nu=0.2,              # Poisson's ratio = 0.2
        density_value=7850,  # ความหนาแน่น kg/m³
        alpha=12e-6,         # สัมประสิทธิ์การขยายตัว /°C
        label="เหล็ก"
    )
    
    # 3. สร้าง Cross Section
    หน้าตัด = RectangularSection(
        material=เหล็ก,
        width=0.3,      # กว้าง 30 cm
        height=0.4,     # สูง 40 cm
        label="30x40cm"
    )
    
    print(f"วัสดุ: {เหล็ก.label}")
    print(f"  E = {เหล็ก.E/1e9:.0f} GPa")
    print(f"  ν = {เหล็ก.nu}")
    print(f"หน้าตัด: {หน้าตัด.label}")
    print(f"  A = {หน้าตัด.A:.4f} m²")
    print(f"  I = {หน้าตัด.Iz:.2e} m⁴")
    
    # 4. สร้าง Nodes (จุดต่อ)
    # ตำแหน่งเดียวกับ C# example
    n1 = Node2D(x=0, y=0, label="ฐาน_ซ้าย")      # ฐานซ้าย
    n2 = Node2D(x=9, y=0, label="ฐาน_ขวา")       # ฐานขวา
    n3 = Node2D(x=0, y=6, label="ชั้น1_ซ้าย")     # ชั้น 1 ซ้าย
    n4 = Node2D(x=9, y=6, label="ชั้น1_ขวา")      # ชั้น 1 ขวา
    n5 = Node2D(x=0, y=12, label="ชั้น2_ซ้าย")    # ชั้น 2 ซ้าย
    
    print(f"\\nสร้าง Nodes:")
    for node in [n1, n2, n3, n4, n5]:
        print(f"  {node.label}: ({node.x:2.0f}, {node.y:2.0f})")
    
    # 5. กำหนด Boundary Conditions (เงื่อนไขขอบ)
    # ยึดฐานทั้งสองข้างแน่น (fully restrained)
    n1.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY, NodalDegreeOfFreedom.RZ)
    n2.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY, NodalDegreeOfFreedom.RZ)
    
    print(f"\\nเงื่อนไขขอบ:")
    print(f"  {n1.label}: ยึดแน่นทุกทิศทาง (UX, UY, RZ)")
    print(f"  {n2.label}: ยึดแน่นทุกทิศทาง (UX, UY, RZ)")
    
    # เพิ่ม nodes เข้า structure
    structure.add_node(n1, n2, n3, n4, n5)
    
    # 6. สร้าง Elements (สมาชิก)
    # การเชื่อมต่อเดียวกับ C# example
    e1 = FrameElement2D(n1, n3, หน้าตัด, "เสา_ซ้าย_ล่าง")     # เสาซ้าย ช่วงล่าง
    e2 = FrameElement2D(n2, n4, หน้าตัด, "เสา_ขวา_ล่าง")      # เสาขวา ช่วงล่าง
    e3 = FrameElement2D(n3, n5, หน้าตัด, "เสา_ซ้าย_บน")       # เสาซ้าย ช่วงบน
    e4 = FrameElement2D(n3, n4, หน้าตัด, "คาน_ชั้น1")         # คาน ชั้น 1
    e5 = FrameElement2D(n4, n5, หน้าตัด, "คาน_เอียง")         # คานเอียง
    
    elements = [e1, e2, e3, e4, e5]
    
    print(f"\\nสร้าง Elements:")
    for element in elements:
        element.loads = []  # กำหนด list สำหรับโหลด
        structure.add_element(element)
        print(f"  {element.label}: {element.start_node.label} -> {element.end_node.label} "
              f"(ยาว = {element.length:.2f} m)")
    
    return structure, เหล็ก, หน้าตัด, (n1, n2, n3, n4, n5), (e1, e2, e3, e4, e5)


def กำหนดโหลด(structure, nodes, elements):
    """กำหนดโหลดต่างๆ ให้กับโครงสร้าง"""
    
    n1, n2, n3, n4, n5 = nodes
    e1, e2, e3, e4, e5 = elements
    
    # สร้าง Load Case
    live_load = LoadCase("Live Load", LoadType.LIVE)
    structure.add_load_case(live_load)
    
    print(f"\\nกำหนดโหลด สำหรับ Load Case: {live_load.name}")
    print("-" * 30)
    
    # เตรียม nodal loads สำหรับทุก node
    for node in nodes:
        if not hasattr(node, 'loads'):
            node.loads = []
    
    # 1. โหลดแนวนอนที่จุดต่อ (เทียบเท่า C# example)
    horizontal_loads = [
        (n3, 80, 0, 0, "80 kN แนวนอนที่ชั้น 1 ซ้าย"),
        (n5, 40, 0, 0, "40 kN แนวนอนที่ชั้น 2 ซ้าย"),
        (n1, 40, 0, 0, "40 kN แนวนอนที่ฐานซ้าย"),
    ]
    
    print("1. โหลดแนวนอนที่จุดต่อ:")
    for node, fx, fy, mz, description in horizontal_loads:
        load = NodalLoad(
            load_case=live_load,
            node=node,
            Fx=fx, Fy=fy, Mz=mz,
            label=f"Horizontal_Load_{node.label}"
        )
        node.loads.append(load)
        print(f"   {description}")
    
    # 2. โหลดกระจายบนคาน (เทียบเท่า FrameUniformLoad ใน C#)
    print("\\n2. โหลดกระจายบนคาน:")
    beam_load = UniformLoad(
        load_case=live_load,
        wx=0,           # ไม่มีโหลดแนวนอน
        wy=-15,         # โหลด 15 kN/m ลงล่าง
        label="โหลดคาน_UDL"
    )
    e4.loads.append(beam_load)
    print(f"   คาน {e4.label}: โหลดกระจาย {beam_load.wy} kN/m ลงล่าง")
    
    # 3. โหลดจุดบนเสา (เทียบเท่า FramePointLoad ใน C#)
    print("\\n3. โหลดจุดบนเสา:")
    from pyfealite.loads.point_load import PointLoad
    
    point_load = PointLoad(
        load_case=live_load,
        Fx=0,
        Fy=-25,         # โหลด 25 kN ลงล่าง
        Mz=0,
        distance=e3.length / 2,  # ที่กึ่งกลางเสา
        label="โหลดจุด_เสา"
    )
    e3.loads.append(point_load)
    print(f"   เสา {e3.label}: โหลดจุด {point_load.Fy} kN ที่กึ่งกลาง")
    
    return live_load


def แสดงสรุปโครงสร้าง(structure, load_case):
    """แสดงสรุปข้อมูลโครงสร้าง"""
    
    print(f"\\n" + "=" * 50)
    print("สรุปโครงสร้าง")
    print("=" * 50)
    
    print(f"ชื่อโครงสร้าง: {structure.name}")
    print(f"จำนวน Nodes: {len(structure.nodes)}")
    print(f"จำนวน Elements: {len(structure.elements)}")
    print(f"จำนวน Load Cases: {len(structure.load_cases)}")
    
    # คำนวณ DOFs
    total_dofs = sum(node.dof_count for node in structure.nodes)
    print(f"จำนวน DOFs รวม: {total_dofs}")
    
    print(f"\\nNodes และ Restraints:")
    for node in structure.nodes:
        restraints = "".join("R" if r else "F" for r in node.restraints)
        print(f"  {node.label}: ({node.x:2.0f}, {node.y:2.0f}) [{restraints}] - {node.dof_count} DOFs")
    
    print(f"\\nElements:")
    for element in structure.elements:
        print(f"  {element.label}: {element.start_node.label} -> {element.end_node.label} "
              f"(L = {element.length:.2f} m)")
    
    print(f"\\nLoad Summary สำหรับ {load_case.name}:")
    
    # นับโหลด
    nodal_load_count = 0
    element_load_count = 0
    
    for node in structure.nodes:
        if hasattr(node, 'loads'):
            nodal_load_count += len([l for l in node.loads if l.load_case == load_case])
    
    for element in structure.elements:
        if hasattr(element, 'loads'):
            element_load_count += len([l for l in element.loads if l.load_case == load_case])
    
    print(f"  โหลดที่จุดต่อ: {nodal_load_count} โหลด")
    print(f"  โหลดบน Element: {element_load_count} โหลด")


def main():
    """ฟังก์ชันหลักสำหรับรันตัวอย่าง"""
    
    print("PyFEALiTE - ตัวอย่างการใช้งาน")
    print("เทียบเท่ากับ C# FEALiTE2D README example")
    print()
    
    try:
        # ขั้นตอน 1: สร้างโครงสร้าง
        structure, เหล็ก, หน้าตัด, nodes, elements = สร้างโครงสร้าง()
        
        # ขั้นตอน 2: กำหนดโหลด
        load_case = กำหนดโหลด(structure, nodes, elements)
        
        # ขั้นตอน 3: แสดงสรุป
        แสดงสรุปโครงสร้าง(structure, load_case)
        
        print(f"\\n" + "=" * 50)
        print("🎉 สร้างโครงสร้าง PyFEALiTE สำเร็จ!")
        print("=" * 50)
        
        print("\\nขั้นตอนต่อไป:")
        print("1. เรียก structure.solve() เพื่อวิเคราะห์")
        print("2. ใช้เครื่องมือ visualization เพื่อดูผลลัพธ์")
        print("3. ดึงค่า forces, displacements และ reactions")
        
        print("\\nการใช้งาน Visualization:")
        print("""
from pyfealite.visualization import StructurePlotter

# สร้าง plotter
plotter = StructurePlotter(structure)

# วาดรูปโครงสร้าง
plotter.plot_geometry()
plotter.plot_loads(load_case)
plotter.plot_deformed_shape(load_case)  # หลังจาก solve()
plotter.plot_internal_forces(load_case) # หลังจาก solve()
        """)
        
        return structure, load_case
        
    except Exception as e:
        print(f"\\n❌ เกิดข้อผิดพลาด: {e}")
        print("กรุณาตรวจสอบว่าได้ติดตั้ง PyFEALiTE modules ครบถ้วนแล้ว")
        return None, None


if __name__ == "__main__":
    structure, load_case = main()
