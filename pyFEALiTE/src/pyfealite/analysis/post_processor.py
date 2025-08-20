"""Enhanced post-processor for structural analysis results."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt

from ..core.node import Node2D
from ..core.element import FrameElement2D
from ..core.structure import Structure


class ResultType(Enum):
    """Types of analysis results."""
    DISPLACEMENT = "displacement"
    FORCE = "force"
    STRESS = "stress"
    REACTION = "reaction"
    MOMENT = "moment"


@dataclass
class ElementForces:
    """Element force results."""
    element_id: int
    axial_start: float
    axial_end: float
    shear_start: float
    shear_end: float
    moment_start: float
    moment_end: float
    max_moment: float
    max_moment_location: float  # Position along element where max moment occurs


@dataclass
class NodalResults:
    """Nodal results container."""
    node_id: int
    displacement_x: float
    displacement_y: float
    rotation_z: float
    reaction_x: float = 0.0
    reaction_y: float = 0.0
    reaction_moment: float = 0.0


class EnhancedPostProcessor:
    """
    Enhanced post-processor for structural analysis results.
    
    Provides comprehensive result processing, visualization,
    and reporting capabilities.
    """
    
    def __init__(self, structure: Structure):
        """
        Initialize post-processor.
        
        Args:
            structure: Analyzed structure
        """
        self.structure = structure
        self.results: Dict[str, Any] = {}
        self.nodal_results: Dict[int, NodalResults] = {}
        self.element_forces: Dict[int, ElementForces] = {}
        self.load_case_results: Dict[str, Dict] = {}
    
    def add_analysis_results(self, load_case: str, displacements: np.ndarray,
                            reactions: Optional[np.ndarray] = None,
                            element_forces: Optional[Dict] = None) -> None:
        """
        Add analysis results for a load case.
        
        Args:
            load_case: Load case identifier
            displacements: Global displacement vector
            reactions: Reaction forces vector
            element_forces: Element force results
        """
        # Process nodal results
        nodal_results = self._process_nodal_results(displacements, reactions)
        
        # Process element results
        element_results = self._process_element_results(element_forces or {})
        
        # Store results
        self.load_case_results[load_case] = {
            'nodal_results': nodal_results,
            'element_results': element_results,
            'displacements': displacements,
            'reactions': reactions
        }
    
    def _process_nodal_results(self, displacements: np.ndarray,
                              reactions: Optional[np.ndarray] = None) -> Dict[int, NodalResults]:
        """Process nodal displacement and reaction results."""
        nodal_results = {}
        
        for i, node in enumerate(self.structure.nodes):
            # Extract displacements (3 DOF per node)
            start_idx = i * 3
            disp_x = displacements[start_idx] if start_idx < len(displacements) else 0.0
            disp_y = displacements[start_idx + 1] if start_idx + 1 < len(displacements) else 0.0
            rot_z = displacements[start_idx + 2] if start_idx + 2 < len(displacements) else 0.0
            
            # Extract reactions if available
            react_x = react_y = react_m = 0.0
            if reactions is not None and len(reactions) > start_idx + 2:
                react_x = reactions[start_idx]
                react_y = reactions[start_idx + 1]
                react_m = reactions[start_idx + 2]
            
            nodal_results[node.id] = NodalResults(
                node_id=node.id,
                displacement_x=disp_x,
                displacement_y=disp_y,
                rotation_z=rot_z,
                reaction_x=react_x,
                reaction_y=react_y,
                reaction_moment=react_m
            )
        
        return nodal_results
    
    def _process_element_results(self, element_forces: Dict) -> Dict[int, ElementForces]:
        """Process element force results."""
        processed_forces = {}
        
        for element in self.structure.elements:
            if hasattr(element, 'id') and element.id in element_forces:
                forces = element_forces[element.id]
                
                # Calculate maximum moment and location
                max_moment, max_location = self._calculate_max_moment(forces)
                
                processed_forces[element.id] = ElementForces(
                    element_id=element.id,
                    axial_start=forces.get('axial_start', 0.0),
                    axial_end=forces.get('axial_end', 0.0),
                    shear_start=forces.get('shear_start', 0.0),
                    shear_end=forces.get('shear_end', 0.0),
                    moment_start=forces.get('moment_start', 0.0),
                    moment_end=forces.get('moment_end', 0.0),
                    max_moment=max_moment,
                    max_moment_location=max_location
                )
        
        return processed_forces
    
    def _calculate_max_moment(self, forces: Dict) -> Tuple[float, float]:
        """Calculate maximum moment and its location along element."""
        m_start = forces.get('moment_start', 0.0)
        m_end = forces.get('moment_end', 0.0)
        shear = forces.get('shear_start', 0.0)  # Assuming constant shear
        
        # For linear moment distribution
        if abs(shear) < 1e-10:  # No shear, linear moment
            if abs(m_start) >= abs(m_end):
                return m_start, 0.0
            else:
                return m_end, 1.0
        else:
            # Location of zero shear (maximum moment)
            x_max = -m_start / shear if shear != 0 else 0.0
            x_max = max(0.0, min(1.0, x_max))  # Clamp to element length
            
            # Moment at maximum location
            max_moment = m_start + shear * x_max
            
            return max_moment, x_max
    
    def get_max_displacement(self, load_case: str, direction: str = 'total') -> Tuple[float, int]:
        """
        Get maximum displacement for a load case.
        
        Args:
            load_case: Load case identifier
            direction: 'x', 'y', 'rotation', or 'total'
            
        Returns:
            Tuple of (max_displacement, node_id)
        """
        if load_case not in self.load_case_results:
            return 0.0, -1
        
        nodal_results = self.load_case_results[load_case]['nodal_results']
        max_disp = 0.0
        max_node = -1
        
        for node_id, result in nodal_results.items():
            if direction == 'x':
                disp = abs(result.displacement_x)
            elif direction == 'y':
                disp = abs(result.displacement_y)
            elif direction == 'rotation':
                disp = abs(result.rotation_z)
            else:  # total
                disp = np.sqrt(result.displacement_x**2 + result.displacement_y**2)
            
            if disp > max_disp:
                max_disp = disp
                max_node = node_id
        
        return max_disp, max_node
    
    def get_max_element_force(self, load_case: str, force_type: str = 'moment') -> Tuple[float, int]:
        """
        Get maximum element force for a load case.
        
        Args:
            load_case: Load case identifier
            force_type: 'axial', 'shear', or 'moment'
            
        Returns:
            Tuple of (max_force, element_id)
        """
        if load_case not in self.load_case_results:
            return 0.0, -1
        
        element_results = self.load_case_results[load_case]['element_results']
        max_force = 0.0
        max_element = -1
        
        for element_id, result in element_results.items():
            if force_type == 'axial':
                force = max(abs(result.axial_start), abs(result.axial_end))
            elif force_type == 'shear':
                force = max(abs(result.shear_start), abs(result.shear_end))
            else:  # moment
                force = abs(result.max_moment)
            
            if force > max_force:
                max_force = force
                max_element = element_id
        
        return max_force, max_element
    
    def get_summary_report(self, load_case: str) -> Dict[str, Any]:
        """
        Generate summary report for a load case.
        
        Args:
            load_case: Load case identifier
            
        Returns:
            Summary report dictionary
        """
        if load_case not in self.load_case_results:
            return {}
        
        # Maximum displacements
        max_disp_x, node_x = self.get_max_displacement(load_case, 'x')
        max_disp_y, node_y = self.get_max_displacement(load_case, 'y')
        max_disp_total, node_total = self.get_max_displacement(load_case, 'total')
        max_rotation, node_rot = self.get_max_displacement(load_case, 'rotation')
        
        # Maximum forces
        max_axial, elem_axial = self.get_max_element_force(load_case, 'axial')
        max_shear, elem_shear = self.get_max_element_force(load_case, 'shear')
        max_moment, elem_moment = self.get_max_element_force(load_case, 'moment')
        
        # Total reactions
        total_reactions = self._calculate_total_reactions(load_case)
        
        return {
            'load_case': load_case,
            'max_displacements': {
                'x': {'value': max_disp_x, 'node': node_x},
                'y': {'value': max_disp_y, 'node': node_y},
                'total': {'value': max_disp_total, 'node': node_total},
                'rotation': {'value': max_rotation, 'node': node_rot}
            },
            'max_forces': {
                'axial': {'value': max_axial, 'element': elem_axial},
                'shear': {'value': max_shear, 'element': elem_shear},
                'moment': {'value': max_moment, 'element': elem_moment}
            },
            'total_reactions': total_reactions,
            'structure_info': {
                'nodes': len(self.structure.nodes),
                'elements': len(self.structure.elements)
            }
        }
    
    def _calculate_total_reactions(self, load_case: str) -> Dict[str, float]:
        """Calculate total reaction forces."""
        if load_case not in self.load_case_results:
            return {'fx': 0.0, 'fy': 0.0, 'mz': 0.0}
        
        nodal_results = self.load_case_results[load_case]['nodal_results']
        total_fx = sum(result.reaction_x for result in nodal_results.values())
        total_fy = sum(result.reaction_y for result in nodal_results.values())
        total_mz = sum(result.reaction_moment for result in nodal_results.values())
        
        return {'fx': total_fx, 'fy': total_fy, 'mz': total_mz}
    
    def create_deformation_plot(self, load_case: str, scale_factor: float = 1.0,
                               save_path: Optional[str] = None) -> None:
        """
        Create deformation plot.
        
        Args:
            load_case: Load case to plot
            scale_factor: Displacement scale factor
            save_path: Path to save plot
        """
        if load_case not in self.load_case_results:
            return
        
        nodal_results = self.load_case_results[load_case]['nodal_results']
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot original structure
        for element in self.structure.elements:
            if hasattr(element, 'start_node') and hasattr(element, 'end_node'):
                x_orig = [element.start_node.x, element.end_node.x]
                y_orig = [element.start_node.y, element.end_node.y]
                ax.plot(x_orig, y_orig, 'b-', linewidth=1, alpha=0.5, label='Original' if element == self.structure.elements[0] else "")
        
        # Plot deformed structure
        for element in self.structure.elements:
            if hasattr(element, 'start_node') and hasattr(element, 'end_node'):
                start_result = nodal_results.get(element.start_node.id)
                end_result = nodal_results.get(element.end_node.id)
                
                if start_result and end_result:
                    x_def = [
                        element.start_node.x + start_result.displacement_x * scale_factor,
                        element.end_node.x + end_result.displacement_x * scale_factor
                    ]
                    y_def = [
                        element.start_node.y + start_result.displacement_y * scale_factor,
                        element.end_node.y + end_result.displacement_y * scale_factor
                    ]
                    ax.plot(x_def, y_def, 'r-', linewidth=2, label='Deformed' if element == self.structure.elements[0] else "")
        
        # Plot nodes
        for node in self.structure.nodes:
            ax.plot(node.x, node.y, 'bo', markersize=6)
            result = nodal_results.get(node.id)
            if result:
                x_def = node.x + result.displacement_x * scale_factor
                y_def = node.y + result.displacement_y * scale_factor
                ax.plot(x_def, y_def, 'ro', markersize=6)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Deformed Shape - {load_case} (Scale: {scale_factor})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def create_force_diagram(self, load_case: str, force_type: str = 'moment',
                            save_path: Optional[str] = None) -> None:
        """
        Create force diagram.
        
        Args:
            load_case: Load case to plot
            force_type: 'axial', 'shear', or 'moment'
            save_path: Path to save plot
        """
        if load_case not in self.load_case_results:
            return
        
        element_results = self.load_case_results[load_case]['element_results']
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot structure
        for element in self.structure.elements:
            if hasattr(element, 'start_node') and hasattr(element, 'end_node'):
                x = [element.start_node.x, element.end_node.x]
                y = [element.start_node.y, element.end_node.y]
                ax.plot(x, y, 'k-', linewidth=1)
        
        # Plot force diagrams
        for element in self.structure.elements:
            if hasattr(element, 'id') and element.id in element_results:
                result = element_results[element.id]
                self._plot_element_force_diagram(ax, element, result, force_type)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'{force_type.title()} Diagram - {load_case}')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def _plot_element_force_diagram(self, ax, element, result: ElementForces, force_type: str) -> None:
        """Plot force diagram for a single element."""
        if not hasattr(element, 'start_node') or not hasattr(element, 'end_node'):
            return
        
        # Get element coordinates and direction
        x1, y1 = element.start_node.x, element.start_node.y
        x2, y2 = element.end_node.x, element.end_node.y
        length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        if length < 1e-10:
            return
        
        # Unit vectors
        ux = (x2 - x1) / length
        uy = (y2 - y1) / length
        
        # Perpendicular vectors
        nx = -uy
        ny = ux
        
        # Get force values
        if force_type == 'axial':
            f1 = result.axial_start
            f2 = result.axial_end
        elif force_type == 'shear':
            f1 = result.shear_start
            f2 = result.shear_end
        else:  # moment
            f1 = result.moment_start
            f2 = result.moment_end
        
        # Scale factor for diagram
        max_abs_force = max(abs(f1), abs(f2))
        if max_abs_force > 0:
            scale = length * 0.2 / max_abs_force
        else:
            scale = 0
        
        # Plot diagram
        if force_type in ['axial', 'shear']:
            # Linear distribution
            x_diag = [x1 + f1*scale*nx, x2 + f2*scale*nx]
            y_diag = [y1 + f1*scale*ny, y2 + f2*scale*ny]
            ax.plot([x1, x_diag[0]], [y1, y_diag[0]], 'r-', linewidth=1)
            ax.plot([x2, x_diag[1]], [y2, y_diag[1]], 'r-', linewidth=1)
            ax.plot(x_diag, y_diag, 'r-', linewidth=2)
        else:  # moment
            # Parabolic distribution (simplified as linear for now)
            x_diag = [x1 + f1*scale*nx, x2 + f2*scale*nx]
            y_diag = [y1 + f1*scale*ny, y2 + f2*scale*ny]
            ax.plot([x1, x_diag[0]], [y1, y_diag[0]], 'g-', linewidth=1)
            ax.plot([x2, x_diag[1]], [y2, y_diag[1]], 'g-', linewidth=1)
            ax.plot(x_diag, y_diag, 'g-', linewidth=2)
    
    def export_results_to_csv(self, load_case: str, filename: str) -> None:
        """
        Export results to CSV file.
        
        Args:
            load_case: Load case to export
            filename: Output filename
        """
        if load_case not in self.load_case_results:
            return
        
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Load Case', load_case])
            writer.writerow([])
            
            # Nodal results
            writer.writerow(['NODAL RESULTS'])
            writer.writerow(['Node ID', 'Disp X', 'Disp Y', 'Rotation Z', 'React X', 'React Y', 'React Moment'])
            
            nodal_results = self.load_case_results[load_case]['nodal_results']
            for result in nodal_results.values():
                writer.writerow([
                    result.node_id,
                    f"{result.displacement_x:.6e}",
                    f"{result.displacement_y:.6e}",
                    f"{result.rotation_z:.6e}",
                    f"{result.reaction_x:.6e}",
                    f"{result.reaction_y:.6e}",
                    f"{result.reaction_moment:.6e}"
                ])
            
            writer.writerow([])
            
            # Element results
            writer.writerow(['ELEMENT RESULTS'])
            writer.writerow(['Element ID', 'Axial Start', 'Axial End', 'Shear Start', 'Shear End', 
                           'Moment Start', 'Moment End', 'Max Moment', 'Max Moment Location'])
            
            element_results = self.load_case_results[load_case]['element_results']
            for result in element_results.values():
                writer.writerow([
                    result.element_id,
                    f"{result.axial_start:.6e}",
                    f"{result.axial_end:.6e}",
                    f"{result.shear_start:.6e}",
                    f"{result.shear_end:.6e}",
                    f"{result.moment_start:.6e}",
                    f"{result.moment_end:.6e}",
                    f"{result.max_moment:.6e}",
                    f"{result.max_moment_location:.3f}"
                ])
    
    def list_load_cases(self) -> List[str]:
        """Get list of available load cases."""
        return list(self.load_case_results.keys())
    
    def clear_results(self) -> None:
        """Clear all results."""
        self.load_case_results.clear()
        self.nodal_results.clear()
        self.element_forces.clear()
