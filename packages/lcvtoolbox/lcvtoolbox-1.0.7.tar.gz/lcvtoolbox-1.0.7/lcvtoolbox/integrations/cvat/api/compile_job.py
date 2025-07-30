from collections.abc import Callable
from typing import Any

from PIL import Image

from lcvtoolbox.integrations.cvat.api.api_requests import CvatApi
from lcvtoolbox.integrations.cvat.api.compile_annotated_image import AnnotatedImage
from lcvtoolbox.core.schemas import (
    CvatApiJobAnnotations,
    CvatApiJobDetails,
    CvatApiJobMediasMetainformation,
    CvatApiMetainformationFrame,
    CvatApiShape,
    CvatApiTag,
    CvatApiTaskDetails,
)


class CvatJob:
    """Compile all information about a job and provided structured data."""

    def __init__(self, cvat_api: CvatApi, job_id: int):
        self.cvat_api: CvatApi = cvat_api
        self.job_id: int = job_id

        ### Cache for raw data from the API ###
        self._annotations: CvatApiJobAnnotations | None = None
        self._metainformation: CvatApiJobMediasMetainformation | None = None
        self._details: CvatApiJobDetails | None = None
        self._task_details: CvatApiTaskDetails | None = None  # Parent task details
        self._annotated_images: list[AnnotatedImage] | None = None

    ### Cache for data from the API ###

    @property
    def annotations(self) -> CvatApiJobAnnotations:
        """Get annotations for the job."""
        if self._annotations is None:
            # Fetch annotations from the API
            self._annotations = self.cvat_api.get_job_annotations(self.job_id)
        return self._annotations

    @property
    def metainformation(self) -> CvatApiJobMediasMetainformation:
        """Get media metainformation for the job."""
        if self._metainformation is None:
            # Fetch metainformation from the API
            self._metainformation = self.cvat_api.get_job_media_metainformation(self.job_id)
        return self._metainformation

    @property
    def details(self) -> CvatApiJobDetails:
        """Get details for the job."""
        if self._details is None:
            # Fetch details from the API
            self._details = self.cvat_api.get_job_details(self.job_id)
        return self._details

    @property
    def task_details(self) -> CvatApiTaskDetails:
        """Get details for the parent task of the job."""
        if self._task_details is None:
            # Fetch task details from the API
            self._task_details = self.cvat_api.get_task_details(self.details.task_id)
        return self._task_details

    @property
    def annotated_images(self) -> list[AnnotatedImage]:
        """Create annotated images for the job."""
        if self._annotated_images is None:
            # Create annotated images from the job annotations
            self._annotated_images = self.create_annotated_images()
        return self._annotated_images

    ### Shortcuts to access fields ###

    @property
    def task_id(self) -> int:
        """Get the task ID associated with the job."""
        return self.details.task_id

    @property
    def project_id(self) -> int:
        """Get the project ID associated with the job."""
        return self.task_details.project_id

    @property
    def frames(self) -> list[CvatApiMetainformationFrame]:
        """Get the list of frames for the job."""
        return self.metainformation.frames

    ### Computed fields ###

    @property
    def length(self) -> int:
        """Get the number of frames in the job."""
        return self.metainformation.stop_frame - self.metainformation.start_frame + 1

    def __len__(self) -> int:
        """Get the number of frames in the job."""
        return self.length

    @property
    def frames_names(self) -> list[str]:
        """Get the names of the frames in the job."""
        return [frame.name for frame in self.frames]

    @property
    def frames_numbers(self) -> list[int]:
        """List ids as a continuous range from start_frame to stop_frame."""
        return list(range(self.metainformation.start_frame, self.metainformation.stop_frame + 1))

    ### Actions ###

    def download_images(self, save_dir: str) -> list[str]:
        """Download all images from the job."""
        frame_count = len(self.frames)
        saved_files = []

        for frame_idx in range(frame_count):
            try:
                frame_number = self.metainformation.start_frame + frame_idx
                file_path = self.cvat_api.download_job_image(self.job_id, frame_number, save_dir)
                saved_files.append(file_path)
            except Exception as e:
                self.cvat_api.logger.error(f"❌ Failed to download frame {frame_idx} from job {self.job_id}: {e}")

        return saved_files

    def get_image(self, frame_number: int) -> Image.Image:
        """Download a specific frame from the job."""
        image_bytes = self.cvat_api.download_job_image(job_id=self.job_id, frame_number=frame_number, quality="original")
        if image_bytes is None:
            raise ValueError(f"Failed to download image for frame {frame_number} in job {self.job_id}")
        return Image.open(image_bytes)

    ### Process the job annotations ###

    def get_shapes_for_frame(self, frame_number: int) -> list[CvatApiShape]:
        """Get shapes for a specific frame in the job."""
        annotations = self.annotations
        if annotations is None:
            raise ValueError(f"No annotations found for job {self.job_id}")
        return [shape for shape in annotations.shapes if shape.frame == frame_number]

    def get_tags_for_frame(self, frame_number: int) -> list[CvatApiTag]:
        """Get tags for a specific frame in the job."""
        annotations = self.annotations
        if annotations is None:
            raise ValueError(f"No annotations found for job {self.job_id}")
        return [tag for tag in annotations.tags if tag.frame == frame_number]

    def create_annotated_images(self) -> list[AnnotatedImage]:
        """Create annotated images for the job."""
        annotated_images = []
        for frame_number in self.frames_numbers:
            shapes = self.get_shapes_for_frame(frame_number)
            tags = self.get_tags_for_frame(frame_number)
            annotated_image = AnnotatedImage(
                cvat_api=self.cvat_api,
                project_id=self.project_id,
                task_id=self.task_id,
                frame_number=frame_number,
                shapes=shapes,
                tags=tags,
            )
            annotated_images.append(annotated_image)
        return annotated_images

    def process(self, action: Callable[[AnnotatedImage], Any]) -> list:
        """Process the job to ensure all data is loaded and ready."""
        outputs: list = []
        for annotated_image in self.annotated_images:
            output = action(annotated_image)
            outputs.append(output)
            annotated_image.close_image()
        return outputs
