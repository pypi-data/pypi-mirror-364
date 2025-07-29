"""Placeholder mask generation utilities."""

import numpy as np

from lcvtoolbox.vision.encoding.binary_mask import MaskFormat, encode_mask_to_string


def create_square_mask(width: int, height: int) -> np.ndarray:
    """Create a binary mask with a square in the center.

    The square has half the proportions of the canvas (half width and half height).

    Args:
        width: Width of the canvas in pixels
        height: Height of the canvas in pixels

    Returns:
        numpy array of shape (height, width) with 0/1 values.
        1 represents the square area, 0 represents the background.
    """
    # Create a mask filled with zeros (background)
    mask = np.zeros((height, width), dtype=np.uint8)

    # Calculate square dimensions (half of canvas dimensions)
    square_width = width // 2
    square_height = height // 2

    # Calculate square position (centered)
    start_x = (width - square_width) // 2
    start_y = (height - square_height) // 2
    end_x = start_x + square_width
    end_y = start_y + square_height

    # Set the square area to 1
    mask[start_y:end_y, start_x:end_x] = 1

    return mask


def create_square_mask_string(width: int, height: int) -> str:
    """Create a binary mask with a square in the center and return its string encoding.

    Args:
        width: Width of the canvas in pixels
        height: Height of the canvas in pixels

    Returns:
        str encoding of the mask
    """
    # Create the square mask
    mask = create_square_mask(width, height)

    # encode
    encoded_mask = encode_mask_to_string(mask, format=MaskFormat.PNG_L, compress=False)

    return encoded_mask
