"""
UTM Point schema for geographic point operations.
"""

from typing import Dict, Tuple, Optional
from pydantic import BaseModel, Field
import math
import pyproj


class UTMPoint(BaseModel):
    """
    UTM point with zone information for geographic operations.

    Contains the point coordinates and UTM zone information required
    for proper geographic projection and visualization.
    """

    easting: float = Field(..., description="UTM easting coordinate in meters")
    northing: float = Field(..., description="UTM northing coordinate in meters")
    zone_number: int = Field(..., ge=1, le=60, description="UTM zone number (1-60)")
    zone_letter: str = Field(..., pattern="^[C-X]$", description="UTM zone letter (C-X, excluding I and O)")
    height: Optional[float] = Field(None, description="Height/elevation in meters (optional)")
    forced_zone: bool = Field(False, description="Flag indicating if the point was forced into a non-recommended UTM zone")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "easting": 448262.0,
                "northing": 5411932.0,
                "zone_number": 31,
                "zone_letter": "U",
                "height": 245.5,
                "forced_zone": False,
            }
        }

    @property
    def x(self) -> float:
        """
        Alias for easting coordinate.

        Returns:
            float: The easting coordinate value.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U')
            >>> print(point.x)  # Same as point.easting
            448262.0
        """
        return self.easting

    @property
    def y(self) -> float:
        """
        Alias for northing coordinate.

        Returns:
            float: The northing coordinate value.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U')
            >>> print(point.y)  # Same as point.northing
            5411932.0
        """
        return self.northing

    @property
    def z(self) -> Optional[float]:
        """
        Alias for height/elevation.

        Returns:
            Optional[float]: The height value if set, None otherwise.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U', height=245.5)
            >>> print(point.z)  # Same as point.height
            245.5
        """
        return self.height

    def to_dict(self) -> Dict:
        """
        Convert the UTMPoint to a dictionary.

        This is useful for JSON serialization or further processing.

        Returns:
            Dict: Dictionary representation of the UTM point.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U', height=245.5)
            >>> data = point.to_dict()
            >>> print(data)
            {'easting': 448262.0, 'northing': 5411932.0, 'zone_number': 31, 'zone_letter': 'U', 'height': 245.5}
        """
        data = {
            "easting": self.easting,
            "northing": self.northing,
            "zone_number": self.zone_number,
            "zone_letter": self.zone_letter,
            "forced_zone": self.forced_zone,
        }
        if self.height is not None:
            data["height"] = self.height
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "UTMPoint":
        """
        Create a UTMPoint instance from a dictionary.

        This method is the inverse of to_dict() and can be used to reconstruct
        a UTMPoint from a dictionary containing coordinate data.

        Args:
            data: Dictionary containing 'easting', 'northing', 'zone_number',
                  'zone_letter' keys, and optionally 'height'.

        Returns:
            UTMPoint: A new instance created from the dictionary data.

        Raises:
            ValueError: If required keys are missing or data is invalid.

        Example:
            >>> data = {
            ...     "easting": 448262.0,
            ...     "northing": 5411932.0,
            ...     "zone_number": 31,
            ...     "zone_letter": "U",
            ...     "height": 245.5
            ... }
            >>> point = UTMPoint.from_dict(data)
        """
        try:
            return cls(
                easting=data["easting"],
                northing=data["northing"],
                zone_number=data["zone_number"],
                zone_letter=data["zone_letter"],
                height=data.get("height"),
                forced_zone=data.get("forced_zone", False)
            )
        except KeyError as e:
            raise ValueError(f"Missing required key in dictionary: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to create UTMPoint from dictionary: {e}") from e

    def distance_to(self, other: "UTMPoint", include_height: bool = False) -> float:
        """
        Calculate the Euclidean distance to another UTM point.

        Both points must be in the same UTM zone for accurate distance calculation.

        Args:
            other: Another UTMPoint to calculate distance to.
            include_height: If True and both points have height values, calculate 3D distance.

        Returns:
            float: The distance in meters.

        Raises:
            ValueError: If the points are in different UTM zones.

        Example:
            >>> point1 = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U', height=100.0)
            >>> point2 = UTMPoint(easting=448300.0, northing=5411970.0, zone_number=31, zone_letter='U', height=150.0)
            >>> distance_2d = point1.distance_to(point2)
            >>> distance_3d = point1.distance_to(point2, include_height=True)
            >>> print(f"2D Distance: {distance_2d:.2f} meters")
            >>> print(f"3D Distance: {distance_3d:.2f} meters")
        """
        self._validate_same_zone(other)
        
        delta_easting = self.easting - other.easting
        delta_northing = self.northing - other.northing
        
        if include_height and self.height is not None and other.height is not None:
            delta_height = self.height - other.height
            return math.sqrt(delta_easting**2 + delta_northing**2 + delta_height**2)
        else:
            return math.sqrt(delta_easting**2 + delta_northing**2)

    def midpoint_to(self, other: "UTMPoint") -> "UTMPoint":
        """
        Calculate the midpoint between this point and another UTM point.

        Both points must be in the same UTM zone. If both points have height values,
        the midpoint will include the average height.

        Args:
            other: Another UTMPoint to calculate midpoint with.

        Returns:
            UTMPoint: A new UTMPoint representing the midpoint.

        Raises:
            ValueError: If the points are in different UTM zones.

        Example:
            >>> point1 = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U', height=100.0)
            >>> point2 = UTMPoint(easting=448300.0, northing=5411970.0, zone_number=31, zone_letter='U', height=200.0)
            >>> midpoint = point1.midpoint_to(point2)
            >>> print(f"Midpoint: ({midpoint.x}, {midpoint.y}, {midpoint.z})")
        """
        self._validate_same_zone(other)
        
        mid_easting = (self.easting + other.easting) / 2.0
        mid_northing = (self.northing + other.northing) / 2.0
        
        mid_height = None
        if self.height is not None and other.height is not None:
            mid_height = (self.height + other.height) / 2.0
        
        return UTMPoint(
            easting=mid_easting,
            northing=mid_northing,
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            height=mid_height,
            forced_zone=False
        )

    def translate(self, delta_easting: float, delta_northing: float, delta_height: float = 0.0) -> "UTMPoint":
        """
        Create a new UTMPoint translated by the given offsets.

        Args:
            delta_easting: Offset in easting direction (meters).
            delta_northing: Offset in northing direction (meters).
            delta_height: Offset in height direction (meters). Only applied if the point has a height value.

        Returns:
            UTMPoint: A new UTMPoint with translated coordinates.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U', height=100.0)
            >>> translated = point.translate(100.0, 50.0, 10.0)
            >>> print(f"New coordinates: ({translated.x}, {translated.y}, {translated.z})")
        """
        new_height = None
        if self.height is not None:
            new_height = self.height + delta_height
            
        return UTMPoint(
            easting=self.easting + delta_easting,
            northing=self.northing + delta_northing,
            zone_number=self.zone_number,
            zone_letter=self.zone_letter,
            height=new_height,
            forced_zone=self.forced_zone
        )

    def to_tuple(self) -> Tuple[float, float]:
        """
        Convert the UTM point to a coordinate tuple.

        Returns:
            Tuple[float, float]: A tuple of (easting, northing) coordinates.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U')
            >>> coords = point.to_tuple()
            >>> print(coords)  # (448262.0, 5411932.0)
        """
        return (self.easting, self.northing)

    def __str__(self) -> str:
        """
        String representation of the UTM point.

        Returns:
            str: Human-readable string representation.
        """
        if self.height is not None:
            return f"UTMPoint({self.easting:.1f}E, {self.northing:.1f}N, {self.height:.1f}H, {self.zone_number}{self.zone_letter})"
        else:
            return f"UTMPoint({self.easting:.1f}E, {self.northing:.1f}N, {self.zone_number}{self.zone_letter})"

    def __repr__(self) -> str:
        """
        Detailed string representation of the UTM point.

        Returns:
            str: Detailed string representation for debugging.
        """
        if self.height is not None:
            return (f"UTMPoint(easting={self.easting}, northing={self.northing}, "
                    f"zone_number={self.zone_number}, zone_letter='{self.zone_letter}', "
                    f"height={self.height})")
        else:
            return (f"UTMPoint(easting={self.easting}, northing={self.northing}, "
                    f"zone_number={self.zone_number}, zone_letter='{self.zone_letter}')")

    def _validate_same_zone(self, other: "UTMPoint") -> None:
        """
        Validate that two UTMPoint instances are in the same UTM zone.

        Args:
            other: Another UTMPoint to validate against.

        Raises:
            ValueError: If the points are in different UTM zones.
        """
        if self.zone_number != other.zone_number or self.zone_letter != other.zone_letter:
            raise ValueError(
                f"Cannot operate on points in different UTM zones: "
                f"{self.zone_number}{self.zone_letter} vs {other.zone_number}{other.zone_letter}"
            )

    def to_lat_lon(self) -> Tuple[float, float]:
        """
        Convert UTM coordinates to latitude and longitude.

        Returns:
            Tuple[float, float]: (latitude, longitude) in decimal degrees.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U')
            >>> lat, lon = point.to_lat_lon()
            >>> print(f"Lat: {lat:.6f}, Lon: {lon:.6f}")
        """
        # Determine if northern hemisphere
        northern = self.zone_letter >= 'N'
        
        # Create transformer
        utm_crs = pyproj.CRS(f"+proj=utm +zone={self.zone_number} +{'north' if northern else 'south'} +datum=WGS84")
        wgs84_crs = pyproj.CRS("EPSG:4326")
        transformer = pyproj.Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
        
        # Transform coordinates
        lon, lat = transformer.transform(self.easting, self.northing)
        return (lat, lon)

    @staticmethod
    def get_utm_zone_from_lat_lon(lat: float, lon: float) -> Tuple[int, str]:
        """
        Determine the appropriate UTM zone for given latitude and longitude.

        Args:
            lat: Latitude in decimal degrees.
            lon: Longitude in decimal degrees.

        Returns:
            Tuple[int, str]: (zone_number, zone_letter).

        Example:
            >>> zone_num, zone_letter = UTMPoint.get_utm_zone_from_lat_lon(48.8566, 2.3522)
            >>> print(f"Zone: {zone_num}{zone_letter}")
        """
        # Calculate zone number
        zone_number = int((lon + 180) / 6) + 1
        
        # Special cases for Norway
        if lat >= 56.0 and lat < 64.0 and lon >= 3.0 and lon < 12.0:
            zone_number = 32
        
        # Special cases for Svalbard
        if lat >= 72.0 and lat < 84.0:
            if lon >= 0.0 and lon < 9.0:
                zone_number = 31
            elif lon >= 9.0 and lon < 21.0:
                zone_number = 33
            elif lon >= 21.0 and lon < 33.0:
                zone_number = 35
            elif lon >= 33.0 and lon < 42.0:
                zone_number = 37
        
        # Determine zone letter
        if lat >= -80 and lat <= 84:
            letters = 'CDEFGHJKLMNPQRSTUVWX'
            zone_letter = letters[int((lat + 80) / 8)]
        else:
            raise ValueError(f"Latitude {lat} is out of UTM range")
        
        return (zone_number, zone_letter)

    def change_zone(self, target_zone_number: int, target_zone_letter: str) -> "UTMPoint":
        """
        Change the UTM zone of the point, recalculating coordinates.

        Creates a new point with coordinates transformed to the target zone.
        The forced_zone flag will be set to True if the target zone is not
        the recommended zone for this location.

        Args:
            target_zone_number: Target UTM zone number (1-60).
            target_zone_letter: Target UTM zone letter (C-X, excluding I and O).

        Returns:
            UTMPoint: New point in the target UTM zone.

        Example:
            >>> point = UTMPoint(easting=448262.0, northing=5411932.0, zone_number=31, zone_letter='U')
            >>> point_zone32 = point.change_zone(32, 'U')
            >>> print(f"New coordinates: {point_zone32.easting:.1f}E, {point_zone32.northing:.1f}N")
        """
        # Convert to lat/lon
        lat, lon = self.to_lat_lon()
        
        # Determine if target is northern hemisphere
        target_northern = target_zone_letter >= 'N'
        
        # Create transformer to target zone
        target_utm = pyproj.CRS(f"+proj=utm +zone={target_zone_number} +{'north' if target_northern else 'south'} +datum=WGS84")
        wgs84_crs = pyproj.CRS("EPSG:4326")
        transformer = pyproj.Transformer.from_crs(wgs84_crs, target_utm, always_xy=True)
        
        # Transform to new zone
        new_easting, new_northing = transformer.transform(lon, lat)
        
        # Check if this is the recommended zone
        recommended_zone_num, recommended_zone_letter = self.get_utm_zone_from_lat_lon(lat, lon)
        forced = (target_zone_number != recommended_zone_num or target_zone_letter != recommended_zone_letter)
        
        return UTMPoint(
            easting=new_easting,
            northing=new_northing,
            zone_number=target_zone_number,
            zone_letter=target_zone_letter,
            height=self.height,
            forced_zone=forced
        )

    def restore_recommended_zone(self) -> "UTMPoint":
        """
        Restore the point to its recommended UTM zone if it was forced.

        If the point is already in the recommended zone (forced_zone=False),
        returns a copy of the current point.

        Returns:
            UTMPoint: Point in the recommended UTM zone.

        Example:
            >>> # Point forced into zone 32
            >>> point = UTMPoint(easting=250000, northing=5411932, zone_number=32, zone_letter='U', forced_zone=True)
            >>> restored = point.restore_recommended_zone()
            >>> print(f"Restored to zone: {restored.zone_number}{restored.zone_letter}")
        """
        if not self.forced_zone:
            # Already in recommended zone, return a copy
            return UTMPoint(
                easting=self.easting,
                northing=self.northing,
                zone_number=self.zone_number,
                zone_letter=self.zone_letter,
                height=self.height,
                forced_zone=False
            )
        
        # Get lat/lon and find recommended zone
        lat, lon = self.to_lat_lon()
        zone_num, zone_letter = self.get_utm_zone_from_lat_lon(lat, lon)
        
        # Change to recommended zone
        return self.change_zone(zone_num, zone_letter)
