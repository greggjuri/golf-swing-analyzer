"""Tests for frame preprocessing module."""

import pytest
import numpy as np
import cv2

from src.detection.preprocessing import (
    FramePreprocessor,
    create_edge_mask,
    clean_edge_mask,
)


class TestFramePreprocessor:
    """Tests for FramePreprocessor class."""

    def test_initialization_default(self):
        """Test default initialization."""
        preprocessor = FramePreprocessor()
        assert preprocessor.blur_kernel == 5
        assert preprocessor.roi is None
        assert preprocessor.enhance_contrast is False

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        roi = (10, 20, 100, 200)
        preprocessor = FramePreprocessor(
            blur_kernel=7,
            roi=roi,
            enhance_contrast=True
        )
        assert preprocessor.blur_kernel == 7
        assert preprocessor.roi == roi
        assert preprocessor.enhance_contrast is True

    def test_initialization_invalid_blur_kernel(self):
        """Test that even blur kernel raises error."""
        with pytest.raises(ValueError, match="must be positive and odd"):
            FramePreprocessor(blur_kernel=4)

    def test_initialization_negative_blur_kernel(self):
        """Test that negative blur kernel raises error."""
        with pytest.raises(ValueError, match="must be positive and odd"):
            FramePreprocessor(blur_kernel=-1)

    def test_preprocess_color_frame(self):
        """Test preprocessing of color frame."""
        preprocessor = FramePreprocessor()

        # Create test frame (color)
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = preprocessor.preprocess(frame)

        # Should be grayscale
        assert len(result.shape) == 2
        assert result.shape == (100, 100)

    def test_preprocess_grayscale_frame(self):
        """Test preprocessing of already-grayscale frame."""
        preprocessor = FramePreprocessor()

        # Create test frame (grayscale)
        frame = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

        result = preprocessor.preprocess(frame)

        # Should remain grayscale
        assert len(result.shape) == 2
        assert result.shape == (100, 100)

    def test_preprocess_empty_frame_raises_error(self):
        """Test that empty frame raises ValueError."""
        preprocessor = FramePreprocessor()

        with pytest.raises(ValueError, match="empty or None"):
            preprocessor.preprocess(np.array([]))

    def test_preprocess_none_frame_raises_error(self):
        """Test that None frame raises ValueError."""
        preprocessor = FramePreprocessor()

        with pytest.raises(ValueError, match="empty or None"):
            preprocessor.preprocess(None)

    def test_preprocess_invalid_shape_raises_error(self):
        """Test that invalid frame shape raises ValueError."""
        preprocessor = FramePreprocessor()

        # Create 4D array (invalid)
        frame = np.zeros((10, 10, 3, 3))

        with pytest.raises(ValueError, match="must be 2D or 3D"):
            preprocessor.preprocess(frame)

    def test_apply_roi(self):
        """Test ROI extraction."""
        preprocessor = FramePreprocessor()

        # Create test frame
        frame = np.random.randint(0, 255, (200, 300), dtype=np.uint8)

        # Extract ROI
        roi = (50, 50, 100, 100)
        result = preprocessor.apply_roi(frame, roi)

        assert result.shape == (100, 100)

    def test_apply_roi_out_of_bounds_raises_error(self):
        """Test that ROI outside frame bounds raises error."""
        preprocessor = FramePreprocessor()

        frame = np.zeros((100, 100), dtype=np.uint8)

        # ROI extends beyond frame
        roi = (50, 50, 100, 100)

        with pytest.raises(ValueError, match="outside frame bounds"):
            preprocessor.apply_roi(frame, roi)

    def test_apply_roi_negative_coordinates_raises_error(self):
        """Test that negative ROI coordinates raise error."""
        preprocessor = FramePreprocessor()

        frame = np.zeros((100, 100), dtype=np.uint8)

        # Negative ROI
        roi = (-10, 0, 50, 50)

        with pytest.raises(ValueError, match="outside frame bounds"):
            preprocessor.apply_roi(frame, roi)

    def test_enhance_frame_contrast(self):
        """Test CLAHE contrast enhancement."""
        preprocessor = FramePreprocessor(enhance_contrast=True)

        # Create low-contrast frame
        frame = np.random.randint(100, 150, (100, 100), dtype=np.uint8)

        result = preprocessor.enhance_frame_contrast(frame)

        # Result should have higher contrast (larger value range)
        assert result.max() - result.min() >= frame.max() - frame.min()

    def test_enhance_frame_contrast_color_raises_error(self):
        """Test that color frame raises error."""
        preprocessor = FramePreprocessor()

        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="must be grayscale"):
            preprocessor.enhance_frame_contrast(frame)

    def test_preprocess_with_roi(self):
        """Test preprocessing with ROI."""
        roi = (25, 25, 50, 50)
        preprocessor = FramePreprocessor(roi=roi)

        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = preprocessor.preprocess(frame)

        # Result should be ROI size
        assert result.shape == (50, 50)

    def test_preprocess_with_contrast_enhancement(self):
        """Test preprocessing with contrast enhancement."""
        preprocessor = FramePreprocessor(enhance_contrast=True)

        # Create low-contrast frame
        frame = np.full((100, 100, 3), 100, dtype=np.uint8)

        result = preprocessor.preprocess(frame)

        assert result.shape == (100, 100)


class TestEdgeFunctions:
    """Tests for edge detection utility functions."""

    def test_create_edge_mask(self):
        """Test edge mask creation."""
        # Create simple frame with edge
        frame = np.zeros((100, 100), dtype=np.uint8)
        frame[:, 45:55] = 255  # Vertical stripe

        edges = create_edge_mask(frame, low=50, high=150)

        # Should detect edges at stripe boundaries
        assert edges.max() == 255
        assert edges.min() == 0

    def test_create_edge_mask_invalid_thresholds(self):
        """Test that invalid thresholds raise error."""
        frame = np.zeros((100, 100), dtype=np.uint8)

        with pytest.raises(ValueError, match="Invalid thresholds"):
            create_edge_mask(frame, low=150, high=50)

    def test_create_edge_mask_color_frame_raises_error(self):
        """Test that color frame raises error."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="must be grayscale"):
            create_edge_mask(frame)

    def test_clean_edge_mask(self):
        """Test edge mask cleaning."""
        # Create sparse edge mask
        edges = np.zeros((100, 100), dtype=np.uint8)
        edges[45:55, 45:55] = 255  # Small square

        cleaned = clean_edge_mask(edges, kernel_size=3)

        # Should still have edges
        assert cleaned.max() == 255

    def test_clean_edge_mask_invalid_kernel(self):
        """Test that even kernel size raises error."""
        edges = np.zeros((100, 100), dtype=np.uint8)

        with pytest.raises(ValueError, match="must be positive and odd"):
            clean_edge_mask(edges, kernel_size=4)
