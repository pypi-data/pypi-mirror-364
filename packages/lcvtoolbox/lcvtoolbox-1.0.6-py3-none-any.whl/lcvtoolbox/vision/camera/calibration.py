"""This helper adjusts the intrinsic parameters of a camera based on the size of the image using OpenCV for enhanced security and accuracy."""

import numpy as np

try:
    import cv2

    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

from lcvtoolbox.core.schemas import CameraDistortionSchema, CameraMatrixSchema


def adjust_intrinsic_with_size(
    matrix: CameraMatrixSchema,
    dist_coeffs: CameraDistortionSchema,
    original_image_size: tuple[int, int],
    new_image_size: tuple[int, int],
    alpha: float = 1.0,
    use_opencv: bool = True,
) -> tuple[CameraMatrixSchema, tuple[int, int, int, int] | None]:
    """
    Adjust the intrinsic parameters of a camera based on the size of the image using OpenCV's
    getOptimalNewCameraMatrix for enhanced security and accuracy when available.

    This method is more robust than simple scaling as it properly handles distortion effects
    and provides optimal camera parameters for the new image size. Falls back to legacy
    scaling method if OpenCV is not available.

    Note: Distortion coefficients remain unchanged when adjusting for image size, so they are
    not returned. The input dist_coeffs are only used for OpenCV's optimal calculation.

    Args:
        matrix (CameraMatrixSchema): The camera matrix.
        dist_coeffs (CameraDistortionSchema): The distortion coefficients (used for calculation only).
        original_image_size (tuple[int, int]): The size of the original image as (width, height).
        new_image_size (tuple[int, int]): The size of the new image as (width, height).
        alpha (float, optional): Free scaling parameter between 0 (when all pixels in the
            undistorted image are valid) and 1 (when all source image pixels are retained
            in the undistorted image). Defaults to 1.0.
        use_opencv (bool, optional): Whether to use OpenCV if available. Defaults to True.

    Returns:
        tuple[CameraMatrixSchema, Optional[tuple[int, int, int, int]]]:
            Adjusted camera matrix and ROI (x, y, width, height) if OpenCV is used, None otherwise.

    Raises:
        ValueError: If input parameters are invalid.

    Note on ROI:
        The ROI (Region of Interest) is returned as a tuple (x, y, width, height) where:
        - x, y are the top-left coordinates of the ROI in the new image.
        - width, height are the dimensions of the ROI in the new image.
        This ROI represents the valid pixel area after distortion correction and adjustment.
        If OpenCV is not used, ROI is returned as None.
    """
    # Input validation for security
    if not (0.0 <= alpha <= 1.0):
        raise ValueError(f"Alpha parameter must be between 0.0 and 1.0, got {alpha}")

    if original_image_size[0] <= 0 or original_image_size[1] <= 0:
        raise ValueError(f"Original image size must be positive, got {original_image_size}")

    if new_image_size[0] <= 0 or new_image_size[1] <= 0:
        raise ValueError(f"New image size must be positive, got {new_image_size}")

    if use_opencv and OPENCV_AVAILABLE and cv2 is not None:
        try:
            # Convert schema to OpenCV format with validation
            K = matrix.numpy
            dist_coeffs_array = dist_coeffs.numpy

            # Additional validation for camera matrix
            if not np.isfinite(K).all():
                raise ValueError("Camera matrix contains non-finite values")

            if not np.isfinite(dist_coeffs_array).all():
                raise ValueError("Distortion coefficients contain non-finite values")

            # Use OpenCV's secure approach for optimal camera matrix calculation
            new_K, roi = cv2.getOptimalNewCameraMatrix(  # type: ignore[attr-defined]
                K, dist_coeffs_array, original_image_size, alpha, new_image_size
            )

            # Validate OpenCV output
            if new_K is None or roi is None:
                raise ValueError("OpenCV returned invalid results")

            if not np.isfinite(new_K).all():
                raise ValueError("OpenCV returned non-finite camera matrix")

            # Convert back to schema format with validation
            adjusted_matrix = CameraMatrixSchema(
                fx=float(new_K[0, 0]),
                fy=float(new_K[1, 1]),
                cx=float(new_K[0, 2]),
                cy=float(new_K[1, 2]),
                s=float(new_K[0, 1]),
            )

            # ROI format: (x, y, width, height) with validation
            roi_tuple = (max(0, int(roi[0])), max(0, int(roi[1])), max(0, int(roi[2])), max(0, int(roi[3])))

            return adjusted_matrix, roi_tuple

        except (AttributeError, ValueError, Exception) as e:
            # Fall back to legacy method if OpenCV function is not available or fails
            print(f"Warning: OpenCV method failed ({e}), falling back to legacy scaling method")
            adjusted_matrix, _ = adjust_intrinsic_with_size_legacy(matrix, dist_coeffs, original_image_size, new_image_size)
            return adjusted_matrix, None
    else:
        # Use legacy scaling method
        adjusted_matrix, _ = adjust_intrinsic_with_size_legacy(matrix, dist_coeffs, original_image_size, new_image_size)
        return adjusted_matrix, None


def adjust_intrinsic_with_size_legacy(
    matrix: CameraMatrixSchema,
    dist_coeffs: CameraDistortionSchema,
    original_image_size: tuple[int, int],
    new_image_size: tuple[int, int],
) -> tuple[CameraMatrixSchema, CameraDistortionSchema]:
    """
    Legacy method for adjusting intrinsic parameters using simple scaling.

    Note: This method is kept for backward compatibility but the main function
    using OpenCV is recommended for better accuracy and security.

    Args:
        matrix (CameraMatrixSchema): The camera matrix.
        dist_coeffs (CameraDistortionSchema): The distortion coefficients.
        original_image_size (tuple[int, int]): The size of the original image as (width, height).
        new_image_size (tuple[int, int]): The size of the new image as (width, height).

    Returns:
        tuple[CameraMatrixSchema, CameraDistortionSchema]: Adjusted camera matrix and distortion coefficients.

    Raises:
        ValueError: If input parameters are invalid.
        ZeroDivisionError: If original image dimensions are zero.
    """
    # Input validation for security
    if original_image_size[0] <= 0 or original_image_size[1] <= 0:
        raise ValueError(f"Original image size must be positive, got {original_image_size}")

    if new_image_size[0] <= 0 or new_image_size[1] <= 0:
        raise ValueError(f"New image size must be positive, got {new_image_size}")

    # Validate camera matrix parameters
    if not all(np.isfinite([matrix.fx, matrix.fy, matrix.cx, matrix.cy, matrix.s])):
        raise ValueError("Camera matrix contains non-finite values")

    if matrix.fx <= 0 or matrix.fy <= 0:
        raise ValueError("Focal lengths must be positive")

    width, height = new_image_size
    original_width, original_height = original_image_size

    # Calculate scaling factors with validation
    width_scale = width / original_width
    height_scale = height / original_height

    if not np.isfinite([width_scale, height_scale]).all():
        raise ValueError("Calculated scaling factors are not finite")

    adjusted_matrix = CameraMatrixSchema(
        fx=matrix.fx * width_scale,  # Adjusting based on original width
        fy=matrix.fy * height_scale,  # Adjusting based on original height
        cx=matrix.cx * width_scale,
        cy=matrix.cy * height_scale,
        s=matrix.s,  # Skew parameter typically remains unchanged
    )

    return adjusted_matrix, dist_coeffs
