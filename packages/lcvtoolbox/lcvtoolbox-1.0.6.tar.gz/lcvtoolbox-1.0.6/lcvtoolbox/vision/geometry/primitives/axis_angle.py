from __future__ import annotations

import numpy as np

from .vector import Vector3D
from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rpy import RPY
from .rotation_vector import RotationVector


class AxisAngle:
    """
    Represents a rotation using axis-angle representation.

    The rotation is defined by a unit vector (axis) and a rotation angle in radians
    around that axis. This is the most intuitive representation of 3D rotations.

    Args:
        axis: Rotation axis as Vector3D or numpy array (will be normalized)
        angle: Rotation angle in radians

    Examples:
        >>> # Create a 90° rotation around Z axis
        >>> aa = AxisAngle(Vector3D(0, 0, 1), np.pi/2)
        >>>
        >>> # Create from rotation matrix
        >>> R = RotationMatrix.from_rpy(RPY(0.1, 0.2, 0.3))
        >>> aa = AxisAngle.from_rotation_matrix(R)
        >>>
        >>> # Apply to vector
        >>> v = Vector3D(1, 0, 0)
        >>> v_rotated = aa.apply_to_vector(v)
    """

    __slots__ = ("_axis", "_angle")  # Memory optimization

    def __init__(self, axis: Vector3D | np.ndarray, angle: float) -> None:
        """Initialize with axis and angle."""
        if isinstance(axis, np.ndarray):
            axis = Vector3D.from_numpy(axis)
        elif not isinstance(axis, Vector3D):
            raise TypeError("Axis must be Vector3D or numpy array")
        
        # Normalize axis
        if axis.is_zero:
            # No rotation
            self._axis = Vector3D.unit_x()  # Arbitrary axis
            self._angle = 0.0
        else:
            self._axis = axis.normalize()
            self._angle = float(angle)

    @classmethod
    def identity(cls) -> AxisAngle:
        """Create an identity rotation (no rotation)."""
        return cls(Vector3D.unit_x(), 0.0)

    @classmethod
    def from_rotation_matrix(cls, rotation_matrix: RotationMatrix) -> AxisAngle:
        """Create from a rotation matrix.

        Args:
            rotation_matrix: RotationMatrix instance

        Returns:
            AxisAngle instance
        """
        axis, angle = rotation_matrix.to_axis_angle()
        return cls(Vector3D.from_numpy(axis), angle)

    @classmethod
    def from_quaternion(cls, quaternion: Quaternion) -> AxisAngle:
        """Create from a quaternion.

        Args:
            quaternion: Quaternion instance

        Returns:
            AxisAngle instance
        """
        axis, angle = quaternion.to_axis_angle()
        return cls(Vector3D.from_numpy(axis), angle)

    @classmethod
    def from_rpy(cls, rpy: RPY) -> AxisAngle:
        """Create from RPY angles.

        Args:
            rpy: RPY instance

        Returns:
            AxisAngle instance
        """
        rotation_matrix = RotationMatrix(rpy.to_rotation_matrix())
        return cls.from_rotation_matrix(rotation_matrix)

    @classmethod
    def from_rotation_vector(cls, rotation_vector: RotationVector) -> AxisAngle:
        """Create from a rotation vector.

        Args:
            rotation_vector: RotationVector instance

        Returns:
            AxisAngle instance
        """
        axis, angle = rotation_vector.to_axis_angle()
        return cls(axis, angle)

    @classmethod
    def from_two_vectors(cls, from_vec: Vector3D | np.ndarray, to_vec: Vector3D | np.ndarray) -> AxisAngle:
        """Create rotation that aligns from_vec to to_vec.

        Args:
            from_vec: Source vector (will be normalized)
            to_vec: Target vector (will be normalized)

        Returns:
            AxisAngle instance
        """
        if isinstance(from_vec, np.ndarray):
            from_vec = Vector3D.from_numpy(from_vec)
        if isinstance(to_vec, np.ndarray):
            to_vec = Vector3D.from_numpy(to_vec)
        
        # Normalize vectors
        v1 = from_vec.normalize()
        v2 = to_vec.normalize()
        
        # Check if vectors are parallel
        dot = v1.dot(v2)
        
        if np.abs(dot - 1.0) < 1e-6:
            # Vectors are already aligned
            return cls.identity()
        elif np.abs(dot + 1.0) < 1e-6:
            # Vectors are opposite, need 180 degree rotation
            # Find an orthogonal vector
            if np.abs(v1.x) < 0.9:
                ortho = Vector3D.unit_x()
            else:
                ortho = Vector3D.unit_y()
            
            axis = v1.cross(ortho).normalize()
            return cls(axis, np.pi)
        else:
            # General case
            axis = v1.cross(v2).normalize()
            angle = np.arccos(np.clip(dot, -1, 1))
            return cls(axis, angle)

    @classmethod
    def random(cls, max_angle: float = np.pi) -> AxisAngle:
        """Generate a random axis-angle rotation.

        Args:
            max_angle: Maximum rotation angle in radians

        Returns:
            Random AxisAngle
        """
        axis = Vector3D.random_unit()
        angle = np.random.uniform(0, max_angle)
        return cls(axis, angle)

    @property
    def axis(self) -> Vector3D:
        """Get the rotation axis (unit vector)."""
        return self._axis.copy()

    @property
    def angle(self) -> float:
        """Get the rotation angle in radians."""
        return self._angle

    @property
    def angle_degrees(self) -> float:
        """Get the rotation angle in degrees."""
        return np.rad2deg(self._angle)

    def to_rotation_matrix(self) -> RotationMatrix:
        """Convert to rotation matrix using Rodrigues' formula.

        Returns:
            RotationMatrix instance
        """
        if np.abs(self._angle) < 1e-6:
            return RotationMatrix.identity()
        
        axis = self._axis.numpy
        cos_a = np.cos(self._angle)
        sin_a = np.sin(self._angle)
        
        # Cross product matrix
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        
        # Rodrigues' formula
        R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
        
        return RotationMatrix(R)

    def to_quaternion(self) -> Quaternion:
        """Convert to quaternion representation.

        Returns:
            Quaternion instance
        """
        half_angle = self._angle / 2
        sin_half = np.sin(half_angle)
        
        w = np.cos(half_angle)
        x = self._axis.x * sin_half
        y = self._axis.y * sin_half
        z = self._axis.z * sin_half
        
        return Quaternion(w, x, y, z)

    def to_rpy(self) -> RPY:
        """Convert to RPY angles.

        Returns:
            RPY instance
        """
        rotation_matrix = self.to_rotation_matrix()
        return rotation_matrix.to_rpy()

    def to_rotation_vector(self) -> RotationVector:
        """Convert to rotation vector representation.

        Returns:
            RotationVector instance
        """
        rotation_vector = self._axis * self._angle
        return RotationVector(rotation_vector)

    def apply_to_vector(self, vector: Vector3D | np.ndarray) -> Vector3D | np.ndarray:
        """Apply rotation to a vector using Rodrigues' formula.

        Args:
            vector: Vector to rotate

        Returns:
            Rotated vector (same type as input)
        """
        return_numpy = isinstance(vector, np.ndarray)
        
        if return_numpy:
            vector = Vector3D.from_numpy(vector)
        
        # Use Rodrigues' formula
        if np.abs(self._angle) < 1e-6:
            result = vector.copy()
        else:
            result = vector.rotate_around_axis(self._axis, self._angle)
        
        return result.numpy if return_numpy else result

    def compose(self, other: AxisAngle) -> AxisAngle:
        """Compose this rotation with another.

        Args:
            other: Another AxisAngle

        Returns:
            Composed AxisAngle
        """
        # Convert to rotation matrices for composition
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        R_composed = R1.compose(R2)
        
        return AxisAngle.from_rotation_matrix(R_composed)

    def inverse(self) -> AxisAngle:
        """Get the inverse rotation.

        Returns:
            Inverse AxisAngle
        """
        # Same axis, opposite angle
        return AxisAngle(self._axis, -self._angle)

    def power(self, exponent: float) -> AxisAngle:
        """Raise rotation to a power (fractional rotations).

        Args:
            exponent: Power to raise the rotation to

        Returns:
            New AxisAngle
        """
        return AxisAngle(self._axis, self._angle * exponent)

    def interpolate(self, other: AxisAngle, t: float) -> AxisAngle:
        """Interpolate between rotations.

        Args:
            other: Target rotation
            t: Interpolation parameter [0, 1]

        Returns:
            Interpolated AxisAngle
        """
        # Convert to quaternions for proper SLERP
        q1 = self.to_quaternion()
        q2 = other.to_quaternion()
        q_interp = Quaternion.slerp(q1, q2, t)
        
        return AxisAngle.from_quaternion(q_interp)

    def distance_to(self, other: AxisAngle) -> float:
        """Compute angular distance to another rotation.

        Args:
            other: Another AxisAngle

        Returns:
            Angular distance in radians
        """
        # Use quaternions for accurate distance
        q1 = self.to_quaternion()
        q2 = other.to_quaternion()
        return q1.distance_to(q2)

    def is_close(self, other: AxisAngle, tolerance: float = 1e-6) -> bool:
        """Check if this rotation is close to another.

        Args:
            other: Another AxisAngle
            tolerance: Tolerance for comparison

        Returns:
            True if rotations are close
        """
        # Compare rotation matrices
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        return R1.is_close(R2, tolerance)

    def normalize(self) -> AxisAngle:
        """Normalize the angle to [-π, π] range.

        Returns:
            Normalized AxisAngle
        """
        # Normalize angle
        normalized_angle = np.arctan2(np.sin(self._angle), np.cos(self._angle))
        
        # If angle became negative, flip axis
        if normalized_angle < 0:
            return AxisAngle(-self._axis, -normalized_angle)
        else:
            return AxisAngle(self._axis, normalized_angle)

    def copy(self) -> AxisAngle:
        """Create a copy of this axis-angle."""
        return AxisAngle(self._axis, self._angle)

    def __repr__(self) -> str:
        """String representation."""
        return (f"AxisAngle(axis=[{self._axis.x:.3f}, {self._axis.y:.3f}, "
                f"{self._axis.z:.3f}], angle={self.angle_degrees:.1f}°)")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"AxisAngle({self._axis}, {self.angle_degrees:.1f}°)"

    def __eq__(self, other: object) -> bool:
        """Check equality with another AxisAngle."""
        if not isinstance(other, AxisAngle):
            return NotImplemented
        
        # Check if they represent the same rotation
        # (axis, angle) and (-axis, -angle) are the same
        same_rotation = (self._axis.is_close(other._axis) and 
                        np.abs(self._angle - other._angle) < 1e-6)
        opposite_rotation = (self._axis.is_close(-other._axis) and 
                           np.abs(self._angle + other._angle) < 1e-6)
        
        return same_rotation or opposite_rotation

    def __ne__(self, other: object) -> bool:
        """Check inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function."""
        # Use rotation matrix for consistent hashing
        return hash(self.to_rotation_matrix())
