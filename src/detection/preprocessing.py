"""Frame preprocessing utilities for club detection.

This module provides image preprocessing functions to prepare video frames
for club detection, including grayscale conversion, noise reduction, contrast
enhancement, and region of interest extraction.
"""

import logging
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Type alias
ROI = Tuple[int, int, int, int]  # (x, y, width, height)


class FramePreprocessor:
    """Preprocess video frames for club detection.

    Applies grayscale conversion, Gaussian blur, optional ROI cropping,
    and contrast enhancement to prepare frames for edge detection.

    Example:
        preprocessor = FramePreprocessor(blur_kernel=5)
        gray = preprocessor.preprocess(frame)
        edges = cv2.Canny(gray, 50, 150)
    """

    def __init__(
        self,
        blur_kernel: int = 5,
        roi: Optional[ROI] = None,
        enhance_contrast: bool = False
    ):
        """Initialize preprocessor.

        Args:
            blur_kernel: Kernel size for Gaussian blur (must be odd)
            roi: Optional region of interest (x, y, width, height)
            enhance_contrast: Whether to apply CLAHE contrast enhancement

        Raises:
            ValueError: If blur_kernel is not a positive odd number
        """
        if blur_kernel <= 0 or blur_kernel % 2 == 0:
            raise ValueError(f"blur_kernel must be positive and odd, got {blur_kernel}")

        self.blur_kernel = blur_kernel
        self.roi = roi
        self.enhance_contrast = enhance_contrast

        # CLAHE for adaptive contrast enhancement
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) if enhance_contrast else None  # type: ignore[assignment]  # noqa: E501

        logger.info(
            f"Initialized FramePreprocessor: blur={blur_kernel}, "
            f"roi={roi}, contrast={enhance_contrast}"
        )

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Apply full preprocessing pipeline.

        Args:
            frame: Input frame (BGR format from OpenCV)

        Returns:
            Preprocessed grayscale frame

        Raises:
            ValueError: If frame is empty or invalid format
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")

        if len(frame.shape) not in [2, 3]:
            raise ValueError(
                f"Frame must be 2D or 3D array, got shape {frame.shape}"
            )

        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()

        # Apply ROI if specified
        if self.roi is not None:
            gray = self.apply_roi(gray, self.roi)

        # Apply Gaussian blur for noise reduction
        blurred = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)

        # Apply contrast enhancement if enabled
        if self.enhance_contrast and self.clahe is not None:
            blurred = self.clahe.apply(blurred)

        return blurred

    def apply_roi(self, frame: np.ndarray, roi: ROI) -> np.ndarray:
        """Extract region of interest from frame.

        Args:
            frame: Input frame (grayscale)
            roi: Region of interest (x, y, width, height)

        Returns:
            Cropped frame

        Raises:
            ValueError: If ROI is outside frame bounds
        """
        x, y, w, h = roi
        frame_h, frame_w = frame.shape[:2]

        if x < 0 or y < 0 or x + w > frame_w or y + h > frame_h:
            raise ValueError(
                f"ROI ({x}, {y}, {w}, {h}) is outside frame bounds "
                f"({frame_w}, {frame_h})"
            )

        return frame[y:y+h, x:x+w].copy()

    def enhance_frame_contrast(self, frame: np.ndarray) -> np.ndarray:
        """Apply CLAHE contrast enhancement to frame.

        Args:
            frame: Input grayscale frame

        Returns:
            Contrast-enhanced frame

        Raises:
            ValueError: If frame is not grayscale
        """
        if len(frame.shape) != 2:
            raise ValueError("Frame must be grayscale (2D array)")

        if self.clahe is None:
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        return self.clahe.apply(frame)


def create_edge_mask(frame: np.ndarray, low: int = 50, high: int = 150) -> np.ndarray:
    """Apply Canny edge detection to create binary edge mask.

    Args:
        frame: Input grayscale frame
        low: Low threshold for Canny
        high: High threshold for Canny

    Returns:
        Binary edge mask (0 or 255)

    Raises:
        ValueError: If frame is not grayscale or thresholds are invalid
    """
    if len(frame.shape) != 2:
        raise ValueError("Frame must be grayscale (2D array)")

    if low <= 0 or high <= 0 or low >= high:
        raise ValueError(f"Invalid thresholds: low={low}, high={high}")

    edges = cv2.Canny(frame, low, high)
    return edges


def clean_edge_mask(edges: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Clean up edge mask using morphological operations.

    Applies closing operation to connect nearby edges and remove noise.

    Args:
        edges: Binary edge mask
        kernel_size: Size of morphological kernel

    Returns:
        Cleaned edge mask

    Raises:
        ValueError: If kernel_size is invalid
    """
    if kernel_size <= 0 or kernel_size % 2 == 0:
        raise ValueError(f"kernel_size must be positive and odd, got {kernel_size}")

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (kernel_size, kernel_size)
    )

    # Closing: dilation followed by erosion (connects nearby edges)
    cleaned = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    return cleaned
