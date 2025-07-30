"""
UTM Frame schema for grouping annotations from the same camera frame.
"""

from typing import List, Optional, Iterator, Union, overload
from pydantic import BaseModel, Field

from lcvtoolbox.core.schemas.utm.annotation import UTMAnnotation
from lcvtoolbox.core.schemas.utm.point import UTMPoint


class UTMFrame(BaseModel):
    """
    UTM frame grouping annotations captured from the same camera frame.
    
    This class groups annotations that were captured from the same frame
    and provides list-like behavior for easy manipulation.
    """
    
    annotations: List[UTMAnnotation] = Field(default_factory=list, description="List of annotations from this frame")
    camera_center: UTMPoint = Field(..., description="Center of camera when the frame was captured")
    trajectory_index: Optional[int] = Field(None, description="Index of the camera center point in the trajectory")

    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "annotations": [
                    {
                        "polygon": {"polygon": {"exterior": [(448262.0, 5411932.0), (448300.0, 5411932.0), (448300.0, 5411970.0), (448262.0, 5411970.0), (448262.0, 5411932.0)], "interiors": []}, "zone_number": 31, "zone_letter": "U"},
                        "label": "pothole",
                        "attributes": [{"key": "severity", "value": "high"}],
                    }
                ],
                "camera_center": {"easting": 448280.0, "northing": 5411950.0, "zone_number": 31, "zone_letter": "U", "height": 2.0},
                "trajectory_index": 42
            }
        }

    def __len__(self) -> int:
        """Get the number of annotations in this frame."""
        return len(self.annotations)

    @overload
    def __getitem__(self, index: int) -> UTMAnnotation: ...
    
    @overload
    def __getitem__(self, index: slice) -> List[UTMAnnotation]: ...

    def __getitem__(self, index: Union[int, slice]) -> Union[UTMAnnotation, List[UTMAnnotation]]:
        """Get annotation(s) by index or slice."""
        return self.annotations[index]

    def __setitem__(self, index: Union[int, slice], value: Union[UTMAnnotation, List[UTMAnnotation]]) -> None:
        """Set annotation(s) by index or slice."""
        self.annotations[index] = value  # type: ignore

    def __delitem__(self, index: Union[int, slice]) -> None:
        """Delete annotation(s) by index or slice."""
        del self.annotations[index]

    def __iter__(self) -> Iterator[UTMAnnotation]:
        """Iterate over annotations."""
        return iter(self.annotations)

    def __contains__(self, annotation: UTMAnnotation) -> bool:
        """Check if an annotation is in this frame."""
        return annotation in self.annotations

    def append(self, annotation: UTMAnnotation) -> None:
        """
        Append an annotation to the frame.
        
        Args:
            annotation: UTMAnnotation to append.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> annotation = UTMAnnotation(...)
            >>> frame.append(annotation)
        """
        self.annotations.append(annotation)

    def extend(self, annotations: List[UTMAnnotation]) -> None:
        """
        Extend the frame with multiple annotations.
        
        Args:
            annotations: List of UTMAnnotation objects to add.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> frame.extend([ann1, ann2, ann3])
        """
        self.annotations.extend(annotations)

    def insert(self, index: int, annotation: UTMAnnotation) -> None:
        """
        Insert an annotation at the specified index.
        
        Args:
            index: Index where to insert.
            annotation: UTMAnnotation to insert.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> frame.insert(0, annotation)
        """
        self.annotations.insert(index, annotation)

    def remove(self, annotation: UTMAnnotation) -> None:
        """
        Remove the first occurrence of an annotation.
        
        Args:
            annotation: UTMAnnotation to remove.
            
        Raises:
            ValueError: If the annotation is not found.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> frame.remove(annotation)
        """
        self.annotations.remove(annotation)

    def pop(self, index: int = -1) -> UTMAnnotation:
        """
        Remove and return an annotation at the given index.
        
        Args:
            index: Index of the annotation to remove (default: -1).
            
        Returns:
            UTMAnnotation: The removed annotation.
            
        Raises:
            IndexError: If the frame is empty or index is out of range.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> last_annotation = frame.pop()
        """
        return self.annotations.pop(index)

    def clear(self) -> None:
        """
        Remove all annotations from the frame.
        
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> frame.clear()
            >>> print(len(frame))  # 0
        """
        self.annotations.clear()

    def index(self, annotation: UTMAnnotation, start: int = 0, stop: Optional[int] = None) -> int:
        """
        Return the index of the first occurrence of the annotation.
        
        Args:
            annotation: UTMAnnotation to find.
            start: Start searching from this index.
            stop: Stop searching at this index.
            
        Returns:
            int: Index of the first occurrence.
            
        Raises:
            ValueError: If the annotation is not found.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> idx = frame.index(annotation)
        """
        if stop is None:
            return self.annotations.index(annotation, start)
        else:
            return self.annotations.index(annotation, start, stop)

    def count(self, annotation: UTMAnnotation) -> int:
        """
        Return the number of occurrences of the annotation.
        
        Args:
            annotation: UTMAnnotation to count.
            
        Returns:
            int: Number of occurrences.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> count = frame.count(annotation)
        """
        return self.annotations.count(annotation)

    def reverse(self) -> None:
        """
        Reverse the annotations in-place.
        
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> frame.reverse()
        """
        self.annotations.reverse()

    def sort(self, key=None, reverse: bool = False) -> None:
        """
        Sort the annotations in-place.
        
        Args:
            key: Function of one argument to extract comparison key.
            reverse: If True, sort in descending order.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> # Sort by area
            >>> frame.sort(key=lambda ann: ann.area_square_meters())
        """
        self.annotations.sort(key=key, reverse=reverse)

    def copy(self) -> "UTMFrame":
        """
        Create a shallow copy of the frame.
        
        Returns:
            UTMFrame: A new frame with the same annotations.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> frame_copy = frame.copy()
        """
        return UTMFrame(
            annotations=self.annotations.copy(),
            camera_center=self.camera_center,
            trajectory_index=self.trajectory_index
        )

    def get_annotations_by_label(self, label: str) -> List[UTMAnnotation]:
        """
        Get all annotations with a specific label.
        
        Args:
            label: Label to filter by.
            
        Returns:
            List[UTMAnnotation]: Annotations with the specified label.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> potholes = frame.get_annotations_by_label("pothole")
        """
        return [ann for ann in self.annotations if ann.label == label]

    def get_total_area(self) -> float:
        """
        Get the total area of all annotations in the frame.
        
        Returns:
            float: Total area in square meters.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> total_area = frame.get_total_area()
            >>> print(f"Total annotated area: {total_area:.2f} m²")
        """
        return sum(ann.area_square_meters() for ann in self.annotations)

    def to_dict(self) -> dict:
        """
        Convert the UTMFrame to a dictionary.
        
        Returns:
            dict: Dictionary representation of the frame.
            
        Example:
            >>> frame = UTMFrame(camera_center=...)
            >>> data = frame.to_dict()
        """
        result = {
            "annotations": [ann.to_dict() for ann in self.annotations],
            "camera_center": self.camera_center.to_dict()
        }
        if self.trajectory_index is not None:
            result["trajectory_index"] = self.trajectory_index
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "UTMFrame":
        """
        Create a UTMFrame from a dictionary.
        
        Args:
            data: Dictionary containing frame data.
            
        Returns:
            UTMFrame: New frame instance.
            
        Raises:
            ValueError: If required keys are missing or data is invalid.
            
        Example:
            >>> data = {...}
            >>> frame = UTMFrame.from_dict(data)
        """
        try:
            annotations = [UTMAnnotation.from_dict(ann) for ann in data.get("annotations", [])]
            camera_center = UTMPoint.from_dict(data["camera_center"])
            
            return cls(
                annotations=annotations,
                camera_center=camera_center,
                trajectory_index=data.get("trajectory_index")
            )
        except KeyError as e:
            raise ValueError(f"Missing required key in dictionary: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to create UTMFrame from dictionary: {e}") from e

    def __repr__(self) -> str:
        """String representation of the frame."""
        return f"UTMFrame(annotations={len(self.annotations)}, camera_center={self.camera_center}, trajectory_index={self.trajectory_index})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        labels = [ann.label for ann in self.annotations]
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        label_str = ", ".join(f"{count} {label}" for label, count in label_counts.items())
        return f"UTMFrame with {label_str} at index {self.trajectory_index}"
