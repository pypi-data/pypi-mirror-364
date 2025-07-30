"""Tests for data generators module."""

import numpy as np
import pytest
from PIL import Image

from lcvtoolbox.data.generators import (
    create_gradient_image,
    create_gradient_image_string,
    create_square_mask,
    create_square_mask_string,
)


class TestImageGenerators:
    """Test image generation functionality."""

    def test_create_gradient_image(self):
        """Test creating a gradient image."""
        width, height = 100, 100
        img = create_gradient_image(width, height)
        
        assert isinstance(img, Image.Image)
        assert img.size == (width, height)
        assert img.mode == "RGB"

    def test_create_gradient_image_string(self):
        """Test creating a gradient image as base64 string."""
        width, height = 50, 50
        img_str = create_gradient_image_string(width, height)
        
        assert isinstance(img_str, str)
        assert len(img_str) > 0
        # Should be valid base64
        import base64
        try:
            base64.b64decode(img_str)
        except Exception:
            pytest.fail("Invalid base64 string")

    @pytest.mark.parametrize("width,height", [
        (10, 10),
        (100, 50),
        (256, 256),
    ])
    def test_gradient_image_sizes(self, width, height):
        """Test creating gradient images with different sizes."""
        img = create_gradient_image(width, height)
        assert img.size == (width, height)


class TestMaskGenerators:
    """Test mask generation functionality."""

    def test_create_square_mask(self):
        """Test creating a square mask."""
        width, height = 100, 100
        mask = create_square_mask(width, height)
        
        assert isinstance(mask, np.ndarray)
        assert mask.shape == (height, width)
        assert mask.dtype == np.uint8
        # Check it's binary
        unique_values = np.unique(mask)
        assert len(unique_values) <= 2

    def test_create_square_mask_string(self):
        """Test creating a square mask as base64 string."""
        width, height = 50, 50
        mask_str = create_square_mask_string(width, height)
        
        assert isinstance(mask_str, str)
        assert len(mask_str) > 0
        # Should be valid base64
        import base64
        try:
            base64.b64decode(mask_str)
        except Exception:
            pytest.fail("Invalid base64 string")

    def test_square_mask_has_square(self):
        """Test that square mask actually contains a square."""
        width, height = 100, 100
        mask = create_square_mask(width, height)
        
        # Check center region is non-zero (the square)
        center_region = mask[25:75, 25:75]
        assert np.any(center_region > 0)
        
        # Check corners are zero (outside the square)
        assert mask[0, 0] == 0
        assert mask[0, -1] == 0
        assert mask[-1, 0] == 0
        assert mask[-1, -1] == 0
