"""
Encoding-related TypedDict schemas.
"""

from typing import List, TypedDict

import numpy as np


class CocoRleDict(TypedDict):
    """
    COCO Run-Length Encoding dictionary format.
    
    Used for encoding binary masks in COCO format.
    """
    
    size: List[int]  # [height, width]
    counts: List[int]  # RLE counts


class CvatMaskAnnotation(TypedDict):
    """
    CVAT mask annotation format.
    
    Represents a mask annotation as exported by CVAT.
    """
    
    label: str
    source: str
    occluded: bool
    points: List[float]  # Encoded mask points
    z_order: int
    group: int
    attributes: List[dict]
