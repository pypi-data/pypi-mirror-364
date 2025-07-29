from __future__ import annotations

import numpy as np
from typing import Tuple, Optional

from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rpy import RPY
from .rotation_vector import RotationVector
from .axis_angle import AxisAngle
from .two_vectors import TwoVectors
from .euler_angles import EulerAngles
from .vector import Vector3D
from .point import Point3D


class TransformationMatrix:
    """
    Represents a homogeneous transformation matrix (4x4) combining rotation and translation.

    A transformation matrix represents a rigid body transformation in 3D space,
    combining rotation and translation into a single 4x4 matrix:
    
    [ R  t ]
    [ 0  1 ]
    
    where R is a 3x3 rotation matrix and t is a 3x1 translation vector.

    Args:
        matrix: Optional 4x4 numpy array. If None, creates identity transformation.
        rotation: Optional rotation component (can be any rotation representation)
        translation: Optional translation component (as Point3D, Vector3D, or numpy array)

    Examples:
        >>> # Create identity transformation
        >>> T = TransformationMatrix()
        >>>
        >>> # Create from rotation and translation
        >>> R = RPY(0.1, 0.2, 0.3)
        >>> t = Point3D(1, 2, 3)
        >>> T = TransformationMatrix.from_rotation_translation(R, t)
        >>>
        >>> # Compose transformations (chain them)
        >>> T3 = T1.compose(T2)  # T3 = T1 @ T2
        >>>
        >>> # Transform a point
        >>> p_new = T.transform_point(p)
    """

    __slots__ = ("_matrix",)  # Memory optimization

    def __init__(self, matrix: Optional[np.ndarray] = None) -> None:
        """Initialize transformation matrix."""
        if matrix is None:
            # Create identity transformation
            self._matrix = np.eye(4, dtype=np.float64)
        else:
            matrix = np.array(matrix, dtype=np.float64)
            if matrix.shape != (4, 4):
                raise ValueError(f"Matrix must be 4x4, got {matrix.shape}")
            
            # Validate it's a valid transformation matrix
            if not np.allclose(matrix[3, :], [0, 0, 0, 1]):
                raise ValueError("Invalid transformation matrix: last row must be [0, 0, 0, 1]")
            
            # Validate rotation part is orthonormal
            R = matrix[:3, :3]
            if not np.allclose(R @ R.T, np.eye(3), atol=1e-6):
                raise ValueError("Invalid transformation matrix: rotation part is not orthonormal")
            
            if not np.allclose(np.linalg.det(R), 1.0, atol=1e-6):
                raise ValueError("Invalid transformation matrix: rotation determinant is not 1")
            
            self._matrix = matrix

    @classmethod
    def identity(cls) -> TransformationMatrix:
        """Create an identity transformation (no rotation, no translation)."""
        return cls()

    @classmethod
    def from_rotation_translation(cls, rotation: RotationMatrix | Quaternion | RPY | RotationVector | AxisAngle | TwoVectors | EulerAngles | np.ndarray,
                                translation: Point3D | Vector3D | np.ndarray | list | tuple) -> TransformationMatrix:
        """Create from rotation and translation components.

        Args:
            rotation: Rotation component (any rotation representation)
            translation: Translation component

        Returns:
            TransformationMatrix instance
        """
        # Convert rotation to RotationMatrix if needed
        if isinstance(rotation, RotationMatrix):
            R = rotation.matrix
        elif isinstance(rotation, np.ndarray):
            if rotation.shape == (3, 3):
                R = rotation
            else:
                raise ValueError("Rotation matrix must be 3x3")
        elif hasattr(rotation, 'to_rotation_matrix'):
            rot_mat_result = rotation.to_rotation_matrix()
            # Check if result is a RotationMatrix object or numpy array
            if hasattr(rot_mat_result, 'matrix'):
                R = rot_mat_result.matrix
            elif isinstance(rot_mat_result, np.ndarray):
                R = rot_mat_result
            else:
                raise TypeError(f"Unexpected return type from to_rotation_matrix: {type(rot_mat_result)}")
        else:
            raise TypeError(f"Unsupported rotation type: {type(rotation)}")
        
        # Convert translation to numpy array
        if isinstance(translation, Point3D):
            t = translation.numpy
        elif isinstance(translation, Vector3D):
            t = translation.numpy
        elif isinstance(translation, (list, tuple)):
            t = np.array(translation, dtype=np.float64)
        elif isinstance(translation, np.ndarray):
            t = translation.astype(np.float64)
        else:
            raise TypeError(f"Unsupported translation type: {type(translation)}")
        
        if len(t) != 3:
            raise ValueError("Translation must be 3D")
        
        # Build 4x4 matrix
        T = np.eye(4, dtype=np.float64)
        T[:3, :3] = R
        T[:3, 3] = t
        
        return cls(T)

    @classmethod
    def from_point_rpy(cls, point: Point3D, rpy: RPY) -> TransformationMatrix:
        """Create from a point (translation) and RPY angles (rotation)."""
        return cls.from_rotation_translation(rpy, point)

    @classmethod
    def from_point_quaternion(cls, point: Point3D, quaternion: Quaternion) -> TransformationMatrix:
        """Create from a point (translation) and quaternion (rotation)."""
        return cls.from_rotation_translation(quaternion, point)

    @classmethod
    def from_translation(cls, translation: Point3D | Vector3D | np.ndarray | list | tuple) -> TransformationMatrix:
        """Create a pure translation transformation (no rotation)."""
        return cls.from_rotation_translation(RotationMatrix.identity(), translation)

    @classmethod
    def from_rotation(cls, rotation: RotationMatrix | Quaternion | RPY | RotationVector | AxisAngle | TwoVectors | EulerAngles) -> TransformationMatrix:
        """Create a pure rotation transformation (no translation)."""
        return cls.from_rotation_translation(rotation, [0, 0, 0])

    @classmethod
    def from_position_orientation(cls, position: Point3D | np.ndarray,
                                orientation: Quaternion | RPY | RotationMatrix | np.ndarray) -> TransformationMatrix:
        """Create from position and orientation (common in robotics).
        
        Args:
            position: 3D position
            orientation: Orientation as quaternion, RPY, or rotation matrix
        """
        return cls.from_rotation_translation(orientation, position)

    @property
    def matrix(self) -> np.ndarray:
        """Get the 4x4 transformation matrix."""
        return self._matrix.copy()

    @property
    def rotation_matrix(self) -> RotationMatrix:
        """Get the rotation component as a RotationMatrix."""
        return RotationMatrix(self._matrix[:3, :3])

    @property
    def translation(self) -> Point3D:
        """Get the translation component as a Point3D."""
        return Point3D(*self._matrix[:3, 3])

    @property
    def translation_vector(self) -> np.ndarray:
        """Get the translation component as a numpy array."""
        return self._matrix[:3, 3].copy()

    @property
    def position(self) -> Point3D:
        """Get the position (translation) component. Alias for translation."""
        return self.translation

    def to_rotation_translation(self) -> Tuple[RotationMatrix, Point3D]:
        """Decompose into rotation and translation components."""
        return self.rotation_matrix, self.translation

    def to_position_quaternion(self) -> Tuple[Point3D, Quaternion]:
        """Decompose into position and quaternion (common in robotics)."""
        quat = Quaternion.from_rotation_matrix(self.rotation_matrix)
        return self.translation, quat

    def to_position_rpy(self) -> Tuple[Point3D, RPY]:
        """Decompose into position and RPY angles."""
        return self.translation, self.rotation_matrix.to_rpy()

    def transform_point(self, point: Point3D | np.ndarray) -> Point3D:
        """Transform a point using this transformation.

        Args:
            point: Point to transform

        Returns:
            Transformed point
        """
        if isinstance(point, Point3D):
            p = np.append(point.numpy, 1)
        elif isinstance(point, np.ndarray):
            if len(point) == 3:
                p = np.append(point, 1)
            elif len(point) == 4:
                p = point
            else:
                raise ValueError("Point must be 3D or 4D homogeneous")
        else:
            raise TypeError(f"Unsupported point type: {type(point)}")
        
        # Transform: p' = T @ p
        p_transformed = self._matrix @ p
        
        return Point3D(p_transformed[0], p_transformed[1], p_transformed[2])

    def transform_points(self, points: np.ndarray) -> np.ndarray:
        """Transform multiple points efficiently.

        Args:
            points: Nx3 array of points

        Returns:
            Nx3 array of transformed points
        """
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("Points must be Nx3 array")
        
        # Convert to homogeneous coordinates
        N = points.shape[0]
        points_h = np.ones((N, 4))
        points_h[:, :3] = points
        
        # Transform all points: (4x4) @ (4xN) = (4xN)
        points_transformed = (self._matrix @ points_h.T).T
        
        # Return only x, y, z
        return points_transformed[:, :3]

    def transform_vector(self, vector: Vector3D | np.ndarray) -> Vector3D:
        """Transform a vector (only rotation, no translation).

        Args:
            vector: Vector to transform

        Returns:
            Transformed vector
        """
        if isinstance(vector, Vector3D):
            v = vector.numpy
        elif isinstance(vector, np.ndarray):
            v = vector
        else:
            raise TypeError(f"Unsupported vector type: {type(vector)}")
        
        # Only apply rotation part
        v_transformed = self._matrix[:3, :3] @ v
        
        return Vector3D(*v_transformed)

    def compose(self, other: TransformationMatrix) -> TransformationMatrix:
        """Compose this transformation with another.

        This implements the operation: T_result = self @ other
        
        In terms of frames: if self transforms from frame A to B,
        and other transforms from frame B to C, then the result
        transforms from frame A to C.

        Args:
            other: Another transformation

        Returns:
            Composed transformation
        """
        return TransformationMatrix(self._matrix @ other._matrix)

    def __matmul__(self, other: TransformationMatrix) -> TransformationMatrix:
        """Matrix multiplication operator for composing transformations."""
        if isinstance(other, TransformationMatrix):
            return self.compose(other)
        else:
            raise TypeError(f"Cannot multiply TransformationMatrix with {type(other)}")

    def inverse(self) -> TransformationMatrix:
        """Get the inverse transformation.

        For a transformation T with rotation R and translation t,
        the inverse is:
        T^(-1) = [ R^T  -R^T @ t ]
                 [ 0      1      ]
        """
        T_inv = np.eye(4, dtype=np.float64)
        
        # Inverse rotation is transpose
        R_inv = self._matrix[:3, :3].T
        T_inv[:3, :3] = R_inv
        
        # Inverse translation
        T_inv[:3, 3] = -R_inv @ self._matrix[:3, 3]
        
        return TransformationMatrix(T_inv)

    def interpolate(self, other: TransformationMatrix, t: float) -> TransformationMatrix:
        """Interpolate between this and another transformation.

        Args:
            other: Target transformation
            t: Interpolation parameter (0 = self, 1 = other)

        Returns:
            Interpolated transformation
        """
        # Interpolate rotation using quaternion SLERP
        q1 = Quaternion.from_rotation_matrix(self.rotation_matrix)
        q2 = Quaternion.from_rotation_matrix(other.rotation_matrix)
        q_interp = Quaternion.slerp(q1, q2, t)
        
        # Linear interpolation for translation
        trans1 = self.translation_vector
        trans2 = other.translation_vector
        trans_interp = (1 - t) * trans1 + t * trans2
        
        return TransformationMatrix.from_rotation_translation(q_interp, trans_interp)

    def is_close(self, other: TransformationMatrix, tolerance: float = 1e-6) -> bool:
        """Check if two transformations are close."""
        return np.allclose(self._matrix, other._matrix, atol=tolerance)

    def copy(self) -> TransformationMatrix:
        """Create a copy of this transformation."""
        return TransformationMatrix(self._matrix.copy())

    def __repr__(self) -> str:
        """String representation."""
        pos = self.translation
        rpy = self.rotation_matrix.to_rpy()
        return (f"TransformationMatrix(position=({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}), "
                f"rpy=({np.rad2deg(rpy.roll):.1f}°, {np.rad2deg(rpy.pitch):.1f}°, {np.rad2deg(rpy.yaw):.1f}°))")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"Transform:\n{self._matrix}"

    # Frame transformation methods
    def change_frame(self, frame_transform: TransformationMatrix) -> TransformationMatrix:
        """Express this transformation in a different reference frame.

        If this transformation is T_AB (from frame A to B) and frame_transform
        is T_WA (from world to A), then the result is T_WB (from world to B).

        Args:
            frame_transform: Transformation to the new reference frame

        Returns:
            This transformation expressed in the new frame
        """
        return frame_transform @ self

    @classmethod
    def from_dh_parameters(cls, a: float, alpha: float, d: float, theta: float) -> TransformationMatrix:
        """Create transformation from Denavit-Hartenberg parameters.

        Common in robotics for describing kinematic chains.

        Args:
            a: Link length
            alpha: Link twist (radians)
            d: Link offset
            theta: Joint angle (radians)

        Returns:
            TransformationMatrix from DH parameters
        """
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)
        
        T = np.array([
            [ct, -st*ca,  st*sa, a*ct],
            [st,  ct*ca, -ct*sa, a*st],
            [0,   sa,     ca,    d   ],
            [0,   0,      0,     1   ]
        ], dtype=np.float64)
        
        return cls(T)

    def to_homogeneous_coordinates(self, point: Point3D | np.ndarray) -> np.ndarray:
        """Convert a 3D point to homogeneous coordinates [x, y, z, 1]."""
        if isinstance(point, Point3D):
            return np.array([point.x, point.y, point.z, 1.0])
        elif isinstance(point, np.ndarray) and len(point) == 3:
            return np.append(point, 1.0)
        else:
            raise ValueError("Input must be a Point3D or 3D numpy array")

    @property
    def x_axis(self) -> Vector3D:
        """Get the transformed X-axis direction."""
        return Vector3D(*self._matrix[:3, 0])

    @property
    def y_axis(self) -> Vector3D:
        """Get the transformed Y-axis direction."""
        return Vector3D(*self._matrix[:3, 1])

    @property
    def z_axis(self) -> Vector3D:
        """Get the transformed Z-axis direction."""
        return Vector3D(*self._matrix[:3, 2])
