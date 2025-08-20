"""
Simple test for materials.base module without complex imports
============================================================

Direct test of Material base class and MaterialType enum.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

# Import the specific module directly
module_path = Path(__file__).parent / "src" / "pyfealite" / "materials" / "base.py"
spec = __import__('importlib.util', fromlist=['spec_from_file_location']).spec_from_file_location("base", module_path)
base_module = __import__('importlib.util', fromlist=['module_from_spec']).module_from_spec(spec)
spec.loader.exec_module(base_module)

Material = base_module.Material
MaterialType = base_module.MaterialType


# Create concrete implementation for testing
@dataclass
class TestMaterial(Material):
    """Test implementation of Material abstract class."""
    
    G_value: float = 80000.0
    density_value: float = 7850.0
    
    @property
    def G(self) -> float:
        """Shear modulus."""
        return self.G_value
    
    @property
    def density(self) -> float:
        """Material density."""
        return self.density_value


def test_material_type():
    """Test MaterialType enumeration."""
    print("📋 Testing MaterialType enum...")
    
    # Test enum values
    assert MaterialType.STEEL.value == "steel"
    assert MaterialType.CONCRETE.value == "concrete"
    assert MaterialType.ALUMINUM.value == "aluminum"
    assert MaterialType.WOOD.value == "wood"
    assert MaterialType.COMPOSITE.value == "composite"
    
    # Test enum count
    assert len(MaterialType) == 5
    
    print("✅ MaterialType tests passed")


def test_material_creation():
    """Test Material creation and validation."""
    print("🏗️  Testing Material creation...")
    
    # Valid material
    material = TestMaterial(
        E=200000.0,
        label="Steel Grade 50",
        material_type=MaterialType.STEEL
    )
    
    assert material.E == 200000.0
    assert material.label == "Steel Grade 50"
    assert material.material_type == MaterialType.STEEL
    assert material.G == 80000.0
    assert material.density == 7850.0
    
    print("✅ Material creation tests passed")


def test_material_validation():
    """Test Material validation."""
    print("🛡️  Testing Material validation...")
    
    # Test zero Young's modulus
    try:
        TestMaterial(E=0.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Young's modulus must be positive" in str(e)
    
    # Test negative Young's modulus
    try:
        TestMaterial(E=-1000.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Young's modulus must be positive" in str(e)
    
    print("✅ Material validation tests passed")


def test_material_string_representation():
    """Test Material string representation."""
    print("📝 Testing Material string representation...")
    
    material = TestMaterial(
        E=200000.0,
        label="Test Steel"
    )
    
    expected = "TestMaterial('Test Steel', E=200000.0)"
    actual = str(material)
    assert actual == expected, f"Expected '{expected}', got '{actual}'"
    
    print("✅ Material string representation tests passed")


def test_material_equality():
    """Test Material equality."""
    print("⚖️  Testing Material equality...")
    
    material1 = TestMaterial(
        E=200000.0,
        label="Steel",
        material_type=MaterialType.STEEL
    )
    material2 = TestMaterial(
        E=200000.0,
        label="Steel",
        material_type=MaterialType.STEEL
    )
    
    assert material1 == material2
    
    # Test inequality
    material3 = TestMaterial(E=210000.0, label="Steel")
    assert material1 != material3
    
    print("✅ Material equality tests passed")


def test_material_properties():
    """Test Material properties."""
    print("🔧 Testing Material properties...")
    
    material = TestMaterial(
        E=70000.0,
        label="Aluminum 6061",
        material_type=MaterialType.ALUMINUM,
        G_value=26000.0,
        density_value=2700.0
    )
    
    assert material.E == 70000.0
    assert material.G == 26000.0
    assert material.density == 2700.0
    assert material.material_type == MaterialType.ALUMINUM
    
    print("✅ Material properties tests passed")


def test_material_edge_cases():
    """Test Material edge cases."""
    print("🎯 Testing Material edge cases...")
    
    # Very large E
    large_E = 1e12
    material = TestMaterial(E=large_E)
    assert material.E == large_E
    
    # Very small positive E
    small_E = 1e-6
    material = TestMaterial(E=small_E)
    assert material.E == small_E
    
    # Unicode label
    material = TestMaterial(E=200000.0, label="เหล็ก Grade 50")
    assert material.label == "เหล็ก Grade 50"
    
    # Empty label
    material = TestMaterial(E=200000.0, label="")
    assert material.label == ""
    
    print("✅ Material edge cases tests passed")


def main():
    """Run all tests."""
    print("🧪 Running Material Base Class Tests")
    print("=" * 50)
    
    try:
        test_material_type()
        test_material_creation()
        test_material_validation()
        test_material_string_representation()
        test_material_equality()
        test_material_properties()
        test_material_edge_cases()
        
        print("\n🎉 All Material base class tests completed successfully!")
        print("📊 Test Summary:")
        print("   ✅ MaterialType enum: 5 types validated")
        print("   ✅ Material creation: Valid and invalid cases tested")
        print("   ✅ Material validation: Positive E enforcement working")
        print("   ✅ Material representation: String output correct")
        print("   ✅ Material equality: Comparison logic working")
        print("   ✅ Material properties: Abstract methods implemented")
        print("   ✅ Material edge cases: Unicode, extremes handled")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
