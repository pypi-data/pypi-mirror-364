"""
Comprehensive test file to verify that all rotation conversions produce consistent results.
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


def matrices_equal(R1: np.ndarray, R2: np.ndarray, tolerance: float = 1e-6) -> bool:
    """Check if two rotation matrices are equal within tolerance."""
    return np.allclose(R1, R2, atol=tolerance)


def test_conversion_consistency():
    """Test that all conversions produce consistent rotation matrices."""
    
    # Start with a non-trivial rotation
    initial_rpy = RPY(roll=0.1, pitch=0.2, yaw=0.3)
    reference_matrix = initial_rpy.to_rotation_matrix()
    
    print(f"Testing conversions starting from RPY: {initial_rpy}")
    print(f"Reference rotation matrix:\n{reference_matrix}\n")
    
    # Test all conversion paths
    conversions_tested = 0
    errors = []
    
    # From RPY to all others and back
    print("Testing RPY conversions...")
    representations = {
        "RotationMatrix": RotationMatrix.from_rpy(initial_rpy),
        "Quaternion": Quaternion.from_rpy(initial_rpy),
        "RotationVector": RotationVector.from_rpy(initial_rpy),
        "AxisAngle": AxisAngle.from_rpy(initial_rpy),
        "TwoVectors": TwoVectors.from_rpy(initial_rpy),
        "EulerAngles": EulerAngles.from_rpy(initial_rpy)
    }
    
    # Verify each representation produces the same rotation matrix
    for name, rep in representations.items():
        if isinstance(rep, RotationMatrix):
            matrix = rep.matrix
        else:
            matrix = rep.to_rotation_matrix().matrix
        if matrices_equal(reference_matrix, matrix):
            print(f"✓ RPY -> {name} -> RotationMatrix: PASS")
            conversions_tested += 1
        else:
            error_msg = f"✗ RPY -> {name} -> RotationMatrix: FAIL"
            print(error_msg)
            errors.append(error_msg)
    
    # Test round-trip conversions (A -> B -> A)
    print("\nTesting round-trip conversions...")
    
    # RPY round trips
    for name, rep in representations.items():
        if hasattr(rep, 'to_rpy'):
            rpy_back = rep.to_rpy()
            if initial_rpy.is_close(rpy_back, tolerance=1e-5):
                print(f"✓ RPY -> {name} -> RPY: PASS")
                conversions_tested += 1
            else:
                error_msg = f"✗ RPY -> {name} -> RPY: FAIL"
                print(error_msg)
                errors.append(error_msg)
    
    # Quaternion round trips
    initial_quat = Quaternion.from_rpy(initial_rpy)
    quat_conversions = {
        "RotationMatrix": lambda q: Quaternion.from_rotation_matrix(q.to_rotation_matrix()),
        "RotationVector": lambda q: RotationVector.from_quaternion(q).to_quaternion(),
        "AxisAngle": lambda q: AxisAngle.from_quaternion(q).to_quaternion(),
        "TwoVectors": lambda q: TwoVectors.from_quaternion(q).to_quaternion(),
        "EulerAngles": lambda q: EulerAngles.from_quaternion(q).to_quaternion()
    }
    
    for name, conversion in quat_conversions.items():
        quat_back = conversion(initial_quat)
        if initial_quat.is_close(quat_back):
            print(f"✓ Quaternion -> {name} -> Quaternion: PASS")
            conversions_tested += 1
        else:
            error_msg = f"✗ Quaternion -> {name} -> Quaternion: FAIL"
            print(error_msg)
            errors.append(error_msg)
    
    # Test vector rotation consistency
    print("\nTesting vector rotation consistency...")
    test_vector = Vector3D(1, 2, 3)
    reference_rotated = RotationMatrix(initial_rpy.to_rotation_matrix()).apply_to_vector(test_vector.numpy)
    
    for name, rep in representations.items():
        if hasattr(rep, 'apply_to_vector'):
            rotated = rep.apply_to_vector(test_vector)
            if isinstance(rotated, Vector3D):
                rotated = rotated.numpy
            
            if np.allclose(reference_rotated, rotated, atol=1e-6):
                print(f"✓ {name}.apply_to_vector(): PASS")
                conversions_tested += 1
            else:
                error_msg = f"✗ {name}.apply_to_vector(): FAIL"
                print(error_msg)
                errors.append(error_msg)
    
    # Test special cases
    print("\nTesting special cases...")
    
    # Identity rotation
    identity_rpy = RPY(0, 0, 0)
    identity_matrix = np.eye(3)
    
    identity_tests = {
        "RotationMatrix": RotationMatrix.identity().matrix,
        "Quaternion": Quaternion.identity().to_rotation_matrix().matrix,
        "RotationVector": RotationVector.identity().to_rotation_matrix().matrix,
        "AxisAngle": AxisAngle.identity().to_rotation_matrix().matrix,
        "TwoVectors": TwoVectors.identity().to_rotation_matrix().matrix,
        "EulerAngles": EulerAngles.identity().to_rotation_matrix().matrix
    }
    
    for name, matrix in identity_tests.items():
        if matrices_equal(identity_matrix, matrix):
            print(f"✓ {name}.identity(): PASS")
            conversions_tested += 1
        else:
            error_msg = f"✗ {name}.identity(): FAIL"
            print(error_msg)
            errors.append(error_msg)
    
    # Test 180-degree rotation (challenging case)
    print("\nTesting 180-degree rotation...")
    axis_180 = Vector3D(0, 0, 1)
    angle_180 = np.pi
    aa_180 = AxisAngle(axis_180, angle_180)
    ref_matrix_180 = aa_180.to_rotation_matrix().matrix
    
    # Convert through different paths
    quat_180 = aa_180.to_quaternion()
    rv_180 = aa_180.to_rotation_vector()
    
    conversions_180 = {
        "AxisAngle -> Quaternion -> RotationMatrix": quat_180.to_rotation_matrix().matrix,
        "AxisAngle -> RotationVector -> RotationMatrix": rv_180.to_rotation_matrix().matrix,
        "AxisAngle -> RPY -> RotationMatrix": RotationMatrix(aa_180.to_rpy().to_rotation_matrix()).matrix
    }
    
    for name, matrix in conversions_180.items():
        if matrices_equal(ref_matrix_180, matrix):
            print(f"✓ {name}: PASS")
            conversions_tested += 1
        else:
            error_msg = f"✗ {name}: FAIL"
            print(error_msg)
            errors.append(error_msg)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Total conversions tested: {conversions_tested}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nFailed conversions:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\nAll conversions passed! ✓")
    
    return len(errors) == 0


def test_euler_angles_conventions():
    """Test different Euler angle conventions."""
    print("\n" + "="*50)
    print("Testing Euler angle conventions...")
    
    # Test rotation
    test_rotation = RotationMatrix.from_rpy(RPY(0.1, 0.2, 0.3))
    
    conventions = ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX", "XYX", "YZY", "ZXZ"]
    
    for convention in conventions:
        # Convert to Euler angles and back
        euler = EulerAngles.from_rotation_matrix(test_rotation, convention)
        matrix_back = euler.to_rotation_matrix()
        
        if test_rotation.is_close(matrix_back, tolerance=1e-5):
            print(f"✓ Convention {convention}: PASS")
        else:
            print(f"✗ Convention {convention}: FAIL")


def test_two_vectors_special_cases():
    """Test TwoVectors with special cases."""
    print("\n" + "="*50)
    print("Testing TwoVectors special cases...")
    
    # Parallel vectors (no rotation)
    v1 = Vector3D(1, 0, 0)
    v2 = Vector3D(2, 0, 0)  # Same direction, different magnitude
    tv_parallel = TwoVectors(v1, v2)
    
    if np.abs(tv_parallel.angle) < 1e-6:
        print("✓ Parallel vectors: PASS")
    else:
        print("✗ Parallel vectors: FAIL")
    
    # Opposite vectors (180° rotation)
    v3 = Vector3D(1, 0, 0)
    v4 = Vector3D(-1, 0, 0)
    tv_opposite = TwoVectors(v3, v4)
    
    if np.abs(tv_opposite.angle - np.pi) < 1e-6:
        print("✓ Opposite vectors: PASS")
    else:
        print("✗ Opposite vectors: FAIL")
    
    # Perpendicular vectors (90° rotation)
    v5 = Vector3D(1, 0, 0)
    v6 = Vector3D(0, 1, 0)
    tv_perp = TwoVectors(v5, v6)
    
    if np.abs(tv_perp.angle - np.pi/2) < 1e-6:
        print("✓ Perpendicular vectors: PASS")
    else:
        print("✗ Perpendicular vectors: FAIL")


if __name__ == "__main__":
    print("Running comprehensive rotation conversion tests...\n")
    
    # Run main conversion tests
    all_passed = test_conversion_consistency()
    
    # Run additional tests
    test_euler_angles_conventions()
    test_two_vectors_special_cases()
    
    print("\n" + "="*50)
    if all_passed:
        print("ALL TESTS PASSED! ✓✓✓")
    else:
        print("Some tests failed. Please check the output above.")
