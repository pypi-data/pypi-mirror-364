"""
UTM Trajectory schema for efficient storage and manipulation of point sequences.
"""

from typing import List, Optional, Tuple, Union
import numpy as np
from pydantic import BaseModel, Field, validator, root_validator
from numpy.typing import NDArray

from lcvtoolbox.core.schemas.utm.point import UTMPoint


class UTMTrajectory(BaseModel):
    """
    UTM trajectory storing a sequence of points efficiently.

    Uses numpy arrays for internal storage while maintaining compatibility
    with lists of UTMPoint objects for import/export operations.
    All points must be in the same UTM zone.
    """

    # Internal storage as numpy array
    _points_array: Optional[NDArray[np.float64]] = None
    zone_number: int = Field(..., ge=1, le=60, description="UTM zone number (1-60)")
    zone_letter: str = Field(..., pattern="^[C-X]$", description="UTM zone letter (C-X, excluding I and O)")
    has_height: bool = Field(False, description="Whether the trajectory includes height values")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
        json_schema_extra = {
            "example": {
                "points": [
                    {"easting": 448262.0, "northing": 5411932.0, "zone_number": 31, "zone_letter": "U"},
                    {"easting": 448263.0, "northing": 5411933.0, "zone_number": 31, "zone_letter": "U"},
                    {"easting": 448264.0, "northing": 5411934.0, "zone_number": 31, "zone_letter": "U"}
                ],
                "zone_number": 31,
                "zone_letter": "U",
                "has_height": False
            }
        }

    @classmethod
    def from_points(cls, points: List[UTMPoint]) -> "UTMTrajectory":
        """
        Create a UTMTrajectory from a list of UTMPoint objects.

        All points must be in the same UTM zone.

        Args:
            points: List of UTMPoint objects.

        Returns:
            UTMTrajectory: A new trajectory instance.

        Raises:
            ValueError: If points list is empty or points are in different zones.

        Example:
            >>> points = [
            ...     UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U'),
            ...     UTMPoint(easting=448263.0, northing=5411933.0, zone_number=31, zone_letter='U')
            ... ]
            >>> trajectory = UTMTrajectory.from_points(points)
        """
        if not points:
            raise ValueError("Cannot create trajectory from empty points list")

        # Validate all points are in same zone
        first_point = points[0]
        zone_number = first_point.zone_number
        zone_letter = first_point.zone_letter

        for i, point in enumerate(points[1:], 1):
            if point.zone_number != zone_number or point.zone_letter != zone_letter:
                raise ValueError(
                    f"All points must be in the same UTM zone. Point at index {i} is in "
                    f"{point.zone_number}{point.zone_letter}, expected {zone_number}{zone_letter}"
                )

        # Check if any points have height
        has_height = any(p.height is not None for p in points)

        # Create numpy array
        if has_height:
            # Use 3 columns (easting, northing, height)
            points_array = np.zeros((len(points), 3), dtype=np.float64)
            for i, point in enumerate(points):
                points_array[i, 0] = point.easting
                points_array[i, 1] = point.northing
                points_array[i, 2] = point.height if point.height is not None else np.nan
        else:
            # Use 2 columns (easting, northing)
            points_array = np.zeros((len(points), 2), dtype=np.float64)
            for i, point in enumerate(points):
                points_array[i, 0] = point.easting
                points_array[i, 1] = point.northing

        # Create instance
        instance = cls(
            zone_number=zone_number,
            zone_letter=zone_letter,
            has_height=has_height
        )
        instance._points_array = points_array
        return instance

    def to_points(self) -> List[UTMPoint]:
        """
        Convert the trajectory to a list of UTMPoint objects.

        Returns:
            List[UTMPoint]: List of points in the trajectory.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> points = trajectory.to_points()
            >>> for point in points:
            ...     print(f"Point: {point.x}, {point.y}")
        """
        if self._points_array is None:
            return []

        points = []
        for i in range(len(self._points_array)):
            if self.has_height:
                height = self._points_array[i, 2]
                # Convert NaN to None
                height = None if np.isnan(height) else float(height)
            else:
                height = None

            point = UTMPoint(
                easting=float(self._points_array[i, 0]),
                northing=float(self._points_array[i, 1]),
                zone_number=self.zone_number,
                zone_letter=self.zone_letter,
                height=height
            )
            points.append(point)

        return points

    @property
    def points(self) -> List[UTMPoint]:
        """
        Property to access points as a list of UTMPoint objects.

        This is provided for convenience and Pydantic serialization.

        Returns:
            List[UTMPoint]: List of points in the trajectory.
        """
        return self.to_points()

    @points.setter
    def points(self, points: List[UTMPoint]) -> None:
        """
        Set points from a list of UTMPoint objects.

        Args:
            points: List of UTMPoint objects.
        """
        if not points:
            self._points_array = None
            return

        # Validate and convert
        trajectory = UTMTrajectory.from_points(points)
        self._points_array = trajectory._points_array
        self.zone_number = trajectory.zone_number
        self.zone_letter = trajectory.zone_letter
        self.has_height = trajectory.has_height

    def __len__(self) -> int:
        """
        Get the number of points in the trajectory.

        Returns:
            int: Number of points.
        """
        if self._points_array is None:
            return 0
        return len(self._points_array)

    def __getitem__(self, index: Union[int, slice]) -> Union[UTMPoint, List[UTMPoint]]:
        """
        Get point(s) by index or slice.

        Args:
            index: Integer index or slice.

        Returns:
            UTMPoint or List[UTMPoint]: Single point or list of points.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> first_point = trajectory[0]
            >>> last_three = trajectory[-3:]
        """
        if self._points_array is None:
            raise IndexError("Trajectory is empty")

        if isinstance(index, int):
            # Single point
            if index < -len(self) or index >= len(self):
                raise IndexError(f"Index {index} out of range for trajectory of length {len(self)}")

            # Handle negative indices
            if index < 0:
                index = len(self) + index

            if self.has_height:
                height = self._points_array[index, 2]
                height = None if np.isnan(height) else float(height)
            else:
                height = None

            return UTMPoint(
                easting=float(self._points_array[index, 0]),
                northing=float(self._points_array[index, 1]),
                zone_number=self.zone_number,
                zone_letter=self.zone_letter,
                height=height
            )
        else:
            # Slice - return list of points
            sliced_array = self._points_array[index]
            points = []
            for i in range(len(sliced_array)):
                if self.has_height:
                    height = sliced_array[i, 2]
                    height = None if np.isnan(height) else float(height)
                else:
                    height = None

                point = UTMPoint(
                    easting=float(sliced_array[i, 0]),
                    northing=float(sliced_array[i, 1]),
                    zone_number=self.zone_number,
                    zone_letter=self.zone_letter,
                    height=height
                )
                points.append(point)
            return points

    def get_coordinates_array(self) -> NDArray[np.float64]:
        """
        Get the raw numpy array of coordinates.

        Returns a copy to prevent external modifications.

        Returns:
            NDArray: Numpy array of shape (n_points, 2) or (n_points, 3) if height is included.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> coords = trajectory.get_coordinates_array()
            >>> print(f"Shape: {coords.shape}")
        """
        if self._points_array is None:
            return np.array([], dtype=np.float64).reshape(0, 3 if self.has_height else 2)
        return self._points_array.copy()

    def append(self, point: UTMPoint) -> None:
        """
        Append a point to the trajectory.

        Args:
            point: UTMPoint to append.

        Raises:
            ValueError: If point is in a different UTM zone.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> new_point = UTMPoint(easting=448265.0, northing=5411935.0, zone_number=31, zone_letter='U')
            >>> trajectory.append(new_point)
        """
        if point.zone_number != self.zone_number or point.zone_letter != self.zone_letter:
            raise ValueError(
                f"Cannot append point in zone {point.zone_number}{point.zone_letter} "
                f"to trajectory in zone {self.zone_number}{self.zone_letter}"
            )

        if self._points_array is None:
            # First point
            self.has_height = point.height is not None
            if self.has_height:
                self._points_array = np.array([[point.easting, point.northing, point.height]], dtype=np.float64)
            else:
                self._points_array = np.array([[point.easting, point.northing]], dtype=np.float64)
        else:
            # Add to existing array
            if self.has_height:
                height_val = point.height if point.height is not None else np.nan
                new_row = np.array([[point.easting, point.northing, height_val]])
            else:
                new_row = np.array([[point.easting, point.northing]])
            self._points_array = np.vstack([self._points_array, new_row])

    def extend(self, points: List[UTMPoint]) -> None:
        """
        Extend the trajectory with multiple points.

        Args:
            points: List of UTMPoint objects to append.

        Raises:
            ValueError: If any point is in a different UTM zone.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> new_points = [point1, point2, point3]
            >>> trajectory.extend(new_points)
        """
        for point in points:
            self.append(point)

    def total_distance(self) -> float:
        """
        Calculate the total distance along the trajectory.

        Returns:
            float: Total distance in meters.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> distance = trajectory.total_distance()
            >>> print(f"Total distance: {distance:.2f} meters")
        """
        if self._points_array is None or len(self._points_array) < 2:
            return 0.0

        # Calculate distances between consecutive points
        diffs = np.diff(self._points_array[:, :2], axis=0)  # Only use x,y for distance
        distances = np.sqrt(np.sum(diffs**2, axis=1))
        return float(np.sum(distances))

    def to_dict(self) -> dict:
        """
        Convert the trajectory to a dictionary.

        Returns:
            dict: Dictionary representation with points as list.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> data = trajectory.to_dict()
        """
        return {
            "points": [p.to_dict() for p in self.to_points()],
            "zone_number": self.zone_number,
            "zone_letter": self.zone_letter,
            "has_height": self.has_height
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UTMTrajectory":
        """
        Create a UTMTrajectory from a dictionary.

        Args:
            data: Dictionary containing trajectory data.

        Returns:
            UTMTrajectory: New trajectory instance.

        Example:
            >>> data = {
            ...     "points": [...],
            ...     "zone_number": 31,
            ...     "zone_letter": "U",
            ...     "has_height": False
            ... }
            >>> trajectory = UTMTrajectory.from_dict(data)
        """
        points = [UTMPoint.from_dict(p) for p in data.get("points", [])]
        
        if points:
            return cls.from_points(points)
        else:
            # Empty trajectory
            return cls(
                zone_number=data["zone_number"],
                zone_letter=data["zone_letter"],
                has_height=data.get("has_height", False)
            )

    def resample(self, n_points: int) -> "UTMTrajectory":
        """
        Resample the trajectory to have exactly n_points.

        Uses linear interpolation along the trajectory.

        Args:
            n_points: Number of points in the resampled trajectory.

        Returns:
            UTMTrajectory: New trajectory with n_points.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> resampled = trajectory.resample(100)
        """
        if self._points_array is None or len(self._points_array) < 2:
            raise ValueError("Cannot resample trajectory with less than 2 points")

        if n_points < 2:
            raise ValueError("Resampled trajectory must have at least 2 points")

        # Calculate cumulative distances
        diffs = np.diff(self._points_array[:, :2], axis=0)
        segment_distances = np.sqrt(np.sum(diffs**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(segment_distances)])
        total_distance = cumulative_distances[-1]

        # Create evenly spaced distances
        new_distances = np.linspace(0, total_distance, n_points)

        # Interpolate coordinates
        new_easting = np.interp(new_distances, cumulative_distances, self._points_array[:, 0])
        new_northing = np.interp(new_distances, cumulative_distances, self._points_array[:, 1])

        # Handle height if present
        if self.has_height:
            new_height = np.interp(new_distances, cumulative_distances, self._points_array[:, 2])
            new_array = np.column_stack([new_easting, new_northing, new_height])
        else:
            new_array = np.column_stack([new_easting, new_northing])

        # Create new trajectory
        instance = UTMTrajectory(
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            has_height=self.has_height
        )
        instance._points_array = new_array
        return instance

    def _interpolate_between_points(self, point1: UTMPoint, point2: UTMPoint, t: float) -> UTMPoint:
        """
        Interpolate between two UTM points.

        Args:
            point1: First point (t=0).
            point2: Second point (t=1).
            t: Interpolation parameter between 0 and 1.

        Returns:
            UTMPoint: Interpolated point.

        Example:
            >>> p1 = UTMPoint(easting=100, northing=200, zone_number=31, zone_letter='U')
            >>> p2 = UTMPoint(easting=200, northing=300, zone_number=31, zone_letter='U')
            >>> mid = trajectory._interpolate_between_points(p1, p2, 0.5)
        """
        # Linear interpolation
        easting = point1.easting + t * (point2.easting - point1.easting)
        northing = point1.northing + t * (point2.northing - point1.northing)
        
        # Handle height if both points have it
        height = None
        if point1.height is not None and point2.height is not None:
            height = point1.height + t * (point2.height - point1.height)
        
        return UTMPoint(
            easting=easting,
            northing=northing,
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            height=height
        )

    def get_point_at_arc_length(self, arc_length: float) -> UTMPoint:
        """
        Get the interpolated point at a specific arc length along the trajectory.

        Arc length is the distance from the start of the trajectory.

        Args:
            arc_length: Distance from the start in meters.

        Returns:
            UTMPoint: Interpolated point at the specified arc length.

        Raises:
            ValueError: If arc_length is negative or exceeds total trajectory length.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> total = trajectory.total_distance()
            >>> midpoint = trajectory.get_point_at_arc_length(total / 2)
            >>> print(f"Midpoint: {midpoint.x:.2f}, {midpoint.y:.2f}")
        """
        if self._points_array is None or len(self._points_array) == 0:
            raise ValueError("Cannot get point from empty trajectory")

        if arc_length < 0:
            raise ValueError(f"Arc length must be non-negative, got {arc_length}")

        # Handle single point trajectory
        if len(self._points_array) == 1:
            if arc_length > 0:
                raise ValueError("Arc length exceeds trajectory length (single point)")
            return self[0]  # type: ignore

        # Calculate cumulative distances
        diffs = np.diff(self._points_array[:, :2], axis=0)
        segment_distances = np.sqrt(np.sum(diffs**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(segment_distances)])
        total_distance = cumulative_distances[-1]

        if arc_length > total_distance:
            raise ValueError(
                f"Arc length {arc_length:.2f} exceeds total trajectory length {total_distance:.2f}"
            )

        # Handle edge cases
        if arc_length == 0:
            return self[0]  # type: ignore
        if arc_length == total_distance:
            return self[-1]  # type: ignore

        # Find the segment containing the arc length
        segment_idx = int(np.searchsorted(cumulative_distances, arc_length) - 1)
        
        # Calculate position within the segment
        segment_start_distance = cumulative_distances[segment_idx]
        segment_length = segment_distances[segment_idx]
        distance_in_segment = arc_length - segment_start_distance
        
        # Interpolation parameter (0 to 1)
        t = distance_in_segment / segment_length
        
        # Get the two points - we know these are UTMPoint because we're using int indices
        point1: UTMPoint = self[segment_idx]  # type: ignore
        point2: UTMPoint = self[segment_idx + 1]  # type: ignore
        
        # Interpolate
        return self._interpolate_between_points(point1, point2, t)

    def get_cumulative_distances(self) -> NDArray[np.float64]:
        """
        Get cumulative distances along the trajectory.

        Returns:
            NDArray: Array of cumulative distances from the start, same length as trajectory.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> distances = trajectory.get_cumulative_distances()
            >>> print(f"Distance to last point: {distances[-1]:.2f} meters")
        """
        if self._points_array is None or len(self._points_array) == 0:
            return np.array([], dtype=np.float64)
        
        if len(self._points_array) == 1:
            return np.array([0.0], dtype=np.float64)
        
        # Calculate distances between consecutive points
        diffs = np.diff(self._points_array[:, :2], axis=0)
        segment_distances = np.sqrt(np.sum(diffs**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(segment_distances)])
        
        return cumulative_distances

    def __iter__(self):
        """
        Iterate over points in the trajectory.

        Yields:
            UTMPoint: Each point in the trajectory.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> for point in trajectory:
            ...     print(f"Point: {point.x}, {point.y}")
        """
        for i in range(len(self)):
            yield self[i]

    def __contains__(self, point: UTMPoint) -> bool:
        """
        Check if a point exists in the trajectory.

        Args:
            point: UTMPoint to check.

        Returns:
            bool: True if the exact point exists in the trajectory.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> point = trajectory[0]
            >>> print(point in trajectory)  # True
        """
        if self._points_array is None or len(self._points_array) == 0:
            return False
        
        # Check zone first
        if point.zone_number != self.zone_number or point.zone_letter != self.zone_letter:
            return False
        
        # Check coordinates
        for i in range(len(self._points_array)):
            if (self._points_array[i, 0] == point.easting and 
                self._points_array[i, 1] == point.northing):
                # Check height if trajectory has it
                if self.has_height:
                    stored_height = self._points_array[i, 2]
                    stored_height = None if np.isnan(stored_height) else stored_height
                    if stored_height == point.height:
                        return True
                else:
                    # No height to check
                    return True
        return False

    def insert(self, index: int, point: UTMPoint) -> None:
        """
        Insert a point at the specified index.

        Args:
            index: Index where to insert the point.
            point: UTMPoint to insert.

        Raises:
            ValueError: If point is in a different UTM zone.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> new_point = UTMPoint(easting=100, northing=200, zone_number=31, zone_letter='U')
            >>> trajectory.insert(1, new_point)
        """
        if point.zone_number != self.zone_number or point.zone_letter != self.zone_letter:
            raise ValueError(
                f"Cannot insert point in zone {point.zone_number}{point.zone_letter} "
                f"to trajectory in zone {self.zone_number}{self.zone_letter}"
            )

        if self._points_array is None:
            # Empty trajectory, just append
            self.append(point)
            return

        # Handle negative indices
        if index < 0:
            index = len(self) + index + 1
        
        # Clamp index to valid range
        index = max(0, min(index, len(self)))

        # Create new row
        if self.has_height:
            new_row = np.array([[point.easting, point.northing, 
                               point.height if point.height is not None else np.nan]])
        else:
            new_row = np.array([[point.easting, point.northing]])

        # Insert into array
        self._points_array = np.insert(self._points_array, index, new_row, axis=0)

    def remove(self, point: UTMPoint) -> None:
        """
        Remove the first occurrence of a point from the trajectory.

        Args:
            point: UTMPoint to remove.

        Raises:
            ValueError: If the point is not found in the trajectory.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> point = trajectory[0]
            >>> trajectory.remove(point)
        """
        if self._points_array is None:
            raise ValueError("Point not found in empty trajectory")

        # Find the point
        for i in range(len(self)):
            if self[i] == point or (
                self._points_array[i, 0] == point.easting and 
                self._points_array[i, 1] == point.northing and
                point.zone_number == self.zone_number and 
                point.zone_letter == self.zone_letter
            ):
                # Remove the point
                self._points_array = np.delete(self._points_array, i, axis=0)
                return

        raise ValueError("Point not found in trajectory")

    def pop(self, index: int = -1) -> UTMPoint:
        """
        Remove and return a point at the given index.

        Args:
            index: Index of the point to remove (default: -1, last point).

        Returns:
            UTMPoint: The removed point.

        Raises:
            IndexError: If the trajectory is empty or index is out of range.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> last_point = trajectory.pop()
            >>> first_point = trajectory.pop(0)
        """
        if self._points_array is None or len(self._points_array) == 0:
            raise IndexError("pop from empty trajectory")

        # Get the point before removing
        point = self[index]
        
        # Calculate actual index for negative indices
        if index < 0:
            index = len(self) + index

        # Remove from array
        self._points_array = np.delete(self._points_array, index, axis=0)
        
        # If array is now empty, set to None
        if len(self._points_array) == 0:
            self._points_array = None
        
        return point  # type: ignore

    def clear(self) -> None:
        """
        Remove all points from the trajectory.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> trajectory.clear()
            >>> print(len(trajectory))  # 0
        """
        self._points_array = None

    def index(self, point: UTMPoint, start: int = 0, stop: Optional[int] = None) -> int:
        """
        Return the index of the first occurrence of the point.

        Args:
            point: UTMPoint to find.
            start: Start searching from this index.
            stop: Stop searching at this index.

        Returns:
            int: Index of the first occurrence.

        Raises:
            ValueError: If the point is not found.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> idx = trajectory.index(trajectory[2])
            >>> print(idx)  # 2
        """
        if self._points_array is None:
            raise ValueError("Point not found in empty trajectory")

        if stop is None:
            stop = len(self)

        for i in range(start, stop):
            if i >= len(self):
                break
            current: UTMPoint = self[i]  # type: ignore
            if (current.easting == point.easting and 
                current.northing == point.northing and
                current.zone_number == point.zone_number and
                current.zone_letter == point.zone_letter):
                # Check height if needed
                if self.has_height:
                    if current.height == point.height:
                        return i
                else:
                    return i

        raise ValueError("Point not found in trajectory")

    def reverse(self) -> None:
        """
        Reverse the trajectory in-place.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> trajectory.reverse()
        """
        if self._points_array is not None and len(self._points_array) > 1:
            self._points_array = np.flip(self._points_array, axis=0)

    def copy(self) -> "UTMTrajectory":
        """
        Create a shallow copy of the trajectory.

        Returns:
            UTMTrajectory: A new trajectory with the same points.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> copy = trajectory.copy()
        """
        instance = UTMTrajectory(
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            has_height=self.has_height
        )
        if self._points_array is not None:
            instance._points_array = self._points_array.copy()
        return instance

    def project_point(self, point: UTMPoint) -> UTMPoint:
        """
        Project a point onto the trajectory using the shortest distance.

        Finds the closest point on the trajectory to the given point.

        Args:
            point: UTMPoint to project onto the trajectory.

        Returns:
            UTMPoint: The closest point on the trajectory.

        Raises:
            ValueError: If the trajectory is empty or point is in different UTM zone.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> external_point = UTMPoint(easting=100, northing=200, zone_number=31, zone_letter='U')
            >>> projected = trajectory.project_point(external_point)
            >>> print(f"Projected to: {projected.x:.2f}, {projected.y:.2f}")
        """
        if self._points_array is None or len(self._points_array) == 0:
            raise ValueError("Cannot project point onto empty trajectory")

        if point.zone_number != self.zone_number or point.zone_letter != self.zone_letter:
            raise ValueError(
                f"Cannot project point in zone {point.zone_number}{point.zone_letter} "
                f"onto trajectory in zone {self.zone_number}{self.zone_letter}"
            )

        # Handle single point trajectory
        if len(self._points_array) == 1:
            return self[0]  # type: ignore

        # Initialize with first point
        min_distance = float('inf')
        best_point = self[0]  # type: ignore
        
        # Check each segment
        for i in range(len(self._points_array) - 1):
            # Get segment endpoints
            p1 = self._points_array[i]
            p2 = self._points_array[i + 1]
            
            # Vector from p1 to p2
            v = p2[:2] - p1[:2]  # Only use x,y
            
            # Vector from p1 to point
            w = np.array([point.easting, point.northing]) - p1[:2]
            
            # Project w onto v
            c1 = np.dot(w, v)
            if c1 <= 0:
                # Closest point is p1
                dist = np.linalg.norm(w)
                if dist < min_distance:
                    min_distance = dist
                    best_point = self[i]  # type: ignore
            else:
                c2 = np.dot(v, v)
                if c1 >= c2:
                    # Closest point is p2
                    w2 = np.array([point.easting, point.northing]) - p2[:2]
                    dist = np.linalg.norm(w2)
                    if dist < min_distance:
                        min_distance = dist
                        best_point = self[i + 1]  # type: ignore
                else:
                    # Closest point is on the segment
                    t = c1 / c2
                    projected_on_segment = p1[:2] + t * v
                    
                    # Distance from point to projected point
                    dist = np.linalg.norm(np.array([point.easting, point.northing]) - projected_on_segment)
                    
                    if dist < min_distance:
                        min_distance = dist
                        # Create interpolated point
                        point1: UTMPoint = self[i]  # type: ignore
                        point2: UTMPoint = self[i + 1]  # type: ignore
                        best_point = self._interpolate_between_points(point1, point2, t)
        
        # Also check the last point
        last_point_dist = np.sqrt(
            (point.easting - self._points_array[-1, 0])**2 + 
            (point.northing - self._points_array[-1, 1])**2
        )
        if last_point_dist < min_distance:
            best_point = self[-1]  # type: ignore
        
        return best_point  # type: ignore

    def distance_to_point(self, point: UTMPoint) -> float:
        """
        Calculate the minimum distance from a point to the trajectory.

        Args:
            point: UTMPoint to measure distance from.

        Returns:
            float: Minimum distance in meters.

        Raises:
            ValueError: If the trajectory is empty or point is in different UTM zone.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> external_point = UTMPoint(easting=100, northing=200, zone_number=31, zone_letter='U')
            >>> distance = trajectory.distance_to_point(external_point)
            >>> print(f"Distance to trajectory: {distance:.2f} meters")
        """
        projected = self.project_point(point)
        return point.distance_to(projected)

    def get_arc_length_of_point(self, point: UTMPoint) -> float:
        """
        Get the arc length coordinate of a point projected onto the trajectory.

        Projects the point onto the trajectory and returns the arc length
        (distance from start) of the projected point.

        Args:
            point: UTMPoint to project and get arc length for.

        Returns:
            float: Arc length in meters from the start of the trajectory.

        Raises:
            ValueError: If the trajectory is empty or point is in different UTM zone.

        Example:
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> external_point = UTMPoint(easting=50, northing=50, zone_number=31, zone_letter='U')
            >>> arc_length = trajectory.get_arc_length_of_point(external_point)
            >>> print(f"Point projects at {arc_length:.2f} meters along trajectory")
        """
        if self._points_array is None or len(self._points_array) == 0:
            raise ValueError("Cannot get arc length for empty trajectory")

        if point.zone_number != self.zone_number or point.zone_letter != self.zone_letter:
            raise ValueError(
                f"Cannot project point in zone {point.zone_number}{point.zone_letter} "
                f"onto trajectory in zone {self.zone_number}{self.zone_letter}"
            )

        # Handle single point trajectory
        if len(self._points_array) == 1:
            return 0.0

        # Calculate cumulative distances
        diffs = np.diff(self._points_array[:, :2], axis=0)
        segment_distances = np.sqrt(np.sum(diffs**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(segment_distances)])

        # Initialize with first point
        min_distance = float('inf')
        best_arc_length = 0.0
        
        # Check each segment
        for i in range(len(self._points_array) - 1):
            # Get segment endpoints
            p1 = self._points_array[i]
            p2 = self._points_array[i + 1]
            
            # Vector from p1 to p2
            v = p2[:2] - p1[:2]  # Only use x,y
            
            # Vector from p1 to point
            w = np.array([point.easting, point.northing]) - p1[:2]
            
            # Project w onto v
            c1 = np.dot(w, v)
            if c1 <= 0:
                # Closest point is p1
                dist = np.linalg.norm(w)
                if dist < min_distance:
                    min_distance = dist
                    best_arc_length = cumulative_distances[i]
            else:
                c2 = np.dot(v, v)
                if c1 >= c2:
                    # Closest point is p2
                    w2 = np.array([point.easting, point.northing]) - p2[:2]
                    dist = np.linalg.norm(w2)
                    if dist < min_distance:
                        min_distance = dist
                        best_arc_length = cumulative_distances[i + 1]
                else:
                    # Closest point is on the segment
                    t = c1 / c2
                    projected_on_segment = p1[:2] + t * v
                    
                    # Distance from point to projected point
                    dist = np.linalg.norm(np.array([point.easting, point.northing]) - projected_on_segment)
                    
                    if dist < min_distance:
                        min_distance = dist
                        # Calculate arc length at this position
                        segment_length = segment_distances[i]
                        best_arc_length = cumulative_distances[i] + t * segment_length
        
        # Also check the last point
        last_point_dist = np.sqrt(
            (point.easting - self._points_array[-1, 0])**2 + 
            (point.northing - self._points_array[-1, 1])**2
        )
        if last_point_dist < min_distance:
            best_arc_length = cumulative_distances[-1]
        
        return best_arc_length

    def project_polygon(self, polygon) -> Tuple[float, float]:
        """
        Project a UTMPolygon onto the trajectory and return arc length range.

        Finds the starting and ending arc length coordinates where the polygon
        projects onto the trajectory.

        Args:
            polygon: UTMPolygon to project onto the trajectory.

        Returns:
            Tuple[float, float]: (start_arc_length, end_arc_length) in meters.

        Raises:
            ValueError: If the trajectory is empty or polygon is in different UTM zone.

        Example:
            >>> from lcvtoolbox.core.schemas.utm.polygon import UTMPolygon
            >>> from shapely.geometry import Polygon as ShapelyPolygon
            >>> 
            >>> trajectory = UTMTrajectory.from_points([...])
            >>> poly = ShapelyPolygon([(40, -10), (60, -10), (60, 10), (40, 10)])
            >>> utm_poly = UTMPolygon(polygon=poly, zone_number=31, zone_letter='U')
            >>> start, end = trajectory.project_polygon(utm_poly)
            >>> print(f"Polygon projects from {start:.2f}m to {end:.2f}m")
        """
        from lcvtoolbox.core.schemas.utm.polygon import UTMPolygon
        
        if self._points_array is None or len(self._points_array) == 0:
            raise ValueError("Cannot project polygon onto empty trajectory")

        if polygon.zone_number != self.zone_number or polygon.zone_letter != self.zone_letter:
            raise ValueError(
                f"Cannot project polygon in zone {polygon.zone_number}{polygon.zone_letter} "
                f"onto trajectory in zone {self.zone_number}{self.zone_letter}"
            )

        # Get polygon boundary coordinates
        coords = list(polygon.polygon.exterior.coords)
        
        # Sample additional points along each edge for better coverage
        sampled_points = []
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            # Sample 10 points along each edge
            for t in np.linspace(0, 1, 10):
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                sampled_points.append((x, y))
        
        # Project all points and collect arc lengths
        arc_lengths = []
        for x, y in sampled_points:
            point = UTMPoint(
                easting=float(x),
                northing=float(y),
                zone_number=self.zone_number,
                zone_letter=self.zone_letter,
                height=None
            )
            arc_length = self.get_arc_length_of_point(point)
            arc_lengths.append(arc_length)
        
        # Return min and max arc lengths
        return (min(arc_lengths), max(arc_lengths))
