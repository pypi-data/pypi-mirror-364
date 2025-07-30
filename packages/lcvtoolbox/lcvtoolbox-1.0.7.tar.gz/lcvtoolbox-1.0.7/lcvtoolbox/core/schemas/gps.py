"""
GPS and location-related schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field


class GPSPoint(BaseModel):
    """
    Schema for GPS metadata in image metadata.
    
    Attributes:
        time: Timestamp in milliseconds
        latitude: Latitude coordinate in degrees
        longitude: Longitude coordinate in degrees  
        altitude: Altitude in meters
        orientation: Orientation angle in degrees
    """

    time: int = Field(..., description="Timestamp in milliseconds")
    latitude: float = Field(..., description="Latitude coordinate in degrees", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate in degrees", ge=-180, le=180)
    altitude: float = Field(..., description="Altitude in meters")
    orientation: float = Field(..., description="Orientation angle in degrees", ge=-180, le=180)


class GPSCoordinates(BaseModel):
    """
    GPS coordinates with optional heading for vehicle localization.
    
    Extends basic GPS coordinates with heading information needed
    for proper orientation in UTM projection.
    """
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    heading: Optional[float] = Field(None, ge=0, lt=360, description="Vehicle heading in degrees (0° = North)")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "heading": 45.0
            }
        }
