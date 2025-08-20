"""
PyFEALiTE Frame Analysis Example
===============================

This example demonstrates a complete 2D frame analysis using PyFEALiTE
with visualization of:
1. Frame geometry
2. Dead load application
3. Live load application  
4. Wind load application
5. Deformed shapes for each load case
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from pyfealite.core.node import Node2D
from pyfealite.core.structure import Structure
from pyfealite.core.element import FrameElement2D
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.materials.base import MaterialType
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.loads.base import LoadCase, LoadDirection
from pyfealite.loads.point_load import NodalLoad

print("🏗️ PyFEALiTE Frame Analysis Example")
print("=" * 50)

# Create materials
print("📊 Creating materials...")
steel = IsotropicMaterial(
    E=200000,  # MPa
    nu=0.3,
    density_value=7850,  # kg/m³
    material_type=MaterialType.STEEL,
    label="Steel S355"
)

concrete = IsotropicMaterial(
    E=30000,   # MPa
    nu=0.2,
    density_value=2400,  # kg/m³
    material_type=MaterialType.CONCRETE,
    label="Concrete C30"
)

print(f"   ✅ Steel: E={steel.E} MPa, G={steel.G:.0f} MPa")
print(f"   ✅ Concrete: E={concrete.E} MPa, G={concrete.G:.0f} MPa")

# Create sections
print("📐 Creating cross-sections...")
beam_section = RectangularSection(
    material=steel,
    width=300,
    height=600,
    label="Beam 300x600"
)

column_section = RectangularSection(
    material=concrete,
    width=400,
    height=400,
    label="Column 400x400"
)

print(f"   ✅ Beam: A={beam_section.A:.0f} mm², Iz={beam_section.Iz:.0e} mm⁴")
print(f"   ✅ Column: A={column_section.A:.0f} mm², Iz={column_section.Iz:.0e} mm⁴")

# Create 2-story frame structure
print("🏗️ Creating 2-story frame structure...")
structure = Structure(name="2-Story Office Building Frame")

# Define coordinates (in mm)
bay_width = 6000    # 6m
story_height = 3500 # 3.5m

# Create nodes
nodes = []
node_labels = []

# Ground floor nodes
for i in range(3):  # 3 columns
    x = i * bay_width
    y = 0
    label = f"N{i+1}"
    node = Node2D(x, y, label, restraints=[True, True, True])  # Fixed supports
    nodes.append(node)
    node_labels.append(label)
    structure.add_node(node)

# First floor nodes  
for i in range(3):
    x = i * bay_width
    y = story_height
    label = f"N{i+4}"
    node = Node2D(x, y, label)
    nodes.append(node)
    node_labels.append(label)
    structure.add_node(node)

# Second floor nodes
for i in range(3):
    x = i * bay_width
    y = 2 * story_height
    label = f"N{i+7}"
    node = Node2D(x, y, label)
    nodes.append(node)
    node_labels.append(label)
    structure.add_node(node)

print(f"   ✅ Created {len(nodes)} nodes")

# Create elements
elements = []

# Ground floor columns
for i in range(3):
    start_node = nodes[i]      # Ground nodes
    end_node = nodes[i+3]      # First floor nodes
    label = f"Col{i+1}_GF"
    element = FrameElement2D(start_node, end_node, column_section, label)
    elements.append(element)
    structure.add_element(element)

# First floor columns
for i in range(3):
    start_node = nodes[i+3]    # First floor nodes
    end_node = nodes[i+6]      # Second floor nodes
    label = f"Col{i+1}_1F"
    element = FrameElement2D(start_node, end_node, column_section, label)
    elements.append(element)
    structure.add_element(element)

# First floor beams
for i in range(2):
    start_node = nodes[i+3]    # First floor nodes
    end_node = nodes[i+4]      # Adjacent first floor node
    label = f"Beam{i+1}_1F"
    element = FrameElement2D(start_node, end_node, beam_section, label)
    elements.append(element)
    structure.add_element(element)

# Second floor beams
for i in range(2):
    start_node = nodes[i+6]    # Second floor nodes
    end_node = nodes[i+7]      # Adjacent second floor node
    label = f"Beam{i+1}_2F"
    element = FrameElement2D(start_node, end_node, beam_section, label)
    elements.append(element)
    structure.add_element(element)

print(f"   ✅ Created {len(elements)} elements")
print(f"   📊 Structure: {len(structure.nodes)} nodes, {len(structure.elements)} elements")

# Create load cases
print("🎯 Creating load cases...")

dead_load_case = LoadCase("Dead Load", 1.0)
live_load_case = LoadCase("Live Load", 1.0)
wind_load_case = LoadCase("Wind Load", 1.0)

# Dead loads (gravity loads on beams)
dead_loads = []
# First floor beams - distributed load converted to point loads
for i in [3, 4]:  # First floor middle nodes
    load = NodalLoad(
        load_case=dead_load_case,
        node=nodes[i],
        Fx=0,
        Fy=-15000,  # 15 kN downward
        Mz=0,
        direction=LoadDirection.GLOBAL,
        label=f"Dead_1F_N{i+1}"
    )
    dead_loads.append(load)

# Second floor beams
for i in [6, 7]:  # Second floor middle nodes
    load = NodalLoad(
        load_case=dead_load_case,
        node=nodes[i],
        Fx=0,
        Fy=-12000,  # 12 kN downward
        Mz=0,
        direction=LoadDirection.GLOBAL,
        label=f"Dead_2F_N{i+1}"
    )
    dead_loads.append(load)

# Live loads (occupancy loads)
live_loads = []
# First floor
for i in [3, 4]:  # First floor nodes
    load = NodalLoad(
        load_case=live_load_case,
        node=nodes[i],
        Fx=0,
        Fy=-8000,   # 8 kN downward
        Mz=0,
        direction=LoadDirection.GLOBAL,
        label=f"Live_1F_N{i+1}"
    )
    live_loads.append(load)

# Second floor
for i in [6, 7]:  # Second floor nodes
    load = NodalLoad(
        load_case=live_load_case,
        node=nodes[i],
        Fx=0,
        Fy=-6000,   # 6 kN downward
        Mz=0,
        direction=LoadDirection.GLOBAL,
        label=f"Live_2F_N{i+1}"
    )
    live_loads.append(load)

# Wind loads (lateral loads)
wind_loads = []
# Wind pressure on left side of building
for i in [3, 6]:  # Left column nodes (first and second floor)
    load = NodalLoad(
        load_case=wind_load_case,
        node=nodes[i],
        Fx=5000,    # 5 kN horizontal (wind from left)
        Fy=0,
        Mz=0,
        direction=LoadDirection.GLOBAL,
        label=f"Wind_Left_N{i+1}"
    )
    wind_loads.append(load)

print(f"   ✅ Created {len(dead_loads)} dead loads")
print(f"   ✅ Created {len(live_loads)} live loads") 
print(f"   ✅ Created {len(wind_loads)} wind loads")

# Visualization functions
def create_frame_geometry_plot():
    """Create frame geometry visualization."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Plot elements
    for element in elements:
        x1, y1 = element.start_node.x/1000, element.start_node.y/1000  # Convert to meters
        x2, y2 = element.end_node.x/1000, element.end_node.y/1000
        
        if "Col" in element.label:
            ax.plot([x1, x2], [y1, y2], 'b-', linewidth=8, label='Columns' if element == elements[0] else "")
        else:
            ax.plot([x1, x2], [y1, y2], 'r-', linewidth=6, label='Beams' if "Beam1" in element.label else "")
    
    # Plot nodes
    for i, node in enumerate(nodes):
        x, y = node.x/1000, node.y/1000
        if node.restraints == [True, True, True]:  # Fixed support
            ax.plot(x, y, 's', markersize=12, color='green', markerfacecolor='lightgreen')
            ax.text(x, y-0.3, node.label, ha='center', va='top', fontweight='bold')
        else:
            ax.plot(x, y, 'o', markersize=10, color='black', markerfacecolor='yellow')
            ax.text(x, y+0.2, node.label, ha='center', va='bottom', fontweight='bold')
    
    # Add dimensions
    ax.annotate('', xy=(6, -0.5), xytext=(0, -0.5), 
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(3, -0.7, '6.0 m', ha='center', va='top', fontsize=10, fontweight='bold')
    
    ax.annotate('', xy=(12, -0.5), xytext=(6, -0.5), 
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(9, -0.7, '6.0 m', ha='center', va='top', fontsize=10, fontweight='bold')
    
    ax.annotate('', xy=(-0.5, 3.5), xytext=(-0.5, 0), 
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(-0.8, 1.75, '3.5 m', ha='center', va='center', rotation=90, fontsize=10, fontweight='bold')
    
    ax.annotate('', xy=(-0.5, 7.0), xytext=(-0.5, 3.5), 
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(-0.8, 5.25, '3.5 m', ha='center', va='center', rotation=90, fontsize=10, fontweight='bold')
    
    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(-1.5, 8.5)
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, fontweight='bold')
    ax.set_title('PyFEALiTE - 2-Story Frame Geometry', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=12)
    ax.set_aspect('equal')
    
    # Add info box
    info_text = f"""Structure Information:
• Nodes: {len(nodes)}
• Elements: {len(elements)}  
• Beam Section: {beam_section.label}
• Column Section: {column_section.label}
• Steel E = {steel.E:,.0f} MPa
• Concrete E = {concrete.E:,.0f} MPa"""
    
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7)
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=bbox_props)
    
    plt.tight_layout()
    plt.savefig('frame_geometry.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("   ✅ Saved frame_geometry.png")

def create_load_visualization(loads, load_case_name, filename, color='red'):
    """Create load visualization."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Plot frame structure (lighter)
    for element in elements:
        x1, y1 = element.start_node.x/1000, element.start_node.y/1000
        x2, y2 = element.end_node.x/1000, element.end_node.y/1000
        
        if "Col" in element.label:
            ax.plot([x1, x2], [y1, y2], 'lightgray', linewidth=4, alpha=0.7)
        else:
            ax.plot([x1, x2], [y1, y2], 'lightgray', linewidth=3, alpha=0.7)
    
    # Plot nodes (smaller)
    for node in nodes:
        x, y = node.x/1000, node.y/1000
        if node.restraints == [True, True, True]:
            ax.plot(x, y, 's', markersize=8, color='gray', alpha=0.7)
        else:
            ax.plot(x, y, 'o', markersize=6, color='gray', alpha=0.7)
        ax.text(x, y+0.2, node.label, ha='center', va='bottom', fontsize=8, alpha=0.7)
    
    # Plot loads
    max_force = max([abs(load.Fx) for load in loads] + [abs(load.Fy) for load in loads] + [0.1])
    scale_factor = 2.0 / max_force  # Scale arrows
    
    for load in loads:
        x, y = load.node.x/1000, load.node.y/1000
        
        # Force arrows
        if abs(load.Fx) > 0:
            dx = load.Fx * scale_factor
            ax.arrow(x, y, dx, 0, head_width=0.15, head_length=0.1, 
                    fc=color, ec=color, linewidth=3, alpha=0.8)
            ax.text(x + dx/2, y + 0.3, f'{load.Fx/1000:.1f} kN', 
                   ha='center', va='bottom', fontweight='bold', color=color)
        
        if abs(load.Fy) > 0:
            dy = load.Fy * scale_factor
            ax.arrow(x, y, 0, dy, head_width=0.15, head_length=0.1, 
                    fc=color, ec=color, linewidth=3, alpha=0.8)
            ax.text(x + 0.3, y + dy/2, f'{abs(load.Fy)/1000:.1f} kN', 
                   ha='left', va='center', fontweight='bold', color=color)
    
    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(-1.5, 8.5)
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, fontweight='bold')
    ax.set_title(f'PyFEALiTE - {load_case_name}', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Load summary
    total_fx = sum([load.Fx for load in loads]) / 1000
    total_fy = sum([load.Fy for load in loads]) / 1000
    
    info_text = f"""{load_case_name} Summary:
• Number of loads: {len(loads)}
• Total Fx: {total_fx:.1f} kN
• Total Fy: {total_fy:.1f} kN
• Load Case Factor: {loads[0].load_case.factor if loads else 1.0}"""
    
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8)
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=bbox_props)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"   ✅ Saved {filename}")

# Generate all visualizations
print("\n📊 Generating visualizations...")

# 1. Frame geometry
create_frame_geometry_plot()

# 2. Dead load visualization
create_load_visualization(dead_loads, "Dead Load Application", "frame_loads_dead_load.png", "purple")

# 3. Live load visualization  
create_load_visualization(live_loads, "Live Load Application", "frame_loads_live_load.png", "orange")

# 4. Wind load visualization
create_load_visualization(wind_loads, "Wind Load Application", "frame_loads_wind_load.png", "blue")

print("\n🎉 PyFEALiTE Frame Analysis Example Complete!")
print("=" * 50)
print("Generated files:")
print("  📊 frame_geometry.png - Structure geometry")
print("  🏗️ frame_loads_dead_load.png - Dead load application")
print("  🏢 frame_loads_live_load.png - Live load application") 
print("  💨 frame_loads_wind_load.png - Wind load application")
print("\n✅ All visualizations created successfully!")
