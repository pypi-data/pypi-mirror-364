"""
UTM Polygon schema for geographic polygon operations.
"""

from typing import Optional, Tuple, List
from pydantic import BaseModel, Field, root_validator
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
from collections import Counter

from lcvtoolbox.core.schemas.utm.point import UTMPoint


class UTMPolygon(BaseModel):
    """
    UTM polygon with zone information for geographic operations.

    Contains the polygon geometry and UTM zone information required
    for proper geographic projection and visualization.
    """

    polygon: Polygon = Field(..., description="Shapely Polygon in UTM coordinates")
    zone_number: int = Field(..., ge=1, le=60, description="UTM zone number (1-60)")
    zone_letter: str = Field(..., pattern="^[C-X]$", description="UTM zone letter (C-X, excluding I and O)")
    simplify_tolerance: float = Field(0.1, description="Simplification tolerance in meters (default: 0.1m = 10cm)")
    
    # Cache for expensive computations
    _cached_area: Optional[float] = None
    _cached_centroid: Optional[UTMPoint] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
        json_schema_extra = {
            "example": {
                "polygon": "POLYGON ((448262.0 5411932.0, ...))",
                "zone_number": 31,
                "zone_letter": "U",
                "simplify_tolerance": 0.1,
            }
        }

    @root_validator(pre=True)
    def simplify_polygon_on_init(cls, values):
        """Simplify polygon on initialization if tolerance is set."""
        polygon = values.get('polygon')
        tolerance = values.get('simplify_tolerance', 0.1)
        
        if polygon and tolerance > 0:
            if isinstance(polygon, Polygon):
                # Simplify the polygon
                values['polygon'] = polygon.simplify(tolerance, preserve_topology=True)
        
        return values

    def __setattr__(self, name, value):
        """Clear cache when polygon is modified."""
        if name == 'polygon':
            self._cached_area = None
            self._cached_centroid = None
        super().__setattr__(name, value)

    @classmethod
    def from_points_with_zone_normalization(cls, points: List[Tuple[float, float]], 
                                           zone_numbers: List[int], 
                                           zone_letters: List[str],
                                           simplify_tolerance: float = 0.1) -> "UTMPolygon":
        """
        Create a UTMPolygon from points that may be in different zones.
        
        Finds the most common zone and converts all points to that zone.
        
        Args:
            points: List of (easting, northing) tuples.
            zone_numbers: List of zone numbers corresponding to each point.
            zone_letters: List of zone letters corresponding to each point.
            simplify_tolerance: Tolerance for polygon simplification in meters.
            
        Returns:
            UTMPolygon: Polygon with all points in the most common zone.
            
        Example:
            >>> points = [(448262, 5411932), (448300, 5411970)]
            >>> zones_num = [31, 32]
            >>> zones_letter = ['U', 'U']
            >>> polygon = UTMPolygon.from_points_with_zone_normalization(points, zones_num, zones_letter)
        """
        if not points or not zone_numbers or not zone_letters:
            raise ValueError("Points, zone_numbers, and zone_letters must not be empty")
            
        if not (len(points) == len(zone_numbers) == len(zone_letters)):
            raise ValueError("All input lists must have the same length")
        
        # Find most common zone
        zone_pairs = list(zip(zone_numbers, zone_letters))
        zone_counter = Counter(zone_pairs)
        target_zone_num, target_zone_letter = zone_counter.most_common(1)[0][0]
        
        # Convert all points to target zone
        normalized_points = []
        for i, (easting, northing) in enumerate(points):
            zone_num = zone_numbers[i]
            zone_letter = zone_letters[i]
            
            if zone_num == target_zone_num and zone_letter == target_zone_letter:
                # Already in target zone
                normalized_points.append((easting, northing))
            else:
                # Convert to target zone
                point = UTMPoint(
                    easting=easting,
                    northing=northing,
                    zone_number=zone_num,
                    zone_letter=zone_letter,
                    height=None,
                    forced_zone=False
                )
                converted = point.change_zone(target_zone_num, target_zone_letter)
                normalized_points.append((converted.easting, converted.northing))
        
        # Create polygon
        polygon = Polygon(normalized_points)
        
        return cls(
            polygon=polygon,
            zone_number=target_zone_num,
            zone_letter=target_zone_letter,
            simplify_tolerance=simplify_tolerance
        )

    def optimize(self, tolerance: Optional[float] = None) -> "UTMPolygon":
        """
        Optimize the polygon by reducing the number of points.
        
        Uses Douglas-Peucker algorithm to simplify the polygon while
        preserving topology.
        
        Args:
            tolerance: Simplification tolerance in meters. If None, uses
                      the instance's simplify_tolerance (default: 0.1m).
                      
        Returns:
            UTMPolygon: New optimized polygon.
            
        Example:
            >>> polygon = UTMPolygon(...)
            >>> optimized = polygon.optimize(0.5)  # 50cm tolerance
            >>> print(f"Points reduced from {len(polygon.polygon.exterior.coords)} to {len(optimized.polygon.exterior.coords)}")
        """
        if tolerance is None:
            tolerance = self.simplify_tolerance
            
        simplified = self.polygon.simplify(tolerance, preserve_topology=True)  # pylint: disable=no-member
        
        # Ensure we still have a valid Polygon
        if not isinstance(simplified, Polygon):
            raise ValueError(f"Simplification resulted in invalid geometry type: {type(simplified)}")
        
        return UTMPolygon(
            polygon=simplified,
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            simplify_tolerance=tolerance
        )

    def normalize_to_zone(self, target_zone_number: int, target_zone_letter: str) -> "UTMPolygon":
        """
        Convert the polygon to a different UTM zone.
        
        Args:
            target_zone_number: Target zone number.
            target_zone_letter: Target zone letter.
            
        Returns:
            UTMPolygon: New polygon in the target zone.
        """
        # Get all exterior coordinates
        exterior_coords = list(self.polygon.exterior.coords)  # pylint: disable=no-member
        
        # Convert each point
        converted_exterior = []
        for easting, northing in exterior_coords:
            point = UTMPoint(
                easting=easting,
                northing=northing,
                zone_number=self.zone_number,
                zone_letter=self.zone_letter,
                height=None,
                forced_zone=False
            )
            converted = point.change_zone(target_zone_number, target_zone_letter)
            converted_exterior.append((converted.easting, converted.northing))
        
        # Handle interior rings (holes)
        converted_interiors = []
        if self.polygon.interiors:  # pylint: disable=no-member
            for interior in self.polygon.interiors:  # pylint: disable=no-member
                converted_interior = []
                for easting, northing in interior.coords:
                    point = UTMPoint(
                        easting=easting,
                        northing=northing,
                        zone_number=self.zone_number,
                        zone_letter=self.zone_letter,
                        height=None,
                        forced_zone=False
                    )
                    converted = point.change_zone(target_zone_number, target_zone_letter)
                    converted_interior.append((converted.easting, converted.northing))
                converted_interiors.append(converted_interior)
        
        # Create new polygon
        new_polygon = Polygon(converted_exterior, converted_interiors)
        
        return UTMPolygon(
            polygon=new_polygon,
            zone_number=target_zone_number,
            zone_letter=target_zone_letter,
            simplify_tolerance=self.simplify_tolerance
        )

    def to_dict(self) -> dict:
        """
        Convert the UTMPolygon to a dictionary.

        This is useful for JSON serialization or further processing.
        The polygon is stored as a list of coordinate tuples for better compatibility.
        """
        # Extract exterior coordinates as list of tuples
        exterior_coords = list(self.polygon.exterior.coords)  # pylint: disable=no-member

        # Handle interior rings (holes) if they exist
        interior_coords = []
        if self.polygon.interiors:  # pylint: disable=no-member
            interior_coords = [list(interior.coords) for interior in self.polygon.interiors]  # pylint: disable=no-member

        polygon_data = {"exterior": exterior_coords, "interiors": interior_coords}

        return {
            "polygon": polygon_data,
            "zone_number": self.zone_number,
            "zone_letter": self.zone_letter,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UTMPolygon":
        """
        Create a UTMPolygon instance from a dictionary.

        This method is the inverse of to_dict() and can be used to reconstruct
        a UTMPolygon from a dictionary containing polygon coordinate data.

        Args:
            data: Dictionary containing 'polygon' (coordinate data), 'zone_number',
                  and 'zone_letter' keys. The polygon should have 'exterior'
                  (list of coordinate tuples) and optionally 'interiors'
                  (list of lists of coordinate tuples).

        Returns:
            UTMPolygon: A new instance created from the dictionary data.

        Raises:
            ValueError: If the polygon data is invalid or required keys are missing.
            TypeError: If the polygon cannot be created from the coordinate data.

        Example:
            >>> data = {
            ...     "polygon": {
            ...         "exterior": [(448262.0, 5411932.0), (448300.0, 5411932.0),
            ...                      (448300.0, 5411970.0), (448262.0, 5411970.0),
            ...                      (448262.0, 5411932.0)],
            ...         "interiors": []
            ...     },
            ...     "zone_number": 31,
            ...     "zone_letter": "U"
            ... }
            >>> result = UTMPolygon.from_dict(data)
        """
        try:
            polygon_data = data["polygon"]

            # Extract exterior coordinates
            exterior_coords = polygon_data["exterior"]
            if not exterior_coords:
                raise ValueError("Polygon exterior coordinates cannot be empty")

            # Extract interior coordinates (holes) if they exist
            interior_coords = polygon_data.get("interiors", [])

            # Create Shapely Polygon
            polygon = Polygon(exterior_coords, interior_coords) if interior_coords else Polygon(exterior_coords)

            # Validate that we got a valid polygon
            if not polygon.is_valid:
                raise ValueError(f"Created polygon is not valid: {polygon}")

            return cls(
                polygon=polygon, 
                zone_number=data["zone_number"], 
                zone_letter=data["zone_letter"],
                simplify_tolerance=data.get("simplify_tolerance", 0.1)
            )
        except KeyError as e:
            raise ValueError(f"Missing required key in dictionary: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to create polygon from coordinates: {e}") from e

    def intersects(self, other: "UTMPolygon") -> bool:
        """
        Check if this polygon intersects with another UTMPolygon.

        Args:
            other: Another UTMPolygon to check intersection with.

        Returns:
            bool: True if the polygons intersect, False otherwise.

        Raises:
            ValueError: If the polygons are in different UTM zones.

        Example:
            >>> polygon1 = UTMPolygon(...)
            >>> polygon2 = UTMPolygon(...)
            >>> if polygon1.intersects(polygon2):
            ...     print("Polygons intersect!")
        """
        self._validate_same_zone(other)
        return self.polygon.intersects(other.polygon)  # pylint: disable=no-member

    def intersection_area(self, other: "UTMPolygon") -> float:
        """
        Calculate the area of intersection between this polygon and another.

        Args:
            other: Another UTMPolygon to calculate intersection area with.

        Returns:
            float: The area of intersection in square meters. Returns 0.0 if 
                   polygons don't intersect.

        Raises:
            ValueError: If the polygons are in different UTM zones.

        Example:
            >>> polygon1 = UTMPolygon(...)
            >>> polygon2 = UTMPolygon(...)
            >>> area = polygon1.intersection_area(polygon2)
            >>> print(f"Intersection area: {area} square meters")
        """
        self._validate_same_zone(other)
        if not self.polygon.intersects(other.polygon):  # pylint: disable=no-member
            return 0.0
        
        intersection = self.polygon.intersection(other.polygon)  # pylint: disable=no-member
        return float(intersection.area)

    def intersection_over_union(self, other: "UTMPolygon") -> float:
        """
        Calculate the Intersection over Union (IoU) between this polygon and another.

        IoU is defined as the area of intersection divided by the area of union.
        It's a common metric for measuring overlap between two polygons, with
        values ranging from 0 (no overlap) to 1 (complete overlap).

        Args:
            other: Another UTMPolygon to calculate IoU with.

        Returns:
            float: The IoU value between 0.0 and 1.0. Returns 0.0 if polygons
                   don't intersect.

        Raises:
            ValueError: If the polygons are in different UTM zones.

        Example:
            >>> polygon1 = UTMPolygon(...)
            >>> polygon2 = UTMPolygon(...)
            >>> iou = polygon1.intersection_over_union(polygon2)
            >>> print(f"IoU: {iou:.3f}")
        """
        self._validate_same_zone(other)
        
        if not self.polygon.intersects(other.polygon):  # pylint: disable=no-member
            return 0.0
        
        intersection = self.polygon.intersection(other.polygon)  # pylint: disable=no-member
        union = self.polygon.union(other.polygon)  # pylint: disable=no-member
        
        intersection_area = float(intersection.area)
        union_area = float(union.area)
        
        # Handle edge case where union area is zero (shouldn't happen with valid polygons)
        if union_area == 0.0:
            return 0.0
        
        return intersection_area / union_area

    def area_square_meters(self) -> float:
        """
        Get the area of the polygon in square meters.

        Since UTM coordinates are in meters, the polygon area is directly
        in square meters without any conversion needed. The result is cached
        for performance.

        Returns:
            float: The area of the polygon in square meters.

        Example:
            >>> polygon = UTMPolygon(...)
            >>> area = polygon.area_square_meters()
            >>> print(f"Polygon area: {area:.2f} m²")
        """
        if self._cached_area is None:
            self._cached_area = float(self.polygon.area)  # pylint: disable=no-member
        return self._cached_area

    def distance_to(self, other: "UTMPolygon") -> float:
        """
        Calculate the minimum distance between this polygon and another.

        The distance is calculated as the minimum distance between any points
        on the two polygons. If the polygons intersect, the distance is 0.

        Args:
            other: Another UTMPolygon to calculate distance to.

        Returns:
            float: The minimum distance in meters.

        Raises:
            ValueError: If the polygons are in different UTM zones.

        Example:
            >>> polygon1 = UTMPolygon(...)
            >>> polygon2 = UTMPolygon(...)
            >>> distance = polygon1.distance_to(polygon2)
            >>> print(f"Distance: {distance:.2f} meters")
        """
        self._validate_same_zone(other)
        return float(self.polygon.distance(other.polygon))  # pylint: disable=no-member

    def get_center(self) -> UTMPoint:
        """
        Get the center point (centroid) of the polygon.

        Uses Shapely's built-in centroid calculation which is economical to compute.
        The centroid is the geometric center of the polygon. The result is cached
        for performance.

        Returns:
            UTMPoint: The center point of the polygon in the same UTM zone.

        Example:
            >>> polygon = UTMPolygon(...)
            >>> center = polygon.get_center()
            >>> print(f"Center: {center.easting}E, {center.northing}N")
        """
        if self._cached_centroid is None:
            centroid = self.polygon.centroid  # pylint: disable=no-member
            self._cached_centroid = UTMPoint(
                easting=float(centroid.x),
                northing=float(centroid.y),
                zone_number=self.zone_number,
                zone_letter=self.zone_letter,
                height=None,  # 2D polygon centroid has no height
                forced_zone=False
            )
        return self._cached_centroid

    def merge_with(self, other: "UTMPolygon") -> "UTMPolygon":
        """
        Merge this UTM polygon with another UTM polygon using geometric union.

        Creates a new UTMPolygon containing the union of both polygon geometries.
        Both polygons must be in the same UTM zone.

        Args:
            other: Another UTMPolygon to merge with.

        Returns:
            UTMPolygon: A new UTMPolygon containing the merged geometry.

        Raises:
            ValueError: If the polygons are in different UTM zones or if the
                       union result is not a valid polygon.

        Example:
            >>> polygon1 = UTMPolygon(...)
            >>> polygon2 = UTMPolygon(...)
            >>> merged = polygon1.merge_with(polygon2)
            >>> print(f"Merged area: {merged.area_square_meters():.2f} m²")
        """
        self._validate_same_zone(other)
        
        # Create union of both polygons
        from shapely.ops import unary_union
        union_result = unary_union([self.polygon, other.polygon])  # pylint: disable=no-member
        
        # Ensure the result is a Polygon (unary_union can return different geometry types)
        if not isinstance(union_result, Polygon):
            # If it's a MultiPolygon, take the largest polygon
            from shapely.geometry import MultiPolygon
            if isinstance(union_result, MultiPolygon):
                union_polygon = max(union_result.geoms, key=lambda p: p.area)
            else:
                raise ValueError(f"Union operation resulted in unsupported geometry type: {type(union_result)}")
        else:
            union_polygon = union_result
        
        # Create new UTMPolygon with merged geometry
        return UTMPolygon(
            polygon=union_polygon,
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            simplify_tolerance=self.simplify_tolerance
        )

    def _validate_same_zone(self, other: "UTMPolygon") -> None:
        """
        Validate that two UTMPolygon instances are in the same UTM zone.

        Args:
            other: Another UTMPolygon to validate against.

        Raises:
            ValueError: If the polygons are in different UTM zones.
        """
        if self.zone_number != other.zone_number or self.zone_letter != other.zone_letter:
            raise ValueError(
                f"Cannot compare polygons in different UTM zones: "
                f"{self.zone_number}{self.zone_letter} vs {other.zone_number}{other.zone_letter}"
            )
