from __future__ import annotations

import math
from collections.abc import Iterator
from typing import Tuple

import numpy as np

from .point import Point3D


class Points3DArray:
    """
    Manages a collection of points in a single numpy array for efficient operations.

    This class is optimized for handling large collections of points used in computer vision
    applications such as marking surfaces, trajectories, contours, and other spatial data.

    Args:
        data: Points data as numpy array (N, 3) or list of Point objects

    Examples:
        >>> # Create from Point objects
        >>> points = Points([Point(1, 2, 3), Point(4, 5, 6)])
        >>>
        >>> # Create from numpy array
        >>> points = Points(np.array([[1, 2, 3], [4, 5, 6]]))
        >>>
        >>> # Create trajectory
        >>> trajectory = Points.trajectory(Point(0, 0, 0), Point(10, 10, 10), 100)
        >>>
        >>> # Apply transformations
        >>> scaled = points.scale(2.0)
        >>> rotated = points.rotate_2d(np.pi/4)
    """

    __slots__ = ("_data",)

    def __init__(self, data: np.ndarray | list[Point3D] | list[list[float]] | list[tuple[float, ...]]) -> None:
        """Initialize Points collection from various data sources."""
        if isinstance(data, np.ndarray):
            if data.ndim == 1:
                # Single point
                if len(data) == 2:
                    self._data = np.array([[data[0], data[1], 0.0]], dtype=np.float64)
                elif len(data) == 3:
                    self._data = np.array([data], dtype=np.float64)
                else:
                    raise ValueError("Point array must have 2 or 3 elements")
            elif data.ndim == 2:
                if data.shape[1] == 2:
                    # 2D points, add z=0
                    self._data = np.column_stack([data, np.zeros(data.shape[0])]).astype(np.float64)
                elif data.shape[1] == 3:
                    self._data = data.astype(np.float64)
                else:
                    raise ValueError("Points array must have shape (N, 2) or (N, 3)")
            else:
                raise ValueError("Points array must be 1D or 2D")
        elif isinstance(data, (list, tuple)):
            if not data:
                self._data = np.empty((0, 3), dtype=np.float64)
            elif isinstance(data[0], Point3D):
                self._data = np.array([[p.x, p.y, p.z] for p in data], dtype=np.float64)
            elif isinstance(data[0], (list, tuple)):
                points_data = []
                for point in data:
                    if len(point) == 2:
                        points_data.append([point[0], point[1], 0.0])
                    elif len(point) == 3:
                        points_data.append([point[0], point[1], point[2]])
                    else:
                        raise ValueError("Each point must have 2 or 3 coordinates")
                self._data = np.array(points_data, dtype=np.float64)
            else:
                raise ValueError("List elements must be Point objects or coordinate lists/tuples")
        else:
            raise ValueError("Data must be numpy array, list of Points, or list of coordinates")

    @classmethod
    def empty(cls) -> Points3DArray:
        """Create an empty Points collection."""
        return cls(np.empty((0, 3), dtype=np.float64))

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> Points3DArray:
        """Create Points from numpy array."""
        return cls(array)

    @classmethod
    def from_points(cls, points: list[Point3D]) -> Points3DArray:
        """Create Points from list of Point objects."""
        return cls(points)

    @classmethod
    def grid(cls, x_range: tuple[float, float], y_range: tuple[float, float], x_steps: int, y_steps: int, z: float = 0.0) -> Points3DArray:
        """Create a grid of points."""
        x_vals = np.linspace(x_range[0], x_range[1], x_steps)
        y_vals = np.linspace(y_range[0], y_range[1], y_steps)
        xx, yy = np.meshgrid(x_vals, y_vals)
        points_data = np.column_stack([xx.ravel(), yy.ravel(), np.full(xx.size, z)])
        return cls(points_data)

    @classmethod
    def circle(cls, center: Point3D, radius: float, num_points: int, z: float = 0.0) -> Points3DArray:
        """Create points arranged in a circle."""
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points_data = np.column_stack([center.x + radius * np.cos(angles), center.y + radius * np.sin(angles), np.full(num_points, center.z + z)])
        return cls(points_data)

    @classmethod
    def line(cls, start: Point3D, end: Point3D, num_points: int) -> Points3DArray:
        """Create points along a line between two points."""
        t_values = np.linspace(0, 1, num_points)
        points_data = np.column_stack([start.x + t_values * (end.x - start.x), start.y + t_values * (end.y - start.y), start.z + t_values * (end.z - start.z)])
        return cls(points_data)

    @classmethod
    def trajectory(cls, start: Point3D, end: Point3D, num_points: int) -> Points3DArray:
        """Create a trajectory (alias for line)."""
        return cls.line(start, end, num_points)

    @classmethod
    def rectangle(cls, min_point: Point3D, max_point: Point3D, num_points_x: int, num_points_y: int) -> Points3DArray:
        """Create points forming a rectangle."""
        return cls.grid((min_point.x, max_point.x), (min_point.y, max_point.y), num_points_x, num_points_y, min_point.z)

    @classmethod
    def random(cls, num_points: int, bounds: tuple[Point3D, Point3D], seed: int | None = None) -> Points3DArray:
        """Create random points within bounds."""
        if seed is not None:
            np.random.seed(seed)

        min_point, max_point = bounds
        points_data = np.random.uniform([min_point.x, min_point.y, min_point.z], [max_point.x, max_point.y, max_point.z], (num_points, 3))
        return cls(points_data)

    @property
    def size(self) -> int:
        """Number of points in the collection."""
        return self._data.shape[0]

    @property
    def shape(self) -> Tuple[int, int]:
        """Shape of the underlying data array."""
        return self._data.shape

    @property
    def numpy(self) -> np.ndarray:
        """Get the underlying numpy array."""
        return self._data.copy()

    @property
    def x(self) -> np.ndarray:
        """Get all x coordinates."""
        return self._data[:, 0]

    @property
    def y(self) -> np.ndarray:
        """Get all y coordinates."""
        return self._data[:, 1]

    @property
    def z(self) -> np.ndarray:
        """Get all z coordinates."""
        return self._data[:, 2]

    @property
    def xy(self) -> np.ndarray:
        """Get x,y coordinates as (N, 2) array."""
        return self._data[:, :2]

    @property
    def xyz(self) -> np.ndarray:
        """Get x,y,z coordinates as (N, 3) array."""
        return self._data.copy()

    @property
    def centroid(self) -> Point3D:
        """Calculate the centroid of all points."""
        if self.size == 0:
            return Point3D(0, 0, 0)
        center = np.mean(self._data, axis=0)
        return Point3D(center[0], center[1], center[2])

    @property
    def bounds(self) -> tuple[Point3D, Point3D]:
        """Get bounding box as (min_point, max_point)."""
        if self.size == 0:
            return (Point3D(0, 0, 0), Point3D(0, 0, 0))

        min_coords = np.min(self._data, axis=0)
        max_coords = np.max(self._data, axis=0)
        return (Point3D(min_coords[0], min_coords[1], min_coords[2]), Point3D(max_coords[0], max_coords[1], max_coords[2]))

    @property
    def is_empty(self) -> bool:
        """Check if the collection is empty."""
        return self.size == 0

    def append(self, point: Point3D) -> None:
        """Add a point to the collection."""
        new_point = np.array([[point.x, point.y, point.z]], dtype=np.float64)
        self._data = np.vstack([self._data, new_point])

    def extend(self, points: Points3DArray | list[Point3D]) -> None:
        """Add multiple points to the collection."""
        if isinstance(points, Points3DArray):
            if points.size > 0:
                self._data = np.vstack([self._data, points._data])
        else:
            for point in points:
                self.append(point)

    def insert(self, index: int, point: Point3D) -> None:
        """Insert a point at the specified index."""
        new_point = np.array([[point.x, point.y, point.z]], dtype=np.float64)
        self._data = np.insert(self._data, index, new_point, axis=0)

    def remove(self, index: int) -> Point3D:
        """Remove and return the point at the specified index."""
        if index >= self.size or index < -self.size:
            raise IndexError("Point index out of range")

        removed_point = self._data[index]
        self._data = np.delete(self._data, index, axis=0)
        return Point3D(removed_point[0], removed_point[1], removed_point[2])

    def clear(self) -> None:
        """Remove all points from the collection."""
        self._data = np.empty((0, 3), dtype=np.float64)

    def copy(self) -> Points3DArray:
        """Create a copy of the Points collection."""
        return Points3DArray(self._data.copy())

    def filter(self, condition: np.ndarray) -> Points3DArray:
        """Filter points based on a boolean condition array."""
        return Points3DArray(self._data[condition])

    def closest_to(self, point: Point3D, k: int = 1) -> Point3D | Points3DArray:
        """Find the k closest points to the given point."""
        if self.size == 0:
            raise ValueError("Cannot find closest points in empty collection")

        distances = np.linalg.norm(self._data - np.array([point.x, point.y, point.z]), axis=1)
        indices = np.argsort(distances)[:k]

        if k == 1:
            closest_data = self._data[indices[0]]
            return Point3D(closest_data[0], closest_data[1], closest_data[2])
        else:
            return Points3DArray(self._data[indices])

    def farthest_from(self, point: Point3D, k: int = 1) -> Point3D | Points3DArray:
        """Find the k farthest points from the given point."""
        if self.size == 0:
            raise ValueError("Cannot find farthest points in empty collection")

        distances = np.linalg.norm(self._data - np.array([point.x, point.y, point.z]), axis=1)
        indices = np.argsort(distances)[-k:]

        if k == 1:
            farthest_data = self._data[indices[0]]
            return Point3D(farthest_data[0], farthest_data[1], farthest_data[2])
        else:
            return Points3DArray(self._data[indices])

    def distances_to(self, point: Point3D) -> np.ndarray:
        """Calculate distances from all points to the given point."""
        return np.linalg.norm(self._data - np.array([point.x, point.y, point.z]), axis=1)

    def distances_between(self) -> np.ndarray:
        """Calculate pairwise distances between all points."""
        if self.size == 0:
            return np.array([])

        # Use broadcasting for efficient pairwise distance calculation
        diff = self._data[:, np.newaxis, :] - self._data[np.newaxis, :, :]
        return np.linalg.norm(diff, axis=2)

    def translate(self, dx: float, dy: float, dz: float = 0.0) -> Points3DArray:
        """Translate all points by the given offsets."""
        translated_data = self._data + np.array([dx, dy, dz])
        return Points3DArray(translated_data)

    def scale(self, factor: float, center: Point3D | None = None) -> Points3DArray:
        """Scale all points by a factor around a center."""
        if center is None:
            center = self.centroid

        center_array = np.array([center.x, center.y, center.z])
        scaled_data = (self._data - center_array) * factor + center_array
        return Points3DArray(scaled_data)

    def rotate_2d(self, angle: float, center: Point3D | None = None) -> Points3DArray:
        """Rotate all points in 2D around a center."""
        if center is None:
            center = self.centroid

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Translate to origin
        translated = self._data - np.array([center.x, center.y, center.z])

        # Rotate
        rotated = translated.copy()
        rotated[:, 0] = translated[:, 0] * cos_a - translated[:, 1] * sin_a
        rotated[:, 1] = translated[:, 0] * sin_a + translated[:, 1] * cos_a

        # Translate back
        rotated += np.array([center.x, center.y, center.z])

        return Points3DArray(rotated)

    def normalize(self) -> Points3DArray:
        """Normalize all points to unit vectors."""
        magnitudes = np.linalg.norm(self._data, axis=1)
        non_zero_mask = magnitudes != 0

        normalized_data = self._data.copy()
        normalized_data[non_zero_mask] = self._data[non_zero_mask] / magnitudes[non_zero_mask, np.newaxis]

        return Points3DArray(normalized_data)

    def clamp(self, min_point: Point3D, max_point: Point3D) -> Points3DArray:
        """Clamp all points to be within bounds."""
        min_array = np.array([min_point.x, min_point.y, min_point.z])
        max_array = np.array([max_point.x, max_point.y, max_point.z])
        clamped_data = np.clip(self._data, min_array, max_array)
        return Points3DArray(clamped_data)

    def smooth(self, window_size: int = 3) -> Points3DArray:
        """Apply smoothing to the points (useful for trajectories)."""
        if self.size < window_size:
            return self.copy()

        smoothed_data = np.zeros_like(self._data)
        half_window = window_size // 2

        for i in range(self.size):
            start_idx = max(0, i - half_window)
            end_idx = min(self.size, i + half_window + 1)
            smoothed_data[i] = np.mean(self._data[start_idx:end_idx], axis=0)

        return Points3DArray(smoothed_data)

    def resample(self, num_points: int, method: str = "linear") -> Points3DArray:
        """Resample the points to a different number of points."""
        if self.size == 0:
            return Points3DArray.empty()

        if self.size == 1:
            return Points3DArray(np.tile(self._data[0], (num_points, 1)))

        if method == "linear":
            # Linear interpolation along the path
            old_indices = np.arange(self.size)
            new_indices = np.linspace(0, self.size - 1, num_points)

            resampled_data = np.zeros((num_points, 3))
            for i in range(3):
                resampled_data[:, i] = np.interp(new_indices, old_indices, self._data[:, i])

            return Points3DArray(resampled_data)
        else:
            raise ValueError(f"Unknown resampling method: {method}")

    def subsample(self, step: int) -> Points3DArray:
        """Subsample points by taking every nth point."""
        return Points3DArray(self._data[::step])

    def reverse(self) -> Points3DArray:
        """Reverse the order of points."""
        return Points3DArray(self._data[::-1])

    def unique(self, tolerance: float = 1e-9) -> Points3DArray:
        """Remove duplicate points within tolerance."""
        if self.size <= 1:
            return self.copy()

        # Use a simple approach for small collections
        unique_indices = []
        for i in range(self.size):
            is_unique = True
            for j in unique_indices:
                if np.allclose(self._data[i], self._data[j], atol=tolerance):
                    is_unique = False
                    break
            if is_unique:
                unique_indices.append(i)

        return Points3DArray(self._data[unique_indices])

    def to_points(self) -> list[Point3D]:
        """Convert to a list of Point objects."""
        return [Point3D(row[0], row[1], row[2]) for row in self._data]

    def to_2d(self) -> np.ndarray:
        """Get 2D coordinates as (N, 2) array."""
        return self._data[:, :2]

    def to_3d(self) -> np.ndarray:
        """Get 3D coordinates as (N, 3) array."""
        return self._data.copy()

    def __len__(self) -> int:
        """Number of points in the collection."""
        return self.size

    def __getitem__(self, key: int | slice | np.ndarray) -> Point3D | Points3DArray:
        """Get point(s) by index or slice."""
        if isinstance(key, int):
            if key >= self.size or key < -self.size:
                raise IndexError("Point index out of range")
            point_data = self._data[key]
            return Point3D(point_data[0], point_data[1], point_data[2])
        elif isinstance(key, slice) or isinstance(key, np.ndarray):
            return Points3DArray(self._data[key])
        else:
            raise TypeError("Index must be int, slice, or numpy array")

    def __setitem__(self, key: int | slice, value: Point3D | Points3DArray) -> None:
        """Set point(s) by index or slice."""
        if isinstance(key, int):
            if key >= self.size or key < -self.size:
                raise IndexError("Point index out of range")
            if isinstance(value, Point3D):
                self._data[key] = [value.x, value.y, value.z]
            else:
                raise TypeError("Value must be a Point when setting single index")
        elif isinstance(key, slice):
            if isinstance(value, Points3DArray):
                self._data[key] = value._data
            else:
                raise TypeError("Value must be Points when setting slice")
        else:
            raise TypeError("Index must be int or slice")

    def __iter__(self) -> Iterator[Point3D]:
        """Iterate over points."""
        for row in self._data:
            yield Point3D(row[0], row[1], row[2])

    def __repr__(self) -> str:
        """String representation of the Points collection."""
        return f"Points({self.size} points)"

    def __str__(self) -> str:
        """User-friendly string representation."""
        if self.size == 0:
            return "Points(empty)"
        elif self.size <= 5:
            points_str = ", ".join(str(Point3D(row[0], row[1], row[2])) for row in self._data)
            return f"Points([{points_str}])"
        else:
            first_few = ", ".join(str(Point3D(row[0], row[1], row[2])) for row in self._data[:3])
            return f"Points([{first_few}, ... ({self.size} total)])"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Points collection."""
        if not isinstance(other, Points3DArray):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Points collection."""
        return not self.__eq__(other)

    def __add__(self, other: Points3DArray | Point3D | float | np.ndarray) -> Points3DArray:
        """Add to all points."""
        if isinstance(other, Points3DArray):
            if self.size != other.size:
                raise ValueError("Points collections must have the same size")
            return Points3DArray(self._data + other._data)
        elif isinstance(other, Point3D):
            return Points3DArray(self._data + np.array([other.x, other.y, other.z]))
        elif isinstance(other, (int, float)) or isinstance(other, np.ndarray):
            return Points3DArray(self._data + other)
        else:
            return NotImplemented

    def __sub__(self, other: Points3DArray | Point3D | float | np.ndarray) -> Points3DArray:
        """Subtract from all points."""
        if isinstance(other, Points3DArray):
            if self.size != other.size:
                raise ValueError("Points collections must have the same size")
            return Points3DArray(self._data - other._data)
        elif isinstance(other, Point3D):
            return Points3DArray(self._data - np.array([other.x, other.y, other.z]))
        elif isinstance(other, (int, float)) or isinstance(other, np.ndarray):
            return Points3DArray(self._data - other)
        else:
            return NotImplemented

    def __mul__(self, other: float | np.ndarray) -> Points3DArray:
        """Multiply all points by a scalar or array."""
        if isinstance(other, (int, float)) or isinstance(other, np.ndarray):
            return Points3DArray(self._data * other)
        else:
            return NotImplemented

    def __truediv__(self, other: float | np.ndarray) -> Points3DArray:
        """Divide all points by a scalar or array."""
        if isinstance(other, (int, float)) or isinstance(other, np.ndarray):
            return Points3DArray(self._data / other)
        else:
            return NotImplemented

    def __contains__(self, point: Point3D) -> bool:
        """Check if a point is in the collection."""
        return any(np.allclose(row, [point.x, point.y, point.z]) for row in self._data)
