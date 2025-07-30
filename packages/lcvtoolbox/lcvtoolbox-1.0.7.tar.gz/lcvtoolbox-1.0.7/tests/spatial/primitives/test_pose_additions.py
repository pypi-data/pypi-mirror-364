"""
Test additional methods for PoseRPY and PoseQuaternion classes.
"""

import numpy as np

from .pose_rpy import PoseRPY
from .pose_quaternion import PoseQuaternion
from .point import Point3D
from .rpy import RPY
from .quaternion import Quaternion
from .vector import Vector3D


def test_additional_pose_methods():
    """Test additional methods added to pose classes."""
    
    print("Testing additional pose methods...")
    
    # Test 1: Create PoseRPY from degrees
    pose_rpy_deg = PoseRPY.from_degrees([1, 2, 3], 30, 45, 60)
    expected_rpy = RPY.from_degrees(30, 45, 60)
    assert pose_rpy_deg.orientation.is_close(expected_rpy)
    print("✓ PoseRPY from degrees")
    
    # Test 2: Random pose generation for PoseRPY
    random_rpy = PoseRPY.random(position_range=10.0, angle_range=np.pi/2)
    assert -10 <= random_rpy.x <= 10
    assert -10 <= random_rpy.y <= 10
    assert -10 <= random_rpy.z <= 10
    assert -np.pi/2 <= random_rpy.roll <= np.pi/2
    print("✓ Random PoseRPY generation")
    
    # Test 3: Transform vector
    pose = PoseRPY([0, 0, 0], [0, 0, np.pi/2])  # 90° rotation around Z
    vec = Vector3D(1, 0, 0)
    vec_transformed = pose.transform_vector(vec)
    assert vec_transformed.is_close(Vector3D(0, 1, 0), tolerance=1e-6)
    print("✓ Transform vector")
    
    # Test 4: Transform multiple points
    points = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    pose = PoseRPY([1, 2, 3], [0, 0, 0])  # Pure translation
    points_transformed = pose.transform_points(points)
    expected = points + np.array([1, 2, 3])
    assert np.allclose(points_transformed, expected)
    print("✓ Transform multiple points")
    
    # Test 5: To degrees
    pose_rad = PoseRPY([1, 2, 3], RPY(np.pi/6, np.pi/4, np.pi/3))
    pose_deg = pose_rad.to_degrees()
    assert np.isclose(pose_deg.roll, 30)
    assert np.isclose(pose_deg.pitch, 45)
    assert np.isclose(pose_deg.yaw, 60)
    print("✓ Convert to degrees")
    
    # Test 6: Relative pose
    pose1 = PoseRPY([2, 0, 0], [0, 0, 0])
    pose2 = PoseRPY([3, 1, 0], [0, 0, np.pi/4])
    relative = pose2.relative_to(pose1)
    # pose2 relative to pose1 should be at (1, 1, 0) with 45° rotation
    assert relative.position.is_close(Point3D(1, 1, 0), tolerance=1e-6)
    assert np.isclose(relative.yaw, np.pi/4)
    print("✓ Relative pose")
    
    # Test 7: Matrix multiplication operator
    pose1 = PoseRPY([1, 0, 0], [0, 0, 0])
    pose2 = PoseRPY([0, 1, 0], [0, 0, np.pi/2])
    composed = pose1 @ pose2
    assert isinstance(composed, PoseRPY)
    print("✓ Matrix multiplication operator")
    
    # Test 8: Rotation matrix property
    pose = PoseRPY([0, 0, 0], RPY(0.1, 0.2, 0.3))
    rot_mat = pose.rotation_matrix
    assert rot_mat.matrix.shape == (3, 3)
    print("✓ Rotation matrix property")
    
    # Test 9: Apply to vector
    pose = PoseRPY([0, 0, 0], [0, 0, np.pi/2])
    vec = np.array([1, 0, 0])
    vec_rotated = pose.apply_to_vector(vec)
    assert np.allclose(vec_rotated, [0, 1, 0])
    print("✓ Apply to vector")
    
    # Test 10: PoseQuaternion additional methods
    pose_quat = PoseQuaternion([1, 2, 3], Quaternion.from_rpy(RPY(0, 0, np.pi/2)))
    
    # Transform vector with PoseQuaternion
    vec_transformed_quat = pose_quat.transform_vector(Vector3D(1, 0, 0))
    assert vec_transformed_quat.is_close(Vector3D(0, 1, 0), tolerance=1e-6)
    
    # Relative pose with PoseQuaternion
    pose_quat1 = PoseQuaternion([2, 0, 0], Quaternion.identity())
    pose_quat2 = PoseQuaternion([3, 1, 0], Quaternion.from_rpy(RPY(0, 0, np.pi/4)))
    relative_quat = pose_quat2.relative_to(pose_quat1)
    assert relative_quat.position.is_close(Point3D(1, 1, 0), tolerance=1e-6)
    
    # Matrix multiplication for PoseQuaternion
    composed_quat = pose_quat1 @ pose_quat2
    assert isinstance(composed_quat, PoseQuaternion)
    
    print("✓ PoseQuaternion additional methods")
    
    # Test 11: Consistency between PoseRPY and PoseQuaternion methods
    pose_rpy = PoseRPY([1, 2, 3], RPY(0.1, 0.2, 0.3))
    pose_quat = pose_rpy.to_pose_quaternion()
    
    # Both should give same rotation matrix
    assert np.allclose(pose_rpy.rotation_matrix.matrix, 
                      pose_quat.rotation_matrix.matrix)
    
    # Both should transform vectors the same way
    test_vec = Vector3D(1, 1, 1)
    vec_rpy = pose_rpy.transform_vector(test_vec)
    vec_quat = pose_quat.transform_vector(test_vec)
    assert vec_rpy.is_close(vec_quat, tolerance=1e-6)
    
    print("✓ Consistency between PoseRPY and PoseQuaternion")
    
    print("\nAll additional pose method tests passed! ✓✓✓")
    
    # Demonstrate new features
    print("\n" + "="*50)
    print("New features demonstration:")
    
    # Create pose from degrees
    pose_deg = PoseRPY.from_degrees([0, 0, 0], 45, 30, 60)
    print(f"\nPose from degrees: {pose_deg}")
    
    # Matrix multiplication
    p1 = PoseRPY([1, 0, 0], [0, 0, 0])
    p2 = PoseRPY([0, 1, 0], [0, 0, np.pi/2])
    p3 = p1 @ p2
    print(f"\nPose composition: p1 @ p2 = {p3}")
    
    # Relative pose
    world_pose = PoseRPY([5, 5, 0], [0, 0, np.pi/4])
    object_pose = PoseRPY([6, 6, 0], [0, 0, np.pi/2])
    relative = object_pose.relative_to(world_pose)
    print(f"\nObject relative to world: {relative}")


if __name__ == "__main__":
    test_additional_pose_methods()
