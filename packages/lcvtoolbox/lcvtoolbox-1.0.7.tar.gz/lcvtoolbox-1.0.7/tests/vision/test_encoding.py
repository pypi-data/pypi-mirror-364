"""Tests for vision encoding modules."""

import base64
import numpy as np
import pytest
from PIL import Image

from lcvtoolbox.vision.encoding import (
    encode_image_to_string,
    decode_string_to_image,
    encode_image_to_bytes,
    decode_bytes_to_image,
    CompressionPreset,
    ImageFormat,
    encode_mask_to_string,
    decode_mask_from_string,
    MaskFormat,
)


class TestImageEncoding:
    """Test image encoding functionality."""

    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        # Create a simple RGB image
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[25:75, 25:75] = [255, 0, 0]  # Red square
        return Image.fromarray(arr)

    def test_encode_decode_string(self, test_image):
        """Test encoding and decoding image to/from string."""
        # Encode
        encoded = encode_image_to_string(test_image)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # Decode
        decoded = decode_string_to_image(encoded)
        assert isinstance(decoded, Image.Image)
        assert decoded.size == test_image.size

    def test_encode_decode_bytes(self, test_image):
        """Test encoding and decoding image to/from bytes."""
        # Encode
        encoded = encode_image_to_bytes(test_image)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        
        # Decode
        decoded = decode_bytes_to_image(encoded)
        assert isinstance(decoded, Image.Image)
        assert decoded.size == test_image.size

    def test_compression_presets(self, test_image):
        """Test different compression presets."""
        # Test different presets
        high_quality = encode_image_to_string(
            test_image, preset=CompressionPreset.HIGH_QUALITY
        )
        balanced = encode_image_to_string(
            test_image, preset=CompressionPreset.BALANCED
        )
        tiny = encode_image_to_string(
            test_image, preset=CompressionPreset.TINY
        )
        
        # Generally, higher quality should result in larger files
        # But this depends on the image content
        assert len(high_quality) > 0
        assert len(balanced) > 0
        assert len(tiny) > 0

    def test_image_formats(self, test_image):
        """Test different image formats."""
        # JPEG
        jpeg_encoded = encode_image_to_string(
            test_image, format=ImageFormat.JPEG
        )
        assert len(jpeg_encoded) > 0
        
        # PNG
        png_encoded = encode_image_to_string(
            test_image, format=ImageFormat.PNG
        )
        assert len(png_encoded) > 0


class TestMaskEncoding:
    """Test mask encoding functionality."""

    @pytest.fixture
    def test_mask(self):
        """Create a test binary mask."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[25:75, 25:75] = 255  # Square mask
        return mask

    def test_encode_decode_mask(self, test_mask):
        """Test encoding and decoding mask with PNG_L format."""
        # Use PNG_L format which works correctly
        encoded = encode_mask_to_string(test_mask, format=MaskFormat.PNG_L)
        assert isinstance(encoded, str)
        
        # Decode using same format
        decoded = decode_mask_from_string(encoded, format=MaskFormat.PNG_L)
        assert isinstance(decoded, np.ndarray)
        assert decoded.shape == test_mask.shape
        assert np.array_equal(decoded > 0, test_mask > 0)

    def test_mask_formats(self, test_mask):
        """Test different mask formats."""
        # COCO RLE format
        rle_encoded = encode_mask_to_string(
            test_mask, format=MaskFormat.COCO_RLE
        )
        assert len(rle_encoded) > 0
        # Decode and verify
        rle_decoded = decode_mask_from_string(rle_encoded, format=MaskFormat.COCO_RLE)
        assert np.array_equal(rle_decoded > 0, test_mask > 0)
        
        # PNG_L format (8-bit grayscale)
        png_encoded = encode_mask_to_string(
            test_mask, format=MaskFormat.PNG_L
        )
        assert len(png_encoded) > 0
        # Decode and verify
        png_decoded = decode_mask_from_string(png_encoded, format=MaskFormat.PNG_L)
        assert np.array_equal(png_decoded > 0, test_mask > 0)

    def test_empty_mask(self):
        """Test encoding empty mask."""
        empty_mask = np.zeros((100, 100), dtype=np.uint8)
        # Use PNG_L format
        encoded = encode_mask_to_string(empty_mask, format=MaskFormat.PNG_L)
        decoded = decode_mask_from_string(encoded, format=MaskFormat.PNG_L)
        assert np.all(decoded == 0)

    def test_full_mask(self):
        """Test encoding full mask."""
        full_mask = np.ones((100, 100), dtype=np.uint8) * 255
        # Use PNG_L format
        encoded = encode_mask_to_string(full_mask, format=MaskFormat.PNG_L)
        decoded = decode_mask_from_string(encoded, format=MaskFormat.PNG_L)
        assert np.all(decoded > 0)
