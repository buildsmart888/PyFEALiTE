"""
Tests for materials.base module
==============================

Comprehensive tests for Material base class and MaterialType enum.
"""

import pytest
import sys
from pathlib import Path
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyfealite.materials.base import Material, MaterialType


# Create concrete implementation for testing
@dataclass
class TestMaterial(Material):
    """Test implementation of Material abstract class."""
    
    G_value: float = 80000.0  # Default shear modulus
    density_value: float = 7850.0  # Default density (steel)
    
    @property
    def G(self) -> float:
        """Shear modulus."""
        return self.G_value
    
    @property
    def density(self) -> float:
        """Material density."""
        return self.density_value


class TestMaterialType:
    """Test MaterialType enumeration."""
    
    def test_material_type_values(self):
        """Test MaterialType enum values."""
        assert MaterialType.STEEL.value == "steel"
        assert MaterialType.CONCRETE.value == "concrete"
        assert MaterialType.ALUMINUM.value == "aluminum"
        assert MaterialType.WOOD.value == "wood"
        assert MaterialType.COMPOSITE.value == "composite"
    
    def test_material_type_members(self):
        """Test MaterialType enum members."""
        expected_types = {
            MaterialType.STEEL,
            MaterialType.CONCRETE,
            MaterialType.ALUMINUM,
            MaterialType.WOOD,
            MaterialType.COMPOSITE
        }
        assert set(MaterialType) == expected_types
    
    def test_material_type_count(self):
        """Test number of material types."""
        assert len(MaterialType) == 5


class TestMaterial:
    """Test Material base class."""
    
    def test_material_creation_valid(self):
        """Test creating material with valid properties."""
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
    
    def test_material_creation_minimal(self):
        """Test creating material with minimal properties."""
        material = TestMaterial(E=200000.0)
        
        assert material.E == 200000.0
        assert material.label == ""
        assert material.material_type == MaterialType.STEEL  # Default
        assert material.G == 80000.0
        assert material.density == 7850.0
    
    def test_material_creation_with_custom_properties(self):
        """Test creating material with custom G and density."""
        material = TestMaterial(
            E=70000.0,
            label="Aluminum 6061",
            material_type=MaterialType.ALUMINUM,
            G_value=26000.0,
            density_value=2700.0
        )
        
        assert material.E == 70000.0
        assert material.label == "Aluminum 6061"
        assert material.material_type == MaterialType.ALUMINUM
        assert material.G == 26000.0
        assert material.density == 2700.0
    
    def test_material_invalid_young_modulus_zero(self):
        """Test material creation with zero Young's modulus."""
        with pytest.raises(ValueError, match="Young's modulus must be positive"):
            TestMaterial(E=0.0)
    
    def test_material_invalid_young_modulus_negative(self):
        """Test material creation with negative Young's modulus."""
        with pytest.raises(ValueError, match="Young's modulus must be positive"):
            TestMaterial(E=-1000.0)
    
    def test_material_string_representation(self):
        """Test material string representation."""
        material = TestMaterial(
            E=200000.0,
            label="Test Steel"
        )
        
        expected = "TestMaterial('Test Steel', E=200000.0)"
        assert str(material) == expected
    
    def test_material_string_representation_no_label(self):
        """Test material string representation without label."""
        material = TestMaterial(E=200000.0)
        
        expected = "TestMaterial('', E=200000.0)"
        assert str(material) == expected
    
    def test_material_properties_abstract(self):
        """Test that Material cannot be instantiated directly."""
        with pytest.raises(TypeError):
            # This should fail because Material is abstract
            Material(E=200000.0)  # type: ignore
    
    def test_material_modification_after_creation(self):
        """Test modifying material properties after creation."""
        material = TestMaterial(E=200000.0, label="Original")
        
        # Dataclass allows modification
        material.label = "Modified"
        material.E = 210000.0
        
        assert material.label == "Modified"
        assert material.E == 210000.0
    
    def test_material_validation_on_modification(self):
        """Test validation when modifying Young's modulus."""
        material = TestMaterial(E=200000.0)
        
        # Direct assignment bypasses __post_init__, so this won't raise an error
        # This is a limitation of dataclasses - validation only occurs during __init__
        material.E = -1000.0
        assert material.E == -1000.0
        
        # However, creating a new instance with invalid E will still raise an error
        with pytest.raises(ValueError):
            TestMaterial(E=-1000.0)


class TestMaterialComparison:
    """Test material comparison and equality."""
    
    def test_material_equality(self):
        """Test material equality comparison."""
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
        
        # Dataclasses implement __eq__ automatically
        assert material1 == material2
    
    def test_material_inequality_different_E(self):
        """Test material inequality with different E."""
        material1 = TestMaterial(E=200000.0, label="Steel")
        material2 = TestMaterial(E=210000.0, label="Steel")
        
        assert material1 != material2
    
    def test_material_inequality_different_label(self):
        """Test material inequality with different label."""
        material1 = TestMaterial(E=200000.0, label="Steel A")
        material2 = TestMaterial(E=200000.0, label="Steel B")
        
        assert material1 != material2
    
    def test_material_inequality_different_type(self):
        """Test material inequality with different material type."""
        material1 = TestMaterial(
            E=200000.0,
            material_type=MaterialType.STEEL
        )
        material2 = TestMaterial(
            E=200000.0,
            material_type=MaterialType.ALUMINUM
        )
        
        assert material1 != material2


class TestMaterialEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_material_very_large_E(self):
        """Test material with very large Young's modulus."""
        large_E = 1e12  # Very stiff material
        material = TestMaterial(E=large_E)
        
        assert material.E == large_E
    
    def test_material_very_small_E(self):
        """Test material with very small positive Young's modulus."""
        small_E = 1e-6  # Very soft material
        material = TestMaterial(E=small_E)
        
        assert material.E == small_E
    
    def test_material_unicode_label(self):
        """Test material with unicode characters in label."""
        material = TestMaterial(
            E=200000.0,
            label="เหล็ก Grade 50"  # Thai characters
        )
        
        assert material.label == "เหล็ก Grade 50"
        assert "เหล็ก Grade 50" in str(material)
    
    def test_material_long_label(self):
        """Test material with very long label."""
        long_label = "A" * 1000  # Very long label
        material = TestMaterial(E=200000.0, label=long_label)
        
        assert material.label == long_label
        assert len(material.label) == 1000
    
    def test_material_empty_vs_none_label(self):
        """Test difference between empty string and no label."""
        material1 = TestMaterial(E=200000.0, label="")
        material2 = TestMaterial(E=200000.0)  # Uses default empty string
        
        assert material1.label == material2.label == ""
        assert material1 == material2


# Integration tests with other material types
class TestMaterialIntegration:
    """Integration tests for Material base class."""
    
    def test_different_material_types(self):
        """Test creating materials of different types."""
        materials = [
            TestMaterial(E=200000.0, label="Steel", material_type=MaterialType.STEEL),
            TestMaterial(E=30000.0, label="Concrete", material_type=MaterialType.CONCRETE),
            TestMaterial(E=70000.0, label="Aluminum", material_type=MaterialType.ALUMINUM),
            TestMaterial(E=12000.0, label="Wood", material_type=MaterialType.WOOD),
            TestMaterial(E=150000.0, label="Composite", material_type=MaterialType.COMPOSITE),
        ]
        
        assert len(materials) == 5
        assert all(isinstance(m, TestMaterial) for m in materials)
        assert all(m.E > 0 for m in materials)
    
    def test_material_library_simulation(self):
        """Test simulating a material library."""
        material_library = {
            "ASTM_A992": TestMaterial(
                E=200000.0,
                label="ASTM A992 Steel",
                material_type=MaterialType.STEEL,
                G_value=80000.0,
                density_value=7850.0
            ),
            "ALUMINUM_6061": TestMaterial(
                E=69000.0,
                label="Aluminum 6061-T6",
                material_type=MaterialType.ALUMINUM,
                G_value=26000.0,
                density_value=2700.0
            ),
            "DOUGLAS_FIR": TestMaterial(
                E=13100.0,
                label="Douglas Fir",
                material_type=MaterialType.WOOD,
                G_value=830.0,
                density_value=510.0
            )
        }
        
        # Test accessing materials
        steel = material_library["ASTM_A992"]
        assert steel.material_type == MaterialType.STEEL
        assert steel.E == 200000.0
        
        aluminum = material_library["ALUMINUM_6061"]
        assert aluminum.material_type == MaterialType.ALUMINUM
        assert aluminum.density == 2700.0
        
        wood = material_library["DOUGLAS_FIR"]
        assert wood.material_type == MaterialType.WOOD
        assert wood.G == 830.0


if __name__ == "__main__":
    # Run tests manually if executed directly
    import sys
    
    print("🧪 Running Material Base Class Tests")
    print("=" * 50)
    
    # Test MaterialType
    print("\n📋 Testing MaterialType enum...")
    test_type = TestMaterialType()
    test_type.test_material_type_values()
    test_type.test_material_type_members()
    test_type.test_material_type_count()
    print("✅ MaterialType tests passed")
    
    # Test Material
    print("\n🏗️  Testing Material base class...")
    test_material = TestMaterial()
    try:
        test_material.test_material_creation_valid()
        test_material.test_material_creation_minimal()
        test_material.test_material_string_representation()
        print("✅ Material basic tests passed")
    except Exception as e:
        print(f"❌ Material test failed: {e}")
        sys.exit(1)
    
    # Test validation
    print("\n🛡️  Testing validation...")
    try:
        TestMaterial(E=-1000.0)
        print("❌ Validation test failed - should have raised ValueError")
        sys.exit(1)
    except ValueError:
        print("✅ Validation tests passed")
    
    print("\n🎉 All Material base class tests completed successfully!")
