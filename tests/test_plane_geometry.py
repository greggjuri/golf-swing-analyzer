"""Tests for plane geometry module."""

import pytest
import numpy as np
import math

from src.plane.geometry import (
    Point3D,
    Plane3D,
    fit_plane_svd,
    plane_line_intersection,
    angle_between_planes,
    weighted_plane_fit
)


class TestPoint3D:
    """Test Point3D class."""

    def test_create_point(self):
        """Test creating a point."""
        p = Point3D(1.0, 2.0, 3.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_to_array(self):
        """Test converting to numpy array."""
        p = Point3D(1.0, 2.0, 3.0)
        arr = p.to_array()

        assert isinstance(arr, np.ndarray)
        assert np.allclose(arr, [1.0, 2.0, 3.0])

    def test_distance_to(self):
        """Test distance calculation."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(3, 4, 0)

        dist = p1.distance_to(p2)
        assert math.isclose(dist, 5.0)

    def test_distance_to_3d(self):
        """Test 3D distance calculation."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(1, 1, 1)

        dist = p1.distance_to(p2)
        assert math.isclose(dist, math.sqrt(3))


class TestPlane3D:
    """Test Plane3D class."""

    def test_create_plane(self):
        """Test creating a plane."""
        plane = Plane3D(0, 1, 0, -5)
        assert plane.a == 0
        assert plane.b == 1
        assert plane.c == 0
        assert plane.d == -5

    def test_normal_vector(self):
        """Test getting normal vector."""
        plane = Plane3D(1, 2, 3, 4)
        normal = plane.normal_vector()

        assert np.allclose(normal, [1, 2, 3])

    def test_normalize(self):
        """Test normalizing plane."""
        plane = Plane3D(3, 4, 0, 10)
        normalized = plane.normalize()

        # Normal should have unit length
        normal = normalized.normal_vector()
        assert math.isclose(np.linalg.norm(normal), 1.0)

        # Components should be scaled consistently
        assert math.isclose(normalized.a, 0.6)
        assert math.isclose(normalized.b, 0.8)
        assert math.isclose(normalized.c, 0.0)

    def test_normalize_zero_normal(self):
        """Test error on normalizing zero normal."""
        plane = Plane3D(0, 0, 0, 1)

        with pytest.raises(ValueError, match="zero normal vector"):
            plane.normalize()

    def test_point_distance(self):
        """Test distance from point to plane."""
        # Horizontal plane at y=5: 0x + 1y + 0z - 5 = 0
        plane = Plane3D(0, 1, 0, -5)

        # Point at y=8 should be distance 3 above plane
        point = Point3D(0, 8, 0)
        dist = plane.point_distance(point)

        assert math.isclose(dist, 3.0)

    def test_point_distance_negative(self):
        """Test negative distance (below plane)."""
        plane = Plane3D(0, 1, 0, -5)

        # Point at y=2 should be distance -3 below plane
        point = Point3D(0, 2, 0)
        dist = plane.point_distance(point)

        assert math.isclose(dist, -3.0)

    def test_project_point(self):
        """Test projecting point onto plane."""
        # Horizontal plane at y=0
        plane = Plane3D(0, 1, 0, 0)

        # Point above plane
        point = Point3D(5, 10, 3)
        projected = plane.project_point(point)

        # Should project to y=0
        assert math.isclose(projected.x, 5)
        assert math.isclose(projected.y, 0)
        assert math.isclose(projected.z, 3)

    def test_angle_to_horizontal(self):
        """Test angle to horizontal plane."""
        # Horizontal plane
        plane = Plane3D(0, 1, 0, 0)
        angle = plane.angle_to_horizontal()
        assert math.isclose(angle, 0.0, abs_tol=0.1)

        # Vertical plane
        plane = Plane3D(1, 0, 0, 0)
        angle = plane.angle_to_horizontal()
        assert math.isclose(angle, 90.0, abs_tol=0.1)

    def test_angle_to_target_line(self):
        """Test angle to target direction."""
        # Plane perpendicular to target
        plane = Plane3D(0, 1, 0, 0)
        target = np.array([0, 1, 0])

        angle = plane.angle_to_target_line(target)
        assert math.isclose(angle, 0.0, abs_tol=0.1)


class TestFitPlaneSVD:
    """Test SVD plane fitting."""

    def test_fit_horizontal_plane(self):
        """Test fitting horizontal plane."""
        # Points on horizontal plane at y=5
        points = [
            Point3D(0, 5, 0),
            Point3D(1, 5, 0),
            Point3D(0, 5, 1),
            Point3D(1, 5, 1)
        ]

        plane = fit_plane_svd(points)
        normalized = plane.normalize()

        # Normal should point up/down (y-axis)
        assert math.isclose(abs(normalized.b), 1.0, abs_tol=0.01)
        assert math.isclose(abs(normalized.a), 0.0, abs_tol=0.01)
        assert math.isclose(abs(normalized.c), 0.0, abs_tol=0.01)

    def test_fit_tilted_plane(self):
        """Test fitting tilted plane."""
        # Points on plane: z = x (45 degree tilt)
        points = [
            Point3D(0, 0, 0),
            Point3D(1, 0, 1),
            Point3D(0, 1, 0),
            Point3D(1, 1, 1)
        ]

        plane = fit_plane_svd(points)

        # All points should be on plane (distance ~0)
        for p in points:
            dist = plane.point_distance(p)
            assert math.isclose(dist, 0.0, abs_tol=0.01)

    def test_fit_insufficient_points(self):
        """Test error with too few points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1)]

        with pytest.raises(ValueError, match="at least 3 points"):
            fit_plane_svd(points)

    def test_fit_noisy_points(self):
        """Test fitting with noisy points."""
        # Points roughly on horizontal plane with noise
        points = [
            Point3D(i, 5 + 0.1 * np.random.randn(), j)
            for i in range(5)
            for j in range(5)
        ]

        plane = fit_plane_svd(points)

        # Should still fit approximately horizontal plane
        angle = plane.angle_to_horizontal()
        assert angle < 5.0  # Within 5 degrees of horizontal


class TestPlaneLineIntersection:
    """Test plane-line intersection."""

    def test_intersection_perpendicular(self):
        """Test intersection with perpendicular line."""
        # Horizontal plane at y=0
        plane = Plane3D(0, 1, 0, 0)

        # Vertical line through (0, 5, 0) pointing down
        line_point = Point3D(0, 5, 0)
        line_dir = np.array([0, -1, 0])

        intersection = plane_line_intersection(plane, line_point, line_dir)

        assert intersection is not None
        assert math.isclose(intersection.x, 0)
        assert math.isclose(intersection.y, 0)
        assert math.isclose(intersection.z, 0)

    def test_intersection_angled(self):
        """Test intersection with angled line."""
        # Horizontal plane at y=0
        plane = Plane3D(0, 1, 0, 0)

        # Line at 45 degrees
        line_point = Point3D(0, 10, 0)
        line_dir = np.array([1, -1, 0]) / np.sqrt(2)

        intersection = plane_line_intersection(plane, line_point, line_dir)

        assert intersection is not None
        assert math.isclose(intersection.y, 0)
        assert math.isclose(intersection.x, 10)

    def test_intersection_parallel(self):
        """Test no intersection with parallel line."""
        # Horizontal plane at y=0
        plane = Plane3D(0, 1, 0, 0)

        # Horizontal line
        line_point = Point3D(0, 5, 0)
        line_dir = np.array([1, 0, 0])

        intersection = plane_line_intersection(plane, line_point, line_dir)

        assert intersection is None


class TestAngleBetweenPlanes:
    """Test angle between planes."""

    def test_angle_parallel_planes(self):
        """Test angle between parallel planes."""
        plane1 = Plane3D(0, 1, 0, 0)
        plane2 = Plane3D(0, 1, 0, -5)

        angle = angle_between_planes(plane1, plane2)
        assert math.isclose(angle, 0.0, abs_tol=0.1)

    def test_angle_perpendicular_planes(self):
        """Test angle between perpendicular planes."""
        plane1 = Plane3D(0, 1, 0, 0)  # Horizontal
        plane2 = Plane3D(1, 0, 0, 0)  # Vertical

        angle = angle_between_planes(plane1, plane2)
        assert math.isclose(angle, 90.0, abs_tol=0.1)

    def test_angle_45_degree_planes(self):
        """Test angle between 45-degree planes."""
        plane1 = Plane3D(0, 1, 0, 0)
        plane2 = Plane3D(1, 1, 0, 0)

        angle = angle_between_planes(plane1, plane2)
        assert math.isclose(angle, 45.0, abs_tol=0.1)


class TestWeightedPlaneFit:
    """Test weighted plane fitting."""

    def test_weighted_fit_uniform(self):
        """Test weighted fit with uniform weights."""
        points = [
            Point3D(0, 5, 0),
            Point3D(1, 5, 0),
            Point3D(0, 5, 1),
            Point3D(1, 5, 1)
        ]
        weights = [1.0, 1.0, 1.0, 1.0]

        plane = weighted_plane_fit(points, weights)

        # Should fit horizontal plane (y=5)
        angle = plane.angle_to_horizontal()
        assert math.isclose(angle, 0.0, abs_tol=0.1)

    def test_weighted_fit_emphasis(self):
        """Test weighted fit emphasizes high-weight points."""
        # Three points at y=0, one outlier at y=10
        points = [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 0, 1),
            Point3D(0.5, 10, 0.5)  # Outlier
        ]

        # Low weight for outlier
        weights = [1.0, 1.0, 1.0, 0.01]

        plane = weighted_plane_fit(points, weights)

        # Should still fit close to y=0 plane
        for i in range(3):
            dist = abs(plane.point_distance(points[i]))
            assert dist < 1.0  # Close to first three points

    def test_weighted_fit_mismatched_lengths(self):
        """Test error with mismatched lengths."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1)]
        weights = [1.0]

        with pytest.raises(ValueError, match="same length"):
            weighted_plane_fit(points, weights)

    def test_weighted_fit_insufficient_points(self):
        """Test error with too few points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1)]
        weights = [1.0, 1.0]

        with pytest.raises(ValueError, match="at least 3 points"):
            weighted_plane_fit(points, weights)

    def test_weighted_fit_zero_weights(self):
        """Test error with zero total weight."""
        points = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)]
        weights = [0.0, 0.0, 0.0]

        with pytest.raises(ValueError, match="Total weight must be positive"):
            weighted_plane_fit(points, weights)
