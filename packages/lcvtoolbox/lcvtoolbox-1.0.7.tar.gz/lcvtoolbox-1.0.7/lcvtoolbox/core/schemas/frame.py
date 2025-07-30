"""
Frame and metadata schemas for image/video processing.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .camera import CameraDistortionSchema, CameraMatrixSchema
from .gps import GPSPoint
from .pose import PoseRPYSchema


class ImageMetadata(BaseModel):
    """
    Metadata for images in a video frame.

    Attributes:
        device: Device identifier for the image
        video_name: Name of the video file
        frame_number: Frame number in the video
        date: Timestamp of the frame
        elapsed: Elapsed time since the start of the video
        frame_index: Index of the frame in the video
        matrix: Camera intrinsic matrix parameters
        dist_coeffs: Camera distortion coefficients
        pose: 3D pose with position and RPY orientation
        gps_point: Optional GPS coordinates, can be None
        extraction_index: Optional index of extracted image, can be None
    """

    device: str = Field(..., description="Device identifier for the image")
    video_name: str = Field(..., description="Name of the video file")
    frame_number: int = Field(..., description="Frame number in the video")
    date: float = Field(..., description="Timestamp of the frame")
    elapsed: float = Field(..., description="Elapsed time since the start of the video")
    frame_index: int = Field(..., description="Index of the frame in the video")
    matrix: CameraMatrixSchema = Field(..., description="Camera intrinsic matrix parameters")
    dist_coeffs: CameraDistortionSchema = Field(..., description="Camera distortion coefficients")
    pose: PoseRPYSchema = Field(..., description="3D pose with position and RPY orientation")
    gps_point: GPSPoint | None = Field(None, description="Optional GPS coordinates")
    extraction_index: int | None = Field(None, description="Optional index of extracted image")


class FrameMetadata(BaseModel):
    """
    Metadata for frames in a video.
    
    Attributes:
        time: Timestamp in milliseconds
        latitude: Latitude coordinate in degrees
        longitude: Longitude coordinate in degrees
        altitude: Altitude in meters
        orientation: Orientation angle in degrees
        images: List of image metadata for this frame
    """

    time: int = Field(..., description="Timestamp in milliseconds")
    latitude: float = Field(..., description="Latitude coordinate in degrees", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate in degrees", ge=-180, le=180)
    altitude: float = Field(..., description="Altitude in meters")
    orientation: float = Field(..., description="Orientation angle in degrees", ge=-180, le=180)
    images: list[ImageMetadata] = Field(..., description="List of image metadata for this frame")

    @property
    def gps_point(self) -> GPSPoint:
        """Convert FrameMetadata to GPSPoint."""
        return GPSPoint(
            time=self.time,
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
            orientation=self.orientation,
        )
