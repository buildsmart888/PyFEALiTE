"""Standard load combination utilities."""

from typing import List, Dict
from ..loads.base import LoadCase, LoadCombination, LoadType


def standard_load_combinations(load_cases: List[LoadCase]) -> List[LoadCombination]:
    """
    Generate standard load combinations based on available load cases.
    
    Implements common structural design code combinations:
    - Service combinations (unfactored)
    - Ultimate limit state combinations (factored)
    - Eurocode/ASCE style combinations
    
    Args:
        load_cases: List of available load cases
        
    Returns:
        List of standard load combinations
    """
    combinations = []
    
    # Categorize load cases by type
    dead_cases = [lc for lc in load_cases if lc.load_type == LoadType.DEAD]
    live_cases = [lc for lc in load_cases if lc.load_type == LoadType.LIVE]
    wind_cases = [lc for lc in load_cases if lc.load_type == LoadType.WIND]
    seismic_cases = [lc for lc in load_cases if lc.load_type == LoadType.SEISMIC]
    snow_cases = [lc for lc in load_cases if lc.load_type == LoadType.SNOW]
    
    # Service combinations (unfactored)
    if dead_cases and live_cases:
        service_combo = LoadCombination("Service: D + L")
        for dead_case in dead_cases:
            service_combo.add(dead_case, 1.0)
        for live_case in live_cases:
            service_combo.add(live_case, 1.0)
        combinations.append(service_combo)
    
    # Ultimate limit state combinations
    
    # 1. Dead + Live (basic combination)
    if dead_cases and live_cases:
        uls_basic = LoadCombination("ULS: 1.2D + 1.6L")
        for dead_case in dead_cases:
            uls_basic.add(dead_case, 1.2)
        for live_case in live_cases:
            uls_basic.add(live_case, 1.6)
        combinations.append(uls_basic)
    
    # 2. Dead + Live + Wind
    if dead_cases and live_cases and wind_cases:
        uls_wind = LoadCombination("ULS: 1.2D + L + 1.6W")
        for dead_case in dead_cases:
            uls_wind.add(dead_case, 1.2)
        for live_case in live_cases:
            uls_wind.add(live_case, 1.0)  # Reduced live load with wind
        for wind_case in wind_cases:
            uls_wind.add(wind_case, 1.6)
        combinations.append(uls_wind)
        
        # Alternative wind combination
        uls_wind_alt = LoadCombination("ULS: 1.2D + 0.5L + 1.6W")
        for dead_case in dead_cases:
            uls_wind_alt.add(dead_case, 1.2)
        for live_case in live_cases:
            uls_wind_alt.add(live_case, 0.5)
        for wind_case in wind_cases:
            uls_wind_alt.add(wind_case, 1.6)
        combinations.append(uls_wind_alt)
    
    # 3. Dead + Live + Seismic
    if dead_cases and live_cases and seismic_cases:
        uls_seismic = LoadCombination("ULS: 1.2D + L + E")
        for dead_case in dead_cases:
            uls_seismic.add(dead_case, 1.2)
        for live_case in live_cases:
            uls_seismic.add(live_case, 1.0)
        for seismic_case in seismic_cases:
            uls_seismic.add(seismic_case, 1.0)
        combinations.append(uls_seismic)
    
    # 4. Dead + Snow combinations
    if dead_cases and snow_cases:
        uls_snow = LoadCombination("ULS: 1.2D + 1.6S")
        for dead_case in dead_cases:
            uls_snow.add(dead_case, 1.2)
        for snow_case in snow_cases:
            uls_snow.add(snow_case, 1.6)
        combinations.append(uls_snow)
        
        if live_cases:
            uls_snow_live = LoadCombination("ULS: 1.2D + 0.5L + 1.6S")
            for dead_case in dead_cases:
                uls_snow_live.add(dead_case, 1.2)
            for live_case in live_cases:
                uls_snow_live.add(live_case, 0.5)
            for snow_case in snow_cases:
                uls_snow_live.add(snow_case, 1.6)
            combinations.append(uls_snow_live)
    
    # 5. Wind uplift combinations (if applicable)
    if dead_cases and wind_cases:
        # Check for uplift scenario
        uplift_combo = LoadCombination("ULS: 0.9D + 1.6W (Uplift)")
        for dead_case in dead_cases:
            uplift_combo.add(dead_case, 0.9)  # Reduced dead load for uplift
        for wind_case in wind_cases:
            uplift_combo.add(wind_case, 1.6)
        combinations.append(uplift_combo)
    
    return combinations


def create_custom_combination(name: str, load_case_factors: Dict[LoadCase, float]) -> LoadCombination:
    """
    Create a custom load combination.
    
    Args:
        name: Name of the combination
        load_case_factors: Dictionary mapping load cases to factors
        
    Returns:
        Custom load combination
    """
    combination = LoadCombination(name)
    
    for load_case, factor in load_case_factors.items():
        combination.add(load_case, factor)
    
    return combination


def eurocode_combinations(load_cases: List[LoadCase]) -> List[LoadCombination]:
    """
    Generate Eurocode EN 1990 standard load combinations.
    
    Args:
        load_cases: List of available load cases
        
    Returns:
        List of Eurocode combinations
    """
    combinations = []
    
    # Categorize load cases
    dead_cases = [lc for lc in load_cases if lc.load_type == LoadType.DEAD]
    live_cases = [lc for lc in load_cases if lc.load_type == LoadType.LIVE]
    wind_cases = [lc for lc in load_cases if lc.load_type == LoadType.WIND]
    snow_cases = [lc for lc in load_cases if lc.load_type == LoadType.SNOW]
    
    # SLS Characteristic combination
    if dead_cases and live_cases:
        sls_char = LoadCombination("EC SLS: G + Q")
        for dead_case in dead_cases:
            sls_char.add(dead_case, 1.0)
        for live_case in live_cases:
            sls_char.add(live_case, 1.0)
        combinations.append(sls_char)
    
    # ULS - Persistent and transient design situations
    # EQU: γG,j * Gk,j + γQ,1 * Qk,1 + γQ,i * ψ0,i * Qk,i
    
    # Basic combination: 1.35*G + 1.5*Q
    if dead_cases and live_cases:
        uls_basic = LoadCombination("EC ULS: 1.35G + 1.5Q")
        for dead_case in dead_cases:
            uls_basic.add(dead_case, 1.35)
        for live_case in live_cases:
            uls_basic.add(live_case, 1.5)
        combinations.append(uls_basic)
    
    # Wind as leading action
    if dead_cases and wind_cases:
        uls_wind = LoadCombination("EC ULS: 1.35G + 1.5W + 0.75L")
        for dead_case in dead_cases:
            uls_wind.add(dead_case, 1.35)
        for wind_case in wind_cases:
            uls_wind.add(wind_case, 1.5)
        for live_case in live_cases:
            uls_wind.add(live_case, 0.75)  # ψ0 = 0.5 for imposed loads * 1.5
        combinations.append(uls_wind)
    
    # Snow as leading action
    if dead_cases and snow_cases:
        uls_snow = LoadCombination("EC ULS: 1.35G + 1.5S + 0.75L")
        for dead_case in dead_cases:
            uls_snow.add(dead_case, 1.35)
        for snow_case in snow_cases:
            uls_snow.add(snow_case, 1.5)
        for live_case in live_cases:
            uls_snow.add(live_case, 0.75)
        combinations.append(uls_snow)
    
    return combinations


def asce_combinations(load_cases: List[LoadCase]) -> List[LoadCombination]:
    """
    Generate ASCE 7 standard load combinations.
    
    Args:
        load_cases: List of available load cases
        
    Returns:
        List of ASCE combinations
    """
    combinations = []
    
    # Categorize load cases
    dead_cases = [lc for lc in load_cases if lc.load_type == LoadType.DEAD]
    live_cases = [lc for lc in load_cases if lc.load_type == LoadType.LIVE]
    wind_cases = [lc for lc in load_cases if lc.load_type == LoadType.WIND]
    seismic_cases = [lc for lc in load_cases if lc.load_type == LoadType.SEISMIC]
    snow_cases = [lc for lc in load_cases if lc.load_type == LoadType.SNOW]
    
    # ASCE 7 Load combinations
    asce_combos = [
        # 1. D (Dead load only)
        ("ASCE: D", [(dead_cases, 1.0)]),
        
        # 2. D + L
        ("ASCE: D + L", [(dead_cases, 1.0), (live_cases, 1.0)]),
        
        # 3. D + (Lr or S or R)
        ("ASCE: D + S", [(dead_cases, 1.0), (snow_cases, 1.0)]),
        
        # 4. D + 0.75L + 0.75(Lr or S or R)
        ("ASCE: D + 0.75L + 0.75S", [(dead_cases, 1.0), (live_cases, 0.75), (snow_cases, 0.75)]),
        
        # 5. D + (W or 0.7E)
        ("ASCE: D + W", [(dead_cases, 1.0), (wind_cases, 1.0)]),
        ("ASCE: D + 0.7E", [(dead_cases, 1.0), (seismic_cases, 0.7)]),
        
        # 6. D + 0.75L + 0.75(0.6W) + 0.75(Lr or S or R)
        ("ASCE: D + 0.75L + 0.45W + 0.75S", [(dead_cases, 1.0), (live_cases, 0.75), (wind_cases, 0.45), (snow_cases, 0.75)]),
        
        # 7. 0.6D + W
        ("ASCE: 0.6D + W", [(dead_cases, 0.6), (wind_cases, 1.0)]),
        
        # 8. 0.6D + 0.7E
        ("ASCE: 0.6D + 0.7E", [(dead_cases, 0.6), (seismic_cases, 0.7)]),
        
        # LRFD combinations
        # 1. 1.4D
        ("ASCE LRFD: 1.4D", [(dead_cases, 1.4)]),
        
        # 2. 1.2D + 1.6L + 0.5(Lr or S or R)
        ("ASCE LRFD: 1.2D + 1.6L + 0.5S", [(dead_cases, 1.2), (live_cases, 1.6), (snow_cases, 0.5)]),
        
        # 3. 1.2D + 1.6(Lr or S or R) + (L or 0.5W)
        ("ASCE LRFD: 1.2D + 1.6S + L", [(dead_cases, 1.2), (snow_cases, 1.6), (live_cases, 1.0)]),
        
        # 4. 1.2D + 1.0W + L + 0.5(Lr or S or R)
        ("ASCE LRFD: 1.2D + W + L + 0.5S", [(dead_cases, 1.2), (wind_cases, 1.0), (live_cases, 1.0), (snow_cases, 0.5)]),
        
        # 5. 1.2D + 1.0E + L + 0.2S
        ("ASCE LRFD: 1.2D + E + L + 0.2S", [(dead_cases, 1.2), (seismic_cases, 1.0), (live_cases, 1.0), (snow_cases, 0.2)]),
        
        # 6. 0.9D + 1.0W
        ("ASCE LRFD: 0.9D + W", [(dead_cases, 0.9), (wind_cases, 1.0)]),
        
        # 7. 0.9D + 1.0E
        ("ASCE LRFD: 0.9D + E", [(dead_cases, 0.9), (seismic_cases, 1.0)]),
    ]
    
    # Create combinations that are applicable
    for combo_name, case_groups in asce_combos:
        # Check if all required case types are available
        applicable = True
        for case_list, _ in case_groups:
            if not case_list:  # Empty list means this load type is not available
                applicable = False
                break
        
        if applicable:
            combo = LoadCombination(combo_name)
            for case_list, factor in case_groups:
                for load_case in case_list:
                    combo.add(load_case, factor)
            combinations.append(combo)
    
    return combinations