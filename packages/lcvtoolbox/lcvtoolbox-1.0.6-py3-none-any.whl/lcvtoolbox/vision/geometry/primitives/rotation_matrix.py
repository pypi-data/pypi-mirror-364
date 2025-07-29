from __future__ import annotations

import numpy as np

from .rpy import RPY


class RotationMatrix:
    """
    Represents a 3x3 rotation matrix for 3D transformations.

    This class provides a robust interface for working with rotation matrices,
    including creation from various sources, composition, and conversion to
    other rotation representations.

    Args:
        matrix: A 3x3 numpy array representing the rotation matrix

    Examples:
        >>> # Create from RPY angles
        >>> rpy = RPY(roll=0.1, pitch=0.2, yaw=0.3)
        >>> rot_mat = RotationMatrix.from_rpy(rpy)
        >>>
        >>> # Create from axis-angle
        >>> axis = np.array([0, 0, 1])
        >>> angle = np.pi / 4
        >>> rot_mat = RotationMatrix.from_axis_angle(axis, angle)
        >>>
        >>> # Compose rotations
        >>> rot1 = RotationMatrix.from_rpy(RPY(0.1, 0, 0))
        >>> rot2 = RotationMatrix.from_rpy(RPY(0, 0.2, 0))
        >>> rot_combined = rot1.compose(rot2)
    """

    __slots__ = ("_data",)  # Memory optimization

    def __init__(self, matrix: np.ndarray) -> None:
        """Initialize with a 3x3 rotation matrix.
        
        Args:
            matrix: 3x3 numpy array
            
        Raises:
            ValueError: If matrix is not 3x3 or not a valid rotation matrix
        """
        if matrix.shape != (3, 3):
            raise ValueError("Matrix must be 3x3")
        
        self._data = matrix.astype(np.float64)
        
        # Validate that it's a proper rotation matrix
        if not self._is_valid_rotation_matrix():
            # Try to orthogonalize it
            self._data = self._orthogonalize()
            if not self._is_valid_rotation_matrix():
                raise ValueError("Invalid rotation matrix: not orthogonal with determinant 1")

    def _is_valid_rotation_matrix(self, tolerance: float = 1e-6) -> bool:
        """Check if the matrix is a valid rotation matrix."""
        # Check if R^T * R = I
        should_be_identity = self._data.T @ self._data
        identity_check = np.allclose(should_be_identity, np.eye(3), atol=tolerance)
        
        # Check if determinant is 1 (not -1)
        det_check = np.abs(np.linalg.det(self._data) - 1.0) < tolerance
        
        return identity_check and det_check

    def _orthogonalize(self) -> np.ndarray:
        """Orthogonalize the matrix using SVD."""
        U, _, Vt = np.linalg.svd(self._data)
        R = U @ Vt
        
        # Ensure positive determinant
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = U @ Vt
        
        return R

    @classmethod
    def identity(cls) -> RotationMatrix:
        """Create an identity rotation matrix (no rotation)."""
        return cls(np.eye(3))

    @classmethod
    def from_rpy(cls, rpy: RPY) -> RotationMatrix:
        """Create a rotation matrix from RPY angles.
        
        Args:
            rpy: RPY instance containing roll, pitch, yaw angles
            
        Returns:
            RotationMatrix instance
        """
        return cls(rpy.to_rotation_matrix())

    @classmethod
    def from_axis_angle(cls, axis: np.ndarray, angle: float) -> RotationMatrix:
        """Create a rotation matrix from axis-angle representation.
        
        Uses Rodrigues' rotation formula.
        
        Args:
            axis: 3D vector representing the rotation axis (will be normalized)
            angle: Rotation angle in radians
            
        Returns:
            RotationMatrix instance
        """
        # Normalize the axis
        axis = np.array(axis, dtype=np.float64)
        axis_norm = np.linalg.norm(axis)
        
        if axis_norm == 0:
            return cls.identity()
        
        axis = axis / axis_norm
        
        # Rodrigues' formula
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Cross product matrix
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        
        # Rotation matrix
        R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
        
        return cls(R)

    @classmethod
    def from_quaternion(cls, quaternion: np.ndarray) -> RotationMatrix:
        """Create a rotation matrix from a quaternion.
        
        Args:
            quaternion: Quaternion as [w, x, y, z] or [x, y, z, w]
                       (will auto-detect based on which component is largest)
            
        Returns:
            RotationMatrix instance
        """
        q = np.array(quaternion, dtype=np.float64)
        
        if len(q) != 4:
            raise ValueError("Quaternion must have 4 components")
        
        # Normalize quaternion
        q = q / np.linalg.norm(q)
        
        # Assume scalar-first convention [w, x, y, z]
        # If the last component is the largest, assume scalar-last [x, y, z, w]
        if np.abs(q[3]) > np.abs(q[0]):
            q = np.array([q[3], q[0], q[1], q[2]])
        
        w, x, y, z = q
        
        # Convert to rotation matrix
        R = np.array([
            [1 - 2*(y**2 + z**2), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x**2 + z**2), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x**2 + y**2)]
        ])
        
        return cls(R)

    @classmethod
    def from_euler_angles(cls, angles: np.ndarray, order: str = "XYZ") -> RotationMatrix:
        """Create a rotation matrix from Euler angles with specified order.
        
        Args:
            angles: Array of three angles in radians
            order: Rotation order string (e.g., "XYZ", "ZYX", "ZXZ")
                  Each letter represents a rotation axis
            
        Returns:
            RotationMatrix instance
        """
        if len(angles) != 3:
            raise ValueError("Must provide exactly 3 angles")
        
        if len(order) != 3:
            raise ValueError("Order must be a 3-character string")
        
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
        
        # Apply rotations in specified order
        R = np.eye(3)
        for i, axis in enumerate(order):
            if axis not in rotation_funcs:
                raise ValueError(f"Invalid axis: {axis}")
            R = R @ rotation_funcs[axis](angles[i])
        
        return cls(R)

    @classmethod
    def from_two_vectors(cls, from_vec: np.ndarray, to_vec: np.ndarray) -> RotationMatrix:
        """Create a rotation matrix that rotates from_vec to to_vec.
        
        Args:
            from_vec: Source vector (will be normalized)
            to_vec: Target vector (will be normalized)
            
        Returns:
            RotationMatrix instance
        """
        # Normalize vectors
        v1 = np.array(from_vec, dtype=np.float64)
        v2 = np.array(to_vec, dtype=np.float64)
        
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)
        
        # Check if vectors are parallel
        cos_angle = np.dot(v1, v2)
        
        if np.abs(cos_angle - 1.0) < 1e-6:
            # Vectors are already aligned
            return cls.identity()
        elif np.abs(cos_angle + 1.0) < 1e-6:
            # Vectors are opposite, need 180 degree rotation
            # Find an orthogonal vector
            if np.abs(v1[0]) < 0.9:
                ortho = np.array([1, 0, 0])
            else:
                ortho = np.array([0, 1, 0])
            
            axis = np.cross(v1, ortho)
            axis = axis / np.linalg.norm(axis)
            return cls.from_axis_angle(axis, np.pi)
        else:
            # General case
            axis = np.cross(v1, v2)
            axis = axis / np.linalg.norm(axis)
            angle = np.arccos(cos_angle)
            return cls.from_axis_angle(axis, angle)

    @classmethod
    def random(cls) -> RotationMatrix:
        """Generate a random rotation matrix using uniform distribution."""
        # Use QR decomposition of random matrix
        random_matrix = np.random.randn(3, 3)
        Q, R = np.linalg.qr(random_matrix)
        
        # Ensure positive determinant
        if np.linalg.det(Q) < 0:
            Q[:, 0] *= -1
        
        return cls(Q)

    @property
    def matrix(self) -> np.ndarray:
        """Get the rotation matrix as a numpy array."""
        return self._data.copy()

    @property
    def determinant(self) -> float:
        """Get the determinant of the rotation matrix (should be 1)."""
        return float(np.linalg.det(self._data))

    @property
    def trace(self) -> float:
        """Get the trace of the rotation matrix."""
        return float(np.trace(self._data))

    def to_rpy(self) -> RPY:
        """Convert to RPY (roll, pitch, yaw) angles.
        
        Returns:
            RPY instance
        """
        return RPY.from_rotation_matrix(self._data)

    def to_axis_angle(self) -> tuple[np.ndarray, float]:
        """Convert to axis-angle representation.
        
        Returns:
            Tuple of (axis, angle) where axis is a unit 3D vector
            and angle is in radians
        """
        # Extract angle from trace
        trace = self.trace
        angle = np.arccos(np.clip((trace - 1) / 2, -1, 1))
        
        if np.abs(angle) < 1e-6:
            # No rotation
            return np.array([1, 0, 0]), 0.0
        elif np.abs(angle - np.pi) < 1e-6:
            # 180 degree rotation, need to find axis differently
            # Find the largest diagonal element
            diag = np.diag(self._data)
            idx = np.argmax(diag)
            
            axis = np.zeros(3)
            axis[idx] = np.sqrt((diag[idx] + 1) / 2)
            
            for i in range(3):
                if i != idx:
                    axis[i] = self._data[idx, i] / (2 * axis[idx])
            
            return axis / np.linalg.norm(axis), angle
        else:
            # General case
            axis = np.array([
                self._data[2, 1] - self._data[1, 2],
                self._data[0, 2] - self._data[2, 0],
                self._data[1, 0] - self._data[0, 1]
            ])
            axis = axis / (2 * np.sin(angle))
            
            return axis, angle

    def to_quaternion(self, scalar_first: bool = True) -> np.ndarray:
        """Convert to quaternion representation.
        
        Args:
            scalar_first: If True, return [w, x, y, z], else [x, y, z, w]
            
        Returns:
            Quaternion as numpy array
        """
        # Based on Shepperd's method
        trace = self.trace
        
        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (self._data[2, 1] - self._data[1, 2]) * s
            y = (self._data[0, 2] - self._data[2, 0]) * s
            z = (self._data[1, 0] - self._data[0, 1]) * s
        else:
            if self._data[0, 0] > self._data[1, 1] and self._data[0, 0] > self._data[2, 2]:
                s = 2.0 * np.sqrt(1.0 + self._data[0, 0] - self._data[1, 1] - self._data[2, 2])
                w = (self._data[2, 1] - self._data[1, 2]) / s
                x = 0.25 * s
                y = (self._data[0, 1] + self._data[1, 0]) / s
                z = (self._data[0, 2] + self._data[2, 0]) / s
            elif self._data[1, 1] > self._data[2, 2]:
                s = 2.0 * np.sqrt(1.0 + self._data[1, 1] - self._data[0, 0] - self._data[2, 2])
                w = (self._data[0, 2] - self._data[2, 0]) / s
                x = (self._data[0, 1] + self._data[1, 0]) / s
                y = 0.25 * s
                z = (self._data[1, 2] + self._data[2, 1]) / s
            else:
                s = 2.0 * np.sqrt(1.0 + self._data[2, 2] - self._data[0, 0] - self._data[1, 1])
                w = (self._data[1, 0] - self._data[0, 1]) / s
                x = (self._data[0, 2] + self._data[2, 0]) / s
                y = (self._data[1, 2] + self._data[2, 1]) / s
                z = 0.25 * s
        
        if scalar_first:
            return np.array([w, x, y, z])
        else:
            return np.array([x, y, z, w])

    def apply_to_vector(self, vector: np.ndarray) -> np.ndarray:
        """Apply rotation to a 3D vector.
        
        Args:
            vector: 3D vector or array of vectors
            
        Returns:
            Rotated vector(s)
        """
        vector = np.array(vector)
        
        if vector.ndim == 1:
            # Single vector
            if len(vector) != 3:
                raise ValueError("Vector must be 3D")
            return self._data @ vector
        elif vector.ndim == 2:
            # Multiple vectors
            if vector.shape[1] != 3:
                raise ValueError("Vectors must be 3D (shape [..., 3])")
            return (self._data @ vector.T).T
        else:
            raise ValueError("Vector must be 1D or 2D array")

    def compose(self, other: RotationMatrix) -> RotationMatrix:
        """Compose this rotation with another.
        
        The resulting rotation is equivalent to applying this rotation
        followed by the other rotation.
        
        Args:
            other: Another RotationMatrix instance
            
        Returns:
            New RotationMatrix representing the composed rotation
        """
        return RotationMatrix(other._data @ self._data)

    def inverse(self) -> RotationMatrix:
        """Get the inverse rotation.
        
        For rotation matrices, the inverse is the transpose.
        
        Returns:
            New RotationMatrix representing the inverse rotation
        """
        return RotationMatrix(self._data.T)

    def power(self, exponent: float) -> RotationMatrix:
        """Raise the rotation to a power (fractional rotations).
        
        Args:
            exponent: Power to raise the rotation to
            
        Returns:
            New RotationMatrix
        """
        axis, angle = self.to_axis_angle()
        return RotationMatrix.from_axis_angle(axis, angle * exponent)

    def interpolate(self, other: RotationMatrix, t: float) -> RotationMatrix:
        """Spherical linear interpolation (SLERP) between rotations.
        
        Args:
            other: Target rotation
            t: Interpolation parameter (0.0 to 1.0)
            
        Returns:
            Interpolated RotationMatrix
        """
        # Compute relative rotation
        R_rel = other._data @ self._data.T
        
        # Convert to axis-angle
        axis, angle = RotationMatrix(R_rel).to_axis_angle()
        
        # Interpolate angle
        interpolated_angle = angle * t
        
        # Create interpolated relative rotation
        R_interp_rel = RotationMatrix.from_axis_angle(axis, interpolated_angle)
        
        # Apply to original rotation
        return RotationMatrix(R_interp_rel._data @ self._data)

    def distance_to(self, other: RotationMatrix) -> float:
        """Compute the angular distance to another rotation.
        
        Args:
            other: Another RotationMatrix
            
        Returns:
            Angular distance in radians
        """
        R_rel = other._data @ self._data.T
        trace = np.trace(R_rel)
        return np.arccos(np.clip((trace - 1) / 2, -1, 1))

    def is_close(self, other: RotationMatrix, tolerance: float = 1e-6) -> bool:
        """Check if this rotation is close to another.
        
        Args:
            other: Another RotationMatrix
            tolerance: Tolerance for comparison
            
        Returns:
            True if rotations are close
        """
        return np.allclose(self._data, other._data, atol=tolerance)

    def align_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Apply rotation to align a set of vectors.
        
        This is an alias for apply_to_vector for clarity.
        
        Args:
            vectors: Array of 3D vectors
            
        Returns:
            Aligned vectors
        """
        return self.apply_to_vector(vectors)

    def copy(self) -> RotationMatrix:
        """Create a copy of this rotation matrix."""
        return RotationMatrix(self._data.copy())

    def __repr__(self) -> str:
        """String representation of the rotation matrix."""
        rpy = self.to_rpy()
        rpy_deg = rpy.to_degrees()
        return (f"RotationMatrix(rpy=[{rpy_deg.roll:.1f}°, "
                f"{rpy_deg.pitch:.1f}°, {rpy_deg.yaw:.1f}°])")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"RotationMatrix:\n{self._data}"

    def __eq__(self, other: object) -> bool:
        """Check equality with another RotationMatrix."""
        if not isinstance(other, RotationMatrix):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another RotationMatrix."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for RotationMatrix objects."""
        return hash(self._data.tobytes())

    def __matmul__(self, other: RotationMatrix) -> RotationMatrix:
        """Matrix multiplication operator for rotation composition."""
        if isinstance(other, RotationMatrix):
            return self.compose(other)
        return NotImplemented

    def __array__(self) -> np.ndarray:
        """Allow numpy array conversion."""
        return self._data

    def __getitem__(self, index) -> float | np.ndarray:
        """Get matrix elements by index."""
        return self._data[index]

    def __setitem__(self, index, value) -> None:
        """Set matrix elements by index."""
        self._data[index] = value
        # Validate after modification
        if not self._is_valid_rotation_matrix():
            self._data = self._orthogonalize()
