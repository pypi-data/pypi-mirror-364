from __future__ import annotations

import numpy as np
from typing import Optional

from .point import Point3D
from .rpy import RPY
from .transformation_matrix import TransformationMatrix
from .quaternion import Quaternion
from .rotation_matrix import RotationMatrix
from .vector import Vector3D


class PoseRPY:
    """
    Represents a 3D pose combining position (Point3D) and orientation (RPY).

    This class provides a convenient way to work with poses using RPY angles
    for orientation, which is common in robotics and navigation applications.

    Args:
        position: 3D position as Point3D, numpy array, list, or tuple
        orientation: Orientation as RPY angles (in radians)

    Examples:
        >>> # Create from position and RPY
        >>> pose = PoseRPY(Point3D(1, 2, 3), RPY(0.1, 0.2, 0.3))
        >>>
        >>> # Create from transformation matrix
        >>> T = TransformationMatrix.from_point_rpy(Point3D(1, 2, 3), RPY(0.1, 0.2, 0.3))
        >>> pose = PoseRPY.from_transformation_matrix(T)
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
                 orientation: RPY | np.ndarray | list | tuple) -> None:
        """Initialize pose with position and RPY orientation."""
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
        if isinstance(orientation, RPY):
            self._orientation = orientation
        elif isinstance(orientation, (np.ndarray, list, tuple)):
            if len(orientation) != 3:
                raise ValueError("Orientation must have 3 angles (roll, pitch, yaw)")
            self._orientation = RPY(float(orientation[0]), float(orientation[1]), float(orientation[2]))
        else:
            raise TypeError(f"Unsupported orientation type: {type(orientation)}")

    @classmethod
    def identity(cls) -> PoseRPY:
        """Create an identity pose (origin position, no rotation)."""
        return cls(Point3D(0, 0, 0), RPY(0, 0, 0))

    @classmethod
    def from_transformation_matrix(cls, transformation_matrix: TransformationMatrix) -> PoseRPY:
        """Create from a transformation matrix.

        Args:
            transformation_matrix: TransformationMatrix instance

        Returns:
            PoseRPY instance
        """
        position, rpy = transformation_matrix.to_position_rpy()
        return cls(position, rpy)

    @classmethod
    def from_numpy(cls, position: np.ndarray, orientation: np.ndarray) -> PoseRPY:
        """Create from numpy arrays.

        Args:
            position: 3D position array
            orientation: 3D RPY angles array (in radians)

        Returns:
            PoseRPY instance
        """
        return cls(position, orientation)

    @classmethod
    def from_list(cls, pose_list: list | np.ndarray) -> PoseRPY:
        """Create from a list/array of 6 values [x, y, z, roll, pitch, yaw].

        Args:
            pose_list: List or array with 6 elements

        Returns:
            PoseRPY instance
        """
        if len(pose_list) != 6:
            raise ValueError("Pose list must have 6 elements [x, y, z, roll, pitch, yaw]")
        
        position = pose_list[:3]
        orientation = pose_list[3:]
        return cls(position, orientation)

    @property
    def position(self) -> Point3D:
        """Get the position component."""
        return self._position

    @property
    def orientation(self) -> RPY:
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
    def roll(self) -> float:
        """Get roll angle in radians."""
        return self._orientation.roll

    @property
    def pitch(self) -> float:
        """Get pitch angle in radians."""
        return self._orientation.pitch

    @property
    def yaw(self) -> float:
        """Get yaw angle in radians."""
        return self._orientation.yaw

    def to_transformation_matrix(self) -> TransformationMatrix:
        """Convert to transformation matrix.

        Returns:
            TransformationMatrix instance
        """
        return TransformationMatrix.from_point_rpy(self._position, self._orientation)

    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array [x, y, z, roll, pitch, yaw].

        Returns:
            6D numpy array
        """
        return np.array([
            self.x, self.y, self.z,
            self.roll, self.pitch, self.yaw
        ])

    def to_list(self) -> list[float]:
        """Convert to list [x, y, z, roll, pitch, yaw].

        Returns:
            List with 6 elements
        """
        return [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]

    def to_pose_quaternion(self) -> 'PoseQuaternion':
        """Convert to PoseQuaternion representation.

        Returns:
            PoseQuaternion instance
        """
        from .pose_quaternion import PoseQuaternion
        quat = Quaternion.from_rpy(self._orientation)
        return PoseQuaternion(self._position, quat)

    def transform_point(self, point: Point3D | np.ndarray) -> Point3D:
        """Transform a point from this pose's frame to the world frame.

        Args:
            point: Point to transform

        Returns:
            Transformed point
        """
        T = self.to_transformation_matrix()
        return T.transform_point(point)

    def inverse(self) -> PoseRPY:
        """Get the inverse pose.

        Returns:
            Inverse PoseRPY
        """
        T = self.to_transformation_matrix()
        T_inv = T.inverse()
        return PoseRPY.from_transformation_matrix(T_inv)

    def compose(self, other: PoseRPY) -> PoseRPY:
        """Compose this pose with another.

        Args:
            other: Another PoseRPY

        Returns:
            Composed PoseRPY
        """
        T1 = self.to_transformation_matrix()
        T2 = other.to_transformation_matrix()
        T_composed = T1 @ T2
        return PoseRPY.from_transformation_matrix(T_composed)

    def interpolate(self, other: PoseRPY, t: float) -> PoseRPY:
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
        
        # Use RPY interpolation through quaternions for better results
        T1 = self.to_transformation_matrix()
        T2 = other.to_transformation_matrix()
        T_interp = T1.interpolate(T2, t)
        
        _, rpy_interp = T_interp.to_position_rpy()
        
        return PoseRPY(pos_interp, rpy_interp)

    def distance_to(self, other: PoseRPY) -> tuple[float, float]:
        """Compute distance to another pose.

        Returns:
            Tuple of (position_distance, angular_distance_radians)
        """
        # Position distance
        pos_dist = self._position.distance_to(other._position)
        
        # Angular distance (using quaternions for accuracy)
        q1 = Quaternion.from_rpy(self._orientation)
        q2 = Quaternion.from_rpy(other._orientation)
        ang_dist = q1.distance_to(q2)
        
        return pos_dist, ang_dist

    def is_close(self, other: PoseRPY, pos_tolerance: float = 1e-6, 
                 ang_tolerance: float = 1e-6) -> bool:
        """Check if this pose is close to another.

        Args:
            other: Another PoseRPY
            pos_tolerance: Position tolerance
            ang_tolerance: Angular tolerance (radians)

        Returns:
            True if poses are close
        """
        return (self._position.is_close(other._position, pos_tolerance) and
                self._orientation.is_close(other._orientation, ang_tolerance))

    def copy(self) -> PoseRPY:
        """Create a copy of this pose."""
        return PoseRPY(self._position.copy(), self._orientation.copy())

    def __repr__(self) -> str:
        """String representation."""
        return (f"PoseRPY(position=({self.x:.3f}, {self.y:.3f}, {self.z:.3f}), "
                f"rpy=({np.rad2deg(self.roll):.1f}°, "
                f"{np.rad2deg(self.pitch):.1f}°, "
                f"{np.rad2deg(self.yaw):.1f}°))")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (f"Pose: pos=[{self.x:.3f}, {self.y:.3f}, {self.z:.3f}], "
                f"rpy=[{np.rad2deg(self.roll):.1f}°, "
                f"{np.rad2deg(self.pitch):.1f}°, "
                f"{np.rad2deg(self.yaw):.1f}°]")

    def __eq__(self, other: object) -> bool:
        """Check equality with another PoseRPY."""
        if not isinstance(other, PoseRPY):
            return NotImplemented
        return (self._position == other._position and
                self._orientation == other._orientation)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another PoseRPY."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for PoseRPY objects."""
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
    
    # Additional useful methods
    @classmethod
    def from_degrees(cls, position: Point3D | np.ndarray | list | tuple,
                     roll_deg: float, pitch_deg: float, yaw_deg: float) -> PoseRPY:
        """Create PoseRPY from position and angles in degrees.
        
        Args:
            position: 3D position
            roll_deg: Roll angle in degrees
            pitch_deg: Pitch angle in degrees  
            yaw_deg: Yaw angle in degrees
            
        Returns:
            PoseRPY instance
        """
        rpy = RPY.from_degrees(roll_deg, pitch_deg, yaw_deg)
        return cls(position, rpy)
    
    @classmethod
    def random(cls, position_range: float = 1.0, 
               angle_range: float = np.pi) -> PoseRPY:
        """Generate a random pose.
        
        Args:
            position_range: Range for position coordinates [-range, range]
            angle_range: Range for angles [-range, range]
            
        Returns:
            Random PoseRPY
        """
        position = Point3D(
            np.random.uniform(-position_range, position_range),
            np.random.uniform(-position_range, position_range),
            np.random.uniform(-position_range, position_range)
        )
        orientation = RPY(
            np.random.uniform(-angle_range, angle_range),
            np.random.uniform(-angle_range, angle_range),
            np.random.uniform(-angle_range, angle_range)
        )
        return cls(position, orientation)
    
    def transform_vector(self, vector: Vector3D | np.ndarray) -> Vector3D:
        """Transform a vector (rotation only, no translation).
        
        Args:
            vector: Vector to transform
            
        Returns:
            Transformed vector
        """
        T = self.to_transformation_matrix()
        return T.transform_vector(vector)
    
    def transform_points(self, points: np.ndarray) -> np.ndarray:
        """Transform multiple points efficiently.
        
        Args:
            points: Nx3 array of points
            
        Returns:
            Nx3 array of transformed points
        """
        T = self.to_transformation_matrix()
        return T.transform_points(points)
    
    def to_degrees(self) -> PoseRPY:
        """Get a copy with orientation angles in degrees.
        
        Returns:
            New PoseRPY with angles in degrees
        """
        return PoseRPY(self._position.copy(), self._orientation.to_degrees())
    
    def relative_to(self, reference: PoseRPY) -> PoseRPY:
        """Get this pose relative to a reference pose.
        
        This computes: reference^(-1) * self
        
        Args:
            reference: Reference pose
            
        Returns:
            Relative pose
        """
        return reference.inverse().compose(self)
    
    def __matmul__(self, other: PoseRPY) -> PoseRPY:
        """Matrix multiplication operator for pose composition."""
        if isinstance(other, PoseRPY):
            return self.compose(other)
        return NotImplemented
    
    @property 
    def rotation_matrix(self) -> RotationMatrix:
        """Get the rotation matrix."""
        return RotationMatrix(self._orientation.to_rotation_matrix())
    
    def apply_to_vector(self, vector: np.ndarray) -> np.ndarray:
        """Apply only the rotation to a vector.
        
        Args:
            vector: 3D vector or array of vectors
            
        Returns:
            Rotated vector(s)
        """
        return self._orientation.to_rotation_matrix() @ vector
