"""Tests for core angle calculation utilities."""

import pytest
import numpy as np

from src.analysis.angles import (
    angle_between_points,
    angle_between_vectors,
    angle_from_horizontal,
    angle_from_vertical,
    normalize_angle,
    degrees_to_radians,
    radians_to_degrees,
    distance_between_points,
    line_slope,
    point_to_line_distance,
    project_point_onto_line,
    line_intersection,
)


class TestAngleConversions:
    """Tests for angle unit conversions."""

    def test_degrees_to_radians(self):
        """Test degrees to radians conversion."""
        assert abs(degrees_to_radians(0) - 0) < 0.001
        assert abs(degrees_to_radians(90) - np.pi/2) < 0.001
        assert abs(degrees_to_radians(180) - np.pi) < 0.001
        assert abs(degrees_to_radians(360) - 2*np.pi) < 0.001

    def test_radians_to_degrees(self):
        """Test radians to degrees conversion."""
        assert abs(radians_to_degrees(0) - 0) < 0.001
        assert abs(radians_to_degrees(np.pi/2) - 90) < 0.001
        assert abs(radians_to_degrees(np.pi) - 180) < 0.001
        assert abs(radians_to_degrees(2*np.pi) - 360) < 0.001


class TestAngleBetweenVectors:
    """Tests for angle_between_vectors function."""

    def test_perpendicular_vectors(self):
        """Test 90-degree angle between perpendicular vectors."""
        v1 = np.array([1, 0])
        v2 = np.array([0, 1])
        angle = angle_between_vectors(v1, v2)
        assert abs(angle - 90.0) < 0.01

    def test_parallel_vectors(self):
        """Test 0-degree angle between parallel vectors."""
        v1 = np.array([1, 0])
        v2 = np.array([2, 0])
        angle = angle_between_vectors(v1, v2)
        assert abs(angle - 0.0) < 0.01

    def test_opposite_vectors(self):
        """Test 180-degree angle between opposite vectors."""
        v1 = np.array([1, 0])
        v2 = np.array([-1, 0])
        angle = angle_between_vectors(v1, v2)
        assert abs(angle - 180.0) < 0.01

    def test_45_degree_vectors(self):
        """Test 45-degree angle."""
        v1 = np.array([1, 0])
        v2 = np.array([1, 1])
        angle = angle_between_vectors(v1, v2)
        assert abs(angle - 45.0) < 0.01

    def test_zero_length_vector_raises_error(self):
        """Test that zero-length vector raises ValueError."""
        v1 = np.array([0, 0])
        v2 = np.array([1, 0])

        with pytest.raises(ValueError, match="zero length"):
            angle_between_vectors(v1, v2)

        with pytest.raises(ValueError, match="zero length"):
            angle_between_vectors(v2, v1)


class TestAngleBetweenPoints:
    """Tests for angle_between_points function."""

    def test_right_angle(self):
        """Test 90-degree angle."""
        p1 = (0, 0)
        vertex = (1, 0)
        p2 = (1, 1)
        angle = angle_between_points(p1, vertex, p2)
        assert abs(angle - 90.0) < 0.01

    def test_45_degree_angle(self):
        """Test 45-degree angle."""
        p1 = (0, 0)
        vertex = (1, 0)
        p2 = (2, 1)
        angle = angle_between_points(p1, vertex, p2)
        # Actual angle is arctan(1/1) = 45 degrees
        # But from the vectors: (0,0)-(1,0) and (2,1)-(1,0) = (-1,0) and (1,1)
        # Angle between (-1,0) and (1,1) is 135 degrees
        assert abs(angle - 135.0) < 0.1

    def test_straight_line(self):
        """Test 180-degree angle (straight line)."""
        p1 = (0, 0)
        vertex = (1, 0)
        p2 = (2, 0)
        angle = angle_between_points(p1, vertex, p2)
        assert abs(angle - 180.0) < 0.01

    def test_duplicate_point_raises_error(self):
        """Test that duplicate points raise ValueError."""
        p1 = (0, 0)
        vertex = (0, 0)
        p2 = (1, 1)

        with pytest.raises(ValueError, match="identical"):
            angle_between_points(p1, vertex, p2)

    def test_numpy_array_input(self):
        """Test that numpy array inputs work."""
        p1 = np.array([0, 0])
        vertex = np.array([1, 0])
        p2 = np.array([1, 1])
        angle = angle_between_points(p1, vertex, p2)
        assert abs(angle - 90.0) < 0.01


class TestAngleFromHorizontal:
    """Tests for angle_from_horizontal function."""

    def test_horizontal_line(self):
        """Test horizontal line gives 0 degrees."""
        angle = angle_from_horizontal((0, 0), (1, 0))
        assert abs(angle - 0.0) < 0.01

    def test_vertical_line_up(self):
        """Test vertical line upward gives 90 degrees."""
        angle = angle_from_horizontal((0, 0), (0, -1))  # y increases down
        assert abs(angle - (-90.0)) < 0.01

    def test_45_degree_line(self):
        """Test 45-degree line."""
        angle = angle_from_horizontal((0, 0), (1, 1))
        assert abs(angle - 45.0) < 0.01

    def test_negative_45_degree_line(self):
        """Test -45-degree line."""
        angle = angle_from_horizontal((0, 0), (1, -1))
        assert abs(angle - (-45.0)) < 0.01

    def test_identical_points_raises_error(self):
        """Test that identical points raise ValueError."""
        with pytest.raises(ValueError, match="identical"):
            angle_from_horizontal((0, 0), (0, 0))


class TestAngleFromVertical:
    """Tests for angle_from_vertical function."""

    def test_vertical_line(self):
        """Test vertical line gives 0 degrees."""
        angle = angle_from_vertical((0, 0), (0, 1))
        assert abs(angle - 0.0) < 0.01

    def test_horizontal_line(self):
        """Test horizontal line gives 90 degrees."""
        angle = angle_from_vertical((0, 0), (1, 0))
        assert abs(angle - 90.0) < 0.01

    def test_45_degree_from_vertical(self):
        """Test 45-degree angle from vertical."""
        angle = angle_from_vertical((0, 0), (1, 1))
        assert abs(angle - 45.0) < 0.01


class TestNormalizeAngle:
    """Tests for normalize_angle function."""

    def test_normalize_0_360(self):
        """Test normalization to [0, 360) range."""
        assert abs(normalize_angle(0, "0-360") - 0) < 0.01
        assert abs(normalize_angle(180, "0-360") - 180) < 0.01
        assert abs(normalize_angle(360, "0-360") - 0) < 0.01
        assert abs(normalize_angle(450, "0-360") - 90) < 0.01
        assert abs(normalize_angle(-90, "0-360") - 270) < 0.01

    def test_normalize_minus_180_180(self):
        """Test normalization to [-180, 180) range."""
        assert abs(normalize_angle(0, "-180-180") - 0) < 0.01
        assert abs(normalize_angle(90, "-180-180") - 90) < 0.01
        assert abs(normalize_angle(180, "-180-180") - 180) < 0.01
        assert abs(normalize_angle(270, "-180-180") - (-90)) < 0.01
        assert abs(normalize_angle(-90, "-180-180") - (-90)) < 0.01

    def test_normalize_0_180(self):
        """Test normalization to [0, 180] range."""
        assert abs(normalize_angle(0, "0-180") - 0) < 0.01
        assert abs(normalize_angle(90, "0-180") - 90) < 0.01
        assert abs(normalize_angle(180, "0-180") - 180) < 0.01
        assert abs(normalize_angle(270, "0-180") - 90) < 0.01
        assert abs(normalize_angle(-90, "0-180") - 90) < 0.01

    def test_invalid_range_type_raises_error(self):
        """Test that invalid range type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid range_type"):
            normalize_angle(45, "invalid")


class TestDistanceBetweenPoints:
    """Tests for distance_between_points function."""

    def test_horizontal_distance(self):
        """Test horizontal distance."""
        dist = distance_between_points((0, 0), (3, 0))
        assert abs(dist - 3.0) < 0.01

    def test_vertical_distance(self):
        """Test vertical distance."""
        dist = distance_between_points((0, 0), (0, 4))
        assert abs(dist - 4.0) < 0.01

    def test_diagonal_distance(self):
        """Test diagonal distance (3-4-5 triangle)."""
        dist = distance_between_points((0, 0), (3, 4))
        assert abs(dist - 5.0) < 0.01

    def test_zero_distance(self):
        """Test distance between identical points."""
        dist = distance_between_points((1, 2), (1, 2))
        assert abs(dist - 0.0) < 0.01


class TestLineSlope:
    """Tests for line_slope function."""

    def test_horizontal_line(self):
        """Test horizontal line has slope 0."""
        slope = line_slope((0, 1), (1, 1))
        assert abs(slope - 0.0) < 0.01

    def test_45_degree_line(self):
        """Test 45-degree line has slope 1."""
        slope = line_slope((0, 0), (1, 1))
        assert abs(slope - 1.0) < 0.01

    def test_vertical_line(self):
        """Test vertical line returns None."""
        slope = line_slope((1, 0), (1, 1))
        assert slope is None

    def test_negative_slope(self):
        """Test negative slope."""
        slope = line_slope((0, 1), (1, 0))
        assert abs(slope - (-1.0)) < 0.01

    def test_identical_points_raises_error(self):
        """Test that identical points raise ValueError."""
        with pytest.raises(ValueError, match="identical"):
            line_slope((1, 1), (1, 1))


class TestPointToLineDistance:
    """Tests for point_to_line_distance function."""

    def test_point_on_line(self):
        """Test distance is zero for point on line."""
        dist = point_to_line_distance((1, 1), (0, 0), (2, 2))
        assert abs(dist - 0.0) < 0.01

    def test_perpendicular_distance(self):
        """Test perpendicular distance calculation."""
        # Point (0, 1) to line from (0, 0) to (2, 0) should be 1
        dist = point_to_line_distance((0, 1), (0, 0), (2, 0))
        assert abs(dist - 1.0) < 0.01

    def test_distance_from_diagonal(self):
        """Test distance from point to diagonal line."""
        # Point (1, 0) to line y=x should be sqrt(2)/2
        dist = point_to_line_distance((1, 0), (0, 0), (2, 2))
        expected = np.sqrt(2) / 2
        assert abs(dist - expected) < 0.01


class TestProjectPointOntoLine:
    """Tests for project_point_onto_line function."""

    def test_project_onto_horizontal(self):
        """Test projection onto horizontal line."""
        proj = project_point_onto_line((1, 2), (0, 1), (3, 1))
        assert abs(proj[0] - 1) < 0.01
        assert abs(proj[1] - 1) < 0.01

    def test_project_onto_diagonal(self):
        """Test projection onto diagonal line."""
        proj = project_point_onto_line((1, 0), (0, 0), (2, 2))
        assert abs(proj[0] - 0.5) < 0.01
        assert abs(proj[1] - 0.5) < 0.01

    def test_point_on_line(self):
        """Test projection of point already on line."""
        proj = project_point_onto_line((1, 1), (0, 0), (2, 2))
        assert abs(proj[0] - 1) < 0.01
        assert abs(proj[1] - 1) < 0.01


class TestLineIntersection:
    """Tests for line_intersection function."""

    def test_perpendicular_lines(self):
        """Test intersection of perpendicular lines."""
        intersection = line_intersection((0, 1), (2, 1), (1, 0), (1, 2))
        assert intersection is not None
        assert abs(intersection[0] - 1) < 0.01
        assert abs(intersection[1] - 1) < 0.01

    def test_diagonal_lines(self):
        """Test intersection of diagonal lines."""
        intersection = line_intersection((0, 0), (2, 2), (0, 2), (2, 0))
        assert intersection is not None
        assert abs(intersection[0] - 1) < 0.01
        assert abs(intersection[1] - 1) < 0.01

    def test_parallel_lines(self):
        """Test that parallel lines return None."""
        intersection = line_intersection((0, 0), (1, 0), (0, 1), (1, 1))
        assert intersection is None

    def test_zero_length_line_raises_error(self):
        """Test that zero-length line raises ValueError."""
        with pytest.raises(ValueError, match="zero length"):
            line_intersection((0, 0), (0, 0), (1, 0), (2, 0))
