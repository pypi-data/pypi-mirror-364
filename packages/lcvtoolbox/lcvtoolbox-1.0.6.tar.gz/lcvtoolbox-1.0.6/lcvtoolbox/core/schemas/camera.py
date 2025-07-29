"""
Camera-related schemas.
"""

from typing import Any, List, Optional

import numpy as np
from pydantic import BaseModel


class CameraMatrixSchema(BaseModel):
    """
    Schema for camera intrinsic matrix parameters.
    
    Represents the camera intrinsic parameters in a format
    suitable for serialization and validation.
    
    Attributes:
        fx: Focal length in x direction (pixels)
        fy: Focal length in y direction (pixels)
        cx: Principal point x coordinate (pixels)
        cy: Principal point y coordinate (pixels)
        s: Skew parameter (optional, usually 0)
    """
    
    fx: float
    fy: float
    cx: float
    cy: float
    s: float = 0.0
    
    @property
    def numpy(self) -> np.ndarray:
        """
        Get the camera matrix as a numpy array.
        
        Returns:
            np.ndarray: 3x3 camera intrinsic matrix
        """
        return self.to_matrix()
    
    def to_matrix(self) -> np.ndarray:
        """
        Convert to 3x3 camera matrix.
        
        Returns:
            np.ndarray: 3x3 camera intrinsic matrix
        """
        return np.array([
            [self.fx, self.s, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ], dtype=np.float64)
    
    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> "CameraMatrixSchema":
        """
        Create from 3x3 camera matrix.
        
        Args:
            matrix: 3x3 numpy array
            
        Returns:
            CameraMatrixSchema instance
        """
        if matrix.shape != (3, 3):
            raise ValueError(f"Expected 3x3 matrix, got {matrix.shape}")
        
        return cls(
            fx=float(matrix[0, 0]),
            fy=float(matrix[1, 1]),
            cx=float(matrix[0, 2]),
            cy=float(matrix[1, 2]),
            s=float(matrix[0, 1])
        )


class CameraDistortionSchema(BaseModel):
    """
    Schema for camera distortion coefficients.
    
    Supports various distortion models including radial and tangential distortion.
    
    Attributes:
        k1: First radial distortion coefficient
        k2: Second radial distortion coefficient
        p1: First tangential distortion coefficient
        p2: Second tangential distortion coefficient
        k3: Third radial distortion coefficient (optional)
        k4: Fourth radial distortion coefficient (optional)
        k5: Fifth radial distortion coefficient (optional)
        k6: Sixth radial distortion coefficient (optional)
    """
    
    k1: float = 0.0
    k2: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    k3: Optional[float] = None
    k4: Optional[float] = None
    k5: Optional[float] = None
    k6: Optional[float] = None
    
    @property
    def numpy(self) -> np.ndarray:
        """
        Get the distortion coefficients as a numpy array.
        
        Returns:
            np.ndarray: Distortion coefficients in OpenCV format
        """
        return self.to_opencv_coeffs()
    
    def to_opencv_coeffs(self) -> np.ndarray:
        """
        Convert to OpenCV distortion coefficients array.
        
        Returns:
            np.ndarray: Distortion coefficients in OpenCV format
        """
        coeffs = [self.k1, self.k2, self.p1, self.p2]
        
        if self.k3 is not None:
            coeffs.append(self.k3)
        if self.k4 is not None:
            coeffs.append(self.k4)
        if self.k5 is not None:
            coeffs.append(self.k5)
        if self.k6 is not None:
            coeffs.append(self.k6)
            
        return np.array(coeffs, dtype=np.float64)
    
    @classmethod
    def from_opencv_coeffs(cls, coeffs: np.ndarray) -> "CameraDistortionSchema":
        """
        Create from OpenCV distortion coefficients.
        
        Args:
            coeffs: Array of distortion coefficients
            
        Returns:
            CameraDistortionSchema instance
        """
        coeffs = coeffs.flatten()
        n_coeffs = len(coeffs)
        
        if n_coeffs < 4:
            raise ValueError(f"Expected at least 4 coefficients, got {n_coeffs}")
        
        kwargs = {
            'k1': float(coeffs[0]),
            'k2': float(coeffs[1]),
            'p1': float(coeffs[2]),
            'p2': float(coeffs[3])
        }
        
        if n_coeffs > 4:
            kwargs['k3'] = float(coeffs[4])
        if n_coeffs > 5:
            kwargs['k4'] = float(coeffs[5])
        if n_coeffs > 6:
            kwargs['k5'] = float(coeffs[6])
        if n_coeffs > 7:
            kwargs['k6'] = float(coeffs[7])
            
        return cls(**kwargs)
