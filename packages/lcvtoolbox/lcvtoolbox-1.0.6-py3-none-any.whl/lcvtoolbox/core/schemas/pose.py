"""Pydantic schema for handling pose data from APIs and JSON files."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from pydantic import BaseModel, Field, field_validator

# Import only for type checking to avoid circular imports
if TYPE_CHECKING:
    from lcvtoolbox.vision.geometry.primitives.point import Point3D
    from lcvtoolbox.vision.geometry.primitives.pose_rpy import PoseRPY
    from lcvtoolbox.vision.geometry.primitives.rpy import RPY
    from lcvtoolbox.vision.geometry.primitives.transformation_matrix import TransformationMatrix


class PoseRPYSchema(BaseModel):
    """
    Pydantic schema for 3D pose data with position and RPY orientation.

    This schema is designed to handle pose data from APIs and JSON files
    where orientation is typically provided as roll, pitch, yaw angles in degrees
    for human readability.

    Attributes:
        x: X coordinate in meters
        y: Y coordinate in meters
        z: Z coordinate in meters
        roll: Roll angle in degrees
        pitch: Pitch angle in degrees
        yaw: Yaw angle in degrees

    Examples:
        >>> # From JSON/API data
        >>> data = {
        ...     "x": 1.0, "y": 2.0, "z": 3.0,
        ...     "roll": 30.0, "pitch": 45.0, "yaw": 60.0
        ... }
        >>> pose = PoseRPYSchema(**data)
        >>>
        >>> # Convert to PoseRPY
        >>> pose_rpy = pose.to_pose_rpy()
        >>>
        >>> # Convert to TransformationMatrix
        >>> T = pose.to_transformation_matrix()
        >>>
        >>> # Export back to dict
        >>> pose_dict = pose.model_dump()
    """

    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")
    roll: float = Field(..., description="Roll angle in degrees", ge=-180, le=180)
    pitch: float = Field(..., description="Pitch angle in degrees", ge=-90, le=90)
    yaw: float = Field(..., description="Yaw angle in degrees", ge=-180, le=180)

    model_config = {
        "json_schema_extra": {
            "example": {"x": 1.0, "y": 2.0, "z": 3.0, "roll": 30.0, "pitch": 45.0, "yaw": 60.0}
        }
    }

    @field_validator("pitch", mode="before")
    @classmethod
    def validate_pitch(cls, v):
        """Validate pitch is within gimbal lock safe range."""
        if abs(v) > 89.9:
            # Warning about gimbal lock, but still allow
            import warnings

            warnings.warn(f"Pitch angle {v}° is very close to ±90°, which may cause gimbal lock", RuntimeWarning)
        return v

    @field_validator("x", "y", "z", mode="before")
    @classmethod
    def validate_finite(cls, v):
        """Ensure position values are finite."""
        if not np.isfinite(v):
            raise ValueError(f"Position coordinate must be finite, got {v}")
        return v

    def to_point3d(self) -> Point3D:
        """
        Convert position to Point3D.

        Returns:
            Point3D instance representing the position
        """
        from lcvtoolbox.vision.geometry.primitives.point import Point3D
        return Point3D(self.x, self.y, self.z)

    def to_rpy_radians(self) -> RPY:
        """
        Convert orientation to RPY in radians.

        Returns:
            RPY instance with angles in radians
        """
        from lcvtoolbox.vision.geometry.primitives.rpy import RPY
        return RPY.from_degrees(self.roll, self.pitch, self.yaw)

    def to_pose_rpy(self) -> PoseRPY:
        """
        Convert to PoseRPY object.

        Returns:
            PoseRPY instance
        """
        from lcvtoolbox.vision.geometry.primitives.pose_rpy import PoseRPY
        position = self.to_point3d()
        orientation = self.to_rpy_radians()
        return PoseRPY(position, orientation)

    def to_transformation_matrix(self) -> TransformationMatrix:
        """
        Convert to TransformationMatrix.

        Returns:
            TransformationMatrix instance
        """
        from lcvtoolbox.vision.geometry.primitives.transformation_matrix import TransformationMatrix
        pose_rpy = self.to_pose_rpy()
        return pose_rpy.to_transformation_matrix()

    @classmethod
    def from_pose_rpy(cls, pose_rpy: PoseRPY) -> PoseRPYSchema:
        """
        Create from PoseRPY object.

        Args:
            pose_rpy: PoseRPY instance

        Returns:
            PoseRPYSchema instance with angles in degrees
        """
        position = pose_rpy.position
        orientation_deg = pose_rpy.orientation.to_degrees()

        return cls(x=position.x, y=position.y, z=position.z, roll=orientation_deg.roll, pitch=orientation_deg.pitch, yaw=orientation_deg.yaw)

    @classmethod
    def from_transformation_matrix(cls, T: TransformationMatrix) -> PoseRPYSchema:
        """
        Create from TransformationMatrix.

        Args:
            T: TransformationMatrix instance

        Returns:
            PoseRPYSchema instance with angles in degrees
        """
        position, rpy = T.to_position_rpy()
        rpy_deg = rpy.to_degrees()

        return cls(x=position.x, y=position.y, z=position.z, roll=rpy_deg.roll, pitch=rpy_deg.pitch, yaw=rpy_deg.yaw)

    def to_list(self) -> list[float]:
        """
        Convert to list format [x, y, z, roll, pitch, yaw].

        Returns:
            List of 6 float values
        """
        return [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]

    def to_numpy(self) -> np.ndarray:
        """
        Convert to numpy array [x, y, z, roll, pitch, yaw].

        Returns:
            Numpy array of shape (6,)
        """
        return np.array(self.to_list())

    @classmethod
    def from_list(cls, values: list[float] | np.ndarray) -> PoseRPYSchema:
        """
        Create from list or array [x, y, z, roll, pitch, yaw].

        Args:
            values: List or array with 6 elements

        Returns:
            PoseRPYSchema instance

        Raises:
            ValueError: If values doesn't have exactly 6 elements
        """
        if len(values) != 6:
            raise ValueError(f"Expected 6 values, got {len(values)}")

        return cls(x=float(values[0]), y=float(values[1]), z=float(values[2]), roll=float(values[3]), pitch=float(values[4]), yaw=float(values[5]))

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"Pose(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f}, roll={self.roll:.1f}°, pitch={self.pitch:.1f}°, yaw={self.yaw:.1f}°)"

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"PoseRPYSchema(x={self.x}, y={self.y}, z={self.z}, roll={self.roll}, pitch={self.pitch}, yaw={self.yaw})"
