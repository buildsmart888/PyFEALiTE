"""Support displacement load implementation."""

from typing import Dict, Optional
from dataclasses import dataclass
import numpy as np

from .base import ILoad
from ..core.node import Node2D
from ..core.enums import DOF


@dataclass
class DisplacementValue:
    """Displacement value with direction."""
    dof: DOF
    value: float  # Displacement value (m or rad)
    
    def __post_init__(self):
        """Validate displacement value."""
        if not isinstance(self.dof, DOF):
            raise ValueError("DOF must be a valid degree of freedom")


class SupportDisplacementLoad(ILoad):
    """
    Support displacement (settlement) load.
    
    Applies prescribed displacements to supported nodes.
    Used for settlement analysis, thermal effects, or
    prescribed support movements.
    
    Attributes:
        displacements: Dictionary mapping nodes to displacement values
        load_case: Load case identifier
        label: Load label
    """
    
    def __init__(self, load_case: str, label: str = "Support Displacement"):
        """
        Initialize support displacement load.
        
        Args:
            load_case: Load case identifier
            label: Load label
        """
        super().__init__(load_case, label)
        self.displacements: Dict[Node2D, list[DisplacementValue]] = {}
    
    def add_displacement(self, node: Node2D, dof: DOF, value: float) -> None:
        """
        Add displacement to a node.
        
        Args:
            node: Node to apply displacement
            dof: Degree of freedom (UX, UY, RZ)
            value: Displacement value (m for translation, rad for rotation)
        """
        displacement = DisplacementValue(dof, value)
        
        if node not in self.displacements:
            self.displacements[node] = []
        
        # Check if displacement already exists for this DOF
        for i, existing in enumerate(self.displacements[node]):
            if existing.dof == dof:
                self.displacements[node][i] = displacement
                return
        
        self.displacements[node].append(displacement)
    
    def add_settlement(self, node: Node2D, settlement: float) -> None:
        """
        Add vertical settlement to node.
        
        Args:
            node: Node to apply settlement
            settlement: Settlement value (m, positive down)
        """
        self.add_displacement(node, DOF.UY, -settlement)  # Negative for downward
    
    def add_horizontal_movement(self, node: Node2D, movement: float) -> None:
        """
        Add horizontal movement to node.
        
        Args:
            node: Node to apply movement
            movement: Horizontal movement (m, positive right)
        """
        self.add_displacement(node, DOF.UX, movement)
    
    def add_rotation(self, node: Node2D, rotation: float) -> None:
        """
        Add rotational displacement to node.
        
        Args:
            node: Node to apply rotation
            rotation: Rotation (rad, positive counter-clockwise)
        """
        self.add_displacement(node, DOF.RZ, rotation)
    
    def remove_displacement(self, node: Node2D, dof: Optional[DOF] = None) -> None:
        """
        Remove displacement from node.
        
        Args:
            node: Node to remove displacement from
            dof: Specific DOF to remove (if None, removes all)
        """
        if node not in self.displacements:
            return
        
        if dof is None:
            del self.displacements[node]
        else:
            self.displacements[node] = [
                d for d in self.displacements[node] if d.dof != dof
            ]
            if not self.displacements[node]:
                del self.displacements[node]
    
    def get_displacement_vector(self, nodes: list[Node2D]) -> np.ndarray:
        """
        Get displacement vector for analysis.
        
        Args:
            nodes: List of all nodes in structure
            
        Returns:
            Displacement vector matching global DOF numbering
        """
        n_dofs = len(nodes) * 3  # 3 DOFs per node
        displacement_vector = np.zeros(n_dofs)
        
        for node, displacements in self.displacements.items():
            if node not in nodes:
                continue
                
            node_index = nodes.index(node)
            base_dof = node_index * 3
            
            for displacement in displacements:
                dof_index = base_dof + displacement.dof.value
                displacement_vector[dof_index] = displacement.value
        
        return displacement_vector
    
    def get_affected_nodes(self) -> list[Node2D]:
        """Get list of nodes with prescribed displacements."""
        return list(self.displacements.keys())
    
    def get_node_displacements(self, node: Node2D) -> list[DisplacementValue]:
        """
        Get all displacements for a specific node.
        
        Args:
            node: Node to query
            
        Returns:
            List of displacement values for the node
        """
        return self.displacements.get(node, [])
    
    def has_displacement(self, node: Node2D, dof: DOF) -> bool:
        """
        Check if node has displacement in specific DOF.
        
        Args:
            node: Node to check
            dof: Degree of freedom to check
            
        Returns:
            True if displacement exists
        """
        if node not in self.displacements:
            return False
        
        return any(d.dof == dof for d in self.displacements[node])
    
    def get_displacement_value(self, node: Node2D, dof: DOF) -> Optional[float]:
        """
        Get displacement value for specific node and DOF.
        
        Args:
            node: Node to query
            dof: Degree of freedom
            
        Returns:
            Displacement value or None if not found
        """
        if node not in self.displacements:
            return None
        
        for displacement in self.displacements[node]:
            if displacement.dof == dof:
                return displacement.value
        
        return None
    
    def get_load_info(self) -> dict:
        """Get complete load information."""
        info = {
            'type': 'Support Displacement Load',
            'load_case': self.load_case,
            'label': self.label,
            'total_nodes': len(self.displacements),
            'displacements': []
        }
        
        for node, displacements in self.displacements.items():
            node_info = {
                'node_id': node.id,
                'node_coords': [node.x, node.y],
                'displacements': []
            }
            
            for displacement in displacements:
                node_info['displacements'].append({
                    'dof': displacement.dof.name,
                    'value': displacement.value,
                    'units': 'm' if displacement.dof in [DOF.UX, DOF.UY] else 'rad'
                })
            
            info['displacements'].append(node_info)
        
        return info
    
    def scale(self, factor: float) -> None:
        """
        Scale all displacement values.
        
        Args:
            factor: Scale factor
        """
        for node_displacements in self.displacements.values():
            for displacement in node_displacements:
                displacement.value *= factor
    
    def copy(self) -> 'SupportDisplacementLoad':
        """Create a copy of the load."""
        new_load = SupportDisplacementLoad(self.load_case, self.label)
        
        for node, displacements in self.displacements.items():
            for displacement in displacements:
                new_load.add_displacement(node, displacement.dof, displacement.value)
        
        return new_load
    
    @classmethod
    def create_uniform_settlement(cls, nodes: list[Node2D], settlement: float,
                                 load_case: str, label: str = "Uniform Settlement") -> 'SupportDisplacementLoad':
        """
        Create uniform settlement for multiple nodes.
        
        Args:
            nodes: Nodes to apply settlement
            settlement: Settlement value (m, positive down)
            load_case: Load case identifier
            label: Load label
        """
        load = cls(load_case, label)
        
        for node in nodes:
            load.add_settlement(node, settlement)
        
        return load
    
    @classmethod
    def create_differential_settlement(cls, settlement_map: Dict[Node2D, float],
                                     load_case: str, label: str = "Differential Settlement") -> 'SupportDisplacementLoad':
        """
        Create differential settlement for nodes.
        
        Args:
            settlement_map: Dictionary mapping nodes to settlement values
            load_case: Load case identifier
            label: Load label
        """
        load = cls(load_case, label)
        
        for node, settlement in settlement_map.items():
            load.add_settlement(node, settlement)
        
        return load
    
    def __str__(self) -> str:
        """String representation."""
        return f"SupportDisplacementLoad({self.label}, {len(self.displacements)} nodes)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"SupportDisplacementLoad(load_case='{self.load_case}', "
                f"label='{self.label}', nodes={len(self.displacements)})")
