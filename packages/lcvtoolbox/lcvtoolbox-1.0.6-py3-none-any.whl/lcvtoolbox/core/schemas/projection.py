"""
Pydantic schemas for mask projection functionality.
"""

from typing import Optional

from pydantic import BaseModel, Field
from shapely.geometry import Polygon


class UTMPolygonResult(BaseModel):
    """
    Result of mask projection to UTM coordinates.
    
    Contains the polygon geometry and UTM zone information required
    for proper geographic projection and visualization.
    """
    
    polygon: Polygon = Field(..., description="Shapely Polygon in UTM coordinates")
    zone_number: int = Field(..., ge=1, le=60, description="UTM zone number (1-60)")
    zone_letter: str = Field(..., pattern="^[C-X]$", description="UTM zone letter (C-X, excluding I and O)")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "polygon": "POLYGON ((448262.0 5411932.0, ...))",
                "zone_number": 31,
                "zone_letter": "U"
            }
        }


class MaskProjectionParams(BaseModel):
    """
    Parameters for mask projection configuration.
    
    Controls the polygon generation and simplification process.
    """
    
    simplify_tolerance: float = Field(
        default=0.5,
        ge=0,
        description="Tolerance for polygon simplification in meters. Higher values create simpler polygons."
    )
    min_area: float = Field(
        default=1.0,
        ge=0,
        description="Minimum polygon area in square meters. Smaller polygons are filtered out."
    )
    alpha: float = Field(
        default=2.0,
        gt=0,
        description="Alpha parameter for concave hull. Smaller values create tighter fits around points."
    )
    use_convex_hull: bool = Field(
        default=False,
        description="If True, uses convex hull instead of alpha shape for simpler shapes."
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "simplify_tolerance": 0.5,
                "min_area": 1.0,
                "alpha": 2.0,
                "use_convex_hull": False
            }
        }


class UTMReference(BaseModel):
    """
    Pre-computed UTM reference for efficiency.
    
    Stores UTM conversion results to avoid repeated calculations.
    """
    
    easting: float = Field(..., description="UTM easting coordinate in meters")
    northing: float = Field(..., description="UTM northing coordinate in meters")
    zone_number: int = Field(..., ge=1, le=60, description="UTM zone number")
    zone_letter: str = Field(..., pattern="^[C-X]$", description="UTM zone letter")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "easting": 448262.0,
                "northing": 5411932.0,
                "zone_number": 31,
                "zone_letter": "U"
            }
        }
