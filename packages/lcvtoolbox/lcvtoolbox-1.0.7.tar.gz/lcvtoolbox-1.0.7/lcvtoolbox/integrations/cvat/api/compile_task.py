from collections.abc import Callable
from typing import Any

from PIL import Image

from lcvtoolbox.integrations.cvat.api.api_requests import CvatApi
from lcvtoolbox.integrations.cvat.api.compile_annotated_image import AnnotatedImage
from lcvtoolbox.integrations.cvat.api.compile_job import CvatJob
from lcvtoolbox.core.schemas import (
    CvatApiJobDetails,
    CvatApiMetainformationFrame,
    CvatApiShape,
    CvatApiTag,
    CvatApiTaskAnnotations,
    CvatApiTaskDetails,
    CvatApiTaskMediasMetainformation,
)


class CvatTask:
    """Compile all information about a task and provide structured data."""

    def __init__(self, cvat_api: CvatApi, task_id: int):
        self.cvat_api: CvatApi = cvat_api
        self.task_id: int = task_id

        ### Cache for raw data from the API ###
        self._annotations: CvatApiTaskAnnotations | None = None
        self._metainformation: CvatApiTaskMediasMetainformation | None = None
        self._details: CvatApiTaskDetails | None = None
        self._jobs: list[CvatJob] | None = None
        self._annotated_images: list[AnnotatedImage] | None = None

    ### Cache for data from the API ###

    @property
    def annotations(self) -> CvatApiTaskAnnotations:
        """Get annotations for the task."""
        if self._annotations is None:
            # Fetch annotations from the API
            self._annotations = self.cvat_api.get_task_annotations(self.task_id)
        return self._annotations

    @property
    def metainformation(self) -> CvatApiTaskMediasMetainformation:
        """Get media metainformation for the task."""
        if self._metainformation is None:
            # Fetch metainformation from the API
            self._metainformation = self.cvat_api.get_task_media_metainformation(self.task_id)
        return self._metainformation

    @property
    def details(self) -> CvatApiTaskDetails:
        """Get details for the task."""
        if self._details is None:
            # Fetch details from the API
            self._details = self.cvat_api.get_task_details(self.task_id)
        return self._details

    @property
    def jobs(self) -> list[CvatJob]:
        """Get all jobs in the task."""
        if self._jobs is None:
            # Create CvatJob instances from task segments
            self._jobs = []
            for job_details in self.details.segments:
                job = CvatJob(self.cvat_api, job_details.id)
                self._jobs.append(job)
        return self._jobs

    @property
    def annotated_images(self) -> list[AnnotatedImage]:
        """Create annotated images for the task."""
        if self._annotated_images is None:
            # Create annotated images from the task annotations
            self._annotated_images = self.create_annotated_images()
        return self._annotated_images

    ### Shortcuts to access fields ###

    @property
    def project_id(self) -> int:
        """Get the project ID associated with the task."""
        return self.details.project_id

    @property
    def name(self) -> str:
        """Get the name of the task."""
        return self.details.name

    @property
    def status(self) -> str:
        """Get the status of the task."""
        return self.details.status

    @property
    def owner(self) -> str:
        """Get the owner of the task."""
        return self.details.owner

    @property
    def assignee(self) -> str | None:
        """Get the assignee of the task."""
        return self.details.assignee

    @property
    def frames(self) -> list[CvatApiMetainformationFrame]:
        """Get the list of frames for the task."""
        return self.metainformation.frames

    @property
    def job_ids(self) -> list[int]:
        """Get the list of job IDs in the task."""
        return [job.job_id for job in self.jobs]

    @property
    def job_details(self) -> list[CvatApiJobDetails]:
        """Get the list of job details in the task."""
        return self.details.segments

    ### Computed fields ###

    @property
    def length(self) -> int:
        """Get the number of frames in the task."""
        return self.metainformation.stop_frame - self.metainformation.start_frame + 1

    def __len__(self) -> int:
        """Get the number of frames in the task."""
        return self.length

    @property
    def job_count(self) -> int:
        """Get the number of jobs in the task."""
        return len(self.jobs)

    @property
    def frames_names(self) -> list[str]:
        """Get the names of the frames in the task."""
        return [frame.name for frame in self.frames]

    @property
    def frames_numbers(self) -> list[int]:
        """List ids as a continuous range from start_frame to stop_frame."""
        return list(range(self.metainformation.start_frame, self.metainformation.stop_frame + 1))

    ### Actions ###

    def download_images(self, save_dir: str) -> list[str]:
        """Download all images from the task."""
        frame_count = len(self.frames)
        saved_files = []

        for frame_idx in range(frame_count):
            try:
                frame_number = self.metainformation.start_frame + frame_idx
                file_path = self.cvat_api.download_task_image(self.task_id, frame_number, save_dir)
                saved_files.append(file_path)
            except Exception as e:
                self.cvat_api.logger.error(f"❌ Failed to download frame {frame_idx} from task {self.task_id}: {e}")

        return saved_files

    def get_image(self, frame_number: int) -> Image.Image:
        """Download a specific frame from the task."""
        image_bytes = self.cvat_api.download_task_image(task_id=self.task_id, frame_number=frame_number, quality="original")
        if image_bytes is None:
            raise ValueError(f"Failed to download image for frame {frame_number} in task {self.task_id}")
        return Image.open(image_bytes)

    def get_job_by_id(self, job_id: int) -> CvatJob | None:
        """Get a specific job by its ID."""
        for job in self.jobs:
            if job.job_id == job_id:
                return job
        return None

    def get_job_by_frame(self, frame_number: int) -> CvatJob | None:
        """Get the job that contains a specific frame number."""
        for job in self.jobs:
            if job.details.start_frame <= frame_number <= job.details.stop_frame:
                return job
        return None

    ### Process the task annotations ###

    def get_shapes_for_frame(self, frame_number: int) -> list[CvatApiShape]:
        """Get shapes for a specific frame in the task."""
        annotations = self.annotations
        if annotations is None:
            raise ValueError(f"No annotations found for task {self.task_id}")
        return [shape for shape in annotations.shapes if shape.frame == frame_number]

    def get_tags_for_frame(self, frame_number: int) -> list[CvatApiTag]:
        """Get tags for a specific frame in the task."""
        annotations = self.annotations
        if annotations is None:
            raise ValueError(f"No annotations found for task {self.task_id}")
        return [tag for tag in annotations.tags if tag.frame == frame_number]

    def create_annotated_images(self) -> list[AnnotatedImage]:
        """Create annotated images for the task."""
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
        """Process the task to ensure all data is loaded and ready."""
        outputs: list = []
        for annotated_image in self.annotated_images:
            output = action(annotated_image)
            outputs.append(output)
            annotated_image.close_image()
        return outputs

    def process_jobs(self, action: Callable[[CvatJob], Any]) -> list:
        """Process each job in the task individually."""
        outputs: list = []
        for job in self.jobs:
            self.cvat_api.logger.info(f"🔍 Processing job {job.job_id} in task {self.task_id}...")
            output = action(job)
            outputs.append(output)
            self.cvat_api.logger.info(f"✅ Completed processing job {job.job_id}")
        return outputs

    def process_jobs_with_callback(self, action: Callable[[CvatJob], Any], callback: Callable[[int, CvatJob, Any], None] | None = None) -> list:
        """
        Process each job in the task individually with optional callback for progress tracking.

        Args:
            action: Function to apply to each job
            callback: Optional callback function called after each job is processed
                     with signature (job_index, job, result)

        Returns:
            List of results from processing each job
        """
        outputs: list = []
        total_jobs = len(self.jobs)

        for job_index, job in enumerate(self.jobs):
            self.cvat_api.logger.info(f"🔍 Processing job {job.job_id} ({job_index + 1}/{total_jobs}) in task {self.task_id}...")

            output = action(job)
            outputs.append(output)

            if callback is not None:
                callback(job_index, job, output)

            self.cvat_api.logger.info(f"✅ Completed processing job {job.job_id} ({job_index + 1}/{total_jobs})")

        return outputs

    def list_jobs(self) -> list[dict[str, Any]]:
        """List all jobs in the task with their basic information."""
        job_info = []
        for job in self.jobs:
            job_details = job.details
            job_info.append(
                {
                    "job_id": job.job_id,
                    "status": job_details.status,
                    "stage": job_details.stage,
                    "state": job_details.state,
                    "assignee": job_details.assignee,
                    "start_frame": job_details.start_frame,
                    "stop_frame": job_details.stop_frame,
                    "frame_count": job.length,
                    "created_date": job_details.created_date,
                    "updated_date": job_details.updated_date,
                }
            )
        return job_info

    def get_job_statistics(self) -> dict[str, Any]:
        """Get statistics about jobs in the task."""
        job_statuses = {}
        job_stages = {}
        job_states = {}
        total_frames = 0

        for job in self.jobs:
            details = job.details

            # Count statuses
            status = details.status
            job_statuses[status] = job_statuses.get(status, 0) + 1

            # Count stages
            stage = details.stage
            job_stages[stage] = job_stages.get(stage, 0) + 1

            # Count states
            state = details.state
            job_states[state] = job_states.get(state, 0) + 1

            # Sum frames
            total_frames += job.length

        return {
            "total_jobs": len(self.jobs),
            "total_frames": total_frames,
            "task_frames": self.length,
            "statuses": job_statuses,
            "stages": job_stages,
            "states": job_states,
        }

    def process_job_by_job_with_images(self, action: Callable[[CvatJob, list[AnnotatedImage]], Any]) -> list:
        """
        Process each job individually with its annotated images.

        Args:
            action: Function that takes a CvatJob and list of AnnotatedImages

        Returns:
            List of results from processing each job
        """
        outputs: list = []
        total_jobs = len(self.jobs)

        for job_index, job in enumerate(self.jobs):
            self.cvat_api.logger.info(f"🔍 Processing job {job.job_id} ({job_index + 1}/{total_jobs}) with images...")

            # Get annotated images for this job
            job_images = job.annotated_images

            # Process the job with its images
            output = action(job, job_images)
            outputs.append(output)

            # Clean up images to free memory
            for img in job_images:
                img.close_image()

            self.cvat_api.logger.info(f"✅ Completed processing job {job.job_id} ({job_index + 1}/{total_jobs})")

        return outputs
