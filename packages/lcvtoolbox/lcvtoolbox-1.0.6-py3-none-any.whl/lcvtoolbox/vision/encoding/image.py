"""Image encoding utilities for API transfer with lossy and lossless compression options."""

import base64
import io
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


class ImageFormat(Enum):
    """Supported image formats for encoding."""

    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WebP"
    WEBP_LOSSLESS = "WebP_Lossless"


class CompressionPreset(Enum):
    """Predefined compression presets for different use cases."""

    # Lossless presets
    LOSSLESS_MAX = "lossless_max"  # PNG with max compression
    LOSSLESS_FAST = "lossless_fast"  # PNG with fast compression
    LOSSLESS_WEBP = "lossless_webp"  # WebP lossless

    # Lossy presets
    HIGH_QUALITY = "high_quality"  # JPEG 95 or WebP 95
    BALANCED = "balanced"  # JPEG 85 or WebP 85
    SMALL_SIZE = "small_size"  # JPEG 75 or WebP 75
    TINY = "tiny"  # JPEG 60 or WebP 60


# Preset configurations
PRESET_CONFIGS = {
    CompressionPreset.LOSSLESS_MAX: {"format": ImageFormat.PNG, "compress_level": 9},
    CompressionPreset.LOSSLESS_FAST: {"format": ImageFormat.PNG, "compress_level": 1},
    CompressionPreset.LOSSLESS_WEBP: {"format": ImageFormat.WEBP_LOSSLESS},
    CompressionPreset.HIGH_QUALITY: {"format": ImageFormat.JPEG, "quality": 95},
    CompressionPreset.BALANCED: {"format": ImageFormat.JPEG, "quality": 85},
    CompressionPreset.SMALL_SIZE: {"format": ImageFormat.JPEG, "quality": 75},
    CompressionPreset.TINY: {"format": ImageFormat.JPEG, "quality": 60},
}


def _normalize_image_input(image: str | Path | Image.Image | np.ndarray) -> Image.Image:
    """Convert various image inputs to PIL Image.

    Args:
        image: Input image as file path, PIL Image, or numpy array.

    Returns:
        PIL Image object.

    Raises:
        TypeError: If image type is not supported.
        FileNotFoundError: If image path doesn't exist.
    """
    if isinstance(image, (str, Path)):
        path = Path(image)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        return Image.open(path)
    elif isinstance(image, Image.Image):
        return image
    elif isinstance(image, np.ndarray):
        # Handle different numpy array formats
        if image.ndim == 2:  # Grayscale
            return Image.fromarray(image.astype(np.uint8), mode="L")
        elif image.ndim == 3:
            if image.shape[2] == 3:  # RGB
                return Image.fromarray(image.astype(np.uint8), mode="RGB")
            elif image.shape[2] == 4:  # RGBA
                return Image.fromarray(image.astype(np.uint8), mode="RGBA")
            else:
                raise ValueError(f"Unsupported number of channels: {image.shape[2]}")
        else:
            raise ValueError(f"Unsupported array dimensions: {image.ndim}")
    else:
        raise TypeError(f"Unsupported image type: {type(image)}. Expected str, Path, PIL.Image, or numpy.ndarray")


def encode_image_to_bytes(
    image: str | Path | Image.Image | np.ndarray,
    format: ImageFormat | None = None,
    quality: int | None = None,
    compress_level: int | None = None,
    preset: CompressionPreset | None = None,
    optimize: bool = True,
    max_size_mb: float | None = None,
) -> bytes:
    """Encode an image to bytes with flexible compression options.

    Args:
        image: Input image as file path, PIL Image, or numpy array.
        format: Image format to use. If None, uses preset or defaults to JPEG.
        quality: JPEG/WebP quality (1-100). Higher is better quality.
        compress_level: PNG compression level (0-9). Higher is more compression.
        preset: Use a predefined compression preset instead of manual settings.
        optimize: Whether to optimize the encoding (slower but smaller).
        max_size_mb: Maximum encoded size in MB. Raises error if exceeded.

    Returns:
        Compressed image as bytes.

    Raises:
        ValueError: If parameters are invalid or size limit exceeded.

    Examples:
        >>> # Get JPEG bytes
        >>> image_bytes = encode_image_to_bytes("photo.jpg", format=ImageFormat.JPEG, quality=90)
        >>>
        >>> # Using preset
        >>> image_bytes = encode_image_to_bytes(numpy_array, preset=CompressionPreset.BALANCED)
    """
    # Convert input to PIL Image
    pil_image = _normalize_image_input(image)

    # Apply preset if specified
    if preset:
        config = PRESET_CONFIGS[preset]
        format = config.get("format", format)
        quality = config.get("quality", quality)
        compress_level = config.get("compress_level", compress_level)

    # Default format
    if format is None:
        format = ImageFormat.JPEG

    # Prepare save parameters
    save_params: dict[str, Any] = {"optimize": optimize}

    if format == ImageFormat.JPEG:
        # Convert RGBA to RGB for JPEG
        if pil_image.mode == "RGBA":
            background = Image.new("RGB", pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.split()[3])
            pil_image = background
        save_params["quality"] = quality or 85
        save_format = "JPEG"
    elif format == ImageFormat.PNG:
        save_params["compress_level"] = compress_level or 6
        save_format = "PNG"
    elif format == ImageFormat.WEBP:
        save_params["quality"] = quality or 85
        save_params["lossless"] = False
        save_format = "WebP"
    elif format == ImageFormat.WEBP_LOSSLESS:
        save_params["lossless"] = True
        save_params.pop("quality", None)  # Remove quality for lossless
        save_format = "WebP"
    else:
        save_format = "JPEG"
        save_params["quality"] = quality or 85

    # Encode to bytes
    buffer = io.BytesIO()
    pil_image.save(buffer, format=save_format, **save_params)
    image_bytes = buffer.getvalue()

    # Check size limit
    if max_size_mb is not None:
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"Encoded image size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)")

    return image_bytes


def encode_image_to_string(
    image: str | Path | Image.Image | np.ndarray,
    format: ImageFormat | None = None,
    quality: int | None = None,
    compress_level: int | None = None,
    preset: CompressionPreset | None = None,
    optimize: bool = True,
    max_size_mb: float | None = None,
) -> str:
    """Encode an image to a base64 string with flexible compression options.

    This is a wrapper around encode_image_to_bytes that adds base64 encoding
    for text-safe transmission through APIs.

    Args:
        image: Input image as file path, PIL Image, or numpy array.
        format: Image format to use. If None, uses preset or defaults to JPEG.
        quality: JPEG/WebP quality (1-100). Higher is better quality.
        compress_level: PNG compression level (0-9). Higher is more compression.
        preset: Use a predefined compression preset instead of manual settings.
        optimize: Whether to optimize the encoding (slower but smaller).
        max_size_mb: Maximum encoded size in MB. Raises error if exceeded.

    Returns:
        Base64 encoded string of the compressed image.

    Raises:
        ValueError: If parameters are invalid or size limit exceeded.

    Examples:
        >>> # Lossless PNG from file
        >>> encoded = encode_image_to_string("photo.jpg", format=ImageFormat.PNG)
        >>>
        >>> # Lossy JPEG with custom quality
        >>> encoded = encode_image_to_string(pil_image, format=ImageFormat.JPEG, quality=90)
        >>>
        >>> # Using preset for balanced compression
        >>> encoded = encode_image_to_string(numpy_array, preset=CompressionPreset.BALANCED)
    """
    image_bytes = encode_image_to_bytes(image=image, format=format, quality=quality, compress_level=compress_level, preset=preset, optimize=optimize, max_size_mb=max_size_mb)
    return base64.b64encode(image_bytes).decode("utf-8")


def encode_image_adaptive(
    image: str | Path | Image.Image | np.ndarray,
    target_size_kb: int = 500,
    min_quality: int = 60,
    max_quality: int = 95,
    format: ImageFormat = ImageFormat.JPEG,
) -> tuple[str, int]:
    """Encode image with adaptive quality to meet target size.

    Automatically adjusts quality to get as close as possible to target size
    while maintaining the best possible quality.

    Args:
        image: Input image as file path, PIL Image, or numpy array.
        target_size_kb: Target size in kilobytes.
        min_quality: Minimum acceptable quality.
        max_quality: Maximum quality to try.
        format: Image format (JPEG or WebP recommended).

    Returns:
        Tuple of (encoded_string, final_quality).

    Example:
        >>> # Encode to approximately 500KB
        >>> encoded, quality = encode_image_adaptive("large_photo.jpg", target_size_kb=500)
        >>> print(f"Encoded at quality {quality}")
    """
    pil_image = _normalize_image_input(image)
    target_bytes = target_size_kb * 1024

    # Binary search for optimal quality
    low, high = min_quality, max_quality
    best_encoded = None
    best_quality = min_quality

    while low <= high:
        mid_quality = (low + high) // 2

        # Try encoding at this quality
        encoded = encode_image_to_string(pil_image, format=format, quality=mid_quality, optimize=True)

        size_bytes = len(base64.b64decode(encoded))

        if size_bytes <= target_bytes:
            # Size is acceptable, try higher quality
            best_encoded = encoded
            best_quality = mid_quality
            low = mid_quality + 1
        else:
            # Size too large, reduce quality
            high = mid_quality - 1

    # If we couldn't get under target size even at min quality, use min quality
    if best_encoded is None:
        best_encoded = encode_image_to_string(pil_image, format=format, quality=min_quality, optimize=True)
        best_quality = min_quality

    return best_encoded, best_quality


def decode_bytes_to_image(image_bytes: bytes, output_format: str = "PIL") -> Image.Image | np.ndarray:
    """Decode image bytes back to an image.

    Args:
        image_bytes: Compressed image bytes.
        output_format: Output format - "PIL" for PIL Image or "numpy" for array.

    Returns:
        Decoded image as PIL Image or numpy array.

    Raises:
        ValueError: If bytes are invalid or output format unknown.

    Example:
        >>> # Decode to PIL Image
        >>> pil_image = decode_bytes_to_image(image_bytes)
        >>>
        >>> # Decode to numpy array
        >>> np_array = decode_bytes_to_image(image_bytes, output_format="numpy")
    """
    try:
        buffer = io.BytesIO(image_bytes)
        pil_image = Image.open(buffer)
    except Exception as e:
        raise ValueError(f"Invalid image bytes: {e}")

    if output_format.lower() == "pil":
        return pil_image
    elif output_format.lower() == "numpy":
        return np.array(pil_image)
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def decode_string_to_image(encoded_string: str, output_format: str = "PIL") -> Image.Image | np.ndarray:
    """Decode a base64 string back to an image.

    Args:
        encoded_string: Base64 encoded image string.
        output_format: Output format - "PIL" for PIL Image or "numpy" for array.

    Returns:
        Decoded image as PIL Image or numpy array.

    Raises:
        ValueError: If encoded string is invalid or output format unknown.

    Example:
        >>> # Decode to PIL Image
        >>> pil_image = decode_string_to_image(encoded_string)
        >>>
        >>> # Decode to numpy array
        >>> np_array = decode_string_to_image(encoded_string, output_format="numpy")
    """
    try:
        image_bytes = base64.b64decode(encoded_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}")

    return decode_bytes_to_image(image_bytes, output_format)


def decode_bytes_to_file(image_bytes: bytes, output_path: str | Path, format: str | None = None) -> None:
    """Decode image bytes and save to file.

    Args:
        image_bytes: Compressed image bytes.
        output_path: Path to save the decoded image.
        format: Output format. If None, inferred from file extension.

    Example:
        >>> decode_bytes_to_file(image_bytes, "decoded_image.png")
    """
    decoded_image = decode_bytes_to_image(image_bytes, output_format="PIL")
    # Type assertion to ensure it's a PIL Image
    assert isinstance(decoded_image, Image.Image)

    output_path = Path(output_path)

    # Create directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save image
    if format:
        decoded_image.save(output_path, format=format)
    else:
        decoded_image.save(output_path)


def decode_string_to_file(encoded_string: str, output_path: str | Path, format: str | None = None) -> None:
    """Decode a base64 string and save to file.

    Args:
        encoded_string: Base64 encoded image string.
        output_path: Path to save the decoded image.
        format: Output format. If None, inferred from file extension.

    Example:
        >>> decode_string_to_file(encoded_string, "decoded_image.png")
    """
    try:
        image_bytes = base64.b64decode(encoded_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}")

    decode_bytes_to_file(image_bytes, output_path, format)


def get_encoding_stats(image: str | Path | Image.Image | np.ndarray, encoded_string: str) -> dict[str, Any]:
    """Get statistics about image encoding.

    Args:
        image: Original image.
        encoded_string: Encoded image string.

    Returns:
        Dictionary with encoding statistics.
    """
    pil_image = _normalize_image_input(image)

    # Calculate sizes
    original_bytes = io.BytesIO()
    pil_image.save(original_bytes, format="PNG")
    original_bytes.seek(0)
    original_size = len(original_bytes.read())

    encoded_size = len(encoded_string.encode("utf-8"))
    decoded_size = len(base64.b64decode(encoded_string))

    return {
        "image_dimensions": pil_image.size,
        "image_mode": pil_image.mode,
        "original_size_bytes": original_size,
        "encoded_size_bytes": encoded_size,
        "decoded_size_bytes": decoded_size,
        "compression_ratio": decoded_size / original_size if original_size > 0 else 0,
        "base64_overhead": encoded_size / decoded_size if decoded_size > 0 else 0,
    }


# Convenience functions for common use cases
def encode_image_lossless(image: str | Path | Image.Image | np.ndarray, fast: bool = False) -> str:
    """Encode image using lossless compression to base64 string.

    Args:
        image: Input image.
        fast: Use fast compression (larger file) vs max compression.

    Returns:
        Base64 encoded string.
    """
    preset = CompressionPreset.LOSSLESS_FAST if fast else CompressionPreset.LOSSLESS_MAX
    return encode_image_to_string(image, preset=preset)


def encode_image_lossy(image: str | Path | Image.Image | np.ndarray, size_priority: bool = False) -> str:
    """Encode image using lossy compression to base64 string.

    Args:
        image: Input image.
        size_priority: Prioritize small size over quality.

    Returns:
        Base64 encoded string.
    """
    preset = CompressionPreset.SMALL_SIZE if size_priority else CompressionPreset.BALANCED
    return encode_image_to_string(image, preset=preset)


def encode_image_lossless_bytes(image: str | Path | Image.Image | np.ndarray, fast: bool = False) -> bytes:
    """Encode image using lossless compression to bytes.

    Args:
        image: Input image.
        fast: Use fast compression (larger file) vs max compression.

    Returns:
        Compressed image bytes.
    """
    preset = CompressionPreset.LOSSLESS_FAST if fast else CompressionPreset.LOSSLESS_MAX
    return encode_image_to_bytes(image, preset=preset)


def encode_image_lossy_bytes(image: str | Path | Image.Image | np.ndarray, size_priority: bool = False) -> bytes:
    """Encode image using lossy compression to bytes.

    Args:
        image: Input image.
        size_priority: Prioritize small size over quality.

    Returns:
        Compressed image bytes.
    """
    preset = CompressionPreset.SMALL_SIZE if size_priority else CompressionPreset.BALANCED
    return encode_image_to_bytes(image, preset=preset)


def encode_image_adaptive_bytes(
    image: str | Path | Image.Image | np.ndarray,
    target_size_kb: int = 500,
    min_quality: int = 60,
    max_quality: int = 95,
    format: ImageFormat = ImageFormat.JPEG,
) -> tuple[bytes, int]:
    """Encode image to bytes with adaptive quality to meet target size.

    Automatically adjusts quality to get as close as possible to target size
    while maintaining the best possible quality.

    Args:
        image: Input image as file path, PIL Image, or numpy array.
        target_size_kb: Target size in kilobytes.
        min_quality: Minimum acceptable quality.
        max_quality: Maximum quality to try.
        format: Image format (JPEG or WebP recommended).

    Returns:
        Tuple of (image_bytes, final_quality).

    Example:
        >>> # Encode to approximately 500KB
        >>> image_bytes, quality = encode_image_adaptive_bytes("large_photo.jpg", target_size_kb=500)
        >>> print(f"Encoded at quality {quality}")
    """
    pil_image = _normalize_image_input(image)
    target_bytes = target_size_kb * 1024

    # Binary search for optimal quality
    low, high = min_quality, max_quality
    best_bytes = None
    best_quality = min_quality

    while low <= high:
        mid_quality = (low + high) // 2

        # Try encoding at this quality
        image_bytes = encode_image_to_bytes(pil_image, format=format, quality=mid_quality, optimize=True)

        if len(image_bytes) <= target_bytes:
            # Size is acceptable, try higher quality
            best_bytes = image_bytes
            best_quality = mid_quality
            low = mid_quality + 1
        else:
            # Size too large, reduce quality
            high = mid_quality - 1

    # If we couldn't get under target size even at min quality, use min quality
    if best_bytes is None:
        best_bytes = encode_image_to_bytes(pil_image, format=format, quality=min_quality, optimize=True)
        best_quality = min_quality

    return best_bytes, best_quality
