"""Load combination system for structural analysis."""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import numpy as np

from .base import ILoad
from .load_case import LoadCase


@dataclass
class LoadCombinationFactor:
    """Load combination factor with case reference."""
    load_case: str
    factor: float
    
    def __post_init__(self):
        """Validate combination factor."""
        if not isinstance(self.load_case, str) or not self.load_case.strip():
            raise ValueError("Load case must be a non-empty string")


class LoadCombination:
    """
    Load combination for structural analysis.
    
    Combines multiple load cases with factors according to
    design codes (LRFD, ASD, etc.).
    
    Attributes:
        name: Combination name
        description: Combination description
        factors: List of load case factors
        combination_type: Type of combination (LRFD, ASD, etc.)
    """
    
    def __init__(self, name: str, description: str = "", combination_type: str = "LRFD"):
        """
        Initialize load combination.
        
        Args:
            name: Combination name
            description: Combination description  
            combination_type: Type of combination
        """
        if not name.strip():
            raise ValueError("Combination name cannot be empty")
        
        self.name = name.strip()
        self.description = description
        self.combination_type = combination_type
        self.factors: List[LoadCombinationFactor] = []
    
    def add_load_case(self, load_case: str, factor: float) -> None:
        """
        Add load case with factor.
        
        Args:
            load_case: Load case identifier
            factor: Load factor
        """
        # Check if load case already exists
        for i, existing in enumerate(self.factors):
            if existing.load_case == load_case:
                self.factors[i].factor = factor
                return
        
        self.factors.append(LoadCombinationFactor(load_case, factor))
    
    def remove_load_case(self, load_case: str) -> None:
        """
        Remove load case from combination.
        
        Args:
            load_case: Load case to remove
        """
        self.factors = [f for f in self.factors if f.load_case != load_case]
    
    def get_factor(self, load_case: str) -> Optional[float]:
        """
        Get factor for load case.
        
        Args:
            load_case: Load case identifier
            
        Returns:
            Load factor or None if not found
        """
        for factor in self.factors:
            if factor.load_case == load_case:
                return factor.factor
        return None
    
    def get_load_cases(self) -> List[str]:
        """Get list of load cases in combination."""
        return [f.load_case for f in self.factors]
    
    def get_combination_info(self) -> dict:
        """Get combination information."""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.combination_type,
            'factors': [
                {'load_case': f.load_case, 'factor': f.factor}
                for f in self.factors
            ]
        }
    
    def is_empty(self) -> bool:
        """Check if combination is empty."""
        return len(self.factors) == 0
    
    def __str__(self) -> str:
        """String representation."""
        factor_strs = [f"{f.factor:.2f}*{f.load_case}" for f in self.factors]
        return f"{self.name}: {' + '.join(factor_strs)}"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"LoadCombination(name='{self.name}', factors={len(self.factors)})"


class LoadCombinationManager:
    """
    Manager for load combinations.
    
    Handles creation, storage, and application of load combinations
    for structural analysis.
    """
    
    def __init__(self):
        """Initialize combination manager."""
        self.combinations: Dict[str, LoadCombination] = {}
        self.load_cases: Dict[str, LoadCase] = {}
    
    def add_load_case(self, load_case: LoadCase) -> None:
        """
        Add load case for combinations.
        
        Args:
            load_case: Load case to add
        """
        self.load_cases[load_case.name] = load_case
    
    def add_combination(self, combination: LoadCombination) -> None:
        """
        Add load combination.
        
        Args:
            combination: Load combination to add
        """
        # Validate that all referenced load cases exist
        for factor in combination.factors:
            if factor.load_case not in self.load_cases:
                raise ValueError(f"Load case '{factor.load_case}' not found")
        
        self.combinations[combination.name] = combination
    
    def create_combination(self, name: str, factors: Dict[str, float],
                          description: str = "", combination_type: str = "LRFD") -> LoadCombination:
        """
        Create and add load combination.
        
        Args:
            name: Combination name
            factors: Dictionary of load case names to factors
            description: Combination description
            combination_type: Type of combination
            
        Returns:
            Created combination
        """
        combination = LoadCombination(name, description, combination_type)
        
        for load_case, factor in factors.items():
            if load_case not in self.load_cases:
                raise ValueError(f"Load case '{load_case}' not found")
            combination.add_load_case(load_case, factor)
        
        self.combinations[name] = combination
        return combination
    
    def get_combination(self, name: str) -> Optional[LoadCombination]:
        """Get combination by name."""
        return self.combinations.get(name)
    
    def remove_combination(self, name: str) -> None:
        """Remove combination."""
        if name in self.combinations:
            del self.combinations[name]
    
    def list_combinations(self) -> List[str]:
        """List all combination names."""
        return list(self.combinations.keys())
    
    def list_load_cases(self) -> List[str]:
        """List all load case names."""
        return list(self.load_cases.keys())
    
    def get_combined_loads(self, combination_name: str) -> List[ILoad]:
        """
        Get combined loads for a combination.
        
        Args:
            combination_name: Name of combination
            
        Returns:
            List of scaled loads
        """
        if combination_name not in self.combinations:
            raise ValueError(f"Combination '{combination_name}' not found")
        
        combination = self.combinations[combination_name]
        combined_loads = []
        
        for factor_info in combination.factors:
            load_case_name = factor_info.load_case
            factor = factor_info.factor
            
            if load_case_name not in self.load_cases:
                continue
            
            load_case = self.load_cases[load_case_name]
            
            # Scale loads in the load case
            for load in load_case.loads:
                scaled_load = load.copy()
                scaled_load.scale(factor)
                scaled_load.load_case = combination_name  # Update load case
                combined_loads.append(scaled_load)
        
        return combined_loads
    
    def create_standard_combinations(self) -> None:
        """Create standard LRFD combinations."""
        standard_combinations = [
            # Basic combinations
            ("D", {"DEAD": 1.0}, "Dead load only"),
            ("L", {"LIVE": 1.0}, "Live load only"),
            ("W", {"WIND": 1.0}, "Wind load only"),
            ("S", {"SNOW": 1.0}, "Snow load only"),
            
            # LRFD combinations
            ("1.4D", {"DEAD": 1.4}, "1.4D"),
            ("1.2D+1.6L", {"DEAD": 1.2, "LIVE": 1.6}, "1.2D + 1.6L"),
            ("1.2D+1.0L+1.0W", {"DEAD": 1.2, "LIVE": 1.0, "WIND": 1.0}, "1.2D + 1.0L + 1.0W"),
            ("1.2D+1.6S", {"DEAD": 1.2, "SNOW": 1.6}, "1.2D + 1.6S"),
            ("0.9D+1.0W", {"DEAD": 0.9, "WIND": 1.0}, "0.9D + 1.0W"),
        ]
        
        for name, factors, description in standard_combinations:
            # Only create if all referenced load cases exist
            if all(lc in self.load_cases for lc in factors.keys()):
                try:
                    self.create_combination(name, factors, description, "LRFD")
                except ValueError:
                    # Skip if load case doesn't exist
                    pass
    
    def create_asd_combinations(self) -> None:
        """Create standard ASD combinations."""
        asd_combinations = [
            ("D", {"DEAD": 1.0}, "Dead load only"),
            ("D+L", {"DEAD": 1.0, "LIVE": 1.0}, "D + L"),
            ("D+0.75L+0.75W", {"DEAD": 1.0, "LIVE": 0.75, "WIND": 0.75}, "D + 0.75L + 0.75W"),
            ("D+0.75L+0.75S", {"DEAD": 1.0, "LIVE": 0.75, "SNOW": 0.75}, "D + 0.75L + 0.75S"),
            ("D+0.6W", {"DEAD": 1.0, "WIND": 0.6}, "D + 0.6W"),
            ("0.6D+0.6W", {"DEAD": 0.6, "WIND": 0.6}, "0.6D + 0.6W"),
        ]
        
        for name, factors, description in asd_combinations:
            # Only create if all referenced load cases exist
            if all(lc in self.load_cases for lc in factors.keys()):
                try:
                    self.create_combination(name, factors, description, "ASD")
                except ValueError:
                    # Skip if load case doesn't exist
                    pass
    
    def get_envelope_results(self, combinations: List[str]) -> dict:
        """
        Get envelope (max/min) results from multiple combinations.
        
        Args:
            combinations: List of combination names
            
        Returns:
            Dictionary with envelope information
        """
        envelope = {
            'combinations': combinations,
            'max_combination': {},
            'min_combination': {},
            'governing_combinations': {}
        }
        
        # This would be implemented with actual analysis results
        # For now, return structure for future implementation
        return envelope
    
    def validate_combinations(self) -> List[str]:
        """
        Validate all combinations.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        for name, combination in self.combinations.items():
            # Check if all load cases exist
            for factor in combination.factors:
                if factor.load_case not in self.load_cases:
                    errors.append(f"Combination '{name}': Load case '{factor.load_case}' not found")
            
            # Check if combination is empty
            if combination.is_empty():
                errors.append(f"Combination '{name}' is empty")
        
        return errors
    
    def __str__(self) -> str:
        """String representation."""
        return f"LoadCombinationManager({len(self.combinations)} combinations, {len(self.load_cases)} load cases)"
