"""NumPy array encoding utilities optimized for efficient API transfer.

This module provides various encoding strategies for numpy arrays, including
compression, quantization, and format optimization based on array characteristics.
"""

import base64
import io
import json
import pickle
import zlib
from enum import Enum
from typing import Any

import numpy as np


class NumpyFormat(Enum):
    """Supported formats for numpy array encoding."""

    NPZ_COMPRESSED = "NPZ_COMPRESSED"  # NumPy's compressed format
    NPY = "NPY"  # NumPy's native format
    PICKLE = "PICKLE"  # Python pickle format
    JSON_FULL = "JSON_FULL"  # Full precision JSON
    JSON_ROUNDED = "JSON_ROUNDED"  # Rounded values JSON
    BYTES_RAW = "BYTES_RAW"  # Raw bytes with metadata
    BYTES_COMPRESSED = "BYTES_COMPRESSED"  # Compressed bytes
    FLOAT16 = "FLOAT16"  # Half precision for float arrays
    UINT8_SCALED = "UINT8_SCALED"  # Scale to uint8 for compression


class ArrayMetadata:
    """Metadata for array reconstruction."""

    def __init__(self, shape: tuple, dtype: str, **kwargs):
        self.shape = shape
        self.dtype = dtype
        self.extra = kwargs

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        return {"shape": self.shape, "dtype": self.dtype, **self.extra}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArrayMetadata":
        """Create metadata from dictionary."""
        extra = {k: v for k, v in data.items() if k not in ["shape", "dtype"]}
        return cls(shape=tuple(data["shape"]), dtype=data["dtype"], **extra)


def analyze_array(arr: np.ndarray) -> dict[str, Any]:
    """Analyze array characteristics to determine optimal encoding.

    Args:
        arr: NumPy array to analyze.

    Returns:
        Dictionary with array statistics and recommendations.
    """
    stats = {
        "shape": arr.shape,
        "dtype": str(arr.dtype),
        "size": arr.size,
        "bytes": arr.nbytes,
        "min": float(arr.min()) if arr.size > 0 else None,
        "max": float(arr.max()) if arr.size > 0 else None,
        "unique_ratio": len(np.unique(arr)) / arr.size if arr.size > 0 else 0,
        "is_sparse": np.count_nonzero(arr) / arr.size < 0.1 if arr.size > 0 else False,
        "is_integer": np.issubdtype(arr.dtype, np.integer),
        "is_boolean": arr.dtype == bool,
        "is_float": np.issubdtype(arr.dtype, np.floating),
    }

    # Recommendations
    if stats["is_boolean"]:
        stats["recommended_format"] = NumpyFormat.BYTES_COMPRESSED
    elif stats["is_sparse"]:
        stats["recommended_format"] = NumpyFormat.NPZ_COMPRESSED
    elif stats["is_float"] and stats["bytes"] > 1000:
        # Check if float16 would preserve enough precision
        if arr.size > 0:
            arr_f16 = arr.astype(np.float16).astype(arr.dtype)
            max_error = np.abs(arr - arr_f16).max()
            relative_error = max_error / (np.abs(arr).max() + 1e-10)
            if relative_error < 0.001:  # Less than 0.1% error
                stats["recommended_format"] = NumpyFormat.FLOAT16
            else:
                stats["recommended_format"] = NumpyFormat.NPZ_COMPRESSED
        else:
            stats["recommended_format"] = NumpyFormat.NPZ_COMPRESSED
    elif stats["unique_ratio"] < 0.01:  # Very few unique values
        stats["recommended_format"] = NumpyFormat.BYTES_COMPRESSED
    else:
        stats["recommended_format"] = NumpyFormat.NPZ_COMPRESSED

    return stats


def encode_array_npz(arr: np.ndarray, compressed: bool = True) -> bytes:
    """Encode array using NumPy's NPZ format.

    Args:
        arr: NumPy array to encode.
        compressed: Whether to use compression.

    Returns:
        NPZ format bytes.
    """
    buffer = io.BytesIO()
    if compressed:
        np.savez_compressed(buffer, array=arr)
    else:
        np.savez(buffer, array=arr)
    return buffer.getvalue()


def encode_array_npy(arr: np.ndarray) -> bytes:
    """Encode array using NumPy's NPY format.

    Args:
        arr: NumPy array to encode.

    Returns:
        NPY format bytes.
    """
    buffer = io.BytesIO()
    np.save(buffer, arr, allow_pickle=False)
    return buffer.getvalue()


def encode_array_pickle(arr: np.ndarray, protocol: int = pickle.HIGHEST_PROTOCOL) -> bytes:
    """Encode array using pickle.

    Args:
        arr: NumPy array to encode.
        protocol: Pickle protocol version.

    Returns:
        Pickled bytes.
    """
    return pickle.dumps(arr, protocol=protocol)


def encode_array_json(arr: np.ndarray, decimals: int | None = None) -> str:
    """Encode array as JSON.

    Args:
        arr: NumPy array to encode.
        decimals: Number of decimal places to round to (None for full precision).

    Returns:
        JSON string.
    """
    if decimals is not None:
        arr_rounded = np.around(arr, decimals=decimals)
        data = {"data": arr_rounded.tolist(), "shape": arr.shape, "dtype": str(arr.dtype), "decimals": decimals}
    else:
        data = {"data": arr.tolist(), "shape": arr.shape, "dtype": str(arr.dtype)}

    return json.dumps(data, separators=(",", ":"))


def encode_array_bytes(arr: np.ndarray, compress: bool = True) -> bytes:
    """Encode array as raw bytes with metadata.

    Args:
        arr: NumPy array to encode.
        compress: Whether to compress the bytes.

    Returns:
        Bytes with embedded metadata.
    """
    # Create metadata
    metadata = ArrayMetadata(arr.shape, str(arr.dtype))
    metadata_json = json.dumps(metadata.to_dict()).encode("utf-8")
    metadata_size = len(metadata_json).to_bytes(4, "little")

    # Get array bytes
    arr_bytes = arr.tobytes()
    if compress:
        arr_bytes = zlib.compress(arr_bytes, level=9)

    # Combine metadata size + metadata + array bytes
    return metadata_size + metadata_json + arr_bytes


def encode_array_float16(arr: np.ndarray) -> bytes:
    """Encode float array as float16 for size reduction.

    Args:
        arr: NumPy array (should be float type).

    Returns:
        Encoded bytes with float16 data.
    """
    if not np.issubdtype(arr.dtype, np.floating):
        raise ValueError("Float16 encoding only supports floating point arrays")

    # Convert to float16
    arr_f16 = arr.astype(np.float16)

    # Store original dtype for reconstruction
    metadata = ArrayMetadata(arr.shape, str(arr.dtype), original_dtype=str(arr.dtype))

    # Encode
    metadata_json = json.dumps(metadata.to_dict()).encode("utf-8")
    metadata_size = len(metadata_json).to_bytes(4, "little")
    arr_bytes = zlib.compress(arr_f16.tobytes(), level=9)

    return metadata_size + metadata_json + arr_bytes


def encode_array_uint8_scaled(arr: np.ndarray) -> bytes:
    """Encode array by scaling to uint8 range.

    Args:
        arr: NumPy array to encode.

    Returns:
        Encoded bytes with scaling information.
    """
    # Find min/max for scaling
    if arr.size == 0:
        arr_min, arr_max = 0.0, 1.0
    else:
        arr_min = float(arr.min())
        arr_max = float(arr.max())

    # Avoid division by zero
    if arr_max == arr_min:
        arr_uint8 = np.zeros(arr.shape, dtype=np.uint8)
    else:
        # Scale to 0-255
        arr_normalized = (arr - arr_min) / (arr_max - arr_min)
        arr_uint8 = (arr_normalized * 255).astype(np.uint8)

    # Store metadata for reconstruction
    metadata = ArrayMetadata(arr.shape, str(arr.dtype), min_value=arr_min, max_value=arr_max, original_dtype=str(arr.dtype))

    # Encode
    metadata_json = json.dumps(metadata.to_dict()).encode("utf-8")
    metadata_size = len(metadata_json).to_bytes(4, "little")
    arr_bytes = zlib.compress(arr_uint8.tobytes(), level=9)

    return metadata_size + metadata_json + arr_bytes


def encode_numpy_to_bytes(arr: np.ndarray, format: NumpyFormat | None = None, optimize: bool = True) -> bytes:
    """Encode numpy array to bytes using specified or optimal format.

    Args:
        arr: NumPy array to encode.
        format: Encoding format. If None, automatically selected.
        optimize: Whether to analyze and optimize encoding.

    Returns:
        Encoded bytes.
    """
    # Auto-select format if not specified
    if format is None and optimize:
        stats = analyze_array(arr)
        format = stats["recommended_format"]
    elif format is None:
        format = NumpyFormat.NPZ_COMPRESSED

    # Encode based on format
    if format == NumpyFormat.NPZ_COMPRESSED:
        return encode_array_npz(arr, compressed=True)
    elif format == NumpyFormat.NPY:
        return encode_array_npy(arr)
    elif format == NumpyFormat.PICKLE:
        return encode_array_pickle(arr)
    elif format == NumpyFormat.BYTES_RAW:
        return encode_array_bytes(arr, compress=False)
    elif format == NumpyFormat.BYTES_COMPRESSED:
        return encode_array_bytes(arr, compress=True)
    elif format == NumpyFormat.FLOAT16:
        return encode_array_float16(arr)
    elif format == NumpyFormat.UINT8_SCALED:
        return encode_array_uint8_scaled(arr)
    else:
        raise ValueError(f"Bytes encoding not supported for format: {format}")


def encode_numpy_to_string(arr: np.ndarray, format: NumpyFormat | None = None, optimize: bool = True, decimals: int | None = None) -> str:
    """Encode numpy array to base64 string using specified or optimal format.

    Args:
        arr: NumPy array to encode.
        format: Encoding format. If None, automatically selected.
        optimize: Whether to analyze and optimize encoding.
        decimals: For JSON formats, number of decimal places.

    Returns:
        Base64 encoded string or JSON string.
    """
    # Handle JSON formats specially
    if format == NumpyFormat.JSON_FULL:
        return encode_array_json(arr, decimals=None)
    elif format == NumpyFormat.JSON_ROUNDED:
        return encode_array_json(arr, decimals=decimals or 6)

    # For binary formats, encode to bytes then base64
    arr_bytes = encode_numpy_to_bytes(arr, format=format, optimize=optimize)
    return base64.b64encode(arr_bytes).decode("utf-8")


def decode_numpy_from_bytes(data: bytes, format: NumpyFormat) -> np.ndarray:
    """Decode bytes back to numpy array.

    Args:
        data: Encoded bytes.
        format: Format used for encoding.

    Returns:
        Decoded numpy array.
    """
    if format in [NumpyFormat.NPZ_COMPRESSED, NumpyFormat.NPY]:
        buffer = io.BytesIO(data)
        if format == NumpyFormat.NPZ_COMPRESSED:
            with np.load(buffer) as npz:
                return npz["array"]
        else:
            return np.load(buffer, allow_pickle=False)

    elif format == NumpyFormat.PICKLE:
        return pickle.loads(data)

    elif format in [NumpyFormat.BYTES_RAW, NumpyFormat.BYTES_COMPRESSED, NumpyFormat.FLOAT16, NumpyFormat.UINT8_SCALED]:
        # Extract metadata
        metadata_size = int.from_bytes(data[:4], "little")
        metadata_json = data[4 : 4 + metadata_size].decode("utf-8")
        metadata = ArrayMetadata.from_dict(json.loads(metadata_json))
        arr_bytes = data[4 + metadata_size :]

        # Decompress if needed
        if format in [NumpyFormat.BYTES_COMPRESSED, NumpyFormat.FLOAT16, NumpyFormat.UINT8_SCALED]:
            arr_bytes = zlib.decompress(arr_bytes)

        # Reconstruct array
        if format == NumpyFormat.FLOAT16:
            # Load as float16 then convert to original dtype
            arr_f16 = np.frombuffer(arr_bytes, dtype=np.float16).reshape(metadata.shape)
            return arr_f16.astype(metadata.extra.get("original_dtype", "float32"))

        elif format == NumpyFormat.UINT8_SCALED:
            # Load uint8 and scale back
            arr_uint8 = np.frombuffer(arr_bytes, dtype=np.uint8).reshape(metadata.shape)
            min_val = metadata.extra["min_value"]
            max_val = metadata.extra["max_value"]

            if max_val == min_val:
                return np.full(metadata.shape, min_val, dtype=metadata.extra["original_dtype"])

            # Scale back to original range
            arr_normalized = arr_uint8.astype(np.float64) / 255.0
            arr_scaled = arr_normalized * (max_val - min_val) + min_val
            return arr_scaled.astype(metadata.extra["original_dtype"])

        else:
            # Direct reconstruction
            return np.frombuffer(arr_bytes, dtype=metadata.dtype).reshape(metadata.shape)

    else:
        raise ValueError(f"Decoding not supported for format: {format}")


def decode_numpy_from_string(encoded: str, format: NumpyFormat) -> np.ndarray:
    """Decode base64 string back to numpy array.

    Args:
        encoded: Base64 encoded string or JSON string.
        format: Format used for encoding.

    Returns:
        Decoded numpy array.
    """
    # Handle JSON formats
    if format in [NumpyFormat.JSON_FULL, NumpyFormat.JSON_ROUNDED]:
        data = json.loads(encoded)
        arr = np.array(data["data"], dtype=data["dtype"])
        return arr.reshape(data["shape"])

    # For binary formats, decode base64 then bytes
    arr_bytes = base64.b64decode(encoded)
    return decode_numpy_from_bytes(arr_bytes, format)


def get_encoding_stats(arr: np.ndarray) -> dict[str, Any]:
    """Get encoding statistics for all formats.

    Args:
        arr: NumPy array to analyze.

    Returns:
        Dictionary with size statistics for each format.
    """
    original_size = arr.nbytes
    stats = {"array_info": analyze_array(arr), "original_size_bytes": original_size, "formats": {}}

    # Test each format
    for format in NumpyFormat:
        try:
            if format in [NumpyFormat.JSON_FULL, NumpyFormat.JSON_ROUNDED]:
                encoded = encode_numpy_to_string(arr, format=format, decimals=6)
                size = len(encoded.encode("utf-8"))
            else:
                encoded_bytes = encode_numpy_to_bytes(arr, format=format, optimize=False)
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
def encode_numpy_efficient(arr: np.ndarray, output: str = "string") -> str | bytes:
    """Encode array using the most efficient format automatically.

    Args:
        arr: NumPy array to encode.
        output: "string" for base64 or "bytes" for raw bytes.

    Returns:
        Encoded array in the most efficient format.
    """
    # Analyze array to find best format
    stats = analyze_array(arr)
    format = stats["recommended_format"]

    if output == "string":
        return encode_numpy_to_string(arr, format=format)
    else:
        return encode_numpy_to_bytes(arr, format=format)


def encode_numpy_batch(arrays: list[np.ndarray], format: NumpyFormat | None = None, optimize: bool = True) -> list[str]:
    """Encode multiple arrays efficiently.

    Args:
        arrays: List of numpy arrays.
        format: Format to use (None for auto-selection per array).
        optimize: Whether to optimize each array individually.

    Returns:
        List of base64 encoded strings.
    """
    return [encode_numpy_to_string(arr, format=format, optimize=optimize) for arr in arrays]


def save_numpy_compressed(arr: np.ndarray, filepath: str, format: NumpyFormat | None = None) -> None:
    """Save numpy array to file with optimal compression.

    Args:
        arr: NumPy array to save.
        filepath: Path to save file.
        format: Format to use (None for auto-selection).
    """
    data = encode_numpy_to_bytes(arr, format=format, optimize=True)

    # Save format info in filename or as header
    with open(filepath, "wb") as f:
        # Write format identifier
        format_used = format or analyze_array(arr)["recommended_format"]
        f.write(format_used.value.encode("utf-8").ljust(32)[:32])
        f.write(data)


def load_numpy_compressed(filepath: str) -> np.ndarray:
    """Load numpy array from compressed file.

    Args:
        filepath: Path to compressed file.

    Returns:
        Loaded numpy array.
    """
    with open(filepath, "rb") as f:
        # Read format identifier
        format_str = f.read(32).decode("utf-8").strip()
        format = NumpyFormat(format_str)

        # Read data
        data = f.read()

    return decode_numpy_from_bytes(data, format)
