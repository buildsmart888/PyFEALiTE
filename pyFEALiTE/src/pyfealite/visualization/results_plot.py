"""Results visualization functions."""

from typing import Optional, List, Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import warnings

from .plotter import StructurePlotter
from ..core.structure import Structure
from ..core.node import Node2D
from ..loads.base import LoadCase


def plot_displacements(structure: Structure, load_case: LoadCase,
                      scale: float = 100.0, component: str = 'all',
                      figsize: Tuple[float, float] = (12, 8),
                      save_as: Optional[str] = None) -> plt.Figure:
    """
    Plot displacement results.
    
    Args:
        structure: Analyzed structure
        load_case: Load case to display
        scale: Displacement magnification factor
        component: 'all', 'UX', 'UY', or 'RZ'
        figsize: Figure size
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure
    """
    if structure.analysis_status != "success":
        raise ValueError("Structure must be analyzed before plotting displacements")
    
    plotter = StructurePlotter(structure, figsize=figsize)
    
    if component.lower() == 'all':
        # Create subplot for each displacement component
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f"Displacement Results - {load_case.name}", fontsize=16, fontweight='bold')
        
        components = ['UX', 'UY', 'RZ', 'Total']
        titles = ['Horizontal Displacement (UX)', 'Vertical Displacement (UY)', 
                 'Rotation (RZ)', 'Deformed Shape']
        
        for i, (comp, title) in enumerate(zip(components, titles)):
            row, col = divmod(i, 2)
            plotter.ax = axes[row, col]
            
            if comp == 'Total':
                plotter.plot_deformed_shape(load_case, scale=scale, show_original=True)
            else:
                _plot_displacement_component(plotter, structure, load_case, comp, scale)
            
            plotter.ax.set_title(title)
            plotter.ax.grid(True, alpha=0.3)
            plotter.ax.set_aspect('equal')
    
    else:
        # Plot single component
        fig, ax = plt.subplots(figsize=figsize)
        plotter.ax = ax
        plotter.fig = fig
        
        if component.upper() == 'TOTAL':
            plotter.plot_deformed_shape(load_case, scale=scale, show_original=True)
            title = "Deformed Shape"
        else:
            _plot_displacement_component(plotter, structure, load_case, component.upper(), scale)
            comp_names = {'UX': 'Horizontal', 'UY': 'Vertical', 'RZ': 'Rotation'}
            title = f"{comp_names.get(component.upper(), component)} Displacement"
        
        ax.set_title(f"{title} - {load_case.name}")
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if save_as:
        fig.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Displacement plot saved as: {save_as}")
    
    return fig


def _plot_displacement_component(plotter: StructurePlotter, structure: Structure, 
                                load_case: LoadCase, component: str, scale: float) -> None:
    """Plot specific displacement component."""
    # Plot original geometry
    plotter.plot_geometry(show_labels=True)
    
    # Component index mapping
    comp_idx = {'UX': 0, 'UY': 1, 'RZ': 2}
    
    if component not in comp_idx:
        warnings.warn(f"Unknown component: {component}")
        return
    
    idx = comp_idx[component]
    
    # Get displacements for all nodes
    displacements = []
    positions = []
    
    for node in structure.nodes:
        disp = structure.get_node_displacement(node, load_case)
        displacements.append(disp[idx])
        positions.append((node.x, node.y))
    
    displacements = np.array(displacements)
    
    # Create colormap based on displacement magnitude
    if len(displacements) > 0:
        vmin, vmax = np.min(displacements), np.max(displacements)
        
        # Plot displacement vectors or values
        for i, ((x, y), disp_val) in enumerate(zip(positions, displacements)):
            if component in ['UX', 'UY']:
                # Draw displacement arrow
                if component == 'UX':
                    dx, dy = disp_val * scale, 0
                else:  # UY
                    dx, dy = 0, disp_val * scale
                
                if abs(disp_val) > 1e-12:
                    arrow = FancyArrowPatch((x, y), (x + dx, y + dy),
                                           arrowstyle='->', color='red', 
                                           linewidth=2, mutation_scale=15)
                    plotter.ax.add_patch(arrow)
                
                # Add displacement value as text
                plotter.ax.text(x + dx * 0.5, y + dy * 0.5, f"{disp_val:.2e}",
                               ha='center', va='center', fontsize=8,
                               bbox=dict(boxstyle='round,pad=0.2', 
                                       facecolor='white', alpha=0.8))
            
            else:  # RZ (rotation)
                if abs(disp_val) > 1e-12:
                    # Draw rotation arc
                    from matplotlib.patches import Arc
                    radius = 0.1 * abs(disp_val) * scale
                    direction = 1 if disp_val > 0 else -1
                    
                    arc = Arc((x, y), 2*radius, 2*radius, angle=0,
                             theta1=0, theta2=270*direction, 
                             linewidth=2, color='blue')
                    plotter.ax.add_patch(arc)
                    
                    # Add rotation value
                    plotter.ax.text(x + radius, y, f"{disp_val:.2e} rad",
                                   ha='left', va='center', fontsize=8,
                                   bbox=dict(boxstyle='round,pad=0.2',
                                           facecolor='white', alpha=0.8))


def plot_reactions(structure: Structure, load_case: LoadCase,
                  scale: float = 0.1, figsize: Tuple[float, float] = (10, 8),
                  save_as: Optional[str] = None) -> plt.Figure:
    """
    Plot support reactions.
    
    Args:
        structure: Analyzed structure
        load_case: Load case to display
        scale: Reaction visualization scale
        figsize: Figure size
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure
    """
    if structure.analysis_status != "success":
        raise ValueError("Structure must be analyzed before plotting reactions")
    
    plotter = StructurePlotter(structure, figsize=figsize)
    plotter.setup_figure(f"Support Reactions - {load_case.name}")
    plotter.plot_reactions(load_case, scale=scale)
    
    # Add reaction summary
    _add_reaction_summary(plotter, structure, load_case)
    
    if save_as:
        plotter.save_plot(save_as)
    
    return plotter.fig


def _add_reaction_summary(plotter: StructurePlotter, structure: Structure, 
                         load_case: LoadCase) -> None:
    """Add reaction summary text box."""
    summary_text = [f"Reaction Summary - {load_case.name}", "-" * 30]
    total_fx = total_fy = total_mz = 0
    
    for node in structure.nodes:
        if not node.is_free:
            reaction = structure.get_node_reaction(node, load_case)
            
            if abs(reaction[0]) > 1e-6 or abs(reaction[1]) > 1e-6 or abs(reaction[2]) > 1e-6:
                summary_text.append(f"{node.label}:")
                if abs(reaction[0]) > 1e-6:
                    summary_text.append(f"  Rx = {reaction[0]:.2f} kN")
                    total_fx += reaction[0]
                if abs(reaction[1]) > 1e-6:
                    summary_text.append(f"  Ry = {reaction[1]:.2f} kN")
                    total_fy += reaction[1]
                if abs(reaction[2]) > 1e-6:
                    summary_text.append(f"  Mz = {reaction[2]:.2f} kN⋅m")
                    total_mz += reaction[2]
    
    summary_text.extend(["-" * 30, "Equilibrium Check:",
                        f"ΣFx = {total_fx:.2f} kN",
                        f"ΣFy = {total_fy:.2f} kN", 
                        f"ΣMz = {total_mz:.2f} kN⋅m"])
    
    # Add text box
    text_str = "\n".join(summary_text)
    plotter.ax.text(0.02, 0.98, text_str, transform=plotter.ax.transAxes,
                   fontsize=9, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))


def plot_element_forces(structure: Structure, load_case: LoadCase, element_idx: int,
                       figsize: Tuple[float, float] = (12, 6),
                       save_as: Optional[str] = None) -> plt.Figure:
    """
    Plot element internal forces (axial, shear, moment).
    
    Args:
        structure: Analyzed structure
        load_case: Load case to display
        element_idx: Index of element to plot
        figsize: Figure size
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure
    """
    if structure.analysis_status != "success":
        raise ValueError("Structure must be analyzed before plotting element forces")
    
    if element_idx >= len(structure.elements):
        raise ValueError(f"Element index {element_idx} out of range")
    
    element = structure.elements[element_idx]
    
    # Get element displacements
    disp_start = structure.get_node_displacement(element.start_node, load_case)
    disp_end = structure.get_node_displacement(element.end_node, load_case)
    element_displacements = np.concatenate([disp_start, disp_end])
    
    # Calculate element forces in local coordinates
    k_local = element.local_stiffness_matrix
    # Transform global displacements to local
    T = element.transformation_matrix
    local_displacements = T.T @ element_displacements
    local_forces = k_local @ local_displacements
    
    # Add equivalent nodal forces from element loads
    for load in getattr(element, 'loads', []):
        if load.load_case == load_case:
            equiv_forces = load.get_equivalent_nodal_forces(element)
            # Transform to local coordinates
            local_equiv_forces = T.T @ equiv_forces
            local_forces += local_equiv_forces
    
    # Extract force components
    # Local forces: [Fx1, Fy1, Mz1, Fx2, Fy2, Mz2]
    axial_start = local_forces[0]
    shear_start = local_forces[1] 
    moment_start = local_forces[2]
    axial_end = -local_forces[3]  # Sign convention
    shear_end = -local_forces[4]
    moment_end = local_forces[5]
    
    # Create force diagrams
    fig, axes = plt.subplots(3, 1, figsize=figsize)
    fig.suptitle(f"Element Forces - {element.label} - {load_case.name}", 
                 fontsize=14, fontweight='bold')
    
    x_coords = [0, element.length]
    
    # Axial force diagram
    axes[0].plot(x_coords, [axial_start, axial_end], 'b-', linewidth=2)
    axes[0].axhline(y=0, color='k', linestyle='-', alpha=0.3)
    axes[0].set_ylabel('Axial Force\n(kN)', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title('Axial Force Diagram')
    
    # Shear force diagram  
    axes[1].plot(x_coords, [shear_start, shear_end], 'r-', linewidth=2)
    axes[1].axhline(y=0, color='k', linestyle='-', alpha=0.3)
    axes[1].set_ylabel('Shear Force\n(kN)', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title('Shear Force Diagram')
    
    # Moment diagram
    axes[2].plot(x_coords, [moment_start, moment_end], 'g-', linewidth=2)
    axes[2].axhline(y=0, color='k', linestyle='-', alpha=0.3)
    axes[2].set_ylabel('Moment\n(kN⋅m)', fontsize=10)
    axes[2].set_xlabel('Distance along element (m)', fontsize=10)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_title('Bending Moment Diagram')
    
    # Add force values as text
    for ax, values, label in zip(axes, 
                                [(axial_start, axial_end), (shear_start, shear_end), (moment_start, moment_end)],
                                ['N', 'V', 'M']):
        ax.text(0, values[0], f'{label}₁={values[0]:.2f}', ha='right', va='bottom')
        ax.text(element.length, values[1], f'{label}₂={values[1]:.2f}', ha='left', va='bottom')
    
    plt.tight_layout()
    
    if save_as:
        fig.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Element forces plot saved as: {save_as}")
    
    return fig


def create_results_comparison(structure: Structure, load_cases: List[LoadCase],
                             node: Node2D, figsize: Tuple[float, float] = (12, 8),
                             save_as: Optional[str] = None) -> plt.Figure:
    """
    Compare results across multiple load cases for a specific node.
    
    Args:
        structure: Analyzed structure
        load_cases: List of load cases to compare
        node: Node to analyze
        figsize: Figure size
        save_as: Filename to save plot (optional)
        
    Returns:
        Matplotlib figure
    """
    if structure.analysis_status != "success":
        raise ValueError("Structure must be analyzed before plotting results")
    
    if node not in structure.nodes:
        raise ValueError("Node not found in structure")
    
    # Collect data
    case_names = [lc.name for lc in load_cases]
    displacements = {'UX': [], 'UY': [], 'RZ': []}
    reactions = {'RX': [], 'RY': [], 'MZ': []} if not node.is_free else None
    
    for load_case in load_cases:
        disp = structure.get_node_displacement(node, load_case)
        displacements['UX'].append(disp[0])
        displacements['UY'].append(disp[1])
        displacements['RZ'].append(disp[2])
        
        if not node.is_free:
            reaction = structure.get_node_reaction(node, load_case)
            reactions['RX'].append(reaction[0])
            reactions['RY'].append(reaction[1]) 
            reactions['MZ'].append(reaction[2])
    
    # Create plots
    n_plots = 2 if not node.is_free else 1
    fig, axes = plt.subplots(n_plots, 1, figsize=figsize)
    if n_plots == 1:
        axes = [axes]
    
    fig.suptitle(f"Results Comparison - Node {node.label}", fontsize=14, fontweight='bold')
    
    # Displacement comparison
    x = np.arange(len(case_names))
    width = 0.25
    
    axes[0].bar(x - width, displacements['UX'], width, label='UX (m)', alpha=0.8)
    axes[0].bar(x, displacements['UY'], width, label='UY (m)', alpha=0.8)
    axes[0].bar(x + width, displacements['RZ'], width, label='RZ (rad)', alpha=0.8)
    
    axes[0].set_xlabel('Load Cases')
    axes[0].set_ylabel('Displacement')
    axes[0].set_title('Displacements')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(case_names, rotation=45, ha='right')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Reaction comparison (if applicable)
    if not node.is_free and reactions:
        axes[1].bar(x - width, reactions['RX'], width, label='RX (kN)', alpha=0.8)
        axes[1].bar(x, reactions['RY'], width, label='RY (kN)', alpha=0.8) 
        axes[1].bar(x + width, reactions['MZ'], width, label='MZ (kN⋅m)', alpha=0.8)
        
        axes[1].set_xlabel('Load Cases')
        axes[1].set_ylabel('Reaction')
        axes[1].set_title('Reactions')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(case_names, rotation=45, ha='right')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_as:
        fig.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Results comparison saved as: {save_as}")
    
    return fig