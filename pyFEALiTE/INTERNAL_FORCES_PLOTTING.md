# PyFEALiTE Internal Forces Plotting

## ภาพรวม

ฟังก์ชันใหม่สำหรับการสร้างกราฟแสดงผลแรงภายในแบบเดียวกับ C# FEALiTE2D พร้อมกับการปรับแต่งระดับละเอียดและสีสันต่าง ๆ

## ฟีเจอร์หลัก

### ฟังก์ชัน `plot_structure_with_internal_forces()`

สร้างกราฟแสดงผลแรงภายในแบบครบถ้วน 4 แผงในรูปแบบ 2×2:

1. **Structure Geometry with Loads** - โครงสร้างพร้อมแรงที่กระทำและมิติ
2. **Normal Force Diagram (NFD)** - แผนภาพแรงแกน พร้อมสีและค่า max/min
3. **Shear Force Diagram (SFD)** - แผนภาพแรงเฉือน พร้อมสีและค่า max/min  
4. **Bending Moment Diagram (BMD)** - แผนภาพโมเมนต์ดัด พร้อมสีและค่า max/min

### พารามิเตอร์ที่สำคัญ

```python
plot_structure_with_internal_forces(
    structure: Structure,                    # โครงสร้างที่ต้องการวิเคราะห์
    load_case: Optional[LoadCase] = None,    # Load case ที่ต้องการแสดง
    nfd_scale: float = 0.01,                # Scale factor สำหรับ NFD
    sfd_scale: float = 0.01,                # Scale factor สำหรับ SFD  
    bmd_scale: float = 0.01,                # Scale factor สำหรับ BMD
    displacement_scale: float = 1.0,        # Scale factor สำหรับ displacement
    diagram_offset: float = 10.0,           # Horizontal offset สำหรับ diagrams
    title: str = "",                        # ชื่อกราฟ
    figsize: Tuple[float, float] = (16, 12), # ขนาดรูปภาพ
    save_as: Optional[str] = None           # ชื่อไฟล์สำหรับบันทึก
) -> plt.Figure
```

## คุณสมบัติเด่น

### 1. สีสันตามประเภทแรง
- **NFD**: สีม่วง (Magenta), ฟ้า (Cyan), น้ำเงิน (Blue)
- **SFD**: สีฟ้า (Cyan) พร้อมขอบน้ำเงิน
- **BMD**: สีแดง (Red) พร้อมขอบแดงเข้ม

### 2. แสดงค่า Max/Min
- แสดงค่าสูงสุดและต่ำสุดใน box สีแดงและน้ำเงิน
- ตำแหน่งที่มุมบนซ้ายของแต่ละกราฟ

### 3. Dimension Lines
- เส้นมิติแนวนอนและแนวตั้ง
- แสดงขนาดโครงสร้างพร้อมค่าตัวเลข

### 4. Support Symbols
- Fixed support: สี่เหลี่ยมพร้อมเส้นแฮทช์
- Pin support: สามเหลี่ยมสีเทา
- Roller support: สามเหลี่ยมพร้อมล้อเลื่อน

### 5. Load Visualization
- Point loads: ลูกศรสีแดง
- Distributed loads: ลูกศรสีส้มต่อเนื่อง
- Nodal loads: แสดงที่ตำแหน่ง node

## ตัวอย่างการใช้งาน

### ตัวอย่างพื้นฐาน

```python
from pyfealite.visualization.structure_plot import plot_structure_with_internal_forces

# สร้างกราฟแสดงผลแรงภายใน
fig = plot_structure_with_internal_forces(
    structure=my_structure,
    load_case=dead_load,
    nfd_scale=0.01,
    sfd_scale=0.01, 
    bmd_scale=0.01,
    title="Structural Analysis Results",
    save_as="my_analysis.png"
)

# แสดงกราฟ
import matplotlib.pyplot as plt
plt.show()
```

### ตัวอย่างขั้นสูง

```python
# ปรับ scale factors สำหรับโครงสร้างขนาดใหญ่
fig = plot_structure_with_internal_forces(
    structure=large_structure,
    load_case=wind_load,
    nfd_scale=0.005,      # NFD เล็กลง
    sfd_scale=0.008,      # SFD ปานกลาง
    bmd_scale=0.002,      # BMD เล็กมาก
    displacement_scale=50.0,  # ขยายการเคลื่อนที่
    diagram_offset=20.0,  # เพิ่มระยะห่าง
    figsize=(20, 16),     # ขนาดใหญ่ขึ้น
    title="Large Structure Analysis",
    save_as="large_structure_forces.png"
)
```

## ไฟล์ตัวอย่าง

### 1. `simple_internal_forces_test.py`
- ตัวอย่างพื้นฐานสำหรับโครงสร้างง่าย ๆ
- Portal frame พร้อม point load และ uniform load

### 2. `detailed_internal_forces_plot.py`  
- ตัวอย่างขั้นสูงที่เลียนแบบ C# FEALiTE2D README
- โครงสร้าง 5 nodes, 5 elements
- หลาย load types: nodal loads, distributed loads

## การปรับแต่งสีและรูปแบบ

### ปรับสีใน source code

ใน `structure_plot.py` สามารถปรับสีได้ที่:

```python
# สำหรับ NFD
colors_nf = ['magenta', 'cyan', 'magenta', 'blue', 'magenta']

# สำหรับ SFD  
ax.fill(poly_x, poly_y, color='cyan', alpha=0.6, edgecolor='blue')

# สำหรับ BMD
ax.fill(poly_x, poly_y, color='red', alpha=0.6, edgecolor='darkred')
```

### ปรับขนาด scale factors

- `nfd_scale = 0.01`: เหมาะสำหรับแรงแกน 50-200 kN
- `sfd_scale = 0.01`: เหมาะสำหรับแรงเฉือน 20-100 kN  
- `bmd_scale = 0.01`: เหมาะสำหรับโมเมนต์ 50-200 kN⋅m

## ข้อจำกัดปัจจุบัน

1. **Mock Data**: ยังใช้ข้อมูลจำลองสำหรับแสดงผล จำเป็นต้องเชื่อมต่อกับ solver จริง
2. **Static Values**: ค่า max/min เป็นค่าคงที่ ต้องคำนวณจากผลการวิเคราะห์จริง
3. **Element Types**: รองรับเฉพาะ FrameElement2D

## การพัฒนาในอนาคต

1. **Integration with Solver**: เชื่อมต่อกับ structural analysis solver
2. **Interactive Plots**: ใช้ Plotly สำหรับกราฟแบบ interactive
3. **Animation**: แสดงผลการเปลี่ยนแปลงตามเวลา
4. **3D Visualization**: รองรับโครงสร้าง 3 มิติ

## การติดตั้งและใช้งาน

```bash
# รันตัวอย่าง
cd pyFEALiTE
python examples/simple_internal_forces_test.py
python examples/detailed_internal_forces_plot.py
```

ผลลัพธ์จะถูกบันทึกเป็นไฟล์ PNG ในโฟลเดอร์ปัจจุบัน และแสดงในหน้าต่าง matplotlib

---

**หมายเหตุ**: ฟังก์ชันนี้ออกแบบมาให้เหมือนกับ C# FEALiTE2D plotting ให้มากที่สุด รวมถึงสีสัน รูปแบบ และการแสดงค่าต่าง ๆ
