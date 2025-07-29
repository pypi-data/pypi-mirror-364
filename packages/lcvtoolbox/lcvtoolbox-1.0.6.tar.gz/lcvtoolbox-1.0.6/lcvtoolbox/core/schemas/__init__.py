"""
Centralized schema module for all Pydantic models and TypedDict definitions.

This module consolidates all schemas used throughout the cv-toolbox project
to ensure consistency and avoid duplication.
"""

# GPS and Location schemas
from .gps import GPSCoordinates, GPSPoint

# Pose and spatial schemas
from .pose import PoseRPYSchema

# Camera schemas
from .camera import CameraDistortionSchema, CameraMatrixSchema

# Frame and metadata schemas
from .frame import FrameMetadata, ImageMetadata

# UTM and projection schemas
from .projection import MaskProjectionParams, UTMPolygonResult, UTMReference

# CVAT schemas (Pydantic)
from .cvat_pydantic import (
    CvatApiAttribute,
    CvatApiAttributeDefinition,
    CvatApiJobAnnotations,
    CvatApiJobDetails,
    CvatApiJobMediasMetainformation,
    CvatApiLabelDefinition,
    CvatApiMetainformationFrame,
    CvatApiShape,
    CvatApiTag,
    CvatApiTaskAnnotations,
    CvatApiTaskDetails,
    CvatApiTaskMediasMetainformation,
)

# CVAT TypedDict schemas
from .cvat_typed import (
    CvatApiAttribute as CvatApiAttributeDict,
    CvatApiAttributeDefinition as CvatApiAttributeDefinitionDict,
    CvatApiJobAnnotations as CvatApiJobAnnotationsDict,
    CvatApiJobDetails as CvatApiJobDetailsDict,
    CvatApiJobMediasMetainformation as CvatApiJobMediasMetainformationDict,
    CvatApiLabelDefinition as CvatApiLabelDefinitionDict,
    CvatApiMetainformationFrame as CvatApiMetainformationFrameDict,
    CvatApiShape as CvatApiShapeDict,
    CvatApiTag as CvatApiTagDict,
    CvatApiTaskAnnotations as CvatApiTaskAnnotationsDict,
    CvatApiTaskDetails as CvatApiTaskDetailsDict,
    CvatApiTaskMediasMetainformation as CvatApiTaskMediasMetainformationDict,
)

# Encoding schemas
from .encoding import CocoRleDict, CvatMaskAnnotation

# HuggingFace endpoint schemas
from .huggingface import Annotation, InputData, Logs, Parameters, RawAnnotation

__all__ = [
    # GPS
    "GPSCoordinates",
    "GPSPoint",
    # Pose
    "PoseRPYSchema",
    # Camera
    "CameraDistortionSchema",
    "CameraMatrixSchema",
    # Frame
    "FrameMetadata",
    "ImageMetadata",
    # Projection
    "MaskProjectionParams",
    "UTMPolygonResult",
    "UTMReference",
    # CVAT Pydantic
    "CvatApiAttribute",
    "CvatApiAttributeDefinition",
    "CvatApiJobAnnotations",
    "CvatApiJobDetails",
    "CvatApiJobMediasMetainformation",
    "CvatApiLabelDefinition",
    "CvatApiMetainformationFrame",
    "CvatApiShape",
    "CvatApiTag",
    "CvatApiTaskAnnotations",
    "CvatApiTaskDetails",
    "CvatApiTaskMediasMetainformation",
    # CVAT TypedDict
    "CvatApiAttributeDict",
    "CvatApiAttributeDefinitionDict",
    "CvatApiJobAnnotationsDict",
    "CvatApiJobDetailsDict",
    "CvatApiJobMediasMetainformationDict",
    "CvatApiLabelDefinitionDict",
    "CvatApiMetainformationFrameDict",
    "CvatApiShapeDict",
    "CvatApiTagDict",
    "CvatApiTaskAnnotationsDict",
    "CvatApiTaskDetailsDict",
    "CvatApiTaskMediasMetainformationDict",
    # Encoding
    "CocoRleDict",
    "CvatMaskAnnotation",
    # HuggingFace
    "Annotation",
    "InputData",
    "Logs",
    "Parameters",
    "RawAnnotation",
]
