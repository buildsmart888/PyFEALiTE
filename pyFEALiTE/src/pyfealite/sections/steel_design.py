"""Steel design utilities and helper functions for AISC sections."""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .aisc_section import AISCSection, STEELPY_AVAILABLE
from ..materials.base import Material


class SteelGrade(Enum):
    """Standard steel grades."""
    A36 = "A36"      # Fy = 36 ksi (248 MPa)
    A572_50 = "A572_50"  # Fy = 50 ksi (345 MPa) 
    A992 = "A992"    # Fy = 50 ksi (345 MPa)
    A588 = "A588"    # Fy = 50 ksi (345 MPa), weathering steel


@dataclass
class SteelProperties:
    """Steel material properties."""
    grade: str
    fy: float  # Yield strength (Pa)
    fu: float  # Ultimate strength (Pa)
    E: float   # Elastic modulus (Pa)
    description: str = ""


class SteelDesignHelper:
    """
    Helper class for steel design with AISC sections.
    
    Provides utilities for:
    - Steel grade management
    - Section selection assistance
    - Design checks and calculations
    - Code compliance verification
    """
    
    # Standard steel properties (SI units)
    STEEL_GRADES = {
        SteelGrade.A36: SteelProperties(
            grade="A36",
            fy=248e6,    # 248 MPa
            fu=400e6,    # 400 MPa  
            E=200e9,     # 200 GPa
            description="General construction steel"
        ),
        SteelGrade.A572_50: SteelProperties(
            grade="A572-50",
            fy=345e6,    # 345 MPa
            fu=450e6,    # 450 MPa
            E=200e9,     # 200 GPa
            description="High-strength low-alloy steel"
        ),
        SteelGrade.A992: SteelProperties(
            grade="A992",
            fy=345e6,    # 345 MPa (minimum)
            fu=450e6,    # 450 MPa (minimum)
            E=200e9,     # 200 GPa
            description="Structural steel for wide-flange shapes"
        ),
        SteelGrade.A588: SteelProperties(
            grade="A588",
            fy=345e6,    # 345 MPa
            fu=485e6,    # 485 MPa
            E=200e9,     # 200 GPa
            description="Weathering steel"
        )
    }
    
    def __init__(self):
        """Initialize steel design helper."""
        self.current_grade = SteelGrade.A992
    
    def get_steel_material(self, grade: SteelGrade, label: str = "") -> Material:
        """
        Get steel material for specified grade.
        
        Args:
            grade: Steel grade
            label: Material label
            
        Returns:
            Material object with steel properties
        """
        from ..materials.isotropic import IsotropicMaterial
        
        props = self.STEEL_GRADES[grade]
        material_label = label or f"Steel {props.grade}"
        
        return IsotropicMaterial(
            elastic_modulus=props.E,
            poisson_ratio=0.3,    # Typical for steel
            density=7850,         # kg/m³
            yield_strength=props.fy,
            ultimate_strength=props.fu,
            label=material_label
        )
    
    def recommend_beam_section(self, 
                             span: float,
                             total_load: float,
                             deflection_limit: float = None,
                             steel_grade: SteelGrade = SteelGrade.A992) -> List[Dict]:
        """
        Recommend beam sections for given loading.
        
        Args:
            span: Beam span (m)
            total_load: Total uniform load (N/m)
            deflection_limit: Maximum deflection (m), defaults to span/240
            steel_grade: Steel grade to use
            
        Returns:
            List of recommended sections with utilization ratios
        """
        if not STEELPY_AVAILABLE:
            return []
        
        # Default deflection limit
        if deflection_limit is None:
            deflection_limit = span / 240  # L/240 for live load
        
        # Calculate required section properties
        max_moment = total_load * span**2 / 8  # Simply supported beam
        steel_props = self.STEEL_GRADES[steel_grade]
        
        # Required section modulus for flexure
        required_sx = max_moment / (0.9 * steel_props.fy)  # LRFD with φ = 0.9
        
        # Required moment of inertia for deflection
        E = steel_props.E
        required_ix = (5 * total_load * span**4) / (384 * E * deflection_limit)
        
        # Convert to imperial units for steelpy search
        required_sx_in3 = required_sx / (0.0254**3)  # m³ to in³
        required_ix_in4 = required_ix / (0.0254**4)  # m⁴ to in⁴
        
        # Search for suitable W sections
        criteria = {
            'Sx': {'min': required_sx_in3 * 1.1},  # 10% margin
            'Ix': {'min': required_ix_in4 * 1.1}   # 10% margin
        }
        
        try:
            filtered_sections = AISCSection.search_sections('W', criteria, sort_by='weight')
            
            recommendations = []
            for name, section in list(filtered_sections.items())[:10]:  # Top 10
                # Calculate utilization ratios
                flex_utilization = (required_sx_in3) / section.Sx
                deflection_utilization = (required_ix_in4) / section.Ix
                max_utilization = max(flex_utilization, deflection_utilization)
                
                recommendations.append({
                    'section_name': name,
                    'weight_lb_ft': section.weight,
                    'area_in2': section.area,
                    'depth_in': section.d,
                    'Sx_in3': section.Sx,
                    'Ix_in4': section.Ix,
                    'flexure_utilization': flex_utilization,
                    'deflection_utilization': deflection_utilization,
                    'max_utilization': max_utilization,
                    'efficiency': 1.0 / max_utilization if max_utilization > 0 else 0
                })
            
            # Sort by efficiency (higher is better)
            recommendations.sort(key=lambda x: x['efficiency'], reverse=True)
            return recommendations
            
        except Exception:
            return []
    
    def recommend_column_section(self,
                               length: float,
                               axial_load: float, 
                               k_factor: float = 1.0,
                               steel_grade: SteelGrade = SteelGrade.A992) -> List[Dict]:
        """
        Recommend column sections for axial loading.
        
        Args:
            length: Column length (m)
            axial_load: Factored axial load (N)
            k_factor: Effective length factor
            steel_grade: Steel grade to use
            
        Returns:
            List of recommended sections
        """
        if not STEELPY_AVAILABLE:
            return []
        
        steel_props = self.STEEL_GRADES[steel_grade]
        
        # Estimate required area (conservative)
        # Assume compression capacity ≈ 0.85 * Fy * Ag for short columns
        required_area = axial_load / (0.85 * 0.9 * steel_props.fy)  # LRFD
        
        # Convert to imperial
        required_area_in2 = required_area / (0.0254**2)
        
        # Search criteria
        criteria = {
            'area': {'min': required_area_in2 * 1.1}  # 10% margin
        }
        
        try:
            # Try W sections first (common for columns)
            filtered_w = AISCSection.search_sections('W', criteria, sort_by='area')
            
            # Also try HSS sections
            filtered_hss = AISCSection.search_sections('HSS_R', criteria, sort_by='area')
            
            recommendations = []
            
            # Process W sections
            for name, section in list(filtered_w.items())[:5]:
                # Calculate slenderness ratio
                effective_length = length * k_factor
                slenderness_x = (effective_length * 39.37) / section.rx  # Convert to inches
                slenderness_y = (effective_length * 39.37) / section.ry
                max_slenderness = max(slenderness_x, slenderness_y)
                
                recommendations.append({
                    'section_name': name,
                    'type': 'W-Shape',
                    'weight_lb_ft': section.weight,
                    'area_in2': section.area,
                    'depth_in': section.d,
                    'width_in': getattr(section, 'bf', 0),
                    'slenderness_x': slenderness_x,
                    'slenderness_y': slenderness_y,
                    'max_slenderness': max_slenderness,
                    'area_utilization': required_area_in2 / section.area
                })
            
            # Process HSS sections
            for name, section in list(filtered_hss.items())[:3]:
                if hasattr(section, 'rx') and hasattr(section, 'ry'):
                    effective_length = length * k_factor
                    slenderness_x = (effective_length * 39.37) / section.rx
                    slenderness_y = (effective_length * 39.37) / section.ry
                    max_slenderness = max(slenderness_x, slenderness_y)
                    
                    recommendations.append({
                        'section_name': name,
                        'type': 'HSS',
                        'weight_lb_ft': section.weight,
                        'area_in2': section.area,
                        'depth_in': getattr(section, 'Ht', 0),
                        'width_in': getattr(section, 'b', 0),
                        'slenderness_x': slenderness_x,
                        'slenderness_y': slenderness_y,
                        'max_slenderness': max_slenderness,
                        'area_utilization': required_area_in2 / section.area
                    })
            
            # Sort by area utilization (closer to 1.0 is better)
            recommendations.sort(key=lambda x: abs(1.0 - x['area_utilization']))
            return recommendations
            
        except Exception:
            return []
    
    def check_beam_deflection(self,
                            section: AISCSection,
                            span: float,
                            load: float,
                            limit_ratio: float = 240) -> Dict:
        """
        Check beam deflection against limits.
        
        Args:
            section: AISC section
            span: Beam span (m)
            load: Service load (N/m)
            limit_ratio: Deflection limit (span/limit_ratio)
            
        Returns:
            Deflection check results
        """
        # Calculate deflection for simply supported beam
        E = section.material.elastic_modulus
        I = section.Iz
        
        max_deflection = (5 * load * span**4) / (384 * E * I)
        deflection_limit = span / limit_ratio
        
        return {
            'max_deflection_mm': max_deflection * 1000,
            'limit_mm': deflection_limit * 1000,
            'ratio': max_deflection / deflection_limit,
            'passes': max_deflection <= deflection_limit,
            'margin_percent': ((deflection_limit - max_deflection) / deflection_limit) * 100
        }
    
    def calculate_beam_capacity(self,
                              section: AISCSection,
                              unbraced_length: float = 0,
                              steel_grade: SteelGrade = SteelGrade.A992) -> Dict:
        """
        Calculate beam flexural capacity (simplified).
        
        Args:
            section: AISC section
            unbraced_length: Unbraced length for lateral-torsional buckling (m)
            steel_grade: Steel grade
            
        Returns:
            Capacity calculation results
        """
        steel_props = self.STEEL_GRADES[steel_grade]
        
        # Plastic moment capacity
        Mp = section.Zx * steel_props.fy
        
        # For simplicity, assume compact section with adequate bracing
        # In practice, need to check compact/noncompact criteria and LTB
        phi_b = 0.9  # Resistance factor for flexure
        Mn = Mp      # Nominal moment capacity (simplified)
        
        design_moment = phi_b * Mn
        
        return {
            'Mp_kNm': Mp / 1000,
            'Mn_kNm': Mn / 1000,
            'phi_Mn_kNm': design_moment / 1000,
            'steel_grade': steel_props.grade,
            'Fy_MPa': steel_props.fy / 1e6,
            'section_name': section.section_name,
            'Zx_m3': section.Zx
        }
    
    def get_design_summary(self, section: AISCSection, steel_grade: SteelGrade) -> Dict:
        """
        Get comprehensive design summary for a section.
        
        Args:
            section: AISC section
            steel_grade: Steel grade
            
        Returns:
            Complete design summary
        """
        steel_props = self.STEEL_GRADES[steel_grade]
        
        return {
            'section_info': section.get_section_info(),
            'steel_properties': {
                'grade': steel_props.grade,
                'fy_MPa': steel_props.fy / 1e6,
                'fu_MPa': steel_props.fu / 1e6,
                'E_GPa': steel_props.E / 1e9,
                'description': steel_props.description
            },
            'design_properties': {
                'Mp_kNm': (section.Zx * steel_props.fy) / 1000,
                'Py_kN': (section.area * steel_props.fy) / 1000,
                'weight_kg_m': section.weight_per_length,
                'classification': self._classify_section(section, steel_props)
            }
        }
    
    def _classify_section(self, section: AISCSection, steel_props: SteelProperties) -> str:
        """Classify section as compact/noncompact/slender (simplified)."""
        # This is a simplified classification
        # Real implementation would check AISC 360 criteria
        
        if hasattr(section.dimensions, 'bf') and hasattr(section.dimensions, 'tf'):
            if section.dimensions.bf and section.dimensions.tf:
                # Flange slenderness ratio
                bf_2tf = section.dimensions.bf / (2 * section.dimensions.tf)
                
                # Simplified compact limit for flange
                E = steel_props.E
                Fy = steel_props.fy
                lambda_p_flange = 0.38 * np.sqrt(E / Fy)
                
                if bf_2tf <= lambda_p_flange:
                    return "Compact (estimated)"
                else:
                    return "Non-compact (estimated)"
        
        return "Classification requires detailed analysis"
    
    @classmethod
    def list_steel_grades(cls) -> List[str]:
        """List available steel grades."""
        return [grade.value for grade in cls.STEEL_GRADES.keys()]
    
    @classmethod
    def get_grade_properties(cls, grade: SteelGrade) -> SteelProperties:
        """Get properties for specified steel grade."""
        return cls.STEEL_GRADES[grade]


def create_steel_material(grade: str = "A992", label: str = "") -> Material:
    """
    Convenience function to create steel material.
    
    Args:
        grade: Steel grade ("A36", "A572_50", "A992", "A588")
        label: Material label
        
    Returns:
        Steel material object
    """
    helper = SteelDesignHelper()
    
    # Convert string to enum
    grade_enum = None
    for g in SteelGrade:
        if g.value.upper() == grade.upper():
            grade_enum = g
            break
    
    if grade_enum is None:
        grade_enum = SteelGrade.A992  # Default
    
    return helper.get_steel_material(grade_enum, label)
