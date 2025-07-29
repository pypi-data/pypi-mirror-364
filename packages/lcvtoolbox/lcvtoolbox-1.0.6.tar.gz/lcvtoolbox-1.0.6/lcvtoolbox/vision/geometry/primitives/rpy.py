from __future__ import annotations

import numpy as np


class RPY:
    """
    Represents roll, pitch, yaw angles as extrinsic X-Y-Z Euler angles.

    This class handles 3D rotations using Euler angles with the convention of
    extrinsic rotations applied in the order: Roll (X), Pitch (Y), Yaw (Z).
    All angles are in radians.

    Args:
        roll: Rotation angle around X-axis in radians
        pitch: Rotation angle around Y-axis in radians
        yaw: Rotation angle around Z-axis in radians

    Examples:
        >>> # Create from individual angles
        >>> rpy = RPY(roll=0.1, pitch=0.2, yaw=0.3)
        >>> rotation_matrix = rpy.to_rotation_matrix()
        >>>
        >>> # Create from numpy array
        >>> angles = np.array([0.1, 0.2, 0.3])
        >>> rpy = RPY.from_numpy(angles)
        >>>
        >>> # Convert to degrees
        >>> rpy_deg = rpy.to_degrees()
        >>> print(f"Roll: {rpy_deg.roll}°, Pitch: {rpy_deg.pitch}°, Yaw: {rpy_deg.yaw}°")
    """

    __slots__ = ("_data",)  # Memory optimization

    def __init__(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> None:
        """Initialize RPY angles with given values in radians."""
        self._data = np.array([roll, pitch, yaw], dtype=np.float64)

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> RPY:
        """Create RPY from a numpy array.

        Args:
            array: Numpy array with 3 elements [roll, pitch, yaw]

        Returns:
            RPY instance

        Raises:
            ValueError: If array doesn't have exactly 3 elements
        """
        if len(array) != 3:
            raise ValueError("Array must have exactly 3 elements [roll, pitch, yaw]")

        return cls(float(array[0]), float(array[1]), float(array[2]))

    @classmethod
    def from_tuple(cls, angles: tuple[float, float, float]) -> RPY:
        """Create RPY from a tuple of angles.

        Args:
            angles: Tuple with (roll, pitch, yaw) in radians

        Returns:
            RPY instance
        """
        return cls(angles[0], angles[1], angles[2])

    @classmethod
    def from_degrees(cls, roll_deg: float, pitch_deg: float, yaw_deg: float) -> RPY:
        """Create RPY from angles in degrees.

        Args:
            roll_deg: Roll angle in degrees
            pitch_deg: Pitch angle in degrees
            yaw_deg: Yaw angle in degrees

        Returns:
            RPY instance with angles converted to radians
        """
        return cls(np.deg2rad(roll_deg), np.deg2rad(pitch_deg), np.deg2rad(yaw_deg))

    @classmethod
    def zeros(cls) -> RPY:
        """Create RPY with all angles set to zero."""
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def from_rotation_matrix(cls, matrix: np.ndarray) -> RPY:
        """Create RPY from a 3x3 rotation matrix.

        This uses the extrinsic X-Y-Z Euler angle convention.

        Args:
            matrix: 3x3 rotation matrix

        Returns:
            RPY instance

        Raises:
            ValueError: If matrix is not 3x3
        """
        if matrix.shape != (3, 3):
            raise ValueError("Matrix must be 3x3")

        # Extract Euler angles from rotation matrix
        # For extrinsic X-Y-Z convention: R = Rz(yaw) * Ry(pitch) * Rx(roll)

        # Check for gimbal lock
        sy = np.sqrt(matrix[0, 0] ** 2 + matrix[1, 0] ** 2)

        singular = sy < 1e-6

        if not singular:
            roll = np.arctan2(matrix[2, 1], matrix[2, 2])
            pitch = np.arctan2(-matrix[2, 0], sy)
            yaw = np.arctan2(matrix[1, 0], matrix[0, 0])
        else:
            # Gimbal lock case
            roll = np.arctan2(-matrix[1, 2], matrix[1, 1])
            pitch = np.arctan2(-matrix[2, 0], sy)
            yaw = 0.0

        return cls(roll, pitch, yaw)

    @property
    def roll(self) -> float:
        """Get the roll angle in radians."""
        return float(self._data[0])

    @property
    def pitch(self) -> float:
        """Get the pitch angle in radians."""
        return float(self._data[1])

    @property
    def yaw(self) -> float:
        """Get the yaw angle in radians."""
        return float(self._data[2])

    @roll.setter
    def roll(self, value: float) -> None:
        """Set the roll angle in radians."""
        self._data[0] = value

    @pitch.setter
    def pitch(self, value: float) -> None:
        """Set the pitch angle in radians."""
        self._data[1] = value

    @yaw.setter
    def yaw(self, value: float) -> None:
        """Set the yaw angle in radians."""
        self._data[2] = value

    @property
    def numpy(self) -> np.ndarray:
        """Get angles as a numpy array [roll, pitch, yaw]."""
        return self._data.copy()

    @property
    def tuple(self) -> tuple[float, float, float]:
        """Get angles as a tuple (roll, pitch, yaw)."""
        return (self.roll, self.pitch, self.yaw)

    def to_rotation_matrix(self) -> np.ndarray:
        """Convert RPY angles to a 3x3 rotation matrix.

        Uses extrinsic X-Y-Z Euler angle convention:
        R = Rz(yaw) * Ry(pitch) * Rx(roll)

        Returns:
            3x3 numpy array representing the rotation matrix
        """
        roll, pitch, yaw = self._data

        # Individual rotation matrices
        # Rotation around X-axis (roll)
        cr = np.cos(roll)
        sr = np.sin(roll)
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])

        # Rotation around Y-axis (pitch)
        cp = np.cos(pitch)
        sp = np.sin(pitch)
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])

        # Rotation around Z-axis (yaw)
        cy = np.cos(yaw)
        sy = np.sin(yaw)
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])

        # Combined rotation matrix for extrinsic rotations
        # R = Rz * Ry * Rx
        R = Rz @ Ry @ Rx

        return R

    def to_degrees(self) -> RPY:
        """Convert angles to degrees.

        Returns:
            New RPY instance with angles in degrees
        """
        return RPY(np.rad2deg(self.roll), np.rad2deg(self.pitch), np.rad2deg(self.yaw))

    def to_radians(self) -> RPY:
        """Return a copy with angles in radians (identity operation)."""
        return self.copy()

    def normalize(self) -> RPY:
        """Normalize angles to [-π, π] range.

        Returns:
            New RPY instance with normalized angles
        """
        normalized = np.array([np.arctan2(np.sin(self.roll), np.cos(self.roll)), np.arctan2(np.sin(self.pitch), np.cos(self.pitch)), np.arctan2(np.sin(self.yaw), np.cos(self.yaw))])
        return RPY.from_numpy(normalized)

    def normalize_positive(self) -> RPY:
        """Normalize angles to [0, 2π] range.

        Returns:
            New RPY instance with positive normalized angles
        """
        normalized = self.normalize()
        positive = np.where(normalized.numpy < 0, normalized.numpy + 2 * np.pi, normalized.numpy)
        return RPY.from_numpy(positive)

    def compose(self, other: RPY) -> RPY:
        """Compose this rotation with another RPY rotation.

        The resulting rotation is equivalent to applying this rotation
        followed by the other rotation.

        Args:
            other: Another RPY instance

        Returns:
            New RPY instance representing the composed rotation
        """
        # Convert to rotation matrices
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()

        # Compose rotations
        R_combined = R2 @ R1

        # Convert back to RPY
        return RPY.from_rotation_matrix(R_combined)

    def inverse(self) -> RPY:
        """Get the inverse rotation.

        Returns:
            New RPY instance representing the inverse rotation
        """
        # For inverse, we need to reverse the order and negate the angles
        # The inverse of R = Rz(yaw) * Ry(pitch) * Rx(roll) is
        # R^(-1) = Rx(-roll) * Ry(-pitch) * Rz(-yaw)
        R = self.to_rotation_matrix()
        R_inv = R.T  # Transpose of rotation matrix is its inverse
        return RPY.from_rotation_matrix(R_inv)

    def interpolate(self, other: RPY, t: float) -> RPY:
        """Spherical linear interpolation (SLERP) between two rotations.

        Args:
            other: Target RPY rotation
            t: Interpolation parameter (0.0 to 1.0)

        Returns:
            New RPY instance representing the interpolated rotation
        """
        # Convert to rotation matrices
        R1 = self.to_rotation_matrix()
        R2 = other.to_rotation_matrix()

        # Use matrix exponential for interpolation
        # This is a simplified version - for production use, consider quaternions
        R_diff = R2 @ R1.T

        # Extract angle from rotation matrix
        trace = np.trace(R_diff)
        angle = np.arccos(np.clip((trace - 1) / 2, -1, 1))

        if np.abs(angle) < 1e-6:
            # Small angle approximation
            R_interp = (1 - t) * R1 + t * R2
        else:
            # Compute rotation axis
            axis = np.array([R_diff[2, 1] - R_diff[1, 2], R_diff[0, 2] - R_diff[2, 0], R_diff[1, 0] - R_diff[0, 1]])
            axis = axis / (2 * np.sin(angle))

            # Rodrigues formula for interpolated rotation
            K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])

            interpolated_angle = t * angle
            R_interp_diff = np.eye(3) + np.sin(interpolated_angle) * K + (1 - np.cos(interpolated_angle)) * K @ K

            R_interp = R_interp_diff @ R1

        return RPY.from_rotation_matrix(R_interp)

    def is_close(self, other: RPY, tolerance: float = 1e-6) -> bool:
        """Check if this RPY is close to another within tolerance.

        Args:
            other: Another RPY instance
            tolerance: Tolerance for comparison in radians

        Returns:
            True if all angles are within tolerance
        """
        return np.allclose(self._data, other._data, atol=tolerance)

    def copy(self) -> RPY:
        """Create a copy of this RPY."""
        return RPY(self.roll, self.pitch, self.yaw)

    def __repr__(self) -> str:
        """String representation of the RPY."""
        return f"RPY(roll={self.roll:.6f}, pitch={self.pitch:.6f}, yaw={self.yaw:.6f})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        deg = self.to_degrees()
        return f"RPY(r={deg.roll:.2f}°, p={deg.pitch:.2f}°, y={deg.yaw:.2f}°)"

    def __eq__(self, other: object) -> bool:
        """Check equality with another RPY."""
        if not isinstance(other, RPY):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __ne__(self, other: object) -> bool:
        """Check inequality with another RPY."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash function for RPY objects."""
        return hash(self._data.tobytes())

    def __add__(self, other: RPY) -> RPY:
        """Add another RPY to this one (angle-wise addition)."""
        if isinstance(other, RPY):
            return RPY(self.roll + other.roll, self.pitch + other.pitch, self.yaw + other.yaw)
        return NotImplemented

    def __sub__(self, other: RPY) -> RPY:
        """Subtract another RPY from this one (angle-wise subtraction)."""
        if isinstance(other, RPY):
            return RPY(self.roll - other.roll, self.pitch - other.pitch, self.yaw - other.yaw)
        return NotImplemented

    def __mul__(self, scalar: float) -> RPY:
        """Multiply all angles by a scalar."""
        if isinstance(scalar, (int, float)):
            return RPY(self.roll * scalar, self.pitch * scalar, self.yaw * scalar)
        return NotImplemented

    def __truediv__(self, scalar: float) -> RPY:
        """Divide all angles by a scalar."""
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero")
            return RPY(self.roll / scalar, self.pitch / scalar, self.yaw / scalar)
        return NotImplemented

    def __neg__(self) -> RPY:
        """Negate all angles."""
        return RPY(-self.roll, -self.pitch, -self.yaw)

    def __iter__(self):
        """Make RPY iterable."""
        return iter([self.roll, self.pitch, self.yaw])

    def __getitem__(self, index: int) -> float:
        """Get angle by index (0=roll, 1=pitch, 2=yaw)."""
        if index == 0:
            return self.roll
        elif index == 1:
            return self.pitch
        elif index == 2:
            return self.yaw
        else:
            raise IndexError("RPY index out of range")

    def __setitem__(self, index: int, value: float) -> None:
        """Set angle by index (0=roll, 1=pitch, 2=yaw)."""
        if index == 0:
            self.roll = value
        elif index == 1:
            self.pitch = value
        elif index == 2:
            self.yaw = value
        else:
            raise IndexError("RPY index out of range")

    def __len__(self) -> int:
        """Length of the RPY (always 3)."""
        return 3
