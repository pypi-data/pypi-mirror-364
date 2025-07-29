"""
HuggingFace endpoint TypedDict schemas.
"""

from typing import Any, Dict, List, NotRequired, TypedDict

import numpy as np


class Logs(TypedDict):
    """
    Logs structure for HuggingFace endpoint responses.
    """
    
    message: str
    level: str
    timestamp: str


class Annotation(TypedDict):
    """Type of annotation data exchanged between the server and the client but with the masks decoded."""

    id: int
    image_id: int
    category_id: int
    bbox: List[float]  # [x, y, width, height]
    area: float
    segmentation: np.ndarray  # Decoded mask
    iscrowd: int


class RawAnnotation(TypedDict):
    """
    Raw annotation format with encoded masks.
    """
    
    id: int
    image_id: int
    category_id: int
    bbox: List[float]  # [x, y, width, height]
    area: float
    segmentation: Dict[str, Any]  # Encoded mask (e.g., RLE)
    iscrowd: int


class Parameters(TypedDict):
    """Type of entry parameters exchanged between the server and the client."""
    
    model_name: str
    task: str
    device: NotRequired[str]
    batch_size: NotRequired[int]
    threshold: NotRequired[float]
    max_detections: NotRequired[int]
    nms_threshold: NotRequired[float]


class InputData(TypedDict):
    """
    Input data structure for HuggingFace endpoint.
    """
    
    image: np.ndarray
    metadata: NotRequired[Dict[str, Any]]
