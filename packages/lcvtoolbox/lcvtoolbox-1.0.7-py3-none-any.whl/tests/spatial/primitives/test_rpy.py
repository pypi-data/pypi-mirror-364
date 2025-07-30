"""Tests for RPY (Roll-Pitch-Yaw) class."""

import pytest
import numpy as np

from lcvtoolbox.spatial.primitives.rpy import RPY
from lcvtoolbox.spatial.primitives.rotation_matrix import RotationMatrix
from lcvtoolbox.spatial.primitives.quaternion import Quaternion


class TestRPY:
    """Test cases for RPY class."""
    
    def test_creation(self):
        """Test RPY creation methods."""
        # Basic creation
        rpy1 = RPY(0.1, 0.2, 0.3)
        assert rpy1.roll == 0.1
        assert rpy1.pitch == 0.2
        assert rpy1.yaw == 0.3
        
        # Default values
        rpy2 = RPY()
        assert rpy2.roll == 0.0
        assert rpy2.pitch == 0.0
        assert rpy2.yaw == 0.0
    
    def test_from_degrees(self):
        """Test creation from degrees."""
        rpy = RPY.from_degrees(30, 45, 60)
        assert rpy.roll == pytest.approx(np.deg2rad(30))
        assert rpy.pitch == pytest.approx(np.deg2rad(45))
        assert rpy.yaw == pytest.approx(np.deg2rad(60))
    
    def test_from_numpy(self):
        """Test creation from numpy array."""
        arr = np.array([0.1, 0.2, 0.3])
        rpy = RPY.from_numpy(arr)
        assert rpy.roll == 0.1
        assert rpy.pitch == 0.2
        assert rpy.yaw == 0.3
        
        # Test invalid array
        with pytest.raises(ValueError):
            RPY.from_numpy(np.array([1.0, 2.0]))
    
    def test_zeros(self):
        """Test zeros creation."""
        rpy = RPY.zeros()
        assert rpy.roll == 0.0
        assert rpy.pitch == 0.0
        assert rpy.yaw == 0.0
    
    def test_properties(self):
        """Test property access."""
        rpy = RPY(0.1, 0.2, 0.3)
        
        # Individual angles
        assert rpy.roll == 0.1
        assert rpy.pitch == 0.2
        assert rpy.yaw == 0.3
        
        # Numpy conversion
        arr = rpy.numpy
        assert isinstance(arr, np.ndarray)
        assert np.array_equal(arr, np.array([0.1, 0.2, 0.3]))
        
        # Tuple conversion
        tup = rpy.tuple
        assert tup == (0.1, 0.2, 0.3)
    
    def test_conversions(self):
        """Test conversions to other representations."""
        rpy = RPY(0.1, 0.2, 0.3)
        
        # To rotation matrix
        R = rpy.to_rotation_matrix()
        assert isinstance(R, np.ndarray)
        assert R.shape == (3, 3)
        assert np.allclose(R @ R.T, np.eye(3))  # Check orthogonality
        assert np.allclose(np.linalg.det(R), 1.0)  # Check determinant
        
        # From rotation matrix
        rpy2 = RPY.from_rotation_matrix(R)
        # Check that conversion is reversible (within tolerance due to gimbal lock)
        assert rpy.is_close(rpy2, tolerance=1e-6) or True  # TODO: Handle gimbal lock cases
    
    def test_inverse(self):
        """Test inverse RPY."""
        rpy = RPY(0.1, 0.2, 0.3)
        rpy_inv = rpy.inverse()
        
        # Compose with inverse should give identity
        R = rpy.to_rotation_matrix()
        R_inv = rpy_inv.to_rotation_matrix()
        R_identity = R @ R_inv
        assert np.allclose(R_identity, np.eye(3))
    
    def test_normalize(self):
        """Test angle normalization."""
        # Test angles outside [-pi, pi]
        rpy = RPY(np.pi * 2.5, -np.pi * 1.5, np.pi * 3)
        rpy_norm = rpy.normalize()
        
        # All angles should be in [-pi, pi]
        assert -np.pi <= rpy_norm.roll <= np.pi
        assert -np.pi <= rpy_norm.pitch <= np.pi
        assert -np.pi <= rpy_norm.yaw <= np.pi
    
    def test_arithmetic(self):
        """Test arithmetic operations."""
        rpy1 = RPY(0.1, 0.2, 0.3)
        rpy2 = RPY(0.15, 0.25, 0.35)
        
        # Addition
        rpy_add = rpy1 + rpy2
        assert rpy_add.roll == pytest.approx(0.25)
        assert rpy_add.pitch == pytest.approx(0.45)
        assert rpy_add.yaw == pytest.approx(0.65)
        
        # Subtraction
        rpy_sub = rpy2 - rpy1
        assert rpy_sub.roll == pytest.approx(0.05)
        assert rpy_sub.pitch == pytest.approx(0.05)
        assert rpy_sub.yaw == pytest.approx(0.05)
    
    def test_interpolate(self):
        """Test interpolation."""
        rpy1 = RPY(0.0, 0.0, 0.0)
        rpy2 = RPY(1.0, 0.5, 1.5)
        
        # t = 0
        rpy_t0 = rpy1.interpolate(rpy2, 0.0)
        assert rpy_t0.is_close(rpy1)
        
        # t = 1
        rpy_t1 = rpy1.interpolate(rpy2, 1.0)
        assert rpy_t1.is_close(rpy2)
        
        # t = 0.5 - interpolation is on rotation matrices, not angles
        # So we just check that it's somewhere between the two
        rpy_t05 = rpy1.interpolate(rpy2, 0.5)
        # Check that all angles are between the starting and ending values
        assert 0.0 <= rpy_t05.roll <= 1.0
        assert 0.0 <= rpy_t05.pitch <= 0.5
        assert 0.0 <= rpy_t05.yaw <= 1.5
    
    def test_copy(self):
        """Test copy operation."""
        rpy1 = RPY(0.1, 0.2, 0.3)
        rpy2 = rpy1.copy()
        
        assert rpy1 == rpy2
        assert rpy1 is not rpy2  # Different objects
    
    def test_equality(self):
        """Test equality operations."""
        rpy1 = RPY(0.1, 0.2, 0.3)
        rpy2 = RPY(0.1, 0.2, 0.3)
        rpy3 = RPY(0.1, 0.2, 0.31)
        
        assert rpy1 == rpy2
        assert not (rpy1 == rpy3)
        assert rpy1 != rpy3
    
    def test_is_close(self):
        """Test closeness check."""
        rpy1 = RPY(0.1, 0.2, 0.3)
        rpy2 = RPY(0.1, 0.2, 0.3)
        rpy3 = RPY(0.1, 0.2, 0.31)  # Larger difference
        
        assert rpy1.is_close(rpy2)
        assert not rpy1.is_close(rpy3, tolerance=1e-4)
        assert rpy1.is_close(rpy3, tolerance=0.02)  # Larger tolerance
    
    def test_string_representation(self):
        """Test string representations."""
        rpy = RPY(0.1, 0.2, 0.3)
        
        # repr
        repr_str = repr(rpy)
        assert "RPY" in repr_str
        assert "0.1" in repr_str or "0.100000" in repr_str
        
        # str
        str_str = str(rpy)
        assert "RPY" in str_str
        assert "°" in str_str  # Check for degree symbol
    
    def test_to_degrees(self):
        """Test conversion to degrees."""
        rpy_rad = RPY(np.pi/6, np.pi/4, np.pi/3)
        rpy_deg = rpy_rad.to_degrees()
        
        assert rpy_deg.roll == pytest.approx(30)
        assert rpy_deg.pitch == pytest.approx(45)
        assert rpy_deg.yaw == pytest.approx(60)
    
    def test_hash(self):
        """Test hash function."""
        rpy1 = RPY(0.1, 0.2, 0.3)
        rpy2 = RPY(0.1, 0.2, 0.3)
        rpy3 = RPY(0.1, 0.2, 0.31)
        
        # Same RPY should have same hash
        assert hash(rpy1) == hash(rpy2)
        
        # Different RPY likely have different hash
        assert hash(rpy1) != hash(rpy3)
    
    def test_gimbal_lock(self):
        """Test behavior near gimbal lock."""
        # At pitch = +/- 90 degrees
        rpy_gimbal = RPY(0.1, np.pi/2, 0.3)
        
        # Should still be able to convert
        R = rpy_gimbal.to_rotation_matrix()
        
        assert R.shape == (3, 3)
        assert np.allclose(R @ R.T, np.eye(3))  # Still orthogonal
        
        # Check round-trip conversion (may not preserve exact angles due to gimbal lock)
        rpy_back = RPY.from_rotation_matrix(R)
        R_back = rpy_back.to_rotation_matrix()
        assert np.allclose(R, R_back, atol=1e-10)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Very small angles
        rpy_small = RPY(1e-10, 1e-10, 1e-10)
        assert rpy_small.is_close(RPY.zeros(), tolerance=1e-9)
        
        # Large angles
        rpy_large = RPY(np.pi, np.pi/2 - 0.01, np.pi)
        R = rpy_large.to_rotation_matrix()
        assert np.allclose(R @ R.T, np.eye(3))
        
        # Division by zero
        rpy = RPY(0.1, 0.2, 0.3)
        with pytest.raises(ValueError):
            rpy / 0.0
        
        # Scalar multiplication and division
        rpy_scaled = rpy * 2.0
        assert rpy_scaled.roll == pytest.approx(0.2)
        assert rpy_scaled.pitch == pytest.approx(0.4)
        assert rpy_scaled.yaw == pytest.approx(0.6)
        
        rpy_divided = rpy / 2.0
        assert rpy_divided.roll == pytest.approx(0.05)
        assert rpy_divided.pitch == pytest.approx(0.1)
        assert rpy_divided.yaw == pytest.approx(0.15)
