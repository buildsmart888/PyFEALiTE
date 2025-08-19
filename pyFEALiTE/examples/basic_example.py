"""Basic example demonstrating PyFEALiTE usage."""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyfealite.core.node import Node2D, NodalDegreeOfFreedom
from pyfealite.materials.isotropic import IsotropicMaterial


def main():
    """Demonstrate basic PyFEALiTE functionality."""
    print("PyFEALiTE Basic Example")
    print("=" * 30)
    
    # Create nodes
    n1 = Node2D(x=0.0, y=0.0, label="Node_1")
    n2 = Node2D(x=5.0, y=0.0, label="Node_2")
    n3 = Node2D(x=2.5, y=3.0, label="Node_3")
    
    print("\n1. Created Nodes:")
    print(f"   {n1}")
    print(f"   {n2}")
    print(f"   {n3}")
    
    # Apply boundary conditions
    n1.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
    n2.restrain(NodalDegreeOfFreedom.UY)
    
    print("\n2. Applied Restraints:")
    print(f"   {n1.label}: {''.join('R' if r else 'F' for r in n1.restraints)}")
    print(f"   {n2.label}: {''.join('R' if r else 'F' for r in n2.restraints)}")
    print(f"   {n3.label}: {''.join('R' if r else 'F' for r in n3.restraints)}")
    
    # Calculate distances
    print(f"\n3. Distances:")
    print(f"   {n1.label} to {n2.label}: {n1.distance_to(n2):.2f}")
    print(f"   {n1.label} to {n3.label}: {n1.distance_to(n3):.2f}")
    print(f"   {n2.label} to {n3.label}: {n2.distance_to(n3):.2f}")
    
    # Create materials
    steel = IsotropicMaterial.steel("Structural Steel")
    concrete = IsotropicMaterial.concrete("C30")
    
    print(f"\n4. Materials:")
    print(f"   {steel}")
    print(f"   G = {steel.G/1e9:.1f} GPa")
    print(f"   {concrete}")
    print(f"   G = {concrete.G/1e9:.1f} GPa")
    
    print("\n[OK] Basic functionality working!")


if __name__ == "__main__":
    main()