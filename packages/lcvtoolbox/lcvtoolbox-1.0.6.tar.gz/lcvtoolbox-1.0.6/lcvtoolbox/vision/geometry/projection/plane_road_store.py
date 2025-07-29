"""
Plane Road Store - Cached 3D Points Generation for Road Plane Projection

This module provides a cached implementation of the PlaneRoadModel that stores
and reuses 3D point computations when parameters are similar enough.
"""

from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from lcvtoolbox.vision.camera import adjust_intrinsic_with_size
from lcvtoolbox.core.schemas import CameraDistortionSchema, CameraMatrixSchema, PoseRPYSchema
from lcvtoolbox.vision.geometry.projection.plan_road import Calibration, PlaneRoadModel


@dataclass
class CachedPoints3DEntry:
    """
    Entry for cached 3D points with associated parameters.
    
    Attributes:
        camera_matrix: Camera intrinsic matrix parameters
        distortion: Camera distortion coefficients
        pose: Camera pose (position and orientation)
        image_size: Image dimensions (width, height)
        points3d: Computed 3D points array
    """
    camera_matrix: CameraMatrixSchema
    distortion: CameraDistortionSchema
    pose: PoseRPYSchema
    image_size: Tuple[int, int]
    points3d: np.ndarray


class PlaneRoadStore:
    """
    A store for computing and caching 3D points from road plane projections.
    
    This class manages the computation of 3D points for road plane projections
    with intelligent caching. When similar parameters are provided (within tolerance),
    it reuses previously computed results instead of recalculating.
    
    The cache stores up to 10 entries using LRU (Least Recently Used) policy.
    
    Attributes:
        cache_size: Maximum number of cached entries (default: 10)
        position_tolerance: Tolerance for position matching in meters (default: 0.1)
        angle_tolerance: Tolerance for angle matching in degrees (default: 0.5)
        focal_tolerance: Tolerance for focal length matching in pixels (default: 5.0)
    """
    
    def __init__(
        self,
        cache_size: int = 10,
        position_tolerance: float = 0.1,  # 10 cm tolerance for positions
        angle_tolerance: float = 0.5,     # 0.5 degree tolerance for angles
        focal_tolerance: float = 5.0      # 5 pixel tolerance for focal lengths
    ):
        """
        Initialize the PlaneRoadStore with caching parameters.
        
        Args:
            cache_size: Maximum number of cached entries
            position_tolerance: Tolerance for position matching in meters
            angle_tolerance: Tolerance for angle matching in degrees
            focal_tolerance: Tolerance for focal length matching in pixels
        """
        self.cache: OrderedDict[int, CachedPoints3DEntry] = OrderedDict()
        self.cache_size = cache_size
        self.position_tolerance = position_tolerance
        self.angle_tolerance = angle_tolerance
        self.focal_tolerance = focal_tolerance
    
    def _parameters_match(
        self,
        entry: CachedPoints3DEntry,
        camera_matrix: CameraMatrixSchema,
        distortion: CameraDistortionSchema,
        pose: PoseRPYSchema,
        image_size: Tuple[int, int]
    ) -> bool:
        """
        Check if cached parameters match the requested parameters within tolerance.
        
        Args:
            entry: Cached entry to compare against
            camera_matrix: Requested camera matrix
            distortion: Requested distortion coefficients
            pose: Requested pose
            image_size: Requested image size
            
        Returns:
            bool: True if parameters match within tolerance
        """
        # Check image size (must match exactly)
        if entry.image_size != image_size:
            return False
        
        # Check focal lengths
        if abs(entry.camera_matrix.fx - camera_matrix.fx) > self.focal_tolerance:
            return False
        if abs(entry.camera_matrix.fy - camera_matrix.fy) > self.focal_tolerance:
            return False
            
        # Check principal point (with pixel tolerance)
        if abs(entry.camera_matrix.cx - camera_matrix.cx) > self.focal_tolerance:
            return False
        if abs(entry.camera_matrix.cy - camera_matrix.cy) > self.focal_tolerance:
            return False
            
        # Check distortion coefficients (must be very close)
        if not np.allclose(
            entry.distortion.numpy,
            distortion.numpy,
            rtol=1e-3,
            atol=1e-5
        ):
            return False
            
        # Check position (within position tolerance)
        if abs(entry.pose.x - pose.x) > self.position_tolerance:
            return False
        if abs(entry.pose.y - pose.y) > self.position_tolerance:
            return False
        if abs(entry.pose.z - pose.z) > self.position_tolerance:
            return False
            
        # Check angles (within angle tolerance)
        if abs(entry.pose.roll - pose.roll) > self.angle_tolerance:
            return False
        if abs(entry.pose.pitch - pose.pitch) > self.angle_tolerance:
            return False
        if abs(entry.pose.yaw - pose.yaw) > self.angle_tolerance:
            return False
            
        return True
    
    def _find_cached_entry(
        self,
        camera_matrix: CameraMatrixSchema,
        distortion: CameraDistortionSchema,
        pose: PoseRPYSchema,
        image_size: Tuple[int, int]
    ) -> Optional[CachedPoints3DEntry]:
        """
        Find a cached entry that matches the requested parameters.
        
        Args:
            camera_matrix: Requested camera matrix
            distortion: Requested distortion coefficients
            pose: Requested pose
            image_size: Requested image size
            
        Returns:
            Matching cached entry or None if no match found
        """
        for key, entry in self.cache.items():
            if self._parameters_match(entry, camera_matrix, distortion, pose, image_size):
                # Move to end (LRU update)
                self.cache.move_to_end(key)
                return entry
        return None
    
    def _add_to_cache(
        self,
        camera_matrix: CameraMatrixSchema,
        distortion: CameraDistortionSchema,
        pose: PoseRPYSchema,
        image_size: Tuple[int, int],
        points3d: np.ndarray
    ) -> None:
        """
        Add a new entry to the cache.
        
        Args:
            camera_matrix: Camera matrix used
            distortion: Distortion coefficients used
            pose: Pose used
            image_size: Image size used
            points3d: Computed 3D points
        """
        # Create cache key based on hash of parameters
        cache_key = hash((
            camera_matrix.fx,
            camera_matrix.fy,
            camera_matrix.cx,
            camera_matrix.cy,
            tuple(distortion.numpy.tolist()),
            pose.x,
            pose.y,
            pose.z,
            pose.roll,
            pose.pitch,
            pose.yaw,
            image_size
        ))
        
        # Create new entry
        entry = CachedPoints3DEntry(
            camera_matrix=camera_matrix,
            distortion=distortion,
            pose=pose,
            image_size=image_size,
            points3d=points3d.copy()  # Copy to avoid reference issues
        )
        
        # Add to cache
        self.cache[cache_key] = entry
        
        # Remove oldest entry if cache is full
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)  # Remove oldest (first) item
    
    def get_points3d(
        self,
        camera_matrix: CameraMatrixSchema,
        distortion: CameraDistortionSchema,
        pose: PoseRPYSchema,
        original_image_size: Tuple[int, int],
        resized_image_size: Optional[Tuple[int, int]] = None
    ) -> Tuple[np.ndarray, bool]:
        """
        Get 3D points for the given parameters, using cache if available.
        
        This method is the main interface for obtaining 3D points. It will:
        1. Adjust camera intrinsics if image was resized
        2. Check cache for matching parameters
        3. Compute new points if no cache hit
        4. Store result in cache for future use
        
        Args:
            camera_matrix: Camera intrinsic matrix
            distortion: Camera distortion coefficients
            pose: Camera pose (position and orientation in degrees)
            original_image_size: Original image dimensions (width, height)
            resized_image_size: Resized image dimensions if different from original
            
        Returns:
            Tuple of (points3d array, was_cached boolean)
            - points3d: Array of shape (height, width, 3) with X,Y,Z coordinates
            - was_cached: True if result was retrieved from cache
            
        Example:
            >>> store = PlaneRoadStore()
            >>> camera = CameraMatrixSchema(fx=1000, fy=1000, cx=960, cy=540)
            >>> distortion = CameraDistortionSchema(k1=0, k2=0, p1=0, p2=0, k3=0)
            >>> pose = PoseRPYSchema(x=0, y=0, z=1.1, roll=0, pitch=30, yaw=0)
            >>> points3d, cached = store.get_points3d(
            ...     camera, distortion, pose, 
            ...     original_image_size=(1920, 1080)
            ... )
        """
        # Determine actual image size to use
        actual_image_size = resized_image_size if resized_image_size else original_image_size
        
        # Adjust camera matrix if image was resized
        if resized_image_size and resized_image_size != original_image_size:
            adjusted_matrix, _ = adjust_intrinsic_with_size(
                camera_matrix,
                distortion,
                original_image_size,
                resized_image_size
            )
        else:
            adjusted_matrix = camera_matrix
        
        # Check cache for matching parameters
        cached_entry = self._find_cached_entry(
            adjusted_matrix,
            distortion,
            pose,
            actual_image_size
        )
        
        if cached_entry is not None:
            # Cache hit - return cached points
            return cached_entry.points3d, True
        
        # Cache miss - compute new points
        # Convert schemas to numpy arrays for PlaneRoadModel
        calibration = Calibration(
            camera_matrix=adjusted_matrix.numpy,
            dist_coeffs=distortion.numpy
        )
        
        # Create PlaneRoadModel with pose parameters
        # Note: pose angles are in degrees in the schema
        model = PlaneRoadModel(
            camera_calibration=calibration,
            camera_pitch=pose.pitch,  # Already in degrees
            camera_yaw=pose.yaw,      # Already in degrees
            camera_roll=pose.roll,    # Already in degrees
            camera_height=pose.z      # Height in meters
        )
        
        # Compute 3D points
        points3d = model.get_points3D(image_size=actual_image_size)
        
        # Add to cache
        self._add_to_cache(
            adjusted_matrix,
            distortion,
            pose,
            actual_image_size,
            points3d
        )
        
        return points3d, False
    
    def clear_cache(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
    
    def get_cache_info(self) -> dict:
        """
        Get information about the current cache state.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.cache_size,
            "position_tolerance_m": self.position_tolerance,
            "angle_tolerance_deg": self.angle_tolerance,
            "focal_tolerance_px": self.focal_tolerance,
            "cached_entries": [
                {
                    "image_size": entry.image_size,
                    "position": (entry.pose.x, entry.pose.y, entry.pose.z),
                    "orientation": (entry.pose.roll, entry.pose.pitch, entry.pose.yaw),
                    "focal": (entry.camera_matrix.fx, entry.camera_matrix.fy)
                }
                for entry in self.cache.values()
            ]
        }


# Example usage
def example_usage():
    """Demonstrate usage of PlaneRoadStore with caching."""
    
    # Create store instance
    store = PlaneRoadStore(
        cache_size=10,
        position_tolerance=0.1,  # 10 cm
        angle_tolerance=0.5,     # 0.5 degrees
        focal_tolerance=5.0      # 5 pixels
    )
    
    # Define camera parameters
    camera_matrix = CameraMatrixSchema(
        fx=1000.0,
        fy=1000.0,
        cx=960.0,
        cy=540.0,
        s=0.0
    )
    
    distortion = CameraDistortionSchema(
        k1=0.0,
        k2=0.0,
        p1=0.0,
        p2=0.0,
        k3=0.0
    )
    
    # Define pose
    pose = PoseRPYSchema(
        x=0.0,
        y=0.0,
        z=1.1,  # 1.1 meters height
        roll=0.0,
        pitch=30.0,  # 30 degrees looking down
        yaw=0.0
    )
    
    # Original image size
    original_size = (1920, 1080)
    
    print("=== PlaneRoadStore Example ===\n")
    
    # First call - will compute
    print("1. First call (no cache):")
    points3d_1, cached_1 = store.get_points3d(
        camera_matrix, distortion, pose, original_size
    )
    print(f"   - Points shape: {points3d_1.shape}")
    print(f"   - From cache: {cached_1}")
    
    # Second call with same parameters - should use cache
    print("\n2. Second call (same parameters):")
    points3d_2, cached_2 = store.get_points3d(
        camera_matrix, distortion, pose, original_size
    )
    print(f"   - Points shape: {points3d_2.shape}")
    print(f"   - From cache: {cached_2}")
    print(f"   - Same array: {np.array_equal(points3d_1, points3d_2)}")
    
    # Third call with slightly different pose - within tolerance
    print("\n3. Third call (pose within tolerance):")
    pose_similar = PoseRPYSchema(
        x=0.05,      # 5 cm difference (within 10 cm tolerance)
        y=0.0,
        z=1.15,      # 5 cm difference
        roll=0.2,    # 0.2 degrees (within 0.5 degree tolerance)
        pitch=30.3,  # 0.3 degrees difference
        yaw=0.0
    )
    points3d_3, cached_3 = store.get_points3d(
        camera_matrix, distortion, pose_similar, original_size
    )
    print(f"   - Points shape: {points3d_3.shape}")
    print(f"   - From cache: {cached_3}")
    
    # Fourth call with different pose - outside tolerance
    print("\n4. Fourth call (pose outside tolerance):")
    pose_different = PoseRPYSchema(
        x=0.5,       # 50 cm difference (outside tolerance)
        y=0.0,
        z=1.1,
        roll=0.0,
        pitch=45.0,  # 15 degrees difference
        yaw=0.0
    )
    points3d_4, cached_4 = store.get_points3d(
        camera_matrix, distortion, pose_different, original_size
    )
    print(f"   - Points shape: {points3d_4.shape}")
    print(f"   - From cache: {cached_4}")
    
    # Fifth call with resized image
    print("\n5. Fifth call (resized image):")
    resized_size = (1280, 720)
    points3d_5, cached_5 = store.get_points3d(
        camera_matrix, distortion, pose, original_size, resized_size
    )
    print(f"   - Points shape: {points3d_5.shape}")
    print(f"   - From cache: {cached_5}")
    
    # Show cache info
    print("\n6. Cache information:")
    cache_info = store.get_cache_info()
    print(f"   - Cache entries: {cache_info['cache_size']}/{cache_info['max_cache_size']}")
    print(f"   - Tolerances:")
    print(f"     * Position: ±{cache_info['position_tolerance_m']} m")
    print(f"     * Angle: ±{cache_info['angle_tolerance_deg']}°")
    print(f"     * Focal: ±{cache_info['focal_tolerance_px']} px")
    
    print("\n   - Cached configurations:")
    for i, entry in enumerate(cache_info['cached_entries']):
        print(f"     {i+1}. Size: {entry['image_size']}, "
              f"Pos: {entry['position']}, "
              f"Angles: {entry['orientation']}")


if __name__ == "__main__":
    example_usage()
