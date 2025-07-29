"""Binary mask encoding utilities optimized for efficient API transfer.

Binary masks are images with only two values (0/1 or 0/255) and can be compressed
much more efficiently than regular images using specialized techniques.
"""

import base64
import io
import zlib
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


class MaskFormat(Enum):
    """Supported formats for binary mask encoding."""

    PNG_1BIT = "PNG_1BIT"  # 1-bit PNG (most efficient for simple masks)
    PNG_L = "PNG_L"  # 8-bit grayscale PNG
    RLE = "RLE"  # Run-length encoding
    COCO_RLE = "COCO_RLE"  # COCO-style RLE format
    PACKED_BITS = "PACKED_BITS"  # Bit-packed array
    ZLIB_COMPRESSED = "ZLIB_COMPRESSED"  # Zlib compressed binary


def _normalize_mask_input(mask: str | Path | Image.Image | np.ndarray | list[list[int]]) -> np.ndarray:
    """Convert various mask inputs to binary numpy array.

    Args:
        mask: Input mask as file path, PIL Image, numpy array, or list.

    Returns:
        Binary numpy array with values 0 and 1.

    Raises:
        TypeError: If mask type is not supported.
        ValueError: If mask contains non-binary values.
    """
    if isinstance(mask, (str, Path)):
        path = Path(mask)
        if not path.exists():
            raise FileNotFoundError(f"Mask file not found: {path}")
        pil_image = Image.open(path)
        if pil_image.mode != "L":
            pil_image = pil_image.convert("L")
        mask_array = np.array(pil_image)
    elif isinstance(mask, Image.Image):
        if mask.mode != "L":
            mask = mask.convert("L")
        mask_array = np.array(mask)
    elif isinstance(mask, list):
        mask_array = np.array(mask, dtype=np.uint8)
    elif isinstance(mask, np.ndarray):
        mask_array = mask.astype(np.uint8)
    else:
        raise TypeError(f"Unsupported mask type: {type(mask)}. Expected str, Path, PIL.Image, numpy.ndarray, or list")

    # Normalize to binary (0 or 1)
    unique_values = np.unique(mask_array)
    if len(unique_values) > 2:
        raise ValueError(f"Mask contains {len(unique_values)} unique values. Binary masks should contain only 2 values.")

    # Convert to 0/1
    if len(unique_values) == 2:
        threshold = (unique_values[0] + unique_values[1]) / 2
        mask_array = (mask_array > threshold).astype(np.uint8)
    elif len(unique_values) == 1:
        # All zeros or all ones
        mask_array = (mask_array > 0).astype(np.uint8)

    return mask_array


def encode_mask_png_1bit(mask_array: np.ndarray) -> bytes:
    """Encode binary mask as 1-bit PNG (most efficient for simple masks).

    Args:
        mask_array: Binary numpy array with values 0 and 1.

    Returns:
        PNG bytes with 1-bit depth.
    """
    # Convert to PIL Image with mode '1' (1-bit pixels)
    pil_image = Image.fromarray((mask_array * 255).astype(np.uint8), mode="L")
    pil_image = pil_image.convert("1")

    # Save as PNG
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG", optimize=True, compress_level=9)
    return buffer.getvalue()


def encode_mask_png_l(mask_array: np.ndarray) -> bytes:
    """Encode binary mask as 8-bit grayscale PNG.

    Args:
        mask_array: Binary numpy array with values 0 and 1.

    Returns:
        PNG bytes with 8-bit grayscale.
    """
    # Convert to 0/255 for better visualization
    mask_255 = (mask_array * 255).astype(np.uint8)
    pil_image = Image.fromarray(mask_255, mode="L")

    # Save as PNG with maximum compression
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG", optimize=True, compress_level=9)
    return buffer.getvalue()


def encode_mask_rle(mask_array: np.ndarray) -> dict[str, Any]:
    """Encode binary mask using run-length encoding.

    RLE encodes runs of 0s and 1s as pairs of (value, count).

    Args:
        mask_array: Binary numpy array with values 0 and 1.

    Returns:
        Dictionary with RLE data and shape information.
    """
    # Flatten the array
    flat_mask = mask_array.flatten()

    # Find run lengths
    runs = []
    current_value = flat_mask[0]
    current_length = 1

    for i in range(1, len(flat_mask)):
        if flat_mask[i] == current_value:
            current_length += 1
        else:
            runs.append((int(current_value), current_length))
            current_value = flat_mask[i]
            current_length = 1

    # Don't forget the last run
    runs.append((int(current_value), current_length))

    return {"shape": mask_array.shape, "runs": runs, "dtype": "uint8"}


def encode_mask_coco_rle(mask_array: np.ndarray) -> dict[str, Any]:
    """Encode binary mask using COCO-style RLE format.

    COCO RLE format encodes the mask column-wise and stores counts of
    consecutive 0s and 1s, starting with 0s.

    Args:
        mask_array: Binary numpy array with values 0 and 1.

    Returns:
        Dictionary in COCO RLE format.
    """
    # COCO uses column-major (Fortran) order
    mask_fortran = np.asfortranarray(mask_array)
    flat_mask = mask_fortran.flatten()

    # Compute RLE counts (starting with 0s)
    counts = []
    current_val = 0
    current_count = 0

    for val in flat_mask:
        if val == current_val:
            current_count += 1
        else:
            counts.append(current_count)
            current_val = val
            current_count = 1

    # Add the last count
    counts.append(current_count)

    # If we started with 1, prepend a 0
    if flat_mask[0] == 1:
        counts = [0] + counts

    return {
        "size": [int(mask_array.shape[0]), int(mask_array.shape[1])],  # height, width
        "counts": counts,
    }


def encode_mask_packed_bits(mask_array: np.ndarray) -> bytes:
    """Encode binary mask as packed bits (8 pixels per byte).

    Args:
        mask_array: Binary numpy array with values 0 and 1.

    Returns:
        Packed bytes where each bit represents a pixel.
    """
    # Flatten the array
    flat_mask = mask_array.flatten()

    # Pack bits into bytes
    num_bytes = (len(flat_mask) + 7) // 8
    packed = np.zeros(num_bytes, dtype=np.uint8)

    for i in range(len(flat_mask)):
        if flat_mask[i]:
            byte_idx = i // 8
            bit_idx = i % 8
            packed[byte_idx] |= 1 << (7 - bit_idx)

    return packed.tobytes()


def encode_mask_to_bytes(mask: str | Path | Image.Image | np.ndarray | list[list[int]], format: MaskFormat = MaskFormat.PNG_1BIT, compress: bool = True) -> bytes:
    """Encode a binary mask to bytes using the specified format.

    Args:
        mask: Input mask in various formats.
        format: Encoding format to use.
        compress: Whether to apply additional zlib compression.

    Returns:
        Encoded mask as bytes.

    Examples:
        >>> # Encode as 1-bit PNG (most efficient)
        >>> mask_bytes = encode_mask_to_bytes(mask_array, format=MaskFormat.PNG_1BIT)
        >>>
        >>> # Encode as packed bits with compression
        >>> mask_bytes = encode_mask_to_bytes(mask_array, format=MaskFormat.PACKED_BITS)
    """
    # Normalize input to binary array
    mask_array = _normalize_mask_input(mask)

    # Encode based on format
    if format == MaskFormat.PNG_1BIT:
        encoded = encode_mask_png_1bit(mask_array)
    elif format == MaskFormat.PNG_L:
        encoded = encode_mask_png_l(mask_array)
    elif format == MaskFormat.PACKED_BITS:
        # Include shape information for decoding
        shape_bytes = np.array(mask_array.shape, dtype=np.uint32).tobytes()
        packed_bytes = encode_mask_packed_bits(mask_array)
        encoded = shape_bytes + packed_bytes
    elif format == MaskFormat.ZLIB_COMPRESSED:
        # Direct zlib compression of binary array
        encoded = zlib.compress(mask_array.tobytes(), level=9)
        # Prepend shape for decoding
        shape_bytes = np.array(mask_array.shape, dtype=np.uint32).tobytes()
        encoded = shape_bytes + encoded
    else:
        raise ValueError(f"Bytes encoding not supported for format: {format}")

    # Apply additional compression if requested and not already compressed
    if compress and format not in [MaskFormat.PNG_1BIT, MaskFormat.PNG_L, MaskFormat.ZLIB_COMPRESSED]:
        encoded = zlib.compress(encoded, level=9)

    return encoded


def encode_mask_to_string(mask: str | Path | Image.Image | np.ndarray | list[list[int]], format: MaskFormat = MaskFormat.PNG_1BIT, compress: bool = True) -> str:
    """Encode a binary mask to base64 string using the specified format.

    Args:
        mask: Input mask in various formats.
        format: Encoding format to use.
        compress: Whether to apply additional compression.

    Returns:
        Base64 encoded string of the mask.
    """
    if format in [MaskFormat.RLE, MaskFormat.COCO_RLE]:
        # These formats return dictionaries, encode as JSON string
        import json

        mask_array = _normalize_mask_input(mask)
        if format == MaskFormat.RLE:
            data = encode_mask_rle(mask_array)
        else:
            data = encode_mask_coco_rle(mask_array)
        return base64.b64encode(json.dumps(data).encode()).decode("utf-8")
    else:
        # Binary formats
        mask_bytes = encode_mask_to_bytes(mask, format=format, compress=compress)
        return base64.b64encode(mask_bytes).decode("utf-8")


def decode_mask_from_bytes(mask_bytes: bytes, format: MaskFormat, compressed: bool = True) -> np.ndarray:
    """Decode bytes back to a binary mask array.

    Args:
        mask_bytes: Encoded mask bytes.
        format: Format used for encoding.
        compressed: Whether additional compression was applied.

    Returns:
        Binary numpy array with values 0 and 1.
    """
    # Decompress if needed
    if compressed and format not in [MaskFormat.PNG_1BIT, MaskFormat.PNG_L, MaskFormat.ZLIB_COMPRESSED]:
        mask_bytes = zlib.decompress(mask_bytes)

    if format in [MaskFormat.PNG_1BIT, MaskFormat.PNG_L]:
        # Decode PNG
        buffer = io.BytesIO(mask_bytes)
        pil_image = Image.open(buffer)
        mask_array = np.array(pil_image)
        # Normalize to 0/1
        return (mask_array > 127).astype(np.uint8)

    elif format == MaskFormat.PACKED_BITS:
        # Extract shape and packed data
        shape = np.frombuffer(mask_bytes[:8], dtype=np.uint32)
        packed_data = np.frombuffer(mask_bytes[8:], dtype=np.uint8)

        # Unpack bits
        total_pixels = shape[0] * shape[1]
        mask_flat = np.zeros(total_pixels, dtype=np.uint8)

        for i in range(total_pixels):
            byte_idx = i // 8
            bit_idx = i % 8
            if byte_idx < len(packed_data):
                mask_flat[i] = (packed_data[byte_idx] >> (7 - bit_idx)) & 1

        return mask_flat.reshape(shape)

    elif format == MaskFormat.ZLIB_COMPRESSED:
        # Extract shape and decompress
        shape = np.frombuffer(mask_bytes[:8], dtype=np.uint32)
        decompressed = zlib.decompress(mask_bytes[8:])
        mask_array = np.frombuffer(decompressed, dtype=np.uint8).reshape(shape)
        return mask_array

    else:
        raise ValueError(f"Bytes decoding not supported for format: {format}")


def decode_mask_from_string(encoded_string: str, format: MaskFormat, compressed: bool = True) -> np.ndarray:
    """Decode base64 string back to a binary mask array.

    Args:
        encoded_string: Base64 encoded mask string.
        format: Format used for encoding.
        compressed: Whether additional compression was applied.

    Returns:
        Binary numpy array with values 0 and 1.
    """
    if format in [MaskFormat.RLE, MaskFormat.COCO_RLE]:
        # Decode JSON-based formats
        import json

        decoded_bytes = base64.b64decode(encoded_string)
        data = json.loads(decoded_bytes.decode("utf-8"))

        if format == MaskFormat.RLE:
            # Decode standard RLE
            shape = tuple(data["shape"])
            runs = data["runs"]

            # Reconstruct mask
            mask_flat = []
            for value, count in runs:
                mask_flat.extend([value] * count)

            return np.array(mask_flat, dtype=np.uint8).reshape(shape)

        else:  # COCO_RLE
            # Decode COCO RLE
            size = data["size"]  # [height, width]
            counts = data["counts"]

            # Reconstruct mask
            mask_flat = []
            val = 0
            for count in counts:
                mask_flat.extend([val] * count)
                val = 1 - val

            # COCO uses column-major order
            mask_fortran = np.array(mask_flat[: size[0] * size[1]], dtype=np.uint8)
            return mask_fortran.reshape(size[1], size[0]).T

    else:
        # Binary formats
        mask_bytes = base64.b64decode(encoded_string)
        return decode_mask_from_bytes(mask_bytes, format=format, compressed=compressed)


def get_mask_encoding_stats(mask: str | Path | Image.Image | np.ndarray | list[list[int]]) -> dict[str, Any]:
    """Compare encoding efficiency of different formats for a given mask.

    Args:
        mask: Input mask to analyze.

    Returns:
        Dictionary with size statistics for each encoding format.
    """
    mask_array = _normalize_mask_input(mask)
    original_size = mask_array.nbytes

    stats = {"shape": mask_array.shape, "original_size_bytes": original_size, "formats": {}}

    # Test each format
    for format in MaskFormat:
        try:
            if format in [MaskFormat.RLE, MaskFormat.COCO_RLE]:
                # JSON-based formats
                encoded = encode_mask_to_string(mask_array, format=format)
                size = len(encoded.encode("utf-8"))
            else:
                # Binary formats
                encoded_bytes = encode_mask_to_bytes(mask_array, format=format, compress=True)
                size = len(encoded_bytes)

            stats["formats"][format.value] = {"size_bytes": size, "compression_ratio": original_size / size if size > 0 else 0, "size_reduction": f"{(1 - size / original_size) * 100:.1f}%"}
        except Exception as e:
            stats["formats"][format.value] = {"error": str(e)}

    # Find best format
    valid_formats = {k: v for k, v in stats["formats"].items() if "size_bytes" in v}
    if valid_formats:
        best_format = min(valid_formats.items(), key=lambda x: x[1]["size_bytes"])
        stats["best_format"] = best_format[0]
        stats["best_size_bytes"] = best_format[1]["size_bytes"]

    return stats


# Convenience functions
def encode_mask_efficient(mask: str | Path | Image.Image | np.ndarray | list[list[int]], output: str = "string") -> str | bytes:
    """Encode mask using the most efficient format automatically.

    Args:
        mask: Input mask.
        output: "string" for base64 or "bytes" for raw bytes.

    Returns:
        Encoded mask in the most efficient format.
    """
    # Get stats to find best format
    stats = get_mask_encoding_stats(mask)
    best_format = MaskFormat(stats.get("best_format", "PNG_1BIT"))

    if output == "string":
        return encode_mask_to_string(mask, format=best_format)
    else:
        return encode_mask_to_bytes(mask, format=best_format)


def encode_mask_batch(masks: list[np.ndarray | Image.Image], format: MaskFormat = MaskFormat.PNG_1BIT) -> list[str]:
    """Encode multiple masks efficiently.

    Args:
        masks: List of masks to encode.
        format: Format to use for all masks.

    Returns:
        List of base64 encoded strings.
    """
    return [encode_mask_to_string(mask, format=format) for mask in masks]
