"""
Test file for TransformationMatrix class.
"""

import numpy as np

from .transformation_matrix import TransformationMatrix
from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rpy import RPY
from .point import Point3D
from .vector import Vector3D


def test_transformation_matrix():
    """Test TransformationMatrix functionality."""
    
    print("Testing TransformationMatrix class...")
    
    # Test 1: Identity transformation
    T_identity = TransformationMatrix.identity()
    assert np.allclose(T_identity.matrix, np.eye(4))
    print("✓ Identity transformation")
    
    # Test 2: Create from rotation and translation
    rpy = RPY(0.1, 0.2, 0.3)
    point = Point3D(1, 2, 3)
    T1 = TransformationMatrix.from_rotation_translation(rpy, point)
    
    # Verify decomposition
    pos, quat = T1.to_position_quaternion()
    assert pos.is_close(point)
    print("✓ Create from rotation and translation")
    
    # Test 3: Create from point and RPY
    T2 = TransformationMatrix.from_point_rpy(point, rpy)
    assert T1.is_close(T2)
    print("✓ Create from point and RPY")
    
    # Test 4: Transform point
    p = Point3D(1, 0, 0)
    p_transformed = T1.transform_point(p)
    print(f"✓ Transform point: {p} -> {p_transformed}")
    
    # Test 5: Transform vector (no translation)
    v = Vector3D(1, 0, 0)
    v_transformed = T1.transform_vector(v)
    print(f"✓ Transform vector: {v} -> {v_transformed}")
    
    # Test 6: Composition of transformations
    T3 = TransformationMatrix.from_translation([1, 0, 0])
    T4 = TransformationMatrix.from_rotation(RPY(0, 0, np.pi/2))
    T_composed = T3 @ T4  # First translate, then rotate
    
    # Test the composed transformation
    p_test = Point3D(0, 0, 0)
    p_result = T_composed.transform_point(p_test)
    # Should be at (1, 0, 0) after composition
    assert p_result.is_close(Point3D(1, 0, 0), tolerance=1e-6)
    print("✓ Transformation composition")
    
    # Test 7: Inverse transformation
    T_inv = T1.inverse()
    T_identity_check = T1 @ T_inv
    assert np.allclose(T_identity_check.matrix, np.eye(4))
    print("✓ Inverse transformation")
    
    # Test 8: Frame transformations
    # Create coordinate frames
    T_world_to_A = TransformationMatrix.from_point_rpy(Point3D(1, 0, 0), RPY(0, 0, 0))
    T_A_to_B = TransformationMatrix.from_point_rpy(Point3D(1, 0, 0), RPY(0, 0, np.pi/2))
    
    # Chain transformations
    T_world_to_B = T_world_to_A @ T_A_to_B
    
    # Verify result
    p_origin = Point3D(0, 0, 0)
    p_in_B = T_world_to_B.transform_point(p_origin)
    assert p_in_B.is_close(Point3D(2, 0, 0), tolerance=1e-6)
    print("✓ Frame transformations")
    
    # Test 9: Denavit-Hartenberg parameters
    T_dh = TransformationMatrix.from_dh_parameters(a=1, alpha=0, d=0, theta=np.pi/2)
    # This should be a 90-degree rotation about Z with translation along X
    print("✓ Denavit-Hartenberg parameters")
    
    # Test 10: Interpolation
    T_start = TransformationMatrix.identity()
    T_end = TransformationMatrix.from_point_rpy(Point3D(1, 0, 0), RPY(0, 0, np.pi/2))
    T_mid = T_start.interpolate(T_end, 0.5)
    
    pos_mid = T_mid.position
    # Should be halfway between start and end positions
    assert pos_mid.is_close(Point3D(0.5, 0, 0), tolerance=1e-6)
    print("✓ Interpolation")
    
    # Test 11: Transform multiple points
    points = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    points_transformed = T1.transform_points(points)
    assert points_transformed.shape == (3, 3)
    print("✓ Transform multiple points")
    
    # Test 12: Axis properties
    T_rot = TransformationMatrix.from_rotation(RPY(0, 0, np.pi/2))
    x_axis = T_rot.x_axis  # Should point in Y direction after 90° Z rotation
    y_axis = T_rot.y_axis  # Should point in -X direction
    assert x_axis.is_close(Vector3D(0, 1, 0), tolerance=1e-6)
    assert y_axis.is_close(Vector3D(-1, 0, 0), tolerance=1e-6)
    print("✓ Axis properties")
    
    print("\nAll TransformationMatrix tests passed! ✓✓✓")
    
    # Demonstrate usage
    print("\n" + "="*50)
    print("Example usage:")
    print(f"T1 = {T1}")
    print(f"\nDecomposed: position={T1.position}, rpy={T1.rotation_matrix.to_rpy()}")


if __name__ == "__main__":
    test_transformation_matrix()
