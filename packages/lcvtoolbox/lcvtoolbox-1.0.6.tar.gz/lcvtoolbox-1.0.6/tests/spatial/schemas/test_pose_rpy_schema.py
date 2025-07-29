"""Tests for PoseRPYSchema Pydantic model."""

import pytest
import numpy as np
from pydantic import ValidationError

from lcvtoolbox.spatial.schemas import PoseRPYSchema
from lcvtoolbox.spatial.primitives.point import Point3D
from lcvtoolbox.spatial.primitives.rpy import RPY
from lcvtoolbox.spatial.primitives.pose_rpy import PoseRPY
from lcvtoolbox.spatial.primitives.transformation_matrix import TransformationMatrix


class TestPoseRPYSchema:
    """Test cases for PoseRPYSchema class."""
    
    def test_creation_from_dict(self):
        """Test creating PoseRPYSchema from dictionary."""
        data = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
            "roll": 30.0,
            "pitch": 45.0,
            "yaw": 60.0
        }
        
        pose = PoseRPYSchema(**data)
        assert pose.x == 1.0
        assert pose.y == 2.0
        assert pose.z == 3.0
        assert pose.roll == 30.0
        assert pose.pitch == 45.0
        assert pose.yaw == 60.0
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=10, pitch=20, yaw=30)
        
        # Convert to JSON
        json_str = pose.json()
        
        # Parse back from JSON
        pose2 = PoseRPYSchema.parse_raw(json_str)
        
        assert pose2.x == pose.x
        assert pose2.y == pose.y
        assert pose2.z == pose.z
        assert pose2.roll == pose.roll
        assert pose2.pitch == pose.pitch
        assert pose2.yaw == pose.yaw
    
    def test_dict_export(self):
        """Test exporting to dictionary."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=10, pitch=20, yaw=30)
        
        pose_dict = pose.dict()
        assert pose_dict["x"] == 1.0
        assert pose_dict["y"] == 2.0
        assert pose_dict["z"] == 3.0
        assert pose_dict["roll"] == 10.0
        assert pose_dict["pitch"] == 20.0
        assert pose_dict["yaw"] == 30.0
    
    def test_validation_angle_ranges(self):
        """Test angle range validation."""
        # Valid angles
        pose = PoseRPYSchema(x=0, y=0, z=0, roll=180, pitch=90, yaw=-180)
        assert pose.roll == 180
        assert pose.pitch == 90
        assert pose.yaw == -180
        
        # Invalid roll (> 180)
        with pytest.raises(ValidationError):
            PoseRPYSchema(x=0, y=0, z=0, roll=181, pitch=0, yaw=0)
        
        # Invalid pitch (> 90)
        with pytest.raises(ValidationError):
            PoseRPYSchema(x=0, y=0, z=0, roll=0, pitch=91, yaw=0)
        
        # Invalid yaw (< -180)
        with pytest.raises(ValidationError):
            PoseRPYSchema(x=0, y=0, z=0, roll=0, pitch=0, yaw=-181)
    
    def test_validation_finite_values(self):
        """Test finite value validation."""
        # Invalid position (infinity)
        with pytest.raises(ValidationError):
            PoseRPYSchema(x=float('inf'), y=0, z=0, roll=0, pitch=0, yaw=0)
        
        # Invalid position (NaN)
        with pytest.raises(ValidationError):
            PoseRPYSchema(x=float('nan'), y=0, z=0, roll=0, pitch=0, yaw=0)
    
    def test_gimbal_lock_warning(self):
        """Test gimbal lock warning."""
        import warnings
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pose = PoseRPYSchema(x=0, y=0, z=0, roll=0, pitch=89.95, yaw=0)
            assert len(w) == 1
            assert "gimbal lock" in str(w[0].message).lower()
    
    def test_to_point3d(self):
        """Test conversion to Point3D."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=0, pitch=0, yaw=0)
        point = pose.to_point3d()
        
        assert isinstance(point, Point3D)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0
    
    def test_to_rpy_radians(self):
        """Test conversion to RPY in radians."""
        pose = PoseRPYSchema(x=0, y=0, z=0, roll=30, pitch=45, yaw=60)
        rpy = pose.to_rpy_radians()
        
        assert isinstance(rpy, RPY)
        assert rpy.roll == pytest.approx(np.deg2rad(30))
        assert rpy.pitch == pytest.approx(np.deg2rad(45))
        assert rpy.yaw == pytest.approx(np.deg2rad(60))
    
    def test_to_pose_rpy(self):
        """Test conversion to PoseRPY."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=30, pitch=45, yaw=60)
        pose_rpy = pose.to_pose_rpy()
        
        assert isinstance(pose_rpy, PoseRPY)
        assert pose_rpy.x == 1.0
        assert pose_rpy.y == 2.0
        assert pose_rpy.z == 3.0
        assert pose_rpy.roll == pytest.approx(np.deg2rad(30))
        assert pose_rpy.pitch == pytest.approx(np.deg2rad(45))
        assert pose_rpy.yaw == pytest.approx(np.deg2rad(60))
    
    def test_to_transformation_matrix(self):
        """Test conversion to TransformationMatrix."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=0, pitch=0, yaw=0)
        T = pose.to_transformation_matrix()
        
        assert isinstance(T, TransformationMatrix)
        # Check position
        position = T.position
        assert position.x == 1.0
        assert position.y == 2.0
        assert position.z == 3.0
    
    def test_from_pose_rpy(self):
        """Test creation from PoseRPY."""
        position = Point3D(1, 2, 3)
        orientation = RPY.from_degrees(30, 45, 60)
        pose_rpy = PoseRPY(position, orientation)
        
        pose_schema = PoseRPYSchema.from_pose_rpy(pose_rpy)
        
        assert pose_schema.x == 1.0
        assert pose_schema.y == 2.0
        assert pose_schema.z == 3.0
        assert pose_schema.roll == pytest.approx(30)
        assert pose_schema.pitch == pytest.approx(45)
        assert pose_schema.yaw == pytest.approx(60)
    
    def test_from_transformation_matrix(self):
        """Test creation from TransformationMatrix."""
        position = Point3D(1, 2, 3)
        orientation = RPY.from_degrees(30, 45, 60)
        T = TransformationMatrix.from_point_rpy(position, orientation)
        
        pose_schema = PoseRPYSchema.from_transformation_matrix(T)
        
        assert pose_schema.x == pytest.approx(1.0)
        assert pose_schema.y == pytest.approx(2.0)
        assert pose_schema.z == pytest.approx(3.0)
        # Note: Due to gimbal lock and numerical precision, angles might not be exact
        assert abs(pose_schema.roll - 30) < 1.0
        assert abs(pose_schema.pitch - 45) < 1.0
        assert abs(pose_schema.yaw - 60) < 1.0
    
    def test_to_from_list(self):
        """Test conversion to and from list."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=30, pitch=45, yaw=60)
        
        # To list
        pose_list = pose.to_list()
        assert pose_list == [1.0, 2.0, 3.0, 30.0, 45.0, 60.0]
        
        # From list
        pose2 = PoseRPYSchema.from_list(pose_list)
        assert pose2.x == 1.0
        assert pose2.y == 2.0
        assert pose2.z == 3.0
        assert pose2.roll == 30.0
        assert pose2.pitch == 45.0
        assert pose2.yaw == 60.0
        
        # Invalid list length
        with pytest.raises(ValueError):
            PoseRPYSchema.from_list([1, 2, 3])
    
    def test_to_numpy(self):
        """Test conversion to numpy array."""
        pose = PoseRPYSchema(x=1, y=2, z=3, roll=30, pitch=45, yaw=60)
        
        arr = pose.to_numpy()
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (6,)
        assert np.array_equal(arr, np.array([1.0, 2.0, 3.0, 30.0, 45.0, 60.0]))
    
    def test_string_representations(self):
        """Test string representations."""
        pose = PoseRPYSchema(x=1.234, y=2.345, z=3.456, roll=30.1, pitch=45.2, yaw=60.3)
        
        # str representation
        str_repr = str(pose)
        assert "1.234" in str_repr
        assert "30.1°" in str_repr
        
        # repr representation
        repr_str = repr(pose)
        assert "PoseRPYSchema" in repr_str
        assert "x=1.234" in repr_str
    
    def test_api_example(self):
        """Test realistic API/JSON usage example."""
        # Simulate API response
        api_response = {
            "position": {
                "x": 10.5,
                "y": -3.2,
                "z": 2.1
            },
            "orientation": {
                "roll": 15.0,
                "pitch": -10.0,
                "yaw": 45.0
            }
        }
        
        # Flatten the structure for PoseRPYSchema
        pose_data = {
            "x": api_response["position"]["x"],
            "y": api_response["position"]["y"],
            "z": api_response["position"]["z"],
            "roll": api_response["orientation"]["roll"],
            "pitch": api_response["orientation"]["pitch"],
            "yaw": api_response["orientation"]["yaw"]
        }
        
        # Create schema
        pose = PoseRPYSchema(**pose_data)
        
        # Use in application
        pose_rpy = pose.to_pose_rpy()
        T = pose.to_transformation_matrix()
        
        # Transform a point
        test_point = Point3D(1, 0, 0)
        transformed = T.transform_point(test_point)
        
        assert isinstance(transformed, Point3D)
