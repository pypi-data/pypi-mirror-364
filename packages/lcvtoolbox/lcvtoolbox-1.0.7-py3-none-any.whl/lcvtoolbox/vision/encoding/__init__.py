"""
Image and mask encoding utilities.
"""

from .binary_mask import (
    MaskFormat,
    encode_mask_to_bytes,
    encode_mask_to_string,
    decode_mask_from_bytes,
    decode_mask_from_string,
    get_mask_encoding_stats,
    encode_mask_efficient,
    encode_mask_batch,
)

from .image import (
    ImageFormat,
    CompressionPreset,
    encode_image_to_bytes,
    encode_image_to_string,
    decode_bytes_to_image,
    decode_string_to_image,
    encode_image_adaptive,
    encode_image_lossless,
    encode_image_lossy,
)

__all__ = [
    # Mask encoding
    "MaskFormat",
    "encode_mask_to_bytes",
    "encode_mask_to_string",
    "decode_mask_from_bytes",
    "decode_mask_from_string",
    "get_mask_encoding_stats",
    "encode_mask_efficient",
    "encode_mask_batch",
    # Image encoding
    "ImageFormat",
    "CompressionPreset",
    "encode_image_to_bytes",
    "encode_image_to_string",
    "decode_bytes_to_image",
    "decode_string_to_image",
    "encode_image_adaptive",
    "encode_image_lossless",
    "encode_image_lossy",
]
