"""Tests for pose detector."""

import pytest
import numpy as np

from src.pose import PoseDetector, PoseResult, PoseLandmark


class TestPoseDetectorInit:
    """Test PoseDetector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        detector = PoseDetector()
        assert detector.model_complexity == 1
        assert detector.min_detection_confidence == 0.5
        assert detector.min_tracking_confidence == 0.5
        assert not detector.enable_segmentation
        detector.close()

    def test_init_custom_params(self):
        """Test custom parameters."""
        detector = PoseDetector(
            model_complexity=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            enable_segmentation=True
        )
        assert detector.model_complexity == 2
        assert detector.min_detection_confidence == 0.7
        assert detector.min_tracking_confidence == 0.6
        assert detector.enable_segmentation
        detector.close()

    def test_init_invalid_complexity(self):
        """Test error on invalid model complexity."""
        with pytest.raises(ValueError, match="model_complexity must be"):
            PoseDetector(model_complexity=3)

        with pytest.raises(ValueError, match="model_complexity must be"):
            PoseDetector(model_complexity=-1)

    def test_init_invalid_confidence(self):
        """Test error on invalid confidence values."""
        with pytest.raises(ValueError, match="min_detection_confidence"):
            PoseDetector(min_detection_confidence=1.5)

        with pytest.raises(ValueError, match="min_tracking_confidence"):
            PoseDetector(min_tracking_confidence=-0.1)


class TestPoseDetectorDetect:
    """Test pose detection."""

    def test_detect_valid_frame(self):
        """Test detection on valid frame."""
        detector = PoseDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        result = detector.detect(frame)

        assert result is not None
        assert isinstance(result, PoseResult)
        assert len(result.landmarks) == 33
        assert result.detection_confidence > 0

        detector.close()

    def test_detect_grayscale_frame(self):
        """Test detection on grayscale frame."""
        detector = PoseDetector()
        frame = np.zeros((480, 640), dtype=np.uint8)

        result = detector.detect(frame)

        assert result is not None
        detector.close()

    def test_detect_none_frame(self):
        """Test error on None frame."""
        detector = PoseDetector()

        with pytest.raises(ValueError, match="Frame is empty or None"):
            detector.detect(None)

        detector.close()

    def test_detect_empty_frame(self):
        """Test error on empty frame."""
        detector = PoseDetector()

        with pytest.raises(ValueError, match="Frame is empty or None"):
            detector.detect(np.array([]))

        detector.close()

    def test_detect_invalid_dimensions(self):
        """Test error on invalid frame dimensions."""
        detector = PoseDetector()

        # 1D array
        with pytest.raises(ValueError, match="Frame must be 2D or 3D"):
            detector.detect(np.zeros(100, dtype=np.uint8))

        detector.close()


class TestPoseResult:
    """Test PoseResult functionality."""

    def test_pose_result_creation(self):
        """Test creating PoseResult."""
        from src.pose.landmarks import LandmarkPoint

        landmarks = {
            PoseLandmark.NOSE: LandmarkPoint(0.5, 0.3, 0.0, 0.9, 0.95),
            PoseLandmark.LEFT_SHOULDER: LandmarkPoint(0.4, 0.5, 0.0, 0.85, 0.9),
        }

        result = PoseResult(
            landmarks=landmarks,
            world_landmarks=landmarks.copy(),
            timestamp=1234.56,
            detection_confidence=0.88
        )

        assert len(result.landmarks) == 2
        assert result.timestamp == 1234.56
        assert result.detection_confidence == 0.88

    def test_is_visible_above_threshold(self):
        """Test is_visible returns True for visible landmarks."""
        from src.pose.landmarks import LandmarkPoint

        landmarks = {
            PoseLandmark.NOSE: LandmarkPoint(0.5, 0.3, 0.0, 0.9, 0.95),
        }

        result = PoseResult(
            landmarks=landmarks,
            world_landmarks={},
            timestamp=0.0,
            detection_confidence=0.9
        )

        assert result.is_visible(PoseLandmark.NOSE, min_visibility=0.5)
        assert result.is_visible(PoseLandmark.NOSE, min_visibility=0.8)

    def test_is_visible_below_threshold(self):
        """Test is_visible returns False below threshold."""
        from src.pose.landmarks import LandmarkPoint

        landmarks = {
            PoseLandmark.NOSE: LandmarkPoint(0.5, 0.3, 0.0, 0.3, 0.4),
        }

        result = PoseResult(
            landmarks=landmarks,
            world_landmarks={},
            timestamp=0.0,
            detection_confidence=0.9
        )

        assert not result.is_visible(PoseLandmark.NOSE, min_visibility=0.5)

    def test_is_visible_missing_landmark(self):
        """Test is_visible returns False for missing landmark."""
        result = PoseResult(
            landmarks={},
            world_landmarks={},
            timestamp=0.0,
            detection_confidence=0.9
        )

        assert not result.is_visible(PoseLandmark.NOSE)

    def test_get_position(self):
        """Test get_position returns correct coordinates."""
        from src.pose.landmarks import LandmarkPoint

        landmarks = {
            PoseLandmark.NOSE: LandmarkPoint(0.5, 0.3, 0.0, 0.9, 0.95),
        }

        result = PoseResult(
            landmarks=landmarks,
            world_landmarks={},
            timestamp=0.0,
            detection_confidence=0.9
        )

        pos = result.get_position(PoseLandmark.NOSE)
        assert pos == (0.5, 0.3)

    def test_get_position_missing(self):
        """Test get_position returns None for missing landmark."""
        result = PoseResult(
            landmarks={},
            world_landmarks={},
            timestamp=0.0,
            detection_confidence=0.9
        )

        pos = result.get_position(PoseLandmark.NOSE)
        assert pos is None

    def test_get_world_position(self):
        """Test get_world_position returns 3D coordinates."""
        from src.pose.landmarks import LandmarkPoint

        world_landmarks = {
            PoseLandmark.NOSE: LandmarkPoint(0.5, 0.3, 0.1, 0.9, 0.95),
        }

        result = PoseResult(
            landmarks={},
            world_landmarks=world_landmarks,
            timestamp=0.0,
            detection_confidence=0.9
        )

        pos = result.get_world_position(PoseLandmark.NOSE)
        assert pos == (0.5, 0.3, 0.1)


class TestPoseDetectorContextManager:
    """Test context manager functionality."""

    def test_context_manager(self):
        """Test using detector as context manager."""
        with PoseDetector() as detector:
            assert detector is not None
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = detector.detect(frame)
            assert result is not None

        # Should be closed after context
        assert detector.pose is None

    def test_context_manager_with_error(self):
        """Test context manager cleans up on error."""
        try:
            with PoseDetector() as detector:
                assert detector is not None
                raise RuntimeError("Test error")
        except RuntimeError:
            pass

        # Should still be closed
        assert detector.pose is None


class TestPoseDetectorClose:
    """Test resource cleanup."""

    def test_close(self):
        """Test close method."""
        detector = PoseDetector()
        detector.close()
        assert detector.pose is None

    def test_double_close(self):
        """Test closing twice doesn't error."""
        detector = PoseDetector()
        detector.close()
        detector.close()  # Should not error
        assert detector.pose is None
