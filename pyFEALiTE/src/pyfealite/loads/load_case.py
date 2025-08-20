"""Load case management for structural analysis."""

from typing import List, Optional, Dict, Any
from .base import ILoad


class LoadCase:
    """
    Load case container for grouping loads.
    
    Groups related loads together for analysis and combination.
    Common load cases include Dead, Live, Wind, Snow, etc.
    
    Attributes:
        name: Load case name
        description: Load case description
        loads: List of loads in this case
        load_type: Type of loading (DEAD, LIVE, WIND, etc.)
        is_active: Whether load case is active for analysis
    """
    
    def __init__(self, name: str, description: str = "", load_type: str = "GENERAL"):
        """
        Initialize load case.
        
        Args:
            name: Load case name
            description: Load case description
            load_type: Type of loading
        """
        if not name.strip():
            raise ValueError("Load case name cannot be empty")
        
        self.name = name.strip()
        self.description = description
        self.load_type = load_type.upper()
        self.loads: List[ILoad] = []
        self.is_active = True
        self.metadata: Dict[str, Any] = {}
    
    def add_load(self, load: ILoad) -> None:
        """
        Add load to case.
        
        Args:
            load: Load to add
        """
        # Update load's case identifier to match this case
        load.load_case = self.name
        self.loads.append(load)
    
    def remove_load(self, load: ILoad) -> None:
        """
        Remove load from case.
        
        Args:
            load: Load to remove
        """
        if load in self.loads:
            self.loads.remove(load)
    
    def clear_loads(self) -> None:
        """Clear all loads from case."""
        self.loads.clear()
    
    def get_loads_by_type(self, load_type: type) -> List[ILoad]:
        """
        Get loads of specific type.
        
        Args:
            load_type: Type of load to filter
            
        Returns:
            List of loads of specified type
        """
        return [load for load in self.loads if isinstance(load, load_type)]
    
    def get_load_count(self) -> int:
        """Get total number of loads."""
        return len(self.loads)
    
    def get_load_count_by_type(self) -> Dict[str, int]:
        """Get count of loads by type."""
        counts = {}
        for load in self.loads:
            load_type = type(load).__name__
            counts[load_type] = counts.get(load_type, 0) + 1
        return counts
    
    def scale_all_loads(self, factor: float) -> None:
        """
        Scale all loads in the case.
        
        Args:
            factor: Scale factor
        """
        for load in self.loads:
            load.scale(factor)
    
    def copy_loads_to(self, target_case: 'LoadCase', scale_factor: float = 1.0) -> None:
        """
        Copy loads to another case.
        
        Args:
            target_case: Target load case
            scale_factor: Scale factor for copied loads
        """
        for load in self.loads:
            copied_load = load.copy()
            if scale_factor != 1.0:
                copied_load.scale(scale_factor)
            target_case.add_load(copied_load)
    
    def get_case_info(self) -> dict:
        """Get complete case information."""
        return {
            'name': self.name,
            'description': self.description,
            'load_type': self.load_type,
            'is_active': self.is_active,
            'total_loads': len(self.loads),
            'loads_by_type': self.get_load_count_by_type(),
            'metadata': self.metadata
        }
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the load case."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def activate(self) -> None:
        """Activate load case for analysis."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate load case from analysis."""
        self.is_active = False
    
    def __len__(self) -> int:
        """Return number of loads."""
        return len(self.loads)
    
    def __iter__(self):
        """Iterate over loads."""
        return iter(self.loads)
    
    def __str__(self) -> str:
        """String representation."""
        return f"LoadCase({self.name}, {len(self.loads)} loads)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"LoadCase(name='{self.name}', type='{self.load_type}', "
                f"loads={len(self.loads)}, active={self.is_active})")


class LoadCaseManager:
    """
    Manager for load cases.
    
    Handles creation, storage, and management of load cases
    for structural analysis.
    """
    
    def __init__(self):
        """Initialize load case manager."""
        self.load_cases: Dict[str, LoadCase] = {}
        self.default_case_name = "DEFAULT"
    
    def create_load_case(self, name: str, description: str = "", load_type: str = "GENERAL") -> LoadCase:
        """
        Create new load case.
        
        Args:
            name: Load case name
            description: Load case description
            load_type: Type of loading
            
        Returns:
            Created load case
        """
        if name in self.load_cases:
            raise ValueError(f"Load case '{name}' already exists")
        
        load_case = LoadCase(name, description, load_type)
        self.load_cases[name] = load_case
        return load_case
    
    def add_load_case(self, load_case: LoadCase) -> None:
        """
        Add existing load case.
        
        Args:
            load_case: Load case to add
        """
        if load_case.name in self.load_cases:
            raise ValueError(f"Load case '{load_case.name}' already exists")
        
        self.load_cases[load_case.name] = load_case
    
    def get_load_case(self, name: str) -> Optional[LoadCase]:
        """Get load case by name."""
        return self.load_cases.get(name)
    
    def remove_load_case(self, name: str) -> None:
        """Remove load case."""
        if name in self.load_cases:
            del self.load_cases[name]
    
    def list_load_cases(self) -> List[str]:
        """List all load case names."""
        return list(self.load_cases.keys())
    
    def get_active_load_cases(self) -> List[LoadCase]:
        """Get all active load cases."""
        return [case for case in self.load_cases.values() if case.is_active]
    
    def get_load_cases_by_type(self, load_type: str) -> List[LoadCase]:
        """
        Get load cases by type.
        
        Args:
            load_type: Type of loading
            
        Returns:
            List of matching load cases
        """
        return [case for case in self.load_cases.values() if case.load_type == load_type.upper()]
    
    def create_standard_load_cases(self) -> None:
        """Create standard load cases."""
        standard_cases = [
            ("DEAD", "Dead Load", "DEAD"),
            ("LIVE", "Live Load", "LIVE"),
            ("WIND", "Wind Load", "WIND"),
            ("SNOW", "Snow Load", "SNOW"),
            ("SEISMIC", "Seismic Load", "SEISMIC"),
            ("THERMAL", "Temperature Load", "THERMAL")
        ]
        
        for name, description, load_type in standard_cases:
            if name not in self.load_cases:
                self.create_load_case(name, description, load_type)
    
    def get_total_loads(self) -> int:
        """Get total number of loads across all cases."""
        return sum(len(case.loads) for case in self.load_cases.values())
    
    def get_summary(self) -> dict:
        """Get summary of all load cases."""
        summary = {
            'total_cases': len(self.load_cases),
            'active_cases': len(self.get_active_load_cases()),
            'total_loads': self.get_total_loads(),
            'cases': []
        }
        
        for case in self.load_cases.values():
            summary['cases'].append(case.get_case_info())
        
        return summary
    
    def clear_all(self) -> None:
        """Clear all load cases."""
        self.load_cases.clear()
    
    def __len__(self) -> int:
        """Return number of load cases."""
        return len(self.load_cases)
    
    def __iter__(self):
        """Iterate over load cases."""
        return iter(self.load_cases.values())
    
    def __str__(self) -> str:
        """String representation."""
        return f"LoadCaseManager({len(self.load_cases)} cases)"
