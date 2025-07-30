"""Holds the annotations for a single image in a CVAT project."""

import io

from PIL import Image

from lcvtoolbox.integrations.cvat.api.api_requests import CvatApi
from lcvtoolbox.core.schemas import CvatApiShape, CvatApiTag


class AnnotatedImage:
    """Represents an annotated image in a CVAT project."""

    def __init__(
        self,
        cvat_api: CvatApi,
        project_id: int,
        task_id: int,
        frame_number: int,
        shapes: list[CvatApiShape] | None = None,
        tags: list[CvatApiTag] | None = None,
    ):
        self.cvat_api: CvatApi = cvat_api
        self.project_id: int = project_id
        self.task_id: int = task_id
        self.frame_number: int = frame_number
        self.shapes: list[CvatApiShape] = shapes if shapes is not None else []
        self.tags: list[CvatApiTag] = tags if tags is not None else []

        # Cache for the image
        self._image: Image.Image | None = None

    @property
    def image(self) -> Image.Image:
        """Returns the image associated with this annotated image."""
        if self._image is None:
            image_bytes = self.cvat_api.download_task_image(
                task_id=self.task_id,
                frame_number=self.frame_number,
            )
            self._image = Image.open(io.BytesIO(image_bytes))
            if self._image is None:
                raise ValueError(f"Failed to load image {self.frame_number} from task {self.task_id}.")
        return self._image

    def close_image(self):
        """Erase the cached image. Ensure memory is freed."""
        if self._image is not None:
            self._image.close()
        self._image = None
