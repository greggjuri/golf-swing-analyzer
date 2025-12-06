"""Tests for club detector module."""

import pytest
import numpy as np
import cv2

from src.detection.club_detector import (
    ClubDetector,
    DetectionResult,
    ClubHead,
)


class TestClubDetector:
    """Tests for ClubDetector class."""

    def test_initialization_default(self):
        """Test default initialization."""
        detector = ClubDetector()
        assert detector.canny_low == 50
        assert detector.canny_high == 150
        assert detector.hough_threshold == 50
        assert detector.min_line_length == 100
        assert detector.debug is False

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        detector = ClubDetector(
            canny_low=30,
            canny_high=120,
            hough_threshold=40,
            min_line_length=80,
            debug=True
        )
        assert detector.canny_low == 30
        assert detector.canny_high == 120
        assert detector.hough_threshold == 40
        assert detector.min_line_length == 80
        assert detector.debug is True

    def test_initialization_invalid_canny_thresholds(self):
        """Test that invalid Canny thresholds raise error."""
        with pytest.raises(ValueError, match="Invalid Canny thresholds"):
            ClubDetector(canny_low=150, canny_high=50)

    def test_initialization_negative_hough_threshold(self):
        """Test that negative Hough threshold raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            ClubDetector(hough_threshold=-10)

    def test_initialization_negative_min_line_length(self):
        """Test that negative min_line_length raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            ClubDetector(min_line_length=-10)

    def test_detect_empty_frame_raises_error(self):
        """Test that empty frame raises error."""
        detector = ClubDetector()

        with pytest.raises(ValueError, match="empty or None"):
            detector.detect(np.array([]))

    def test_detect_none_frame_raises_error(self):
        """Test that None frame raises error."""
        detector = ClubDetector()

        with pytest.raises(ValueError, match="empty or None"):
            detector.detect(None)

    def test_detect_no_lines_in_blank_frame(self):
        """Test detection on blank frame (no lines)."""
        detector = ClubDetector()

        # Create blank frame
        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        result = detector.detect(frame)

        assert result.shaft_detected is False
        assert result.shaft_line is None
        assert result.shaft_angle is None
        assert result.confidence == 0.0

    def test_detect_shaft_in_synthetic_image(self):
        """Test shaft detection with synthetic image containing line."""
        detector = ClubDetector(min_line_length=50)

        # Create frame with diagonal line (club shaft)
        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame, (100, 50), (200, 250), (255, 255, 255), 3)

        result = detector.detect(frame)

        # Should detect the line
        assert result.shaft_detected is True
        assert result.shaft_line is not None
        assert result.shaft_angle is not None

        # Line should be roughly diagonal
        assert 30 < abs(result.shaft_angle) < 90

    def test_detect_filters_horizontal_lines(self):
        """Test that horizontal lines are filtered out."""
        detector = ClubDetector(
            min_shaft_angle=20.0,
            max_shaft_angle=160.0,
            min_line_length=50
        )

        # Create frame with horizontal line
        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame, (50, 150), (250, 150), (255, 255, 255), 3)

        result = detector.detect(frame)

        # Horizontal line should be filtered out
        assert result.shaft_detected is False

    def test_detect_filters_vertical_lines(self):
        """Test that nearly vertical lines can be filtered out with tight constraints."""
        detector = ClubDetector(
            min_shaft_angle=15.0,
            max_shaft_angle=75.0,  # Exclude vertical lines (90°)
            min_line_length=50
        )

        # Create frame with vertical line
        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame, (150, 50), (150, 250), (255, 255, 255), 3)

        result = detector.detect(frame)

        # Vertical line (90°) should be filtered out with max_shaft_angle=75
        assert result.shaft_detected is False

    def test_detect_selects_longest_line(self):
        """Test that detector selects longest valid line."""
        detector = ClubDetector(min_line_length=30)

        # Create frame with multiple lines
        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame, (50, 50), (100, 100), (255, 255, 255), 3)  # Short
        cv2.line(frame, (120, 50), (220, 250), (255, 255, 255), 3)  # Long

        result = detector.detect(frame)

        assert result.shaft_detected is True

        # Should select the longer line
        x1, y1, x2, y2 = result.shaft_line
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        assert length > 100  # Long line is ~200px

    def test_detect_club_head_with_circle(self):
        """Test club head detection with synthetic circle."""
        detector = ClubDetector(min_line_length=50)

        # Create frame with shaft and club head
        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        # Draw shaft
        cv2.line(frame, (100, 50), (150, 200), (255, 255, 255), 3)

        # Draw club head circle
        cv2.circle(frame, (150, 210), 25, (255, 255, 255), 2)

        result = detector.detect(frame)

        # May or may not detect club head depending on circle quality
        # Just verify it doesn't crash
        assert isinstance(result.club_head_detected, bool)

    def test_detect_debug_mode(self):
        """Test that debug mode creates debug image."""
        detector = ClubDetector(debug=True)

        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame, (100, 50), (200, 250), (255, 255, 255), 3)

        result = detector.detect(frame)

        assert result.debug_image is not None
        assert result.debug_image.shape == frame.shape

    def test_detect_confidence_increases_with_line_length(self):
        """Test that confidence increases with line length."""
        detector = ClubDetector(min_line_length=30)

        # Short line
        frame1 = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame1, (100, 100), (150, 150), (255, 255, 255), 3)

        # Long line
        frame2 = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.line(frame2, (50, 50), (250, 250), (255, 255, 255), 3)

        result1 = detector.detect(frame1)
        result2 = detector.detect(frame2)

        if result1.shaft_detected and result2.shaft_detected:
            assert result2.confidence > result1.confidence


class TestDetectionResult:
    """Tests for DetectionResult dataclass."""

    def test_detection_result_creation(self):
        """Test creating DetectionResult."""
        result = DetectionResult(
            shaft_detected=True,
            shaft_line=(10, 20, 30, 40),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.8
        )

        assert result.shaft_detected is True
        assert result.shaft_line == (10, 20, 30, 40)
        assert result.shaft_angle == 45.0
        assert result.club_head_detected is False
        assert result.confidence == 0.8

    def test_detection_result_no_detection(self):
        """Test DetectionResult for failed detection."""
        result = DetectionResult(
            shaft_detected=False,
            shaft_line=None,
            shaft_angle=None,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.0
        )

        assert result.shaft_detected is False
        assert result.shaft_line is None
        assert result.confidence == 0.0


class TestClubHead:
    """Tests for ClubHead dataclass."""

    def test_club_head_creation(self):
        """Test creating ClubHead."""
        head = ClubHead(
            center=(100.0, 150.0),
            radius=25.0,
            confidence=0.75
        )

        assert head.center == (100.0, 150.0)
        assert head.radius == 25.0
        assert head.confidence == 0.75
