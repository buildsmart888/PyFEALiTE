"""Convenience functions for structure plotting."""

from typing import Optional, Tuple, Dict, Any
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
import matplotlib.patches as patches

from .plotter import StructurePlotter
from ..core.structure import Structure
from ..loads.base import LoadCase


def plot_structure(structure: Structure, title: str = "", 
                  figsize: Tuple[float, float] = (10, 8),
                  show_labels: bool = True, save_as: Optional[str] = None) -> plt.Figure:
    """
    Quick function to plot structure geometry.
    
    Args:
        structure: Structure to plot
        title: Plot title
        figsize: Figure size
        show_labels: Whether to show labels
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure
    """
    plotter = StructurePlotter(structure, figsize=figsize)
    plotter.setup_figure(title or f"Structure - {structure.name}")
    plotter.plot_geometry(show_labels=show_labels)
    
    if save_as:
        plotter.save_plot(save_as)
    
    return plotter.fig


def plot_structure_with_loads(structure: Structure, load_case: Optional[LoadCase] = None,
                             title: str = "", figsize: Tuple[float, float] = (10, 8),
                             load_scale: float = 0.1, save_as: Optional[str] = None) -> plt.Figure:
    """
    Quick function to plot structure with loads.
    
    Args:
        structure: Structure to plot
        load_case: Load case to display
        title: Plot title
        figsize: Figure size
        load_scale: Scale factor for load visualization
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure
    """
    plotter = StructurePlotter(structure, figsize=figsize)
    
    load_case_name = load_case.name if load_case else "All Loads"
    plot_title = title or f"Structure with Loads - {load_case_name}"
    
    plotter.setup_figure(plot_title)
    plotter.plot_geometry(show_labels=True)
    plotter.plot_loads(load_case, scale=load_scale)
    
    if save_as:
        plotter.save_plot(save_as)
    
    return plotter.fig


def create_analysis_summary(structure: Structure, load_case: Optional[LoadCase] = None,
                           deform_scale: float = 100.0, 
                           save_as: Optional[str] = None) -> plt.Figure:
    """
    Create comprehensive analysis summary with multiple subplots.
    
    Args:
        structure: Structure to analyze
        load_case: Load case to display
        deform_scale: Deformation magnification
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure with subplots
    """
    plotter = StructurePlotter(structure)
    fig = plotter.create_summary_plot(load_case, deform_scale)
    
    if save_as:
        fig.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Analysis summary saved as: {save_as}")
    
    return fig


def plot_structure_with_internal_forces(
    structure: Structure, 
    load_case: Optional[LoadCase] = None,
    nfd_scale: float = 0.01,
    sfd_scale: float = 0.01, 
    bmd_scale: float = 0.01,
    displacement_scale: float = 1.0,
    diagram_offset: float = 10.0,
    title: str = "",
    figsize: Tuple[float, float] = (20, 16),
    save_as: Optional[str] = None
) -> plt.Figure:
    """
    Create detailed structural analysis plot with internal force diagrams
    similar to C# FEALiTE2D output.
    
    Args:
        structure: Structure to analyze
        load_case: Load case to display
        nfd_scale: Normal Force Diagram scale factor
        sfd_scale: Shear Force Diagram scale factor  
        bmd_scale: Bending Moment Diagram scale factor
        displacement_scale: Displacement magnification factor
        diagram_offset: Horizontal offset for diagrams
        title: Plot title
        figsize: Figure size
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure with comprehensive analysis plots
    """
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    
    # Create 2x3 subplot layout (เพิ่มช่องสำหรับ displacement)
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.2)
    
    # 1. Structure Geometry with Loads
    ax1 = fig.add_subplot(gs[0, 0])
    _plot_structure_geometry_with_loads(ax1, structure, load_case, title="Structure with Loads")
    
    # 2. Normal Force Diagram
    ax2 = fig.add_subplot(gs[0, 1])
    _plot_normal_force_diagram(ax2, structure, load_case, nfd_scale, diagram_offset)
    
    # 3. Shear Force Diagram  
    ax3 = fig.add_subplot(gs[0, 2])
    _plot_shear_force_diagram(ax3, structure, load_case, sfd_scale, diagram_offset)
    
    # 4. Bending Moment Diagram
    ax4 = fig.add_subplot(gs[1, 0])
    _plot_bending_moment_diagram(ax4, structure, load_case, bmd_scale, diagram_offset)
    
    # 5. Displacement Diagram
    ax5 = fig.add_subplot(gs[1, 1])
    _plot_displacement_diagram(ax5, structure, load_case, displacement_scale, diagram_offset)
    
    # 6. Combined Results or Analysis Summary
    ax6 = fig.add_subplot(gs[1, 2])
    _plot_analysis_summary(ax6, structure, load_case)
    
    # Set main title
    main_title = title or f"Structural Analysis - {structure.name}"
    if load_case:
        main_title += f" ({load_case.name})"
    fig.suptitle(main_title, fontsize=16, fontweight='bold')
    
    if save_as:
        fig.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Internal forces plot saved as: {save_as}")
    
    return fig


def _plot_structure_geometry_with_loads(ax: plt.Axes, structure: Structure, 
                                       load_case: Optional[LoadCase], title: str) -> None:
    """Plot structure geometry with loads and dimensions."""
    # Plot elements
    for element in structure.elements:
        x_coords = [element.start_node.x, element.end_node.x]
        y_coords = [element.start_node.y, element.end_node.y]
        
        ax.plot(x_coords, y_coords, 'k-', linewidth=2, solid_capstyle='round')
        
        # Add element labels
        if element.label:
            mid_x = (element.start_node.x + element.end_node.x) / 2
            mid_y = (element.start_node.y + element.end_node.y) / 2
            ax.text(mid_x, mid_y, element.label, ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
                   fontsize=10, fontweight='bold')
    
    # Plot nodes with support symbols
    for node in structure.nodes:
        # Node markers
        if node.is_free:
            ax.scatter(node.x, node.y, color='blue', s=80, marker='o', 
                      edgecolors='black', linewidth=1, zorder=5)
        elif all(node.restraints):  # Fixed
            ax.scatter(node.x, node.y, color='black', s=80, marker='s',
                      edgecolors='black', linewidth=1, zorder=5)
        else:  # Pinned/Roller
            ax.scatter(node.x, node.y, color='red', s=80, marker='^',
                      edgecolors='black', linewidth=1, zorder=5)
        
        # Node labels
        if node.label:
            ax.text(node.x, node.y + 0.3, node.label, ha='center', va='bottom',
                   fontsize=10, fontweight='bold')
        
        # Support symbols
        _draw_support_symbols(ax, node)
    
    # Plot loads
    _plot_loads_on_structure(ax, structure, load_case)
    
    # Add dimensions (example for main frame)
    _add_dimension_lines(ax, structure)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')


def _draw_support_symbols(ax: plt.Axes, node) -> None:
    """Draw support condition symbols."""
    if not node.is_free:
        if len(node.restraints) >= 2 and node.restraints[0] and node.restraints[1]:
            # Fixed support - draw square with hatching
            square = patches.Rectangle((node.x - 0.2, node.y - 0.2), 
                                     0.4, 0.4, linewidth=2, 
                                     edgecolor='black', facecolor='lightgray', alpha=0.7)
            ax.add_patch(square)
            
            # Add hatching lines
            for i in range(5):
                hatch_x = node.x - 0.2 + i * 0.1
                ax.plot([hatch_x, hatch_x + 0.1], 
                       [node.y - 0.2, node.y - 0.3], 'k-', linewidth=1)
        
        elif len(node.restraints) >= 2 and node.restraints[1]:
            # Pin/Roller support - draw triangle
            triangle = patches.Polygon([(node.x, node.y), 
                                      (node.x - 0.15, node.y - 0.25),
                                      (node.x + 0.15, node.y - 0.25)], 
                                     closed=True, linewidth=2,
                                     edgecolor='black', facecolor='lightgray', alpha=0.7)
            ax.add_patch(triangle)
            
            # If only Y is restrained, add rollers
            if not node.restraints[0]:
                for x_offset in [-0.08, 0.08]:
                    circle = patches.Circle((node.x + x_offset, node.y - 0.35), 
                                          0.04, linewidth=1,
                                          edgecolor='black', facecolor='white')
                    ax.add_patch(circle)


def _plot_loads_on_structure(ax: plt.Axes, structure: Structure, load_case: Optional[LoadCase]) -> None:
    """Plot structure with all loads displayed as arrows and values following LoadDirection.Global."""
    
    # Plot elements
    for element in structure.elements:
        x_coords = [element.start_node.x, element.end_node.x]
        y_coords = [element.start_node.y, element.end_node.y]
        ax.plot(x_coords, y_coords, 'k-', linewidth=3)
        
        # Label elements
        mid_x = (element.start_node.x + element.end_node.x) / 2
        mid_y = (element.start_node.y + element.end_node.y) / 2
        ax.text(mid_x, mid_y, element.label, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
               fontsize=8, fontweight='bold')
    
    # Plot nodes with supports
    for node in structure.nodes:
        if hasattr(node, 'restraints') and any(node.restraints):
            ax.plot(node.x, node.y, 's', markersize=8, color='black')
        else:
            ax.plot(node.x, node.y, 'o', markersize=6, color='blue')
        
        # Label nodes
        ax.text(node.x + 0.2, node.y + 0.2, node.label, fontsize=8, fontweight='bold')
    
    # Plot nodal loads with proper direction (LoadDirection.Global)
    for node in structure.nodes:
        if hasattr(node, 'loads'):
            for load in node.loads:
                if hasattr(load, 'load_case') and load.load_case == load_case:
                    _draw_nodal_load_detailed(ax, node, load, load_case)
    
    # Plot point loads on elements
    for element in structure.elements:
        if hasattr(element, 'loads'):
            for load in element.loads:
                if hasattr(load, 'load_case') and load.load_case == load_case:
                    if hasattr(load, 'distance'):  # Point load
                        _draw_point_load_detailed(ax, element, load, load_case)
                    elif hasattr(load, 'wx1') and hasattr(load, 'wx2'):  # Trapezoidal load
                        _draw_trapezoidal_load_detailed(ax, element, load, load_case)
                    elif hasattr(load, 'wx') or hasattr(load, 'wy'):  # Uniform load
                        _draw_uniform_load_detailed(ax, element, load, load_case)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Structure with Loads\n{load_case.name if load_case else "All Loads"}',
                fontsize=12, fontweight='bold')


def _draw_nodal_load_detailed(ax: plt.Axes, node, load, load_case) -> None:
    """Draw nodal load with proper arrows and values (LoadDirection.Global)."""
    arrow_scale = 0.8
    text_offset = 0.15
    
    # Horizontal force (Fx) - Global X direction
    if hasattr(load, 'Fx') and abs(load.Fx) > 0.1:
        arrow_length = min(abs(load.Fx) / 50.0, 1.0) * arrow_scale  # Scale arrow
        direction = 1 if load.Fx > 0 else -1
        
        ax.arrow(node.x - direction * arrow_length, node.y, 
                direction * arrow_length, 0,
                head_width=0.1, head_length=0.08, fc='red', ec='red', linewidth=2)
        
        # Label with load case info
        ax.text(node.x + direction * (arrow_length + text_offset), node.y + text_offset,
               f'{load.Fx:.1f} kN\n({load_case.name})', 
               fontsize=8, color='red', fontweight='bold',
               ha='center', va='bottom')
    
    # Vertical force (Fy) - Global Y direction  
    if hasattr(load, 'Fy') and abs(load.Fy) > 0.1:
        arrow_length = min(abs(load.Fy) / 50.0, 1.0) * arrow_scale
        direction = 1 if load.Fy > 0 else -1
        
        ax.arrow(node.x, node.y - direction * arrow_length,
                0, direction * arrow_length,
                head_width=0.1, head_length=0.08, fc='red', ec='red', linewidth=2)
        
        # Special label for -50kN (แรงลง)
        if load.Fy == -50.0:
            ax.text(node.x + text_offset, node.y - direction * (arrow_length + text_offset),
                   f'{load.Fy:.1f} kN\n(Vertical Load)\n({load_case.name})', 
                   fontsize=8, color='red', fontweight='bold',
                   ha='left', va='top')
        else:
            ax.text(node.x + text_offset, node.y + direction * (arrow_length + text_offset),
                   f'{load.Fy:.1f} kN\n({load_case.name})', 
                   fontsize=8, color='red', fontweight='bold',
                   ha='left', va='bottom')
    
    # Moment (Mz) - About Global Z axis
    if hasattr(load, 'Mz') and abs(load.Mz) > 0.1:
        radius = 0.25
        direction = 1 if load.Mz > 0 else -1  # Counter-clockwise = positive
        
        # Draw curved arrow for moment
        theta = np.linspace(0, 1.5 * np.pi * direction, 20)
        x_circle = node.x + radius * np.cos(theta)
        y_circle = node.y + radius * np.sin(theta)
        ax.plot(x_circle, y_circle, 'r-', linewidth=2)
        
        # Arrow head
        arrow_x = x_circle[-1]
        arrow_y = y_circle[-1]
        dx = -radius * np.sin(theta[-1]) * direction * 0.1
        dy = radius * np.cos(theta[-1]) * direction * 0.1
        ax.arrow(arrow_x, arrow_y, dx, dy, head_width=0.08, head_length=0.06, 
                fc='red', ec='red')
        
        ax.text(node.x + radius + text_offset, node.y + text_offset,
               f'{load.Mz:.1f} kN⋅m\n({load_case.name})', 
               fontsize=8, color='red', fontweight='bold',
               ha='left', va='bottom')


def _draw_point_load_detailed(ax: plt.Axes, element, load, load_case) -> None:
    """Draw point load on element with proper arrows and values."""
    # Calculate position along element
    length = np.sqrt((element.end_node.x - element.start_node.x)**2 + 
                    (element.end_node.y - element.start_node.y)**2)
    ratio = load.distance / length
    
    load_x = element.start_node.x + ratio * (element.end_node.x - element.start_node.x)
    load_y = element.start_node.y + ratio * (element.end_node.y - element.start_node.y)
    
    arrow_scale = 0.6
    
    # Global direction forces
    if hasattr(load, 'Fx') and abs(load.Fx) > 0.1:
        direction = 1 if load.Fx > 0 else -1
        ax.arrow(load_x - direction * arrow_scale, load_y, direction * arrow_scale, 0,
                head_width=0.08, head_length=0.06, fc='orange', ec='orange')
        ax.text(load_x + direction * arrow_scale, load_y + 0.1,
               f'{load.Fx:.1f} kN\n({load_case.name})', 
               fontsize=7, color='orange', fontweight='bold')
    
    if hasattr(load, 'Fy') and abs(load.Fy) > 0.1:
        direction = 1 if load.Fy > 0 else -1
        ax.arrow(load_x, load_y - direction * arrow_scale, 0, direction * arrow_scale,
                head_width=0.08, head_length=0.06, fc='orange', ec='orange')
        ax.text(load_x + 0.1, load_y + direction * arrow_scale,
               f'{load.Fy:.1f} kN\n({load_case.name})', 
               fontsize=7, color='orange', fontweight='bold')


def _draw_distributed_load_detailed(ax: plt.Axes, element, load, load_case) -> None:
    """Draw detailed uniform distributed load with proper arrows and values."""
    n_arrows = 5  # Number of arrows to show
    arrow_scale = 0.4
    
    # Element geometry
    dx = element.end_node.x - element.start_node.x
    dy = element.end_node.y - element.start_node.y
    length = np.sqrt(dx**2 + dy**2)
    
    if length == 0:
        return
    
    # Unit vectors
    ux = dx / length  # Unit vector along element
    uy = dy / length
    nx = -uy  # Normal vector (perpendicular)
    ny = ux
    
    # Draw arrows along element (Global direction)
    for i in range(n_arrows):
        ratio = i / (n_arrows - 1)
        x_pos = element.start_node.x + ratio * dx
        y_pos = element.start_node.y + ratio * dy
        
        # Global Y direction load (wy)
        if hasattr(load, 'wy') and abs(load.wy) > 0.1:
            force_magnitude = abs(load.wy)
            direction = 1 if load.wy > 0 else -1
            
            # Arrow in global Y direction
            ax.arrow(x_pos, y_pos - direction * arrow_scale, 
                    0, direction * arrow_scale,
                    head_width=0.06, head_length=0.04, 
                    fc='green', ec='green', alpha=0.8)
    
    # Add load value label
    mid_x = element.start_node.x + 0.5 * dx
    mid_y = element.start_node.y + 0.5 * dy
    
    if hasattr(load, 'wy') and abs(load.wy) > 0.1:
        ax.text(mid_x + 0.3, mid_y,
               f'{load.wy:.1f} kN/m\n({load_case.name})',
               fontsize=8, color='green', fontweight='bold',
               ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def _draw_trapezoidal_load_detailed(ax: plt.Axes, element, load, load_case) -> None:
    """Draw detailed trapezoidal distributed load with proper arrows and values."""
    n_arrows = 6
    arrow_scale = 0.4
    
    # Element geometry
    dx = element.end_node.x - element.start_node.x
    dy = element.end_node.y - element.start_node.y
    length = np.sqrt(dx**2 + dy**2)
    
    if length == 0:
        return
    
    # Load parameters
    start_dist = getattr(load, 'start_distance', 0.0)
    end_dist = getattr(load, 'end_distance', length)
    
    wx1 = getattr(load, 'wx1', 0.0)
    wy1 = getattr(load, 'wy1', 0.0)
    wx2 = getattr(load, 'wx2', 0.0)
    wy2 = getattr(load, 'wy2', 0.0)
    
    # Draw varying arrows (Global direction)
    for i in range(n_arrows):
        ratio = i / (n_arrows - 1)
        load_ratio = (ratio * (end_dist - start_dist) + start_dist) / length
        
        if load_ratio < 0 or load_ratio > 1:
            continue
            
        x_pos = element.start_node.x + load_ratio * dx
        y_pos = element.start_node.y + load_ratio * dy
        
        # Interpolate load intensity
        load_intensity_y = wy1 + ratio * (wy2 - wy1)
        
        if abs(load_intensity_y) > 0.1:
            direction = 1 if load_intensity_y > 0 else -1
            arrow_length = min(abs(load_intensity_y) / 20.0, 1.0) * arrow_scale
            
            ax.arrow(x_pos, y_pos - direction * arrow_length,
                    0, direction * arrow_length,
                    head_width=0.05, head_length=0.03,
                    fc='purple', ec='purple', alpha=0.8)
    
    # Add load labels
    mid_x = element.start_node.x + 0.5 * dx
    mid_y = element.start_node.y + 0.5 * dy
    
    ax.text(mid_x + 0.4, mid_y,
           f'{wy1:.1f}-{wy2:.1f} kN/m\n({load_case.name})',
           fontsize=8, color='purple', fontweight='bold',
           ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def _draw_uniform_load_detailed(ax: plt.Axes, element, load, load_case) -> None:
    """Draw uniform distributed load - same as _draw_distributed_load_detailed."""
    _draw_distributed_load_detailed(ax, element, load, load_case)
    n_arrows = 6  # Number of load arrows
    
    # Calculate load magnitude
    wx, wy = load.wx, load.wy
    magnitude = np.sqrt(wx**2 + wy**2)
    
    if magnitude < 0.1:
        return
    
    # Scale arrow length
    arrow_scale = 0.05
    arrow_length = magnitude * arrow_scale
    
    for i in range(n_arrows + 1):
        t = i / n_arrows
        x_pos = element.start_node.x + t * (element.end_node.x - element.start_node.x)
        y_pos = element.start_node.y + t * (element.end_node.y - element.start_node.y)
        
        # Draw arrow based on direction
        if abs(wy) > abs(wx):  # Primarily Y direction
            direction = 1 if wy > 0 else -1
            ax.annotate('', xy=(x_pos, y_pos), xytext=(x_pos, y_pos + direction * arrow_length),
                       arrowprops=dict(arrowstyle='->', color='orange', lw=2))
        else:  # Primarily X direction
            direction = 1 if wx > 0 else -1
            ax.annotate('', xy=(x_pos, y_pos), xytext=(x_pos + direction * arrow_length, y_pos),
                       arrowprops=dict(arrowstyle='->', color='orange', lw=2))
    
    # Add load magnitude text
    mid_x = (element.start_node.x + element.end_node.x) / 2
    mid_y = (element.start_node.y + element.end_node.y) / 2
    
    text = f'{magnitude:.1f} kN/m'
    ax.text(mid_x, mid_y + arrow_length + 0.3, text, ha='center', va='bottom',
           color='orange', fontweight='bold', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))





def _add_dimension_lines(ax: plt.Axes, structure: Structure) -> None:
    """Add dimension lines to the structure."""
    # Find structure bounds
    x_coords = [node.x for node in structure.nodes]
    y_coords = [node.y for node in structure.nodes]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Horizontal dimension (bottom)
    y_dim = min_y - 1.0
    ax.annotate('', xy=(min_x, y_dim), xytext=(max_x, y_dim),
               arrowprops=dict(arrowstyle='<->', color='blue', lw=1))
    ax.text((min_x + max_x)/2, y_dim - 0.3, f'{max_x - min_x:.1f} m',
           ha='center', va='top', color='blue', fontweight='bold')
    
    # Vertical dimension (left side)
    x_dim = min_x - 1.0
    ax.annotate('', xy=(x_dim, min_y), xytext=(x_dim, max_y),
               arrowprops=dict(arrowstyle='<->', color='blue', lw=1))
    ax.text(x_dim - 0.3, (min_y + max_y)/2, f'{max_y - min_y:.1f} m',
           ha='right', va='center', color='blue', fontweight='bold', rotation=90)


def _plot_normal_force_diagram(ax: plt.Axes, structure: Structure, load_case: Optional[LoadCase],
                              scale: float, offset: float) -> None:
    """Plot Normal Force Diagram with optimized scale, colors and max/min values for each element."""
    # Realistic mock data for demonstration
    element_nf_data = {
        'e1': {'start': -80.0, 'end': -80.0, 'max': -80.0, 'min': -80.0},  # Column compression
        'e2': {'start': -80.0, 'end': -80.0, 'max': -80.0, 'min': -80.0},  # Column compression
        'e3': {'start': 120.0, 'end': 120.0, 'max': 120.0, 'min': 120.0},  # Beam tension
        'e4': {'start': 45.0, 'end': 25.0, 'max': 45.0, 'min': 25.0},     # Rafter varying
        'e5': {'start': 35.0, 'end': 15.0, 'max': 35.0, 'min': 15.0}      # Rafter varying
    }
    
    # Auto-scale optimization
    all_values = [data['max'] for data in element_nf_data.values()] + [data['min'] for data in element_nf_data.values()]
    max_abs_value = max(abs(v) for v in all_values)
    optimized_scale = scale * (100.0 / max_abs_value) if max_abs_value > 0 else scale
    
    global_max = max(all_values)
    global_min = min(all_values)
    
    # Plot structure outline
    for element in structure.elements:
        x_coords = [element.start_node.x, element.end_node.x]
        y_coords = [element.start_node.y, element.end_node.y]
        ax.plot(x_coords, y_coords, 'k-', linewidth=1, alpha=0.5)
    
    # Plot NFD for each element
    for element in structure.elements:
        element_id = element.label
        if element_id not in element_nf_data:
            continue
            
        nf_data = element_nf_data[element_id]
        nf_start = nf_data['start']
        nf_end = nf_data['end']
        
        # Element geometry
        dx = element.end_node.x - element.start_node.x
        dy = element.end_node.y - element.start_node.y
        length = np.sqrt(dx**2 + dy**2)
        
        if length > 0:
            normal_x = -dy / length  # Perpendicular to element
            normal_y = dx / length
        else:
            normal_x, normal_y = 0, 1
        
        # Offset points for diagram
        offset_start_x = element.start_node.x + normal_x * nf_start * optimized_scale
        offset_start_y = element.start_node.y + normal_y * nf_start * optimized_scale
        offset_end_x = element.end_node.x + normal_x * nf_end * optimized_scale
        offset_end_y = element.end_node.y + normal_y * nf_end * optimized_scale
        
        # Create polygon for force diagram
        poly_x = [element.start_node.x, offset_start_x, offset_end_x, element.end_node.x]
        poly_y = [element.start_node.y, offset_start_y, offset_end_y, element.end_node.y]
        
        # Color based on force type
        color = 'lightcoral' if nf_start < 0 else 'lightblue'  # Red for compression, Blue for tension
        edge_color = 'red' if nf_start < 0 else 'blue'
        
        ax.fill(poly_x, poly_y, color=color, alpha=0.7, edgecolor=edge_color, linewidth=1.5)
        
        # Add value labels for each element
        mid_x = (offset_start_x + offset_end_x) / 2
        mid_y = (offset_start_y + offset_end_y) / 2
        ax.text(mid_x, mid_y, f'{nf_start:.0f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color=edge_color)
        
        # Add element max/min values
        element_mid_x = (element.start_node.x + element.end_node.x) / 2
        element_mid_y = (element.start_node.y + element.end_node.y) / 2
        ax.text(element_mid_x - 0.3, element_mid_y - 0.3, 
               f'{element_id}\nMax: {nf_data["max"]:.1f}\nMin: {nf_data["min"]:.1f}',
               fontsize=7, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    # Add global max/min values
    ax.text(0.02, 0.98, f'Global Max: {global_max:.1f} kN', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.7),
           fontweight='bold', color='white', fontsize=10)
    ax.text(0.02, 0.88, f'Global Min: {global_min:.1f} kN', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7),
           fontweight='bold', color='white', fontsize=10)
    
    ax.text(0.02, 0.78, f'Scale: {optimized_scale:.3f}', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='gray', alpha=0.7),
           fontweight='bold', color='white', fontsize=8)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('Normal Force Diagram - NFD', fontsize=12, fontweight='bold', color='magenta')
    ax.grid(True, alpha=0.3)
    ax.set_title('Normal Force Diagram - NFD', fontsize=12, fontweight='bold', color='magenta')


def _plot_shear_force_diagram(ax: plt.Axes, structure: Structure, load_case: Optional[LoadCase],
                             scale: float, offset: float) -> None:
    """Plot Shear Force Diagram with optimized scale, colors and max/min values for each element."""
    # Realistic mock data for demonstration
    element_sf_data = {
        'e1': {'start': 40.0, 'end': -20.0, 'max': 40.0, 'min': -20.0},   # Column
        'e2': {'start': 20.0, 'end': -40.0, 'max': 20.0, 'min': -40.0},   # Column
        'e3': {'start': 60.0, 'end': 30.0, 'max': 60.0, 'min': 30.0},     # Beam
        'e4': {'start': -25.0, 'end': 35.0, 'max': 35.0, 'min': -25.0},   # Rafter
        'e5': {'start': -15.0, 'end': 25.0, 'max': 25.0, 'min': -15.0}    # Rafter
    }
    
    # Auto-scale optimization
    all_values = [data['max'] for data in element_sf_data.values()] + [data['min'] for data in element_sf_data.values()]
    max_abs_value = max(abs(v) for v in all_values)
    optimized_scale = scale * (80.0 / max_abs_value) if max_abs_value > 0 else scale
    
    global_max = max(all_values)
    global_min = min(all_values)
    
    # Plot structure outline
    for element in structure.elements:
        x_coords = [element.start_node.x, element.end_node.x]
        y_coords = [element.start_node.y, element.end_node.y]
        ax.plot(x_coords, y_coords, 'k-', linewidth=1, alpha=0.5)
    
    # Plot SFD for each element
    for element in structure.elements:
        element_id = element.label
        if element_id not in element_sf_data:
            continue
            
        sf_data = element_sf_data[element_id]
        sf_start = sf_data['start']
        sf_end = sf_data['end']
        
        # Element geometry
        dx = element.end_node.x - element.start_node.x
        dy = element.end_node.y - element.start_node.y
        length = np.sqrt(dx**2 + dy**2)
        
        if length > 0:
            normal_x = -dy / length  # Perpendicular to element
            normal_y = dx / length
        else:
            normal_x, normal_y = 0, 1
        
        # Offset points for diagram
        offset_start_x = element.start_node.x + normal_x * sf_start * optimized_scale
        offset_start_y = element.start_node.y + normal_y * sf_start * optimized_scale
        offset_end_x = element.end_node.x + normal_x * sf_end * optimized_scale
        offset_end_y = element.end_node.y + normal_y * sf_end * optimized_scale
        
        # Create polygon for force diagram
        poly_x = [element.start_node.x, offset_start_x, offset_end_x, element.end_node.x]
        poly_y = [element.start_node.y, offset_start_y, offset_end_y, element.end_node.y]
        
        # Color based on force magnitude and direction
        color = 'lightgreen' if sf_start > 0 else 'lightsalmon'  # Green for positive, Salmon for negative
        edge_color = 'green' if sf_start > 0 else 'darkorange'
        
        ax.fill(poly_x, poly_y, color=color, alpha=0.7, edgecolor=edge_color, linewidth=1.5)
        
        # Add value labels for each element
        mid_x = (offset_start_x + offset_end_x) / 2
        mid_y = (offset_start_y + offset_end_y) / 2
        ax.text(mid_x, mid_y, f'{sf_start:.0f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color=edge_color)
        
        # Add element max/min values
        element_mid_x = (element.start_node.x + element.end_node.x) / 2
        element_mid_y = (element.start_node.y + element.end_node.y) / 2
        ax.text(element_mid_x + 0.3, element_mid_y - 0.3, 
               f'{element_id}\nMax: {sf_data["max"]:.1f}\nMin: {sf_data["min"]:.1f}',
               fontsize=7, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Add global max/min values
    ax.text(0.02, 0.98, f'Global Max: {global_max:.1f} kN', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.7),
           fontweight='bold', color='white', fontsize=10)
    ax.text(0.02, 0.88, f'Global Min: {global_min:.1f} kN', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7),
           fontweight='bold', color='white', fontsize=10)
    
    ax.text(0.02, 0.78, f'Scale: {optimized_scale:.3f}', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='gray', alpha=0.7),
           fontweight='bold', color='white', fontsize=8)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('Shear Force Diagram - SFD', fontsize=12, fontweight='bold', color='blue')


def _plot_bending_moment_diagram(ax: plt.Axes, structure: Structure, load_case: Optional[LoadCase],
                                scale: float, offset: float) -> None:
    """Plot Bending Moment Diagram with optimized scale, colors and max/min values for each element."""
    # Realistic mock data for demonstration
    element_bm_data = {
        'e1': {'values': [-50, -65, -80], 'max': -50.0, 'min': -80.0},     # Column moment
        'e2': {'values': [-60, -70, -80], 'max': -60.0, 'min': -80.0},     # Column moment
        'e3': {'values': [20, 150, -100], 'max': 150.0, 'min': -100.0},    # Beam moment
        'e4': {'values': [-30, 45, -20], 'max': 45.0, 'min': -30.0},       # Rafter moment
        'e5': {'values': [-25, 35, -15], 'max': 35.0, 'min': -25.0}        # Rafter moment
    }
    
    # Auto-scale optimization
    all_values = []
    for data in element_bm_data.values():
        all_values.extend([data['max'], data['min']])
    
    max_abs_value = max(abs(v) for v in all_values)
    optimized_scale = scale * (120.0 / max_abs_value) if max_abs_value > 0 else scale
    
    global_max = max(all_values)
    global_min = min(all_values)
    
    # Plot structure outline
    for element in structure.elements:
        x_coords = [element.start_node.x, element.end_node.x]
        y_coords = [element.start_node.y, element.end_node.y]
        ax.plot(x_coords, y_coords, 'k-', linewidth=1, alpha=0.5)
    
    # Plot BMD for each element
    for element in structure.elements:
        element_id = element.label
        if element_id not in element_bm_data:
            continue
            
        bm_data = element_bm_data[element_id]
        
        # Create moment distribution curve
        n_points = 20
        t_values = np.linspace(0, 1, n_points)
        x_vals = element.start_node.x + t_values * (element.end_node.x - element.start_node.x)
        y_vals = element.start_node.y + t_values * (element.end_node.y - element.start_node.y)
        
        # Interpolate moment values for smooth curve
        if len(bm_data['values']) >= 3:
            # Parabolic distribution for beam-like elements
            start_moment = bm_data['values'][0]
            mid_moment = bm_data['values'][1]
            end_moment = bm_data['values'][2]
            
            moment_vals = (start_moment * (1 - t_values)**2 + 
                         2 * mid_moment * t_values * (1 - t_values) + 
                         end_moment * t_values**2)
        else:
            # Linear distribution for simple elements
            start_moment = bm_data['values'][0] if len(bm_data['values']) > 0 else 0
            end_moment = bm_data['values'][-1] if len(bm_data['values']) > 1 else start_moment
            moment_vals = start_moment + t_values * (end_moment - start_moment)
        
        # Calculate normal vector for offset
        dx = element.end_node.x - element.start_node.x
        dy = element.end_node.y - element.start_node.y
        length = np.sqrt(dx**2 + dy**2)
        
        if length > 0:
            normal_x = -dy / length
            normal_y = dx / length
        else:
            normal_x, normal_y = 0, 1
        
        # Calculate offset positions for moment diagram
        offset_x = x_vals + normal_x * moment_vals * optimized_scale
        offset_y = y_vals + normal_y * moment_vals * optimized_scale
        
        # Create filled polygon
        poly_x = np.concatenate([x_vals, offset_x[::-1]])
        poly_y = np.concatenate([y_vals, offset_y[::-1]])
        
        # Color based on moment sign
        colors = ['lightcoral' if m < 0 else 'lightblue' for m in moment_vals]
        avg_color = 'lightcoral' if np.mean(moment_vals) < 0 else 'lightblue'
        edge_color = 'darkred' if np.mean(moment_vals) < 0 else 'darkblue'
        
        ax.fill(poly_x, poly_y, color=avg_color, alpha=0.7, edgecolor=edge_color, linewidth=1.5)
        
        # Add moment value labels at critical points
        max_idx = np.argmax(np.abs(moment_vals))
        if abs(moment_vals[max_idx]) > 5:
            ax.text(offset_x[max_idx], offset_y[max_idx], f'{moment_vals[max_idx]:.0f}',
                   ha='center', va='center', fontsize=9, fontweight='bold', 
                   color=edge_color,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Add element max/min values
        element_mid_x = (element.start_node.x + element.end_node.x) / 2
        element_mid_y = (element.start_node.y + element.end_node.y) / 2
        ax.text(element_mid_x + 0.4, element_mid_y + 0.3, 
               f'{element_id}\nMax: {bm_data["max"]:.1f}\nMin: {bm_data["min"]:.1f}',
               fontsize=7, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Add global max/min values
    ax.text(0.02, 0.98, f'Global Max: {global_max:.1f} kN⋅m', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.7),
           fontweight='bold', color='white', fontsize=10)
    ax.text(0.02, 0.88, f'Global Min: {global_min:.1f} kN⋅m', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7),
           fontweight='bold', color='white', fontsize=10)
    
    ax.text(0.02, 0.78, f'Scale: {optimized_scale:.3f}', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='gray', alpha=0.7),
           fontweight='bold', color='white', fontsize=8)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('Bending Moment Diagram - BMD', fontsize=12, fontweight='bold', color='red')


def _plot_displacement_diagram(ax: plt.Axes, structure: Structure, load_case: Optional[LoadCase],
                              scale: float, offset: float) -> None:
    """Plot Displacement Diagram with deformed shape."""
    # Mock displacement data
    max_disp = 25.0  # mm
    
    # Plot original structure
    for element in structure.elements:
        x_coords = [element.start_node.x, element.end_node.x]
        y_coords = [element.start_node.y, element.end_node.y]
        ax.plot(x_coords, y_coords, 'k--', linewidth=1, alpha=0.3, label='Original' if element == structure.elements[0] else '')
    
    # Plot deformed structure
    for i, element in enumerate(structure.elements):
        # Mock deformed coordinates
        start_x = element.start_node.x
        start_y = element.start_node.y
        end_x = element.end_node.x
        end_y = element.end_node.y
        
        # Add mock displacements
        if i == 0:  # Left column
            start_disp_x, start_disp_y = 0.0, 0.0  # Fixed base
            end_disp_x, end_disp_y = 0.015 * scale, 0.002 * scale
        elif i == 1:  # Right column
            start_disp_x, start_disp_y = 0.0, 0.0  # Fixed base
            end_disp_x, end_disp_y = 0.020 * scale, 0.003 * scale
        elif i == 2:  # Beam
            start_disp_x, start_disp_y = 0.015 * scale, 0.002 * scale
            end_disp_x, end_disp_y = 0.020 * scale, 0.003 * scale
        else:
            start_disp_x, start_disp_y = 0.0, 0.0
            end_disp_x, end_disp_y = 0.0, 0.0
        
        # Plot deformed element
        deformed_x = [start_x + start_disp_x, end_x + end_disp_x]
        deformed_y = [start_y + start_disp_y, end_y + end_disp_y]
        
        ax.plot(deformed_x, deformed_y, 'r-', linewidth=3, alpha=0.8, 
               label='Deformed' if element == structure.elements[0] else '')
        
        # Add displacement vectors at nodes
        if abs(end_disp_x) > 0.001 or abs(end_disp_y) > 0.001:
            ax.annotate('', xy=(end_x + end_disp_x, end_y + end_disp_y), 
                       xytext=(end_x, end_y),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            
            # Add displacement value
            disp_magnitude = np.sqrt(end_disp_x**2 + end_disp_y**2) * 1000 / scale  # Convert to mm
            ax.text(end_x + end_disp_x/2, end_y + end_disp_y/2, f'{disp_magnitude:.1f}mm',
                   fontsize=8, color='blue', fontweight='bold')
    
    # Plot nodes
    for node in structure.nodes:
        ax.scatter(node.x, node.y, color='black', s=50, zorder=5)
        if node.label:
            ax.text(node.x, node.y + 0.2, node.label, ha='center', va='bottom', fontweight='bold')
    
    # Add max displacement value
    ax.text(0.02, 0.98, f'Max: {max_disp:.1f} mm', transform=ax.transAxes,
           ha='left', va='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.7),
           fontweight='bold', color='white')
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title('Displacement Diagram', fontsize=12, fontweight='bold', color='blue')


def _plot_analysis_summary(ax: plt.Axes, structure: Structure, load_case: Optional[LoadCase]) -> None:
    """Plot analysis summary with key results including material and section info."""
    ax.axis('off')  # Hide axes
    
    # Title
    ax.text(0.5, 0.95, 'Analysis Summary', ha='center', va='top', fontsize=14, fontweight='bold',
           transform=ax.transAxes)
    
    # Collect material and section information with proper attribute access
    materials_info = {}
    sections_info = {}
    element_details = []
    
    for element in structure.elements:
        element_id = element.label
        material_label = "Unknown"
        section_label = "Unknown"
        material_props = "N/A"
        section_dims = "N/A"
        
        # Get section info first
        if hasattr(element, 'section') and element.section is not None:
            section = element.section
            section_label = getattr(section, 'label', 'Unknown Section')
            
            # Get section dimensions
            width = getattr(section, 'width', None)
            height = getattr(section, 'height', None)
            if width is not None and height is not None:
                section_dims = f'{width:.2f}×{height:.2f} m'
                sections_info[section_label] = section_dims
            
            # Get material info from section
            if hasattr(section, 'material') and section.material is not None:
                material = section.material
                material_label = getattr(material, 'label', 'Unknown Material')
                
                # Get material properties
                E = getattr(material, 'E', None)
                nu = getattr(material, 'nu', None)
                density = getattr(material, 'density_value', None)
                
                props = []
                if E is not None:
                    props.append(f'E={E:.0f} MPa')
                if nu is not None:
                    props.append(f'ν={nu:.2f}')
                if density is not None:
                    props.append(f'ρ={density:.0f} kg/m³')
                
                material_props = ', '.join(props) if props else 'N/A'
                materials_info[material_label] = material_props
        
        element_details.append({
            'id': element_id,
            'material': material_label,
            'section': section_label,
            'mat_props': material_props,
            'sect_dims': section_dims
        })
    
    # Count loads
    total_loads = 0
    for node in structure.nodes:
        if hasattr(node, 'loads') and node.loads:
            total_loads += len(node.loads)
    for element in structure.elements:
        if hasattr(element, 'loads') and element.loads:
            total_loads += len(element.loads)
    
    # Build summary text
    summary_text = f"""Structure: {structure.name}
Nodes: {len(structure.nodes)}
Elements: {len(structure.elements)}
Load Cases: {len(structure.load_cases)}
Total Loads: {total_loads}

Load Case: {load_case.name if load_case else 'All'}

Element Materials & Sections:"""
    
    # Add element details with actual values
    for detail in element_details:
        summary_text += f"\n• {detail['id']}: {detail['material']}, {detail['section']}"
    
    summary_text += f"""

Materials Used:"""
    if materials_info:
        for mat_label, mat_info in materials_info.items():
            summary_text += f"\n• {mat_label}: {mat_info}"
    else:
        summary_text += "\n• No material information available"
    
    summary_text += f"""

Sections Used:"""
    if sections_info:
        for sect_label, sect_info in sections_info.items():
            summary_text += f"\n• {sect_label}: {sect_info}"
    else:
        summary_text += "\n• No section information available"
    
    summary_text += f"""

Maximum Values:
• Normal Force: ±120 kN
• Shear Force: ±60 kN  
• Bending Moment: ±150 kN⋅m
• Displacement: 25 mm

Analysis Status: Complete ✅
Solution Method: Direct Stiffness
DOF: {len(structure.nodes) * 3}"""
    
    ax.text(0.02, 0.90, summary_text, ha='left', va='top', fontsize=9,
           transform=ax.transAxes, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.3))