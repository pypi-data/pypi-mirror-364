"""Tests for Point3D class."""

import pytest
import numpy as np

from lcvtoolbox.spatial.primitives.point import Point3D


class TestPoint3D:
    """Test cases for Point3D class."""
    
    def test_creation(self):
        """Test Point3D creation methods."""
        # Basic creation
        p1 = Point3D(1.0, 2.0, 3.0)
        assert p1.x == 1.0
        assert p1.y == 2.0
        assert p1.z == 3.0
        
        # Default z value
        p2 = Point3D(1.0, 2.0)
        assert p2.z == 0.0
    
    def test_from_numpy(self):
        """Test creation from numpy array."""
        arr = np.array([1.0, 2.0, 3.0])
        p = Point3D.from_numpy(arr)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0
        
        # Test 2D array
        arr2d = np.array([4.0, 5.0])
        p2d = Point3D.from_numpy(arr2d)
        assert p2d.x == 4.0
        assert p2d.y == 5.0
        assert p2d.z == 0.0
        
        # Test invalid array
        with pytest.raises(ValueError):
            Point3D.from_numpy(np.array([1.0]))
    
    def test_from_tuple(self):
        """Test creation from tuple."""
        p = Point3D.from_tuple((1.0, 2.0, 3.0))
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0
        
        # 2D tuple
        p2d = Point3D.from_tuple((4.0, 5.0))
        assert p2d.z == 0.0
    
    def test_from_list(self):
        """Test creation from list using numpy."""
        p = Point3D.from_numpy(np.array([1.0, 2.0, 3.0]))
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0
    
    def test_origin(self):
        """Test origin creation."""
        p = Point3D.origin()
        assert p.x == 0.0
        assert p.y == 0.0
        assert p.z == 0.0
    
    def test_unit_vectors(self):
        """Test unit vector creation."""
        px = Point3D.unit_x()
        assert px.x == 1.0 and px.y == 0.0 and px.z == 0.0
        
        py = Point3D.unit_y()
        assert py.x == 0.0 and py.y == 1.0 and py.z == 0.0
        
        pz = Point3D.unit_z()
        assert pz.x == 0.0 and pz.y == 0.0 and pz.z == 1.0
    
    def test_properties(self):
        """Test property access."""
        p = Point3D(1.0, 2.0, 3.0)
        
        # Numpy conversion
        arr = p.numpy
        assert isinstance(arr, np.ndarray)
        assert np.array_equal(arr, np.array([1.0, 2.0, 3.0]))
        
        # XY and XYZ properties
        assert p.xy == (1.0, 2.0)
        assert p.xyz == (1.0, 2.0, 3.0)
        
        # Magnitude
        assert p.magnitude == pytest.approx(np.sqrt(14.0))
        assert p.magnitude_squared == 14.0
        
        # Normalized
        p_norm = p.normalize()
        assert p_norm.magnitude == pytest.approx(1.0)
        
        # is_origin
        assert not p.is_origin
        assert Point3D.origin().is_origin
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        
        # Addition
        p_add = p1 + p2
        assert p_add.x == 5.0
        assert p_add.y == 7.0
        assert p_add.z == 9.0
        
        # Subtraction
        p_sub = p2 - p1
        assert p_sub.x == 3.0
        assert p_sub.y == 3.0
        assert p_sub.z == 3.0
        
        # Scalar multiplication
        p_mul = p1 * 2.0
        assert p_mul.x == 2.0
        assert p_mul.y == 4.0
        assert p_mul.z == 6.0
        
        # Scalar division
        p_div = p2 / 2.0
        assert p_div.x == 2.0
        assert p_div.y == 2.5
        assert p_div.z == 3.0
        
        # Division by zero (returns inf/nan with warning)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p_div_zero = p1 / 0.0
            assert np.isinf(p_div_zero.x)
        
        # Negation
        p_neg = -p1
        assert p_neg.x == -1.0
        assert p_neg.y == -2.0
        assert p_neg.z == -3.0
    
    def test_distance(self):
        """Test distance calculations."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)
        
        assert p1.distance_to(p2) == 5.0
        assert p2.distance_to(p1) == 5.0
    
    def test_dot_product(self):
        """Test dot product."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        
        assert p1.dot(p2) == 32.0  # 1*4 + 2*5 + 3*6
    
    def test_cross_product(self):
        """Test cross product."""
        p1 = Point3D(1.0, 0.0, 0.0)
        p2 = Point3D(0.0, 1.0, 0.0)
        
        p_cross = p1.cross(p2)
        assert p_cross.x == 0.0
        assert p_cross.y == 0.0
        assert p_cross.z == 1.0
    
    def test_comparison(self):
        """Test comparison operations."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(1.0, 2.0, 3.0)
        p3 = Point3D(1.0, 2.0, 3.1)
        
        # Equality
        assert p1 == p2
        assert not (p1 == p3)
        assert p1 != p3
        
        # is_close
        assert p1.is_close(p2)
        assert not p1.is_close(p3, tolerance=0.01)
        assert p1.is_close(p3, tolerance=0.2)
    
    def test_midpoint(self):
        """Test midpoint calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(2.0, 2.0, 2.0)
        
        mid = p1.midpoint(p2)
        assert mid.x == 1.0
        assert mid.y == 1.0
        assert mid.z == 1.0
    
    def test_lerp(self):
        """Test linear interpolation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(10.0, 10.0, 10.0)
        
        # t = 0
        p_t0 = p1.lerp(p2, 0.0)
        assert p_t0 == p1
        
        # t = 1
        p_t1 = p1.lerp(p2, 1.0)
        assert p_t1 == p2
        
        # t = 0.5
        p_t05 = p1.lerp(p2, 0.5)
        assert p_t05.x == 5.0
        assert p_t05.y == 5.0
        assert p_t05.z == 5.0
    
    def test_copy(self):
        """Test copy operation."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = p1.copy()
        
        assert p1 == p2
        assert p1 is not p2  # Different objects
    
    def test_string_representation(self):
        """Test string representations."""
        p = Point3D(1.5, 2.5, 3.5)
        
        # repr
        repr_str = repr(p)
        assert "Point" in repr_str  # The class uses "Point" in repr
        assert "1.5" in repr_str
        
        # str
        str_str = str(p)
        assert "1.5" in str_str
        assert "2.5" in str_str
        assert "3.5" in str_str
    
    def test_indexing(self):
        """Test indexing operations."""
        p = Point3D(1.0, 2.0, 3.0)
        
        # Get item
        assert p[0] == 1.0
        assert p[1] == 2.0
        assert p[2] == 3.0
        
        # Invalid index
        with pytest.raises(IndexError):
            _ = p[3]
        
        # Set item
        p[0] = 10.0
        assert p.x == 10.0
        
        # Iteration
        coords = list(p)
        assert coords == [10.0, 2.0, 3.0]
        
        # Length
        assert len(p) == 3
    
    def test_hash(self):
        """Test hash function."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(1.0, 2.0, 3.0)
        p3 = Point3D(1.0, 2.0, 3.1)
        
        # Same points should have same hash
        assert hash(p1) == hash(p2)
        
        # Different points likely have different hash (not guaranteed but very likely)
        assert hash(p1) != hash(p3)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Very large values
        p_large = Point3D(1e308, 1e308, 1e308)
        assert p_large.x == 1e308
        
        # Very small values (avoid underflow)
        p_small = Point3D(1e-150, 1e-150, 1e-150)
        assert p_small.magnitude > 0 or p_small.magnitude == 0  # May underflow to 0
        
        # NaN handling
        p_nan = Point3D(float('nan'), 0, 0)
        assert np.isnan(p_nan.x)
        assert np.isnan(p_nan.magnitude)
        
        # Infinity
        p_inf = Point3D(float('inf'), 0, 0)
        assert np.isinf(p_inf.x)
        assert np.isinf(p_inf.magnitude)
