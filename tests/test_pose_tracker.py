"""Tests for pose tracker."""

import pytest
import numpy as np

from src.pose import PoseDetector, PoseTracker, PoseLandmark
from src.pose.landmarks import LandmarkPoint
from src.pose.detector import PoseResult


@pytest.fixture
def sample_pose_result():
    """Create sample pose result."""
    landmarks = {
        PoseLandmark.NOSE: LandmarkPoint(0.5, 0.3, 0.0, 0.9, 0.95),
        PoseLandmark.LEFT_SHOULDER: LandmarkPoint(0.4, 0.5, 0.0, 0.85, 0.9),
        PoseLandmark.RIGHT_SHOULDER: LandmarkPoint(0.6, 0.5, 0.0, 0.85, 0.9),
    }

    return PoseResult(
        landmarks=landmarks,
        world_landmarks=landmarks.copy(),
        timestamp=0.0,
        detection_confidence=0.88
    )


class TestPoseTrackerInit:
    """Test PoseTracker initialization."""

    def test_init_default(self):
        """Test default initialization."""
        tracker = PoseTracker()
        assert tracker.smoothing_window == 5
        assert tracker.max_gap_frames == 10
        assert tracker.confidence_threshold == 0.5

    def test_init_custom_params(self):
        """Test custom parameters."""
        tracker = PoseTracker(
            smoothing_window=3,
            max_gap_frames=5,
            confidence_threshold=0.7
        )
        assert tracker.smoothing_window == 3
        assert tracker.max_gap_frames == 5
        assert tracker.confidence_threshold == 0.7

    def test_init_invalid_window(self):
        """Test error on invalid smoothing window."""
        with pytest.raises(ValueError, match="smoothing_window must be"):
            PoseTracker(smoothing_window=0)

    def test_init_invalid_gap(self):
        """Test error on invalid max gap."""
        with pytest.raises(ValueError, match="max_gap_frames must be"):
            PoseTracker(max_gap_frames=-1)

    def test_init_invalid_threshold(self):
        """Test error on invalid confidence threshold."""
        with pytest.raises(ValueError, match="confidence_threshold"):
            PoseTracker(confidence_threshold=1.5)


class TestPoseTrackerUpdate:
    """Test tracker update functionality."""

    def test_update_first_frame(self, sample_pose_result):
        """Test updating with first frame."""
        tracker = PoseTracker()

        result = tracker.update(0, sample_pose_result)

        assert result is not None
        assert len(result.landmarks) > 0

    def test_update_sequential_frames(self, sample_pose_result):
        """Test updating multiple sequential frames."""
        tracker = PoseTracker()

        for i in range(5):
            result = tracker.update(i, sample_pose_result)
            assert result is not None

    def test_update_invalid_frame_number(self, sample_pose_result):
        """Test error on non-sequential frame numbers."""
        tracker = PoseTracker()

        tracker.update(0, sample_pose_result)

        with pytest.raises(ValueError, match="Frame numbers must be sequential"):
            tracker.update(0, sample_pose_result)  # Same frame again

    def test_update_with_none_result(self):
        """Test updating with None result."""
        tracker = PoseTracker(max_gap_frames=0)

        result = tracker.update(0, None)

        # No previous valid pose, should return None
        assert result is None

    def test_update_smoothing(self, sample_pose_result):
        """Test that smoothing reduces noise."""
        tracker = PoseTracker(smoothing_window=3)

        # Add multiple frames
        results = []
        for i in range(5):
            result = tracker.update(i, sample_pose_result)
            results.append(result)

        # All should be valid
        assert all(r is not None for r in results)


class TestPoseTrackerInterpolation:
    """Test gap interpolation."""

    def test_interpolate_small_gap(self, sample_pose_result):
        """Test interpolation over small gap."""
        tracker = PoseTracker(max_gap_frames=10)

        # First valid frame
        tracker.update(0, sample_pose_result)

        # Gap of 3 frames
        result1 = tracker.update(1, None)
        result2 = tracker.update(2, None)
        result3 = tracker.update(3, None)

        # Should all be interpolated
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None

        # Confidence should decay
        assert result1.detection_confidence < sample_pose_result.detection_confidence
        assert result2.detection_confidence < result1.detection_confidence

    def test_gap_too_large(self, sample_pose_result):
        """Test no interpolation when gap too large."""
        tracker = PoseTracker(max_gap_frames=2)

        # First valid frame
        tracker.update(0, sample_pose_result)

        # Gap of 1 frame - should interpolate
        result1 = tracker.update(1, None)
        assert result1 is not None

        # Gap of 2 frames - should interpolate
        result2 = tracker.update(2, None)
        assert result2 is not None

        # Gap of 3 frames - too large
        result3 = tracker.update(3, None)
        assert result3 is None


class TestPoseTrackerHistory:
    """Test position history tracking."""

    def test_get_history_empty(self):
        """Test getting history when empty."""
        tracker = PoseTracker()

        history = tracker.get_history(PoseLandmark.NOSE)

        assert history == []

    def test_get_history_with_data(self, sample_pose_result):
        """Test getting history with data."""
        tracker = PoseTracker()

        # Add frames
        for i in range(5):
            tracker.update(i, sample_pose_result)

        history = tracker.get_history(PoseLandmark.NOSE, num_frames=5)

        assert len(history) == 5
        # All positions should be tuples (x, y)
        for pos in history:
            assert len(pos) == 2

    def test_get_history_limited(self, sample_pose_result):
        """Test getting limited history."""
        tracker = PoseTracker()

        # Add 10 frames
        for i in range(10):
            tracker.update(i, sample_pose_result)

        # Request only 3
        history = tracker.get_history(PoseLandmark.NOSE, num_frames=3)

        assert len(history) == 3


class TestPoseTrackerReset:
    """Test tracker reset."""

    def test_reset(self, sample_pose_result):
        """Test reset clears history."""
        tracker = PoseTracker()

        # Add some frames
        for i in range(5):
            tracker.update(i, sample_pose_result)

        # Reset
        tracker.reset()

        assert len(tracker.pose_history) == 0
        assert tracker.last_valid_frame is None
        assert tracker.current_frame == -1

    def test_reset_and_continue(self, sample_pose_result):
        """Test continuing after reset."""
        tracker = PoseTracker()

        # Add frames
        for i in range(3):
            tracker.update(i, sample_pose_result)

        # Reset
        tracker.reset()

        # Continue from 0
        result = tracker.update(0, sample_pose_result)
        assert result is not None


class TestPoseTrackerStats:
    """Test tracking statistics."""

    def test_stats_all_detections(self, sample_pose_result):
        """Test stats with all valid detections."""
        tracker = PoseTracker()

        for i in range(10):
            tracker.update(i, sample_pose_result)

        stats = tracker.get_tracking_stats()

        assert stats['detection_rate'] == 100.0
        assert stats['avg_confidence'] > 0.8
        assert stats['history_size'] == 5  # Limited by smoothing_window

    def test_stats_with_gaps(self, sample_pose_result):
        """Test stats with some gaps."""
        tracker = PoseTracker(smoothing_window=10)

        # Alternate between detections and gaps
        for i in range(10):
            result = sample_pose_result if i % 2 == 0 else None
            tracker.update(i, result)

        stats = tracker.get_tracking_stats()

        assert stats['detection_rate'] == 50.0
        assert stats['history_size'] == 10

    def test_stats_empty(self):
        """Test stats when no data."""
        tracker = PoseTracker()

        stats = tracker.get_tracking_stats()

        assert stats['detection_rate'] == 0.0
        assert stats['avg_confidence'] == 0.0
        assert stats['history_size'] == 0


class TestPoseTrackerIntegration:
    """Test integration with detector."""

    def test_track_video_sequence(self):
        """Test tracking poses across video sequence."""
        detector = PoseDetector()
        tracker = PoseTracker(smoothing_window=3)

        # Simulate video frames
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(10)]

        results = []
        for i, frame in enumerate(frames):
            detection = detector.detect(frame)
            tracked = tracker.update(i, detection)
            results.append(tracked)

        # All frames should have tracked results
        assert all(r is not None for r in results)

        # Get stats
        stats = tracker.get_tracking_stats()
        assert stats['detection_rate'] == 100.0

        detector.close()

    def test_track_with_detection_failures(self):
        """Test tracking with some detection failures."""
        detector = PoseDetector()
        tracker = PoseTracker(max_gap_frames=5)

        # Simulate detections with gaps
        for i in range(20):
            if i % 4 == 0:
                # Simulate detection failure every 4th frame
                result = tracker.update(i, None)
            else:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                detection = detector.detect(frame)
                result = tracker.update(i, detection)

            # Small gaps should be interpolated
            if i > 0:
                assert result is not None

        detector.close()
