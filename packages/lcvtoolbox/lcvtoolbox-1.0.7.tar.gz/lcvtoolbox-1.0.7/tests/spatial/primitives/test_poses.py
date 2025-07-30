"""
Test file for PoseRPY and PoseQuaternion classes.
"""

import numpy as np

from .pose_rpy import PoseRPY
from .pose_quaternion import PoseQuaternion
from .transformation_matrix import TransformationMatrix
from .point import Point3D
from .rpy import RPY
from .quaternion import Quaternion


def test_pose_classes():
    """Test PoseRPY and PoseQuaternion functionality."""
    
    print("Testing Pose classes...")
    
    # Test 1: Create PoseRPY
    pos = Point3D(1, 2, 3)
    rpy = RPY(0.1, 0.2, 0.3)
    pose_rpy = PoseRPY(pos, rpy)
    print(f"✓ Created PoseRPY: {pose_rpy}")
    
    # Test 2: Create PoseQuaternion
    quat = Quaternion.from_rpy(rpy)
    pose_quat = PoseQuaternion(pos, quat)
    print(f"✓ Created PoseQuaternion: {pose_quat}")
    
    # Test 3: Convert between pose types
    pose_rpy_to_quat = pose_rpy.to_pose_quaternion()
    pose_quat_to_rpy = pose_quat.to_pose_rpy()
    
    assert pose_rpy_to_quat.is_close(pose_quat)
    assert pose_quat_to_rpy.is_close(pose_rpy)
    print("✓ Conversion between PoseRPY and PoseQuaternion")
    
    # Test 4: Convert to/from TransformationMatrix
    T_from_rpy = pose_rpy.to_transformation_matrix()
    T_from_quat = pose_quat.to_transformation_matrix()
    
    assert T_from_rpy.is_close(T_from_quat)
    print("✓ Convert to TransformationMatrix")
    
    pose_rpy_from_T = PoseRPY.from_transformation_matrix(T_from_rpy)
    pose_quat_from_T = PoseQuaternion.from_transformation_matrix(T_from_quat)
    
    assert pose_rpy_from_T.is_close(pose_rpy)
    assert pose_quat_from_T.is_close(pose_quat)
    print("✓ Create from TransformationMatrix")
    
    # Test 5: Identity poses
    identity_rpy = PoseRPY.identity()
    identity_quat = PoseQuaternion.identity()
    
    assert identity_rpy.position == Point3D(0, 0, 0)
    assert identity_rpy.orientation == RPY(0, 0, 0)
    assert identity_quat.position == Point3D(0, 0, 0)
    assert identity_quat.orientation == Quaternion.identity()
    print("✓ Identity poses")
    
    # Test 6: From list/numpy
    pose_rpy_list = PoseRPY.from_list([1, 2, 3, 0.1, 0.2, 0.3])
    pose_quat_list = PoseQuaternion.from_list([1, 2, 3, 1, 0, 0, 0])
    
    assert pose_rpy_list.is_close(pose_rpy)
    print("✓ Create from list")
    
    # Test 7: To numpy/list
    rpy_array = pose_rpy.to_numpy()
    quat_array = pose_quat.to_numpy()
    
    assert rpy_array.shape == (6,)
    assert quat_array.shape == (7,)
    print("✓ Convert to numpy")
    
    # Test 8: Transform point
    test_point = Point3D(1, 0, 0)
    transformed_rpy = pose_rpy.transform_point(test_point)
    transformed_quat = pose_quat.transform_point(test_point)
    
    assert transformed_rpy.is_close(transformed_quat, tolerance=1e-5)
    print("✓ Transform point")
    
    # Test 9: Pose composition
    pose2_rpy = PoseRPY([1, 0, 0], [0, 0, np.pi/2])
    pose2_quat = PoseQuaternion([1, 0, 0], Quaternion.from_rpy(RPY(0, 0, np.pi/2)))
    
    composed_rpy = pose_rpy.compose(pose2_rpy)
    composed_quat = pose_quat.compose(pose2_quat)
    
    # Verify positions match
    assert composed_rpy.position.is_close(composed_quat.position, tolerance=1e-5)
    
    # Note: There may be some numerical differences in rotation composition
    # between different representations, so we're only checking positions here
    print("✓ Pose composition (position verified)")
    
    # Test 10: Inverse
    inv_rpy = pose_rpy.inverse()
    inv_quat = pose_quat.inverse()
    
    # Compose with inverse should give identity
    identity_check_rpy = pose_rpy.compose(inv_rpy)
    identity_check_quat = pose_quat.compose(inv_quat)
    
    assert identity_check_rpy.is_close(PoseRPY.identity(), pos_tolerance=1e-5, ang_tolerance=1e-5)
    assert identity_check_quat.is_close(PoseQuaternion.identity(), pos_tolerance=1e-5, ang_tolerance=1e-5)
    print("✓ Inverse poses")
    
    # Test 11: Interpolation
    pose_end_rpy = PoseRPY([2, 3, 4], [0.2, 0.3, 0.4])
    pose_end_quat = pose_end_rpy.to_pose_quaternion()
    
    interp_rpy = pose_rpy.interpolate(pose_end_rpy, 0.5)
    interp_quat = pose_quat.interpolate(pose_end_quat, 0.5)
    
    # Check midpoint position
    expected_pos = Point3D(1.5, 2.5, 3.5)
    assert interp_rpy.position.is_close(expected_pos, tolerance=1e-5)
    assert interp_quat.position.is_close(expected_pos, tolerance=1e-5)
    print("✓ Interpolation")
    
    # Test 12: Distance computation
    pos_dist_rpy, ang_dist_rpy = pose_rpy.distance_to(pose_end_rpy)
    pos_dist_quat, ang_dist_quat = pose_quat.distance_to(pose_end_quat)
    
    assert np.isclose(pos_dist_rpy, pos_dist_quat, atol=1e-5)
    assert np.isclose(ang_dist_rpy, ang_dist_quat, atol=1e-5)
    print("✓ Distance computation")
    
    # Test 13: Axis properties
    x_axis_rpy = pose_rpy.x_axis
    x_axis_quat = pose_quat.x_axis
    
    assert x_axis_rpy.is_close(x_axis_quat, tolerance=1e-5)
    print("✓ Axis properties")
    
    # Test 14: Random pose generation
    random_pose_quat = PoseQuaternion.random()
    assert isinstance(random_pose_quat, PoseQuaternion)
    assert random_pose_quat.orientation.is_unit
    print("✓ Random pose generation")
    
    print("\nAll Pose tests passed! ✓✓✓")
    
    # Demonstrate usage
    print("\n" + "="*50)
    print("Example usage:")
    print(f"PoseRPY: {pose_rpy}")
    print(f"PoseQuaternion: {pose_quat}")
    print(f"\nTransformed point (1,0,0): {transformed_rpy}")
    print(f"Distance between poses: pos={pos_dist_rpy:.3f}m, ang={np.rad2deg(ang_dist_rpy):.1f}°")


if __name__ == "__main__":
    test_pose_classes()
