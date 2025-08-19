"""Structure class for finite element analysis."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
import warnings

from .node import Node2D, NodalDegreeOfFreedom
from .element import FrameElement2D
from ..loads.base import LoadCase, LoadCombination
from ..loads.point_load import NodalLoad


class AnalysisStatus:
    """Analysis status enumeration."""
    NOT_ANALYZED = "not_analyzed"
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class Structure:
    """
    Main structure class for 2D finite element analysis.
    
    Attributes:
        name: Structure identifier
        nodes: List of nodes in the structure
        elements: List of elements in the structure
        load_cases: List of load cases to analyze
        tolerance: Numerical tolerance for analysis
    """
    name: str = "Structure"
    nodes: List[Node2D] = field(default_factory=list)
    elements: List[FrameElement2D] = field(default_factory=list)
    load_cases: List[LoadCase] = field(default_factory=list)
    tolerance: float = 1e-12
    
    # Analysis results
    _global_stiffness_matrix: Optional[sparse.csr_matrix] = field(default=None, init=False, repr=False)
    _displacements: Dict[LoadCase, np.ndarray] = field(default_factory=dict, init=False, repr=False)
    _reactions: Dict[LoadCase, Dict[Node2D, np.ndarray]] = field(default_factory=dict, init=False, repr=False)
    _analysis_status: str = field(default=AnalysisStatus.NOT_ANALYZED, init=False, repr=False)
    
    def add_node(self, *nodes: Node2D) -> None:
        """Add nodes to the structure."""
        for node in nodes:
            if node not in self.nodes:
                self.nodes.append(node)
                node.parent_structure = self
    
    def add_element(self, *elements: FrameElement2D, add_nodes: bool = True) -> None:
        """Add elements to the structure."""
        for element in elements:
            if element not in self.elements:
                self.elements.append(element)
                element.parent_structure = self
                
                # Automatically add nodes if requested
                if add_nodes:
                    self.add_node(element.start_node, element.end_node)
    
    def add_load_case(self, *load_cases: LoadCase) -> None:
        """Add load cases to the structure."""
        for load_case in load_cases:
            if load_case not in self.load_cases:
                self.load_cases.append(load_case)
    
    def _assign_dof_numbers(self) -> int:
        """
        Assign global DOF numbers to nodes.
        Free DOFs get numbers 0 to n_free-1.
        Restrained DOFs get numbers n_free to n_total-1.
        
        Returns:
            Number of free DOFs
        """
        # Reset all coordinate numbers
        for node in self.nodes:
            node.coord_numbers = [0, 0, 0]
        
        free_dof_count = 0
        restrained_dof_count = 0
        
        # Count DOFs
        for node in self.nodes:
            for i, is_restrained in enumerate(node.restraints):
                if not is_restrained:
                    free_dof_count += 1
                else:
                    restrained_dof_count += 1
        
        # Assign numbers: free DOFs first, then restrained
        free_counter = 0
        restrained_counter = free_dof_count
        
        for node in self.nodes:
            for i, is_restrained in enumerate(node.restraints):
                if not is_restrained:
                    node.coord_numbers[i] = free_counter
                    free_counter += 1
                else:
                    node.coord_numbers[i] = restrained_counter
                    restrained_counter += 1
        
        return free_dof_count
    
    def _assemble_global_stiffness_matrix(self, n_free_dofs: int) -> sparse.csr_matrix:
        """
        Assemble global stiffness matrix.
        
        Args:
            n_free_dofs: Number of free degrees of freedom
            
        Returns:
            Global stiffness matrix for free DOFs only
        """
        total_dofs = len(self.nodes) * 3
        
        # Use COO format for efficient assembly
        row_indices = []
        col_indices = []
        data = []
        
        for element in self.elements:
            # Get element DOF numbers
            dof_numbers = element.get_dof_numbers()
            
            # Get element global stiffness matrix
            k_global = element.global_stiffness_matrix
            
            # Add to global matrix
            for i in range(6):
                for j in range(6):
                    if abs(k_global[i, j]) > self.tolerance:
                        global_i = dof_numbers[i]
                        global_j = dof_numbers[j]
                        
                        # Only include free DOFs in the system matrix
                        if global_i < n_free_dofs and global_j < n_free_dofs:
                            row_indices.append(global_i)
                            col_indices.append(global_j)
                            data.append(k_global[i, j])
        
        # Create sparse matrix
        K_global = sparse.coo_matrix(
            (data, (row_indices, col_indices)),
            shape=(n_free_dofs, n_free_dofs)
        )
        
        return K_global.tocsr()
    
    def _assemble_load_vector(self, load_case: LoadCase, n_free_dofs: int) -> np.ndarray:
        """
        Assemble global load vector for a load case.
        
        Args:
            load_case: Load case to process
            n_free_dofs: Number of free DOFs
            
        Returns:
            Global load vector for free DOFs
        """
        F_global = np.zeros(n_free_dofs)
        
        # Process element loads
        for element in self.elements:
            element_loads = [load for load in getattr(element, 'loads', []) 
                           if load.load_case == load_case]
            
            for load in element_loads:
                # Get equivalent nodal forces
                equiv_forces = load.get_equivalent_nodal_forces(element)
                
                # Get element DOF numbers
                dof_numbers = element.get_dof_numbers()
                
                # Add to global load vector
                for i, force in enumerate(equiv_forces):
                    global_dof = dof_numbers[i]
                    if global_dof < n_free_dofs:  # Only free DOFs
                        F_global[global_dof] += force
        
        # Process nodal loads
        for node in self.nodes:
            nodal_loads = [load for load in getattr(node, 'loads', [])
                          if isinstance(load, NodalLoad) and load.load_case == load_case]
            
            for load in nodal_loads:
                force_vector = load.get_force_vector()
                
                for i, force in enumerate(force_vector):
                    global_dof = node.coord_numbers[i]
                    if global_dof < n_free_dofs:  # Only free DOFs
                        F_global[global_dof] += force
        
        return F_global
    
    def _calculate_reactions(self, load_case: LoadCase, displacements: np.ndarray, 
                           n_free_dofs: int) -> Dict[Node2D, np.ndarray]:
        """Calculate support reactions for a load case."""
        reactions = {}
        
        # Extend displacement vector to include restrained DOFs (zero displacement)
        total_dofs = len(self.nodes) * 3
        full_displacements = np.zeros(total_dofs)
        full_displacements[:n_free_dofs] = displacements
        
        for node in self.nodes:
            if not node.is_free:  # Node has some restraints
                reaction = np.zeros(3)
                
                # Calculate reaction from connected elements
                connected_elements = [e for e in self.elements 
                                    if node in [e.start_node, e.end_node]]
                
                for element in connected_elements:
                    # Get element displacements
                    element_dofs = element.get_dof_numbers()
                    element_displacements = full_displacements[element_dofs]
                    
                    # Calculate element forces
                    k_global = element.global_stiffness_matrix
                    element_forces = k_global @ element_displacements
                    
                    # Add equivalent nodal loads
                    element_loads = [load for load in getattr(element, 'loads', [])
                                   if load.load_case == load_case]
                    for load in element_loads:
                        equiv_forces = load.get_equivalent_nodal_forces(element)
                        element_forces += equiv_forces
                    
                    # Extract forces for this node
                    if node == element.start_node:
                        node_forces = element_forces[:3]
                    else:  # end_node
                        node_forces = element_forces[3:6]
                    
                    reaction += node_forces
                
                # Subtract applied nodal loads
                nodal_loads = [load for load in getattr(node, 'loads', [])
                              if isinstance(load, NodalLoad) and load.load_case == load_case]
                for load in nodal_loads:
                    reaction -= load.get_force_vector()
                
                # Only keep reactions for restrained DOFs
                for i, is_restrained in enumerate(node.restraints):
                    if not is_restrained:
                        reaction[i] = 0.0
                
                reactions[node] = reaction
        
        return reactions
    
    def _solve_load_combinations(self, load_combinations: List[LoadCombination], 
                                n_free_dofs: int) -> None:
        """Solve load combinations by superposition."""
        from ..loads.base import LoadCombination
        
        for combination in load_combinations:
            print(f"Solving load combination: {combination.name}")
            
            # Initialize combined results
            combined_displacements = np.zeros(n_free_dofs)
            combined_reactions = {}
            
            # Superpose results from constituent load cases
            for load_case, factor in combination:
                if load_case in self._displacements:
                    # Scale and add displacements
                    combined_displacements += factor * self._displacements[load_case]
                    
                    # Scale and add reactions
                    if load_case in self._reactions:
                        for node, reaction in self._reactions[load_case].items():
                            if node not in combined_reactions:
                                combined_reactions[node] = np.zeros(3)
                            combined_reactions[node] += factor * reaction
            
            # Create a virtual load case for the combination
            combo_load_case = LoadCase(combination.name, description=f"Combination: {combination.name}")
            
            # Store combined results
            self._displacements[combo_load_case] = combined_displacements
            self._reactions[combo_load_case] = combined_reactions
    
    def solve(self, load_cases: Optional[List[LoadCase]] = None, 
              load_combinations: Optional[List[LoadCombination]] = None) -> None:
        """
        Solve the structure for specified load cases and combinations.
        
        Args:
            load_cases: Load cases to solve. If None, solve all load cases.
            load_combinations: Load combinations to solve.
        """
        if not self.nodes:
            raise ValueError("Structure has no nodes")
        if not self.elements:
            raise ValueError("Structure has no elements")
        
        # Use all load cases if none specified
        if load_cases is None:
            load_cases = self.load_cases
        
        if not load_cases:
            raise ValueError("No load cases to solve")
        
        try:
            # Assign DOF numbers
            n_free_dofs = self._assign_dof_numbers()
            
            if n_free_dofs == 0:
                warnings.warn("Structure is fully restrained (no free DOFs)")
                self._analysis_status = AnalysisStatus.WARNING
                return
            
            # Assemble global stiffness matrix
            print(f"Assembling global stiffness matrix ({n_free_dofs} DOFs)...")
            self._global_stiffness_matrix = self._assemble_global_stiffness_matrix(n_free_dofs)
            
            # Check for singularity
            if self._global_stiffness_matrix.nnz == 0:
                raise ValueError("Global stiffness matrix is singular (no stiffness)")
            
            # Solve each load case
            for load_case in load_cases:
                print(f"Solving load case: {load_case.name}")
                
                # Assemble load vector
                F_global = self._assemble_load_vector(load_case, n_free_dofs)
                
                if np.allclose(F_global, 0):
                    warnings.warn(f"Load case '{load_case.name}' has zero loads")
                    self._displacements[load_case] = np.zeros(n_free_dofs)
                    self._reactions[load_case] = {}
                    continue
                
                # Solve system: K * u = F
                displacements = spsolve(self._global_stiffness_matrix, F_global)
                
                # Store results
                self._displacements[load_case] = displacements
                self._reactions[load_case] = self._calculate_reactions(
                    load_case, displacements, n_free_dofs
                )
            
            # Solve load combinations if provided
            if load_combinations:
                self._solve_load_combinations(load_combinations, n_free_dofs)
            
            self._analysis_status = AnalysisStatus.SUCCESS
            print("Analysis completed successfully!")
            
        except Exception as e:
            self._analysis_status = AnalysisStatus.FAILED
            print(f"Analysis failed: {e}")
            raise
    
    def get_node_displacement(self, node: Node2D, load_case: LoadCase) -> np.ndarray:
        """Get displacement vector for a node in a load case."""
        if load_case not in self._displacements:
            raise ValueError(f"Load case '{load_case.name}' not solved")
        
        displacements = self._displacements[load_case]
        node_disp = np.zeros(3)
        
        for i, global_dof in enumerate(node.coord_numbers):
            if global_dof < len(displacements):  # Free DOF
                node_disp[i] = displacements[global_dof]
            # Restrained DOFs remain zero
        
        return node_disp
    
    def get_node_reaction(self, node: Node2D, load_case: LoadCase) -> np.ndarray:
        """Get reaction vector for a node in a load case."""
        if load_case not in self._reactions:
            raise ValueError(f"Load case '{load_case.name}' not solved")
        
        return self._reactions[load_case].get(node, np.zeros(3))
    
    @property
    def analysis_status(self) -> str:
        """Get analysis status."""
        return self._analysis_status
    
    @property
    def n_nodes(self) -> int:
        """Number of nodes."""
        return len(self.nodes)
    
    @property
    def n_elements(self) -> int:
        """Number of elements."""
        return len(self.elements)
    
    @property
    def n_dofs(self) -> int:
        """Total number of DOFs."""
        return len(self.nodes) * 3
    
    @property
    def n_free_dofs(self) -> int:
        """Number of free DOFs."""
        if not self.nodes:
            return 0
        return sum(node.dof_count for node in self.nodes)
    
    def summary(self) -> str:
        """Get structure summary."""
        return (f"Structure '{self.name}': "
                f"{self.n_nodes} nodes, {self.n_elements} elements, "
                f"{self.n_free_dofs}/{self.n_dofs} free DOFs, "
                f"status: {self.analysis_status}")
    
    def __str__(self) -> str:
        return f"Structure('{self.name}', {self.n_nodes} nodes, {self.n_elements} elements)"