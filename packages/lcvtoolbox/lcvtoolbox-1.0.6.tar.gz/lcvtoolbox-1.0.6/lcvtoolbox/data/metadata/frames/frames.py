import json
import logging
from pathlib import Path

from lcvtoolbox.core.schemas import (
    CameraDistortionSchema,
    CameraMatrixSchema,
    FrameMetadata,
    GPSPoint,
    ImageMetadata,
    PoseRPYSchema,
)

logger = logging.getLogger(__name__)


class FramesMetadata:
    """
    Metadata class for frames metadata.
    It is usually stored in a JSON file.
    """

    def __init__(self, data: list[FrameMetadata] | None = None):
        self.data: list[FrameMetadata] = data if data else self.load_data()
        self.using_example: bool = False

    def load_data(
        self,
        source: Path | str | list | None = None,
        fallback_to_example: bool = True,
    ) -> list[FrameMetadata]:
        """
        Load frame metadata from a JSON file or a list of dictionaries.
        """
        # TODO : add the possibility to download the file from a URL or an Azure Blob Storage
        if source is None:
            if fallback_to_example:
                # Use the local example.json file if no path is provided
                source = Path(__file__).parent / "example.json"
                self.using_example = True
                logger.error(f"No path provided, using default example.json at {source}")
            else:
                raise ValueError("No path provided for frames metadata loading and fallback to example is disabled.")
        elif isinstance(source, list):
            # If a list is provided, assume it is already in the correct format
            return [FrameMetadata(**item) for item in source]
        with open(source, encoding="utf-8") as f:
            data = json.load(f)
        return [FrameMetadata(**item) for item in data]

    def find_image_by_index(self, index: int) -> ImageMetadata | None:
        """
        Find an image by its index.
        Warning : "image.frame_index" is the index of the frame in the video, not the index in the list.
        """
        if self.using_example:
            logger.warning("Using example data, the index may not match the actual data.")
            image = self.data[0].images[0] if self.data else None
            if image is None:
                logger.error("No example data.")
                return None
            gps_point = self.data[0].gps_point
            if gps_point:
                image.gps_point = gps_point
            image.extraction_index = index
            return image
        current_index: int = 0
        for frame in self.data:
            gps_point = frame.gps_point
            for image in frame.images:
                if current_index == index:
                    image.gps_point = gps_point  # Attach GPS point to the image
                    image.extraction_index = index  # Attach extraction index to the image
                    return image
                current_index += 1
        return None

    @staticmethod
    def get_camera_matrix(image: ImageMetadata) -> CameraMatrixSchema | None:
        """
        Get the camera matrix from the image metadata.
        """
        if not image or not image.matrix:
            logger.error("Image or camera matrix is missing.")
            return None
        return image.matrix

    @staticmethod
    def get_distortion_coefficients(image: ImageMetadata) -> CameraDistortionSchema | None:
        """
        Get the distortion coefficients from the image metadata.
        """
        if not image or not image.dist_coeffs:
            logger.error("Image or distortion coefficients are missing.")
            return None
        return image.dist_coeffs

    @staticmethod
    def get_camera_pose(image: ImageMetadata) -> PoseRPYSchema | None:
        """
        Get the camera pose from the image metadata.
        """
        if not image or not image.pose:
            logger.error("Image or camera pose is missing.")
            return None
        return image.pose

    @staticmethod
    def get_gps_point(image: ImageMetadata) -> GPSPoint | None:
        """
        Get the GPS point from the image metadata.
        """
        if not image or not image.gps_point:
            logger.error("Image or GPS point is missing.")
            return None
        return image.gps_point
