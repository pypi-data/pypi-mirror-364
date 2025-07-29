"""
CVAT API TypedDict schemas.
"""

from typing import Any, Dict, List, Optional, TypedDict


class CvatApiAttribute(TypedDict):
    """Represents an attribute in CVAT API."""

    id: int
    spec_id: int
    value: str


class CvatApiTag(TypedDict):
    """Represents a tag in CVAT API."""

    id: int
    frame: int
    label_id: int
    source: str
    attributes: List[CvatApiAttribute]


class CvatApiShape(TypedDict):
    """Represents a shape in CVAT API."""

    id: int
    type: str
    occluded: bool
    z_order: int
    points: List[float]
    rotation: float
    outside: bool
    attributes: List[CvatApiAttribute]
    frame: int
    label_id: int
    source: str


class CvatApiJobAnnotations(TypedDict):
    """Represents a job in CVAT API."""

    version: str
    tags: List[CvatApiTag]
    shapes: List[CvatApiShape]
    tracks: List[Any]


class CvatApiAttributeDefinition(TypedDict):
    """Represents an attribute definition in CVAT API."""

    id: int
    name: str
    mutable: bool
    input_type: str
    values: List[str]
    default_value: Optional[str]


class CvatApiLabelDefinition(TypedDict):
    """Represents a label in CVAT API."""

    id: int
    name: str
    color: str
    type: str
    attributes: List[CvatApiAttributeDefinition]


class CvatApiMetainformationFrame(TypedDict):
    """Represents a frame in CVAT API."""

    width: int
    height: int
    name: str
    related_files: int


class CvatApiJobMediasMetainformation(TypedDict):
    """Represents the metainformation for a job in CVAT API."""

    start_frame: int
    stop_frame: int
    frame_filter: str
    frames: List[CvatApiMetainformationFrame]


class CvatApiTaskMediasMetainformation(TypedDict):
    """Represents the metainformation for a task in CVAT API."""

    media_type: str
    start_frame: int
    stop_frame: int
    frame_filter: str
    frames: List[CvatApiMetainformationFrame]


class CvatApiJobDetails(TypedDict):
    """Represents job details in CVAT API."""

    id: int
    task_id: int
    project_id: Optional[int]
    assignee: Optional[Dict[str, Any]]
    guide_id: Optional[int]
    dimension: str
    data_compressed_chunk_type: str
    data_original_chunk_type: str
    bug_tracker: Optional[str]
    mode: str
    frame_count: int
    start_frame: int
    stop_frame: int
    data_chunk_size: int
    created_date: str
    updated_date: str
    issues: Dict[str, Any]
    labels: List[CvatApiLabelDefinition]
    type: str
    organization: Optional[int]


class CvatApiTaskDetails(TypedDict):
    """Represents task details in CVAT API."""

    id: int
    name: str
    project_id: Optional[int]
    mode: str
    owner: Dict[str, Any]
    assignee: Optional[Dict[str, Any]]
    bug_tracker: str
    created_date: str
    updated_date: str
    overlap: Optional[int]
    segment_size: int
    status: str
    labels: List[CvatApiLabelDefinition]
    segments: List[Dict[str, Any]]
    dimension: str
    data_compressed_chunk_type: str
    data_original_chunk_type: str
    image_quality: int
    data: int
    subset: str
    organization: Optional[int]
    target_storage: Optional[Dict[str, Any]]
    source_storage: Optional[Dict[str, Any]]
    jobs: Dict[str, Any]


class CvatApiTaskAnnotations(TypedDict):
    """Represents annotations for a task in CVAT API."""

    version: str
    tags: List[CvatApiTag]
    shapes: List[CvatApiShape]
    tracks: List[Any]
