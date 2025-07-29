"""Placeholder image generation utilities."""

import numpy as np
from PIL import Image

from lcvtoolbox.vision.encoding.image import CompressionPreset, encode_image_to_string


def create_gradient_image(width: int, height: int) -> Image.Image:
    """Create a greyscale gradient RGB image from white to black.

    Args:
        width: Width of the image in pixels
        height: Height of the image in pixels

    Returns:
        PIL RGB Image with greyscale gradient from white (left) to black (right)
    """
    # Create a numpy array for the gradient (height, width, 3 channels for RGB)
    gradient = np.zeros((height, width, 3), dtype=np.uint8)

    # Create gradient from white (255) to black (0) horizontally
    for x in range(width):
        # Calculate the gradient value: white at x=0, black at x=width-1
        value = int(255 * (1 - x / (width - 1)) if width > 1 else 255)
        # Set all RGB channels to the same value for greyscale effect
        gradient[:, x, :] = value

    # Convert numpy array to PIL Image in RGB mode
    return Image.fromarray(gradient, mode="RGB")


def create_gradient_image_string(width: int, height: int) -> str:
    """Create a grayscale gradient RGB image and return its string encoding.

    Args:
        width: Width of the image in pixels
        height: Height of the image in pixels

    Returns:
        str encoding of the gradient image
    """
    # Create the gradient image
    gradient_image = create_gradient_image(width, height)

    # encode
    encoded = encode_image_to_string(
        image=gradient_image,
        preset=CompressionPreset.LOSSLESS_MAX,
    )
    return encoded
