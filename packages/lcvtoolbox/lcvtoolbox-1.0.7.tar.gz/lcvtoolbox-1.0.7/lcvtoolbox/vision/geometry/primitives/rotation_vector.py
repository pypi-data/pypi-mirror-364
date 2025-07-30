from __future__ import annotations

import numpy as np

from .vector import Vector3D
from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rpy import RPY


class RotationVector:
    """
    Represents a rotation using a rotation vector (axis-angle encoded as a vector).

    The rotation vector is a 3D vector where the direction represents the rotation
    axis and the magnitude represents the rotation angle in radians. This is also
    known as the exponential coordinates of rotation or the Rodrigues vector.

    Args:
        vector: Vector3D or numpy array representing the rotation vector

    Examples:
        >>> # Create from components
        >>> rv = RotationVector(Vector3D(0, 0, np.pi/2))  # 90° rotation around Z
        >>>
        >>> # Create from axis and angle
        >>> axis = Vector3D(0, 0, 1)
        >>> angle = np.pi / 2
        >>> rv = RotationVector.from_axis_angle(axis, angle)
        >>>
        >>> # Convert to rotation matrix
        >>> R = rv.to_rotation_matrix()
    """

    __slots__ = ("_vector",)  # Memory optimization

    def __init__(self, vector: Vector3D | np.ndarray) -> None:
        """Initialize with a rotation vector."""
        if isinstance(vector, Vector3D):
            self._vector = vector.copy()
        elif isinstance(vector, np.ndarray):
            if len(vector) != 3:
                raise ValueError("Vector must have 3 components")
            self._vector = Vector3D.from_numpy(vector)
        else:
            raise TypeError("Vector must be Vector3D or numpy array")

    @classmethod
    def identity(cls) -> RotationVector:
        """Create an identity rotation (zero rotation)."""
        return cls(Vector3D.zeros())

    @classmethod
    def from_axis_angle(cls, axis: Vector3D | np.ndarray, angle: float) -> RotationVector:
        """Create from axis-angle representation.

        Args:
            axis: Rotation axis (will be normalized)
            angle: Rotation angle in radians

        Returns:
            RotationVector instance
        """
        if isinstance(axis, np.ndarray):
            axis = Vector3D.from_numpy(axis)
        
        if axis.is_zero:
            return cls.identity()
        
        # Rotation vector = axis * angle
        axis_normalized = axis.normalize()
        rotation_vector = axis_normalized * angle
        
        return cls(rotation_vector)

    @classmethod
    def from_rotation_matrix(cls, rotation_matrix: RotationMatrix) -> RotationVector:
        """Create from a rotation matrix using the logarithm map.

        Args:
            rotation_matrix: RotationMatrix instance

        Returns:
            RotationVector instance
        """
        matrix = rotation_matrix.matrix
        
        # Calculate rotation angle
        trace = np.trace(matrix)
        cos_angle = (trace - 1) / 2
        cos_angle = np.clip(cos_angle, -1, 1)
        angle = np.arccos(cos_angle)
        
        if np.abs(angle) < 1e-6:
            # Small angle approximation
            # For small angles, (R - R^T) / 2 ≈ [ω]×
            omega_cross = (matrix - matrix.T) / 2
            vector = Vector3D(omega_cross[2, 1], omega_cross[0, 2], omega_cross[1, 0])
            return cls(vector)
        elif np.abs(angle - np.pi) < 1e-6:
            # Near 180 degrees - special case
            # Find the largest diagonal element
            diag = np.diag(matrix)
            idx = np.argmax(diag)
            
            # Extract axis
            axis = np.zeros(3)
            axis[idx] = np.sqrt((diag[idx] + 1) / 2)
            
            for i in range(3):
                if i != idx:
                    axis[i] = matrix[idx, i] / (2 * axis[idx])
            
            # Normalize and scale by angle
            axis = axis / np.linalg.norm(axis)
            vector = Vector3D.from_numpy(axis * angle)
            return cls(vector)
        else:
            # General case
            axis = np.array([
                matrix[2, 1] - matrix[1, 2],
                matrix[0, 2] - matrix[2, 0],
                matrix[1, 0] - matrix[0, 1]
            ])
            axis = axis / (2 * np.sin(angle))
            
            vector = Vector3D.from_numpy(axis * angle)
            return cls(vector)

    @classmethod
    def from_quaternion(cls, quaternion: Quaternion) -> RotationVector:
        """Create from a quaternion.

        Args:
            quaternion: Quaternion instance

        Returns:
            RotationVector instance
        """
        # Convert quaternion to axis-angle
        axis, angle = quaternion.to_axis_angle()
        return cls.from_axis_angle(Vector3D.from_numpy(axis), angle)

    @classmethod
    def from_rpy(cls, rpy: RPY) -> RotationVector:
        """Create from RPY angles.

        Args:
            rpy: RPY instance

        Returns:
            RotationVector instance
        """
        # Convert RPY to rotation matrix first
        rotation_matrix = RotationMatrix(rpy.to_rotation_matrix())
        return cls.from_rotation_matrix(rotation_matrix)

    @classmethod
    def random(cls, max_angle: float = np.pi) -> RotationVector:
        """Generate a random rotation vector.

        Args:
            max_angle: Maximum rotation angle in radians

        Returns:
            Random RotationVector
        """
        # Random axis
        axis = Vector3D.random_unit()
        
        # Random angle
        angle = np.random.uniform(0, max_angle)
        
        return cls.from_axis_angle(axis, angle)

    @property
    def vector(self) -> Vector3D:
        """Get the rotation vector."""
        return self._vector.copy()

    @property
    def numpy(self) -> np.ndarray:
        """Get the rotation vector as numpy array."""
        return self._vector.numpy

    @property
    def angle(self) -> float:
        """Get the rotation angle in radians."""
        return self._vector.magnitude

    @property
    def axis(self) -> Vector3D:
        """Get the rotation axis as a unit vector.

        Returns:
            Unit vector representing rotation axis, or arbitrary axis if angle is zero
        """
        angle = self.angle
        if angle < 1e-6:
            # No rotation, return arbitrary axis
            return Vector3D.unit_x()
        
        return self._vector.normalize()

    def to_axis_angle(self) -> tuple[Vector3D, float]:
        """Convert to axis-angle representation.

        Returns:
            Tuple of (axis, angle) where axis is a unit vector
        """
        return self.axis, self.angle

    def to_rotation_matrix(self) -> RotationMatrix:
        """Convert to rotation matrix using Rodrigues' formula.

        Returns:
            RotationMatrix instance
        """
        angle = self.angle
        
        if angle < 1e-6:
            # Identity rotation
            return RotationMatrix.identity()
        
        axis = self.axis.numpy
        
        # Rodrigues' formula
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Cross product matrix
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        
        # R = I + sin(θ)K + (1-cos(θ))K²
        R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
        
        return RotationMatrix(R)

    def to_quaternion(self) -> Quaternion:
        """Convert to quaternion representation.

        Returns:
            Quaternion instance
        """
        angle = self.angle
        
        if angle < 1e-6:
            # Identity quaternion
            return Quaternion.identity()
        
        axis = self.axis
        half_angle = angle / 2
        sin_half = np.sin(half_angle)
        
        w = np.cos(half_angle)
        x = axis.x * sin_half
        y = axis.y * sin_half
        z = axis.z * sin_half
        
        return Quaternion(w, x, y, z)

    def to_rpy(self) -> RPY:
        """Convert to RPY angles.

        Returns:
            RPY instance
        """
        # Convert to rotation matrix first
        rotation_matrix = self.to_rotation_matrix()
        return rotation_matrix.to_rpy()

    def apply_to_vector(self, vector: Vector3D | np.ndarray) -> Vector3D | np.ndarray:
        """Apply rotation to a vector.

        Args:
            vector: Vector3D or numpy array to rotate

        Returns:
            Rotated vector (same type as input)
        """
        return_numpy = isinstance(vector, np.ndarray)
        
        if return_numpy:
            vector = Vector3D.from_numpy(vector)
        
        # Use Rodrigues' formula directly on the vector
        angle = self.angle
        
        if angle < 1e-6:
            # No rotation
            result = vector.copy()
        else:
            axis = self.axis
            result = vector.rotate_around_axis(axis, angle)
        
        return result.numpy if return_numpy else result

    def compose(self, other: RotationVector) -> RotationVector:
        """Compose this rotation with another.

        The resulting rotation is equivalent to applying this rotation
        followed by the other rotation.

        Args:
            other: Another RotationVector

        Returns:
            Composed RotationVector
        """
        # Convert to rotation matrices for composition
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        R_composed = R1.compose(R2)
        
        return RotationVector.from_rotation_matrix(R_composed)

    def inverse(self) -> RotationVector:
        """Get the inverse rotation.

        Returns:
            Inverse RotationVector
        """
        # Inverse rotation has same axis but opposite angle
        return RotationVector(-self._vector)

    def power(self, exponent: float) -> RotationVector:
        """Raise rotation to a power (fractional rotations).

        Args:
            exponent: Power to raise the rotation to

        Returns:
            New RotationVector
        """
        # Scale the rotation vector by the exponent
        return RotationVector(self._vector * exponent)

    def interpolate(self, other: RotationVector, t: float) -> RotationVector:
        """Interpolate between rotations.

        Uses the exponential map for proper interpolation in SO(3).

        Args:
            other: Target rotation
            t: Interpolation parameter [0, 1]

        Returns:
            Interpolated RotationVector
        """
        # For rotation vectors, we can interpolate in the tangent space
        # This is valid for small rotations
        if self.angle < 0.1 and other.angle < 0.1:
            # Linear interpolation for small angles
            interpolated_vector = self._vector.lerp(other._vector, t)
            return RotationVector(interpolated_vector)
        
        # For larger rotations, convert to quaternions for SLERP
        q1 = self.to_quaternion()
        q2 = other.to_quaternion()
        q_interp = Quaternion.slerp(q1, q2, t)
        
        return RotationVector.from_quaternion(q_interp)

    def distance_to(self, other: RotationVector) -> float:
        """Compute angular distance to another rotation.

        Args:
            other: Another RotationVector

        Returns:
            Angular distance in radians
        """
        # Compute relative rotation
        relative = self.inverse().compose(other)
        return relative.angle

    def is_close(self, other: RotationVector, tolerance: float = 1e-6) -> bool:
        """Check if this rotation is close to another.

        Args:
            other: Another RotationVector
            tolerance: Tolerance for comparison

        Returns:
            True if rotations are close
        """
        # Compare the rotation matrices
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        return R1.is_close(R2, tolerance)

    def normalize_angle(self) -> RotationVector:
        """Normalize the rotation angle to [-π, π].

        Returns:
            Normalized RotationVector
        """
        angle = self.angle
        
        if angle == 0:
            return self.copy()
        
        # Normalize angle to [-π, π]
        normalized_angle = np.arctan2(np.sin(angle), np.cos(angle))
        
        # If angle changed sign, we need to flip the axis
        if np.sign(normalized_angle) != np.sign(angle) and np.abs(angle) > np.pi:
            axis = -self.axis
        else:
            axis = self.axis
        
        return RotationVector.from_axis_angle(axis, np.abs(normalized_angle))

    def copy(self) -> RotationVector:
        """Create a copy of this rotation vector."""
        return RotationVector(self._vector.copy())

    def __repr__(self) -> str:
        """String representation."""
        axis = self.axis
        angle_deg = np.rad2deg(self.angle)
        return (f"RotationVector(axis=[{axis.x:.3f}, {axis.y:.3f}, {axis.z:.3f}], "
                f"angle={angle_deg:.1f}°)")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"RotationVector({self._vector})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another RotationVector."""
        if not isinstance(other, RotationVector):
            return NotImplemented
        return self._vector == other._vector

    def __ne__(self, other: object) -> bool:
        """Check inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function."""
        return hash(self._vector)

    def __mul__(self, scalar: float) -> RotationVector:
        """Multiply by a scalar (scale the rotation)."""
        if isinstance(scalar, (int, float)):
            return RotationVector(self._vector * scalar)
        return NotImplemented

    def __truediv__(self, scalar: float) -> RotationVector:
        """Divide by a scalar."""
        if isinstance(scalar, (int, float)):
            return RotationVector(self._vector / scalar)
        return NotImplemented

    def __neg__(self) -> RotationVector:
        """Negate the rotation (inverse)."""
        return RotationVector(-self._vector)

    def __abs__(self) -> float:
        """Get the rotation angle."""
        return self.angle
