"""Export functionality for PyFEALiTE structures and results."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import numpy as np
import warnings

from ..core.structure import Structure
from ..core.node import Node2D, NodalDegreeOfFreedom
from ..core.element import FrameElement2D
from ..loads.base import LoadCase, LoadCombination
from ..materials.isotropic import IsotropicMaterial
from ..sections.base import CrossSection

try:
    import ezdxf
    DXF_AVAILABLE = True
except ImportError:
    DXF_AVAILABLE = False


class ExportManager:
    """Manager class for exporting PyFEALiTE data to various formats."""
    
    def __init__(self, structure: Structure):
        """Initialize export manager with a structure."""
        self.structure = structure
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert structure to dictionary representation."""
        data = {
            "structure": {
                "name": self.structure.name,
                "analysis_status": self.structure.analysis_status,
                "n_nodes": self.structure.n_nodes,
                "n_elements": self.structure.n_elements,
                "n_dofs": self.structure.n_dofs,
                "n_free_dofs": self.structure.n_free_dofs
            },
            "nodes": [],
            "elements": [],
            "materials": [],
            "cross_sections": [],
            "load_cases": [],
            "results": {}
        }
        
        # Export nodes
        for i, node in enumerate(self.structure.nodes):
            node_data = {
                "id": i,
                "label": node.label,
                "x": float(node.x),
                "y": float(node.y),
                "restraints": {
                    "UX": node.restraints[0],
                    "UY": node.restraints[1], 
                    "RZ": node.restraints[2] if len(node.restraints) > 2 else False
                },
                "coord_numbers": node.coord_numbers,
                "is_free": node.is_free,
                "dof_count": node.dof_count
            }
            data["nodes"].append(node_data)
        
        # Track unique materials and sections
        materials_dict = {}
        sections_dict = {}
        
        # Export elements
        for i, element in enumerate(self.structure.elements):
            # Track material
            material_id = id(element.cross_section.material)
            if material_id not in materials_dict:
                materials_dict[material_id] = len(materials_dict)
            
            # Track cross-section
            section_id = id(element.cross_section)
            if section_id not in sections_dict:
                sections_dict[section_id] = len(sections_dict)
            
            element_data = {
                "id": i,
                "label": element.label,
                "start_node": self.structure.nodes.index(element.start_node),
                "end_node": self.structure.nodes.index(element.end_node),
                "cross_section_id": sections_dict[section_id],
                "length": float(element.length),
                "angle": float(element.angle)
            }
            
            # Add end releases if available
            if hasattr(element, 'start_releases') and hasattr(element, 'end_releases'):
                element_data["end_releases"] = {
                    "start_releases": [bool(r) for r in element.start_releases],
                    "end_releases": [bool(r) for r in element.end_releases]
                }
            data["elements"].append(element_data)
        
        # Export materials
        material_id_map = {v: k for k, v in materials_dict.items()}
        for mat_idx in range(len(materials_dict)):
            mat_id = material_id_map[mat_idx]
            material = None
            # Find the material object
            for element in self.structure.elements:
                if id(element.cross_section.material) == mat_id:
                    material = element.cross_section.material
                    break
            
            if material:
                mat_data = {
                    "id": mat_idx,
                    "label": material.label,
                    "type": material.__class__.__name__,
                    "E": float(material.E),
                    "G": float(material.G) if hasattr(material, 'G') else None,
                    "nu": float(material.nu) if hasattr(material, 'nu') else None,
                    "density": float(material.density_value) if hasattr(material, 'density_value') else None
                }
                data["materials"].append(mat_data)
        
        # Export cross-sections
        section_id_map = {v: k for k, v in sections_dict.items()}
        for sec_idx in range(len(sections_dict)):
            sec_id = section_id_map[sec_idx]
            section = None
            # Find the section object
            for element in self.structure.elements:
                if id(element.cross_section) == sec_id:
                    section = element.cross_section
                    break
            
            if section:
                sec_data = {
                    "id": sec_idx,
                    "label": section.label,
                    "type": section.__class__.__name__,
                    "material_id": materials_dict[id(section.material)],
                    "A": float(section.A),
                    "Iz": float(section.Iz)
                }
                
                # Add specific properties based on section type
                if hasattr(section, 'width'):
                    sec_data["width"] = float(section.width)
                if hasattr(section, 'height'):
                    sec_data["height"] = float(section.height)
                if hasattr(section, 'diameter'):
                    sec_data["diameter"] = float(section.diameter)
                
                data["cross_sections"].append(sec_data)
        
        # Export load cases
        for i, load_case in enumerate(self.structure.load_cases):
            lc_data = {
                "id": i,
                "name": load_case.name,
                "load_type": load_case.load_type.value,
                "factor": float(load_case.factor),
                "description": load_case.description
            }
            data["load_cases"].append(lc_data)
        
        # Export results if available
        if self.structure.analysis_status == "success":
            data["results"] = self._export_results()
        
        return data
    
    def _export_results(self) -> Dict[str, Any]:
        """Export analysis results."""
        results = {}
        
        for load_case in self.structure.load_cases:
            lc_results = {
                "displacements": [],
                "reactions": []
            }
            
            # Node displacements
            for i, node in enumerate(self.structure.nodes):
                disp = self.structure.get_node_displacement(node, load_case)
                lc_results["displacements"].append({
                    "node_id": i,
                    "UX": float(disp[0]),
                    "UY": float(disp[1]),
                    "RZ": float(disp[2])
                })
            
            # Support reactions
            for i, node in enumerate(self.structure.nodes):
                if not node.is_free:
                    reaction = self.structure.get_node_reaction(node, load_case)
                    lc_results["reactions"].append({
                        "node_id": i,
                        "RX": float(reaction[0]),
                        "RY": float(reaction[1]),
                        "MZ": float(reaction[2])
                    })
            
            results[load_case.name] = lc_results
        
        return results
    
    def to_json(self, filepath: Union[str, Path], indent: int = 2) -> None:
        """Export structure to JSON file."""
        filepath = Path(filepath)
        
        # Custom encoder for numpy types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        data = self.to_dict()
        data["export_info"] = {
            "exporter": "PyFEALiTE",
            "version": "0.1.0",
            "format": "json"
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, cls=NumpyEncoder)
        
        print(f"Structure exported to JSON: {filepath}")
    
    def to_csv(self, directory: Union[str, Path]) -> None:
        """Export structure to multiple CSV files."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        # Export nodes
        with open(directory / "nodes.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Label", "X", "Y", "UX_Restrained", "UY_Restrained", "RZ_Restrained"])
            
            for i, node in enumerate(self.structure.nodes):
                writer.writerow([
                    i, node.label, node.x, node.y,
                    node.restraints[0], node.restraints[1],
                    node.restraints[2] if len(node.restraints) > 2 else False
                ])
        
        # Export elements
        with open(directory / "elements.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Label", "Start_Node", "End_Node", "Length", "Angle", "Cross_Section"])
            
            for i, element in enumerate(self.structure.elements):
                writer.writerow([
                    i, element.label, 
                    self.structure.nodes.index(element.start_node),
                    self.structure.nodes.index(element.end_node),
                    element.length, element.angle,
                    element.cross_section.label
                ])
        
        # Export materials
        materials = {}
        for element in self.structure.elements:
            materials[element.cross_section.material.label] = element.cross_section.material
        
        with open(directory / "materials.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Label", "Type", "E", "G", "nu", "Density"])
            
            for label, material in materials.items():
                writer.writerow([
                    label, material.__class__.__name__, material.E,
                    getattr(material, 'G', ''), getattr(material, 'nu', ''),
                    getattr(material, 'density_value', '')
                ])
        
        # Export results if available
        if self.structure.analysis_status == "success":
            for load_case in self.structure.load_cases:
                # Displacements
                filename = f"displacements_{load_case.name.replace(' ', '_')}.csv"
                with open(directory / filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Node_ID", "Node_Label", "UX", "UY", "RZ"])
                    
                    for i, node in enumerate(self.structure.nodes):
                        disp = self.structure.get_node_displacement(node, load_case)
                        writer.writerow([i, node.label, disp[0], disp[1], disp[2]])
                
                # Reactions
                filename = f"reactions_{load_case.name.replace(' ', '_')}.csv"
                with open(directory / filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Node_ID", "Node_Label", "RX", "RY", "MZ"])
                    
                    for i, node in enumerate(self.structure.nodes):
                        if not node.is_free:
                            reaction = self.structure.get_node_reaction(node, load_case)
                            writer.writerow([i, node.label, reaction[0], reaction[1], reaction[2]])
        
        print(f"Structure exported to CSV files in: {directory}")
    
    def to_dxf(self, filepath: Union[str, Path], layer_prefix: str = "PYFEALITE") -> None:
        """Export structure geometry to DXF file."""
        if not DXF_AVAILABLE:
            warnings.warn("DXF export requires ezdxf package. Install with: pip install ezdxf")
            return
        
        filepath = Path(filepath)
        
        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Create layers
        doc.layers.add(f"{layer_prefix}_NODES", color=1)  # Red
        doc.layers.add(f"{layer_prefix}_ELEMENTS", color=7)  # White
        doc.layers.add(f"{layer_prefix}_SUPPORTS", color=3)  # Green
        doc.layers.add(f"{layer_prefix}_LABELS", color=4)  # Cyan
        
        # Draw elements
        for element in self.structure.elements:
            start = (element.start_node.x, element.start_node.y, 0)
            end = (element.end_node.x, element.end_node.y, 0)
            
            msp.add_line(start, end, dxfattribs={'layer': f"{layer_prefix}_ELEMENTS"})
            
            # Add element label
            mid_x = (element.start_node.x + element.end_node.x) / 2
            mid_y = (element.start_node.y + element.end_node.y) / 2
            if element.label:
                msp.add_text(element.label, dxfattribs={'layer': f"{layer_prefix}_LABELS"}).set_pos(
                    (mid_x, mid_y, 0), align='MIDDLE_CENTER'
                )
        
        # Draw nodes
        for node in self.structure.nodes:
            pos = (node.x, node.y, 0)
            
            # Node symbol
            if node.is_free:
                msp.add_circle(pos, radius=0.05, dxfattribs={'layer': f"{layer_prefix}_NODES"})
            else:
                # Support symbol
                if all(node.restraints[:2]):  # Fixed support
                    msp.add_lwpolyline([
                        (node.x - 0.1, node.y - 0.1),
                        (node.x + 0.1, node.y - 0.1),
                        (node.x + 0.1, node.y + 0.1),
                        (node.x - 0.1, node.y + 0.1)
                    ], close=True, dxfattribs={'layer': f"{layer_prefix}_SUPPORTS"})
                elif node.restraints[1]:  # Pinned or roller
                    msp.add_lwpolyline([
                        (node.x, node.y),
                        (node.x - 0.1, node.y - 0.15),
                        (node.x + 0.1, node.y - 0.15)
                    ], close=True, dxfattribs={'layer': f"{layer_prefix}_SUPPORTS"})
            
            # Node label
            if node.label:
                msp.add_text(node.label, dxfattribs={'layer': f"{layer_prefix}_LABELS"}).set_pos(
                    (node.x, node.y + 0.15, 0), align='MIDDLE_CENTER'
                )
        
        doc.saveas(filepath)
        print(f"Structure geometry exported to DXF: {filepath}")


# Convenience functions
def export_to_json(structure: Structure, filepath: Union[str, Path], indent: int = 2) -> None:
    """Export structure to JSON file."""
    ExportManager(structure).to_json(filepath, indent)


def export_to_csv(structure: Structure, directory: Union[str, Path]) -> None:
    """Export structure to CSV files."""
    ExportManager(structure).to_csv(directory)


def export_to_dxf(structure: Structure, filepath: Union[str, Path], 
                  layer_prefix: str = "PYFEALITE") -> None:
    """Export structure geometry to DXF file."""
    ExportManager(structure).to_dxf(filepath, layer_prefix)


def export_results_summary(structure: Structure, filepath: Union[str, Path]) -> None:
    """Export analysis results summary to text file."""
    if structure.analysis_status != "success":
        print("Structure must be analyzed before exporting results")
        return
    
    filepath = Path(filepath)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"PyFEALiTE Analysis Results Summary\n")
        f.write(f"==================================\n\n")
        f.write(f"Structure: {structure.name}\n")
        f.write(f"Analysis Status: {structure.analysis_status}\n")
        f.write(f"Nodes: {structure.n_nodes}\n")
        f.write(f"Elements: {structure.n_elements}\n")
        f.write(f"DOFs: {structure.n_free_dofs}/{structure.n_dofs}\n\n")
        
        for load_case in structure.load_cases:
            f.write(f"Load Case: {load_case.name}\n")
            f.write(f"{'-' * (len(load_case.name) + 11)}\n")
            
            # Displacements
            f.write("\nDisplacements:\n")
            f.write("Node     UX (m)      UY (m)      RZ (rad)\n")
            f.write("-" * 45 + "\n")
            
            for node in structure.nodes:
                disp = structure.get_node_displacement(node, load_case)
                f.write(f"{node.label:8s} {disp[0]:10.6f} {disp[1]:11.6f} {disp[2]:12.6f}\n")
            
            # Reactions
            f.write("\nReactions:\n")
            f.write("Node     RX (kN)     RY (kN)     MZ (kN·m)\n")
            f.write("-" * 45 + "\n")
            
            total_rx = total_ry = total_mz = 0
            for node in structure.nodes:
                if not node.is_free:
                    reaction = structure.get_node_reaction(node, load_case)
                    f.write(f"{node.label:8s} {reaction[0]:10.2f} {reaction[1]:11.2f} {reaction[2]:12.2f}\n")
                    total_rx += reaction[0]
                    total_ry += reaction[1]
                    total_mz += reaction[2]
            
            f.write("-" * 45 + "\n")
            f.write(f"{'Total':8s} {total_rx:10.2f} {total_ry:11.2f} {total_mz:12.2f}\n\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("Generated by PyFEALiTE - Python Finite Element Analysis Library\n")
    
    print(f"Results summary exported to: {filepath}")