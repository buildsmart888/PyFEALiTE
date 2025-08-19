"""Tests for IsotropicMaterial class."""

import pytest
from pyfealite.materials import IsotropicMaterial, MaterialType


class TestIsotropicMaterial:
    """Test cases for IsotropicMaterial class."""
    
    def test_material_creation(self) -> None:
        """Test basic material creation."""
        material = IsotropicMaterial(
            E=200e9,
            nu=0.3,
            density_value=7850,
            label="Steel"
        )
        
        assert material.E == 200e9
        assert material.nu == 0.3
        assert material.density == 7850
        assert material.label == "Steel"
        assert material.G == pytest.approx(200e9 / (2 * (1 + 0.3)))
    
    def test_material_validation(self) -> None:
        """Test material property validation."""
        # Negative Young's modulus should raise error
        with pytest.raises(ValueError, match="Young's modulus must be positive"):
            IsotropicMaterial(E=-1000, nu=0.3)
        
        # Invalid Poisson's ratio
        with pytest.raises(ValueError, match="Poisson's ratio must be between"):
            IsotropicMaterial(E=200e9, nu=0.6)
        
        with pytest.raises(ValueError, match="Poisson's ratio must be between"):
            IsotropicMaterial(E=200e9, nu=-1.5)
        
        # Negative density
        with pytest.raises(ValueError, match="Density must be non-negative"):
            IsotropicMaterial(E=200e9, nu=0.3, density_value=-100)
    
    def test_shear_modulus_calculation(self) -> None:
        """Test shear modulus calculation."""
        material = IsotropicMaterial(E=210e9, nu=0.3)
        
        expected_G = 210e9 / (2 * (1 + 0.3))
        assert material.G == pytest.approx(expected_G)
    
    def test_bulk_modulus_calculation(self) -> None:
        """Test bulk modulus calculation."""
        material = IsotropicMaterial(E=210e9, nu=0.25)
        
        expected_K = 210e9 / (3 * (1 - 2 * 0.25))
        assert material.bulk_modulus == pytest.approx(expected_K)
    
    def test_steel_preset(self) -> None:
        """Test steel material preset."""
        steel = IsotropicMaterial.steel("Custom Steel")
        
        assert steel.label == "Custom Steel"
        assert steel.material_type == MaterialType.STEEL
        assert steel.E == 200e9
        assert steel.nu == 0.3
        assert steel.density == 7850
        assert steel.G > 0
    
    def test_concrete_preset(self) -> None:
        """Test concrete material preset."""
        concrete = IsotropicMaterial.concrete()
        
        assert concrete.label == "Concrete"
        assert concrete.material_type == MaterialType.CONCRETE
        assert concrete.E == 30e9
        assert concrete.nu == 0.2
        assert concrete.density == 2400
    
    def test_aluminum_preset(self) -> None:
        """Test aluminum material preset."""
        aluminum = IsotropicMaterial.aluminum("Al-6061")
        
        assert aluminum.label == "Al-6061"
        assert aluminum.material_type == MaterialType.ALUMINUM
        assert aluminum.E == 70e9
        assert aluminum.nu == 0.33
        assert aluminum.density == 2700
    
    def test_material_string_representation(self) -> None:
        """Test string representation."""
        material = IsotropicMaterial(
            E=200e9, 
            nu=0.3, 
            label="Test Material"
        )
        
        str_repr = str(material)
        assert "IsotropicMaterial" in str_repr
        assert "Test Material" in str_repr
        assert "200000000000.0" in str_repr or "2e+11" in str_repr