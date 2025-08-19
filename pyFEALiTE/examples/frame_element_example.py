"""Example demonstrating FrameElement2D usage."""

import sys
from pathlib import Path
import numpy as np

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.core.element import FrameElement2D, EndRelease
from pyfealite.materials.isotropic import IsotropicMaterial
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.sections.circular import CircularSection


def main():
    """Demonstrate FrameElement2D functionality."""
    print("PyFEALiTE - Frame Element Example")
    print("=" * 40)
    
    # Create material
    steel = IsotropicMaterial.steel("S355")
    concrete = IsotropicMaterial.concrete("C30/37")
    
    print(f"\n1. Materials:")
    print(f"   {steel}")
    print(f"   {concrete}")
    
    # Create cross-sections
    rect_section = RectangularSection(
        width=0.3,
        height=0.5,
        material=concrete,
        label="300x500"
    )
    
    circular_section = CircularSection(
        diameter=0.4,
        material=steel,
        label="D400"
    )
    
    print(f"\n2. Cross-sections:")
    print(f"   {rect_section}")
    print(f"   Area: {rect_section.A:.4f} m^2")
    print(f"   Iz: {rect_section.Iz:.2e} m^4")
    print(f"   {circular_section}")
    print(f"   Area: {circular_section.A:.4f} m^2")
    print(f"   Iz: {circular_section.Iz:.2e} m^4")
    
    # Create nodes
    n1 = Node2D(x=0.0, y=0.0, label="Support")
    n2 = Node2D(x=6.0, y=0.0, label="Mid")
    n3 = Node2D(x=12.0, y=0.0, label="End")
    
    # Apply boundary conditions  
    n1.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY, NodalDegreeOfFreedom.RZ)
    n3.restrain(NodalDegreeOfFreedom.UY)
    
    print(f"\n3. Nodes:")
    for node in [n1, n2, n3]:
        restraints = "".join("R" if r else "F" for r in node.restraints)
        print(f"   {node.label}: ({node.x}, {node.y}) [{restraints}]")
    
    # Create frame elements
    beam1 = FrameElement2D(
        start_node=n1,
        end_node=n2,
        cross_section=rect_section,
        label="Beam_1",
        end_release=EndRelease.NO_RELEASE
    )
    
    beam2 = FrameElement2D(
        start_node=n2,
        end_node=n3,
        cross_section=circular_section,
        label="Beam_2",
        end_release=EndRelease.END_RELEASE
    )
    
    print(f"\n4. Frame Elements:")
    print(f"   {beam1}")
    print(f"   Length: {beam1.length:.2f} m")
    print(f"   Angle: {np.degrees(beam1.angle):.1f} deg")
    print(f"   {beam2}")
    print(f"   Length: {beam2.length:.2f} m")
    print(f"   Angle: {np.degrees(beam2.angle):.1f} deg")
    
    # Display stiffness matrices
    print(f"\n5. Stiffness Matrices:")
    print(f"   Beam_1 Local Stiffness Matrix shape: {beam1.local_stiffness_matrix.shape}")
    print(f"   Non-zero elements: {np.count_nonzero(beam1.local_stiffness_matrix)}")
    
    print(f"   Beam_2 Local Stiffness Matrix shape: {beam2.local_stiffness_matrix.shape}")
    print(f"   Non-zero elements: {np.count_nonzero(beam2.local_stiffness_matrix)}")
    
    # Check transformation matrices
    print(f"\n6. Coordinate Transformation:")
    cos_theta, sin_theta = beam1.direction_cosines
    print(f"   Beam_1: cos(theta)={cos_theta:.3f}, sin(theta)={sin_theta:.3f}")
    
    cos_theta, sin_theta = beam2.direction_cosines
    print(f"   Beam_2: cos(theta)={cos_theta:.3f}, sin(theta)={sin_theta:.3f}")
    
    print("\n[OK] Frame element functionality working!")


if __name__ == "__main__":
    main()