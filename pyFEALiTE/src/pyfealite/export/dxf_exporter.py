"""DXF export functionality for PyFEALiTE structures."""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path

try:
    import ezdxf
    from ezdxf.document import Drawing
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False

from dataclasses import dataclass

from ..core.node import Node2D
from ..core.element import FrameElement2D
from ..core.spring_element import SpringElement2D
from ..loads.base import ILoad
# from ..loads.point_load import PointLoad, NodalLoad
# from ..loads.distributed_load import UniformLoad, TrapezoidalLoad
from ..core.structure import Structure


@dataclass
class DXFExportSettings:
    """Settings for DXF export."""
    # Drawing settings
    units: str = "m"  # Units for dimensions
    scale_factor: float = 1.0  # Scale factor for coordinates
    
    # Layer settings
    node_layer: str = "NODES"
    element_layer: str = "ELEMENTS"
    load_layer: str = "LOADS"
    dimension_layer: str = "DIMENSIONS"
    text_layer: str = "TEXT"
    support_layer: str = "SUPPORTS"
    
    # Symbol settings
    node_symbol_size: float = 0.1  # Size of node symbols
    load_arrow_scale: float = 1.0  # Scale for load arrows
    text_height: float = 0.05  # Text height
    
    # Display options
    show_node_ids: bool = True
    show_element_ids: bool = True
    show_load_values: bool = True
    show_dimensions: bool = False
    show_supports: bool = True
    show_deformed_shape: bool = False
    
    # Colors (AutoCAD color index)
    node_color: int = 1  # Red
    element_color: int = 2  # Yellow
    load_color: int = 3  # Green
    support_color: int = 4  # Cyan
    text_color: int = 7  # White/Black
    dimension_color: int = 8  # Dark gray


class DXFExporter:
    """
    DXF export utility for PyFEALiTE structures.
    
    Exports structural models to DXF format for use in CAD software.
    Supports nodes, elements, loads, supports, and annotations.
    """
    
    def __init__(self, settings: Optional[DXFExportSettings] = None):
        """
        Initialize DXF exporter.
        
        Args:
            settings: Export settings
        """
        self.settings = settings or DXFExportSettings()
        self.doc: Optional[Drawing] = None
        self.modelspace = None
    
    def export_structure(self, structure: Structure, filename: Union[str, Path],
                        include_loads: bool = True, load_case: Optional[str] = None) -> None:
        """
        Export complete structure to DXF.
        
        Args:
            structure: Structure to export
            filename: Output filename
            include_loads: Whether to include loads
            load_case: Specific load case to export
        """
        self._create_document()
        self._setup_layers()
        
        # Export nodes
        self._export_nodes(structure.nodes)
        
        # Export elements
        self._export_elements(structure.elements)
        
        # Export supports
        if self.settings.show_supports:
            self._export_supports(structure.nodes)
        
        # Export loads
        if include_loads:
            loads = self._get_loads_for_export(structure, load_case)
            self._export_loads(loads)
        
        # Add title block and metadata
        self._add_title_block(structure, load_case)
        
        # Save file
        self.doc.saveas(filename)
    
    def export_analysis_results(self, structure: Structure, results: Any,
                               filename: Union[str, Path], result_type: str = "displacement") -> None:
        """
        Export analysis results to DXF.
        
        Args:
            structure: Analyzed structure
            results: Analysis results
            filename: Output filename
            result_type: Type of results (displacement, forces, etc.)
        """
        self._create_document()
        self._setup_layers()
        
        # Export original structure
        self._export_nodes(structure.nodes, color=8)  # Gray
        self._export_elements(structure.elements, color=8)
        
        if result_type == "displacement" and hasattr(results, 'displacements'):
            self._export_deformed_shape(structure, results)
        elif result_type == "forces" and hasattr(results, 'element_forces'):
            self._export_force_diagrams(structure, results)
        
        self.doc.saveas(filename)
    
    def _create_document(self) -> None:
        """Create new DXF document."""
        if EZDXF_AVAILABLE:
            self.doc = ezdxf.new(dxfversion='R2010')
        else:
            self.doc = None
        self.modelspace = self.doc.modelspace()
        
        # Set drawing units
        self.doc.header['$INSUNITS'] = 6  # Meters
    
    def _setup_layers(self) -> None:
        """Setup drawing layers."""
        layers = [
            (self.settings.node_layer, self.settings.node_color),
            (self.settings.element_layer, self.settings.element_color),
            (self.settings.load_layer, self.settings.load_color),
            (self.settings.support_layer, self.settings.support_color),
            (self.settings.text_layer, self.settings.text_color),
            (self.settings.dimension_layer, self.settings.dimension_color),
        ]
        
        for layer_name, color in layers:
            layer = self.doc.layers.new(layer_name)
            layer.color = color
    
    def _export_nodes(self, nodes: List[Node2D], color: Optional[int] = None) -> None:
        """Export nodes to DXF."""
        node_color = color or self.settings.node_color
        
        for node in nodes:
            x, y = self._scale_coordinates(node.x, node.y)
            
            # Draw node symbol (circle)
            self.modelspace.add_circle(
                center=(x, y),
                radius=self.settings.node_symbol_size,
                dxfattribs={
                    'layer': self.settings.node_layer,
                    'color': node_color
                }
            )
            
            # Add node ID text
            if self.settings.show_node_ids:
                self.modelspace.add_text(
                    text=str(node.id),
                    dxfattribs={
                        'layer': self.settings.text_layer,
                        'color': self.settings.text_color,
                        'height': self.settings.text_height
                    }
                ).set_pos((x + self.settings.node_symbol_size, y + self.settings.node_symbol_size))
    
    def _export_elements(self, elements: List[Union[FrameElement2D, SpringElement2D]], 
                        color: Optional[int] = None) -> None:
        """Export elements to DXF."""
        element_color = color or self.settings.element_color
        
        for element in elements:
            start_x, start_y = self._scale_coordinates(element.start_node.x, element.start_node.y)
            end_x, end_y = self._scale_coordinates(element.end_node.x, element.end_node.y)
            
            # Draw element line
            line_type = "CONTINUOUS"
            if isinstance(element, SpringElement2D):
                line_type = "DASHED"  # Springs as dashed lines
            
            self.modelspace.add_line(
                start=(start_x, start_y),
                end=(end_x, end_y),
                dxfattribs={
                    'layer': self.settings.element_layer,
                    'color': element_color,
                    'linetype': line_type
                }
            )
            
            # Add element ID text
            if self.settings.show_element_ids:
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                self.modelspace.add_text(
                    text=str(element.id),
                    dxfattribs={
                        'layer': self.settings.text_layer,
                        'color': self.settings.text_color,
                        'height': self.settings.text_height
                    }
                ).set_pos((mid_x, mid_y))
    
    def _export_supports(self, nodes: List[Node2D]) -> None:
        """Export support symbols."""
        for node in nodes:
            if hasattr(node, 'support') and node.support is not None:
                x, y = self._scale_coordinates(node.x, node.y)
                self._draw_support_symbol(x, y, node.support)
    
    def _draw_support_symbol(self, x: float, y: float, support) -> None:
        """Draw support symbol at coordinates."""
        size = self.settings.node_symbol_size * 2
        
        # Fixed support - triangle
        if hasattr(support, 'is_fixed') and support.is_fixed():
            points = [
                (x - size, y - size),
                (x + size, y - size),
                (x, y),
                (x - size, y - size)
            ]
            self.modelspace.add_lwpolyline(
                points,
                dxfattribs={
                    'layer': self.settings.support_layer,
                    'color': self.settings.support_color
                }
            )
        
        # Pin support - triangle with pin
        elif hasattr(support, 'is_pinned') and support.is_pinned():
            # Triangle
            points = [
                (x - size, y - size),
                (x + size, y - size), 
                (x, y),
                (x - size, y - size)
            ]
            self.modelspace.add_lwpolyline(
                points,
                dxfattribs={
                    'layer': self.settings.support_layer,
                    'color': self.settings.support_color
                }
            )
            
            # Pin circle
            self.modelspace.add_circle(
                center=(x, y - size/3),
                radius=size/4,
                dxfattribs={
                    'layer': self.settings.support_layer,
                    'color': self.settings.support_color
                }
            )
    
    def _export_loads(self, loads: List[ILoad]) -> None:
        """Export loads to DXF."""
        for load in loads:
            # Load type checking temporarily disabled for compatibility
            pass
            # if isinstance(load, (PointLoad, NodalLoad)):
            #     self._draw_point_load(load)
            # elif isinstance(load, UniformLoad):
            #     self._draw_uniform_load(load)
            # elif isinstance(load, TrapezoidalLoad):
            #     self._draw_trapezoidal_load(load)
    
    def _draw_point_load(self, load: Any) -> None:
        """Draw point load arrow."""
        # Temporarily disabled for compatibility
        # if isinstance(load, NodalLoad):
            x, y = self._scale_coordinates(load.node.x, load.node.y)
            force_x = load.fx * self.settings.load_arrow_scale
            force_y = load.fy * self.settings.load_arrow_scale
        else:
            # PointLoad on element
            return  # Skip for now, needs element position calculation
        
        # Draw load arrow
        self._draw_arrow(x, y, force_x, force_y)
        
        # Add load value text
        if self.settings.show_load_values:
            magnitude = np.sqrt(force_x**2 + force_y**2)
            self.modelspace.add_text(
                text=f"{magnitude:.1f}",
                dxfattribs={
                    'layer': self.settings.text_layer,
                    'color': self.settings.load_color,
                    'height': self.settings.text_height
                }
            ).set_pos((x + force_x, y + force_y))
    
    def _draw_uniform_load(self, load: Any) -> None:
        """Draw uniform load arrows."""
        # Get element coordinates
        start_x, start_y = self._scale_coordinates(load.element.start_node.x, load.element.start_node.y)
        end_x, end_y = self._scale_coordinates(load.element.end_node.x, load.element.end_node.y)
        
        # Calculate load direction
        if load.direction.value in ['Y', 'LOCAL_Y']:
            # Perpendicular to element
            element_dx = end_x - start_x
            element_dy = end_y - start_y
            length = np.sqrt(element_dx**2 + element_dy**2)
            
            # Perpendicular direction
            load_dx = -element_dy / length * load.magnitude * self.settings.load_arrow_scale
            load_dy = element_dx / length * load.magnitude * self.settings.load_arrow_scale
        else:
            # Along element or global direction
            load_dx = load.magnitude * self.settings.load_arrow_scale if load.direction.value == 'X' else 0
            load_dy = load.magnitude * self.settings.load_arrow_scale if load.direction.value == 'Y' else 0
        
        # Draw multiple arrows along element
        num_arrows = 5
        for i in range(num_arrows):
            t = i / (num_arrows - 1)
            x = start_x + t * (end_x - start_x)
            y = start_y + t * (end_y - start_y)
            self._draw_arrow(x, y, load_dx, load_dy, scale=0.5)
    
    def _draw_arrow(self, x: float, y: float, dx: float, dy: float, scale: float = 1.0) -> None:
        """Draw arrow symbol."""
        # Main arrow line
        self.modelspace.add_line(
            start=(x, y),
            end=(x + dx * scale, y + dy * scale),
            dxfattribs={
                'layer': self.settings.load_layer,
                'color': self.settings.load_color
            }
        )
        
        # Arrowhead
        if abs(dx) > 1e-6 or abs(dy) > 1e-6:
            length = np.sqrt(dx**2 + dy**2)
            head_length = min(length * 0.2, self.settings.node_symbol_size) * scale
            head_angle = np.pi / 6  # 30 degrees
            
            # Normalize direction
            dx_norm = dx / length
            dy_norm = dy / length
            
            # Arrowhead points
            head_x1 = x + dx * scale - head_length * (dx_norm * np.cos(head_angle) - dy_norm * np.sin(head_angle))
            head_y1 = y + dy * scale - head_length * (dy_norm * np.cos(head_angle) + dx_norm * np.sin(head_angle))
            
            head_x2 = x + dx * scale - head_length * (dx_norm * np.cos(head_angle) + dy_norm * np.sin(head_angle))
            head_y2 = y + dy * scale - head_length * (dy_norm * np.cos(head_angle) - dx_norm * np.sin(head_angle))
            
            # Draw arrowhead lines
            self.modelspace.add_line(
                start=(x + dx * scale, y + dy * scale),
                end=(head_x1, head_y1),
                dxfattribs={'layer': self.settings.load_layer, 'color': self.settings.load_color}
            )
            self.modelspace.add_line(
                start=(x + dx * scale, y + dy * scale),
                end=(head_x2, head_y2),
                dxfattribs={'layer': self.settings.load_layer, 'color': self.settings.load_color}
            )
    
    def _draw_trapezoidal_load(self, load: Any) -> None:
        """Draw trapezoidal load distribution."""
        # Similar to uniform load but with varying magnitude
        # Implementation would vary arrow sizes along element
        pass
    
    def _export_deformed_shape(self, structure: Structure, results: Any) -> None:
        """Export deformed shape."""
        if not hasattr(results, 'displacements'):
            return
        
        scale = 100.0  # Displacement scale factor
        
        for element in structure.elements:
            if hasattr(element, 'start_node') and hasattr(element, 'end_node'):
                # Get nodal displacements
                start_disp = results.get_node_displacement(element.start_node.id)
                end_disp = results.get_node_displacement(element.end_node.id)
                
                if start_disp is not None and end_disp is not None:
                    # Calculate deformed positions
                    start_x = element.start_node.x + start_disp[0] * scale
                    start_y = element.start_node.y + start_disp[1] * scale
                    end_x = element.end_node.x + end_disp[0] * scale
                    end_y = element.end_node.y + end_disp[1] * scale
                    
                    start_x, start_y = self._scale_coordinates(start_x, start_y)
                    end_x, end_y = self._scale_coordinates(end_x, end_y)
                    
                    # Draw deformed element
                    self.modelspace.add_line(
                        start=(start_x, start_y),
                        end=(end_x, end_y),
                        dxfattribs={
                            'layer': 'DEFORMED',
                            'color': 1,  # Red for deformed shape
                            'linetype': 'CONTINUOUS'
                        }
                    )
    
    def _add_title_block(self, structure: Structure, load_case: Optional[str] = None) -> None:
        """Add title block with project information."""
        # Find drawing extents
        all_x = [node.x for node in structure.nodes]
        all_y = [node.y for node in structure.nodes]
        
        if all_x and all_y:
            max_x = max(all_x) * self.settings.scale_factor
            max_y = max(all_y) * self.settings.scale_factor
            
            # Add title text
            title_text = f"PyFEALiTE Structure"
            if load_case:
                title_text += f" - {load_case}"
            
            self.modelspace.add_text(
                text=title_text,
                dxfattribs={
                    'layer': self.settings.text_layer,
                    'color': self.settings.text_color,
                    'height': self.settings.text_height * 2
                }
            ).set_pos((max_x * 1.1, max_y * 1.1))
            
            # Add statistics
            stats = [
                f"Nodes: {len(structure.nodes)}",
                f"Elements: {len(structure.elements)}",
                f"Units: {self.settings.units}"
            ]
            
            for i, stat in enumerate(stats):
                self.modelspace.add_text(
                    text=stat,
                    dxfattribs={
                        'layer': self.settings.text_layer,
                        'color': self.settings.text_color,
                        'height': self.settings.text_height
                    }
                ).set_pos((max_x * 1.1, max_y * 1.1 - (i + 1) * self.settings.text_height * 1.5))
    
    def _scale_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        """Scale coordinates according to settings."""
        return x * self.settings.scale_factor, y * self.settings.scale_factor
    
    def _get_loads_for_export(self, structure: Structure, load_case: Optional[str] = None) -> List[ILoad]:
        """Get loads for export based on load case."""
        if hasattr(structure, 'loads'):
            if load_case:
                return [load for load in structure.loads if load.load_case == load_case]
            else:
                return structure.loads
        return []


def export_structure_to_dxf(structure: Structure, filename: Union[str, Path],
                           settings: Optional[DXFExportSettings] = None,
                           include_loads: bool = True, load_case: Optional[str] = None) -> None:
    """
    Convenience function to export structure to DXF.
    
    Args:
        structure: Structure to export
        filename: Output filename
        settings: Export settings
        include_loads: Whether to include loads
        load_case: Specific load case to export
    """
    exporter = DXFExporter(settings)
    exporter.export_structure(structure, filename, include_loads, load_case)
