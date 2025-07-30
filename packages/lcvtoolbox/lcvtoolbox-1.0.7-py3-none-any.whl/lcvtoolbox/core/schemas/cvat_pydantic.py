"""
CVAT API Pydantic schemas.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CvatApiAttribute(BaseModel):
    """Represents an attribute in CVAT API."""

    id: int
    spec_id: int
    value: str

    model_config = ConfigDict(extra="allow")


class CvatApiTag(BaseModel):
    """Represents a tag in CVAT API."""

    id: int
    frame: int
    label_id: int
    source: str
    attributes: List[CvatApiAttribute] = []

    model_config = ConfigDict(extra="allow")


class CvatApiShape(BaseModel):
    """Represents a shape in CVAT API."""

    id: int
    type: str
    occluded: bool
    z_order: int
    points: List[float]
    rotation: float
    outside: bool
    attributes: List[CvatApiAttribute] = []
    frame: int
    label_id: int
    source: str

    model_config = ConfigDict(extra="allow")


class CvatApiJobAnnotations(BaseModel):
    """Represents job annotations in CVAT API."""

    version: str
    tags: List[CvatApiTag] = []
    shapes: List[CvatApiShape] = []
    tracks: List[Any] = []

    model_config = ConfigDict(extra="allow")


class CvatApiAttributeDefinition(BaseModel):
    """Represents an attribute definition in CVAT API."""

    id: int
    name: str
    mutable: bool
    input_type: str
    values: List[str] = []
    default_value: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class CvatApiLabelDefinition(BaseModel):
    """Represents a label definition in CVAT API."""

    id: int
    name: str
    color: str
    type: str
    attributes: List[CvatApiAttributeDefinition] = []

    model_config = ConfigDict(extra="allow")


class CvatApiMetainformationFrame(BaseModel):
    """Represents a frame in CVAT API."""

    width: int
    height: int
    name: str
    related_files: int

    model_config = ConfigDict(extra="allow")


class CvatApiJobMediasMetainformation(BaseModel):
    """Represents the metainformation for a job in CVAT API."""

    start_frame: int
    stop_frame: int
    frame_filter: str
    frames: List[CvatApiMetainformationFrame]

    model_config = ConfigDict(extra="allow")


class CvatApiTaskMediasMetainformation(BaseModel):
    """Represents the metainformation for a task in CVAT API."""

    media_type: str
    start_frame: int
    stop_frame: int
    frame_filter: str
    frames: List[CvatApiMetainformationFrame]

    model_config = ConfigDict(extra="allow")


class CvatApiJobDetails(BaseModel):
    """Represents job details in CVAT API."""

    id: int
    task_id: int
    project_id: Optional[int] = None
    assignee: Optional[Dict[str, Any]] = None
    guide_id: Optional[int] = None
    dimension: str
    data_compressed_chunk_type: str
    data_original_chunk_type: str
    bug_tracker: Optional[str] = None
    mode: str
    frame_count: int
    start_frame: int
    stop_frame: int
    data_chunk_size: int
    created_date: str
    updated_date: str
    issues: Dict[str, Any] = Field(default_factory=dict)
    labels: List[CvatApiLabelDefinition] = []
    type: str
    organization: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class CvatApiTaskDetails(BaseModel):
    """Represents task details in CVAT API."""

    id: int
    name: str
    project_id: Optional[int] = None
    mode: str
    owner: Dict[str, Any]
    assignee: Optional[Dict[str, Any]] = None
    bug_tracker: str
    created_date: str
    updated_date: str
    overlap: Optional[int] = None
    segment_size: int
    status: str
    labels: List[CvatApiLabelDefinition] = []
    segments: List[Dict[str, Any]] = []
    dimension: str
    data_compressed_chunk_type: str
    data_original_chunk_type: str
    image_quality: int
    data: int
    subset: str
    organization: Optional[int] = None
    target_storage: Optional[Dict[str, Any]] = None
    source_storage: Optional[Dict[str, Any]] = None
    jobs: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class CvatApiTaskAnnotations(BaseModel):
    """Represents annotations for a task in CVAT API."""

    version: str
    tags: List[CvatApiTag] = []
    shapes: List[CvatApiShape] = []
    tracks: List[Any] = []

    model_config = ConfigDict(extra="allow")
