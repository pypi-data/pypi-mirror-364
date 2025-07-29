from __future__ import annotations

import numpy as np

from .point import Point3D
from .points_array import Points3DArray


class Points3DMap:
    """
    Represents a 2D map where each pixel contains a 3D point.

    This class is designed for computer vision applications where spatial data is organized
    in an image-like structure, such as depth maps, normal maps, or 3D reconstructions.

    Args:
        data: A numpy array of shape (H, W, 3) containing 3D coordinates

    Examples:
        >>> # Create from depth map
        >>> depth = np.random.rand(480, 640)
        >>> points_map = Points3DMap.from_depth_map(depth, fx=500, fy=500, cx=320, cy=240)
        >>>
        >>> # Access individual points
        >>> point = points_map[100, 200]  # Returns Point3D
        >>>
        >>> # Extract region
        >>> region = points_map.extract_region(100, 100, 50, 50)
        >>>
        >>> # Apply transformations
        >>> rotated = points_map.rotate_3d(np.array([0, 0, 1]), np.pi/4)
        >>> translated = points_map.translate(10, 20, 30)
    """

    __slots__ = ("_data",)  # Memory optimization

    def __init__(self, data: np.ndarray):
        """Initialize the Points3DMap with a numpy array of shape (H, W, 3)."""
        if data.ndim != 3 or data.shape[2] != 3:
            raise ValueError("Data must be a 3D numpy array with shape (H, W, 3).")
        self._data = data.astype(np.float64)

    @classmethod
    def zeros(cls, height: int, width: int) -> Points3DMap:
        """Create a map filled with zero points."""
        return cls(np.zeros((height, width, 3), dtype=np.float64))

    @classmethod
    def ones(cls, height: int, width: int) -> Points3DMap:
        """Create a map filled with ones."""
        return cls(np.ones((height, width, 3), dtype=np.float64))

    @classmethod
    def from_depth_map(cls, depth: np.ndarray, fx: float, fy: float, cx: float, cy: float, depth_scale: float = 1.0) -> Points3DMap:
        """
        Create a 3D points map from a depth image using camera intrinsics.

        Args:
            depth: Depth image as 2D numpy array
            fx: Focal length in x direction
            fy: Focal length in y direction
            cx: Principal point x coordinate
            cy: Principal point y coordinate
            depth_scale: Scale factor for depth values (default: 1.0)

        Returns:
            Points3DMap with 3D coordinates for each pixel
        """
        if depth.ndim != 2:
            raise ValueError("Depth must be a 2D array")

        height, width = depth.shape

        # Create pixel coordinate grids
        xx, yy = np.meshgrid(np.arange(width), np.arange(height))

        # Convert to 3D coordinates
        z = depth * depth_scale
        x = (xx - cx) * z / fx
        y = (yy - cy) * z / fy

        # Stack into (H, W, 3) array
        points_data = np.stack([x, y, z], axis=-1)

        return cls(points_data)

    @classmethod
    def from_normal_map(cls, normals: np.ndarray, scale: float = 1.0) -> Points3DMap:
        """
        Create a points map from surface normals.

        Args:
            normals: Normal map as (H, W, 3) array
            scale: Scale factor for the normals

        Returns:
            Points3DMap with scaled normal vectors
        """
        if normals.ndim != 3 or normals.shape[2] != 3:
            raise ValueError("Normals must be a 3D array with shape (H, W, 3)")

        return cls(normals * scale)

    @classmethod
    def from_uv_map(cls, u: np.ndarray, v: np.ndarray, z: float = 0.0) -> Points3DMap:
        """
        Create a points map from UV coordinates.

        Args:
            u: U coordinates as 2D array
            v: V coordinates as 2D array
            z: Constant Z value for all points

        Returns:
            Points3DMap with (u, v, z) coordinates
        """
        if u.shape != v.shape:
            raise ValueError("U and V arrays must have the same shape")

        if u.ndim != 2:
            raise ValueError("U and V must be 2D arrays")

        height, width = u.shape
        z_array = np.full((height, width), z)
        points_data = np.stack([u, v, z_array], axis=-1)

        return cls(points_data)

    @property
    def data(self) -> np.ndarray:
        """Get the underlying numpy array."""
        return self._data

    @property
    def shape(self) -> tuple[int, int]:
        """Get the shape of the map as (height, width)."""
        return self._data.shape[:2]

    @property
    def height(self) -> int:
        """Get the height of the map."""
        return self._data.shape[0]

    @property
    def width(self) -> int:
        """Get the width of the map."""
        return self._data.shape[1]

    @property
    def size(self) -> int:
        """Get the total number of points in the map."""
        return self.height * self.width

    @property
    def x(self) -> np.ndarray:
        """Get all x coordinates as a 2D array."""
        return self._data[:, :, 0]

    @property
    def y(self) -> np.ndarray:
        """Get all y coordinates as a 2D array."""
        return self._data[:, :, 1]

    @property
    def z(self) -> np.ndarray:
        """Get all z coordinates as a 2D array."""
        return self._data[:, :, 2]

    @property
    def mean(self) -> Point3D:
        """Calculate the mean point across the entire map."""
        mean_vals = np.mean(self._data.reshape(-1, 3), axis=0)
        return Point3D(mean_vals[0], mean_vals[1], mean_vals[2])

    @property
    def centroid(self) -> Point3D:
        """Calculate the centroid (alias for mean)."""
        return self.mean

    @property
    def bounds(self) -> tuple[Point3D, Point3D]:
        """Get the bounding box as (min_point, max_point)."""
        reshaped = self._data.reshape(-1, 3)
        min_coords = np.min(reshaped, axis=0)
        max_coords = np.max(reshaped, axis=0)
        return (Point3D(min_coords[0], min_coords[1], min_coords[2]), Point3D(max_coords[0], max_coords[1], max_coords[2]))

    @property
    def magnitude_map(self) -> np.ndarray:
        """Get the magnitude of each point as a 2D array."""
        return np.linalg.norm(self._data, axis=2)

    def __getitem__(self, index: tuple[int, int] | tuple[slice, slice]) -> Point3D | Points3DMap:
        """
        Get the 3D point(s) at the specified index.

        Args:
            index: Either (y, x) for single point or (y_slice, x_slice) for region

        Returns:
            Point3D for single index, Points3DMap for slices
        """
        if isinstance(index[0], slice) or isinstance(index[1], slice):
            return Points3DMap(self._data[index[0], index[1]])
        else:
            y, x = index
            return Point3D(*self._data[y, x])

    def __setitem__(self, index: tuple[int, int], value: Point3D) -> None:
        """Set the 3D point at the specified (y, x) pixel location."""
        y, x = index
        self._data[y, x] = [value.x, value.y, value.z]

    def to_numpy(self) -> np.ndarray:
        """Convert the map to a numpy array."""
        return self._data.copy()

    def to_points_array(self) -> Points3DArray:
        """Convert the map to a Points3DArray (flattened)."""
        reshaped = self._data.reshape(-1, 3)
        return Points3DArray(reshaped)

    def extract_region(self, y: int, x: int, height: int, width: int) -> Points3DMap:
        """
        Extract a rectangular region from the map.

        Args:
            y: Top-left y coordinate
            x: Top-left x coordinate
            height: Height of the region
            width: Width of the region

        Returns:
            New Points3DMap containing the extracted region
        """
        return Points3DMap(self._data[y : y + height, x : x + width])

    def sample_points(self, num_points: int, method: str = "uniform") -> Points3DArray:
        """
        Sample points from the map.

        Args:
            num_points: Number of points to sample
            method: Sampling method ("uniform" or "random")

        Returns:
            Points3DArray containing sampled points
        """
        if method == "uniform":
            # Uniform sampling across the image
            total_points = self.size
            if num_points >= total_points:
                return self.to_points_array()

            indices = np.linspace(0, total_points - 1, num_points, dtype=int)
            flat_data = self._data.reshape(-1, 3)
            return Points3DArray(flat_data[indices])

        elif method == "random":
            # Random sampling
            flat_data = self._data.reshape(-1, 3)
            indices = np.random.choice(len(flat_data), num_points, replace=False)
            return Points3DArray(flat_data[indices])

        else:
            raise ValueError(f"Unknown sampling method: {method}")

    def apply_mask(self, mask: np.ndarray) -> Points3DArray:
        """
        Extract points where mask is True.

        Args:
            mask: Boolean mask of shape (H, W)

        Returns:
            Points3DArray containing points where mask is True
        """
        if mask.shape != self.shape:
            raise ValueError("Mask shape must match map shape")

        points = self._data[mask]
        return Points3DArray(points)

    def translate(self, dx: float, dy: float, dz: float) -> Points3DMap:
        """Translate all points by the given offsets."""
        translated = self._data + np.array([dx, dy, dz])
        return Points3DMap(translated)

    def scale(self, factor: float, center: Point3D | None = None) -> Points3DMap:
        """Scale all points by a factor around a center."""
        if center is None:
            center = self.centroid

        center_array = np.array([center.x, center.y, center.z])
        scaled = (self._data - center_array) * factor + center_array
        return Points3DMap(scaled)

    def rotate_3d(self, axis: np.ndarray, angle: float, center: Point3D | None = None) -> Points3DMap:
        """
        Rotate all points around an axis in 3D.

        Args:
            axis: Rotation axis as 3D vector (will be normalized)
            angle: Rotation angle in radians
            center: Center of rotation (default: centroid)

        Returns:
            New rotated Points3DMap
        """
        if center is None:
            center = self.centroid

        # Normalize axis
        axis = axis / np.linalg.norm(axis)

        # Create rotation matrix using Rodrigues' formula
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)

        # Cross product matrix
        K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])

        # Rotation matrix
        R = np.eye(3) + sin_a * K + (1 - cos_a) * np.dot(K, K)

        # Apply rotation
        center_array = np.array([center.x, center.y, center.z])
        centered = self._data - center_array

        # Reshape for matrix multiplication
        flat_centered = centered.reshape(-1, 3)
        rotated_flat = np.dot(flat_centered, R.T)
        rotated = rotated_flat.reshape(self._data.shape) + center_array

        return Points3DMap(rotated)

    def normalize(self) -> Points3DMap:
        """Normalize all points to unit vectors."""
        magnitudes = np.linalg.norm(self._data, axis=2, keepdims=True)
        # Avoid division by zero
        magnitudes = np.where(magnitudes == 0, 1, magnitudes)
        normalized = self._data / magnitudes
        return Points3DMap(normalized)

    def clamp(self, min_point: Point3D, max_point: Point3D) -> Points3DMap:
        """Clamp all points to be within bounds."""
        min_array = np.array([min_point.x, min_point.y, min_point.z])
        max_array = np.array([max_point.x, max_point.y, max_point.z])
        clamped = np.clip(self._data, min_array, max_array)
        return Points3DMap(clamped)

    def smooth(self, kernel_size: int = 3) -> Points3DMap:
        """
        Apply simple smoothing using a uniform kernel.

        Args:
            kernel_size: Size of the smoothing kernel (must be odd)

        Returns:
            Smoothed Points3DMap
        """
        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd")

        pad_size = kernel_size // 2
        padded = np.pad(self._data, ((pad_size, pad_size), (pad_size, pad_size), (0, 0)), mode="edge")

        smoothed = np.zeros_like(self._data)
        for i in range(self.height):
            for j in range(self.width):
                # Extract the kernel region
                region = padded[i : i + kernel_size, j : j + kernel_size]
                # Average the values
                smoothed[i, j] = np.mean(region, axis=(0, 1))

        return Points3DMap(smoothed)

    def downsample(self, factor: int) -> Points3DMap:
        """Downsample the map by a factor."""
        return Points3DMap(self._data[::factor, ::factor])

    def upsample(self, factor: int) -> Points3DMap:
        """
        Upsample the map by a factor using nearest neighbor interpolation.

        Args:
            factor: Upsampling factor

        Returns:
            Upsampled Points3DMap
        """
        # Nearest neighbor upsampling
        upsampled = np.repeat(np.repeat(self._data, factor, axis=0), factor, axis=1)
        return Points3DMap(upsampled)

    def compute_normals(self) -> Points3DMap:
        """
        Compute surface normals from the points map.

        Returns:
            Points3DMap containing normal vectors
        """
        # Compute gradients
        dy, dx = np.gradient(self._data, axis=(0, 1))

        # Compute cross product to get normals
        normals = np.cross(dx, dy)

        # Normalize
        magnitudes = np.linalg.norm(normals, axis=2, keepdims=True)
        magnitudes = np.where(magnitudes == 0, 1, magnitudes)
        normals = normals / magnitudes

        return Points3DMap(normals)

    def to_depth_map(self) -> np.ndarray:
        """Convert to depth map by extracting Z values."""
        return self.z.copy()

    def save(self, filepath: str) -> None:
        """Save the points map to a numpy file."""
        np.save(filepath, self._data)

    @classmethod
    def load(cls, filepath: str) -> Points3DMap:
        """Load a points map from a numpy file."""
        data = np.load(filepath)
        return cls(data)

    def copy(self) -> Points3DMap:
        """Create a copy of this points map."""
        return Points3DMap(self._data.copy())

    def __repr__(self) -> str:
        """String representation of the points map."""
        return f"Points3DMap(shape={self.shape}, bounds={self.bounds})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        min_pt, max_pt = self.bounds
        return f"Points3DMap({self.height}x{self.width}, bounds=[{min_pt}, {max_pt}])"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Points3DMap."""
        if not isinstance(other, Points3DMap):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Points3DMap."""
        return not self.__eq__(other)

    def __add__(self, other: Points3DMap | Point3D | float) -> Points3DMap:
        """Add to all points."""
        if isinstance(other, Points3DMap):
            if self.shape != other.shape:
                raise ValueError("Points maps must have the same shape")
            return Points3DMap(self._data + other._data)
        elif isinstance(other, Point3D):
            return Points3DMap(self._data + np.array([other.x, other.y, other.z]))
        elif isinstance(other, (int, float)):
            return Points3DMap(self._data + other)
        else:
            return NotImplemented

    def __sub__(self, other: Points3DMap | Point3D | float) -> Points3DMap:
        """Subtract from all points."""
        if isinstance(other, Points3DMap):
            if self.shape != other.shape:
                raise ValueError("Points maps must have the same shape")
            return Points3DMap(self._data - other._data)
        elif isinstance(other, Point3D):
            return Points3DMap(self._data - np.array([other.x, other.y, other.z]))
        elif isinstance(other, (int, float)):
            return Points3DMap(self._data - other)
        else:
            return NotImplemented

    def __mul__(self, other: float) -> Points3DMap:
        """Multiply all points by a scalar."""
        if isinstance(other, (int, float)):
            return Points3DMap(self._data * other)
        else:
            return NotImplemented

    def __truediv__(self, other: float) -> Points3DMap:
        """Divide all points by a scalar."""
        if isinstance(other, (int, float)):
            return Points3DMap(self._data / other)
        else:
            return NotImplemented

    def __neg__(self) -> Points3DMap:
        """Negate all points."""
        return Points3DMap(-self._data)

    def __abs__(self) -> Points3DMap:
        """Absolute value of all coordinates."""
        return Points3DMap(np.abs(self._data))
