"""
UTM Capture schema for storing all annotations captured along a trajectory.

The UTMCapture class is designed to efficiently store and manage geographic annotations
(e.g., road damage, signs, etc.) captured from vehicle-mounted cameras along a trajectory.
It provides powerful tools for deduplication, merging, and analysis of annotations.

Key Features:
    - Efficient storage using numpy arrays for camera positions
    - Automatic UTM zone normalization for multi-zone captures
    - List-like views for both frames and annotations
    - Trajectory smoothing to reduce GPS noise
    - Automatic duplicate detection and merging
    - Arc length computation for annotations along trajectory
    - JSON serialization for data persistence

Basic Usage:

1. Creating a capture from annotations:
    ```python
    from lcvtoolbox.core.schemas.utm import UTMCapture, UTMAnnotation, UTMPoint, UTMPolygon
    from shapely.geometry import Polygon

    # Create annotations with camera centers
    annotations = []
    for i in range(10):
        camera = UTMPoint(
            easting=100.0 + i * 5.0,
            northing=200.0,
            zone_number=31,
            zone_letter='U',
            height=2.0
        )

        polygon = UTMPolygon(
            polygon=Polygon([(100 + i*5, 195), (105 + i*5, 195),
                           (105 + i*5, 205), (100 + i*5, 205)]),
            zone_number=31,
            zone_letter='U'
        )

        ann = UTMAnnotation(
            polygon=polygon,
            label="pothole",
            attributes=[AnnotationAttribute(key="severity", value="high")],
            camera_center=camera
        )
        annotations.append(ann)

    # Create capture
    capture = UTMCapture(annotations=annotations)
    ```

2. Creating a capture from frames:
    ```python
    from lcvtoolbox.core.schemas.utm import UTMFrame

    frames = []
    for i in range(5):
        frame = UTMFrame(
            camera_center=UTMPoint(easting=100+i*10, northing=200,
                                 zone_number=31, zone_letter='U'),
            trajectory_index=i
        )
        # Add annotations to frame
        frame.append(annotation1)
        frame.append(annotation2)
        frames.append(frame)

    capture = UTMCapture(frames=frames)
    ```

3. Working with annotations view:
    ```python
    # Access annotations like a list
    print(f"Total annotations: {len(capture.annotations)}")
    first_ann = capture.annotations[0]

    # Iterate over annotations (sorted by arc length if computed)
    for ann in capture.annotations:
        print(f"{ann.label} at {ann.get_center()}")

    # Add new annotation
    capture.annotations.append(new_annotation)
    ```

4. Working with frames view:
    ```python
    # Access frames
    print(f"Total frames: {len(capture.frames)}")

    # Iterate over frames
    for frame in capture.frames:
        print(f"Frame {frame.trajectory_index} has {len(frame)} annotations")
    ```

5. Trajectory operations:
    ```python
    # Get camera trajectory
    trajectory = capture.trajectory
    print(f"Trajectory length: {trajectory.length()} meters")

    # Smooth trajectory to reduce GPS noise
    capture.smooth_trajectory(gps_imprecision=1.0)  # 1 meter GPS error

    # Compute arc lengths for all annotations
    capture.fill_arc_lengths()
    ```

6. Finding and merging duplicates:
    ```python
    # Find overlapping annotations from different frames
    overlapping_groups = capture.find_overlapping_groups(
        iou_threshold=0.1,  # 10% overlap minimum
        same_label=True,
        same_attributes=True
    )

    # Find similar annotations in consecutive frames
    consecutive_groups = capture.find_consecutive_similar_groups(
        angle_threshold=15.0,  # Max 15° angle difference
        form_factor_threshold=0.2,  # Max 20% size ratio difference
        center_distance_threshold=2.0  # Max 2m center distance
    )

    # Merge specific annotations
    capture.merge_annotations([0, 1, 2])  # Merge annotations at indices 0, 1, 2

    # Automatically merge all duplicates
    capture.merge_all_duplicates()
    ```

7. Multi-zone handling:
    ```python
    # UTMCapture automatically handles annotations in different UTM zones
    # It normalizes all annotations to the most common zone
    # This happens transparently during initialization

    ann_zone31 = UTMAnnotation(...,
        polygon=UTMPolygon(..., zone_number=31, zone_letter='U'))
    ann_zone32 = UTMAnnotation(...,
        polygon=UTMPolygon(..., zone_number=32, zone_letter='U'))

    # All annotations will be converted to the dominant zone
    capture = UTMCapture(annotations=[ann_zone31, ann_zone31, ann_zone32])
    print(capture.target_zone)  # (31, 'U')
    ```

8. Saving and loading:
    ```python
    # Save to JSON
    capture.save_json("road_survey.json")

    # Load from JSON
    loaded_capture = UTMCapture.load_json("road_survey.json")

    # Export to dictionary (includes computed metrics)
    data = capture.to_dict()
    # data includes area_square_meters, center, length_on_trajectory for each annotation
    ```

Advanced Features:

1. Custom merging with NA value handling:
    When merging annotations, NA values ("Non renseigné", "NA", "None") are
    automatically replaced with non-NA values from other annotations being merged.

2. Efficient storage:
    Camera centers are stored in a numpy array for memory efficiency, especially
    important for long trajectories with thousands of frames.

3. Sorted annotation access:
    When arc lengths are computed, annotations are automatically sorted along the
    trajectory for sequential processing.

Common Use Cases:

1. Road damage survey deduplication:
    ```python
    # Load captures from multiple survey runs
    capture1 = UTMCapture.load_json("survey_run1.json")
    capture2 = UTMCapture.load_json("survey_run2.json")

    # Combine captures
    all_annotations = []
    for ann in capture1.annotations:
        all_annotations.append(ann)
    for ann in capture2.annotations:
        all_annotations.append(ann)

    # Create combined capture and deduplicate
    combined = UTMCapture(annotations=all_annotations)
    combined.merge_all_duplicates()
    combined.save_json("survey_deduplicated.json")
    ```

2. Filtering annotations by trajectory position:
    ```python
    capture.fill_arc_lengths()

    # Get annotations between 100m and 500m along trajectory
    filtered = []
    for ann in capture.annotations:
        if 100 <= ann.start_arc_length <= 500:
            filtered.append(ann)
    ```

3. Computing statistics per frame:
    ```python
    for frame in capture.frames:
        total_area = frame.get_total_area()
        potholes = frame.get_annotations_by_label("pothole")
        print(f"Frame {frame.trajectory_index}: {len(potholes)} potholes, "
              f"total damage area: {total_area:.2f} m²")
    ```
"""

import json
from collections import Counter, defaultdict
from collections.abc import Iterator
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field

from lcvtoolbox.core.schemas.utm.annotation import AnnotationAttribute, UTMAnnotation
from lcvtoolbox.core.schemas.utm.frame import UTMFrame
from lcvtoolbox.core.schemas.utm.point import UTMPoint
from lcvtoolbox.core.schemas.utm.trajectory import UTMTrajectory

# Define NA attribute values
NA_ATTRIBUTE_VALUES = ["Non renseigné", "NA", "None"]


class FramesView:
    """
    View that provides list-like access to frames in UTMCapture.
    """

    def __init__(self, capture: "UTMCapture"):
        self._capture = capture
        self._frames_cache: list[UTMFrame] | None = None

    def _ensure_cache(self) -> list[UTMFrame]:
        """Build frames cache if needed."""
        if self._frames_cache is None:
            self._frames_cache = []

            # Group annotations by camera center
            frame_groups = defaultdict(list)
            for i, ann_data in enumerate(self._capture.annotations_data):
                camera_idx = ann_data["camera_index"]
                frame_groups[camera_idx].append(i)

            # Create frames
            for camera_idx, ann_indices in sorted(frame_groups.items()):
                camera_center = self._capture.get_camera_center(camera_idx)
                annotations = [self._capture.get_annotation(idx) for idx in ann_indices]

                frame = UTMFrame(annotations=annotations, camera_center=camera_center, trajectory_index=camera_idx)
                self._frames_cache.append(frame)

        return self._frames_cache

    def __len__(self) -> int:
        return len(self._ensure_cache())

    def __getitem__(self, index: int) -> UTMFrame:
        return self._ensure_cache()[index]

    def __iter__(self) -> Iterator[UTMFrame]:
        return iter(self._ensure_cache())

    def append(self, frame: UTMFrame) -> None:
        """Append a frame."""
        # Add camera center if new
        camera_idx = self._capture.add_camera_center(frame.camera_center)

        # Add all annotations
        for ann in frame.annotations:
            self._capture.add_annotation(ann, camera_idx)

        # Clear cache
        self._frames_cache = None

    def pop(self, index: int = -1) -> UTMFrame:
        """Remove and return a frame."""
        frames = self._ensure_cache()
        frame = frames[index]

        # Remove all annotations in this frame
        for ann in frame.annotations:
            # Find annotation index
            for i, ann_data in enumerate(self._capture.annotations_data):
                if ann_data["camera_index"] == frame.trajectory_index:
                    self._capture.annotations_data.pop(i)
                    break

        # Clear cache
        self._frames_cache = None
        return frame


class AnnotationsView:
    """
    View that provides list-like access to annotations in UTMCapture.
    """

    def __init__(self, capture: "UTMCapture"):
        self._capture = capture
        self._sorted_indices: list[int] | None = None

    def _ensure_sorted(self) -> list[int]:
        """Ensure annotations are sorted by start arc length."""
        if self._sorted_indices is None:
            # Get all annotations with their indices
            indices_with_arc = []
            for i, ann_data in enumerate(self._capture.annotations_data):
                start_arc = ann_data.get("start_arc_length")
                # Use index as secondary sort key if arc length is None
                indices_with_arc.append((i, start_arc if start_arc is not None else float("inf"), i))

            # Sort by start arc length, then by index
            indices_with_arc.sort(key=lambda x: (x[1], x[2]))
            self._sorted_indices = [idx for idx, _, _ in indices_with_arc]

        return self._sorted_indices

    def __len__(self) -> int:
        return len(self._capture.annotations_data)

    def __getitem__(self, index: int) -> UTMAnnotation:
        sorted_indices = self._ensure_sorted()
        ann_idx = sorted_indices[index]
        return self._capture.get_annotation(ann_idx)

    def __iter__(self) -> Iterator[UTMAnnotation]:
        for idx in self._ensure_sorted():
            yield self._capture.get_annotation(idx)

    def append(self, annotation: UTMAnnotation) -> None:
        """Append an annotation, computing arc lengths if needed."""
        # Add camera center
        if annotation.camera_center is None:
            raise ValueError("Annotation must have camera_center")

        camera_idx = self._capture.add_camera_center(annotation.camera_center)

        # Compute arc lengths if not present
        if annotation.start_arc_length is None or annotation.end_arc_length is None:
            # Project polygon onto trajectory
            trajectory = self._capture.trajectory
            start_arc, end_arc = trajectory.project_polygon(annotation.polygon)
            annotation.start_arc_length = start_arc
            annotation.end_arc_length = end_arc

        # Add annotation
        self._capture.add_annotation(annotation, camera_idx)

        # Clear sorted cache
        self._sorted_indices = None

    def pop(self, index: int = -1) -> UTMAnnotation:
        """Remove and return an annotation."""
        sorted_indices = self._ensure_sorted()
        ann_idx = sorted_indices[index]

        ann = self._capture.get_annotation(ann_idx)
        self._capture.annotations_data.pop(ann_idx)

        # Clear cache
        self._sorted_indices = None
        return ann


class UTMCapture(BaseModel):
    """
    UTM capture storing all annotations captured along a trajectory.

    Efficiently stores annotations with their camera centers and provides
    various views and operations for analysis and merging.
    """

    # Internal storage - using private attributes instead of fields
    camera_centers: np.ndarray | None = Field(default=None, description="Array of unique camera centers", repr=False)
    camera_zones: list[tuple[int, str]] = Field(default_factory=list, description="UTM zones for camera centers", repr=False)
    annotations_data: list[dict] = Field(default_factory=list, description="Annotation data with references", repr=False)
    target_zone: tuple[int, str] | None = Field(default=None, description="Target UTM zone", repr=False)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def __init__(self, **data):
        """Initialize UTMCapture from frames or annotations."""
        # Handle different initialization methods
        if "frames" in data:
            # Initialize from frames
            frames = data.pop("frames")
            super().__init__(**data)
            self._init_from_frames(frames)
        elif "annotations" in data:
            # Initialize from annotations
            annotations = data.pop("annotations")
            super().__init__(**data)
            self._init_from_annotations(annotations)
        else:
            # Default initialization
            super().__init__(**data)

    def _init_from_frames(self, frames: list[UTMFrame]) -> None:
        """Initialize from list of frames."""
        if not frames:
            return

        # Collect all camera centers and determine target zone
        all_zones = []
        for frame in frames:
            all_zones.append((frame.camera_center.zone_number, frame.camera_center.zone_letter))

        # Find most common zone
        zone_counter = Counter(all_zones)
        self.target_zone = zone_counter.most_common(1)[0][0]

        # Process frames
        for frame in frames:
            # Add camera center
            camera_idx = self.add_camera_center(frame.camera_center)

            # Add annotations
            for ann in frame.annotations:
                ann.camera_center = frame.camera_center
                self.add_annotation(ann, camera_idx)

    def _init_from_annotations(self, annotations: list[UTMAnnotation]) -> None:
        """Initialize from list of annotations."""
        if not annotations:
            return

        # Check all annotations have camera centers
        for ann in annotations:
            if ann.camera_center is None:
                raise ValueError("All annotations must have camera_center")

        # Collect zones
        all_zones = []
        for ann in annotations:
            if ann.camera_center:
                all_zones.append((ann.camera_center.zone_number, ann.camera_center.zone_letter))

        # Find most common zone
        zone_counter = Counter(all_zones)
        self.target_zone = zone_counter.most_common(1)[0][0]

        # Process annotations
        for ann in annotations:
            if ann.camera_center:
                camera_idx = self.add_camera_center(ann.camera_center)
                self.add_annotation(ann, camera_idx)

    def add_camera_center(self, center: UTMPoint) -> int:
        """Add a camera center and return its index."""
        # Convert to target zone if needed
        if self.target_zone and (center.zone_number, center.zone_letter) != self.target_zone:
            center = center.change_zone(self.target_zone[0], self.target_zone[1])

        # Check if already exists
        if self.camera_centers is not None:
            # Find existing
            for i in range(len(self.camera_centers)):
                if abs(self.camera_centers[i, 0] - center.easting) < 0.01 and abs(self.camera_centers[i, 1] - center.northing) < 0.01:
                    return i

        # Add new center
        new_row = np.array([[center.easting, center.northing, center.height or np.nan]])

        if self.camera_centers is None:
            self.camera_centers = new_row
        else:
            self.camera_centers = np.vstack([self.camera_centers, new_row])

        self.camera_zones.append((center.zone_number, center.zone_letter))  # pylint: disable=no-member
        return len(self.camera_centers) - 1

    def get_camera_center(self, index: int) -> UTMPoint:
        """Get camera center by index."""
        if self.camera_centers is None or index >= len(self.camera_centers):
            raise IndexError(f"Camera center index {index} out of range")

        row = self.camera_centers[index]
        zone_num, zone_letter = self.camera_zones[index]

        return UTMPoint(easting=float(row[0]), northing=float(row[1]), zone_number=zone_num, zone_letter=zone_letter, height=None if np.isnan(row[2]) else float(row[2]), forced_zone=False)

    def add_annotation(self, annotation: UTMAnnotation, camera_index: int) -> None:
        """Add an annotation with camera index."""
        # Normalize polygon zone if needed
        if self.target_zone and (annotation.polygon.zone_number, annotation.polygon.zone_letter) != self.target_zone:
            annotation.polygon = annotation.polygon.normalize_to_zone(self.target_zone[0], self.target_zone[1])

        # Store annotation data
        ann_data = {"polygon": annotation.polygon, "label": annotation.label, "attributes": annotation.attributes, "camera_index": camera_index, "start_arc_length": annotation.start_arc_length, "end_arc_length": annotation.end_arc_length}

        self.annotations_data.append(ann_data)  # pylint: disable=no-member

    def get_annotation(self, index: int) -> UTMAnnotation:
        """Get annotation by index."""
        if index >= len(self.annotations_data):
            raise IndexError(f"Annotation index {index} out of range")

        ann_data = self.annotations_data[index]
        camera_center = self.get_camera_center(ann_data["camera_index"])

        return UTMAnnotation(polygon=ann_data["polygon"], label=ann_data["label"], attributes=ann_data["attributes"], camera_center=camera_center, start_arc_length=ann_data.get("start_arc_length"), end_arc_length=ann_data.get("end_arc_length"))

    @property
    def frames(self) -> FramesView:
        """Get frame view of the capture."""
        return FramesView(self)

    @property
    def annotations(self) -> AnnotationsView:
        """Get annotation view of the capture."""
        return AnnotationsView(self)

    @property
    def trajectory(self) -> UTMTrajectory:
        """Get trajectory of camera centers."""
        if self.camera_centers is None or len(self.camera_centers) == 0:
            # Return empty trajectory
            if self.target_zone:
                return UTMTrajectory(zone_number=self.target_zone[0], zone_letter=self.target_zone[1], has_height=False)
            else:
                return UTMTrajectory(zone_number=31, zone_letter="U", has_height=False)  # Default

        # Create UTMPoints
        points = []
        for i in range(len(self.camera_centers)):
            points.append(self.get_camera_center(i))

        return UTMTrajectory.from_points(points)

    def smooth_trajectory(self, gps_imprecision: float = 1.0) -> None:
        """
        Smooth the trajectory to reduce GPS noise.

        Args:
            gps_imprecision: GPS imprecision in meters (default: 1.0).
        """
        if self.camera_centers is None or len(self.camera_centers) < 3:
            return  # Not enough points to smooth

        # Simple moving average smoothing
        window_size = 3
        smoothed = np.copy(self.camera_centers)

        for i in range(1, len(self.camera_centers) - 1):
            # Average with neighbors
            smoothed[i, :2] = np.mean(self.camera_centers[i - 1 : i + 2, :2], axis=0)

            # Limit movement by GPS imprecision
            delta = smoothed[i, :2] - self.camera_centers[i, :2]
            delta_norm = np.linalg.norm(delta)
            if delta_norm > gps_imprecision:
                smoothed[i, :2] = self.camera_centers[i, :2] + delta * (gps_imprecision / delta_norm)

        self.camera_centers = smoothed

    def fill_arc_lengths(self) -> None:
        """Fill start and end arc lengths for all annotations."""
        trajectory = self.trajectory

        for ann_data in self.annotations_data:
            if ann_data.get("start_arc_length") is None or ann_data.get("end_arc_length") is None:
                # Project polygon
                start_arc, end_arc = trajectory.project_polygon(ann_data["polygon"])
                ann_data["start_arc_length"] = start_arc
                ann_data["end_arc_length"] = end_arc

                # Also compute total length
                ann_data["length"] = end_arc - start_arc

    def find_overlapping_groups(self, iou_threshold: float = 0.01, same_label: bool = True, same_attributes: bool = True, ignore_attributes: list[str] | None = None) -> list[list[int]]:
        """
        Find groups of annotations with overlapping polygons.

        Args:
            iou_threshold: Minimum IoU to consider overlap (default: 0.01).
            same_label: If True, only group annotations with same label.
            same_attributes: If True, only group annotations with same attributes.
            ignore_attributes: List of attribute keys to ignore in comparison.

        Returns:
            List of annotation index groups.
        """
        groups = []
        processed = set()

        for i in range(len(self.annotations_data)):  # pylint: disable=consider-using-enumerate
            if i in processed:
                continue

            group = [i]
            processed.add(i)
            ann_i = self.get_annotation(i)

            for j in range(i + 1, len(self.annotations_data)):
                if j in processed:
                    continue

                ann_j = self.get_annotation(j)

                # Check if from different frames
                if self.annotations_data[i]["camera_index"] == self.annotations_data[j]["camera_index"]:
                    continue

                # Check label
                if same_label and ann_i.label != ann_j.label:
                    continue

                # Check attributes
                if same_attributes:
                    attrs_match = True
                    attrs_i = {a.key: a.value for a in ann_i.attributes if a.key not in (ignore_attributes or [])}
                    attrs_j = {a.key: a.value for a in ann_j.attributes if a.key not in (ignore_attributes or [])}
                    if attrs_i != attrs_j:
                        attrs_match = False

                    if not attrs_match:
                        continue

                # Check IoU
                iou = ann_i.polygon.intersection_over_union(ann_j.polygon)  # pylint: disable=no-member
                if iou >= iou_threshold:
                    group.append(j)
                    processed.add(j)

            if len(group) > 1:
                groups.append(group)

        return groups

    def find_consecutive_similar_groups(
        self, angle_threshold: float = 10.0, form_factor_threshold: float = 0.2, center_distance_threshold: float = 1.0, same_label: bool = True, same_attributes: bool = True, ignore_attributes: list[str] | None = None
    ) -> list[list[int]]:
        """
        Find groups of similar annotations from consecutive frames.

        Args:
            angle_threshold: Maximum angle difference in degrees (default: 10.0).
            form_factor_threshold: Maximum form factor difference ratio (default: 0.2).
            center_distance_threshold: Maximum center distance in meters (default: 1.0).
            same_label: If True, only group annotations with same label.
            same_attributes: If True, only group annotations with same attributes.
            ignore_attributes: List of attribute keys to ignore.

        Returns:
            List of annotation index groups.
        """
        groups = []
        processed = set()

        # Sort annotations by camera index (frame order)
        sorted_indices = sorted(range(len(self.annotations_data)), key=lambda i: self.annotations_data[i]["camera_index"])

        for i_idx, i in enumerate(sorted_indices):
            if i in processed:
                continue

            group = [i]
            processed.add(i)
            ann_i = self.get_annotation(i)
            bbox_i, angle_i, length_i, width_i = ann_i.get_oriented_bounding_box()
            center_i = ann_i.get_center()
            form_factor_i = length_i / width_i if width_i > 0 else float("inf")

            # Look at next annotations
            for j_idx in range(i_idx + 1, len(sorted_indices)):
                j = sorted_indices[j_idx]

                if j in processed:
                    continue

                # Check if consecutive frames
                if (self.annotations_data[j]["camera_index"] - self.annotations_data[i]["camera_index"]) > len(group):
                    break

                ann_j = self.get_annotation(j)

                # Check label
                if same_label and ann_i.label != ann_j.label:
                    continue

                # Check attributes
                if same_attributes:
                    attrs_i = {a.key: a.value for a in ann_i.attributes if a.key not in (ignore_attributes or [])}
                    attrs_j = {a.key: a.value for a in ann_j.attributes if a.key not in (ignore_attributes or [])}
                    if attrs_i != attrs_j:
                        continue

                # Check similarity
                bbox_j, angle_j, length_j, width_j = ann_j.get_oriented_bounding_box()
                center_j = ann_j.get_center()
                form_factor_j = length_j / width_j if width_j > 0 else float("inf")

                # Angle difference
                angle_diff = abs(angle_i - angle_j)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff

                if angle_diff > angle_threshold:
                    continue

                # Form factor difference
                if form_factor_i > 0 and form_factor_j > 0:
                    ff_ratio = max(form_factor_i / form_factor_j, form_factor_j / form_factor_i) - 1
                    if ff_ratio > form_factor_threshold:
                        continue

                # Center distance
                center_dist = center_i.distance_to(center_j)
                if center_dist > center_distance_threshold:
                    continue

                # Add to group
                group.append(j)
                processed.add(j)

                # Update reference for next comparison
                ann_i = ann_j
                bbox_i, angle_i, length_i, width_i = bbox_j, angle_j, length_j, width_j
                center_i = center_j
                form_factor_i = form_factor_j

            if len(group) > 1:
                groups.append(group)

        return groups

    def merge_annotations(self, indices: list[int]) -> None:
        """
        Merge annotations at given indices.

        The last annotation's camera_center, label and attributes prevail,
        except for NA values where previous values are used.

        Args:
            indices: List of annotation indices to merge.
        """
        if len(indices) < 2:
            return

        # Get annotations
        annotations = [self.get_annotation(i) for i in indices]

        # Start with last annotation
        merged = annotations[-1]
        merged_polygon = merged.polygon

        # Merge polygons
        for ann in annotations[:-1]:
            merged_polygon = merged_polygon.merge_with(ann.polygon)

        # Merge attributes - use last non-NA value
        merged_attrs = {}
        for ann in annotations:
            for attr in ann.attributes:
                if attr.value not in NA_ATTRIBUTE_VALUES:
                    merged_attrs[attr.key] = attr.value

        # Use last annotation's attributes but override NA values
        final_attrs = []
        for attr in merged.attributes:
            if attr.value in NA_ATTRIBUTE_VALUES and attr.key in merged_attrs:
                final_attrs.append(AnnotationAttribute(key=attr.key, value=merged_attrs[attr.key]))
            else:
                final_attrs.append(attr)

        # Add any missing attributes
        existing_keys = {attr.key for attr in final_attrs}
        for key, value in merged_attrs.items():
            if key not in existing_keys:
                final_attrs.append(AnnotationAttribute(key=key, value=value))

        # Create merged annotation
        # Get arc lengths - only if at least one annotation has them
        start_arcs = [ann.start_arc_length for ann in annotations if ann.start_arc_length is not None]
        end_arcs = [ann.end_arc_length for ann in annotations if ann.end_arc_length is not None]

        merged_annotation = UTMAnnotation(
            polygon=merged_polygon, label=merged.label, attributes=final_attrs, camera_center=merged.camera_center, start_arc_length=min(start_arcs) if start_arcs else None, end_arc_length=max(end_arcs) if end_arcs else None
        )

        # Remove old annotations (in reverse order to maintain indices)
        for i in sorted(indices, reverse=True):
            self.annotations_data.pop(i)  # pylint: disable=no-member

        # Add merged annotation
        if merged_annotation.camera_center:
            camera_idx = self.add_camera_center(merged_annotation.camera_center)
            self.add_annotation(merged_annotation, camera_idx)

    def merge_all_duplicates(self, label_attribute_ignore: dict[str, list[str]] | None = None) -> None:
        """
        Merge all annotations that are duplicates from different frames.

        Args:
            label_attribute_ignore: Dict mapping labels to lists of attribute keys to ignore.
        """
        # First find overlapping groups
        overlapping_groups = self.find_overlapping_groups(iou_threshold=0.01, same_label=True, same_attributes=True, ignore_attributes=None)

        # Then find consecutive similar groups
        consecutive_groups = self.find_consecutive_similar_groups(angle_threshold=15.0, form_factor_threshold=0.3, center_distance_threshold=2.0, same_label=True, same_attributes=True, ignore_attributes=None)

        # Merge groups
        all_groups = overlapping_groups + consecutive_groups

        # Remove duplicates and merge overlapping groups
        merged_groups = []
        processed = set()

        for group in all_groups:
            # Skip if any index already processed
            if any(idx in processed for idx in group):
                # Find which existing group overlaps
                for i, existing in enumerate(merged_groups):
                    if any(idx in existing for idx in group):
                        # Merge groups
                        merged_groups[i] = list(set(existing + group))
                        processed.update(group)
                        break
            else:
                merged_groups.append(group)
                processed.update(group)

        # Merge each group
        for group in merged_groups:
            if len(group) > 1:
                self.merge_annotations(group)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        # Get all annotations with computed metrics
        annotations_list = []
        for i in range(len(self.annotations_data)):
            ann = self.get_annotation(i)
            ann_dict = ann.to_dict()

            # Add computed metrics
            ann_dict["area_square_meters"] = ann.area_square_meters()
            center = ann.get_center()
            ann_dict["center"] = center.to_dict()

            if ann.start_arc_length is not None and ann.end_arc_length is not None:
                ann_dict["length_on_trajectory"] = ann.end_arc_length - ann.start_arc_length

            annotations_list.append(ann_dict)

        return {"annotations": annotations_list, "target_zone": {"zone_number": self.target_zone[0], "zone_letter": self.target_zone[1]} if self.target_zone else None}

    @classmethod
    def from_dict(cls, data: dict) -> "UTMCapture":
        """Create from dictionary."""
        annotations = [UTMAnnotation.from_dict(ann) for ann in data.get("annotations", [])]

        capture = cls()

        # Set target zone if provided
        if "target_zone" in data and data["target_zone"]:
            capture.target_zone = (data["target_zone"]["zone_number"], data["target_zone"]["zone_letter"])

        # Initialize from annotations
        if annotations:
            capture._init_from_annotations(annotations)

        return capture

    def save_json(self, filepath: str | Path) -> None:
        """Save to JSON file."""
        filepath = Path(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, filepath: str | Path) -> "UTMCapture":
        """Load from JSON file."""
        filepath = Path(filepath)
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
