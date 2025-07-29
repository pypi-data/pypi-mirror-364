from __future__ import annotations

import numpy as np


class Vector3D:
    """
    Represents a 3D vector with x, y, z components.

    This class provides efficient operations for 3D vectors commonly used in
    computer vision, graphics, and spatial computations.

    Args:
        x: X component (default: 0.0)
        y: Y component (default: 0.0)
        z: Z component (default: 0.0)

    Examples:
        >>> v1 = Vector3D(1, 2, 3)
        >>> v2 = Vector3D(4, 5, 6)
        >>> dot_product = v1.dot(v2)
        >>> cross_product = v1.cross(v2)
        >>> normalized = v1.normalize()
    """

    __slots__ = ("_data",)  # Memory optimization

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Initialize a Vector3D with given components."""
        self._data = np.array([x, y, z], dtype=np.float64)

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> Vector3D:
        """Create a Vector3D from a numpy array.

        Args:
            array: Numpy array with 3 elements

        Returns:
            Vector3D instance

        Raises:
            ValueError: If array doesn't have exactly 3 elements
        """
        if len(array) != 3:
            raise ValueError("Array must have exactly 3 elements")

        return cls(float(array[0]), float(array[1]), float(array[2]))

    @classmethod
    def from_tuple(cls, components: tuple[float, float, float]) -> Vector3D:
        """Create a Vector3D from a tuple of components.

        Args:
            components: Tuple with (x, y, z)

        Returns:
            Vector3D instance
        """
        return cls(components[0], components[1], components[2])

    @classmethod
    def zeros(cls) -> Vector3D:
        """Create a zero vector."""
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def ones(cls) -> Vector3D:
        """Create a vector of ones."""
        return cls(1.0, 1.0, 1.0)

    @classmethod
    def unit_x(cls) -> Vector3D:
        """Create a unit vector along the x-axis."""
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def unit_y(cls) -> Vector3D:
        """Create a unit vector along the y-axis."""
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def unit_z(cls) -> Vector3D:
        """Create a unit vector along the z-axis."""
        return cls(0.0, 0.0, 1.0)

    @classmethod
    def random(cls, min_val: float = -1.0, max_val: float = 1.0) -> Vector3D:
        """Create a random vector with components in specified range.

        Args:
            min_val: Minimum value for components
            max_val: Maximum value for components

        Returns:
            Random Vector3D
        """
        components = np.random.uniform(min_val, max_val, 3)
        return cls.from_numpy(components)

    @classmethod
    def random_unit(cls) -> Vector3D:
        """Create a random unit vector with uniform distribution on sphere."""
        # Use spherical coordinates for uniform distribution
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.arccos(1 - 2 * np.random.uniform(0, 1))
        
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        
        return cls(x, y, z)

    @property
    def x(self) -> float:
        """Get the x component."""
        return float(self._data[0])

    @property
    def y(self) -> float:
        """Get the y component."""
        return float(self._data[1])

    @property
    def z(self) -> float:
        """Get the z component."""
        return float(self._data[2])

    @x.setter
    def x(self, value: float) -> None:
        """Set the x component."""
        self._data[0] = value

    @y.setter
    def y(self, value: float) -> None:
        """Set the y component."""
        self._data[1] = value

    @z.setter
    def z(self, value: float) -> None:
        """Set the z component."""
        self._data[2] = value

    @property
    def numpy(self) -> np.ndarray:
        """Get components as a numpy array."""
        return self._data.copy()

    @property
    def tuple(self) -> tuple[float, float, float]:
        """Get components as a tuple."""
        return (self.x, self.y, self.z)

    @property
    def magnitude(self) -> float:
        """Get the magnitude (length) of the vector."""
        return float(np.linalg.norm(self._data))

    @property
    def magnitude_squared(self) -> float:
        """Get the squared magnitude (more efficient than magnitude)."""
        return float(np.dot(self._data, self._data))

    @property
    def is_zero(self, tolerance: float = 1e-9) -> bool:
        """Check if this is a zero vector."""
        return self.magnitude_squared < tolerance * tolerance

    @property
    def is_unit(self, tolerance: float = 1e-6) -> bool:
        """Check if this is a unit vector."""
        return np.abs(self.magnitude - 1.0) < tolerance

    def normalize(self) -> Vector3D:
        """Return a normalized (unit) version of this vector.

        Returns:
            New unit Vector3D

        Raises:
            ValueError: If vector is zero
        """
        mag = self.magnitude
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector")

        return Vector3D.from_numpy(self._data / mag)

    def dot(self, other: Vector3D) -> float:
        """Calculate dot product with another vector.

        Args:
            other: Another Vector3D

        Returns:
            Dot product as float
        """
        return float(np.dot(self._data, other._data))

    def cross(self, other: Vector3D) -> Vector3D:
        """Calculate cross product with another vector.

        Args:
            other: Another Vector3D

        Returns:
            New Vector3D representing the cross product
        """
        cross_data = np.cross(self._data, other._data)
        return Vector3D.from_numpy(cross_data)

    def angle_to(self, other: Vector3D) -> float:
        """Calculate angle to another vector in radians.

        Args:
            other: Another Vector3D

        Returns:
            Angle in radians [0, π]
        """
        # Normalize to avoid numerical issues
        v1 = self.normalize()
        v2 = other.normalize()
        
        # Use atan2 for numerical stability
        return np.arctan2(v1.cross(v2).magnitude, v1.dot(v2))

    def project_onto(self, other: Vector3D) -> Vector3D:
        """Project this vector onto another vector.

        Args:
            other: Vector to project onto

        Returns:
            Projected vector
        """
        other_mag_sq = other.magnitude_squared
        if other_mag_sq == 0:
            return Vector3D.zeros()
        
        scalar = self.dot(other) / other_mag_sq
        return other * scalar

    def reject_from(self, other: Vector3D) -> Vector3D:
        """Get the component perpendicular to another vector.

        Args:
            other: Vector to reject from

        Returns:
            Perpendicular component
        """
        return self - self.project_onto(other)

    def reflect(self, normal: Vector3D) -> Vector3D:
        """Reflect this vector off a surface with given normal.

        Args:
            normal: Surface normal (should be unit vector)

        Returns:
            Reflected vector
        """
        # v_reflected = v - 2 * (v · n) * n
        return self - normal * (2 * self.dot(normal))

    def rotate_around_axis(self, axis: Vector3D, angle: float) -> Vector3D:
        """Rotate this vector around an axis using Rodrigues' formula.

        Args:
            axis: Rotation axis (will be normalized)
            angle: Rotation angle in radians

        Returns:
            Rotated vector
        """
        axis_normalized = axis.normalize()
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        
        # Rodrigues' formula
        term1 = self * cos_angle
        term2 = axis_normalized.cross(self) * sin_angle
        term3 = axis_normalized * (axis_normalized.dot(self) * (1 - cos_angle))
        
        return term1 + term2 + term3

    def lerp(self, other: Vector3D, t: float) -> Vector3D:
        """Linear interpolation to another vector.

        Args:
            other: Target vector
            t: Interpolation parameter [0, 1]

        Returns:
            Interpolated vector
        """
        return self + (other - self) * t

    def slerp(self, other: Vector3D, t: float) -> Vector3D:
        """Spherical linear interpolation to another vector.

        Args:
            other: Target vector
            t: Interpolation parameter [0, 1]

        Returns:
            Spherically interpolated vector
        """
        # Normalize both vectors
        v1 = self.normalize()
        v2 = other.normalize()
        
        # Calculate angle
        dot = v1.dot(v2)
        dot = np.clip(dot, -1, 1)
        theta = np.arccos(dot)
        
        # If vectors are nearly parallel, use linear interpolation
        if np.abs(theta) < 1e-6:
            return self.lerp(other, t)
        
        # Spherical interpolation
        sin_theta = np.sin(theta)
        a = np.sin((1 - t) * theta) / sin_theta
        b = np.sin(t * theta) / sin_theta
        
        # Scale by original magnitude
        result = v1 * a + v2 * b
        target_mag = self.magnitude * (1 - t) + other.magnitude * t
        
        return result.normalize() * target_mag

    def distance_to(self, other: Vector3D) -> float:
        """Calculate Euclidean distance to another vector.

        Args:
            other: Another Vector3D

        Returns:
            Distance as float
        """
        return (self - other).magnitude

    def distance_squared_to(self, other: Vector3D) -> float:
        """Calculate squared distance to another vector (more efficient).

        Args:
            other: Another Vector3D

        Returns:
            Squared distance as float
        """
        return (self - other).magnitude_squared

    def clamp(self, min_vec: Vector3D, max_vec: Vector3D) -> Vector3D:
        """Clamp components between min and max vectors.

        Args:
            min_vec: Minimum bounds
            max_vec: Maximum bounds

        Returns:
            Clamped vector
        """
        clamped = np.clip(self._data, min_vec._data, max_vec._data)
        return Vector3D.from_numpy(clamped)

    def clamp_magnitude(self, max_magnitude: float) -> Vector3D:
        """Clamp the magnitude of the vector.

        Args:
            max_magnitude: Maximum allowed magnitude

        Returns:
            Vector with clamped magnitude
        """
        mag = self.magnitude
        if mag <= max_magnitude:
            return self.copy()
        
        return self.normalize() * max_magnitude

    def round(self, decimals: int = 0) -> Vector3D:
        """Round components to specified decimal places.

        Args:
            decimals: Number of decimal places

        Returns:
            Rounded vector
        """
        rounded = np.round(self._data, decimals)
        return Vector3D.from_numpy(rounded)

    def is_close(self, other: Vector3D, tolerance: float = 1e-9) -> bool:
        """Check if this vector is close to another.

        Args:
            other: Another Vector3D
            tolerance: Tolerance for comparison

        Returns:
            True if vectors are close
        """
        return np.allclose(self._data, other._data, atol=tolerance)

    def is_parallel(self, other: Vector3D, tolerance: float = 1e-6) -> bool:
        """Check if this vector is parallel to another.

        Args:
            other: Another Vector3D
            tolerance: Angular tolerance in radians

        Returns:
            True if vectors are parallel
        """
        angle = self.angle_to(other)
        return angle < tolerance or np.abs(angle - np.pi) < tolerance

    def is_perpendicular(self, other: Vector3D, tolerance: float = 1e-6) -> bool:
        """Check if this vector is perpendicular to another.

        Args:
            other: Another Vector3D
            tolerance: Tolerance for dot product

        Returns:
            True if vectors are perpendicular
        """
        return np.abs(self.dot(other)) < tolerance

    def copy(self) -> Vector3D:
        """Create a copy of this vector."""
        return Vector3D(self.x, self.y, self.z)

    def __repr__(self) -> str:
        """String representation of the vector."""
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"[{self.x:.3f}, {self.y:.3f}, {self.z:.3f}]"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Vector3D."""
        if not isinstance(other, Vector3D):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Vector3D."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for Vector3D objects."""
        return hash(self._data.tobytes())

    def __add__(self, other: Vector3D | float) -> Vector3D:
        """Add another vector or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data + other._data)
        elif isinstance(other, (int, float)):
            return Vector3D.from_numpy(self._data + other)
        return NotImplemented

    def __sub__(self, other: Vector3D | float) -> Vector3D:
        """Subtract another vector or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data - other._data)
        elif isinstance(other, (int, float)):
            return Vector3D.from_numpy(self._data - other)
        return NotImplemented

    def __mul__(self, other: Vector3D | float) -> Vector3D:
        """Multiply by another vector (element-wise) or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data * other._data)
        elif isinstance(other, (int, float)):
            return Vector3D.from_numpy(self._data * other)
        return NotImplemented

    def __rmul__(self, other: float) -> Vector3D:
        """Right multiplication by scalar."""
        return self.__mul__(other)

    def __truediv__(self, other: Vector3D | float) -> Vector3D:
        """Divide by another vector (element-wise) or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data / other._data)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Cannot divide by zero")
            return Vector3D.from_numpy(self._data / other)
        return NotImplemented

    def __floordiv__(self, other: Vector3D | float) -> Vector3D:
        """Floor divide by another vector (element-wise) or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data // other._data)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Cannot divide by zero")
            return Vector3D.from_numpy(self._data // other)
        return NotImplemented

    def __mod__(self, other: Vector3D | float) -> Vector3D:
        """Modulo with another vector (element-wise) or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data % other._data)
        elif isinstance(other, (int, float)):
            return Vector3D.from_numpy(self._data % other)
        return NotImplemented

    def __pow__(self, other: Vector3D | float) -> Vector3D:
        """Power with another vector (element-wise) or scalar."""
        if isinstance(other, Vector3D):
            return Vector3D.from_numpy(self._data ** other._data)
        elif isinstance(other, (int, float)):
            return Vector3D.from_numpy(self._data ** other)
        return NotImplemented

    def __neg__(self) -> Vector3D:
        """Negate the vector."""
        return Vector3D.from_numpy(-self._data)

    def __pos__(self) -> Vector3D:
        """Positive unary operator."""
        return self.copy()

    def __abs__(self) -> Vector3D:
        """Absolute value of components."""
        return Vector3D.from_numpy(np.abs(self._data))

    def __iter__(self):
        """Make Vector3D iterable."""
        return iter([self.x, self.y, self.z])

    def __getitem__(self, index: int) -> float:
        """Get component by index (0=x, 1=y, 2=z)."""
        if 0 <= index < 3:
            return float(self._data[index])
        else:
            raise IndexError("Vector3D index out of range")

    def __setitem__(self, index: int, value: float) -> None:
        """Set component by index (0=x, 1=y, 2=z)."""
        if 0 <= index < 3:
            self._data[index] = value
        else:
            raise IndexError("Vector3D index out of range")

    def __len__(self) -> int:
        """Length of the vector (always 3)."""
        return 3
