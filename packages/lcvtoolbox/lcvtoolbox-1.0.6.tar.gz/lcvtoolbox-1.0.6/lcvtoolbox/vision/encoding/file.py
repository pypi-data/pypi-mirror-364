### Encode any file to a string for API transfer"""


import base64
import gzip
import os
from typing import Any


def encode_file_to_string(file_path: str, compress: bool = False, max_size_mb: float | None = None) -> str:
    """Encode a file to a base64 string with optional compression.

    This function is designed for API transfer, converting binary files to
    text-safe base64 strings that can be included in JSON payloads.

    Args:
        file_path: Path to the file to encode.
        compress: If True, compress the file content using gzip before encoding.
                 Defaults to False. Compression can significantly reduce size
                 for text files but may not help much for already compressed
                 formats (jpg, png, zip, etc.).
        max_size_mb: Maximum file size in megabytes. If specified, raises
                    ValueError if file exceeds this size. Useful for API limits.

    Returns:
        Base64 encoded string representation of the file contents.
        If compression is enabled, the content is compressed before encoding.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If file size exceeds max_size_mb (if specified).

    Example:
        >>> # Encode a small text file
        >>> encoded = encode_file_to_string("document.txt", compress=True)
        >>>
        >>> # Encode with size limit for API that accepts max 10MB
        >>> encoded = encode_file_to_string("image.jpg", max_size_mb=10)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file size if limit is specified
    if max_size_mb is not None:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)")

    with open(file_path, "rb") as file:
        file_content = file.read()

    if compress:
        file_content = gzip.compress(file_content)

    return base64.b64encode(file_content).decode("utf-8")


def get_file_metadata(file_path: str, encoded_string: str) -> dict[str, Any]:
    """Get metadata about the file and its encoded representation.

    Useful for including additional information in API requests.

    Args:
        file_path: Path to the original file.
        encoded_string: The base64 encoded string from encode_file_to_string.

    Returns:
        Dictionary containing file metadata including:
        - filename: Name of the file
        - original_size_bytes: Size of original file in bytes
        - encoded_size_bytes: Size of encoded string in bytes
        - compression_ratio: Ratio of encoded to original size
        - mime_type: Guessed MIME type (basic implementation)
    """
    original_size = os.path.getsize(file_path)
    encoded_size = len(encoded_string.encode("utf-8"))
    filename = os.path.basename(file_path)

    # Basic MIME type detection
    ext = os.path.splitext(filename)[1].lower()
    mime_types = {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".json": "application/json",
        ".xml": "application/xml",
        ".csv": "text/csv",
        ".zip": "application/zip",
    }
    mime_type = mime_types.get(ext, "application/octet-stream")

    return {
        "filename": filename,
        "original_size_bytes": original_size,
        "encoded_size_bytes": encoded_size,
        "compression_ratio": encoded_size / original_size if original_size > 0 else 0,
        "mime_type": mime_type,
    }


def decode_string_to_bytes(encoded_string: str, compressed: bool | None = None) -> bytes:
    """Decode a base64 string back to bytes with automatic decompression.

    This function reverses the encoding done by encode_file_to_string,
    converting the base64 string back to its original binary form.

    Args:
        encoded_string: Base64 encoded string to decode.
        compressed: Whether the data is gzip compressed. If None (default),
                   automatically detects compression by checking for gzip
                   magic number. Set to True/False to force behavior.

    Returns:
        The decoded bytes, decompressed if necessary.

    Raises:
        ValueError: If the string is not valid base64.
        gzip.BadGzipFile: If compressed=True but data is not valid gzip.

    Example:
        >>> # Decode a string that was encoded without compression
        >>> encoded = encode_file_to_string("image.jpg")
        >>> decoded_bytes = decode_string_to_bytes(encoded)
        >>>
        >>> # Decode a string that was encoded with compression
        >>> encoded = encode_file_to_string("document.txt", compress=True)
        >>> decoded_bytes = decode_string_to_bytes(encoded)
        >>>
        >>> # Save decoded bytes to a new file
        >>> with open("output.jpg", "wb") as f:
        ...     f.write(decoded_bytes)
    """
    try:
        decoded_data = base64.b64decode(encoded_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}")

    # Auto-detect compression if not specified
    if compressed is None:
        # Check for gzip magic number (1f 8b)
        compressed = len(decoded_data) >= 2 and decoded_data[0] == 0x1F and decoded_data[1] == 0x8B

    if compressed:
        try:
            decoded_data = gzip.decompress(decoded_data)
        except gzip.BadGzipFile:
            if compressed is True:  # Only raise if explicitly told it's compressed
                raise
            # If auto-detected, just return the data as-is
            pass

    return decoded_data


def decode_string_to_file(encoded_string: str, output_path: str, compressed: bool | None = None) -> None:
    """Decode a base64 string and save it to a file.

    Convenience function that combines decode_string_to_bytes with file writing.

    Args:
        encoded_string: Base64 encoded string to decode.
        output_path: Path where the decoded file should be saved.
        compressed: Whether the data is gzip compressed. If None (default),
                   automatically detects compression.

    Example:
        >>> # Decode and save to file
        >>> encoded = encode_file_to_string("original.pdf", compress=True)
        >>> decode_string_to_file(encoded, "decoded.pdf")
    """
    decoded_bytes = decode_string_to_bytes(encoded_string, compressed)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as file:
        file.write(decoded_bytes)
