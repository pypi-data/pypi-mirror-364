from __future__ import annotations

import math

import numpy as np


class Point3D:
    """
    Represents a point in 2D/3D space with x, y, and optional z coordinates.

    This class provides efficient storage and operations for spatial coordinates,
    optimized for computer vision and spatial analysis tasks.

    Args:
        x: The x coordinate
        y: The y coordinate
        z: The z coordinate (default: 0.0)

    Examples:
        >>> p1 = Point(1.0, 2.0)
        >>> p2 = Point(3.0, 4.0, 5.0)
        >>> distance = p1.distance_to(p2)
        >>> midpoint = p1.midpoint(p2)
    """

    __slots__ = ("_data",)  # Memory optimization

    def __init__(self, x: float, y: float, z: float = 0.0) -> None:
        """Initialize a Point with given coordinates."""
        self._data = np.array([x, y, z], dtype=np.float64)

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> Point3D:
        """Create a Point from a numpy array.

        Args:
            array: Numpy array with 2 or 3 elements

        Returns:
            Point instance

        Raises:
            ValueError: If array doesn't have 2 or 3 elements
        """
        if len(array) < 2 or len(array) > 3:
            raise ValueError("Array must have 2 or 3 elements")

        if len(array) == 2:
            return cls(float(array[0]), float(array[1]), 0.0)
        return cls(float(array[0]), float(array[1]), float(array[2]))

    @classmethod
    def from_tuple(cls, coords: tuple[float, ...]) -> Point3D:
        """Create a Point from a tuple of coordinates.

        Args:
            coords: Tuple with 2 or 3 coordinates

        Returns:
            Point instance
        """
        return cls.from_numpy(np.array(coords))

    @classmethod
    def origin(cls) -> Point3D:
        """Create a Point at the origin (0, 0, 0)."""
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def unit_x(cls) -> Point3D:
        """Create a unit point along the x-axis (1, 0, 0)."""
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def unit_y(cls) -> Point3D:
        """Create a unit point along the y-axis (0, 1, 0)."""
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def unit_z(cls) -> Point3D:
        """Create a unit point along the z-axis (0, 0, 1)."""
        return cls(0.0, 0.0, 1.0)

    @property
    def x(self) -> float:
        """Get the x coordinate."""
        return float(self._data[0])

    @property
    def y(self) -> float:
        """Get the y coordinate."""
        return float(self._data[1])

    @property
    def z(self) -> float:
        """Get the z coordinate."""
        return float(self._data[2])

    @x.setter
    def x(self, value: float) -> None:
        """Set the x coordinate."""
        self._data[0] = value

    @y.setter
    def y(self, value: float) -> None:
        """Set the y coordinate."""
        self._data[1] = value

    @z.setter
    def z(self, value: float) -> None:
        """Set the z coordinate."""
        self._data[2] = value

    @property
    def numpy(self) -> np.ndarray:
        """Get coordinates as a numpy array."""
        return self._data.copy()

    @property
    def xy(self) -> tuple[float, float]:
        """Get x and y coordinates as a tuple."""
        return (self.x, self.y)

    @property
    def xyz(self) -> tuple[float, float, float]:
        """Get x, y, and z coordinates as a tuple."""
        return (self.x, self.y, self.z)

    @property
    def magnitude(self) -> float:
        """Get the magnitude (distance from origin) of the point."""
        return float(np.linalg.norm(self._data))

    @property
    def magnitude_squared(self) -> float:
        """Get the squared magnitude of the point (more efficient than magnitude)."""
        return float(np.dot(self._data, self._data))

    @property
    def is_origin(self) -> bool:
        """Check if the point is at the origin."""
        return np.allclose(self._data, 0.0)

    def distance_to(self, other: Point3D) -> float:
        """Calculate Euclidean distance to another point.

        Args:
            other: Another Point instance

        Returns:
            Distance as a float
        """
        return float(np.linalg.norm(self._data - other._data))

    def distance_squared_to(self, other: Point3D) -> float:
        """Calculate squared Euclidean distance to another point.

        More efficient than distance_to() when only comparing distances.

        Args:
            other: Another Point instance

        Returns:
            Squared distance as a float
        """
        diff = self._data - other._data
        return float(np.dot(diff, diff))

    def manhattan_distance_to(self, other: Point3D) -> float:
        """Calculate Manhattan distance to another point.

        Args:
            other: Another Point instance

        Returns:
            Manhattan distance as a float
        """
        return float(np.sum(np.abs(self._data - other._data)))

    def midpoint(self, other: Point3D) -> Point3D:
        """Calculate the midpoint between this point and another.

        Args:
            other: Another Point instance

        Returns:
            New Point at the midpoint
        """
        mid_data = (self._data + other._data) / 2.0
        return Point3D(mid_data[0], mid_data[1], mid_data[2])

    def normalize(self) -> Point3D:
        """Return a normalized version of this point (unit vector).

        Returns:
            New Point with unit magnitude

        Raises:
            ValueError: If point is at origin (cannot normalize)
        """
        magnitude = self.magnitude
        if magnitude == 0:
            raise ValueError("Cannot normalize a point at the origin")

        normalized_data = self._data / magnitude
        return Point3D(normalized_data[0], normalized_data[1], normalized_data[2])

    def dot(self, other: Point3D) -> float:
        """Calculate dot product with another point.

        Args:
            other: Another Point instance

        Returns:
            Dot product as a float
        """
        return float(np.dot(self._data, other._data))

    def cross(self, other: Point3D) -> Point3D:
        """Calculate cross product with another point.

        Args:
            other: Another Point instance

        Returns:
            New Point representing the cross product
        """
        cross_data = np.cross(self._data, other._data)
        return Point3D(cross_data[0], cross_data[1], cross_data[2])

    def rotate_2d(self, angle: float, center: Point3D | None = None) -> Point3D:
        """Rotate point around a center in 2D space.

        Args:
            angle: Rotation angle in radians
            center: Center of rotation (default: origin)

        Returns:
            New rotated Point
        """
        if center is None:
            center = Point3D.origin()

        # Translate to origin
        translated = self - center

        # Rotate
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        rotated_x = translated.x * cos_a - translated.y * sin_a
        rotated_y = translated.x * sin_a + translated.y * cos_a

        # Translate back
        return Point3D(rotated_x + center.x, rotated_y + center.y, self.z)

    def translate(self, dx: float, dy: float, dz: float = 0.0) -> Point3D:
        """Translate point by given offsets.

        Args:
            dx: X offset
            dy: Y offset
            dz: Z offset (default: 0.0)

        Returns:
            New translated Point
        """
        return Point3D(self.x + dx, self.y + dy, self.z + dz)

    def scale(self, factor: float, center: Point3D | None = None) -> Point3D:
        """Scale point by a factor around a center.

        Args:
            factor: Scale factor
            center: Center of scaling (default: origin)

        Returns:
            New scaled Point
        """
        if center is None:
            center = Point3D.origin()

        # Translate to origin, scale, then translate back
        translated = self - center
        scaled = translated * factor
        return scaled + center

    def clamp(self, min_point: Point3D, max_point: Point3D) -> Point3D:
        """Clamp coordinates to be within bounds.

        Args:
            min_point: Minimum bounds
            max_point: Maximum bounds

        Returns:
            New Point with clamped coordinates
        """
        clamped_data = np.clip(self._data, min_point._data, max_point._data)
        return Point3D(clamped_data[0], clamped_data[1], clamped_data[2])

    def lerp(self, other: Point3D, t: float) -> Point3D:
        """Linear interpolation between this point and another.

        Args:
            other: Target point
            t: Interpolation parameter (0.0 to 1.0)

        Returns:
            New interpolated Point
        """
        lerped_data = self._data + t * (other._data - self._data)
        return Point3D(lerped_data[0], lerped_data[1], lerped_data[2])

    def to_int(self) -> Point3D:
        """Convert coordinates to integers.

        Returns:
            New Point with integer coordinates
        """
        return Point3D(int(self.x), int(self.y), int(self.z))

    def round(self, decimals: int = 0) -> Point3D:
        """Round coordinates to specified decimal places.

        Args:
            decimals: Number of decimal places

        Returns:
            New Point with rounded coordinates
        """
        rounded_data = np.round(self._data, decimals)
        return Point3D(rounded_data[0], rounded_data[1], rounded_data[2])

    def is_close(self, other: Point3D, tolerance: float = 1e-9) -> bool:
        """Check if this point is close to another within tolerance.

        Args:
            other: Another Point instance
            tolerance: Tolerance for comparison

        Returns:
            True if points are close, False otherwise
        """
        return np.allclose(self._data, other._data, atol=tolerance)

    def copy(self) -> Point3D:
        """Create a copy of this point."""
        return Point3D(self.x, self.y, self.z)

    def __repr__(self) -> str:
        """String representation of the point."""
        return f"Point({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        if self.z == 0.0:
            return f"({self.x}, {self.y})"
        return f"({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Point."""
        if not isinstance(other, Point3D):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Point."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for Point objects."""
        return hash(self._data.tobytes())

    def __add__(self, other: Point3D | float) -> Point3D:
        """Add another point or scalar to this point."""
        if isinstance(other, Point3D):
            result_data = self._data + other._data
        else:
            result_data = self._data + other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __sub__(self, other: Point3D | float) -> Point3D:
        """Subtract another point or scalar from this point."""
        if isinstance(other, Point3D):
            result_data = self._data - other._data
        else:
            result_data = self._data - other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __mul__(self, other: Point3D | float) -> Point3D:
        """Multiply this point by another point or scalar."""
        if isinstance(other, Point3D):
            result_data = self._data * other._data
        else:
            result_data = self._data * other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __truediv__(self, other: Point3D | float) -> Point3D:
        """Divide this point by another point or scalar."""
        if isinstance(other, Point3D):
            result_data = self._data / other._data
        else:
            result_data = self._data / other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __floordiv__(self, other: Point3D | float) -> Point3D:
        """Floor divide this point by another point or scalar."""
        if isinstance(other, Point3D):
            result_data = self._data // other._data
        else:
            result_data = self._data // other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __mod__(self, other: Point3D | float) -> Point3D:
        """Modulo operation with another point or scalar."""
        if isinstance(other, Point3D):
            result_data = self._data % other._data
        else:
            result_data = self._data % other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __pow__(self, other: Point3D | float) -> Point3D:
        """Power operation with another point or scalar."""
        if isinstance(other, Point3D):
            result_data = self._data**other._data
        else:
            result_data = self._data**other
        return Point3D(result_data[0], result_data[1], result_data[2])

    def __neg__(self) -> Point3D:
        """Negate the point."""
        return Point3D(-self.x, -self.y, -self.z)

    def __pos__(self) -> Point3D:
        """Positive unary operator."""
        return self.copy()

    def __abs__(self) -> Point3D:
        """Absolute value of coordinates."""
        return Point3D(abs(self.x), abs(self.y), abs(self.z))

    def __lt__(self, other: Point3D) -> bool:
        """Less than comparison (by magnitude)."""
        return self.magnitude < other.magnitude

    def __le__(self, other: Point3D) -> bool:
        """Less than or equal comparison (by magnitude)."""
        return self.magnitude <= other.magnitude

    def __gt__(self, other: Point3D) -> bool:
        """Greater than comparison (by magnitude)."""
        return self.magnitude > other.magnitude

    def __ge__(self, other: Point3D) -> bool:
        """Greater than or equal comparison (by magnitude)."""
        return self.magnitude >= other.magnitude

    def __iter__(self):
        """Make Point iterable."""
        return iter([self.x, self.y, self.z])

    def __getitem__(self, index: int) -> float:
        """Get coordinate by index (0=x, 1=y, 2=z)."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("Point index out of range")

    def __setitem__(self, index: int, value: float) -> None:
        """Set coordinate by index (0=x, 1=y, 2=z)."""
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise IndexError("Point index out of range")

    def __len__(self) -> int:
        """Length of the point (always 3)."""
        return 3
