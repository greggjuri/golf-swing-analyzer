"""Tests for club tracking module."""

import pytest
import numpy as np

from src.detection.tracking import ClubTracker
from src.detection.club_detector import DetectionResult, ClubHead


class TestClubTracker:
    """Tests for ClubTracker class."""

    def test_initialization_default(self):
        """Test default initialization."""
        tracker = ClubTracker()
        assert tracker.smoothing_window == 3
        assert tracker.max_gap_frames == 5

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        tracker = ClubTracker(smoothing_window=5, max_gap_frames=10)
        assert tracker.smoothing_window == 5
        assert tracker.max_gap_frames == 10

    def test_initialization_invalid_window(self):
        """Test that invalid smoothing window raises error."""
        with pytest.raises(ValueError, match="must be at least 1"):
            ClubTracker(smoothing_window=0)

    def test_initialization_negative_max_gap(self):
        """Test that negative max_gap raises error."""
        with pytest.raises(ValueError, match="must be non-negative"):
            ClubTracker(max_gap_frames=-1)

    def test_update_single_detection(self):
        """Test updating with single detection."""
        tracker = ClubTracker()

        detection = DetectionResult(
            shaft_detected=True,
            shaft_line=(100, 100, 200, 200),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.8
        )

        result = tracker.update(detection)

        assert result.shaft_detected is True
        assert result.shaft_line is not None

    def test_update_smooths_across_frames(self):
        """Test that tracking smooths detections across frames."""
        tracker = ClubTracker(smoothing_window=3)

        # Create detections with slight variations
        detections = [
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=45.0,
                club_head_detected=False,
                club_head_center=None,
                club_head_radius=None,
                confidence=0.8
            ),
            DetectionResult(
                shaft_detected=True,
                shaft_line=(105, 95, 205, 195),
                shaft_angle=44.0,
                club_head_detected=False,
                club_head_center=None,
                club_head_radius=None,
                confidence=0.8
            ),
            DetectionResult(
                shaft_detected=True,
                shaft_line=(95, 105, 195, 205),
                shaft_angle=46.0,
                club_head_detected=False,
                club_head_center=None,
                club_head_radius=None,
                confidence=0.8
            ),
        ]

        results = [tracker.update(d) for d in detections]

        # Last result should be smoothed
        assert results[-1].shaft_detected is True
        x1, y1, x2, y2 = results[-1].shaft_line

        # Smoothed values should be close to average
        assert 95 <= x1 <= 105
        assert 95 <= y1 <= 105

    def test_update_fills_short_gap(self):
        """Test that tracker fills short gaps using interpolation."""
        tracker = ClubTracker(max_gap_frames=5)

        # First detection
        detection1 = DetectionResult(
            shaft_detected=True,
            shaft_line=(100, 100, 200, 200),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.8
        )
        tracker.update(detection1)

        # Failed detection (gap)
        detection2 = DetectionResult(
            shaft_detected=False,
            shaft_line=None,
            shaft_angle=None,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.0
        )

        result = tracker.update(detection2)

        # Should interpolate
        assert result.shaft_detected is True
        assert result.shaft_line is not None

    def test_update_does_not_fill_long_gap(self):
        """Test that tracker doesn't fill gaps longer than max_gap_frames."""
        tracker = ClubTracker(max_gap_frames=2)

        # First detection
        detection1 = DetectionResult(
            shaft_detected=True,
            shaft_line=(100, 100, 200, 200),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.8
        )
        tracker.update(detection1)

        # Create gap longer than max_gap_frames
        failed_detection = DetectionResult(
            shaft_detected=False,
            shaft_line=None,
            shaft_angle=None,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.0
        )

        # Add 3 failed detections (exceeds max_gap_frames=2)
        tracker.update(failed_detection)
        tracker.update(failed_detection)
        result = tracker.update(failed_detection)

        # Should not interpolate
        assert result.shaft_detected is False

    def test_update_reduces_confidence_during_gap(self):
        """Test that confidence reduces during interpolation."""
        tracker = ClubTracker(max_gap_frames=5)

        # First detection with high confidence
        detection1 = DetectionResult(
            shaft_detected=True,
            shaft_line=(100, 100, 200, 200),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.9
        )
        result0 = tracker.update(detection1)

        # Failed detection with non-zero confidence (base confidence)
        # This simulates failed detection but with base confidence
        failed = DetectionResult(
            shaft_detected=False,
            shaft_line=None,
            shaft_angle=None,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.5  # Use non-zero so penalty has effect
        )

        result1 = tracker.update(failed)
        result2 = tracker.update(failed)

        # Confidence should be reduced from original during interpolation
        assert result1.confidence < result0.confidence
        # Second gap frame should have even lower confidence
        assert result2.confidence < result1.confidence

    def test_smooths_club_head(self):
        """Test smoothing of club head detections."""
        tracker = ClubTracker(smoothing_window=3)

        # Create detections with club head
        detections = [
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=45.0,
                club_head_detected=True,
                club_head_center=(205.0, 205.0),
                club_head_radius=25.0,
                confidence=0.8
            ),
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=45.0,
                club_head_detected=True,
                club_head_center=(210.0, 210.0),
                club_head_radius=27.0,
                confidence=0.8
            ),
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=45.0,
                club_head_detected=True,
                club_head_center=(195.0, 195.0),
                club_head_radius=23.0,
                confidence=0.8
            ),
        ]

        results = [tracker.update(d) for d in detections]

        # Last result should have smoothed club head
        assert results[-1].club_head_detected is True
        assert results[-1].club_head_center is not None

        # Center should be averaged
        cx, cy = results[-1].club_head_center
        assert 200 <= cx <= 210
        assert 200 <= cy <= 210

    def test_reset_clears_history(self):
        """Test that reset clears tracking history."""
        tracker = ClubTracker()

        # Add some detections
        detection = DetectionResult(
            shaft_detected=True,
            shaft_line=(100, 100, 200, 200),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.8
        )

        tracker.update(detection)
        tracker.update(detection)

        # Reset
        tracker.reset()

        # History should be empty
        assert len(tracker.shaft_history) == 0
        assert len(tracker.angle_history) == 0
        assert len(tracker.head_history) == 0
        assert tracker.frames_since_detection == 0

    def test_smooths_angles_with_circular_mean(self):
        """Test that angle smoothing handles wraparound correctly."""
        tracker = ClubTracker(smoothing_window=3)

        # Create detections with angles near 180/-180 boundary
        detections = [
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=175.0,
                club_head_detected=False,
                club_head_center=None,
                club_head_radius=None,
                confidence=0.8
            ),
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=-175.0,
                club_head_detected=False,
                club_head_center=None,
                club_head_radius=None,
                confidence=0.8
            ),
            DetectionResult(
                shaft_detected=True,
                shaft_line=(100, 100, 200, 200),
                shaft_angle=180.0,
                club_head_detected=False,
                club_head_center=None,
                club_head_radius=None,
                confidence=0.8
            ),
        ]

        results = [tracker.update(d) for d in detections]

        # Should handle wraparound correctly
        # Average should be close to 180 or -180, not near 0
        assert results[-1].shaft_angle is not None
        assert abs(abs(results[-1].shaft_angle) - 180) < 10
