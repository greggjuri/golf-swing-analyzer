"""Tests for joint angle calculator."""

import pytest
import numpy as np

from src.analysis.joint_angles import JointAngleCalculator, BodyLandmark


class TestJointAngleCalculator:
    """Tests for JointAngleCalculator class."""

    def test_initialization_right_handed(self):
        """Test initialization for right-handed golfer."""
        calc = JointAngleCalculator(handedness="right")
        assert calc.handedness == "right"

    def test_initialization_left_handed(self):
        """Test initialization for left-handed golfer."""
        calc = JointAngleCalculator(handedness="left")
        assert calc.handedness == "left"

    def test_invalid_handedness_raises_error(self):
        """Test that invalid handedness raises ValueError."""
        with pytest.raises(ValueError, match="Invalid handedness"):
            JointAngleCalculator(handedness="ambidextrous")

    def test_elbow_angle_full_extension(self):
        """Test elbow angle at full extension (~180 degrees)."""
        calc = JointAngleCalculator()

        shoulder = (0, 0)
        elbow = (1, 0)
        wrist = (2, 0)

        angle = calc.elbow_angle(shoulder, elbow, wrist)
        assert abs(angle - 180.0) < 0.1

    def test_elbow_angle_90_degrees(self):
        """Test elbow angle at 90-degree flex."""
        calc = JointAngleCalculator()

        shoulder = (0, 0)
        elbow = (1, 0)
        wrist = (1, 1)

        angle = calc.elbow_angle(shoulder, elbow, wrist)
        assert abs(angle - 90.0) < 0.1

    def test_knee_angle_address_position(self):
        """Test knee angle at address position (~150 degrees)."""
        calc = JointAngleCalculator()

        # Typical address position (slight knee flex)
        # Create points that form ~150 degree angle
        hip = (100, 50)
        knee = (105, 100)
        ankle = (107, 150)

        angle = calc.knee_angle(hip, knee, ankle)

        # Should be in typical range or close to it
        assert 140 < angle < 180

    def test_spine_angle_forward_tilt(self):
        """Test spine angle with forward tilt."""
        calc = JointAngleCalculator()

        # Spine tilted forward (in image coords: shoulder left and up from hip)
        hip = (100, 100)
        shoulder = (80, 50)  # Left and up

        angle = calc.spine_angle(shoulder, hip)

        # Should show some tilt
        assert 0 < angle < 90

    def test_spine_angle_upright(self):
        """Test spine angle when nearly vertical."""
        calc = JointAngleCalculator()

        # Perfectly vertical spine (shoulder directly above hip in y)
        hip = (100, 100)
        shoulder = (100, 50)  # Directly above (lower y value)

        angle = calc.spine_angle(shoulder, hip)

        # Should be close to 0 (vertical alignment)
        assert angle < 1

    def test_shoulder_angle(self):
        """Test shoulder angle calculation."""
        calc = JointAngleCalculator()

        shoulder = (100, 100)
        elbow = (150, 120)
        hip = (100, 150)

        angle = calc.shoulder_angle(shoulder, elbow, hip)

        # Should return valid angle
        assert 0 <= angle <= 180

    def test_hip_angle(self):
        """Test hip angle calculation."""
        calc = JointAngleCalculator()

        shoulder = (100, 50)
        hip = (100, 100)
        knee = (110, 150)

        angle = calc.hip_angle(shoulder, hip, knee)

        # Should return valid angle
        assert 0 <= angle <= 180

    def test_wrist_hinge_angle(self):
        """Test wrist hinge angle calculation."""
        calc = JointAngleCalculator()

        elbow = (100, 100)
        wrist = (150, 110)
        club_grip = (180, 140)

        angle = calc.wrist_hinge_angle(elbow, wrist, club_grip)

        # Should return valid angle
        assert 0 <= angle <= 180

    def test_wrist_hinge_90_degrees(self):
        """Test wrist hinge at 90 degrees (maximum hinge)."""
        calc = JointAngleCalculator()

        elbow = (0, 0)
        wrist = (1, 0)
        club_grip = (1, 1)

        angle = calc.wrist_hinge_angle(elbow, wrist, club_grip)
        assert abs(angle - 90.0) < 0.1

    def test_get_typical_ranges(self):
        """Test that typical ranges are returned."""
        calc = JointAngleCalculator()
        ranges = calc.get_typical_ranges()

        # Check that key ranges exist
        assert 'knee_flex_address' in ranges
        assert 'spine_tilt_address' in ranges
        assert 'wrist_hinge_top' in ranges

        # Check format (min, max)
        for key, (min_val, max_val) in ranges.items():
            assert min_val < max_val
            assert 0 <= min_val <= 180
            assert 0 <= max_val <= 180

    def test_typical_knee_flex_range(self):
        """Test typical knee flex range values."""
        calc = JointAngleCalculator()
        ranges = calc.get_typical_ranges()

        min_angle, max_angle = ranges['knee_flex_address']
        assert 130 < min_angle < 150  # Reasonable range
        assert 150 < max_angle < 170


class TestBodyLandmark:
    """Tests for BodyLandmark constants."""

    def test_landmark_values(self):
        """Test that landmark indices are defined."""
        assert BodyLandmark.NOSE == 0
        assert BodyLandmark.LEFT_SHOULDER == 11
        assert BodyLandmark.RIGHT_SHOULDER == 12
        assert BodyLandmark.LEFT_ELBOW == 13
        assert BodyLandmark.RIGHT_ELBOW == 14
        assert BodyLandmark.LEFT_WRIST == 15
        assert BodyLandmark.RIGHT_WRIST == 16
        assert BodyLandmark.LEFT_HIP == 23
        assert BodyLandmark.RIGHT_HIP == 24
        assert BodyLandmark.LEFT_KNEE == 25
        assert BodyLandmark.RIGHT_KNEE == 26
        assert BodyLandmark.LEFT_ANKLE == 27
        assert BodyLandmark.RIGHT_ANKLE == 28

    def test_landmarks_are_unique(self):
        """Test that all landmark values are unique."""
        landmarks = [
            BodyLandmark.NOSE,
            BodyLandmark.LEFT_SHOULDER,
            BodyLandmark.RIGHT_SHOULDER,
            BodyLandmark.LEFT_ELBOW,
            BodyLandmark.RIGHT_ELBOW,
            BodyLandmark.LEFT_WRIST,
            BodyLandmark.RIGHT_WRIST,
            BodyLandmark.LEFT_HIP,
            BodyLandmark.RIGHT_HIP,
            BodyLandmark.LEFT_KNEE,
            BodyLandmark.RIGHT_KNEE,
            BodyLandmark.LEFT_ANKLE,
            BodyLandmark.RIGHT_ANKLE,
        ]

        assert len(landmarks) == len(set(landmarks))
