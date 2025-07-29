"""Tests for vision geometry primitives."""

import numpy as np
import pytest

from lcvtoolbox.vision.geometry.primitives import (
    Point3D,
    Vector3D,
    RPY,
    Quaternion,
    RotationMatrix,
    TransformationMatrix,
    PoseRPY,
)


class TestPoint3D:
    """Test 3D point operations."""

    def test_create_point(self):
        """Test creating a 3D point."""
        p = Point3D(1.0, 2.0, 3.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_point_operations(self):
        """Test point arithmetic operations."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        
        # Addition
        p3 = p1 + p2
        assert p3.x == 5.0
        assert p3.y == 7.0
        assert p3.z == 9.0
        
        # Subtraction gives another point
        p_diff = p2 - p1
        assert isinstance(p_diff, Point3D)
        assert p_diff.x == 3.0
        assert p_diff.y == 3.0
        assert p_diff.z == 3.0

    def test_distance(self):
        """Test distance calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)
        assert p1.distance_to(p2) == 5.0


class TestVector3D:
    """Test 3D vector operations."""

    def test_create_vector(self):
        """Test creating a 3D vector."""
        v = Vector3D(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_vector_operations(self):
        """Test vector operations."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(0.0, 1.0, 0.0)
        
        # Dot product
        assert v1.dot(v2) == 0.0
        
        # Cross product
        v3 = v1.cross(v2)
        assert v3.x == 0.0
        assert v3.y == 0.0
        assert v3.z == 1.0

    def test_magnitude(self):
        """Test vector magnitude."""
        v = Vector3D(3.0, 4.0, 0.0)
        assert v.magnitude == 5.0

    def test_normalize(self):
        """Test vector normalization."""
        v = Vector3D(3.0, 4.0, 0.0)
        v_norm = v.normalize()
        assert abs(v_norm.magnitude - 1.0) < 1e-10


class TestRPY:
    """Test Roll-Pitch-Yaw representation."""

    def test_create_rpy(self):
        """Test creating RPY angles."""
        rpy = RPY(0.1, 0.2, 0.3)
        assert rpy.roll == 0.1
        assert rpy.pitch == 0.2
        assert rpy.yaw == 0.3

    def test_from_degrees(self):
        """Test creating RPY from degrees."""
        rpy = RPY.from_degrees(30.0, 45.0, 60.0)
        assert abs(rpy.roll - np.radians(30.0)) < 1e-10
        assert abs(rpy.pitch - np.radians(45.0)) < 1e-10
        assert abs(rpy.yaw - np.radians(60.0)) < 1e-10

    def test_to_rotation_matrix(self):
        """Test conversion to rotation matrix."""
        rpy = RPY(0.0, 0.0, 0.0)
        R = rpy.to_rotation_matrix()
        # to_rotation_matrix returns ndarray
        assert isinstance(R, np.ndarray)
        # Identity rotation
        I = np.eye(3)
        np.testing.assert_array_almost_equal(R, I)


class TestQuaternion:
    """Test quaternion operations."""

    def test_create_quaternion(self):
        """Test creating a quaternion."""
        q = Quaternion(1.0, 0.0, 0.0, 0.0)
        assert q.w == 1.0
        assert q.x == 0.0
        assert q.y == 0.0
        assert q.z == 0.0

    def test_from_axis_angle(self):
        """Test creating quaternion from axis-angle."""
        # 90 degree rotation around z-axis
        q = Quaternion.from_axis_angle(np.array([0, 0, 1]), np.pi/2)
        assert abs(q.w - np.sqrt(2)/2) < 1e-10
        assert abs(q.z - np.sqrt(2)/2) < 1e-10

    def test_quaternion_multiplication(self):
        """Test quaternion multiplication."""
        q1 = Quaternion(1.0, 0.0, 0.0, 0.0)  # Identity
        q2 = Quaternion(0.0, 1.0, 0.0, 0.0)  # 180° around x
        q3 = q1 * q2
        assert q3.w == 0.0
        assert q3.x == 1.0


class TestTransformationMatrix:
    """Test transformation matrix operations."""

    def test_create_identity(self):
        """Test creating identity transformation."""
        T = TransformationMatrix()
        I = np.eye(4)
        np.testing.assert_array_almost_equal(T.matrix, I)

    def test_from_translation(self):
        """Test creating transformation from translation."""
        T = TransformationMatrix.from_translation([1.0, 2.0, 3.0])
        assert T.matrix[0, 3] == 1.0
        assert T.matrix[1, 3] == 2.0
        assert T.matrix[2, 3] == 3.0

    def test_transform_point(self):
        """Test transforming a point."""
        T = TransformationMatrix.from_translation([1.0, 2.0, 3.0])
        p = Point3D(1.0, 1.0, 1.0)
        p_transformed = T.transform_point(p)
        assert p_transformed.x == 2.0
        assert p_transformed.y == 3.0
        assert p_transformed.z == 4.0


class TestPoseRPY:
    """Test pose with RPY orientation."""

    def test_create_pose(self):
        """Test creating a pose."""
        position = Point3D(1.0, 2.0, 3.0)
        orientation = RPY(0.1, 0.2, 0.3)
        pose = PoseRPY(position, orientation)
        assert pose.position.x == 1.0
        assert pose.orientation.roll == 0.1

    def test_to_transformation_matrix(self):
        """Test converting pose to transformation matrix."""
        position = Point3D(1.0, 2.0, 3.0)
        orientation = RPY(0.0, 0.0, 0.0)
        pose = PoseRPY(position, orientation)
        T = pose.to_transformation_matrix()
        assert T.matrix[0, 3] == 1.0
        assert T.matrix[1, 3] == 2.0
        assert T.matrix[2, 3] == 3.0
