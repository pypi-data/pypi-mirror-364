"""Tests for core schemas."""

import numpy as np
import pytest
from pydantic import ValidationError

from lcvtoolbox.core.schemas import (
    GPSCoordinates,
    GPSPoint,
    CameraMatrixSchema,
    CameraDistortionSchema,
    FrameMetadata,
    ImageMetadata,
    PoseRPYSchema,
    UTMReference,
    MaskProjectionParams,
)


class TestGPSCoordinates:
    """Test GPS coordinates schema."""

    def test_valid_coordinates(self):
        """Test creating valid GPS coordinates."""
        coords = GPSCoordinates(latitude=48.8566, longitude=2.3522)
        assert coords.latitude == 48.8566
        assert coords.longitude == 2.3522
        assert coords.heading is None

    def test_coordinates_with_heading(self):
        """Test GPS coordinates with heading."""
        coords = GPSCoordinates(latitude=48.8566, longitude=2.3522, heading=45.0)
        assert coords.heading == 45.0

    def test_invalid_latitude(self):
        """Test invalid latitude raises error."""
        with pytest.raises(ValidationError):
            GPSCoordinates(latitude=91.0, longitude=0.0)

    def test_invalid_longitude(self):
        """Test invalid longitude raises error."""
        with pytest.raises(ValidationError):
            GPSCoordinates(latitude=0.0, longitude=181.0)


class TestGPSPoint:
    """Test GPS point schema."""

    def test_valid_gps_point(self):
        """Test creating valid GPS point."""
        gps = GPSPoint(
            time=1234567890,
            latitude=48.8566,
            longitude=2.3522,
            altitude=35.0,
            orientation=90.0
        )
        assert gps.time == 1234567890
        assert gps.latitude == 48.8566
        assert gps.longitude == 2.3522
        assert gps.altitude == 35.0
        assert gps.orientation == 90.0


class TestCameraMatrixSchema:
    """Test camera matrix schema."""

    def test_valid_camera_matrix(self):
        """Test creating valid camera matrix."""
        camera = CameraMatrixSchema(fx=1000.0, fy=1000.0, cx=640.0, cy=480.0)
        assert camera.fx == 1000.0
        assert camera.fy == 1000.0
        assert camera.cx == 640.0
        assert camera.cy == 480.0

    def test_to_matrix(self):
        """Test converting to numpy matrix."""
        camera = CameraMatrixSchema(fx=1000.0, fy=1000.0, cx=640.0, cy=480.0)
        K = camera.to_matrix()
        assert K.shape == (3, 3)
        assert K[0, 0] == 1000.0
        assert K[1, 1] == 1000.0
        assert K[0, 2] == 640.0
        assert K[1, 2] == 480.0


class TestPoseRPYSchema:
    """Test pose with RPY orientation schema."""

    def test_valid_pose(self):
        """Test creating valid pose."""
        pose = PoseRPYSchema(
            x=10.0, y=20.0, z=5.0,
            roll=0.0, pitch=15.0, yaw=90.0
        )
        assert pose.x == 10.0
        assert pose.y == 20.0
        assert pose.z == 5.0
        assert pose.roll == 0.0
        assert pose.pitch == 15.0
        assert pose.yaw == 90.0

    def test_to_transformation_matrix(self):
        """Test converting to transformation matrix."""
        pose = PoseRPYSchema(
            x=10.0, y=20.0, z=5.0,
            roll=0.0, pitch=0.0, yaw=0.0
        )
        T = pose.to_transformation_matrix()
        T_array = np.array(T.matrix)
        assert T_array.shape == (4, 4)
        assert T_array[0, 3] == 10.0
        assert T_array[1, 3] == 20.0
        assert T_array[2, 3] == 5.0


class TestFrameMetadata:
    """Test frame metadata schema."""

    def test_valid_frame_metadata(self):
        """Test creating valid frame metadata."""
        frame = FrameMetadata(
            time=1234567890,
            latitude=48.8566,
            longitude=2.3522,
            altitude=35.0,
            orientation=90.0,
            images=[]
        )
        assert frame.time == 1234567890
        assert frame.latitude == 48.8566
        assert frame.longitude == 2.3522
        assert frame.altitude == 35.0
        assert frame.orientation == 90.0
        assert len(frame.images) == 0

    def test_gps_point_property(self):
        """Test GPS point property conversion."""
        frame = FrameMetadata(
            time=1234567890,
            latitude=48.8566,
            longitude=2.3522,
            altitude=35.0,
            orientation=90.0,
            images=[]
        )
        gps_point = frame.gps_point
        assert gps_point.time == frame.time
        assert gps_point.latitude == frame.latitude
        assert gps_point.longitude == frame.longitude
        assert gps_point.altitude == frame.altitude
        assert gps_point.orientation == frame.orientation


class TestUTMReference:
    """Test UTM reference schema."""

    def test_valid_utm_reference(self):
        """Test creating valid UTM reference."""
        utm = UTMReference(
            easting=448262.0,
            northing=5411932.0,
            zone_number=31,
            zone_letter="U"
        )
        assert utm.easting == 448262.0
        assert utm.northing == 5411932.0
        assert utm.zone_number == 31
        assert utm.zone_letter == "U"

    def test_invalid_zone_number(self):
        """Test invalid UTM zone number raises error."""
        with pytest.raises(ValidationError):
            UTMReference(
                easting=448262.0,
                northing=5411932.0,
                zone_number=61,
                zone_letter="U"
            )

    def test_invalid_zone_letter(self):
        """Test invalid UTM zone letter raises error."""
        with pytest.raises(ValidationError):
            UTMReference(
                easting=448262.0,
                northing=5411932.0,
                zone_number=31,
                zone_letter="A"  # A is not a valid zone letter
            )


class TestMaskProjectionParams:
    """Test mask projection parameters schema."""

    def test_default_params(self):
        """Test mask projection params with defaults."""
        params = MaskProjectionParams()
        assert params.simplify_tolerance == 0.5
        assert params.min_area == 1.0
        assert params.alpha == 2.0
        assert params.use_convex_hull is False

    def test_custom_params(self):
        """Test mask projection params with custom values."""
        params = MaskProjectionParams(
            simplify_tolerance=1.0,
            min_area=5.0,
            alpha=1.0,
            use_convex_hull=True
        )
        assert params.simplify_tolerance == 1.0
        assert params.min_area == 5.0
        assert params.alpha == 1.0
        assert params.use_convex_hull is True
