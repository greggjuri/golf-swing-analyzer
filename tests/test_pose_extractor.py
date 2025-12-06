"""Tests for landmark extractor."""

import pytest
import numpy as np

from src.pose import PoseDetector, LandmarkExtractor, PoseLandmark
from src.pose.landmarks import LandmarkPoint
from src.pose.detector import PoseResult


@pytest.fixture
def sample_pose_result():
    """Create sample pose result for testing."""
    landmarks = {
        # Head
        PoseLandmark.NOSE: LandmarkPoint(0.5, 0.15, 0.0, 0.95, 0.98),

        # Shoulders
        PoseLandmark.LEFT_SHOULDER: LandmarkPoint(0.4, 0.3, 0.0, 0.95, 0.98),
        PoseLandmark.RIGHT_SHOULDER: LandmarkPoint(0.6, 0.3, 0.0, 0.95, 0.98),

        # Elbows
        PoseLandmark.LEFT_ELBOW: LandmarkPoint(0.35, 0.45, 0.0, 0.9, 0.95),
        PoseLandmark.RIGHT_ELBOW: LandmarkPoint(0.65, 0.45, 0.0, 0.9, 0.95),

        # Wrists
        PoseLandmark.LEFT_WRIST: LandmarkPoint(0.38, 0.55, 0.0, 0.85, 0.9),
        PoseLandmark.RIGHT_WRIST: LandmarkPoint(0.62, 0.55, 0.0, 0.85, 0.9),

        # Hips
        PoseLandmark.LEFT_HIP: LandmarkPoint(0.45, 0.6, 0.0, 0.95, 0.98),
        PoseLandmark.RIGHT_HIP: LandmarkPoint(0.55, 0.6, 0.0, 0.95, 0.98),

        # Knees
        PoseLandmark.LEFT_KNEE: LandmarkPoint(0.45, 0.75, 0.0, 0.9, 0.95),
        PoseLandmark.RIGHT_KNEE: LandmarkPoint(0.55, 0.75, 0.0, 0.9, 0.95),

        # Ankles
        PoseLandmark.LEFT_ANKLE: LandmarkPoint(0.45, 0.9, 0.0, 0.85, 0.9),
        PoseLandmark.RIGHT_ANKLE: LandmarkPoint(0.55, 0.9, 0.0, 0.85, 0.9),
    }

    return PoseResult(
        landmarks=landmarks,
        world_landmarks=landmarks.copy(),
        timestamp=0.0,
        detection_confidence=0.9
    )


class TestLandmarkExtractorInit:
    """Test LandmarkExtractor initialization."""

    def test_init_valid(self):
        """Test valid initialization."""
        extractor = LandmarkExtractor(1920, 1080)
        assert extractor.frame_width == 1920
        assert extractor.frame_height == 1080

    def test_init_invalid_dimensions(self):
        """Test error on invalid dimensions."""
        with pytest.raises(ValueError, match="dimensions must be positive"):
            LandmarkExtractor(0, 1080)

        with pytest.raises(ValueError, match="dimensions must be positive"):
            LandmarkExtractor(1920, -10)


class TestGetPixelPosition:
    """Test pixel position conversion."""

    def test_get_pixel_position(self, sample_pose_result):
        """Test converting normalized to pixel coordinates."""
        extractor = LandmarkExtractor(1920, 1080)

        nose_pos = extractor.get_pixel_position(sample_pose_result, PoseLandmark.NOSE)

        assert nose_pos is not None
        assert nose_pos.x == 0.5 * 1920  # 960
        assert nose_pos.y == 0.15 * 1080  # 162

    def test_get_pixel_position_missing(self, sample_pose_result):
        """Test returns None for missing landmark."""
        extractor = LandmarkExtractor(1920, 1080)

        # EYE not in sample_pose_result
        pos = extractor.get_pixel_position(sample_pose_result, PoseLandmark.LEFT_EYE)

        assert pos is None


class TestGetJointAngle:
    """Test joint angle calculation."""

    def test_get_elbow_angle(self, sample_pose_result):
        """Test calculating elbow angle."""
        extractor = LandmarkExtractor(1920, 1080)

        # Left elbow angle
        angle = extractor.get_joint_angle(
            sample_pose_result,
            PoseLandmark.LEFT_ELBOW,
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.LEFT_WRIST
        )

        assert angle is not None
        assert 0 <= angle <= 180

    def test_get_knee_angle(self, sample_pose_result):
        """Test calculating knee angle."""
        extractor = LandmarkExtractor(1920, 1080)

        angle = extractor.get_joint_angle(
            sample_pose_result,
            PoseLandmark.LEFT_KNEE,
            PoseLandmark.LEFT_HIP,
            PoseLandmark.LEFT_ANKLE
        )

        assert angle is not None
        assert 0 <= angle <= 180

    def test_get_joint_angle_missing_landmark(self, sample_pose_result):
        """Test returns None when landmark missing."""
        extractor = LandmarkExtractor(1920, 1080)

        # LEFT_EYE not in sample
        angle = extractor.get_joint_angle(
            sample_pose_result,
            PoseLandmark.LEFT_EYE,
            PoseLandmark.NOSE,
            PoseLandmark.LEFT_EAR
        )

        assert angle is None


class TestGetBodyCenter:
    """Test body center calculation."""

    def test_get_body_center(self, sample_pose_result):
        """Test calculating center between hips."""
        extractor = LandmarkExtractor(1920, 1080)

        center = extractor.get_body_center(sample_pose_result)

        assert center is not None
        # Center of hips at x=0.45 and x=0.55 should be x=0.5
        expected_x = 0.5 * 1920
        expected_y = 0.6 * 1080

        assert abs(center.x - expected_x) < 0.1
        assert abs(center.y - expected_y) < 0.1


class TestGetShoulderLine:
    """Test shoulder line extraction."""

    def test_get_shoulder_line(self, sample_pose_result):
        """Test getting line through shoulders."""
        extractor = LandmarkExtractor(1920, 1080)

        line = extractor.get_shoulder_line(sample_pose_result)

        assert line is not None
        # Shoulders are at same y=0.3, so line should be horizontal (m≈0)
        assert abs(line.m) < 0.01


class TestGetHipLine:
    """Test hip line extraction."""

    def test_get_hip_line(self, sample_pose_result):
        """Test getting line through hips."""
        extractor = LandmarkExtractor(1920, 1080)

        line = extractor.get_hip_line(sample_pose_result)

        assert line is not None
        # Hips are at same y=0.6, so line should be horizontal
        assert abs(line.m) < 0.01


class TestGetSpineAngle:
    """Test spine angle calculation."""

    def test_get_spine_angle(self, sample_pose_result):
        """Test calculating spine angle from vertical."""
        extractor = LandmarkExtractor(1920, 1080)

        angle = extractor.get_spine_angle(sample_pose_result)

        assert angle is not None
        # Vertical spine should be close to 90 degrees
        assert 80 <= angle <= 100


class TestGetRotations:
    """Test rotation measurements."""

    def test_get_shoulder_rotation(self, sample_pose_result):
        """Test shoulder rotation calculation."""
        extractor = LandmarkExtractor(1920, 1080)

        rotation = extractor.get_shoulder_rotation(sample_pose_result)

        assert rotation is not None
        # Horizontal shoulders should have rotation ≈ 0
        assert abs(rotation) < 5

    def test_get_hip_rotation(self, sample_pose_result):
        """Test hip rotation calculation."""
        extractor = LandmarkExtractor(1920, 1080)

        rotation = extractor.get_hip_rotation(sample_pose_result)

        assert rotation is not None
        assert abs(rotation) < 5


class TestGetXFactor:
    """Test X-Factor calculation."""

    def test_get_x_factor(self, sample_pose_result):
        """Test X-Factor (shoulder-hip separation)."""
        extractor = LandmarkExtractor(1920, 1080)

        x_factor = extractor.get_x_factor(sample_pose_result)

        assert x_factor is not None
        assert x_factor >= 0  # X-Factor is absolute value


class TestIntegration:
    """Test integration with real detector."""

    def test_full_pipeline(self):
        """Test complete detection and extraction pipeline."""
        detector = PoseDetector()
        extractor = LandmarkExtractor(640, 480)

        # Create test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Detect
        result = detector.detect(frame)
        assert result is not None

        # Extract measurements
        spine_angle = extractor.get_spine_angle(result)
        body_center = extractor.get_body_center(result)
        shoulder_line = extractor.get_shoulder_line(result)

        # All should return valid results with placeholder
        assert spine_angle is not None
        assert body_center is not None
        assert shoulder_line is not None

        detector.close()
