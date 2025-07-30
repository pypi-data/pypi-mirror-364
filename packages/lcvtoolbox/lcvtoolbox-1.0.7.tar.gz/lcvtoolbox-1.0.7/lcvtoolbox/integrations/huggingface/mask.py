from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict

import numpy as np
from pycocotools import mask as coco_mask


class EncodedRLE(TypedDict):
    """Type definition for COCO RLE format."""
    size: List[int]  # [height, width]
    counts: bytes | str


@dataclass
class HuggingFaceMask:
    """
    Represents a mask for Hugging Face datasets.
    This class is used to define the structure of a mask in the Hugging Face dataset format.
    """

    width: int
    height: int
    encoded_rle: str
    bbox: List[int] | None = None

    def __post_init__(self) -> None:
        """
        Post-initialization method to set the bounding box if not provided.
        """
        if self.bbox is None:
            self.bbox = self.create_bbox()

    @property
    def coco_rle(self) -> EncodedRLE:
        """
        Convert the encoded RLE string to a COCO RLE format.
        """
        rle: EncodedRLE = {
            "size": [self.height, self.width],
            "counts": self.encoded_rle.encode("ascii") if isinstance(self.encoded_rle, str) else self.encoded_rle,
        }
        return rle

    ### Alternative constructors ###

    @classmethod
    def from_coco_rle(cls, rle: EncodedRLE) -> "HuggingFaceMask":
        """
        Create a HuggingFaceMask instance from a COCO RLE.
        This method extracts the width, height, and encoded RLE from the COCO RLE format.
        """
        if not isinstance(rle, dict) or "size" not in rle or "counts" not in rle:
            raise ValueError("Invalid COCO RLE format.")

        height, width = rle["size"]
        counts = rle["counts"]

        encoded_rle: str
        if isinstance(counts, bytes):
            encoded_rle = counts.decode("ascii")
        else:
            encoded_rle = str(counts)

        return cls(
            width=width,
            height=height,
            encoded_rle=encoded_rle,
            bbox=None,  # BBox will be created in __post_init__
        )

    @classmethod
    def from_array(cls, array: np.ndarray) -> "HuggingFaceMask":
        """
        Create a HuggingFaceMask instance from a numpy array.
        This method encodes the array to COCO RLE format and initializes the mask.
        """
        rle = cls.array_as_coco_rle(array)
        return cls.from_coco_rle(rle)

    ### Calculation methods ###

    @staticmethod
    def array_as_coco_rle(array: np.ndarray) -> EncodedRLE:
        """
        Convert a numpy array to COCO RLE format.
        """
        rle = coco_mask.encode(np.asfortranarray(array.astype(np.uint8)))
        return rle

    @staticmethod
    def coco_rle_as_serializable(rle: EncodedRLE) -> Dict[str, List[int] | str]:
        """Convert a COCO RLE to a serializable format."""
        # Convert bytes to a serializable format (base64)
        return {
            "size": rle["size"],
            "counts": rle["counts"].decode("ascii")
            if isinstance(rle["counts"], bytes)
            else rle["counts"],  # Encode bytes to string # type: ignore
        }

    def create_bbox(self) -> List[int]:
        """
        Create a bounding box from the RLE encoded mask.
        The bounding box is defined as [x_min, y_min, width, height].
        """
        bbox = coco_mask.toBbox(self.coco_rle).tolist()
        return [
            int(bbox[0]),  # x_min
            int(bbox[1]),  # y_min
            int(bbox[2]),  # width
            int(bbox[3]),  # height
        ]

    def as_array(self) -> np.ndarray:
        """
        Decode the RLE encoded mask into a numpy array.
        """
        mask = coco_mask.decode(self.coco_rle)
        return mask
