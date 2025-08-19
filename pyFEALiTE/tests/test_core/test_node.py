"""Tests for Node2D class."""

import pytest
import numpy as np
from pyfealite.core.node import Node2D, NodalDegreeOfFreedom


class TestNode2D:
    """Test cases for Node2D class."""
    
    def test_node_creation(self) -> None:
        """Test basic node creation."""
        node = Node2D(x=0.0, y=0.0, label="n1")
        
        assert node.x == 0.0
        assert node.y == 0.0
        assert node.label == "n1"
        assert node.restraints == [False, False, False]
        assert node.is_free
        assert node.dof_count == 3
    
    def test_node_coordinates(self) -> None:
        """Test node coordinates property."""
        node = Node2D(x=1.5, y=2.5, label="n1")
        coords = node.coordinates
        
        assert isinstance(coords, np.ndarray)
        assert coords[0] == 1.5
        assert coords[1] == 2.5
    
    def test_restraints(self) -> None:
        """Test restraint functionality."""
        node = Node2D(x=0.0, y=0.0, label="n1")
        
        # Initially free
        assert not node.is_restrained(NodalDegreeOfFreedom.UX)
        assert not node.is_restrained(NodalDegreeOfFreedom.UY)
        assert not node.is_restrained(NodalDegreeOfFreedom.RZ)
        
        # Restrain UX and UY
        node.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
        
        assert node.is_restrained(NodalDegreeOfFreedom.UX)
        assert node.is_restrained(NodalDegreeOfFreedom.UY)
        assert not node.is_restrained(NodalDegreeOfFreedom.RZ)
        assert node.dof_count == 1
        assert node.is_free
        
        # Fully restrain
        node.restrain(NodalDegreeOfFreedom.RZ)
        assert not node.is_free
        assert node.dof_count == 0
    
    def test_release_restraints(self) -> None:
        """Test releasing restraints."""
        node = Node2D(x=0.0, y=0.0, label="n1")
        
        # Fully restrain first
        node.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY, NodalDegreeOfFreedom.RZ)
        assert not node.is_free
        
        # Release UX
        node.release(NodalDegreeOfFreedom.UX)
        assert not node.is_restrained(NodalDegreeOfFreedom.UX)
        assert node.is_restrained(NodalDegreeOfFreedom.UY)
        assert node.is_restrained(NodalDegreeOfFreedom.RZ)
        assert node.is_free
        assert node.dof_count == 1
    
    def test_distance_calculation(self) -> None:
        """Test distance calculation between nodes."""
        n1 = Node2D(x=0.0, y=0.0, label="n1")
        n2 = Node2D(x=3.0, y=4.0, label="n2")
        
        distance = n1.distance_to(n2)
        assert distance == 5.0
        
        # Distance should be symmetric
        assert n2.distance_to(n1) == distance
        
        # Distance to self should be 0
        assert n1.distance_to(n1) == 0.0
    
    def test_node_equality(self) -> None:
        """Test node equality comparison."""
        n1 = Node2D(x=1.0, y=2.0, label="test")
        n2 = Node2D(x=1.0, y=2.0, label="test")
        n3 = Node2D(x=1.0, y=2.0, label="different")
        n4 = Node2D(x=2.0, y=2.0, label="test")
        
        assert n1 == n2
        assert n1 != n3  # Different label
        assert n1 != n4  # Different coordinates
        assert n1 != "not_a_node"  # Different type
    
    def test_node_hash(self) -> None:
        """Test node hashing for use in sets/dictionaries."""
        n1 = Node2D(x=1.0, y=2.0, label="test")
        n2 = Node2D(x=1.0, y=2.0, label="test")
        n3 = Node2D(x=2.0, y=2.0, label="test")
        
        # Equal nodes should have same hash
        assert hash(n1) == hash(n2)
        
        # Can be used in sets
        node_set = {n1, n2, n3}
        assert len(node_set) == 2  # n1 and n2 are considered same
    
    def test_string_representations(self) -> None:
        """Test string representations."""
        node = Node2D(x=1.5, y=2.5, label="test_node")
        node.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.RZ)
        
        str_repr = str(node)
        assert "test_node" in str_repr
        assert "x=1.5" in str_repr
        assert "y=2.5" in str_repr
        assert "RFR" in str_repr  # Restraint pattern
        
        repr_str = repr(node)
        assert "Node2D" in repr_str
        assert "x=1.5" in repr_str
        assert "y=2.5" in repr_str