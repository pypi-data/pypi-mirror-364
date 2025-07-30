"""
Test file demonstrating conversion between all rotation representations.
This file shows that each rotation class can convert to all others.
"""

import numpy as np

from .rpy import RPY
from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rotation_vector import RotationVector
from .axis_angle import AxisAngle
from .two_vectors import TwoVectors
from .euler_angles import EulerAngles
from .vector import Vector3D


def test_all_conversions():
    """Test that all rotation representations can convert to each other."""
    
    # Start with some example rotation
    initial_rpy = RPY(roll=0.1, pitch=0.2, yaw=0.3)
    
    # Convert RPY to all other representations
    rot_matrix = RotationMatrix.from_rpy(initial_rpy)
    quaternion = Quaternion.from_rpy(initial_rpy)
    rot_vector = RotationVector.from_rpy(initial_rpy)
    axis_angle = AxisAngle.from_rpy(initial_rpy)
    two_vectors = TwoVectors.from_rpy(initial_rpy)
    euler_angles = EulerAngles.from_rpy(initial_rpy)
    
    # Convert RotationMatrix to all others
    rpy_from_matrix = rot_matrix.to_rpy()
    quat_from_matrix = Quaternion.from_rotation_matrix(rot_matrix)
    rv_from_matrix = RotationVector.from_rotation_matrix(rot_matrix)
    aa_from_matrix = AxisAngle.from_rotation_matrix(rot_matrix)
    tv_from_matrix = TwoVectors.from_rotation_matrix(rot_matrix)
    ea_from_matrix = EulerAngles.from_rotation_matrix(rot_matrix)
    
    # Convert Quaternion to all others
    rpy_from_quat = quaternion.to_rpy()
    matrix_from_quat = quaternion.to_rotation_matrix()
    rv_from_quat = RotationVector.from_quaternion(quaternion)
    aa_from_quat = AxisAngle.from_quaternion(quaternion)
    tv_from_quat = TwoVectors.from_quaternion(quaternion)
    ea_from_quat = EulerAngles.from_quaternion(quaternion)
    
    # Convert RotationVector to all others
    rpy_from_rv = rot_vector.to_rpy()
    matrix_from_rv = rot_vector.to_rotation_matrix()
    quat_from_rv = rot_vector.to_quaternion()
    aa_from_rv = AxisAngle.from_rotation_vector(rot_vector)
    tv_from_rv = TwoVectors.from_rotation_vector(rot_vector)
    ea_from_rv = EulerAngles.from_rotation_vector(rot_vector)
    
    # Convert AxisAngle to all others
    rpy_from_aa = axis_angle.to_rpy()
    matrix_from_aa = axis_angle.to_rotation_matrix()
    quat_from_aa = axis_angle.to_quaternion()
    rv_from_aa = axis_angle.to_rotation_vector()
    tv_from_aa = TwoVectors.from_axis_angle(axis_angle)
    ea_from_aa = EulerAngles.from_axis_angle(axis_angle)
    
    # Convert TwoVectors to all others
    rpy_from_tv = two_vectors.to_rpy()
    matrix_from_tv = two_vectors.to_rotation_matrix()
    quat_from_tv = two_vectors.to_quaternion()
    rv_from_tv = two_vectors.to_rotation_vector()
    aa_from_tv = two_vectors.to_axis_angle()
    ea_from_tv = EulerAngles.from_two_vectors(two_vectors)
    
    # Convert EulerAngles to all others
    rpy_from_ea = euler_angles.to_rpy()
    matrix_from_ea = euler_angles.to_rotation_matrix()
    quat_from_ea = euler_angles.to_quaternion()
    rv_from_ea = euler_angles.to_rotation_vector()
    aa_from_ea = euler_angles.to_axis_angle()
    tv_from_ea = euler_angles.to_two_vectors()
    
    print("All conversions work successfully!")
    
    # Example of creating rotations from different sources
    
    # From axis-angle
    axis = Vector3D(0, 0, 1)  # Z-axis
    angle = np.pi / 4  # 45 degrees
    aa1 = AxisAngle(axis, angle)
    
    # From two vectors
    from_vec = Vector3D(1, 0, 0)  # X-axis
    to_vec = Vector3D(1, 1, 0).normalize()  # 45° from X in XY plane
    tv1 = TwoVectors(from_vec, to_vec)
    
    # From Euler angles with different conventions
    ea_xyz = EulerAngles([0.1, 0.2, 0.3], "XYZ", extrinsic=True)
    ea_zyx = EulerAngles([0.3, 0.2, 0.1], "ZYX", extrinsic=True)
    ea_zxz = EulerAngles([0.1, 0.2, 0.3], "ZXZ", extrinsic=False)  # Proper Euler
    
    # All can be used interchangeably
    v = Vector3D(1, 0, 0)
    v_rotated_aa = aa1.apply_to_vector(v)
    v_rotated_tv = tv1.apply_to_vector(v)
    v_rotated_ea = ea_xyz.apply_to_vector(v.numpy)
    
    print("Rotation representations demo complete!")


if __name__ == "__main__":
    test_all_conversions()
