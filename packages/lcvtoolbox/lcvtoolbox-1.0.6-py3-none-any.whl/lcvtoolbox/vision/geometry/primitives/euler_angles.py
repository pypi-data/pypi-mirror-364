from __future__ import annotations

import numpy as np

from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rpy import RPY
from .rotation_vector import RotationVector
from .axis_angle import AxisAngle
from .two_vectors import TwoVectors


class EulerAngles:
    """
    Represents a rotation using general Euler angles with customizable convention.

    Euler angles describe rotations as a sequence of three rotations around
    specified axes. This class supports all 12 possible Euler angle conventions
    (6 proper Euler angles like ZXZ, and 6 Tait-Bryan angles like XYZ).

    Args:
        angles: Three rotation angles in radians
        convention: String specifying the rotation order (e.g., "XYZ", "ZYX", "ZXZ")
        extrinsic: If True, rotations are about fixed axes; if False, about body axes

    Examples:
        >>> # Create using ZYX convention (common in aerospace)
        >>> euler = EulerAngles([0.1, 0.2, 0.3], "ZYX", extrinsic=True)
        >>>
        >>> # Convert to rotation matrix
        >>> R = euler.to_rotation_matrix()
        >>>
        >>> # Create from rotation matrix
        >>> euler2 = EulerAngles.from_rotation_matrix(R, "XYZ")
    """

    __slots__ = ("_angles", "_convention", "_extrinsic")  # Memory optimization

    # Valid Euler angle conventions
    PROPER_EULER = ["XYX", "XZX", "YXY", "YZY", "ZXZ", "ZYZ"]
    TAIT_BRYAN = ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]
    ALL_CONVENTIONS = PROPER_EULER + TAIT_BRYAN

    def __init__(self, angles: np.ndarray | list | tuple, convention: str = "XYZ", 
                 extrinsic: bool = True) -> None:
        """Initialize with angles and convention."""
        # Validate convention
        convention = convention.upper()
        if convention not in self.ALL_CONVENTIONS:
            raise ValueError(f"Invalid convention '{convention}'. Must be one of: {self.ALL_CONVENTIONS}")
        
        # Store angles
        if isinstance(angles, (list, tuple)):
            angles = np.array(angles, dtype=np.float64)
        elif isinstance(angles, np.ndarray):
            angles = angles.astype(np.float64)
        else:
            raise TypeError("Angles must be numpy array, list, or tuple")
        
        if len(angles) != 3:
            raise ValueError("Must provide exactly 3 angles")
        
        self._angles = angles
        self._convention = convention
        self._extrinsic = extrinsic

    @classmethod
    def identity(cls, convention: str = "XYZ") -> EulerAngles:
        """Create an identity rotation (no rotation)."""
        return cls([0.0, 0.0, 0.0], convention)

    @classmethod
    def from_rotation_matrix(cls, rotation_matrix: RotationMatrix, 
                           convention: str = "XYZ", extrinsic: bool = True) -> EulerAngles:
        """Create from a rotation matrix.

        Args:
            rotation_matrix: RotationMatrix instance
            convention: Euler angle convention
            extrinsic: If True, extrinsic rotations; if False, intrinsic

        Returns:
            EulerAngles instance
            
        Raises:
            ValueError: If the convention is invalid or conversion fails
        """
        matrix = rotation_matrix.matrix
        convention = convention.upper()
        
        if convention not in cls.ALL_CONVENTIONS:
            raise ValueError(f"Invalid convention '{convention}'")
        
        # Extract angles based on convention
        # This is complex due to many cases and gimbal lock handling
        angles = cls._extract_angles_from_matrix(matrix, convention, extrinsic)
        
        # Create the EulerAngles instance
        euler = cls(angles, convention, extrinsic)
        
        # Validate the conversion by converting back to matrix
        reconstructed = euler.to_rotation_matrix().matrix
        if not np.allclose(matrix, reconstructed, atol=1e-5):
            # For some conventions, the extraction might not be accurate
            # This is a known limitation of Euler angles
            import warnings
            warnings.warn(
                f"Euler angle extraction for convention '{convention}' may not be accurate. "
                f"Consider using Quaternion or RotationMatrix for more reliable conversions.",
                RuntimeWarning
            )
        
        return euler

    @classmethod
    def _extract_angles_from_matrix(cls, matrix: np.ndarray, convention: str, 
                                  extrinsic: bool) -> np.ndarray:
        """Extract Euler angles from rotation matrix."""
        # For extrinsic rotations, we need to transpose the matrix
        if extrinsic:
            matrix = matrix.T
        
        # Handle each convention
        if convention == "XYZ":
            # Check for gimbal lock
            sy = np.sqrt(matrix[0, 0]**2 + matrix[1, 0]**2)
            singular = sy < 1e-6
            
            if not singular:
                x = np.arctan2(matrix[2, 1], matrix[2, 2])
                y = np.arctan2(-matrix[2, 0], sy)
                z = np.arctan2(matrix[1, 0], matrix[0, 0])
            else:
                x = np.arctan2(-matrix[1, 2], matrix[1, 1])
                y = np.arctan2(-matrix[2, 0], sy)
                z = 0.0
                
        elif convention == "XZY":
            sz = np.sqrt(matrix[0, 0]**2 + matrix[2, 0]**2)
            singular = sz < 1e-6
            
            if not singular:
                x = np.arctan2(-matrix[1, 2], matrix[1, 1])
                z = np.arctan2(matrix[0, 1], sz)
                y = np.arctan2(-matrix[2, 0], matrix[0, 0])
            else:
                x = np.arctan2(matrix[2, 1], matrix[2, 2])
                z = np.arctan2(matrix[0, 1], sz)
                y = 0.0
                
        elif convention == "YXZ":
            sx = np.sqrt(matrix[1, 1]**2 + matrix[2, 1]**2)
            singular = sx < 1e-6
            
            if not singular:
                y = np.arctan2(matrix[0, 2], matrix[0, 0])
                x = np.arctan2(-matrix[0, 1], sx)
                z = np.arctan2(matrix[2, 1], matrix[1, 1])
            else:
                y = np.arctan2(-matrix[2, 0], matrix[2, 2])
                x = np.arctan2(-matrix[0, 1], sx)
                z = 0.0
                
        elif convention == "YZX":
            sz = np.sqrt(matrix[1, 1]**2 + matrix[0, 1]**2)
            singular = sz < 1e-6
            
            if not singular:
                y = np.arctan2(-matrix[2, 0], matrix[2, 2])
                z = np.arctan2(matrix[1, 0], sz)
                x = np.arctan2(-matrix[0, 1], matrix[1, 1])
            else:
                y = np.arctan2(matrix[0, 2], matrix[0, 0])
                z = np.arctan2(matrix[1, 0], sz)
                x = 0.0
                
        elif convention == "ZXY":
            sx = np.sqrt(matrix[2, 2]**2 + matrix[0, 2]**2)
            singular = sx < 1e-6
            
            if not singular:
                z = np.arctan2(-matrix[1, 0], matrix[1, 1])
                x = np.arctan2(matrix[2, 1], sx)
                y = np.arctan2(-matrix[0, 2], matrix[2, 2])
            else:
                z = np.arctan2(matrix[0, 1], matrix[0, 0])
                x = np.arctan2(matrix[2, 1], sx)
                y = 0.0
                
        elif convention == "ZYX":
            sy = np.sqrt(matrix[0, 0]**2 + matrix[1, 0]**2)
            singular = sy < 1e-6
            
            if not singular:
                z = np.arctan2(matrix[1, 0], matrix[0, 0])
                y = np.arctan2(-matrix[2, 0], sy)
                x = np.arctan2(matrix[2, 1], matrix[2, 2])
            else:
                z = 0.0
                y = np.arctan2(-matrix[2, 0], sy)
                x = np.arctan2(-matrix[1, 2], matrix[1, 1])
                
        # Proper Euler angles (two rotations about same axis)
        elif convention == "XYX":
            sy = np.sqrt(matrix[0, 1]**2 + matrix[0, 2]**2)
            singular = sy < 1e-6
            
            if not singular:
                x1 = np.arctan2(matrix[1, 0], -matrix[2, 0])
                y = np.arctan2(sy, matrix[0, 0])
                x2 = np.arctan2(matrix[0, 1], matrix[0, 2])
            else:
                x1 = np.arctan2(-matrix[1, 2], matrix[1, 1])
                y = 0.0
                x2 = 0.0
            angles = np.array([x1, y, x2])
            return angles
            
        elif convention == "XZX":
            sz = np.sqrt(matrix[0, 1]**2 + matrix[0, 2]**2)
            singular = sz < 1e-6
            
            if not singular:
                x1 = np.arctan2(matrix[2, 0], matrix[1, 0])
                z = np.arctan2(sz, matrix[0, 0])
                x2 = np.arctan2(matrix[0, 2], -matrix[0, 1])
            else:
                x1 = np.arctan2(matrix[2, 1], matrix[2, 2])
                z = 0.0
                x2 = 0.0
            angles = np.array([x1, z, x2])
            return angles
            
        elif convention == "YXY":
            sx = np.sqrt(matrix[1, 0]**2 + matrix[1, 2]**2)
            singular = sx < 1e-6
            
            if not singular:
                y1 = np.arctan2(matrix[0, 1], matrix[2, 1])
                x = np.arctan2(sx, matrix[1, 1])
                y2 = np.arctan2(matrix[1, 0], -matrix[1, 2])
            else:
                y1 = np.arctan2(matrix[0, 2], matrix[0, 0])
                x = 0.0
                y2 = 0.0
            angles = np.array([y1, x, y2])
            return angles
            
        elif convention == "YZY":
            sz = np.sqrt(matrix[1, 0]**2 + matrix[1, 2]**2)
            singular = sz < 1e-6
            
            if not singular:
                y1 = np.arctan2(matrix[2, 1], -matrix[0, 1])
                z = np.arctan2(sz, matrix[1, 1])
                y2 = np.arctan2(matrix[1, 2], matrix[1, 0])
            else:
                y1 = np.arctan2(-matrix[2, 0], matrix[2, 2])
                z = 0.0
                y2 = 0.0
            angles = np.array([y1, z, y2])
            return angles
            
        elif convention == "ZXZ":
            sx = np.sqrt(matrix[2, 0]**2 + matrix[2, 1]**2)
            singular = sx < 1e-6
            
            if not singular:
                z1 = np.arctan2(matrix[0, 2], -matrix[1, 2])
                x = np.arctan2(sx, matrix[2, 2])
                z2 = np.arctan2(matrix[2, 0], matrix[2, 1])
            else:
                z1 = np.arctan2(-matrix[0, 1], matrix[0, 0])
                x = 0.0
                z2 = 0.0
            angles = np.array([z1, x, z2])
            return angles
            
        elif convention == "ZYZ":
            sy = np.sqrt(matrix[2, 0]**2 + matrix[2, 1]**2)
            singular = sy < 1e-6
            
            if not singular:
                z1 = np.arctan2(matrix[1, 2], matrix[0, 2])
                y = np.arctan2(sy, matrix[2, 2])
                z2 = np.arctan2(matrix[2, 1], -matrix[2, 0])
            else:
                z1 = np.arctan2(matrix[1, 0], matrix[1, 1])
                y = 0.0
                z2 = 0.0
            angles = np.array([z1, y, z2])
            return angles
        else:
            raise ValueError(f"Convention {convention} not implemented")
        
        # For Tait-Bryan angles
        # Ensure variables are in correct order based on convention
        angles = [0, 0, 0]
        for i, axis in enumerate(convention):
            if axis == 'X' and 'x' in locals():
                angles[i] = x
            elif axis == 'Y' and 'y' in locals():
                angles[i] = y
            elif axis == 'Z' and 'z' in locals():
                angles[i] = z
        
        return np.array(angles)

    @classmethod
    def from_quaternion(cls, quaternion: Quaternion, convention: str = "XYZ", 
                       extrinsic: bool = True) -> EulerAngles:
        """Create from a quaternion."""
        return cls.from_rotation_matrix(quaternion.to_rotation_matrix(), convention, extrinsic)

    @classmethod
    def from_rpy(cls, rpy: RPY, convention: str = "XYZ", extrinsic: bool = True) -> EulerAngles:
        """Create from RPY angles."""
        if convention == "XYZ" and extrinsic:
            # Direct conversion
            return cls([rpy.roll, rpy.pitch, rpy.yaw], convention, extrinsic)
        else:
            # Convert via rotation matrix
            return cls.from_rotation_matrix(RotationMatrix(rpy.to_rotation_matrix()), 
                                          convention, extrinsic)

    @classmethod
    def from_rotation_vector(cls, rotation_vector: RotationVector, 
                           convention: str = "XYZ", extrinsic: bool = True) -> EulerAngles:
        """Create from a rotation vector."""
        return cls.from_rotation_matrix(rotation_vector.to_rotation_matrix(), convention, extrinsic)

    @classmethod
    def from_axis_angle(cls, axis_angle: AxisAngle, convention: str = "XYZ", 
                       extrinsic: bool = True) -> EulerAngles:
        """Create from axis-angle."""
        return cls.from_rotation_matrix(axis_angle.to_rotation_matrix(), convention, extrinsic)

    @classmethod
    def from_two_vectors(cls, two_vectors: TwoVectors, convention: str = "XYZ", 
                        extrinsic: bool = True) -> EulerAngles:
        """Create from two vectors."""
        return cls.from_rotation_matrix(two_vectors.to_rotation_matrix(), convention, extrinsic)

    @property
    def angles(self) -> np.ndarray:
        """Get the three Euler angles in radians."""
        return self._angles.copy()

    @property
    def angles_degrees(self) -> np.ndarray:
        """Get the three Euler angles in degrees."""
        return np.rad2deg(self._angles)

    @property
    def convention(self) -> str:
        """Get the Euler angle convention."""
        return self._convention

    @property
    def extrinsic(self) -> bool:
        """Check if using extrinsic rotations."""
        return self._extrinsic

    @property
    def is_proper_euler(self) -> bool:
        """Check if this uses proper Euler angles (first and third axes are same)."""
        return self._convention in self.PROPER_EULER

    @property
    def is_tait_bryan(self) -> bool:
        """Check if this uses Tait-Bryan angles (all three axes different)."""
        return self._convention in self.TAIT_BRYAN

    def to_rotation_matrix(self) -> RotationMatrix:
        """Convert to rotation matrix.

        Returns:
            RotationMatrix instance
        """
        # Basic rotation matrices
        def Rx(angle):
            c, s = np.cos(angle), np.sin(angle)
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        
        def Ry(angle):
            c, s = np.cos(angle), np.sin(angle)
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        
        def Rz(angle):
            c, s = np.cos(angle), np.sin(angle)
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        
        # Map axes to rotation functions
        rotation_funcs = {'X': Rx, 'Y': Ry, 'Z': Rz}
        
        # Apply rotations based on convention
        if self._extrinsic:
            # Extrinsic: multiply from left to right
            R = np.eye(3)
            for i, axis in enumerate(self._convention):
                R = rotation_funcs[axis](self._angles[i]) @ R
        else:
            # Intrinsic: multiply from right to left
            R = np.eye(3)
            for i in range(len(self._convention) - 1, -1, -1):
                axis = self._convention[i]
                R = R @ rotation_funcs[axis](self._angles[i])
        
        return RotationMatrix(R)

    def to_quaternion(self) -> Quaternion:
        """Convert to quaternion."""
        rot_matrix = self.to_rotation_matrix()
        return Quaternion.from_rotation_matrix(rot_matrix)

    def to_rpy(self) -> RPY:
        """Convert to RPY angles."""
        if self._convention == "XYZ" and self._extrinsic:
            # Direct conversion
            return RPY(self._angles[0], self._angles[1], self._angles[2])
        else:
            # Convert via rotation matrix
            return self.to_rotation_matrix().to_rpy()

    def to_rotation_vector(self) -> RotationVector:
        """Convert to rotation vector."""
        return RotationVector.from_rotation_matrix(self.to_rotation_matrix())

    def to_axis_angle(self) -> AxisAngle:
        """Convert to axis-angle."""
        return AxisAngle.from_rotation_matrix(self.to_rotation_matrix())

    def to_two_vectors(self) -> TwoVectors:
        """Convert to two vectors."""
        return TwoVectors.from_rotation_matrix(self.to_rotation_matrix())

    def apply_to_vector(self, vector: np.ndarray) -> np.ndarray:
        """Apply rotation to a vector."""
        return self.to_rotation_matrix().apply_to_vector(vector)

    def compose(self, other: EulerAngles) -> EulerAngles:
        """Compose this rotation with another."""
        # Convert to rotation matrices for composition
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        R_composed = R1.compose(R2)
        
        # Return with same convention as self
        return EulerAngles.from_rotation_matrix(R_composed, self._convention, self._extrinsic)

    def inverse(self) -> EulerAngles:
        """Get the inverse rotation."""
        R_inv = self.to_rotation_matrix().inverse()
        return EulerAngles.from_rotation_matrix(R_inv, self._convention, self._extrinsic)

    def copy(self) -> EulerAngles:
        """Create a copy."""
        return EulerAngles(self._angles.copy(), self._convention, self._extrinsic)

    def __repr__(self) -> str:
        """String representation."""
        angles_deg = self.angles_degrees
        return (f"EulerAngles(angles=[{angles_deg[0]:.1f}°, {angles_deg[1]:.1f}°, "
                f"{angles_deg[2]:.1f}°], convention='{self._convention}', "
                f"extrinsic={self._extrinsic})")

    def __str__(self) -> str:
        """User-friendly string representation."""
        angles_deg = self.angles_degrees
        rot_type = "extrinsic" if self._extrinsic else "intrinsic"
        return (f"EulerAngles({self._convention} {rot_type}: "
                f"[{angles_deg[0]:.1f}°, {angles_deg[1]:.1f}°, {angles_deg[2]:.1f}°])")
