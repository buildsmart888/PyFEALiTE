# PyFEALiTE Examples - ตัวอย่างการใช้งาน

ไดเรกทอรี่นี้มีตัวอย่างการใช้งาน PyFEALiTE ที่เทียบเท่ากับตัวอย่าง C# FEALiTE2D ใน README หลัก

## ตัวอย่างที่มี

### 1. `quick_start_thai.py` - เริ่มต้นใช้งาน
**ภาษาไทย | เหมาะสำหรับผู้เริ่มต้น**
- สร้างโครงสร้าง 2D frame เทียบเท่า C# README example
- แสดงขั้นตอนการสร้าง nodes, elements, materials
- การกำหนดโหลดและ boundary conditions
- มีคำอธิบายภาษาไทยที่ชัดเจน

```bash
python quick_start_thai.py
```

### 2. `readme_example.py` - ตัวอย่าง README ฉบับเต็ม
**ภาษาอังกฤษ | เทียบเท่าตัวอย่าง C# แบบสมบูรณ์**
- โครงสร้างเดียวกับ C# example ทุกประการ
- ครอบคลุมโหลดทุกประเภท: Point, Distributed, Nodal, Support Displacement
- แสดงการใช้ Generic2DSection เทียบเท่า C#
- มีคำอธิบายการใช้งาน plotting library

```bash
python readme_example.py
```

### 3. `complete_readme_example.py` - ตัวอย่างสมบูรณ์พร้อม Visualization
**ครบครัน | รวมการวิเคราะห์และแสดงผล**
- สร้างโครงสร้างเทียบเท่า README example
- รันการวิเคราะห์ (mock analysis)
- สร้างกราฟแสดงผลลัพธ์ 4 รูปแบบ:
  - Structure Geometry
  - Applied Loads  
  - Deformed Shape
  - Internal Forces (Moment Diagram)
- บันทึกผลลัพธ์เป็นไฟล์ PNG

```bash
python complete_readme_example.py
```

## โครงสร้างที่ใช้ในตัวอย่าง

```
    n5 (0,12)
    |
    |  e3
    |
    n3 (0,6) ----e4---- n4 (9,6)
    |                    |  \\
    |  e1                |   \\ e5
    |                    |    \\
    n1 (0,0) -------- n2 (9,0)  n5 (0,12)
       ^^                ^^
    (Fixed)           (Fixed)
```

**คุณสมบัติ:**
- 5 nodes: 2 base supports (fully restrained), 3 upper nodes
- 5 elements: 2 columns, 2 beams, 1 inclined member
- Steel material: E = 30 GPa, ν = 0.2
- Various loads: horizontal forces, distributed loads, point loads

## ความแตกต่างจาก C# FEALiTE2D

| Feature | C# FEALiTE2D | PyFEALiTE |
|---------|--------------|-----------|
| Language | C# | Python |
| Plotting | DXF export | Matplotlib |
| Sections | Generic2DSection | RectangularSection/GenericSection |
| Load Input | Global/Local coordinates | Similar approach |
| Analysis | Built-in solver | Similar functionality |
| Output | DXF diagrams | PNG/interactive plots |

## การใช้งานขั้นพื้นฐาน

```python
# 1. Import modules
from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D
from pyfealite.core.structure import Structure
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection

# 2. สร้างโครงสร้าง
structure = Structure("My_Frame")

# 3. สร้าง nodes และ boundary conditions
n1 = Node2D(x=0, y=0, label="base_left")
n1.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY, NodalDegreeOfFreedom.RZ)

# 4. สร้าง materials และ sections
steel = IsotropicMaterial.steel("S355")
section = RectangularSection(steel, width=0.3, height=0.4)

# 5. สร้าง elements
beam = FrameElement2D(n1, n2, section, "beam_1")

# 6. กำหนดโหลด
from pyfealite.loads.base import LoadCase, LoadType
load_case = LoadCase("Live Load", LoadType.LIVE)

# 7. วิเคราะห์
structure.solve()

# 8. แสดงผลลัพธ์
from pyfealite.visualization import StructurePlotter
plotter = StructurePlotter(structure)
plotter.plot_results(load_case)
```

## ข้อกำหนดระบบ

- Python 3.8+
- numpy
- matplotlib
- scipy (สำหรับการวิเคราะห์)

## การติดตั้ง PyFEALiTE

```bash
# From source (development)
cd pyFEALiTE
pip install -e .

# Or install requirements
pip install -r requirements.txt
```

## หมายเหตุสำหรับผู้พัฒนา

ตัวอย่างเหล่านี้ออกแบบมาเพื่อ:
1. **แสดงความเท่าเทียม** - PyFEALiTE สามารถทำงานเทียบเท่า C# FEALiTE2D
2. **การเรียนรู้** - เป็นจุดเริ่มต้นสำหรับผู้ใช้ใหม่
3. **การทดสอบ** - ใช้เป็น reference สำหรับการพัฒนา API
4. **เอกสารประกอบ** - อธิบายการใช้งาน features ต่างๆ

## ผลลัพธ์ที่คาดหวัง

เมื่อรันตัวอย่างสำเร็จ จะได้:
- โครงสร้างที่สร้างเสร็จสมบูรณ์
- การแสดงข้อมูลโครงสร้างใน console
- กราฟแสดงผลลัพธ์ (สำหรับ complete example)
- ไฟล์รูปภาพบันทึกใน `demo_exports/`

## การแก้ไขปัญหา

หากพบข้อผิดพลาด:
1. ตรวจสอบการติดตั้ง dependencies
2. ให้แน่ใจว่า Python path ถูกต้อง
3. ตรวจสอบ PyFEALiTE modules ใน `src/` directory
4. อ่านข้อความ error ใน console

## ลิงค์ที่เกี่ยวข้อง

- [FEALiTE2D Original (C#)](https://github.com/FEALiTE/FEALiTE2D)
- [PyFEALiTE Documentation](../docs/)
- [PyFEALiTE Tests](../tests/)
