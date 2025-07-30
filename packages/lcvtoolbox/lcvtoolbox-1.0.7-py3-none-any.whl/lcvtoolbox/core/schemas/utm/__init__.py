"""
UTM coordinate system schemas and utilities.

This module contains all UTM-related schemas for geographic operations,
including polygon representations and annotations with UTM coordinates.
"""

from .polygon import UTMPolygon
from .annotation import AnnotationAttribute, UTMAnnotation
from .point import UTMPoint
from .trajectory import UTMTrajectory
from .frame import UTMFrame
from .capture import UTMCapture

__all__ = [
    "UTMPolygon",
    "UTMPoint",
    "AnnotationAttribute", 
    "UTMAnnotation",
    "UTMTrajectory",
    "UTMFrame",
    "UTMCapture",
]
