from __future__ import annotations

import numpy as np

from .rotation_matrix import RotationMatrix
from .rpy import RPY


class Quaternion:
    """
    Represents a unit quaternion for 3D rotations.

    This class handles quaternions in the form [w, x, y, z] where w is the scalar part
    and (x, y, z) is the vector part. The quaternion is automatically normalized to
    ensure it represents a valid rotation.

    Args:
        w: Scalar component
        x: First vector component
        y: Second vector component
        z: Third vector component

    Examples:
        >>> # Create from components
        >>> q = Quaternion(w=0.707, x=0, y=0, z=0.707)
        >>>
        >>> # Create from RPY angles
        >>> rpy = RPY(roll=0.1, pitch=0.2, yaw=0.3)
        >>> q = Quaternion.from_rpy(rpy)
        >>>
        >>> # Create from rotation matrix
        >>> rot_mat = RotationMatrix.from_rpy(rpy)
        >>> q = Quaternion.from_rotation_matrix(rot_mat)
        >>>
        >>> # Convert to rotation matrix
        >>> R = q.to_rotation_matrix()
    """

    __slots__ = ("_data",)  # Memory optimization

    def __init__(self, w: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Initialize quaternion with given components."""
        self._data = np.array([w, x, y, z], dtype=np.float64)
        self._normalize()

    def _normalize(self) -> None:
        """Normalize the quaternion to unit length."""
        norm = np.linalg.norm(self._data)
        if norm > 0:
            self._data /= norm
        else:
            # Default to identity quaternion
            self._data = np.array([1.0, 0.0, 0.0, 0.0])

    @classmethod
    def identity(cls) -> Quaternion:
        """Create an identity quaternion (no rotation)."""
        return cls(1.0, 0.0, 0.0, 0.0)

    @classmethod
    def from_numpy(cls, array: np.ndarray, scalar_first: bool = True) -> Quaternion:
        """Create quaternion from numpy array.

        Args:
            array: Numpy array with 4 elements
            scalar_first: If True, expects [w, x, y, z], else [x, y, z, w]

        Returns:
            Quaternion instance

        Raises:
            ValueError: If array doesn't have exactly 4 elements
        """
        if len(array) != 4:
            raise ValueError("Array must have exactly 4 elements")

        if scalar_first:
            return cls(float(array[0]), float(array[1]), float(array[2]), float(array[3]))
        else:
            return cls(float(array[3]), float(array[0]), float(array[1]), float(array[2]))

    @classmethod
    def from_tuple(cls, components: tuple[float, float, float, float], scalar_first: bool = True) -> Quaternion:
        """Create quaternion from tuple.

        Args:
            components: Tuple with 4 components
            scalar_first: If True, expects (w, x, y, z), else (x, y, z, w)

        Returns:
            Quaternion instance
        """
        return cls.from_numpy(np.array(components), scalar_first)

    @classmethod
    def from_rpy(cls, rpy: RPY) -> Quaternion:
        """Create quaternion from RPY angles.

        Args:
            rpy: RPY instance

        Returns:
            Quaternion instance
        """
        # Convert RPY to rotation matrix first
        rot_matrix = rpy.to_rotation_matrix()
        return cls.from_rotation_matrix(RotationMatrix(rot_matrix))

    @classmethod
    def from_rotation_matrix(cls, rotation_matrix: RotationMatrix) -> Quaternion:
        """Create quaternion from rotation matrix.

        Uses Shepperd's method for numerical stability.

        Args:
            rotation_matrix: RotationMatrix instance

        Returns:
            Quaternion instance
        """
        matrix = rotation_matrix.matrix
        trace = np.trace(matrix)

        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (matrix[2, 1] - matrix[1, 2]) * s
            y = (matrix[0, 2] - matrix[2, 0]) * s
            z = (matrix[1, 0] - matrix[0, 1]) * s
        else:
            if matrix[0, 0] > matrix[1, 1] and matrix[0, 0] > matrix[2, 2]:
                s = 2.0 * np.sqrt(1.0 + matrix[0, 0] - matrix[1, 1] - matrix[2, 2])
                w = (matrix[2, 1] - matrix[1, 2]) / s
                x = 0.25 * s
                y = (matrix[0, 1] + matrix[1, 0]) / s
                z = (matrix[0, 2] + matrix[2, 0]) / s
            elif matrix[1, 1] > matrix[2, 2]:
                s = 2.0 * np.sqrt(1.0 + matrix[1, 1] - matrix[0, 0] - matrix[2, 2])
                w = (matrix[0, 2] - matrix[2, 0]) / s
                x = (matrix[0, 1] + matrix[1, 0]) / s
                y = 0.25 * s
                z = (matrix[1, 2] + matrix[2, 1]) / s
            else:
                s = 2.0 * np.sqrt(1.0 + matrix[2, 2] - matrix[0, 0] - matrix[1, 1])
                w = (matrix[1, 0] - matrix[0, 1]) / s
                x = (matrix[0, 2] + matrix[2, 0]) / s
                y = (matrix[1, 2] + matrix[2, 1]) / s
                z = 0.25 * s

        return cls(w, x, y, z)

    @classmethod
    def from_axis_angle(cls, axis: np.ndarray, angle: float) -> Quaternion:
        """Create quaternion from axis-angle representation.

        Args:
            axis: 3D rotation axis (will be normalized)
            angle: Rotation angle in radians

        Returns:
            Quaternion instance
        """
        axis = np.array(axis, dtype=np.float64)
        axis_norm = np.linalg.norm(axis)

        if axis_norm == 0:
            return cls.identity()

        axis = axis / axis_norm
        half_angle = angle / 2.0
        sin_half = np.sin(half_angle)

        w = np.cos(half_angle)
        x = axis[0] * sin_half
        y = axis[1] * sin_half
        z = axis[2] * sin_half

        return cls(w, x, y, z)

    @classmethod
    def from_two_vectors(cls, from_vec: np.ndarray, to_vec: np.ndarray) -> Quaternion:
        """Create quaternion that rotates from_vec to to_vec.

        Args:
            from_vec: Source vector (will be normalized)
            to_vec: Target vector (will be normalized)

        Returns:
            Quaternion instance
        """
        # Normalize vectors
        v1 = np.array(from_vec, dtype=np.float64)
        v2 = np.array(to_vec, dtype=np.float64)

        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)

        # Compute rotation axis and angle
        dot = np.dot(v1, v2)

        if np.abs(dot - 1.0) < 1e-6:
            # Vectors are already aligned
            return cls.identity()
        elif np.abs(dot + 1.0) < 1e-6:
            # Vectors are opposite
            # Find an orthogonal vector
            if np.abs(v1[0]) < 0.9:
                ortho = np.array([1, 0, 0])
            else:
                ortho = np.array([0, 1, 0])

            axis = np.cross(v1, ortho)
            axis = axis / np.linalg.norm(axis)
            return cls.from_axis_angle(axis, np.pi)
        else:
            # General case
            axis = np.cross(v1, v2)
            w = 1.0 + dot
            x, y, z = axis

            # This automatically handles normalization
            return cls(w, x, y, z)

    @classmethod
    def random(cls) -> Quaternion:
        """Generate a random unit quaternion using uniform distribution.

        Based on "Uniform Random Rotations" by Ken Shoemake.
        """
        # Generate three random numbers
        u1, u2, u3 = np.random.uniform(0, 1, 3)

        # Convert to quaternion components
        sqrt1_u1 = np.sqrt(1 - u1)
        sqrtu1 = np.sqrt(u1)

        w = sqrt1_u1 * np.sin(2 * np.pi * u2)
        x = sqrt1_u1 * np.cos(2 * np.pi * u2)
        y = sqrtu1 * np.sin(2 * np.pi * u3)
        z = sqrtu1 * np.cos(2 * np.pi * u3)

        return cls(w, x, y, z)

    @classmethod
    def slerp(cls, q1: Quaternion, q2: Quaternion, t: float) -> Quaternion:
        """Spherical linear interpolation between two quaternions.

        Args:
            q1: Start quaternion
            q2: End quaternion
            t: Interpolation parameter (0 to 1)

        Returns:
            Interpolated quaternion
        """
        # Compute dot product
        dot = np.dot(q1._data, q2._data)

        # If quaternions are nearly opposite, flip one
        if dot < 0:
            q2_data = -q2._data
            dot = -dot
        else:
            q2_data = q2._data

        # If quaternions are very close, use linear interpolation
        if dot > 0.9995:
            result = q1._data + t * (q2_data - q1._data)
            return cls.from_numpy(result)

        # Calculate interpolation parameters
        theta = np.arccos(np.clip(dot, -1, 1))
        sin_theta = np.sin(theta)

        # Perform spherical interpolation
        s1 = np.sin((1 - t) * theta) / sin_theta
        s2 = np.sin(t * theta) / sin_theta

        result = s1 * q1._data + s2 * q2_data
        return cls.from_numpy(result)

    @property
    def w(self) -> float:
        """Get the scalar component."""
        return float(self._data[0])

    @property
    def x(self) -> float:
        """Get the x component."""
        return float(self._data[1])

    @property
    def y(self) -> float:
        """Get the y component."""
        return float(self._data[2])

    @property
    def z(self) -> float:
        """Get the z component."""
        return float(self._data[3])

    @property
    def scalar(self) -> float:
        """Get the scalar part (w component)."""
        return self.w

    @property
    def vector(self) -> np.ndarray:
        """Get the vector part [x, y, z]."""
        return self._data[1:].copy()

    @property
    def numpy(self) -> np.ndarray:
        """Get quaternion as numpy array [w, x, y, z]."""
        return self._data.copy()

    @property
    def magnitude(self) -> float:
        """Get the magnitude of the quaternion (should be 1 for unit quaternions)."""
        return float(np.linalg.norm(self._data))

    @property
    def is_unit(self, tolerance: float = 1e-6) -> bool:
        """Check if this is a unit quaternion."""
        return np.abs(self.magnitude - 1.0) < tolerance

    def to_numpy(self, scalar_first: bool = True) -> np.ndarray:
        """Convert to numpy array.

        Args:
            scalar_first: If True, return [w, x, y, z], else [x, y, z, w]

        Returns:
            Numpy array with quaternion components
        """
        if scalar_first:
            return self._data.copy()
        else:
            return np.array([self.x, self.y, self.z, self.w])

    def to_rotation_matrix(self) -> RotationMatrix:
        """Convert quaternion to rotation matrix.

        Returns:
            RotationMatrix instance
        """
        w, x, y, z = self._data

        # Pre-compute repeated values
        xx = x * x
        yy = y * y
        zz = z * z
        xy = x * y
        xz = x * z
        yz = y * z
        wx = w * x
        wy = w * y
        wz = w * z

        # Build rotation matrix
        matrix = np.array([
            [1 - 2*(yy + zz), 2*(xy - wz), 2*(xz + wy)],
            [2*(xy + wz), 1 - 2*(xx + zz), 2*(yz - wx)],
            [2*(xz - wy), 2*(yz + wx), 1 - 2*(xx + yy)]
        ])

        return RotationMatrix(matrix)

    def to_rpy(self) -> RPY:
        """Convert quaternion to RPY angles.

        Returns:
            RPY instance
        """
        # Convert to rotation matrix first
        rot_matrix = self.to_rotation_matrix()
        return rot_matrix.to_rpy()

    def to_axis_angle(self) -> tuple[np.ndarray, float]:
        """Convert quaternion to axis-angle representation.

        Returns:
            Tuple of (axis, angle) where axis is a unit vector
        """
        # Handle near-identity quaternion
        if np.abs(self.w) >= 1.0:
            return np.array([1, 0, 0]), 0.0

        # Extract angle
        angle = 2 * np.arccos(np.clip(self.w, -1, 1))

        # Extract axis
        sin_half_angle = np.sqrt(1 - self.w**2)
        
        if sin_half_angle < 1e-6:
            # Small angle, axis doesn't matter much
            axis = np.array([1, 0, 0])
        else:
            axis = self.vector / sin_half_angle

        return axis, angle

    def apply_to_vector(self, vector: np.ndarray) -> np.ndarray:
        """Apply quaternion rotation to a vector.

        Uses the formula: v' = q * v * q^(-1)

        Args:
            vector: 3D vector or array of vectors

        Returns:
            Rotated vector(s)
        """
        vector = np.array(vector)

        if vector.ndim == 1:
            # Single vector
            if len(vector) != 3:
                raise ValueError("Vector must be 3D")

            # Convert vector to pure quaternion
            v_quat = np.array([0, vector[0], vector[1], vector[2]])

            # Apply rotation: v' = q * v * q^(-1)
            result = self._hamilton_product(
                self._data,
                self._hamilton_product(v_quat, self.conjugate()._data)
            )

            return result[1:]  # Return vector part
        elif vector.ndim == 2:
            # Multiple vectors
            if vector.shape[1] != 3:
                raise ValueError("Vectors must be 3D (shape [..., 3])")

            # Apply rotation to each vector
            result = np.zeros_like(vector)
            for i in range(len(vector)):
                result[i] = self.apply_to_vector(vector[i])
            return result
        else:
            raise ValueError("Vector must be 1D or 2D array")

    def _hamilton_product(self, q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        """Compute Hamilton product of two quaternions."""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2

        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2

        return np.array([w, x, y, z])

    def compose(self, other: Quaternion) -> Quaternion:
        """Compose this quaternion with another.

        The resulting rotation is equivalent to applying this rotation
        followed by the other rotation.

        Args:
            other: Another Quaternion instance

        Returns:
            New Quaternion representing the composed rotation
        """
        result = self._hamilton_product(other._data, self._data)
        return Quaternion.from_numpy(result)

    def conjugate(self) -> Quaternion:
        """Get the conjugate of the quaternion.

        For unit quaternions, this represents the inverse rotation.

        Returns:
            Conjugate quaternion
        """
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def inverse(self) -> Quaternion:
        """Get the inverse quaternion.

        For unit quaternions, this is the same as the conjugate.

        Returns:
            Inverse quaternion
        """
        return self.conjugate()

    def power(self, exponent: float) -> Quaternion:
        """Raise quaternion to a power (fractional rotations).

        Args:
            exponent: Power to raise the quaternion to

        Returns:
            New Quaternion
        """
        # Convert to axis-angle
        axis, angle = self.to_axis_angle()

        # Scale the angle
        new_angle = angle * exponent

        # Convert back to quaternion
        return Quaternion.from_axis_angle(axis, new_angle)

    def distance_to(self, other: Quaternion) -> float:
        """Compute angular distance to another quaternion.

        Args:
            other: Another Quaternion

        Returns:
            Angular distance in radians
        """
        # Compute dot product
        dot = np.abs(np.dot(self._data, other._data))
        
        # Clamp to handle numerical errors
        dot = np.clip(dot, 0, 1)
        
        # Return angle
        return 2 * np.arccos(dot)

    def is_close(self, other: Quaternion, tolerance: float = 1e-6) -> bool:
        """Check if this quaternion is close to another.

        Accounts for the fact that q and -q represent the same rotation.

        Args:
            other: Another Quaternion
            tolerance: Tolerance for comparison

        Returns:
            True if quaternions are close
        """
        # Check both q and -q
        return (np.allclose(self._data, other._data, atol=tolerance) or
                np.allclose(self._data, -other._data, atol=tolerance))

    def normalize(self) -> Quaternion:
        """Return a normalized copy of this quaternion.

        Returns:
            Normalized quaternion
        """
        norm = self.magnitude
        if norm == 0:
            return Quaternion.identity()
        
        normalized_data = self._data / norm
        return Quaternion.from_numpy(normalized_data)

    def copy(self) -> Quaternion:
        """Create a copy of this quaternion."""
        return Quaternion(self.w, self.x, self.y, self.z)

    def __repr__(self) -> str:
        """String representation of the quaternion."""
        return f"Quaternion(w={self.w:.6f}, x={self.x:.6f}, y={self.y:.6f}, z={self.z:.6f})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        rpy = self.to_rpy()
        rpy_deg = rpy.to_degrees()
        return (f"Quaternion([{self.w:.3f}, {self.x:.3f}, {self.y:.3f}, {self.z:.3f}], "
                f"rpy=[{rpy_deg.roll:.1f}°, {rpy_deg.pitch:.1f}°, {rpy_deg.yaw:.1f}°])")

    def __eq__(self, other: object) -> bool:
        """Check equality with another Quaternion."""
        if not isinstance(other, Quaternion):
            return NotImplemented
        # Account for q and -q representing the same rotation
        return (np.array_equal(self._data, other._data) or
                np.array_equal(self._data, -other._data))

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Quaternion."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for Quaternion objects."""
        # Use absolute values to ensure q and -q hash the same
        return hash(np.abs(self._data).tobytes())

    def __mul__(self, other: Quaternion | float) -> Quaternion:
        """Multiply quaternion by another quaternion or scalar."""
        if isinstance(other, Quaternion):
            return self.compose(other)
        elif isinstance(other, (int, float)):
            # Scalar multiplication (not rotation composition)
            return Quaternion.from_numpy(self._data * other)
        return NotImplemented

    def __truediv__(self, scalar: float) -> Quaternion:
        """Divide quaternion by a scalar."""
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero")
            return Quaternion.from_numpy(self._data / scalar)
        return NotImplemented

    def __neg__(self) -> Quaternion:
        """Negate the quaternion.

        Note: -q represents the same rotation as q.
        """
        return Quaternion(-self.w, -self.x, -self.y, -self.z)

    def __abs__(self) -> float:
        """Get the magnitude of the quaternion."""
        return self.magnitude

    def __iter__(self):
        """Make Quaternion iterable."""
        return iter([self.w, self.x, self.y, self.z])

    def __getitem__(self, index: int) -> float:
        """Get component by index (0=w, 1=x, 2=y, 3=z)."""
        if 0 <= index < 4:
            return float(self._data[index])
        else:
            raise IndexError("Quaternion index out of range")

    def __len__(self) -> int:
        """Length of the quaternion (always 4)."""
        return 4
