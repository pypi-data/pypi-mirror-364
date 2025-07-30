"""
UTM Annotation schema for geographic annotation operations.
"""

from typing import Literal, Optional, Tuple
import numpy as np

from pydantic import BaseModel, Field
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.affinity import rotate

from lcvtoolbox.core.schemas.utm.point import UTMPoint
from lcvtoolbox.core.schemas.utm.polygon import UTMPolygon


class AnnotationAttribute(BaseModel):
    """
    Simple key-value attribute for annotations.

    Represents a single attribute as a key-value pair of strings.
    """

    key: str = Field(..., description="Attribute key/name")
    value: str = Field(..., description="Attribute value")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {"example": {"key": "color", "value": "red"}}


class UTMAnnotation(BaseModel):
    """
    UTM annotation with polygon, label, and attributes.

    Contains a UTM polygon geometry, a class label, and a list of attributes
    for comprehensive geographic annotation representation.
    """

    polygon: UTMPolygon = Field(..., description="UTM polygon geometry")
    label: str = Field(..., description="Class label for the annotation")
    attributes: list[AnnotationAttribute] = Field(default_factory=list, description="List of key-value attributes")
    camera_center: Optional[UTMPoint] = Field(None, description="Optional camera center point from which this annotation was captured")
    start_arc_length: Optional[float] = Field(None, description="Start arc length when projected on trajectory (meters)")
    end_arc_length: Optional[float] = Field(None, description="End arc length when projected on trajectory (meters)")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "polygon": {"polygon": {"exterior": [(448262.0, 5411932.0), (448300.0, 5411932.0), (448300.0, 5411970.0), (448262.0, 5411970.0), (448262.0, 5411932.0)], "interiors": []}, "zone_number": 31, "zone_letter": "U"},
                "label": "vehicle",
                "attributes": [{"key": "color", "value": "red"}, {"key": "type", "value": "car"}],
                "camera_center": {"easting": 448280.0, "northing": 5411900.0, "zone_number": 31, "zone_letter": "U", "height": 150.0},
            }
        }

    def has_same_label_and_attributes(self, other: "UTMAnnotation") -> bool:
        """
        Check if two annotations have the same label and attributes.

        Args:
            other: Another UTMAnnotation to compare with.

        Returns:
            bool: True if both label and all attributes match, False otherwise.

        Example:
            >>> ann1 = UTMAnnotation(...)
            >>> ann2 = UTMAnnotation(...)
            >>> if ann1.has_same_label_and_attributes(ann2):
            ...     print("Annotations have same label and attributes")
        """
        # Check if labels match
        if self.label != other.label:
            return False

        # Check if attribute counts match
        if len(self.attributes) != len(other.attributes):
            return False

        # Convert attributes to dictionaries for easier comparison
        self_attrs = {attr.key: attr.value for attr in self.attributes}
        other_attrs = {attr.key: attr.value for attr in other.attributes}

        # Check if all attributes match
        return self_attrs == other_attrs

    def significantly_intersects(self, other: "UTMAnnotation", iou_threshold: float = 0.01) -> bool:
        """
        Check if two annotations significantly intersect based on IoU threshold.

        Args:
            other: Another UTMAnnotation to check intersection with.
            iou_threshold: Minimum IoU value to consider as significant intersection.
                          Default is 0.01 (1% overlap).

        Returns:
            bool: True if IoU >= threshold, False otherwise.

        Raises:
            ValueError: If the polygons are in different UTM zones.

        Example:
            >>> ann1 = UTMAnnotation(...)
            >>> ann2 = UTMAnnotation(...)
            >>> if ann1.significantly_intersects(ann2, iou_threshold=0.3):
            ...     print("Annotations significantly overlap")
        """
        iou = self.polygon.intersection_over_union(other.polygon)  # pylint: disable=no-member
        return iou >= iou_threshold

    def is_compatible_for_merging(self, other: "UTMAnnotation", iou_threshold: float = 0.01) -> bool:
        """
        Check if two annotations can be merged (same label, attributes, and significant intersection).

        Args:
            other: Another UTMAnnotation to check compatibility with.
            iou_threshold: Minimum IoU value to consider as significant intersection.
                          Default is 0.01 (1% overlap).

        Returns:
            bool: True if annotations can be merged, False otherwise.

        Example:
            >>> ann1 = UTMAnnotation(...)
            >>> ann2 = UTMAnnotation(...)
            >>> if ann1.is_compatible_for_merging(ann2):
            ...     merged = ann1.merge_with(ann2)
        """
        return self.has_same_label_and_attributes(other) and self.significantly_intersects(other, iou_threshold)

    def merge_with(self, other: "UTMAnnotation") -> "UTMAnnotation":
        """
        Merge this annotation with another annotation unconditionally.

        Creates a new annotation with the union of both polygons. This method
        performs the merge without any condition checks. The resulting annotation
        will keep the label and attributes from self.

        Args:
            other: Another UTMAnnotation to merge with.

        Returns:
            UTMAnnotation: A new annotation with merged polygon geometry.

        Raises:
            ValueError: If the polygons are in different UTM zones or if the
                       union operation fails.

        Example:
            >>> ann1 = UTMAnnotation(...)
            >>> ann2 = UTMAnnotation(...)
            >>> merged = ann1.merge_with(ann2)
            >>> print(f"Merged area: {merged.polygon.area_square_meters():.2f} m²")
        """
        # Validate zones match
        if (
            self.polygon.zone_number != other.polygon.zone_number  # pylint: disable=no-member
            or self.polygon.zone_letter != other.polygon.zone_letter
        ):  # pylint: disable=no-member
            raise ValueError(
                f"Cannot merge annotations in different UTM zones: "
                f"{self.polygon.zone_number}{self.polygon.zone_letter} vs "  # pylint: disable=no-member
                f"{other.polygon.zone_number}{other.polygon.zone_letter}"  # pylint: disable=no-member
            )

        # Merge the polygons using union
        union_result = unary_union([self.polygon.polygon, other.polygon.polygon])  # pylint: disable=no-member

        # Handle different geometry types that unary_union might return
        if isinstance(union_result, Polygon):
            union_polygon = union_result
        elif isinstance(union_result, MultiPolygon):
            # If MultiPolygon, take the largest polygon
            union_polygon = max(union_result.geoms, key=lambda p: p.area)
        else:
            raise ValueError(f"Union operation resulted in unsupported geometry type: {type(union_result)}")

        # Create new UTMPolygon with the merged geometry
        merged_utm_polygon = UTMPolygon(
            polygon=union_polygon,
            zone_number=self.polygon.zone_number,  # pylint: disable=no-member
            zone_letter=self.polygon.zone_letter,  # pylint: disable=no-member
            simplify_tolerance=self.polygon.simplify_tolerance  # pylint: disable=no-member
        )

        # Create new annotation with merged polygon, keeping self's label, attributes, and camera center
        return UTMAnnotation(
            polygon=merged_utm_polygon,
            label=self.label,
            attributes=self.attributes.copy(),  # pylint: disable=no-member
            camera_center=self.camera_center,  # Keep camera center from self
            start_arc_length=self.start_arc_length,  # Keep arc length from self
            end_arc_length=self.end_arc_length
        )

    def merge_with_condition(
        self,
        other: "UTMAnnotation",
        classification_strategy: Literal["force", "label", "attribute"] = "attribute",
        spatial_strategy: Literal["force", "distance", "iou"] = "iou",
        distance_threshold: float = 1.0,
        iou_threshold: float = 0.01,
    ) -> Optional["UTMAnnotation"]:
        """
        Merge this annotation with another annotation based on specified conditions.

        Checks if the annotations meet the specified classification and spatial
        criteria, then performs the merge using merge_with() if conditions are met.

        Args:
            other: Another UTMAnnotation to merge with.
            classification_strategy: Strategy for handling classification compatibility:
                - "force": Ignore label/attribute differences, always merge
                - "label": Require same label only
                - "attribute": Require same label and attributes (default)
            spatial_strategy: Strategy for spatial merging criteria:
                - "force": Always merge regardless of spatial relationship
                - "distance": Merge if distance <= distance_threshold
                - "iou": Merge if IoU >= iou_threshold (default)
            distance_threshold: Maximum distance in meters for distance-based merging (default: 1.0)
            iou_threshold: Minimum IoU for IoU-based merging (default: 0.01)

        Returns:
            Optional[UTMAnnotation]: A new annotation with merged polygon geometry if
                                   conditions are met, None otherwise.

        Example:
            >>> # Force merge with distance threshold
            >>> merged1 = ann1.merge_with_condition(ann2, classification_strategy="force",
            ...                                    spatial_strategy="distance", distance_threshold=5.0)
            >>> if merged1:
            ...     print("Annotations were merged")
            >>>
            >>> # Merge if same label and IoU > 0.5
            >>> merged2 = ann1.merge_with_condition(ann2, classification_strategy="label",
            ...                                    spatial_strategy="iou", iou_threshold=0.5)
            >>> if merged2 is None:
            ...     print("Conditions not met, no merge performed")
        """
        # Check if in different UTM zones
        if (
            self.polygon.zone_number != other.polygon.zone_number  # pylint: disable=no-member
            or self.polygon.zone_letter != other.polygon.zone_letter
        ):  # pylint: disable=no-member
            return None

        # Check classification compatibility
        if classification_strategy == "attribute":
            if not self.has_same_label_and_attributes(other):
                return None
        elif classification_strategy == "label":
            if self.label != other.label:
                return None
        # classification_strategy == "force" requires no checks

        # Check spatial criteria
        if spatial_strategy == "iou":
            iou = self.polygon.intersection_over_union(other.polygon)  # pylint: disable=no-member
            if iou < iou_threshold:
                return None
        elif spatial_strategy == "distance":
            distance = self.polygon.distance_to(other.polygon)  # pylint: disable=no-member
            if distance > distance_threshold:
                return None
        # spatial_strategy == "force" requires no checks

        # All conditions met, perform the merge
        return self.merge_with(other)

    def area_square_meters(self) -> float:
        """
        Get the area of the annotation polygon in square meters.

        Returns:
            float: The area of the polygon in square meters.

        Example:
            >>> annotation = UTMAnnotation(...)
            >>> area = annotation.area_square_meters()
            >>> print(f"Annotation area: {area:.2f} m²")
        """
        return self.polygon.area_square_meters()  # pylint: disable=no-member

    def get_center(self) -> UTMPoint:
        """
        Get the center point (centroid) of the annotation's polygon.

        This is a shortcut method that delegates to the polygon's get_center method.

        Returns:
            UTMPoint: The center point of the polygon in the same UTM zone.

        Example:
            >>> annotation = UTMAnnotation(...)
            >>> center = annotation.get_center()
            >>> print(f"Center: {center.easting}E, {center.northing}N")
        """
        return self.polygon.get_center()  # pylint: disable=no-member

    def to_dict(self) -> dict:
        """
        Convert the UTMAnnotation to a dictionary.

        Returns:
            Dict: Dictionary representation of the annotation.

        Example:
            >>> annotation = UTMAnnotation(...)
            >>> data = annotation.to_dict()
            >>> reconstructed = UTMAnnotation.from_dict(data)
        """
        result = {
            "polygon": self.polygon.to_dict(),  # pylint: disable=no-member
            "label": self.label,
            "attributes": [{"key": attr.key, "value": attr.value} for attr in self.attributes],
        }
        if self.camera_center is not None:
            result["camera_center"] = self.camera_center.to_dict()  # pylint: disable=no-member
        if self.start_arc_length is not None:
            result["start_arc_length"] = self.start_arc_length
        if self.end_arc_length is not None:
            result["end_arc_length"] = self.end_arc_length
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "UTMAnnotation":
        """
        Create a UTMAnnotation instance from a dictionary.

        Args:
            data: Dictionary containing polygon, label, and attributes data.

        Returns:
            UTMAnnotation: A new instance created from the dictionary data.

        Raises:
            ValueError: If required keys are missing or data is invalid.

        Example:
            >>> data = {
            ...     "polygon": {...},
            ...     "label": "vehicle",
            ...     "attributes": [{"key": "color", "value": "red"}]
            ... }
            >>> annotation = UTMAnnotation.from_dict(data)
        """
        try:
            # Reconstruct UTMPolygon
            polygon_data = data["polygon"]
            
            # Check if we need zone normalization
            if "zone_normalization_data" in polygon_data:
                # Polygon needs zone normalization
                norm_data = polygon_data["zone_normalization_data"]
                polygon = UTMPolygon.from_points_with_zone_normalization(
                    points=norm_data["points"],
                    zone_numbers=norm_data["zone_numbers"],
                    zone_letters=norm_data["zone_letters"],
                    simplify_tolerance=polygon_data.get("simplify_tolerance", 0.1)
                )
            else:
                # Normal polygon creation
                polygon = UTMPolygon.from_dict(polygon_data)

            # Reconstruct attributes
            attributes = [AnnotationAttribute(key=attr["key"], value=attr["value"]) for attr in data.get("attributes", [])]

            # Reconstruct camera center if present
            camera_center = None
            if "camera_center" in data:
                camera_center = UTMPoint.from_dict(data["camera_center"])

            return cls(
                polygon=polygon, 
                label=data["label"], 
                attributes=attributes, 
                camera_center=camera_center,
                start_arc_length=data.get("start_arc_length"),
                end_arc_length=data.get("end_arc_length")
            )
        except KeyError as e:
            raise ValueError(f"Missing required key in dictionary: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to create UTMAnnotation from dictionary: {e}") from e

    def get_oriented_bounding_box(self) -> Tuple[UTMPolygon, float, float, float]:
        """
        Calculate the oriented bounding box of the annotation.

        Returns the minimum area rectangle that contains the polygon,
        along with its orientation and dimensions.

        Returns:
            Tuple containing:
            - UTMPolygon: The oriented bounding box as a polygon
            - float: Angle of rotation relative to north (degrees)
            - float: Length of the bounding box (meters)
            - float: Width of the bounding box (meters)

        Example:
            >>> annotation = UTMAnnotation(...)
            >>> bbox, angle, length, width = annotation.get_oriented_bounding_box()
            >>> print(f"Angle: {angle:.1f}°, Size: {length:.1f}m x {width:.1f}m")
        """
        from shapely.geometry import box, Polygon as ShapelyPolygon
        from shapely import minimum_rotated_rectangle
        
        # Get the minimum rotated rectangle
        min_rect = minimum_rotated_rectangle(self.polygon.polygon)  # pylint: disable=no-member
        
        # Ensure it's a Polygon
        if not isinstance(min_rect, ShapelyPolygon):
            raise ValueError(f"Minimum rotated rectangle is not a Polygon: {type(min_rect)}")
        
        # Get the coordinates of the rectangle
        coords = list(min_rect.exterior.coords)[:-1]  # Remove duplicate last point
        
        # Calculate the angle of the rectangle
        # Take the first edge
        dx = coords[1][0] - coords[0][0]
        dy = coords[1][1] - coords[0][1]
        
        # Calculate angle relative to east (0°), then convert to north (90°)
        angle_east = np.degrees(np.arctan2(dy, dx))
        angle_north = (90 - angle_east) % 360
        
        # Calculate dimensions
        edge1_length = np.sqrt(dx**2 + dy**2)
        dx2 = coords[2][0] - coords[1][0]
        dy2 = coords[2][1] - coords[1][1]
        edge2_length = np.sqrt(dx2**2 + dy2**2)
        
        # Length is the longer edge, width is the shorter
        length = max(edge1_length, edge2_length)
        width = min(edge1_length, edge2_length)
        
        # Create UTMPolygon for the bounding box
        bbox_polygon = UTMPolygon(
            polygon=min_rect,
            zone_number=self.polygon.zone_number,  # pylint: disable=no-member
            zone_letter=self.polygon.zone_letter,  # pylint: disable=no-member
            simplify_tolerance=0.0  # No simplification for bounding box
        )
        
        return (bbox_polygon, angle_north, length, width)

    def normalize_zone(self) -> "UTMAnnotation":
        """
        Normalize the annotation to ensure all points are in the same UTM zone.

        If the polygon has points in different zones, it finds the most common
        zone and converts all points to that zone.

        Returns:
            UTMAnnotation: New annotation with normalized zone.
        """
        # For now, we assume the polygon is already in a single zone
        # This could be extended to handle multi-zone polygons
        return self
