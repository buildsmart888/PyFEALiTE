"""Main plotter class for PyFEALiTE visualization."""

from typing import Optional, List, Dict, Tuple, Union
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from matplotlib import colors
import warnings

try:
    import plotly.graph_objects as go
    import plotly.subplots as sp
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..core.structure import Structure
from ..core.node import Node2D, NodalDegreeOfFreedom
from ..core.element import FrameElement2D
from ..loads.base import LoadCase
from ..loads.point_load import PointLoad, NodalLoad
from ..loads.distributed_load import UniformLoad, TrapezoidalLoad


class StructurePlotter:
    """
    Main plotting class for PyFEALiTE structures.
    
    Provides methods for plotting structure geometry, loads, 
    deformations, and analysis results using matplotlib and plotly.
    """
    
    def __init__(self, structure: Structure, figsize: Tuple[float, float] = (12, 8)):
        """
        Initialize plotter for a structure.
        
        Args:
            structure: Structure to plot
            figsize: Figure size (width, height) in inches
        """
        self.structure = structure
        self.figsize = figsize
        self.fig = None
        self.ax = None
        
        # Style settings
        self.node_size = 50
        self.element_linewidth = 2.0
        self.load_scale = 1.0
        self.deformation_scale = 100.0
        
        # Colors
        self.colors = {
            'node_free': 'blue',
            'node_pinned': 'red', 
            'node_fixed': 'black',
            'element': 'black',
            'element_deformed': 'red',
            'load_point': 'green',
            'load_distributed': 'orange',
            'reaction': 'purple',
            'moment': 'brown'
        }
    
    def setup_figure(self, title: str = "") -> Tuple[plt.Figure, plt.Axes]:
        """Setup matplotlib figure and axes."""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight='bold')
        return self.fig, self.ax
    
    def plot_geometry(self, show_labels: bool = True, show_nodes: bool = True, 
                     show_elements: bool = True) -> None:
        """
        Plot structure geometry (nodes and elements).
        
        Args:
            show_labels: Whether to show node and element labels
            show_nodes: Whether to plot nodes
            show_elements: Whether to plot elements
        """
        if not self.ax:
            self.setup_figure("Structure Geometry")
        
        # Plot elements first (so they appear behind nodes)
        if show_elements and self.structure.elements:
            for element in self.structure.elements:
                x_coords = [element.start_node.x, element.end_node.x]
                y_coords = [element.start_node.y, element.end_node.y]
                
                self.ax.plot(x_coords, y_coords, 
                           color=self.colors['element'],
                           linewidth=self.element_linewidth,
                           solid_capstyle='round')
                
                if show_labels and element.label:
                    # Label at element midpoint
                    mid_x = (element.start_node.x + element.end_node.x) / 2
                    mid_y = (element.start_node.y + element.end_node.y) / 2
                    self.ax.text(mid_x, mid_y, element.label,
                               ha='center', va='bottom', fontsize=8,
                               bbox=dict(boxstyle='round,pad=0.2', 
                                       facecolor='white', alpha=0.8))
        
        # Plot nodes
        if show_nodes and self.structure.nodes:
            for node in self.structure.nodes:
                # Determine node color based on restraints
                if node.is_free:
                    color = self.colors['node_free']
                    marker = 'o'
                elif all(node.restraints):  # Fully fixed
                    color = self.colors['node_fixed']
                    marker = 's'
                else:  # Partially restrained (pinned)
                    color = self.colors['node_pinned']
                    marker = '^'
                
                self.ax.scatter(node.x, node.y, 
                              color=color, s=self.node_size, 
                              marker=marker, edgecolors='black', linewidth=1,
                              zorder=5)
                
                if show_labels and node.label:
                    self.ax.text(node.x, node.y + 0.1, node.label,
                               ha='center', va='bottom', fontsize=9,
                               fontweight='bold')
        
        # Add boundary condition symbols
        self._draw_boundary_conditions()
    
    def _draw_boundary_conditions(self) -> None:
        """Draw boundary condition symbols."""
        for node in self.structure.nodes:
            if not node.is_free:
                # Draw support symbols
                if node.restraints[0] and node.restraints[1]:  # Both UX and UY restrained
                    # Fixed support - draw square
                    square = patches.Rectangle((node.x - 0.15, node.y - 0.15), 
                                             0.3, 0.3, linewidth=2, 
                                             edgecolor='black', facecolor='none')
                    self.ax.add_patch(square)
                    
                    # Add hatching for fixed support
                    for i in range(4):
                        hatch_x = node.x - 0.15 + i * 0.075
                        self.ax.plot([hatch_x, hatch_x + 0.075], 
                                   [node.y - 0.15, node.y - 0.225], 'k-', linewidth=1)
                
                elif node.restraints[1]:  # Only UY restrained (roller)
                    # Roller support - draw triangle
                    triangle = patches.Polygon([(node.x, node.y), 
                                              (node.x - 0.1, node.y - 0.15),
                                              (node.x + 0.1, node.y - 0.15)], 
                                             closed=True, linewidth=2,
                                             edgecolor='black', facecolor='none')
                    self.ax.add_patch(triangle)
                    
                    # Add roller circles
                    for x_offset in [-0.05, 0.05]:
                        circle = patches.Circle((node.x + x_offset, node.y - 0.2), 
                                              0.03, linewidth=1,
                                              edgecolor='black', facecolor='white')
                        self.ax.add_patch(circle)
                
                # Draw moment restraint symbol if Rz is restrained
                if len(node.restraints) > 2 and node.restraints[2]:
                    # Draw a small arc to indicate moment restraint
                    arc = patches.Arc((node.x, node.y), 0.2, 0.2, angle=0,
                                    theta1=0, theta2=270, linewidth=2, color='red')
                    self.ax.add_patch(arc)
    
    def plot_loads(self, load_case: Optional[LoadCase] = None, scale: float = 1.0) -> None:
        """
        Plot loads on the structure.
        
        Args:
            load_case: Specific load case to plot. If None, plot all loads.
            scale: Scale factor for load visualization
        """
        if not self.ax:
            self.setup_figure("Structure Loads")
        
        self.load_scale = scale
        
        # Plot element loads
        for element in self.structure.elements:
            element_loads = getattr(element, 'loads', [])
            
            for load in element_loads:
                if load_case is None or load.load_case == load_case:
                    self._draw_element_load(element, load)
        
        # Plot nodal loads
        for node in self.structure.nodes:
            nodal_loads = getattr(node, 'loads', [])
            
            for load in nodal_loads:
                if isinstance(load, NodalLoad) and (load_case is None or load.load_case == load_case):
                    self._draw_nodal_load(node, load)
    
    def _draw_element_load(self, element: FrameElement2D, load) -> None:
        """Draw element load visualization."""
        if isinstance(load, PointLoad):
            # Calculate load position
            ratio = load.distance / element.length if element.length > 0 else 0
            load_x = element.start_node.x + ratio * (element.end_node.x - element.start_node.x)
            load_y = element.start_node.y + ratio * (element.end_node.y - element.start_node.y)
            
            # Draw force arrows
            if abs(load.Fx) > 1e-6:
                self._draw_force_arrow(load_x, load_y, load.Fx * self.load_scale, 0,
                                     color=self.colors['load_point'], label=f"Fx={load.Fx}")
            
            if abs(load.Fy) > 1e-6:
                self._draw_force_arrow(load_x, load_y, 0, load.Fy * self.load_scale,
                                     color=self.colors['load_point'], label=f"Fy={load.Fy}")
            
            # Draw moment if present
            if abs(load.Mz) > 1e-6:
                self._draw_moment_arc(load_x, load_y, load.Mz, color=self.colors['moment'])
        
        elif isinstance(load, (UniformLoad, TrapezoidalLoad)):
            self._draw_distributed_load(element, load)
    
    def _draw_distributed_load(self, element: FrameElement2D, load) -> None:
        """Draw distributed load visualization."""
        n_arrows = 5  # Number of arrows to draw
        
        start_dist = getattr(load, 'start_distance', 0.0)
        end_dist = getattr(load, 'end_distance', element.length)
        if end_dist < 0:
            end_dist = element.length
        
        # Load intensities
        if isinstance(load, UniformLoad):
            w1x, w1y = load.wx, load.wy
            w2x, w2y = w1x, w1y
        else:  # TrapezoidalLoad
            w1x, w1y = load.wx1, load.wy1
            w2x, w2y = load.wx2, load.wy2
        
        # Draw load arrows
        for i in range(n_arrows):
            ratio = i / (n_arrows - 1) if n_arrows > 1 else 0
            load_dist = start_dist + ratio * (end_dist - start_dist)
            element_ratio = load_dist / element.length if element.length > 0 else 0
            
            # Position along element
            load_x = element.start_node.x + element_ratio * (element.end_node.x - element.start_node.x)
            load_y = element.start_node.y + element_ratio * (element.end_node.y - element.start_node.y)
            
            # Interpolate load intensity
            wx = w1x + ratio * (w2x - w1x)
            wy = w1y + ratio * (w2y - w1y)
            
            # Draw arrows
            if abs(wx) > 1e-6:
                self._draw_force_arrow(load_x, load_y, wx * self.load_scale * 0.5, 0,
                                     color=self.colors['load_distributed'])
            
            if abs(wy) > 1e-6:
                self._draw_force_arrow(load_x, load_y, 0, wy * self.load_scale * 0.5,
                                     color=self.colors['load_distributed'])
    
    def _draw_nodal_load(self, node: Node2D, load: NodalLoad) -> None:
        """Draw nodal load visualization."""
        # Draw force arrows
        if abs(load.Fx) > 1e-6:
            self._draw_force_arrow(node.x, node.y, load.Fx * self.load_scale, 0,
                                 color=self.colors['load_point'], label=f"Fx={load.Fx}")
        
        if abs(load.Fy) > 1e-6:
            self._draw_force_arrow(node.x, node.y, 0, load.Fy * self.load_scale,
                                 color=self.colors['load_point'], label=f"Fy={load.Fy}")
        
        # Draw moment if present
        if abs(load.Mz) > 1e-6:
            self._draw_moment_arc(node.x, node.y, load.Mz, color=self.colors['moment'])
    
    def _draw_force_arrow(self, x: float, y: float, fx: float, fy: float, 
                         color: str = 'green', label: str = "") -> None:
        """Draw force arrow."""
        if abs(fx) < 1e-6 and abs(fy) < 1e-6:
            return
        
        # Create arrow
        arrow = FancyArrowPatch((x, y), (x + fx, y + fy),
                               connectionstyle="arc3", 
                               arrowstyle='->', 
                               color=color, linewidth=2,
                               mutation_scale=20)
        self.ax.add_patch(arrow)
        
        # Add label if provided
        if label:
            label_x = x + fx * 0.5
            label_y = y + fy * 0.5 + 0.05
            self.ax.text(label_x, label_y, label, ha='center', va='bottom',
                        fontsize=8, color=color, fontweight='bold')
    
    def _draw_moment_arc(self, x: float, y: float, moment: float, 
                        color: str = 'brown', radius: float = 0.15) -> None:
        """Draw moment arc."""
        # Direction of arc based on moment sign
        theta1, theta2 = (0, 270) if moment > 0 else (270, 0)
        
        arc = patches.Arc((x, y), 2*radius, 2*radius, angle=0,
                         theta1=theta1, theta2=theta2, 
                         linewidth=2, color=color)
        self.ax.add_patch(arc)
        
        # Add arrow head
        angle_rad = np.radians(theta2)
        arrow_x = x + radius * np.cos(angle_rad)
        arrow_y = y + radius * np.sin(angle_rad)
        
        # Calculate arrow direction
        if moment > 0:
            arrow_dx, arrow_dy = -0.05, 0.05
        else:
            arrow_dx, arrow_dy = 0.05, 0.05
        
        arrow = FancyArrowPatch((arrow_x - arrow_dx, arrow_y - arrow_dy),
                               (arrow_x, arrow_y),
                               arrowstyle='->', color=color, 
                               mutation_scale=15, linewidth=2)
        self.ax.add_patch(arrow)
        
        # Add moment label
        label_x = x + 1.5 * radius
        self.ax.text(label_x, y, f"M={moment:.1f}", ha='left', va='center',
                    fontsize=8, color=color, fontweight='bold')
    
    def plot_deformed_shape(self, load_case: LoadCase, scale: float = 100.0, 
                           show_original: bool = True) -> None:
        """
        Plot deformed shape of the structure.
        
        Args:
            load_case: Load case for deformation
            scale: Deformation magnification factor
            show_original: Whether to show original geometry
        """
        if not self.ax:
            self.setup_figure(f"Deformed Shape - {load_case.name}")
        
        if self.structure.analysis_status != "success":
            raise ValueError("Structure must be analyzed before plotting deformed shape")
        
        # Plot original geometry if requested
        if show_original:
            self.plot_geometry(show_labels=False)
        
        # Plot deformed elements
        for element in self.structure.elements:
            # Get node displacements
            disp_start = self.structure.get_node_displacement(element.start_node, load_case)
            disp_end = self.structure.get_node_displacement(element.end_node, load_case)
            
            # Calculate deformed positions
            x1_def = element.start_node.x + scale * disp_start[0]
            y1_def = element.start_node.y + scale * disp_start[1]
            x2_def = element.end_node.x + scale * disp_end[0]
            y2_def = element.end_node.y + scale * disp_end[1]
            
            # Plot deformed element
            self.ax.plot([x1_def, x2_def], [y1_def, y2_def],
                        color=self.colors['element_deformed'], 
                        linewidth=self.element_linewidth,
                        linestyle='--' if show_original else '-',
                        label='Deformed' if element == self.structure.elements[0] else "")
        
        # Plot deformed nodes
        for node in self.structure.nodes:
            disp = self.structure.get_node_displacement(node, load_case)
            x_def = node.x + scale * disp[0]
            y_def = node.y + scale * disp[1]
            
            self.ax.scatter(x_def, y_def, 
                          color=self.colors['element_deformed'], 
                          s=self.node_size//2, marker='o',
                          edgecolors='black', linewidth=1, zorder=5)
        
        # Add scale information
        self.ax.text(0.02, 0.98, f"Deformation scale: {scale}x", 
                    transform=self.ax.transAxes, fontsize=10,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        if show_original:
            self.ax.legend()
    
    def plot_reactions(self, load_case: LoadCase, scale: float = 1.0) -> None:
        """
        Plot support reactions.
        
        Args:
            load_case: Load case for reactions
            scale: Scale factor for reaction visualization
        """
        if not self.ax:
            self.setup_figure(f"Reactions - {load_case.name}")
        
        if self.structure.analysis_status != "success":
            raise ValueError("Structure must be analyzed before plotting reactions")
        
        # Plot structure geometry first
        self.plot_geometry(show_labels=True)
        
        # Plot reactions
        for node in self.structure.nodes:
            if not node.is_free:
                reaction = self.structure.get_node_reaction(node, load_case)
                
                # Draw reaction forces
                if abs(reaction[0]) > 1e-6:  # Rx
                    self._draw_force_arrow(node.x, node.y, -reaction[0] * scale, 0,
                                         color=self.colors['reaction'], 
                                         label=f"Rx={reaction[0]:.2f}")
                
                if abs(reaction[1]) > 1e-6:  # Ry  
                    self._draw_force_arrow(node.x, node.y, 0, -reaction[1] * scale,
                                         color=self.colors['reaction'],
                                         label=f"Ry={reaction[1]:.2f}")
                
                if abs(reaction[2]) > 1e-6:  # Mz
                    self._draw_moment_arc(node.x, node.y, -reaction[2], 
                                        color=self.colors['reaction'])
    
    def create_summary_plot(self, load_case: Optional[LoadCase] = None, 
                           deform_scale: float = 100.0) -> plt.Figure:
        """
        Create a comprehensive summary plot with multiple subplots.
        
        Args:
            load_case: Load case to analyze
            deform_scale: Deformation scale factor
            
        Returns:
            Figure with multiple subplots
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f"PyFEALiTE Analysis Summary - {self.structure.name}", 
                     fontsize=16, fontweight='bold')
        
        # Use first load case if none specified
        if load_case is None and self.structure.load_cases:
            load_case = self.structure.load_cases[0]
        
        # Subplot 1: Structure geometry
        self.ax = axes[0, 0]
        self.plot_geometry()
        self.ax.set_title("Structure Geometry")
        
        # Subplot 2: Loads
        self.ax = axes[0, 1] 
        self.plot_geometry(show_labels=False)
        if load_case:
            self.plot_loads(load_case, scale=0.1)
        self.ax.set_title(f"Loads - {load_case.name if load_case else 'All'}")
        
        # Subplot 3: Deformed shape
        self.ax = axes[1, 0]
        if self.structure.analysis_status == "success" and load_case:
            self.plot_deformed_shape(load_case, scale=deform_scale)
        else:
            self.ax.text(0.5, 0.5, 'Analysis required', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=12)
        self.ax.set_title("Deformed Shape")
        
        # Subplot 4: Reactions
        self.ax = axes[1, 1]
        if self.structure.analysis_status == "success" and load_case:
            self.plot_reactions(load_case, scale=0.1)
        else:
            self.ax.text(0.5, 0.5, 'Analysis required', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=12)
        self.ax.set_title("Support Reactions")
        
        plt.tight_layout()
        return fig
    
    def save_plot(self, filename: str, dpi: int = 300) -> None:
        """Save current plot to file."""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            print(f"Plot saved as: {filename}")
        else:
            print("No figure to save")
    
    def show(self) -> None:
        """Display the plot."""
        if self.fig:
            plt.show()
        else:
            print("No figure to show")
    
    # Plotly methods (if available)
    def create_plotly_figure(self, load_case: Optional[LoadCase] = None) -> Optional[go.Figure]:
        """Create interactive Plotly figure."""
        if not PLOTLY_AVAILABLE:
            warnings.warn("Plotly not available. Install with: pip install plotly")
            return None
        
        fig = go.Figure()
        
        # Add elements
        for element in self.structure.elements:
            fig.add_trace(go.Scatter(
                x=[element.start_node.x, element.end_node.x],
                y=[element.start_node.y, element.end_node.y],
                mode='lines',
                line=dict(color='black', width=3),
                name=element.label or f"Element_{id(element)}",
                hovertemplate=f"Element: {element.label}<br>Length: {element.length:.3f}m<extra></extra>"
            ))
        
        # Add nodes
        node_colors = []
        node_symbols = []
        node_text = []
        
        for node in self.structure.nodes:
            if node.is_free:
                node_colors.append('blue')
                node_symbols.append('circle')
            elif all(node.restraints):
                node_colors.append('black')
                node_symbols.append('square')
            else:
                node_colors.append('red')
                node_symbols.append('triangle-up')
            
            node_text.append(f"Node: {node.label}<br>({node.x:.2f}, {node.y:.2f})")
        
        fig.add_trace(go.Scatter(
            x=[node.x for node in self.structure.nodes],
            y=[node.y for node in self.structure.nodes],
            mode='markers+text',
            marker=dict(size=10, color=node_colors, symbol=node_symbols,
                       line=dict(width=2, color='black')),
            text=[node.label for node in self.structure.nodes],
            textposition="top center",
            name="Nodes",
            hovertemplate="%{customdata}<extra></extra>",
            customdata=node_text
        ))
        
        fig.update_layout(
            title=f"PyFEALiTE Structure - {self.structure.name}",
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            showlegend=True,
            hovermode='closest',
            template='plotly_white'
        )
        
        fig.update_xaxes(scaleanchor="y", scaleratio=1)
        
        return fig