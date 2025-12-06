"""Tests for pose landmark definitions and utilities."""

import pytest

from src.pose.landmarks import (
    PoseLandmark,
    LandmarkPoint,
    POSE_CONNECTIONS,
    BODY_SEGMENTS,
    GOLF_KEY_LANDMARKS,
    get_landmark_name,
    is_left_side,
    is_right_side,
    get_landmark_pair,
)


class TestPoseLandmark:
    """Test PoseLandmark enum."""

    def test_landmark_count(self):
        """Test that we have 33 landmarks."""
        assert len(PoseLandmark) == 33

    def test_landmark_values(self):
        """Test landmark enum values are sequential."""
        values = [landmark.value for landmark in PoseLandmark]
        assert values == list(range(33))

    def test_nose_is_zero(self):
        """Test that NOSE is landmark 0."""
        assert PoseLandmark.NOSE.value == 0

    def test_foot_is_last(self):
        """Test that right foot index is landmark 32."""
        assert PoseLandmark.RIGHT_FOOT_INDEX.value == 32


class TestLandmarkPoint:
    """Test LandmarkPoint dataclass."""

    def test_create_landmark_point(self):
        """Test creating landmark point."""
        point = LandmarkPoint(0.5, 0.5, 0.0, 0.9, 0.95)
        assert point.x == 0.5
        assert point.y == 0.5
        assert point.z == 0.0
        assert point.visibility == 0.9
        assert point.presence == 0.95


class TestPoseConnections:
    """Test pose skeleton connections."""

    def test_connections_type(self):
        """Test connections is list of tuples."""
        assert isinstance(POSE_CONNECTIONS, list)
        for conn in POSE_CONNECTIONS:
            assert isinstance(conn, tuple)
            assert len(conn) == 2

    def test_connections_are_landmarks(self):
        """Test all connections use valid landmarks."""
        for start, end in POSE_CONNECTIONS:
            assert isinstance(start, PoseLandmark)
            assert isinstance(end, PoseLandmark)

    def test_has_torso_connections(self):
        """Test torso connections exist."""
        # Shoulder line
        assert (PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER) in POSE_CONNECTIONS

        # Hip line
        assert (PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP) in POSE_CONNECTIONS

    def test_has_arm_connections(self):
        """Test arm connections exist."""
        # Left arm
        assert (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW) in POSE_CONNECTIONS
        assert (PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST) in POSE_CONNECTIONS

        # Right arm
        assert (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW) in POSE_CONNECTIONS
        assert (PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST) in POSE_CONNECTIONS

    def test_has_leg_connections(self):
        """Test leg connections exist."""
        # Left leg
        assert (PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE) in POSE_CONNECTIONS
        assert (PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE) in POSE_CONNECTIONS

        # Right leg
        assert (PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE) in POSE_CONNECTIONS
        assert (PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE) in POSE_CONNECTIONS


class TestBodySegments:
    """Test body segment groupings."""

    def test_segments_type(self):
        """Test body segments is dictionary."""
        assert isinstance(BODY_SEGMENTS, dict)

    def test_has_expected_segments(self):
        """Test expected body segments exist."""
        expected = [
            'face', 'torso',
            'left_arm', 'right_arm',
            'left_hand', 'right_hand',
            'left_leg', 'right_leg',
            'left_foot', 'right_foot',
        ]
        for segment in expected:
            assert segment in BODY_SEGMENTS

    def test_torso_segment(self):
        """Test torso segment has correct landmarks."""
        torso = BODY_SEGMENTS['torso']
        assert PoseLandmark.LEFT_SHOULDER in torso
        assert PoseLandmark.RIGHT_SHOULDER in torso
        assert PoseLandmark.LEFT_HIP in torso
        assert PoseLandmark.RIGHT_HIP in torso

    def test_left_arm_segment(self):
        """Test left arm segment."""
        left_arm = BODY_SEGMENTS['left_arm']
        assert PoseLandmark.LEFT_SHOULDER in left_arm
        assert PoseLandmark.LEFT_ELBOW in left_arm
        assert PoseLandmark.LEFT_WRIST in left_arm


class TestGolfKeyLandmarks:
    """Test golf-specific key landmarks."""

    def test_is_set(self):
        """Test golf key landmarks is a set."""
        assert isinstance(GOLF_KEY_LANDMARKS, set)

    def test_has_shoulders(self):
        """Test includes shoulders."""
        assert PoseLandmark.LEFT_SHOULDER in GOLF_KEY_LANDMARKS
        assert PoseLandmark.RIGHT_SHOULDER in GOLF_KEY_LANDMARKS

    def test_has_hips(self):
        """Test includes hips."""
        assert PoseLandmark.LEFT_HIP in GOLF_KEY_LANDMARKS
        assert PoseLandmark.RIGHT_HIP in GOLF_KEY_LANDMARKS

    def test_has_arms(self):
        """Test includes arms."""
        assert PoseLandmark.LEFT_ELBOW in GOLF_KEY_LANDMARKS
        assert PoseLandmark.RIGHT_ELBOW in GOLF_KEY_LANDMARKS
        assert PoseLandmark.LEFT_WRIST in GOLF_KEY_LANDMARKS
        assert PoseLandmark.RIGHT_WRIST in GOLF_KEY_LANDMARKS


class TestGetLandmarkName:
    """Test get_landmark_name function."""

    def test_nose_name(self):
        """Test nose landmark name."""
        name = get_landmark_name(PoseLandmark.NOSE)
        assert name == "Nose"

    def test_left_shoulder_name(self):
        """Test left shoulder name."""
        name = get_landmark_name(PoseLandmark.LEFT_SHOULDER)
        assert name == "Left Shoulder"

    def test_right_knee_name(self):
        """Test right knee name."""
        name = get_landmark_name(PoseLandmark.RIGHT_KNEE)
        assert name == "Right Knee"


class TestIsSide:
    """Test is_left_side and is_right_side functions."""

    def test_left_shoulder_is_left(self):
        """Test left shoulder is left side."""
        assert is_left_side(PoseLandmark.LEFT_SHOULDER)
        assert not is_right_side(PoseLandmark.LEFT_SHOULDER)

    def test_right_shoulder_is_right(self):
        """Test right shoulder is right side."""
        assert is_right_side(PoseLandmark.RIGHT_SHOULDER)
        assert not is_left_side(PoseLandmark.RIGHT_SHOULDER)

    def test_nose_is_neither(self):
        """Test nose is neither left nor right."""
        assert not is_left_side(PoseLandmark.NOSE)
        assert not is_right_side(PoseLandmark.NOSE)


class TestGetLandmarkPair:
    """Test get_landmark_pair function."""

    def test_left_shoulder_pair(self):
        """Test left shoulder pair is right shoulder."""
        pair = get_landmark_pair(PoseLandmark.LEFT_SHOULDER)
        assert pair == PoseLandmark.RIGHT_SHOULDER

    def test_right_elbow_pair(self):
        """Test right elbow pair is left elbow."""
        pair = get_landmark_pair(PoseLandmark.RIGHT_ELBOW)
        assert pair == PoseLandmark.LEFT_ELBOW

    def test_symmetry(self):
        """Test pairing is symmetric."""
        left = PoseLandmark.LEFT_WRIST
        right = get_landmark_pair(left)
        assert get_landmark_pair(right) == left

    def test_nose_has_no_pair(self):
        """Test nose has no pair."""
        with pytest.raises(ValueError, match="has no pair"):
            get_landmark_pair(PoseLandmark.NOSE)
