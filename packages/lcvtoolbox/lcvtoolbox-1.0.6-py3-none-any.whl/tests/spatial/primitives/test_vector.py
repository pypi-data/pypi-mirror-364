"""Tests for Vector3D class."""

import pytest
import numpy as np

from lcvtoolbox.spatial.primitives.vector import Vector3D


class TestVector3D:
    """Test cases for Vector3D class."""
    
    def test_creation(self):
        """Test Vector3D creation methods."""
        # Basic creation
        v1 = Vector3D(1.0, 2.0, 3.0)
        assert v1.x == 1.0
        assert v1.y == 2.0
        assert v1.z == 3.0
        
        # Default values
        v2 = Vector3D(1.0, 2.0)
        assert v2.z == 0.0
    
    def test_from_numpy(self):
        """Test creation from numpy array."""
        arr = np.array([1.0, 2.0, 3.0])
        v = Vector3D.from_numpy(arr)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
        
        # Test invalid array
        with pytest.raises(ValueError):
            Vector3D.from_numpy(np.array([1.0]))
    
    def test_from_tuple(self):
        """Test creation from tuple."""
        v = Vector3D.from_tuple((1.0, 2.0, 3.0))
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
    
    def test_from_list(self):
        """Test creation from list using numpy."""
        v = Vector3D.from_numpy(np.array([1.0, 2.0, 3.0]))
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
    
    def test_special_vectors(self):
        """Test special vector creation."""
        # Zero vector
        v_zero = Vector3D.zeros()
        assert v_zero.x == 0.0 and v_zero.y == 0.0 and v_zero.z == 0.0
        
        # Ones vector
        v_ones = Vector3D.ones()
        assert v_ones.x == 1.0 and v_ones.y == 1.0 and v_ones.z == 1.0
        
        # Unit vectors
        v_x = Vector3D.unit_x()
        assert v_x.x == 1.0 and v_x.y == 0.0 and v_x.z == 0.0
        
        v_y = Vector3D.unit_y()
        assert v_y.x == 0.0 and v_y.y == 1.0 and v_y.z == 0.0
        
        v_z = Vector3D.unit_z()
        assert v_z.x == 0.0 and v_z.y == 0.0 and v_z.z == 1.0
    
    def test_properties(self):
        """Test property access."""
        v = Vector3D(3.0, 4.0, 0.0)
        
        # Numpy conversion
        arr = v.numpy
        assert isinstance(arr, np.ndarray)
        assert np.array_equal(arr, np.array([3.0, 4.0, 0.0]))
        
        # Magnitude
        assert v.magnitude == 5.0
        assert v.magnitude_squared == 25.0
        
        # Normalized
        v_norm = v.normalize()
        assert v_norm.magnitude == pytest.approx(1.0)
        assert v_norm.x == pytest.approx(0.6)
        assert v_norm.y == pytest.approx(0.8)
        
        # is_zero
        assert not v.is_zero
        assert Vector3D.zeros().is_zero
        
        # is_unit
        assert not v.is_unit
        assert v_norm.is_unit
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        
        # Addition
        v_add = v1 + v2
        assert v_add.x == 5.0
        assert v_add.y == 7.0
        assert v_add.z == 9.0
        
        # Subtraction
        v_sub = v2 - v1
        assert v_sub.x == 3.0
        assert v_sub.y == 3.0
        assert v_sub.z == 3.0
        
        # Scalar multiplication
        v_mul = v1 * 2.0
        assert v_mul.x == 2.0
        assert v_mul.y == 4.0
        assert v_mul.z == 6.0
        
        # Scalar division
        v_div = v2 / 2.0
        assert v_div.x == 2.0
        assert v_div.y == 2.5
        assert v_div.z == 3.0
        
        # Division by zero
        with pytest.raises(ValueError):
            v1 / 0.0
        
        # Negation
        v_neg = -v1
        assert v_neg.x == -1.0
        assert v_neg.y == -2.0
        assert v_neg.z == -3.0
    
    def test_dot_product(self):
        """Test dot product."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        
        assert v1.dot(v2) == 32.0  # 1*4 + 2*5 + 3*6
    
    def test_cross_product(self):
        """Test cross product."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(0.0, 1.0, 0.0)
        
        v_cross = v1.cross(v2)
        assert v_cross.x == 0.0
        assert v_cross.y == 0.0
        assert v_cross.z == 1.0
    
    def test_angle_to(self):
        """Test angle between vectors."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(0.0, 1.0, 0.0)
        
        # 90 degrees
        angle = v1.angle_to(v2)
        assert angle == pytest.approx(np.pi / 2)
        
        # 0 degrees (same direction)
        angle_same = v1.angle_to(v1)
        assert angle_same == pytest.approx(0.0)
        
        # 180 degrees (opposite direction)
        angle_opposite = v1.angle_to(-v1)
        assert angle_opposite == pytest.approx(np.pi)
    
    def test_projection(self):
        """Test vector projection."""
        v1 = Vector3D(3.0, 4.0, 0.0)
        v2 = Vector3D(1.0, 0.0, 0.0)
        
        # Project v1 onto v2
        proj = v1.project_onto(v2)
        assert proj.x == 3.0
        assert proj.y == 0.0
        assert proj.z == 0.0
    
    def test_reject_from(self):
        """Test perpendicular component."""
        v1 = Vector3D(3.0, 4.0, 0.0)
        v2 = Vector3D(1.0, 0.0, 0.0)
        
        # Get component perpendicular to v2
        v_perp = v1.reject_from(v2)
        assert v_perp.x == 0.0
        assert v_perp.y == 4.0
        assert v_perp.z == 0.0
        
        # Should be perpendicular
        assert v2.dot(v_perp) == pytest.approx(0.0)
    
    def test_rotate_around_axis(self):
        """Test rotation around axis."""
        v = Vector3D(1.0, 0.0, 0.0)
        axis = Vector3D(0.0, 0.0, 1.0)
        
        # Rotate 90 degrees around Z axis
        v_rotated = v.rotate_around_axis(axis, np.pi / 2)
        assert v_rotated.x == pytest.approx(0.0)
        assert v_rotated.y == pytest.approx(1.0)
        assert v_rotated.z == pytest.approx(0.0)
    
    def test_comparison(self):
        """Test comparison operations."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(1.0, 2.0, 3.0)
        v3 = Vector3D(1.0, 2.0, 3.1)
        
        # Equality
        assert v1 == v2
        assert not (v1 == v3)
        assert v1 != v3
        
        # is_close
        assert v1.is_close(v2)
        assert not v1.is_close(v3, tolerance=0.01)
        assert v1.is_close(v3, tolerance=0.2)
        
        # is_parallel
        v_parallel = v1 * 2.0
        assert v1.is_parallel(v_parallel)
        assert v1.is_parallel(-v_parallel)  # Anti-parallel
        
        v_not_parallel = Vector3D(0.0, 1.0, 0.0)
        assert not v1.is_parallel(v_not_parallel)
        
        # is_perpendicular
        v_x = Vector3D.unit_x()
        v_y = Vector3D.unit_y()
        assert v_x.is_perpendicular(v_y)
        assert not v_x.is_perpendicular(v_x)
    
    def test_copy(self):
        """Test copy operation."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = v1.copy()
        
        assert v1 == v2
        assert v1 is not v2  # Different objects
    
    def test_string_representation(self):
        """Test string representations."""
        v = Vector3D(1.5, 2.5, 3.5)
        
        # repr
        repr_str = repr(v)
        assert "Vector3D" in repr_str
        assert "1.5" in repr_str
        
        # str
        str_str = str(v)
        assert "1.500" in str_str
        assert "2.500" in str_str
        assert "3.500" in str_str
    
    def test_indexing(self):
        """Test indexing operations."""
        v = Vector3D(1.0, 2.0, 3.0)
        
        # Get item
        assert v[0] == 1.0
        assert v[1] == 2.0
        assert v[2] == 3.0
        
        # Invalid index
        with pytest.raises(IndexError):
            _ = v[3]
        
        # Set item
        v[0] = 10.0
        assert v.x == 10.0
        
        # Iteration
        coords = list(v)
        assert coords == [10.0, 2.0, 3.0]
        
        # Length
        assert len(v) == 3
    
    def test_hash(self):
        """Test hash function."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(1.0, 2.0, 3.0)
        v3 = Vector3D(1.0, 2.0, 3.1)
        
        # Same vectors should have same hash
        assert hash(v1) == hash(v2)
        
        # Different vectors likely have different hash
        assert hash(v1) != hash(v3)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Zero vector operations
        v_zero = Vector3D.zeros()
        with pytest.raises(ValueError):
            v_zero.normalize()  # Can't normalize zero vector
        
        # Very small vectors
        v_small = Vector3D(1e-10, 0, 0)
        v_norm = v_small.normalize()
        assert v_norm.x == pytest.approx(1.0)
        
        # Parallel vectors with zero
        v = Vector3D(1.0, 2.0, 3.0)
        # Zero vector is special case, check manually
        with pytest.raises(ValueError):
            v.is_parallel(v_zero)  # Can't check parallelism with zero vector
        
        # Angle with zero vector
        with pytest.raises(ValueError):
            v.angle_to(v_zero)
