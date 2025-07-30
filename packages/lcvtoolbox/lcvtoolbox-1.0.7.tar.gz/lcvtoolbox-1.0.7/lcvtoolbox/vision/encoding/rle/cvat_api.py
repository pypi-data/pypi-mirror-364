"""Handle RLE encoding for CVAT API format.
Note that these are different from the RLE used in CVAT export format.
"""

import logging
from functools import reduce

import numpy as np

logger = logging.getLogger(__name__)


class CvatApiRLE:
    """
    Class to handle RLE encoding for CVAT API format.

    CVAT API RLE format consists of run-length encoded values followed by
    bounding box coordinates: [rle_values..., left, top, right, bottom]
    """

    BBOX_LENGTH = 4

    def __init__(self, data: list[float]):
        """
        Initialize CvatApiRLE instance with RLE data.

        Args:
            data: List of floats in CVAT RLE format: [rle_values..., left, top, right, bottom]
        """
        self.data = data

    ##################################################
    ###   Main methods for encoding and decoding   ###
    ##################################################

    def encode(self) -> list[float]:
        """
        Encode into the CVAT API RLE format.

        Returns:
            List of floats in CVAT RLE format: [rle_values..., left, top, right, bottom]
        """
        return self.data

    def decode(self, width: int, height: int) -> np.ndarray:
        """
        Decode the RLE data from the CVAT API format to a numpy array.

        Args:
            width: Width of the full image
            height: Height of the full image

        Returns:
            numpy array of shape (height, width) with uint8 values

        Raises:
            ValueError: If RLE data is invalid or decoding fails
        """
        array = CvatApiRLE.rle_to_array(self.data, width, height)
        if array is None:
            raise ValueError(f"Invalid RLE data for decoding : {self.data}.")
        return array

    @classmethod
    def from_array(cls, array: np.ndarray) -> "CvatApiRLE":
        """
        Create a CvatApiRLE instance from a numpy array.

        Args:
            array: numpy array representing a binary mask

        Returns:
            CvatApiRLE instance with encoded data
        """
        rle_data = cls.array_to_rle(array)
        return cls(rle_data)

    @property
    def bbox(self) -> list[int] | None:
        """
        Get the bounding box of the shape annotation.

        Returns:
            List[int] | None: The bounding box in the format [left, top, right, bottom] or None if not available.
        """
        # The bounding box is stored in the last 4 elements of the RLE points
        cvat_rle = self.data

        if cvat_rle is None or len(cvat_rle) < self.BBOX_LENGTH:
            logger.warning(f"Invalid RLE data: {cvat_rle}. Expected at least {self.BBOX_LENGTH} elements.")
            return None
        # Extract the bounding box coordinates
        left = int(cvat_rle[-4])
        top = int(cvat_rle[-3])
        right = int(cvat_rle[-2])
        bottom = int(cvat_rle[-1])
        return [left, top, right, bottom]

    ####################################################
    ###   Helper methods for encoding and decoding   ###
    ####################################################

    @staticmethod
    def rle_to_array(data: list[float], width: int, height: int) -> np.ndarray | None:
        """
        Get the mask and convert it to a numpy array.

        Args:
            data: RLE data in CVAT format
            width: Image width
            height: Image height

        Returns:
            numpy array or None if decoding fails
        """

        # Check if cvat_rle is available
        if data is None:
            return None

        # Extract the metadata
        if len(data) < 4:
            logger.warning(f"Invalid RLE data: {data}. Expected at least 4 elements.")
            return None

        # Decode the RLE data
        mask = CvatApiRLE.decode_cvat_rle(data, width, height)
        if mask is None:
            logger.warning(f"Failed to decode RLE data: {data}.")
            return None

        return mask.astype(np.uint8)

    ### Static methods for RLE encoding/decoding ###

    @staticmethod
    def decode_cvat_rle(points: list[float], image_width: int, image_height: int) -> np.ndarray:
        """
        Decode CVAT RLE format to boolean numpy 2D mask array.

        Args:
            points: List containing RLE values + [left, top, right, bottom]
            image_width: Width of the full image
            image_height: Height of the full image

        Returns:
            numpy array of shape (image_height, image_width) with boolean values

        Note:
            The RLE data represents alternating runs of 0s and 1s, starting with 0s.
            The mask is decoded within the bounding box and then placed in the full image.
        """
        # Extract bounding box (last 4 elements)
        left, top, right, bottom = int(points[-4]), int(points[-3]), int(points[-2]), int(points[-1])

        # Extract RLE data (all elements except last 4)
        rle_data = points[:-4]

        # Calculate mask dimensions
        mask_width = right - left + 1
        mask_height = bottom - top + 1

        # Decode RLE to flat binary array
        flat_mask = []
        current_value = 0

        for run_length in rle_data:
            flat_mask.extend([current_value] * int(run_length))
            current_value = 1 - current_value  # Toggle between 0 and 1

        # Reshape to 2D mask
        mask_2d = np.array(flat_mask, dtype=bool).reshape(mask_height, mask_width)

        # Create full image mask
        full_mask = np.zeros((image_height, image_width), dtype=bool)
        full_mask[top : bottom + 1, left : right + 1] = mask_2d

        return full_mask

    @staticmethod
    def mask_to_rle(mask):
        """
        Convert a flattened boolean mask to RLE values.

        Args:
            mask: Flattened list or array of boolean/binary values

        Returns:
            List of run-length encoded values
        """

        def reducer(acc, item):
            idx, val = item
            if idx > 0:
                if mask[idx - 1] == val:
                    acc[-1] += 1
                else:
                    acc.append(1)
                return acc

            if val > 0:
                acc.extend([0, 1])
            else:
                acc.append(1)
            return acc

        return reduce(reducer, enumerate(mask), [])

    @staticmethod
    def to_cvat_mask(box: list[int], mask: np.ndarray) -> list[float]:
        """
        Convert numpy mask to CVAT RLE format.

        Args:
            box: [left, top, right, bottom] bounding box coordinates
            mask: numpy array of the full image mask

        Returns:
            List in CVAT format: [rle_values..., left, top, right, bottom]

        Note:
            This method extracts the region within the bounding box from the full mask,
            flattens it, and encodes it to RLE format with the bounding box appended.
        """
        xtl, ytl, xbr, ybr = box
        flattened = mask[ytl : ybr + 1, xtl : xbr + 1].flat[:].tolist()
        rle = CvatApiRLE.mask_to_rle(flattened)
        rle.extend([xtl, ytl, xbr, ybr])
        return rle

    @staticmethod
    def binary_mask_to_bbox(mask: np.ndarray) -> list[int]:
        """
        Compute the bounding box from a binary mask.

        Args:
            mask: numpy array representing a binary mask

        Returns:
            Bounding box as [left, top, right, bottom]
        """
        binary_mask = mask.astype(bool)
        rows, cols = np.where(binary_mask)
        top, bottom = rows.min(), rows.max()
        left, right = cols.min(), cols.max()
        return [left, top, right, bottom]

    ### Static helper methods for encoding ###

    @staticmethod
    def array_to_rle(array: np.ndarray) -> list[float]:
        """
        Encode a numpy array (binary mask) to CVAT API RLE format.

        Args:
            array: numpy array representing a binary mask

        Returns:
            List of floats in CVAT RLE format: [rle_values..., left, top, right, bottom]
        """
        # Ensure the array is binary
        binary_mask = CvatApiRLE._convert_to_binary_mask(array)

        # Check if mask is empty
        if not np.any(binary_mask):
            logger.warning("Empty mask provided for encoding")
            return []

        # Get bounding box
        bbox = CvatApiRLE._compute_bounding_box(binary_mask)

        # Encode the cropped region to RLE
        rle_data = CvatApiRLE._encode_region_to_rle(binary_mask, bbox)

        return rle_data

    @staticmethod
    def _convert_to_binary_mask(array: np.ndarray) -> np.ndarray:
        """
        Convert input array to binary mask.

        Args:
            array: Input array of any numeric type (bool, int, float)

        Returns:
            Binary mask as boolean numpy array

        Raises:
            ValueError: If array dtype is not supported

        Note:
            - Boolean arrays are returned as-is
            - Integer arrays: non-zero values become True
            - Float arrays: values > 0.5 become True
        """
        # Handle different input types
        if array.dtype == bool:
            return array
        elif np.issubdtype(array.dtype, np.integer):
            # Convert non-zero values to True
            return array > 0
        elif np.issubdtype(array.dtype, np.floating):
            # Use a threshold for floating point values
            return array > 0.5
        else:
            raise ValueError(f"Unsupported array dtype: {array.dtype}")

    @staticmethod
    def _compute_bounding_box(binary_mask: np.ndarray) -> list[int]:
        """
        Compute bounding box from binary mask.

        Args:
            binary_mask: Boolean numpy array representing the mask

        Returns:
            Bounding box as [left, top, right, bottom]

        Note:
            This is a wrapper around binary_mask_to_bbox for consistency
            in the encoding pipeline.
        """
        return CvatApiRLE.binary_mask_to_bbox(binary_mask)

    @staticmethod
    def _encode_region_to_rle(binary_mask: np.ndarray, bbox: list[int]) -> list[float]:
        """
        Encode the region within the bounding box to RLE format.

        Args:
            binary_mask: Full binary mask as numpy array
            bbox: Bounding box [left, top, right, bottom]

        Returns:
            RLE data in CVAT format: [rle_values..., left, top, right, bottom]

        Note:
            This method extracts the region within the bounding box and
            encodes only that region, which is more efficient than encoding
            the entire image.
        """
        return CvatApiRLE.to_cvat_mask(bbox, binary_mask)
