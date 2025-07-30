from __future__ import annotations

import numpy as np

from .vector import Vector3D
from .rotation_matrix import RotationMatrix
from .quaternion import Quaternion
from .rpy import RPY
from .rotation_vector import RotationVector
from .axis_angle import AxisAngle


class TwoVectors:
    """
    Represents a rotation that aligns one vector to another.

    This representation is useful when you need to define a rotation that transforms
    a "from" vector to a "to" vector. The rotation is the minimal rotation that
    aligns the two vectors.

    Args:
        from_vector: Source vector (will be normalized)
        to_vector: Target vector (will be normalized)

    Examples:
        >>> # Create rotation that aligns X axis to a target direction
        >>> from_vec = Vector3D(1, 0, 0)
        >>> to_vec = Vector3D(1, 1, 0)
        >>> tv = TwoVectors(from_vec, to_vec)
        >>>
        >>> # Apply the rotation
        >>> v = Vector3D(1, 0, 0)
        >>> v_rotated = tv.apply_to_vector(v)  # Will align with to_vec
    """

    __slots__ = ("_from_vector", "_to_vector", "_axis", "_angle")  # Memory optimization

    def __init__(self, from_vector: Vector3D | np.ndarray, to_vector: Vector3D | np.ndarray) -> None:
        """Initialize with from and to vectors."""
        # Convert to Vector3D if needed
        if isinstance(from_vector, np.ndarray):
            from_vector = Vector3D.from_numpy(from_vector)
        elif not isinstance(from_vector, Vector3D):
            raise TypeError("from_vector must be Vector3D or numpy array")
        
        if isinstance(to_vector, np.ndarray):
            to_vector = Vector3D.from_numpy(to_vector)
        elif not isinstance(to_vector, Vector3D):
            raise TypeError("to_vector must be Vector3D or numpy array")
        
        # Check for zero vectors
        if from_vector.is_zero:
            raise ValueError("from_vector cannot be zero")
        if to_vector.is_zero:
            raise ValueError("to_vector cannot be zero")
        
        # Normalize vectors
        self._from_vector = from_vector.normalize()
        self._to_vector = to_vector.normalize()
        
        # Compute rotation axis and angle
        self._compute_rotation()

    def _compute_rotation(self) -> None:
        """Compute the rotation axis and angle."""
        dot = self._from_vector.dot(self._to_vector)
        
        if np.abs(dot - 1.0) < 1e-6:
            # Vectors are already aligned
            self._axis = Vector3D.unit_x()  # Arbitrary axis
            self._angle = 0.0
        elif np.abs(dot + 1.0) < 1e-6:
            # Vectors are opposite (180 degree rotation)
            # Find an orthogonal vector
            if np.abs(self._from_vector.x) < 0.9:
                ortho = Vector3D.unit_x()
            else:
                ortho = Vector3D.unit_y()
            
            self._axis = self._from_vector.cross(ortho).normalize()
            self._angle = np.pi
        else:
            # General case
            self._axis = self._from_vector.cross(self._to_vector).normalize()
            self._angle = np.arccos(np.clip(dot, -1, 1))

    @classmethod
    def identity(cls) -> TwoVectors:
        """Create an identity rotation (no rotation)."""
        v = Vector3D.unit_x()
        return cls(v, v)

    @classmethod
    def from_basis_vectors(cls, from_x: Vector3D, from_y: Vector3D, 
                          to_x: Vector3D, to_y: Vector3D) -> TwoVectors:
        """Create rotation from two sets of basis vectors.

        This creates a rotation that aligns the from_x, from_y basis to the
        to_x, to_y basis. The third axis is computed via cross product.

        Args:
            from_x: Source X axis
            from_y: Source Y axis
            to_x: Target X axis
            to_y: Target Y axis

        Returns:
            TwoVectors instance
        """
        # Complete the basis sets
        from_z = from_x.cross(from_y).normalize()
        to_z = to_x.cross(to_y).normalize()
        
        # Create rotation matrices
        R_from = np.column_stack([from_x.numpy, from_y.numpy, from_z.numpy])
        R_to = np.column_stack([to_x.numpy, to_y.numpy, to_z.numpy])
        
        # The rotation is R = R_to @ R_from^T
        R = R_to @ R_from.T
        rot_matrix = RotationMatrix(R)
        
        # Extract primary rotation
        axis, angle = rot_matrix.to_axis_angle()
        
        # Find the best from/to vectors that represent this rotation
        # Use the axis itself as it's invariant under the rotation
        if angle < 1e-6:
            return cls.identity()
        
        # Find a vector perpendicular to the axis
        axis_vec = Vector3D.from_numpy(axis)
        if np.abs(axis_vec.x) < 0.9:
            perp = Vector3D.unit_x()
        else:
            perp = Vector3D.unit_y()
        
        from_vec = axis_vec.cross(perp).normalize()
        to_vec = rot_matrix.apply_to_vector(from_vec.numpy)
        
        return cls(from_vec, Vector3D.from_numpy(to_vec))

    @classmethod
    def from_rotation_matrix(cls, rotation_matrix: RotationMatrix) -> TwoVectors:
        """Create from a rotation matrix.

        Note: This extracts one possible from/to vector pair that represents
        the rotation. There are infinitely many such pairs.

        Args:
            rotation_matrix: RotationMatrix instance

        Returns:
            TwoVectors instance
        """
        # Get axis and angle
        axis, angle = rotation_matrix.to_axis_angle()
        
        if angle < 1e-6:
            # Identity rotation
            return cls.identity()
        
        # Find a vector perpendicular to the axis
        axis_vec = Vector3D.from_numpy(axis)
        if np.abs(axis_vec.x) < 0.9:
            perp = Vector3D.unit_x()
        else:
            perp = Vector3D.unit_y()
        
        # Create from vector perpendicular to axis
        from_vec = axis_vec.cross(perp).normalize()
        
        # Apply rotation to get to vector
        to_vec = rotation_matrix.apply_to_vector(from_vec.numpy)
        
        return cls(from_vec, Vector3D.from_numpy(to_vec))

    @classmethod
    def from_quaternion(cls, quaternion: Quaternion) -> TwoVectors:
        """Create from a quaternion.

        Args:
            quaternion: Quaternion instance

        Returns:
            TwoVectors instance
        """
        return cls.from_rotation_matrix(quaternion.to_rotation_matrix())

    @classmethod
    def from_rpy(cls, rpy: RPY) -> TwoVectors:
        """Create from RPY angles.

        Args:
            rpy: RPY instance

        Returns:
            TwoVectors instance
        """
        return cls.from_rotation_matrix(RotationMatrix(rpy.to_rotation_matrix()))

    @classmethod
    def from_rotation_vector(cls, rotation_vector: RotationVector) -> TwoVectors:
        """Create from a rotation vector.

        Args:
            rotation_vector: RotationVector instance

        Returns:
            TwoVectors instance
        """
        return cls.from_rotation_matrix(rotation_vector.to_rotation_matrix())

    @classmethod
    def from_axis_angle(cls, axis_angle: AxisAngle) -> TwoVectors:
        """Create from an axis-angle representation.

        Args:
            axis_angle: AxisAngle instance

        Returns:
            TwoVectors instance
        """
        return cls.from_rotation_matrix(axis_angle.to_rotation_matrix())

    @property
    def from_vector(self) -> Vector3D:
        """Get the source vector (normalized)."""
        return self._from_vector.copy()

    @property
    def to_vector(self) -> Vector3D:
        """Get the target vector (normalized)."""
        return self._to_vector.copy()

    @property
    def axis(self) -> Vector3D:
        """Get the rotation axis."""
        return self._axis.copy()

    @property
    def angle(self) -> float:
        """Get the rotation angle in radians."""
        return self._angle

    @property
    def angle_degrees(self) -> float:
        """Get the rotation angle in degrees."""
        return np.rad2deg(self._angle)

    def to_axis_angle(self) -> AxisAngle:
        """Convert to axis-angle representation.

        Returns:
            AxisAngle instance
        """
        return AxisAngle(self._axis, self._angle)

    def to_rotation_matrix(self) -> RotationMatrix:
        """Convert to rotation matrix.

        Returns:
            RotationMatrix instance
        """
        return self.to_axis_angle().to_rotation_matrix()

    def to_quaternion(self) -> Quaternion:
        """Convert to quaternion representation.

        Returns:
            Quaternion instance
        """
        return self.to_axis_angle().to_quaternion()

    def to_rpy(self) -> RPY:
        """Convert to RPY angles.

        Returns:
            RPY instance
        """
        return self.to_rotation_matrix().to_rpy()

    def to_rotation_vector(self) -> RotationVector:
        """Convert to rotation vector.

        Returns:
            RotationVector instance
        """
        return self.to_axis_angle().to_rotation_vector()

    def apply_to_vector(self, vector: Vector3D | np.ndarray) -> Vector3D | np.ndarray:
        """Apply the rotation to a vector.

        Args:
            vector: Vector to rotate

        Returns:
            Rotated vector (same type as input)
        """
        # Use axis-angle for efficiency
        axis_angle = self.to_axis_angle()
        return axis_angle.apply_to_vector(vector)

    def compose(self, other: TwoVectors) -> TwoVectors:
        """Compose this rotation with another.

        Args:
            other: Another TwoVectors

        Returns:
            Composed TwoVectors
        """
        # Convert to rotation matrices for composition
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        R_composed = R1.compose(R2)
        
        return TwoVectors.from_rotation_matrix(R_composed)

    def inverse(self) -> TwoVectors:
        """Get the inverse rotation.

        Returns:
            Inverse TwoVectors
        """
        # Swap from and to vectors
        return TwoVectors(self._to_vector, self._from_vector)

    def power(self, exponent: float) -> TwoVectors:
        """Raise rotation to a power (fractional rotations).

        Args:
            exponent: Power to raise the rotation to

        Returns:
            New TwoVectors
        """
        # Use axis-angle representation
        axis_angle = self.to_axis_angle()
        scaled = axis_angle.power(exponent)
        return TwoVectors.from_axis_angle(scaled)

    def interpolate(self, other: TwoVectors, t: float) -> TwoVectors:
        """Interpolate between rotations.

        Args:
            other: Target rotation
            t: Interpolation parameter [0, 1]

        Returns:
            Interpolated TwoVectors
        """
        # Convert to quaternions for SLERP
        q1 = self.to_quaternion()
        q2 = other.to_quaternion()
        q_interp = Quaternion.slerp(q1, q2, t)
        
        return TwoVectors.from_quaternion(q_interp)

    def distance_to(self, other: TwoVectors) -> float:
        """Compute angular distance to another rotation.

        Args:
            other: Another TwoVectors

        Returns:
            Angular distance in radians
        """
        # Use quaternions for distance
        q1 = self.to_quaternion()
        q2 = other.to_quaternion()
        return q1.distance_to(q2)

    def is_close(self, other: TwoVectors, tolerance: float = 1e-6) -> bool:
        """Check if this rotation is close to another.

        Args:
            other: Another TwoVectors
            tolerance: Tolerance for comparison

        Returns:
            True if rotations are close
        """
        # Compare rotation matrices
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()
        return R1.is_close(R2, tolerance)

    def copy(self) -> TwoVectors:
        """Create a copy of this TwoVectors."""
        return TwoVectors(self._from_vector, self._to_vector)

    def __repr__(self) -> str:
        """String representation."""
        return (f"TwoVectors(from=[{self._from_vector.x:.3f}, {self._from_vector.y:.3f}, "
                f"{self._from_vector.z:.3f}], to=[{self._to_vector.x:.3f}, "
                f"{self._to_vector.y:.3f}, {self._to_vector.z:.3f}], "
                f"angle={self.angle_degrees:.1f}°)")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"TwoVectors({self._from_vector} → {self._to_vector})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another TwoVectors."""
        if not isinstance(other, TwoVectors):
            return NotImplemented
        
        # Check if they represent the same rotation
        return (self._from_vector.is_close(other._from_vector) and 
                self._to_vector.is_close(other._to_vector))

    def __ne__(self, other: object) -> bool:
        """Check inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function."""
        return hash((self._from_vector, self._to_vector))
