"""
Test data generators for images and masks.
"""

from .images import create_gradient_image, create_gradient_image_string
from .masks import create_square_mask, create_square_mask_string

__all__ = [
    "create_gradient_image",
    "create_gradient_image_string",
    "create_square_mask",
    "create_square_mask_string",
]
