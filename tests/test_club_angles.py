"""Tests for club angle calculator."""

import pytest
import numpy as np

from src.analysis.club_angles import ClubAngleCalculator


class TestClubAngleCalculator:
    """Tests for ClubAngleCalculator class."""

    def test_initialization(self):
        """Test calculator initialization."""
        calc = ClubAngleCalculator()
        assert calc is not None

    def test_shaft_angle_to_ground_vertical(self):
        """Test shaft angle when club is vertical."""
        calc = ClubAngleCalculator()

        grip = (100, 50)
        club_head = (100, 100)  # Directly below grip

        angle = calc.shaft_angle_to_ground(grip, club_head)

        # Vertical club should be 90 degrees from ground
        assert abs(angle - 90.0) < 0.1

    def test_shaft_angle_to_ground_horizontal(self):
        """Test shaft angle when club is horizontal."""
        calc = ClubAngleCalculator()

        grip = (100, 100)
        club_head = (150, 100)  # Same height

        angle = calc.shaft_angle_to_ground(grip, club_head)

        # Horizontal club should be 0 degrees from ground
        assert abs(angle - 0.0) < 0.1

    def test_shaft_angle_to_ground_typical_iron(self):
        """Test shaft angle for typical iron at address (~65 degrees)."""
        calc = ClubAngleCalculator()

        # Typical 7-iron setup
        grip = (100, 50)
        club_head = (120, 90)

        angle = calc.shaft_angle_to_ground(grip, club_head)

        # Should be in typical iron range (60-70 degrees)
        assert 55 < angle < 75

    def test_shaft_angle_to_vertical_horizontal_club(self):
        """Test shaft angle from vertical when club is horizontal."""
        calc = ClubAngleCalculator()

        grip = (100, 100)
        club_head = (150, 100)

        angle = calc.shaft_angle_to_vertical(grip, club_head)

        # Horizontal club is 90 degrees from vertical
        assert abs(angle - 90.0) < 0.1

    def test_shaft_angle_to_vertical_vertical_club(self):
        """Test shaft angle from vertical when club is vertical."""
        calc = ClubAngleCalculator()

        # Vertical shaft (straight down in image coords)
        grip = (100, 50)
        club_head = (100, 100)  # Same x, increasing y

        angle = calc.shaft_angle_to_vertical(grip, club_head)

        # Vertical club should be 0 degrees from vertical
        assert abs(angle - 0.0) < 1.0

    def test_shaft_angle_to_target_line_parallel(self):
        """Test shaft angle when parallel to target line."""
        calc = ClubAngleCalculator()

        grip = (100, 50)
        club_head = (100, 100)
        target_line = ((0, 75), (200, 75))  # Horizontal target line

        angle = calc.shaft_angle_to_target_line(grip, club_head, target_line)

        # Vertical shaft perpendicular to horizontal target
        assert abs(angle - 90.0) < 0.1

    def test_shaft_angle_to_target_line_aligned(self):
        """Test shaft angle when aligned with target line."""
        calc = ClubAngleCalculator()

        grip = (100, 100)
        club_head = (150, 100)
        target_line = ((0, 100), (200, 100))  # Same line

        angle = calc.shaft_angle_to_target_line(grip, club_head, target_line)

        # Aligned shaft should be 0 degrees
        assert abs(angle - 0.0) < 0.1

    def test_lie_angle_typical_iron(self):
        """Test lie angle for typical iron (60-65 degrees)."""
        calc = ClubAngleCalculator()

        shaft_grip = (100, 50)
        shaft_hosel = (120, 90)
        club_head_toe = (140, 92)
        ground_reference = ((0, 100), (200, 100))

        angle = calc.lie_angle(
            shaft_grip,
            shaft_hosel,
            club_head_toe,
            ground_reference
        )

        # Should be in typical lie angle range
        assert 55 < angle < 70

    def test_swing_plane_angle_typical(self):
        """Test swing plane angle for typical swing."""
        calc = ClubAngleCalculator()

        # Setup typical swing geometry
        # Ball below and to the right, hands above and to the left
        ball_position = (150, 150)
        hands_at_address = (130, 100)
        hands_at_top = (100, 50)

        angle = calc.swing_plane_angle(
            hands_at_address,
            hands_at_top,
            ball_position
        )

        # Should return some angle
        assert 0 < angle < 90

    def test_swing_plane_angle_steep(self):
        """Test steep swing plane."""
        calc = ClubAngleCalculator()

        ball_position = (150, 150)
        hands_at_address = (145, 100)  # Hands close to ball horizontally
        hands_at_top = (140, 40)

        angle = calc.swing_plane_angle(
            hands_at_address,
            hands_at_top,
            ball_position
        )

        # Steeper plane should be larger angle
        assert angle > 60

    def test_swing_plane_angle_flat(self):
        """Test flat swing plane."""
        calc = ClubAngleCalculator()

        ball_position = (150, 150)
        hands_at_address = (140, 140)  # Hands close to ball height
        hands_at_top = (130, 130)

        angle = calc.swing_plane_angle(
            hands_at_address,
            hands_at_top,
            ball_position
        )

        # Should return a valid angle
        assert 0 < angle < 90

    def test_shaft_angle_identical_points_raises_error(self):
        """Test that identical grip and club head raise ValueError."""
        calc = ClubAngleCalculator()

        grip = (100, 100)
        club_head = (100, 100)

        with pytest.raises(ValueError):
            calc.shaft_angle_to_ground(grip, club_head)

    def test_shaft_angle_to_target_line_zero_length_shaft(self):
        """Test error handling for zero-length shaft."""
        calc = ClubAngleCalculator()

        grip = (100, 100)
        club_head = (100, 100)  # Same as grip
        target_line = ((0, 100), (200, 100))

        with pytest.raises(ValueError, match="same position"):
            calc.shaft_angle_to_target_line(grip, club_head, target_line)

    def test_shaft_angle_to_target_line_zero_length_target(self):
        """Test error handling for zero-length target line."""
        calc = ClubAngleCalculator()

        grip = (100, 50)
        club_head = (100, 100)
        target_line = ((50, 75), (50, 75))  # Same points

        with pytest.raises(ValueError, match="zero length"):
            calc.shaft_angle_to_target_line(grip, club_head, target_line)
