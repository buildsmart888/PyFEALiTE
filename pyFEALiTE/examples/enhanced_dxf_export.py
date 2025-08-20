"""
Enhanced DXF Export Example using ezdxf
=======================================

This example demonstrates advanced DXF export capabilities using
PyFEALiTE with the latest ezdxf library integration.

Features demonstrated:
- Professional DXF file creation with ezdxf v1.4.2
- Advanced structural geometry export
- Multiple layer management
- CAD-ready drawings with proper scaling
- Professional annotation and dimensioning
- Steel section symbols and details

Requirements:
- ezdxf library: pip install ezdxf
"""

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import datetime

def create_enhanced_structural_dxf():
    """Create enhanced structural DXF with ezdxf."""
    
    print("🔧 Creating Enhanced Structural DXF with ezdxf")
    print("=" * 50)
    
    # Create new DXF document (R2010 for broad compatibility)
    doc = ezdxf.new(dxfversion="R2010")
    print(f"✅ DXF Document created (version: R2010)")
    
    # Setup layers for structural elements
    setup_structural_layers(doc)
    
    # Get modelspace
    msp = doc.modelspace()
    
    # Create structural frame example
    create_frame_structure(msp)
    
    # Add professional annotations
    add_professional_annotations(msp)
    
    # Add title block
    add_title_block(msp)
    
    # Save the DXF file
    filename = "enhanced_structural_export.dxf"
    doc.saveas(filename)
    
    print(f"✅ DXF file created: {filename}")
    print(f"   Ready for CAD software import")
    
    return filename

def setup_structural_layers(doc):
    """Setup professional structural drawing layers."""
    
    # Define structural layers with colors
    structural_layers = [
        ("GRID", colors.CYAN, "Construction grid lines"),
        ("COLUMNS", colors.RED, "Structural columns"),
        ("BEAMS", colors.BLUE, "Structural beams"),
        ("SUPPORTS", colors.GREEN, "Support conditions"),
        ("LOADS", colors.MAGENTA, "Applied loads"),
        ("DIMENSIONS", colors.YELLOW, "Dimensions and annotations"),
        ("TEXT", colors.WHITE, "Text and labels"),
        ("TITLE", colors.WHITE, "Title block and border"),
        ("SECTIONS", colors.CYAN, "Cross-section details"),
        ("STEEL_DETAILS", colors.RED, "Steel connection details")
    ]
    
    for layer_name, color, description in structural_layers:
        layer = doc.layers.add(layer_name)
        layer.color = color
        layer.description = description
        print(f"   Layer created: {layer_name} (Color: {color})")

def create_frame_structure(msp):
    """Create a sample 2D frame structure."""
    
    print("🏗️  Creating frame structure...")
    
    # Frame geometry (in meters, will be scaled for DXF)
    scale = 1000  # Convert to mm for DXF
    
    # Frame dimensions
    bay_width = 6.0 * scale    # 6m bays
    story_height = 3.5 * scale # 3.5m story height
    num_bays = 3
    num_stories = 2
    
    # Create grid lines
    create_grid_lines(msp, num_bays, num_stories, bay_width, story_height)
    
    # Create columns
    create_columns(msp, num_bays, num_stories, bay_width, story_height)
    
    # Create beams
    create_beams(msp, num_bays, num_stories, bay_width, story_height)
    
    # Create supports
    create_supports(msp, num_bays, bay_width)
    
    # Create loads
    create_loads(msp, num_bays, num_stories, bay_width, story_height)

def create_grid_lines(msp, num_bays, num_stories, bay_width, story_height):
    """Create construction grid lines."""
    
    # Vertical grid lines
    for i in range(num_bays + 1):
        x = i * bay_width
        start = (x, -500)  # Extend below base
        end = (x, num_stories * story_height + 500)  # Extend above top
        
        msp.add_line(start, end, dxfattribs={
            "layer": "GRID",
            "linetype": "CENTER"
        })
        
        # Grid labels
        msp.add_text(
            text=chr(65 + i),  # A, B, C, ...
            dxfattribs={
                "layer": "TEXT",
                "height": 200
            }
        ).set_placement((x, -800), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Horizontal grid lines
    for i in range(num_stories + 1):
        y = i * story_height
        start = (-500, y)
        end = (num_bays * bay_width + 500, y)
        
        msp.add_line(start, end, dxfattribs={
            "layer": "GRID",
            "linetype": "CENTER"
        })
        
        # Grid labels
        msp.add_text(
            text=str(i + 1),
            dxfattribs={
                "layer": "TEXT",
                "height": 200
            }
        ).set_placement((-800, y), align=TextEntityAlignment.MIDDLE_CENTER)

def create_columns(msp, num_bays, num_stories, bay_width, story_height):
    """Create structural columns."""
    
    column_width = 300  # 300mm column width
    
    for bay in range(num_bays + 1):
        for story in range(num_stories):
            x = bay * bay_width
            y_bottom = story * story_height
            y_top = (story + 1) * story_height
            
            # Column centerline
            msp.add_line(
                (x, y_bottom), (x, y_top),
                dxfattribs={"layer": "COLUMNS", "lineweight": 50}
            )
            
            # Column rectangle (simplified representation)
            column_rect = [
                (x - column_width/2, y_bottom),
                (x + column_width/2, y_bottom),
                (x + column_width/2, y_top),
                (x - column_width/2, y_top),
                (x - column_width/2, y_bottom)
            ]
            
            msp.add_lwpolyline(
                column_rect,
                dxfattribs={"layer": "COLUMNS", "lineweight": 25}
            )
            
            # Column label
            mid_y = (y_bottom + y_top) / 2
            msp.add_text(
                text=f"C{bay+1}",
                dxfattribs={
                    "layer": "TEXT",
                    "height": 150,
                    "color": colors.WHITE
                }
            ).set_placement((x + 400, mid_y), align=TextEntityAlignment.MIDDLE_LEFT)

def create_beams(msp, num_bays, num_stories, bay_width, story_height):
    """Create structural beams."""
    
    beam_depth = 400  # 400mm beam depth
    
    for story in range(1, num_stories + 1):
        y = story * story_height
        
        for bay in range(num_bays):
            x_start = bay * bay_width
            x_end = (bay + 1) * bay_width
            
            # Beam centerline
            msp.add_line(
                (x_start, y), (x_end, y),
                dxfattribs={"layer": "BEAMS", "lineweight": 50}
            )
            
            # Beam rectangle
            beam_rect = [
                (x_start, y - beam_depth/2),
                (x_end, y - beam_depth/2),
                (x_end, y + beam_depth/2),
                (x_start, y + beam_depth/2),
                (x_start, y - beam_depth/2)
            ]
            
            msp.add_lwpolyline(
                beam_rect,
                dxfattribs={"layer": "BEAMS", "lineweight": 25}
            )
            
            # Beam label
            mid_x = (x_start + x_end) / 2
            msp.add_text(
                text=f"B{story}-{bay+1}",
                dxfattribs={
                    "layer": "TEXT",
                    "height": 150,
                    "color": colors.WHITE
                }
            ).set_placement((mid_x, y + 600), align=TextEntityAlignment.MIDDLE_CENTER)

def create_supports(msp, num_bays, bay_width):
    """Create support symbols."""
    
    support_size = 400
    
    for bay in range(num_bays + 1):
        x = bay * bay_width
        y = 0
        
        # Fixed support triangle
        support_triangle = [
            (x - support_size, y - support_size),
            (x + support_size, y - support_size),
            (x, y),
            (x - support_size, y - support_size)
        ]
        
        msp.add_lwpolyline(
            support_triangle,
            dxfattribs={
                "layer": "SUPPORTS",
                "lineweight": 30
            }
        )
        
        # Hatch pattern for support
        for i in range(-3, 4):
            hatch_x = x + i * support_size / 6
            msp.add_line(
                (hatch_x, y - support_size),
                (hatch_x - support_size/4, y - support_size * 1.2),
                dxfattribs={"layer": "SUPPORTS"}
            )

def create_loads(msp, num_bays, num_stories, bay_width, story_height):
    """Create load arrows and symbols."""
    
    arrow_length = 800
    arrow_spacing = bay_width / 4
    
    for story in range(1, num_stories + 1):
        y = story * story_height
        
        for bay in range(num_bays):
            # Distributed load arrows
            for i in range(4):
                x = bay * bay_width + (i + 1) * arrow_spacing
                
                # Load arrow
                msp.add_line(
                    (x, y + arrow_length),
                    (x, y + 200),
                    dxfattribs={
                        "layer": "LOADS",
                        "lineweight": 20
                    }
                )
                
                # Arrow head
                arrow_head = [
                    (x, y + 200),
                    (x - 100, y + 400),
                    (x + 100, y + 400),
                    (x, y + 200)
                ]
                
                msp.add_lwpolyline(
                    arrow_head,
                    dxfattribs={"layer": "LOADS"}
                )
            
            # Load label
            mid_x = bay * bay_width + bay_width / 2
            msp.add_text(
                text="5.0 kN/m",
                dxfattribs={
                    "layer": "TEXT",
                    "height": 180,
                    "color": colors.MAGENTA
                }
            ).set_placement((mid_x, y + arrow_length + 300), 
                          align=TextEntityAlignment.MIDDLE_CENTER)

def add_professional_annotations(msp):
    """Add professional annotations and dimensions."""
    
    print("📝 Adding professional annotations...")
    
    # Add dimension lines (simplified)
    msp.add_text(
        text="6000",
        dxfattribs={
            "layer": "DIMENSIONS",
            "height": 200,
            "color": colors.YELLOW
        }
    ).set_placement((3000, -1500), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Add material specifications
    material_text = [
        "MATERIALS:",
        "Concrete: C30/37",
        "Steel: A992 Grade 50", 
        "Reinforcement: Grade 420"
    ]
    
    for i, text in enumerate(material_text):
        msp.add_text(
            text=text,
            dxfattribs={
                "layer": "TEXT",
                "height": 150 if i == 0 else 120,
                "style": "BOLD" if i == 0 else "STANDARD"
            }
        ).set_placement((20000, 6000 - i * 300), align=TextEntityAlignment.LEFT)

def add_title_block(msp):
    """Add professional title block."""
    
    print("🏛️  Adding title block...")
    
    # Title block rectangle
    title_block = [
        (15000, -3000),
        (25000, -3000),
        (25000, -1000),
        (15000, -1000),
        (15000, -3000)
    ]
    
    msp.add_lwpolyline(
        title_block,
        dxfattribs={"layer": "TITLE", "lineweight": 50}
    )
    
    # Title text
    titles = [
        ("PyFEALiTE Structural Analysis", 350, -1300),
        ("2D Frame Structure Export", 250, -1700),
        ("Enhanced DXF with ezdxf v1.4.2", 200, -2000),
        ("Scale: 1:100", 150, -2400),
        (f"Created: {datetime.datetime.now().strftime('%Y-%m-%d')}", 150, -2700)
    ]
    
    for text, height, y in titles:
        msp.add_text(
            text=text,
            dxfattribs={
                "layer": "TITLE",
                "height": height,
                "color": colors.WHITE
            }
        ).set_placement((16000, y), align=TextEntityAlignment.LEFT)

def create_steel_section_details():
    """Create detailed steel section drawings."""
    
    print("🔩 Creating steel section details...")
    
    doc = ezdxf.new(dxfversion="R2010")
    setup_structural_layers(doc)
    msp = doc.modelspace()
    
    # W-section detail
    create_w_section_detail(msp, (5000, 5000), "W18X35")
    
    # HSS section detail  
    create_hss_section_detail(msp, (15000, 5000), "HSS6X6X1/4")
    
    # Connection detail
    create_connection_detail(msp, (25000, 5000))
    
    # Save detailed drawings
    filename = "steel_section_details.dxf"
    doc.saveas(filename)
    print(f"✅ Steel details created: {filename}")
    
    return filename

def create_w_section_detail(msp, origin, section_name):
    """Create W-section cross-section detail."""
    
    x, y = origin
    
    # W-section dimensions (simplified W18X35)
    depth = 1800    # 18 inches ≈ 457mm
    width = 1200    # 6 inches ≈ 152mm  
    web_thickness = 60
    flange_thickness = 100
    
    # Draw W-section
    w_section = [
        # Bottom flange
        (x - width/2, y - depth/2),
        (x + width/2, y - depth/2),
        (x + width/2, y - depth/2 + flange_thickness),
        (x + web_thickness/2, y - depth/2 + flange_thickness),
        # Web
        (x + web_thickness/2, y + depth/2 - flange_thickness),
        (x + width/2, y + depth/2 - flange_thickness),
        # Top flange
        (x + width/2, y + depth/2),
        (x - width/2, y + depth/2),
        (x - width/2, y + depth/2 - flange_thickness),
        (x - web_thickness/2, y + depth/2 - flange_thickness),
        # Web
        (x - web_thickness/2, y - depth/2 + flange_thickness),
        (x - width/2, y - depth/2 + flange_thickness),
        (x - width/2, y - depth/2)
    ]
    
    msp.add_lwpolyline(
        w_section,
        dxfattribs={
            "layer": "STEEL_DETAILS",
            "lineweight": 35
        }
    )
    
    # Section label
    msp.add_text(
        text=section_name,
        dxfattribs={
            "layer": "TEXT",
            "height": 200
        }
    ).set_placement((x, y - depth/2 - 500), align=TextEntityAlignment.MIDDLE_CENTER)

def create_hss_section_detail(msp, origin, section_name):
    """Create HSS section cross-section detail."""
    
    x, y = origin
    
    # HSS6X6X1/4 dimensions
    size = 1500     # 6 inches
    thickness = 60  # 1/4 inch
    
    # Outer rectangle
    outer_rect = [
        (x - size/2, y - size/2),
        (x + size/2, y - size/2),
        (x + size/2, y + size/2),
        (x - size/2, y + size/2),
        (x - size/2, y - size/2)
    ]
    
    # Inner rectangle (hollow)
    inner_size = size - 2 * thickness
    inner_rect = [
        (x - inner_size/2, y - inner_size/2),
        (x + inner_size/2, y - inner_size/2),
        (x + inner_size/2, y + inner_size/2),
        (x - inner_size/2, y + inner_size/2),
        (x - inner_size/2, y - inner_size/2)
    ]
    
    msp.add_lwpolyline(outer_rect, dxfattribs={"layer": "STEEL_DETAILS", "lineweight": 35})
    msp.add_lwpolyline(inner_rect, dxfattribs={"layer": "STEEL_DETAILS", "lineweight": 25})
    
    # Section label
    msp.add_text(
        text=section_name,
        dxfattribs={"layer": "TEXT", "height": 200}
    ).set_placement((x, y - size/2 - 500), align=TextEntityAlignment.MIDDLE_CENTER)

def create_connection_detail(msp, origin):
    """Create beam-column connection detail."""
    
    x, y = origin
    
    # Simplified bolted connection
    # Column (using rectangle via polyline)
    column_rect = [
        (x - 150, y - 1000),
        (x + 150, y - 1000),
        (x + 150, y + 1000),
        (x - 150, y + 1000),
        (x - 150, y - 1000)
    ]
    msp.add_lwpolyline(column_rect, dxfattribs={"layer": "STEEL_DETAILS"})
    
    # Beam (using rectangle via polyline)
    beam_rect = [
        (x, y - 200),
        (x + 1500, y - 200),
        (x + 1500, y + 200),
        (x, y + 200),
        (x, y - 200)
    ]
    msp.add_lwpolyline(beam_rect, dxfattribs={"layer": "STEEL_DETAILS"})
    
    # Bolts
    bolt_positions = [(x + 300, y - 100), (x + 300, y + 100), (x + 600, y - 100), (x + 600, y + 100)]
    for bx, by in bolt_positions:
        msp.add_circle((bx, by), radius=50, dxfattribs={"layer": "STEEL_DETAILS"})
    
    # Connection label
    msp.add_text(
        text="Typical Beam-Column Connection",
        dxfattribs={"layer": "TEXT", "height": 180}
    ).set_placement((x, y - 1500), align=TextEntityAlignment.MIDDLE_CENTER)

def main():
    """Main function for enhanced DXF export demonstration."""
    
    print("🚀 PyFEALiTE Enhanced DXF Export with ezdxf v1.4.2")
    print("=" * 60)
    
    try:
        # Create main structural drawing
        main_file = create_enhanced_structural_dxf()
        
        # Create detailed steel section drawings
        details_file = create_steel_section_details()
        
        print("\n✅ Enhanced DXF Export Completed Successfully!")
        print("=" * 60)
        print("📁 Files created:")
        print(f"   • {main_file} - Main structural frame")
        print(f"   • {details_file} - Steel section details")
        print("\n🔧 Features demonstrated:")
        print("   • Professional DXF R2010 format")
        print("   • Multiple layer organization")
        print("   • Structural frame geometry")
        print("   • Steel section details")
        print("   • Professional annotations")
        print("   • CAD-ready drawings")
        print("\n💡 Integration benefits:")
        print("   • ezdxf v1.4.2 - Latest stable version")
        print("   • Full AutoCAD compatibility")
        print("   • Professional drawing standards")
        print("   • Scalable vector graphics")
        print("   • Layer-based organization")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
