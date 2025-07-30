"""
Tests for UTMCapture schema and related classes.
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import Polygon

from lcvtoolbox.core.schemas.utm import (
    AnnotationAttribute,
    UTMAnnotation,
    UTMCapture,
    UTMFrame,
    UTMPoint,
    UTMPolygon,
)


class TestUTMCapture:
    """Test UTMCapture class functionality."""

    @pytest.fixture
    def sample_annotations(self):
        """Create sample annotations for testing."""
        annotations = []
        for i in range(5):
            # Camera moves along trajectory
            camera = UTMPoint(
                easting=100.0 + i * 4.0,  # 4m between shots
                northing=200.0,
                zone_number=31,
                zone_letter="U",
                height=2.0,
                forced_zone=False,
            )

            # Create overlapping damage annotations
            polygon = UTMPolygon(
                polygon=Polygon(
                    [
                        (100 + i * 3.8, 195),  # Slight overlap
                        (100 + i * 3.8 + 5, 195),
                        (100 + i * 3.8 + 5, 205),
                        (100 + i * 3.8, 205),
                        (100 + i * 3.8, 195),
                    ]
                ),
                zone_number=31,
                zone_letter="U",
                simplify_tolerance=0.1,
            )

            ann = UTMAnnotation(polygon=polygon, label="crack", attributes=[AnnotationAttribute(key="severity", value="medium")], camera_center=camera, start_arc_length=None, end_arc_length=None)
            annotations.append(ann)

        return annotations

    @pytest.fixture
    def sample_frames(self):
        """Create sample frames for testing."""
        frames = []
        for i in range(3):
            camera = UTMPoint(easting=200.0 + i * 5.0, northing=300.0, zone_number=31, zone_letter="U", height=1.5, forced_zone=False)

            frame = UTMFrame(camera_center=camera, trajectory_index=i)

            # Add annotations to frame
            for j in range(2):
                polygon = UTMPolygon(
                    polygon=Polygon(
                        [
                            (200 + i * 5 + j * 2, 295),
                            (202 + i * 5 + j * 2, 295),
                            (202 + i * 5 + j * 2, 305),
                            (200 + i * 5 + j * 2, 305),
                            (200 + i * 5 + j * 2, 295),
                        ],
                    ),
                    zone_number=31,
                    zone_letter="U",
                    simplify_tolerance=0.1,
                )

                ann = UTMAnnotation(
                    polygon=polygon,
                    label=f"damage_{i}_{j}",
                    attributes=[AnnotationAttribute(key="type", value="pothole"), AnnotationAttribute(key="size", value="small")],
                    camera_center=camera,
                    start_arc_length=None,
                    end_arc_length=None,
                )
                frame.append(ann)

            frames.append(frame)

        return frames

    def test_init_empty(self):
        """Test empty capture initialization."""
        capture = UTMCapture()
        assert len(capture.annotations) == 0
        assert len(capture.frames) == 0
        assert capture.target_zone is None

    def test_init_from_annotations(self, sample_annotations):
        """Test initialization from annotations."""
        capture = UTMCapture(annotations=sample_annotations)
        assert len(capture.annotations) == 5
        assert capture.target_zone == (31, "U")

        # Check annotations are accessible
        first_ann = capture.annotations[0]
        assert first_ann.label == "crack"
        assert first_ann.camera_center is not None

    def test_init_from_frames(self, sample_frames):
        """Test initialization from frames."""
        capture = UTMCapture(frames=sample_frames)
        assert len(capture.frames) == 3
        assert len(capture.annotations) == 6  # 3 frames * 2 annotations
        assert capture.target_zone == (31, "U")

    def test_annotations_view(self, sample_annotations):
        """Test AnnotationsView functionality."""
        capture = UTMCapture(annotations=sample_annotations)

        # Test list-like behavior
        assert len(capture.annotations) == 5
        assert capture.annotations[0].label == "crack"

        # Test iteration
        labels = [ann.label for ann in capture.annotations]
        assert all(label == "crack" for label in labels)

        # Test append
        new_ann = sample_annotations[0]
        new_ann.label = "new_damage"
        capture.annotations.append(new_ann)
        assert len(capture.annotations) == 6

    def test_frames_view(self, sample_frames):
        """Test FramesView functionality."""
        capture = UTMCapture(frames=sample_frames)

        # Test list-like behavior
        assert len(capture.frames) == 3
        assert capture.frames[0].trajectory_index == 0

        # Test iteration
        indices = [frame.trajectory_index for frame in capture.frames]
        assert indices == [0, 1, 2]

    def test_trajectory_property(self, sample_annotations):
        """Test trajectory generation."""
        capture = UTMCapture(annotations=sample_annotations)
        trajectory = capture.trajectory

        assert len(trajectory) == 5
        assert trajectory.zone_number == 31
        assert trajectory.zone_letter == "U"

        # Check trajectory points match camera centers
        first_point = trajectory.points[0]
        assert first_point.easting == 100.0
        assert first_point.northing == 200.0

    def test_smooth_trajectory(self):
        """Test trajectory smoothing."""
        # Create annotations with a zigzag pattern that needs smoothing
        annotations = []
        for i in range(5):
            # Camera moves along trajectory with noise
            camera = UTMPoint(
                easting=100.0 + i * 4.0,
                northing=200.0 + (i % 2) * 0.5,  # Zigzag pattern
                zone_number=31,
                zone_letter="U",
                height=2.0,
                forced_zone=False,
            )

            polygon = UTMPolygon(
                polygon=Polygon([(100 + i * 3.8, 195), (100 + i * 3.8 + 5, 195), (100 + i * 3.8 + 5, 205), (100 + i * 3.8, 205), (100 + i * 3.8, 195)]),
                zone_number=31,
                zone_letter="U",
                simplify_tolerance=0.1,
            )

            ann = UTMAnnotation(polygon=polygon, label="crack", attributes=[AnnotationAttribute(key="severity", value="medium")], camera_center=camera, start_arc_length=None, end_arc_length=None)
            annotations.append(ann)

        capture = UTMCapture(annotations=annotations)

        # Get original positions
        assert capture.camera_centers is not None
        original_centers = np.copy(capture.camera_centers)

        # Apply smoothing
        capture.smooth_trajectory(gps_imprecision=0.5)

        # Check that positions changed but not too much
        assert capture.camera_centers is not None
        assert not np.array_equal(original_centers, capture.camera_centers)

        # Check smoothing is within GPS imprecision
        deltas = np.abs(capture.camera_centers - original_centers)
        assert np.all(deltas[:, :2] <= 0.5)

        # Check that zigzag pattern was smoothed out (points with noise should have moved closer to straight line)
        # The smoothed trajectory should be straighter than the original
        original_variance = np.var(original_centers[1:-1, 1])
        smoothed_variance = np.var(capture.camera_centers[1:-1, 1])
        assert smoothed_variance < original_variance

    def test_fill_arc_lengths(self, sample_annotations):
        """Test arc length computation."""
        capture = UTMCapture(annotations=sample_annotations)

        # Initially no arc lengths
        for ann_data in capture.annotations_data:
            assert ann_data.get("start_arc_length") is None

        # Fill arc lengths
        capture.fill_arc_lengths()

        # Check arc lengths are filled
        for ann_data in capture.annotations_data:
            assert ann_data.get("start_arc_length") is not None
            assert ann_data.get("end_arc_length") is not None
            assert ann_data.get("length") is not None
            assert ann_data["end_arc_length"] > ann_data["start_arc_length"]

    def test_find_overlapping_groups(self, sample_annotations):
        """Test finding overlapping annotation groups."""
        capture = UTMCapture(annotations=sample_annotations)

        # Find overlapping groups
        groups = capture.find_overlapping_groups(iou_threshold=0.01)

        # Should find overlapping annotations
        assert len(groups) > 0
        assert all(len(group) >= 2 for group in groups)

        # Check that grouped annotations actually overlap
        for group in groups:
            anns = [capture.get_annotation(i) for i in group]
            for i in range(len(anns) - 1):
                iou = anns[i].polygon.intersection_over_union(anns[i + 1].polygon)
                assert iou >= 0.01

    def test_find_consecutive_similar_groups(self):
        """Test finding similar annotations in consecutive frames."""
        # Create annotations with similar properties
        annotations = []
        for i in range(4):
            camera = UTMPoint(easting=300.0 + i * 2.0, northing=400.0, zone_number=31, zone_letter="U", height=2.0, forced_zone=False)

            # Similar rectangles with slight variations
            polygon = UTMPolygon(
                polygon=Polygon(
                    [
                        (300, 395),
                        (310, 395 + i * 0.1),  # Slight angle change
                        (310, 405 + i * 0.1),
                        (300, 405),
                        (300, 395),
                    ]
                ),
                zone_number=31,
                zone_letter="U",
                simplify_tolerance=0.1,
            )

            ann = UTMAnnotation(polygon=polygon, label="barrier", attributes=[AnnotationAttribute(key="material", value="concrete")], camera_center=camera, start_arc_length=None, end_arc_length=None)
            annotations.append(ann)

        capture = UTMCapture(annotations=annotations)

        # Find similar consecutive groups
        groups = capture.find_consecutive_similar_groups(angle_threshold=15.0, form_factor_threshold=0.3, center_distance_threshold=2.0)

        assert len(groups) > 0
        # Should group all similar annotations
        assert any(len(group) >= 3 for group in groups)

    def test_merge_annotations(self, sample_annotations):
        """Test annotation merging."""
        capture = UTMCapture(annotations=sample_annotations)
        initial_count = len(capture.annotations)

        # Merge first two annotations
        capture.merge_annotations([0, 1])

        # Check count decreased
        assert len(capture.annotations) == initial_count - 1

        # Check merged annotation has correct properties
        merged = capture.annotations[initial_count - 2]  # Last annotation
        assert merged.label == "crack"
        assert merged.polygon.area_square_meters() > sample_annotations[0].polygon.area_square_meters()

    def test_merge_annotations_with_na_values(self):
        """Test merging with NA attribute values."""
        # Create annotations with NA values
        camera = UTMPoint(easting=500, northing=600, zone_number=31, zone_letter="U", height=2.0, forced_zone=False)

        polygon1 = UTMPolygon(polygon=Polygon([(500, 595), (510, 595), (510, 605), (500, 605), (500, 595)]), zone_number=31, zone_letter="U", simplify_tolerance=0.1)

        polygon2 = UTMPolygon(polygon=Polygon([(508, 595), (518, 595), (518, 605), (508, 605), (508, 595)]), zone_number=31, zone_letter="U", simplify_tolerance=0.1)

        ann1 = UTMAnnotation(
            polygon=polygon1,
            label="damage",
            attributes=[AnnotationAttribute(key="severity", value="high"), AnnotationAttribute(key="type", value="Non renseigné")],
            camera_center=camera,
            start_arc_length=None,
            end_arc_length=None,
        )

        ann2 = UTMAnnotation(
            polygon=polygon2,
            label="damage",
            attributes=[AnnotationAttribute(key="severity", value="NA"), AnnotationAttribute(key="type", value="crack")],
            camera_center=camera,
            start_arc_length=None,
            end_arc_length=None,
        )

        capture = UTMCapture(annotations=[ann1, ann2])
        capture.merge_annotations([0, 1])

        # Check merged annotation uses non-NA values
        merged = capture.annotations[0]
        attrs = {attr.key: attr.value for attr in merged.attributes}
        assert attrs["severity"] == "high"  # From ann1
        assert attrs["type"] == "crack"  # From ann2

    def test_merge_all_duplicates(self, sample_annotations):
        """Test automatic duplicate merging."""
        capture = UTMCapture(annotations=sample_annotations)
        initial_count = len(capture.annotations)

        # Merge all duplicates
        capture.merge_all_duplicates()

        # Should have fewer annotations
        assert len(capture.annotations) < initial_count

    def test_to_dict_from_dict(self, sample_annotations):
        """Test dictionary serialization."""
        capture = UTMCapture(annotations=sample_annotations)
        capture.fill_arc_lengths()

        # Convert to dict
        data = capture.to_dict()

        assert "annotations" in data
        assert len(data["annotations"]) == 5
        assert data["target_zone"]["zone_number"] == 31
        assert data["target_zone"]["zone_letter"] == "U"

        # Check computed metrics are included
        first_ann = data["annotations"][0]
        assert "area_square_meters" in first_ann
        assert "center" in first_ann
        assert "length_on_trajectory" in first_ann

        # Reconstruct from dict
        capture2 = UTMCapture.from_dict(data)
        assert len(capture2.annotations) == 5
        assert capture2.target_zone == (31, "U")

    def test_save_load_json(self, sample_annotations):
        """Test JSON file operations."""
        capture = UTMCapture(annotations=sample_annotations)
        capture.fill_arc_lengths()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_capture.json"

            # Save to JSON
            capture.save_json(filepath)
            assert filepath.exists()

            # Load from JSON
            capture2 = UTMCapture.load_json(filepath)
            assert len(capture2.annotations) == len(capture.annotations)
            assert capture2.target_zone == capture.target_zone

            # Verify data integrity
            for i in range(len(capture.annotations)):  # pylint: disable=consider-using-enumerate
                ann1 = capture.annotations[i]
                ann2 = capture2.annotations[i]
                assert ann1.label == ann2.label
                assert ann1.area_square_meters() == pytest.approx(ann2.area_square_meters())

    def test_multi_zone_handling(self):
        """Test handling of annotations in different UTM zones."""
        # Create annotations in different zones
        ann1 = UTMAnnotation(
            polygon=UTMPolygon(polygon=Polygon([(100, 100), (200, 100), (200, 200), (100, 200), (100, 100)]), zone_number=31, zone_letter="U", simplify_tolerance=0.1),
            label="zone31",
            attributes=[],
            camera_center=UTMPoint(easting=150, northing=150, zone_number=31, zone_letter="U", height=2.0, forced_zone=False),
            start_arc_length=None,
            end_arc_length=None,
        )

        ann2 = UTMAnnotation(
            polygon=UTMPolygon(polygon=Polygon([(100, 100), (200, 100), (200, 200), (100, 200), (100, 100)]), zone_number=32, zone_letter="U", simplify_tolerance=0.1),
            label="zone32",
            attributes=[],
            camera_center=UTMPoint(easting=150, northing=150, zone_number=32, zone_letter="U", height=2.0, forced_zone=False),
            start_arc_length=None,
            end_arc_length=None,
        )

        # Create capture - should normalize to most common zone
        capture = UTMCapture(annotations=[ann1, ann1, ann2])  # Zone 31 is more common

        assert capture.target_zone == (31, "U")
        assert len(capture.annotations) == 3

        # All annotations should be in zone 31 now
        for ann in capture.annotations:
            assert ann.polygon.zone_number == 31
            assert ann.polygon.zone_letter == "U"

    def test_empty_capture_trajectory(self):
        """Test trajectory property on empty capture."""
        capture = UTMCapture()
        trajectory = capture.trajectory

        assert len(trajectory) == 0
        assert trajectory.zone_number == 31  # Default
        assert trajectory.zone_letter == "U"  # Default

    def test_annotations_sorting_by_arc_length(self, sample_annotations):
        """Test that annotations are sorted by arc length."""
        capture = UTMCapture(annotations=sample_annotations)
        capture.fill_arc_lengths()

        # Get arc lengths in order
        arc_lengths = []
        for ann in capture.annotations:
            arc_lengths.append(ann.start_arc_length)

        # Check they are sorted
        assert arc_lengths == sorted(arc_lengths)

    def test_frame_annotation_consistency(self, sample_frames):
        """Test consistency between frames and annotations views."""
        capture = UTMCapture(frames=sample_frames)

        # Count annotations in frames
        frame_ann_count = sum(len(frame) for frame in capture.frames)

        # Should match total annotations
        assert frame_ann_count == len(capture.annotations)

        # Check all annotations have camera centers
        for ann in capture.annotations:
            assert ann.camera_center is not None

    def test_annotation_without_camera_center(self):
        """Test error handling for annotations without camera center."""
        polygon = UTMPolygon(polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]), zone_number=31, zone_letter="U", simplify_tolerance=0.1)

        ann = UTMAnnotation(polygon=polygon, label="test", attributes=[], camera_center=None, start_arc_length=None, end_arc_length=None)

        with pytest.raises(ValueError, match="camera_center"):
            UTMCapture(annotations=[ann])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
