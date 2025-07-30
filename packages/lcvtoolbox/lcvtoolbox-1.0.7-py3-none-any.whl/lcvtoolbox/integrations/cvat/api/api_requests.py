import json
import logging
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import TypeVar, Any, Optional

import requests

from lcvtoolbox.core.schemas import (
    CvatApiJobAnnotations,
    CvatApiJobMediasMetainformation,
    CvatApiLabelDefinition,
    CvatApiTaskAnnotations,
    CvatApiTaskMediasMetainformation,
    CvatApiJobDetails,
    CvatApiTaskDetails,
)
from lcvtoolbox.core.utils.pretty import pretty

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    # New parameters for 502 errors
    retry_502: bool = True,
    max_502_retries: int = 10,
    initial_502_delay: float = 30.0,
    max_502_delay: float = 300.0,  # 5 minutes max delay for 502
):
    """
    Decorator that implements retry logic with exponential backoff.
    Special handling for 502 errors with longer delays.

    Args:
        max_retries: Maximum number of retry attempts for general errors
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays to prevent thundering herd
        retry_502: Whether to apply special retry logic for 502 errors
        max_502_retries: Maximum retries specifically for 502 errors
        initial_502_delay: Initial delay for 502 errors (longer than general)
        max_502_delay: Maximum delay for 502 errors
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            last_exception = None
            delay = initial_delay
            total_attempts = 0
            consecutive_502_errors = 0

            # Determine max attempts based on whether we're handling 502s specially
            effective_max_retries = max(max_retries, max_502_retries) if retry_502 else max_retries

            for attempt in range(effective_max_retries + 1):
                total_attempts += 1
                try:
                    result = func(self, *args, **kwargs)
                    # Reset 502 counter on success
                    consecutive_502_errors = 0
                    return result
                except (requests.Timeout, requests.ConnectionError, requests.RequestException) as e:
                    last_exception = e
                    self.logger.error(f"❌ Request failed with error: {str(e)}. Attempt {attempt + 1}/{effective_max_retries + 1}.")

                    # Special handling for 502 errors
                    if isinstance(e, requests.HTTPError) and e.response is not None:
                        if e.response.status_code == 502 and retry_502:
                            consecutive_502_errors += 1

                            # Check if we've exceeded 502-specific retries
                            if consecutive_502_errors > max_502_retries:
                                self.logger.error(f"❌ Max 502 retries ({max_502_retries}) reached for {func.__name__}. CVAT server appears to be having persistent issues.")
                                raise

                            # Use longer delays for 502 errors
                            delay = min(initial_502_delay * (exponential_base ** (consecutive_502_errors - 1)), max_502_delay)

                            self.logger.warning(f"⚠️ 502 Bad Gateway error (attempt {consecutive_502_errors}/{max_502_retries + 1}), CVAT server may be overloaded. Waiting {delay:.1f}s before retry...")
                        elif 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                            # Don't retry client errors except rate limiting
                            raise
                        else:
                            # Regular retry logic for other errors
                            if attempt >= max_retries:
                                self.logger.error(f"❌ Max retries ({max_retries}) reached for {func.__name__}")
                                raise

                            consecutive_502_errors = 0  # Reset 502 counter
                    else:
                        # Network errors - use regular retry logic
                        if attempt >= max_retries:
                            self.logger.error(f"❌ Max retries ({max_retries}) reached for {func.__name__}")
                            raise

                        consecutive_502_errors = 0  # Reset 502 counter

                    # Add jitter to prevent thundering herd
                    actual_delay = delay
                    if jitter:
                        import random

                        actual_delay = delay * (0.5 + random.random())

                    if consecutive_502_errors == 0:
                        # Regular error message
                        self.logger.warning(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {actual_delay:.1f}s... Error: {str(e)}")
                        # Calculate next delay with exponential backoff for regular errors
                        delay = min(delay * exponential_base, max_delay)

                    time.sleep(actual_delay)

            # This should never be reached, but just in case
            raise last_exception if last_exception else RuntimeError("Unexpected retry error")

        return wrapper

    return decorator


class CvatApi:
    """CvatApi class for interacting with the CVAT API."""

    def __init__(
        self,
        cvat_url: str,
        cvat_username: str,
        cvat_password: str,
        organization: str,
        cvat_auth_timeout: float = 30.0,
        cvat_api_timeout: float = 60.0,
    ):
        """
        Initialize the CVAT API client.
        
        Args:
            cvat_url: Base URL of the CVAT server
            cvat_username: Username for authentication
            cvat_password: Password for authentication
            organization: Organization name
            cvat_auth_timeout: Timeout for authentication requests in seconds
            cvat_api_timeout: Timeout for API requests in seconds
        """
        self.cvat_url = cvat_url
        self.cvat_username = cvat_username
        self.cvat_password = cvat_password
        self.organization = organization
        self.cvat_auth_timeout = cvat_auth_timeout
        self.cvat_api_timeout = cvat_api_timeout
        self.logger = logging.getLogger(__name__)
        self.cvat_token = self.get_auth_token()
        self.logger.info("🔑 CVAT API initialized.")

    # 🔹 Helper methods for common patterns
    def _get_headers(self, token: Optional[str] = None, with_organization: bool = True) -> dict[str, str]:
        """Create standard headers for API requests."""
        headers = {"Authorization": f"Token {token or self.cvat_token}"}
        if with_organization:
            headers["X-Organization"] = self.organization
        return headers

    def _handle_response_errors(self, response: requests.Response, error_prefix: str) -> None:
        """Handle common response errors with consistent logging."""
        if isinstance(response, requests.Response):
            self.logger.error(f"{error_prefix}: {response.status_code}")
            self.logger.error(f"❌ Response text:\n{json.dumps(response.text, indent=2) if response.text else 'No response text'}")

    def _make_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        resource_name: str,
        resource_id: Optional[int] = None,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
        response_model: Optional[type] = None,
    ) -> Any:
        """Make HTTP request with standard error handling."""
        timeout = timeout or self.cvat_api_timeout
        resource_desc = f"{resource_name} {resource_id}" if resource_id else resource_name
        
        self.logger.info(f"🔍 {method.upper()} request for {resource_desc}...")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            data = response.json() if response.content else {}
            
            self.logger.info(f"✅ Successfully retrieved {resource_desc}")
            if hasattr(self, 'logger') and self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"📊 Response data:\n{pretty(data)}")
            
            # Parse response with Pydantic model if provided
            if response_model:
                try:
                    return response_model(**data)
                except Exception as e:
                    self.logger.error(f"❌ Failed to parse response with {response_model.__name__}: {e}")
                    # Return raw data if parsing fails
                    return data
            
            return data
            
        except requests.Timeout as e:
            self.logger.error(f"❌ Timeout while retrieving {resource_desc}")
            raise TimeoutError(f"❌ Timeout while retrieving {resource_desc}.") from e
        except requests.HTTPError as e:
            self.logger.error(f"❌ HTTP Error while retrieving {resource_desc}: {e.response.status_code}")
            self._handle_response_errors(e.response, "❌ HTTP Error")
            raise ConnectionError(f"❌ Failed to retrieve {resource_desc}: {e.response.status_code} - {e.response.text}") from e
        except requests.RequestException as e:
            self.logger.error(f"❌ Network error while retrieving {resource_desc}: {e}")
            raise RuntimeError(f"❌ Network error while retrieving {resource_desc}.") from e
        except Exception as e:
            self.logger.error(f"❌ Error retrieving {resource_desc}: {e}")
            raise ValueError(f"❌ Error retrieving {resource_desc}: Invalid response from server.") from e

    # 🔹 Authentication: Get an authentication token
    def get_auth_token(self) -> str:
        """
        Authenticate with the CVAT server and return the token.
        """
        auth_url = f"{self.cvat_url}/api/auth/login"
        json_data = {
            "username": self.cvat_username,
            "password": self.cvat_password,
        }

        self.logger.info(f"🔍 Attempting authentication with CVAT server at {self.cvat_url}...")

        try:
            response = requests.post(auth_url, json=json_data, timeout=self.cvat_auth_timeout)
            response.raise_for_status()

            token = response.json().get("key")
            if not token:
                self.logger.error("❌ Authentication failed: No token received from the server")
                raise ValueError("❌ Authentication failed: No token received from the server.")

            self.logger.info("✅ Successfully authenticated with CVAT server")
            return token
        except requests.Timeout as e:
            self.logger.error("❌ Authentication request timed out")
            raise TimeoutError("❌ Authentication request timed out.") from e
        except requests.HTTPError as e:
            self.logger.error(f"❌ Authentication failed: {e.response.status_code}")
            self._handle_response_errors(e.response, "❌ Authentication failed")
            raise ConnectionError(f"❌ Authentication failed: {e.response.status_code} - {e.response.text}") from e
        except requests.RequestException as e:
            self.logger.error(f"❌ Authentication request failed due to a network error: {e}")
            raise RuntimeError("❌ Authentication request failed due to a network error.") from e
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            raise ValueError("❌ Authentication failed: Invalid response from server.") from e

    # 🔹 Retrieve all job IDs for a specific project (with organization context)
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_project_job_ids(self, project_id: int, token: str | None = None) -> list[int]:
        """
        Fetch all job IDs associated with a specific project.

        Args:
            project_id (int): The ID of the project to get jobs for
            token (str): Authentication token

        Returns:
            list: List of job IDs for the specified project
        """
        headers = self._get_headers(token)
        url = f"{self.cvat_url}/api/jobs?project_id={project_id}&page_size=1000&org={self.organization}"
        
        self.logger.info(f"🔍 Attempting to retrieve jobs for Project {project_id} in organization {self.organization}...")
        
        try:
            job_data = self._make_request("GET", url, headers, "jobs for project", project_id)
            
            self.logger.info(f"📊 Total results count: {job_data.get('count', 'unknown')}")
            
            # Extract job IDs from results
            job_ids = [job["id"] for job in job_data.get("results", [])]
            
            self.logger.info(f"✅ Successfully retrieved {len(job_ids)} job IDs for Project {project_id}")
            return job_ids
            
        except Exception as e:
            self.logger.error(f"❌ Error retrieving jobs: {e}")
            return []

    # 🔹 Retrieve Job Annotations
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_job_annotations(self, job_id: int, token: str | None = None) -> CvatApiJobAnnotations:
        """
        Fetch annotations for a specific job.
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/jobs/{job_id}/annotations"
        
        return self._make_request("GET", url, headers, "annotations for job", job_id, response_model=CvatApiJobAnnotations)

    # 🔹 Retrieve the list of labels for a given project id
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_project_labels(self, project_id: int, token: str | None = None) -> list[CvatApiLabelDefinition]:
        """
        Fetch all labels associated with a specific project.

        Args:
            project_id (int): The ID of the project to get labels for
            token (str): Authentication token

        Returns:
            list[CvatApiLabelDefinition]: List of label definitions for the specified project
        """
        headers = self._get_headers(token)
        url = f"{self.cvat_url}/api/labels?project_id={project_id}&page_size=1000&org={self.organization}"
        
        self.logger.info(f"🔍 Retrieving labels for project {project_id} in organization {self.organization}...")
        
        labels_data = self._make_request("GET", url, headers, "labels for project", project_id)
        
        self.logger.info(f"📊 Total results count: {labels_data.get('count', 'unknown')}")
        
        # Extract labels from results and parse them
        labels_raw = labels_data.get("results", [])
        labels = [CvatApiLabelDefinition(**label) for label in labels_raw]
        
        self.logger.info(f"✅ Successfully retrieved {len(labels)} labels for project {project_id}")
        return labels

    # 🔹 Retrieve details for a given label id
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_label_details(self, label_id: int, token: str | None = None) -> CvatApiLabelDefinition:
        """
        Retrieve details for a given label id
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/labels/{label_id}"
        
        return self._make_request("GET", url, headers, "label details", label_id, response_model=CvatApiLabelDefinition)

    # 🔹 Retrieve job details
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_job_details(self, job_id: int, token: str | None = None) -> CvatApiJobDetails:
        """
        Retrieve details for a specific job.

        Args:
            job_id (int): The ID of the job to get details for
            token (str): Authentication token

        Returns:
            CvatApiJobDetails: Job details including status, assignee, stage, state, etc.
        """
        headers = self._get_headers(token)
        url = f"{self.cvat_url}/api/jobs/{job_id}"
        
        return self._make_request("GET", url, headers, "job details", job_id, response_model=CvatApiJobDetails)

    # 🔹 Retrieve task details
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_task_details(self, task_id: int, token: str | None = None) -> CvatApiTaskDetails:
        """
        Retrieve details for a specific task.

        Args:
            task_id (int): The ID of the task to get details for
            token (str): Authentication token

        Returns:
            CvatApiTaskDetails: Task details including name, status, assignee, project_id, owner, etc.
        """
        headers = self._get_headers(token)
        url = f"{self.cvat_url}/api/tasks/{task_id}"
        
        return self._make_request("GET", url, headers, "task details", task_id, response_model=CvatApiTaskDetails)

    # 🔹 Retrieve Task Annotations
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_task_annotations(self, task_id: int, token: str | None = None) -> CvatApiTaskAnnotations:
        """
        Fetch annotations for a specific task.

        Args:
            task_id (int): The ID of the task to get annotations for
            token (str): Authentication token

        Returns:
            CvatApiTaskAnnotations: Task annotations data
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/tasks/{task_id}/annotations"
        
        return self._make_request("GET", url, headers, "annotations for task", task_id, response_model=CvatApiTaskAnnotations)

    # 🔹 Retrieve metainformation for media files in a task
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_task_media_metainformation(self, task_id: int, token: str | None = None) -> CvatApiTaskMediasMetainformation:
        """
        Retrieve metainformation for media files in a given task.

        Args:
            task_id (int): The ID of the task to get metainformation for
            token (str): Authentication token

        Returns:
            CvatApiTaskMediasMetainformation: Task media metainformation
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/tasks/{task_id}/data/meta"
        
        return self._make_request("GET", url, headers, "metainformation for task", task_id, response_model=CvatApiTaskMediasMetainformation)

    # 🔹 Download a specific image frame from a task
    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        max_delay=30.0,
        retry_502=True,
        max_502_retries=10,
        initial_502_delay=30.0,
        max_502_delay=300.0,
    )
    def download_task_image(self, task_id: int, frame_number: int, quality: str = "original", token: str | None = None) -> bytes:
        """
        Download a specific image frame from a task.

        Args:
            task_id (int): The ID of the task
            frame_number (int): The frame number to download (0-based index)
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            bytes: The image data as bytes
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/tasks/{task_id}/data"
        params = {"type": "frame", "number": frame_number, "quality": quality}
        
        return self._download_binary_data(
            url, headers, params,
            f"frame {frame_number} from task {task_id} (quality: {quality})"
        )

    # 🔹 Download all images from a task
    def download_task_images(self, task_id: int, output_dir: str | Path, quality: str = "original", token: str | None = None) -> list[str]:
        """
        Download all images from a task using metadata to determine frame count.

        Args:
            task_id (int): The ID of the task
            output_dir (str | Path): Directory to save images
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            list[str]: List of saved image file paths
        """
        if token is None:
            token = self.cvat_token

        # First get metadata to know how many frames exist
        try:
            metadata = self.get_task_media_metainformation(task_id, token)
            frame_count = len(metadata.frames)

            if frame_count == 0:
                self.logger.warning(f"⚠️ No frames found in task {task_id}")
                return []

            self.logger.info(f"🔍 Downloading {frame_count} images from task {task_id}...")

            # Create output directory if it doesn't exist using Path
            output_path_obj = Path(output_dir)
            output_path_obj.mkdir(parents=True, exist_ok=True)

            saved_files = []

            for frame_idx in range(frame_count):
                try:
                    # Download the frame
                    image_data = self.download_task_image(task_id, frame_idx, quality, token)

                    # Get frame info from metadata for filename
                    frame_info = metadata.frames[frame_idx]
                    original_name = frame_info.name if frame_info.name else f"frame_{frame_idx:06d}"

                    # Ensure we have a proper file extension
                    if not any(original_name.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]):
                        original_name += ".jpg"  # Default to jpg if no extension

                    # Save the image using Path
                    output_file_path = output_path_obj / f"task_{task_id}_{original_name}"
                    with open(output_file_path, "wb") as f:
                        f.write(image_data)

                    saved_files.append(str(output_file_path))
                    self.logger.debug(f"📁 Saved: {output_file_path}")

                except Exception as e:
                    self.logger.error(f"❌ Failed to download frame {frame_idx} from task {task_id}: {e}")
                    continue

            self.logger.info(f"✅ Successfully downloaded {len(saved_files)}/{frame_count} images from task {task_id}")
            return saved_files

        except Exception as e:
            self.logger.error(f"❌ Failed to download images from task {task_id}: {e}")
            raise RuntimeError(f"❌ Failed to download images from task {task_id}.") from e

    # 🔹 Download task data as chunks (bulk download)
    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        max_delay=30.0,
        retry_502=True,
        max_502_retries=10,
        initial_502_delay=30.0,
        max_502_delay=300.0,
    )
    def download_task_data_chunk(self, task_id: int, chunk_index: int = 0, quality: str = "original", token: str | None = None) -> bytes:
        """
        Download a specific task data chunk.

        Args:
            task_id (int): The ID of the task
            chunk_index (int): The chunk index to download (0-based)
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            bytes: The chunk data as bytes
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/tasks/{task_id}/data"
        params = {"type": "chunk", "quality": quality, "index": chunk_index}
        
        return self._download_binary_data(
            url, headers, params,
            f"data chunk {chunk_index} from task {task_id} (quality: {quality})"
        )

    # 🔹 Download all task data chunks (complete bulk download)
    def download_all_task_chunks(self, task_id: int, output_dir: str | Path, quality: str = "original", token: str | None = None) -> list[str]:
        """
        Download all data chunks from a task. CVAT splits large tasks into multiple chunks,
        so this method downloads all chunks to get the complete dataset.

        Args:
            task_id (int): The ID of the task
            output_dir (str | Path): Directory to save chunk files
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            list[str]: List of saved chunk file paths
        """
        if token is None:
            token = self.cvat_token

        # First get metadata to understand the task structure
        try:
            metadata = self.get_task_media_metainformation(task_id, token)
            frame_count = len(metadata.frames)

            if frame_count == 0:
                self.logger.warning(f"⚠️ No frames found in task {task_id}")
                return []

            self.logger.info(f"🔍 Task {task_id} has {frame_count} frames, downloading all chunks...")

            # Create output directory
            output_path_obj = Path(output_dir)
            output_path_obj.mkdir(parents=True, exist_ok=True)

            saved_chunks = []
            chunk_index = 0

            # Keep downloading chunks until we get an error (no more chunks)
            while True:
                try:
                    self.logger.info(f"🔍 Attempting to download chunk {chunk_index}...")
                    chunk_data = self.download_task_data_chunk(task_id, chunk_index, quality, token)

                    # Save the chunk
                    chunk_filename = f"task_{task_id}_chunk_{chunk_index:03d}.zip"
                    chunk_path = output_path_obj / chunk_filename

                    with open(chunk_path, "wb") as f:
                        f.write(chunk_data)

                    saved_chunks.append(str(chunk_path))
                    self.logger.info(f"✅ Downloaded chunk {chunk_index} ({len(chunk_data)} bytes) to {chunk_path}")

                    chunk_index += 1

                except requests.HTTPError as e:
                    if e.response.status_code == 404:
                        # No more chunks available
                        self.logger.info(f"📊 Reached end of chunks at index {chunk_index}")
                        break
                    else:
                        # Other HTTP error, re-raise
                        raise
                except Exception as e:
                    self.logger.error(f"❌ Failed to download chunk {chunk_index}: {e}")
                    break

            self.logger.info(f"✅ Successfully downloaded {len(saved_chunks)} chunks from task {task_id}")
            self.logger.info(f"📊 Total frames in task: {frame_count}, Chunks downloaded: {len(saved_chunks)}")

            return saved_chunks

        except Exception as e:
            self.logger.error(f"❌ Failed to download chunks from task {task_id}: {e}")
            raise RuntimeError(f"❌ Failed to download chunks from task {task_id}.") from e

    # 🔹 Retrieve metainformation for media files in a job
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_job_media_metainformation(self, job_id: int, token: str | None = None) -> CvatApiJobMediasMetainformation:
        """
        Retrieve metainformation for a given job id
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/jobs/{job_id}/data/meta"
        
        return self._make_request("GET", url, headers, "metainformation for job", job_id, response_model=CvatApiJobMediasMetainformation)

    # 🔹 Download-specific helper
    def _download_binary_data(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any],
        resource_desc: str,
        timeout: Optional[float] = None,
    ) -> bytes:
        """Download binary data with standard error handling."""
        timeout = timeout or self.cvat_api_timeout
        
        self.logger.info(f"🔍 Downloading {resource_desc}...")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            
            self.logger.info(f"✅ Successfully downloaded {resource_desc}")
            self.logger.debug(f"📊 Data size: {len(response.content)} bytes")
            
            return response.content
            
        except requests.Timeout as e:
            self.logger.error(f"❌ Timeout while downloading {resource_desc}")
            raise TimeoutError(f"❌ Timeout while downloading {resource_desc}.") from e
        except requests.HTTPError as e:
            self.logger.error(f"❌ HTTP Error while downloading {resource_desc}: {e.response.status_code}")
            self._handle_response_errors(e.response, "❌ HTTP Error")
            raise ConnectionError(f"❌ Failed to download {resource_desc}: {e.response.status_code} - {e.response.text}") from e
        except requests.RequestException as e:
            self.logger.error(f"❌ Network error while downloading {resource_desc}: {e}")
            raise RuntimeError(f"❌ Network error while downloading {resource_desc}.") from e
        except Exception as e:
            self.logger.error(f"❌ Error downloading {resource_desc}: {e}")
            raise ValueError(f"❌ Error downloading {resource_desc}: Invalid response from server.") from e

    # 🔹 Download a specific image frame from a job
    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        max_delay=30.0,
        retry_502=True,
        max_502_retries=10,
        initial_502_delay=30.0,
        max_502_delay=300.0,
    )
    def download_job_image(self, job_id: int, frame_number: int, quality: str = "original", token: str | None = None) -> bytes:
        """
        Download a specific image frame from a job.

        Args:
            job_id (int): The ID of the job
            frame_number (int): The frame number to download (actual task frame number, not 0-based within job)
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            bytes: The image data as bytes
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/jobs/{job_id}/data"
        params = {"type": "frame", "number": frame_number, "quality": quality}
        
        return self._download_binary_data(
            url, headers, params,
            f"frame {frame_number} from job {job_id} (quality: {quality})"
        )

    # 🔹 Download all images from a job
    def download_job_images(self, job_id: int, output_dir: str | Path, quality: str = "original", token: str | None = None) -> list[str]:
        """
        Download all images from a job using metadata to determine frame count.

        Args:
            job_id (int): The ID of the job
            output_dir (str | Path): Directory to save images
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            list[str]: List of saved image file paths
        """
        if token is None:
            token = self.cvat_token

        # First get metadata to know how many frames exist
        try:
            metadata = self.get_job_media_metainformation(job_id, token)
            frame_count = len(metadata.frames)

            if frame_count == 0:
                self.logger.warning(f"⚠️ No frames found in job {job_id}")
                return []

            self.logger.info(f"🔍 Downloading {frame_count} images from job {job_id}...")

            # Create output directory if it doesn't exist using Path
            output_path_obj = Path(output_dir)
            output_path_obj.mkdir(parents=True, exist_ok=True)

            saved_files = []

            for frame_idx in range(metadata.start_frame, metadata.stop_frame + 1):
                try:
                    # Download the frame using actual task frame number
                    image_data = self.download_job_image(job_id, frame_idx, quality, token)

                    # Get frame info from metadata for filename - need to use relative index
                    frame_info_idx = frame_idx - metadata.start_frame
                    frame_info = metadata.frames[frame_info_idx]
                    original_name = frame_info.name if frame_info.name else f"frame_{frame_idx:06d}"

                    # Ensure we have a proper file extension
                    if not any(original_name.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]):
                        original_name += ".jpg"  # Default to jpg if no extension

                    # Save the image using Path
                    output_file_path = output_path_obj / f"job_{job_id}_{original_name}"
                    with open(output_file_path, "wb") as f:
                        f.write(image_data)

                    saved_files.append(str(output_file_path))
                    self.logger.debug(f"📁 Saved: {output_file_path}")

                except Exception as e:
                    self.logger.error(f"❌ Failed to download frame {frame_idx} from job {job_id}: {e}")
                    continue

            self.logger.info(f"✅ Successfully downloaded {len(saved_files)}/{frame_count} images from job {job_id}")
            return saved_files

        except Exception as e:
            self.logger.error(f"❌ Failed to download images from job {job_id}: {e}")
            raise RuntimeError(f"❌ Failed to download images from job {job_id}.") from e

    # 🔹 Download job data as chunks (bulk download)
    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        max_delay=30.0,
        retry_502=True,
        max_502_retries=10,
        initial_502_delay=30.0,
        max_502_delay=300.0,
    )
    def download_job_data_chunk(self, job_id: int, chunk_index: int = 0, quality: str = "original", token: str | None = None) -> bytes:
        """
        Download a specific job data chunk.

        Args:
            job_id (int): The ID of the job
            chunk_index (int): The chunk index to download (0-based)
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            bytes: The chunk data as bytes
        """
        headers = self._get_headers(token, with_organization=False)
        url = f"{self.cvat_url}/api/jobs/{job_id}/data"
        params = {"type": "chunk", "quality": quality, "index": chunk_index}
        
        return self._download_binary_data(
            url, headers, params,
            f"data chunk {chunk_index} from job {job_id} (quality: {quality})"
        )

    # 🔹 Download all job data chunks (complete bulk download)
    def download_all_job_chunks(self, job_id: int, output_dir: str | Path, quality: str = "original", token: str | None = None) -> list[str]:
        """
        Download all data chunks from a job. CVAT splits large jobs into multiple chunks,
        so this method downloads all chunks to get the complete dataset.

        Args:
            job_id (int): The ID of the job
            output_dir (str | Path): Directory to save chunk files
            quality (str): Image quality - "original" or "compressed"
            token (str): Authentication token

        Returns:
            list[str]: List of saved chunk file paths
        """
        if token is None:
            token = self.cvat_token

        # First get metadata to understand the job structure
        try:
            metadata = self.get_job_media_metainformation(job_id, token)
            frame_count = len(metadata.frames)

            if frame_count == 0:
                self.logger.warning(f"⚠️ No frames found in job {job_id}")
                return []

            self.logger.info(f"🔍 Job {job_id} has {frame_count} frames, downloading all chunks...")

            # Create output directory
            output_path_obj = Path(output_dir)
            output_path_obj.mkdir(parents=True, exist_ok=True)

            saved_chunks = []
            chunk_index = 0

            # Keep downloading chunks until we get an error (no more chunks)
            while True:
                try:
                    self.logger.info(f"🔍 Attempting to download chunk {chunk_index}...")
                    chunk_data = self.download_job_data_chunk(job_id, chunk_index, quality, token)

                    # Save the chunk
                    chunk_filename = f"job_{job_id}_chunk_{chunk_index:03d}.zip"
                    chunk_path = output_path_obj / chunk_filename

                    with open(chunk_path, "wb") as f:
                        f.write(chunk_data)

                    saved_chunks.append(str(chunk_path))
                    self.logger.info(f"✅ Downloaded chunk {chunk_index} ({len(chunk_data)} bytes) to {chunk_path}")

                    chunk_index += 1

                except requests.HTTPError as e:
                    if e.response.status_code == 404:
                        # No more chunks available
                        self.logger.info(f"📊 Reached end of chunks at index {chunk_index}")
                        break
                    else:
                        # Other HTTP error, re-raise
                        raise
                except Exception as e:
                    self.logger.error(f"❌ Failed to download chunk {chunk_index}: {e}")
                    break

            self.logger.info(f"✅ Successfully downloaded {len(saved_chunks)} chunks from job {job_id}")
            self.logger.info(f"📊 Total frames in job: {frame_count}, Chunks downloaded: {len(saved_chunks)}")

            return saved_chunks

        except Exception as e:
            self.logger.error(f"❌ Failed to download chunks from job {job_id}: {e}")
            raise RuntimeError(f"❌ Failed to download chunks from job {job_id}.") from e
