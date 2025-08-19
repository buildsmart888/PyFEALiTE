"""Tests for RectangularSection class."""

import pytest
import math
from pyfealite.sections.rectangular import RectangularSection
from pyfealite.materials.isotropic import IsotropicMaterial


class TestRectangularSection:
    """Test cases for RectangularSection class."""
    
    def test_rectangular_creation(self) -> None:
        """Test basic rectangular section creation."""
        steel = IsotropicMaterial.steel()
        section = RectangularSection(
            width=0.3,
            height=0.5,
            material=steel,
            label="Rect300x500"
        )
        
        assert section.width == 0.3
        assert section.height == 0.5
        assert section.label == "Rect300x500"
        assert section.material == steel
    
    def test_area_calculation(self) -> None:
        """Test area calculation."""
        steel = IsotropicMaterial.steel()
        section = RectangularSection(width=0.25, height=0.5, material=steel)
        
        expected_area = 0.25 * 0.5
        assert section.A == pytest.approx(expected_area)
    
    def test_moment_of_inertia(self) -> None:
        """Test moment of inertia calculations."""
        steel = IsotropicMaterial.steel()
        section = RectangularSection(width=0.25, height=0.5, material=steel)
        
        # Iz = b * h³ / 12
        expected_Iz = 0.25 * (0.5**3) / 12
        assert section.Iz == pytest.approx(expected_Iz)
        
        # Iy = h * b³ / 12
        expected_Iy = 0.5 * (0.25**3) / 12
        assert section.Iy == pytest.approx(expected_Iy)
    
    def test_shear_areas(self) -> None:
        """Test shear area calculations."""
        steel = IsotropicMaterial.steel()
        section = RectangularSection(width=0.25, height=0.5, material=steel)
        
        expected_shear_area = 5/6 * section.A
        assert section.Az == pytest.approx(expected_shear_area)
        assert section.Ay == pytest.approx(expected_shear_area)
    
    def test_section_modulus(self) -> None:
        """Test section modulus calculations."""
        steel = IsotropicMaterial.steel()
        section = RectangularSection(width=0.25, height=0.5, material=steel)
        
        expected_Sz = section.Iz / (section.height / 2)
        expected_Sy = section.Iy / (section.width / 2)
        
        assert section.section_modulus_z == pytest.approx(expected_Sz)
        assert section.section_modulus_y == pytest.approx(expected_Sy)
    
    def test_validation(self) -> None:
        """Test validation of section properties."""
        steel = IsotropicMaterial.steel()
        
        # Negative width
        with pytest.raises(ValueError, match="Width must be positive"):
            RectangularSection(width=-0.1, height=0.5, material=steel)
        
        # Negative height
        with pytest.raises(ValueError, match="Height must be positive"):
            RectangularSection(width=0.25, height=-0.1, material=steel)
        
        # Zero dimensions
        with pytest.raises(ValueError):
            RectangularSection(width=0.0, height=0.5, material=steel)
    
    def test_string_representation(self) -> None:
        """Test string representation."""
        steel = IsotropicMaterial.steel()
        section = RectangularSection(
            width=0.25, 
            height=0.5, 
            material=steel,
            label="Test Section"
        )
        
        str_repr = str(section)
        assert "RectangularSection" in str_repr
        assert "Test Section" in str_repr
        assert "0.25x0.5" in str_repr