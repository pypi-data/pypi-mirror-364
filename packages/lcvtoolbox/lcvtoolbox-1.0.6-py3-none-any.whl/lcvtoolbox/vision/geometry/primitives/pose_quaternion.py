from __future__ import annotations

import numpy as np
from typing import Optional

from .point import Point3D
from .quaternion import Quaternion
from .transformation_matrix import TransformationMatrix
from .rpy import RPY
from .rotation_matrix import RotationMatrix
from .vector import Vector3D


class PoseQuaternion:
    """
    Represents a 3D pose combining position (Point3D) and orientation (Quaternion).

    This class provides a convenient way to work with poses using quaternions
    for orientation, which avoids gimbal lock and provides smooth interpolation.

    Args:
        position: 3D position as Point3D, numpy array, list, or tuple
        orientation: Orientation as Quaternion or array of [w, x, y, z]

    Examples:
        >>> # Create from position and quaternion
        >>> pose = PoseQuaternion(Point3D(1, 2, 3), Quaternion(0.707, 0, 0, 0.707))
        >>>
        >>> # Create from transformation matrix
        >>> T = TransformationMatrix.from_point_quaternion(Point3D(1, 2, 3), Quaternion.identity())
        >>> pose = PoseQuaternion.from_transformation_matrix(T)
        >>>
        >>> # Convert to transformation matrix
        >>> T = pose.to_transformation_matrix()
        >>>
        >>> # Access components
        >>> print(f"Position: {pose.position}")
        >>> print(f"Orientation: {pose.orientation}")
    """

    __slots__ = ("_position", "_orientation")  # Memory optimization

    def __init__(self, position: Point3D | np.ndarray | list | tuple, 
                 orientation: Quaternion | np.ndarray | list | tuple) -> None:
        """Initialize pose with position and quaternion orientation."""
        # Handle position
        if isinstance(position, Point3D):
            self._position = position
        elif isinstance(position, (np.ndarray, list, tuple)):
            if len(position) != 3:
                raise ValueError("Position must be 3D")
            self._position = Point3D(float(position[0]), float(position[1]), float(position[2]))
        else:
            raise TypeError(f"Unsupported position type: {type(position)}")
        
        # Handle orientation
        if isinstance(orientation, Quaternion):
            self._orientation = orientation
        elif isinstance(orientation, (np.ndarray, list, tuple)):
            if len(orientation) != 4:
                raise ValueError("Quaternion must have 4 components [w, x, y, z]")
            self._orientation = Quaternion(
                float(orientation[0]), float(orientation[1]), 
                float(orientation[2]), float(orientation[3])
            )
        else:
            raise TypeError(f"Unsupported orientation type: {type(orientation)}")

    @classmethod
    def identity(cls) -> PoseQuaternion:
        """Create an identity pose (origin position, no rotation)."""
        return cls(Point3D(0, 0, 0), Quaternion.identity())

    @classmethod
    def from_transformation_matrix(cls, transformation_matrix: TransformationMatrix) -> PoseQuaternion:
        """Create from a transformation matrix.

        Args:
            transformation_matrix: TransformationMatrix instance

        Returns:
            PoseQuaternion instance
        """
        position, quaternion = transformation_matrix.to_position_quaternion()
        return cls(position, quaternion)

    @classmethod
    def from_numpy(cls, position: np.ndarray, orientation: np.ndarray) -> PoseQuaternion:
        """Create from numpy arrays.

        Args:
            position: 3D position array
            orientation: 4D quaternion array [w, x, y, z]

        Returns:
            PoseQuaternion instance
        """
        return cls(position, orientation)

    @classmethod
    def from_list(cls, pose_list: list | np.ndarray) -> PoseQuaternion:
        """Create from a list/array of 7 values [x, y, z, qw, qx, qy, qz].

        Args:
            pose_list: List or array with 7 elements

        Returns:
            PoseQuaternion instance
        """
        if len(pose_list) != 7:
            raise ValueError("Pose list must have 7 elements [x, y, z, qw, qx, qy, qz]")
        
        position = pose_list[:3]
        orientation = pose_list[3:]
        return cls(position, orientation)

    @classmethod
    def from_position_rpy(cls, position: Point3D | np.ndarray, rpy: RPY | np.ndarray) -> PoseQuaternion:
        """Create from position and RPY angles.

        Args:
            position: 3D position
            rpy: RPY angles

        Returns:
            PoseQuaternion instance
        """
        if isinstance(rpy, RPY):
            quat = Quaternion.from_rpy(rpy)
        else:
            quat = Quaternion.from_rpy(RPY.from_numpy(rpy))
        
        return cls(position, quat)

    @property
    def position(self) -> Point3D:
        """Get the position component."""
        return self._position

    @property
    def orientation(self) -> Quaternion:
        """Get the orientation component."""
        return self._orientation

    @property
    def x(self) -> float:
        """Get X coordinate."""
        return self._position.x

    @property
    def y(self) -> float:
        """Get Y coordinate."""
        return self._position.y

    @property
    def z(self) -> float:
        """Get Z coordinate."""
        return self._position.z

    @property
    def qw(self) -> float:
        """Get quaternion W component."""
        return self._orientation.w

    @property
    def qx(self) -> float:
        """Get quaternion X component."""
        return self._orientation.x

    @property
    def qy(self) -> float:
        """Get quaternion Y component."""
        return self._orientation.y

    @property
    def qz(self) -> float:
        """Get quaternion Z component."""
        return self._orientation.z

    def to_transformation_matrix(self) -> TransformationMatrix:
        """Convert to transformation matrix.

        Returns:
            TransformationMatrix instance
        """
        return TransformationMatrix.from_point_quaternion(self._position, self._orientation)

    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array [x, y, z, qw, qx, qy, qz].

        Returns:
            7D numpy array
        """
        return np.array([
            self.x, self.y, self.z,
            self.qw, self.qx, self.qy, self.qz
        ])

    def to_list(self) -> list[float]:
        """Convert to list [x, y, z, qw, qx, qy, qz].

        Returns:
            List with 7 elements
        """
        return [self.x, self.y, self.z, self.qw, self.qx, self.qy, self.qz]

    def to_pose_rpy(self) -> 'PoseRPY':
        """Convert to PoseRPY representation.

        Returns:
            PoseRPY instance
        """
        from .pose_rpy import PoseRPY
        rpy = self._orientation.to_rpy()
        return PoseRPY(self._position, rpy)

    def transform_point(self, point: Point3D | np.ndarray) -> Point3D:
        """Transform a point from this pose's frame to the world frame.

        Args:
            point: Point to transform

        Returns:
            Transformed point
        """
        T = self.to_transformation_matrix()
        return T.transform_point(point)

    def inverse(self) -> PoseQuaternion:
        """Get the inverse pose.

        Returns:
            Inverse PoseQuaternion
        """
        # Inverse quaternion
        q_inv = self._orientation.inverse()
        
        # Inverse position: -R^T * t
        pos_inv = q_inv.apply_to_vector(-self._position.numpy)
        
        return PoseQuaternion(Point3D(*pos_inv), q_inv)

    def compose(self, other: PoseQuaternion) -> PoseQuaternion:
        """Compose this pose with another.

        Args:
            other: Another PoseQuaternion

        Returns:
            Composed PoseQuaternion
        """
        # Compose rotations
        q_composed = self._orientation.compose(other._orientation)
        
        # Transform and add positions
        pos_transformed = self._orientation.apply_to_vector(other._position.numpy)
        pos_composed = Point3D(
            self.x + pos_transformed[0],
            self.y + pos_transformed[1],
            self.z + pos_transformed[2]
        )
        
        return PoseQuaternion(pos_composed, q_composed)

    def interpolate(self, other: PoseQuaternion, t: float) -> PoseQuaternion:
        """Interpolate between this pose and another.

        Args:
            other: Target pose
            t: Interpolation parameter (0 = self, 1 = other)

        Returns:
            Interpolated pose
        """
        # Linear interpolation for position
        pos_interp = Point3D(
            (1 - t) * self.x + t * other.x,
            (1 - t) * self.y + t * other.y,
            (1 - t) * self.z + t * other.z
        )
        
        # SLERP for quaternion
        quat_interp = Quaternion.slerp(self._orientation, other._orientation, t)
        
        return PoseQuaternion(pos_interp, quat_interp)

    def distance_to(self, other: PoseQuaternion) -> tuple[float, float]:
        """Compute distance to another pose.

        Returns:
            Tuple of (position_distance, angular_distance_radians)
        """
        # Position distance
        pos_dist = self._position.distance_to(other._position)
        
        # Angular distance
        ang_dist = self._orientation.distance_to(other._orientation)
        
        return pos_dist, ang_dist

    def is_close(self, other: PoseQuaternion, pos_tolerance: float = 1e-6, 
                 ang_tolerance: float = 1e-6) -> bool:
        """Check if this pose is close to another.

        Args:
            other: Another PoseQuaternion
            pos_tolerance: Position tolerance
            ang_tolerance: Angular tolerance (radians)

        Returns:
            True if poses are close
        """
        pos_dist, ang_dist = self.distance_to(other)
        return pos_dist < pos_tolerance and ang_dist < ang_tolerance

    def copy(self) -> PoseQuaternion:
        """Create a copy of this pose."""
        return PoseQuaternion(self._position.copy(), self._orientation.copy())

    def __repr__(self) -> str:
        """String representation."""
        return (f"PoseQuaternion(position=({self.x:.3f}, {self.y:.3f}, {self.z:.3f}), "
                f"quaternion=({self.qw:.3f}, {self.qx:.3f}, {self.qy:.3f}, {self.qz:.3f}))")

    def __str__(self) -> str:
        """User-friendly string representation."""
        rpy = self._orientation.to_rpy()
        return (f"Pose: pos=[{self.x:.3f}, {self.y:.3f}, {self.z:.3f}], "
                f"quat=[{self.qw:.3f}, {self.qx:.3f}, {self.qy:.3f}, {self.qz:.3f}], "
                f"rpy=[{np.rad2deg(rpy.roll):.1f}°, "
                f"{np.rad2deg(rpy.pitch):.1f}°, "
                f"{np.rad2deg(rpy.yaw):.1f}°]")

    def __eq__(self, other: object) -> bool:
        """Check equality with another PoseQuaternion."""
        if not isinstance(other, PoseQuaternion):
            return NotImplemented
        return (self._position == other._position and
                self._orientation == other._orientation)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another PoseQuaternion."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for PoseQuaternion objects."""
        return hash((self._position, self._orientation))

    # Frame properties for convenience
    @property
    def x_axis(self) -> Vector3D:
        """Get the X-axis direction in world frame."""
        return self.to_transformation_matrix().x_axis

    @property
    def y_axis(self) -> Vector3D:
        """Get the Y-axis direction in world frame."""
        return self.to_transformation_matrix().y_axis

    @property
    def z_axis(self) -> Vector3D:
        """Get the Z-axis direction in world frame."""
        return self.to_transformation_matrix().z_axis

    # Additional utility methods
    def to_rpy(self) -> RPY:
        """Get the orientation as RPY angles.

        Returns:
            RPY instance
        """
        return self._orientation.to_rpy()

    @classmethod
    def random(cls, position_range: float = 1.0) -> PoseQuaternion:
        """Generate a random pose.

        Position is uniformly distributed in [-range, range]³
        Orientation is a random unit quaternion.

        Args:
            position_range: Range for position coordinates

        Returns:
            Random PoseQuaternion
        """
        position = Point3D(
            np.random.uniform(-position_range, position_range),
            np.random.uniform(-position_range, position_range),
            np.random.uniform(-position_range, position_range)
        )
        orientation = Quaternion.random()
        return cls(position, orientation)
    
    def transform_vector(self, vector: Vector3D | np.ndarray) -> Vector3D:
        """Transform a vector (rotation only, no translation).
        
        Args:
            vector: Vector to transform
            
        Returns:
            Transformed vector
        """
        if isinstance(vector, Vector3D):
            v_rotated = self._orientation.apply_to_vector(vector.numpy)
            return Vector3D(*v_rotated)
        else:
            v_rotated = self._orientation.apply_to_vector(vector)
            return Vector3D(*v_rotated)
    
    def transform_points(self, points: np.ndarray) -> np.ndarray:
        """Transform multiple points efficiently.
        
        Args:
            points: Nx3 array of points
            
        Returns:
            Nx3 array of transformed points
        """
        T = self.to_transformation_matrix()
        return T.transform_points(points)
    
    def relative_to(self, reference: PoseQuaternion) -> PoseQuaternion:
        """Get this pose relative to a reference pose.
        
        This computes: reference^(-1) * self
        
        Args:
            reference: Reference pose
            
        Returns:
            Relative pose
        """
        return reference.inverse().compose(self)
    
    def __matmul__(self, other: PoseQuaternion) -> PoseQuaternion:
        """Matrix multiplication operator for pose composition."""
        if isinstance(other, PoseQuaternion):
            return self.compose(other)
        return NotImplemented
    
    @property
    def rotation_matrix(self) -> RotationMatrix:
        """Get the rotation matrix."""
        return self._orientation.to_rotation_matrix()
    
    def apply_to_vector(self, vector: np.ndarray) -> np.ndarray:
        """Apply only the rotation to a vector.
        
        Args:
            vector: 3D vector or array of vectors
            
        Returns:
            Rotated vector(s)
        """
        return self._orientation.apply_to_vector(vector)
