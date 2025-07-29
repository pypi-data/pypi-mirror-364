"""Cropper module for cropping images based on annotations."""

from typing import Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw


class Cropper:
    """Class for cropping images based on annotations."""

    def __init__(
        self,
        image: Image.Image,
        left_top_right_bottom: Tuple[int, int, int, int] | None = None,
        color: str = "red",
        line_width: int = 3,
    ):
        """
        Initialize the Copper class with an image and its annotations.
        Set left_top_right_bottom to None if the bounding bow is drawn on the image.
        """
        self.image = image
        self.left_top_right_bottom: Tuple[int, int, int, int] | None = left_top_right_bottom
        self.color: str = color
        self.line_width: int = line_width

    def crop(self):
        """
        Crop the image based on the provided annotations.
        Pillow takes left, upper, right, lower, like stored in CVAT annotations.
        Pillow handles the case where the coordinates are outside the image bounds by clamping them.
        """
        if self.left_top_right_bottom is None:
            return self.crop_drawn_bbox()
        return self.image.crop(self.left_top_right_bottom)

    def crop_drawn_bbox(self) -> Image.Image:
        """
        Crop the image based on the drawn bounding box.
        """
        self.left_top_right_bottom = Cropper.find_bbox_from_drawn_rectangle(self.image, self.color)
        if self.left_top_right_bottom is None:
            raise ValueError("Bounding box coordinates were not found.")
        return self.image.crop(self.left_top_right_bottom)

    def draw_bbox(
        self,
    ) -> Image.Image:
        """
        Draw a bounding box on the image.
        """
        if self.left_top_right_bottom is None:
            raise ValueError("Bounding box coordinates are not set.")
        image = self.image.copy()
        draw = ImageDraw.Draw(image)
        left, top, right, bottom = self.left_top_right_bottom

        # Draw rectangle at exterior by expanding coordinates outward by half the line width
        offset = self.line_width // 2
        exterior_coords = [left - offset, top - offset, right + offset, bottom + offset]

        # Ensure coordinates stay within image bounds
        exterior_coords[0] = max(0, exterior_coords[0])
        exterior_coords[1] = max(0, exterior_coords[1])
        exterior_coords[2] = min(self.image.width, exterior_coords[2])
        exterior_coords[3] = min(self.image.height, exterior_coords[3])

        draw.rectangle(exterior_coords, outline=self.color, width=self.line_width)
        return image

    @staticmethod
    def find_bbox_from_drawn_rectangle(image: Image.Image, color: str = "red") -> Tuple[int, int, int, int]:
        """Find a rectangle drawn on the image in the given color and return the bbox coordinates.
        The bbox contains the pixels that are inside the rectangle.
        The rectangle border shall not be included in the bbox.

        Args:
            image: PIL Image to search for the rectangle
            color: Color name or hex code of the rectangle to find (default: "red")

        Returns:
            Tuple of (left, upper, right, lower) representing the bounding box inside the rectangle

        Raises:
            ValueError: If no rectangle is found or if the color is invalid
        """

        # Convert PIL image to numpy array
        img_array = np.array(image)

        # Handle different image modes
        if len(img_array.shape) == 2:  # Grayscale
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

        # Define color mapping
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
        }

        # Parse color
        if color.startswith("#"):
            # Hex color
            hex_color = color.lstrip("#")
            if len(hex_color) != 6:
                raise ValueError(f"Invalid hex color format: {color}")
            target_color = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        elif color.lower() in color_map:
            target_color = color_map[color.lower()]
        else:
            raise ValueError(f"Unsupported color: {color}")

        # Create mask for the target color with tolerance
        tolerance = 10
        lower_bound = np.array([max(0, c - tolerance) for c in target_color])
        upper_bound = np.array([min(255, c + tolerance) for c in target_color])

        # Create color mask
        mask = cv2.inRange(img_array, lower_bound, upper_bound)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            raise ValueError(f"No {color} rectangle found in the image")

        # Find the largest rectangular contour
        best_contour = None
        best_area = 0
        best_rect = None

        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Check if it's roughly rectangular (4 corners)
            if len(approx) >= 4:
                # Get bounding rectangle
                rect = cv2.boundingRect(contour)
                area = rect[2] * rect[3]

                # Check if this contour is more rectangular than previous ones
                contour_area = cv2.contourArea(contour)
                rect_area = rect[2] * rect[3]
                rectangularity = contour_area / rect_area if rect_area > 0 else 0

                # Prefer larger, more rectangular shapes
                if area > best_area and rectangularity > 0.7:
                    best_area = area
                    best_contour = contour
                    best_rect = rect

        if best_rect is None:
            raise ValueError(f"No rectangular {color} shape found in the image")

        x, y, w, h = best_rect

        # Find the inner rectangle by detecting the border thickness more accurately
        # Method 1: Analyze the border structure by scanning inward from all edges
        border_thickness_top = 0
        border_thickness_left = 0
        border_thickness_right = 0
        border_thickness_bottom = 0

        # Scan from top edge inward until we find a row with no red pixels
        for i in range(min(h // 2, 30)):  # Increased scan depth
            row = y + i
            if row < mask.shape[0]:
                line = mask[row, x : x + w]
                if np.sum(line) == 0:  # No red pixels at all
                    border_thickness_top = i
                    break

        # Scan from bottom edge inward
        for i in range(min(h // 2, 30)):
            row = y + h - 1 - i
            if row >= 0:
                line = mask[row, x : x + w]
                if np.sum(line) == 0:  # No red pixels at all
                    border_thickness_bottom = i
                    break

        # Scan from left edge inward
        for i in range(min(w // 2, 30)):
            col = x + i
            if col < mask.shape[1]:
                line = mask[y : y + h, col]
                if np.sum(line) == 0:  # No red pixels at all
                    border_thickness_left = i
                    break

        # Scan from right edge inward
        for i in range(min(w // 2, 30)):
            col = x + w - 1 - i
            if col >= 0:
                line = mask[y : y + h, col]
                if np.sum(line) == 0:  # No red pixels at all
                    border_thickness_right = i
                    break

        # Use the maximum detected border thickness to ensure we're completely inside
        border_thickness = max(
            border_thickness_top, border_thickness_left, border_thickness_right, border_thickness_bottom
        )

        # If no border thickness detected, use a more conservative estimate
        if border_thickness == 0:
            # Fallback: estimate based on rectangle size
            border_thickness = max(3, min(w, h) // 15)

        # Add an additional safety margin to ensure we're completely inside the border
        border_thickness += 2

        # Calculate inner rectangle coordinates
        inner_x = x + border_thickness
        inner_y = y + border_thickness
        inner_w = w - 2 * border_thickness
        inner_h = h - 2 * border_thickness

        # Ensure positive dimensions
        if inner_w <= 0 or inner_h <= 0:
            raise ValueError("Rectangle border is too thick relative to its size")

        # Convert to (left, upper, right, lower) format
        left = inner_x
        upper = inner_y
        right = inner_x + inner_w
        lower = inner_y + inner_h

        return (left, upper, right, lower)
