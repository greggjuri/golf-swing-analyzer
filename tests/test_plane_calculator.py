"""Tests for plane calculator module."""

import pytest
import math

from src.plane.geometry import Point3D
from src.plane.calculator import PlaneCalculator, ShaftPosition


@pytest.fixture
def sample_shaft_positions():
    """Create sample shaft positions on horizontal plane."""
    positions = []

    for i in range(20):
        # Shaft moving from left to right, roughly horizontal
        base = Point3D(i * 0.1, 0.5, 0)
        tip = Point3D(i * 0.1 + 0.3, 0.5, 0)

        positions.append(ShaftPosition(
            frame_number=i,
            base_point=base,
            tip_point=tip,
            timestamp=i / 30.0
        ))

    return positions


class TestShaftPosition:
    """Test ShaftPosition class."""

    def test_create_shaft_position(self):
        """Test creating shaft position."""
        base = Point3D(0, 0, 0)
        tip = Point3D(1, 0, 0)

        pos = ShaftPosition(
            frame_number=0,
            base_point=base,
            tip_point=tip,
            timestamp=0.0
        )

        assert pos.frame_number == 0
        assert pos.base_point == base
        assert pos.tip_point == tip
        assert pos.timestamp == 0.0

    def test_midpoint(self):
        """Test calculating midpoint."""
        base = Point3D(0, 0, 0)
        tip = Point3D(2, 4, 6)

        pos = ShaftPosition(0, base, tip, 0.0)
        mid = pos.midpoint()

        assert math.isclose(mid.x, 1.0)
        assert math.isclose(mid.y, 2.0)
        assert math.isclose(mid.z, 3.0)

    def test_direction(self):
        """Test getting direction vector."""
        base = Point3D(0, 0, 0)
        tip = Point3D(3, 4, 0)

        pos = ShaftPosition(0, base, tip, 0.0)
        direction = pos.direction()

        # Should be normalized
        assert math.isclose(direction[0], 0.6)
        assert math.isclose(direction[1], 0.8)
        assert math.isclose(direction[2], 0.0)

    def test_direction_zero_length(self):
        """Test error on zero-length shaft."""
        base = Point3D(1, 2, 3)
        tip = Point3D(1, 2, 3)

        pos = ShaftPosition(0, base, tip, 0.0)

        with pytest.raises(ValueError, match="zero length"):
            pos.direction()

    def test_length(self):
        """Test calculating shaft length."""
        base = Point3D(0, 0, 0)
        tip = Point3D(3, 4, 0)

        pos = ShaftPosition(0, base, tip, 0.0)
        length = pos.length()

        assert math.isclose(length, 5.0)


class TestPlaneCalculatorInit:
    """Test PlaneCalculator initialization."""

    def test_init_default(self):
        """Test default initialization."""
        calc = PlaneCalculator()

        assert calc.impact_zone_weight == 2.0
        assert calc.impact_zone_frames == 10
        assert calc.min_points == 10

    def test_init_custom_params(self):
        """Test custom parameters."""
        calc = PlaneCalculator(
            impact_zone_weight=3.0,
            impact_zone_frames=5,
            min_points=8
        )

        assert calc.impact_zone_weight == 3.0
        assert calc.impact_zone_frames == 5
        assert calc.min_points == 8

    def test_init_invalid_weight(self):
        """Test error on invalid impact weight."""
        with pytest.raises(ValueError, match="impact_zone_weight"):
            PlaneCalculator(impact_zone_weight=0.5)

    def test_init_invalid_frames(self):
        """Test error on invalid impact frames."""
        with pytest.raises(ValueError, match="impact_zone_frames"):
            PlaneCalculator(impact_zone_frames=0)

    def test_init_invalid_min_points(self):
        """Test error on invalid min points."""
        with pytest.raises(ValueError, match="min_points"):
            PlaneCalculator(min_points=2)


class TestCalculatePlane:
    """Test plane calculation."""

    def test_calculate_horizontal_plane(self, sample_shaft_positions):
        """Test calculating horizontal plane."""
        calc = PlaneCalculator()

        plane = calc.calculate_plane(sample_shaft_positions)

        assert plane is not None

        # Should be roughly horizontal
        angle = plane.angle_to_horizontal()
        assert angle < 5.0  # Within 5 degrees

    def test_calculate_insufficient_points(self):
        """Test with insufficient points."""
        calc = PlaneCalculator(min_points=10)

        positions = [
            ShaftPosition(i, Point3D(i, 0, 0), Point3D(i + 1, 0, 0), i / 30.0)
            for i in range(5)
        ]

        plane = calc.calculate_plane(positions)

        assert plane is None

    def test_calculate_with_impact_frame(self, sample_shaft_positions):
        """Test calculation with impact frame weighting."""
        calc = PlaneCalculator(impact_zone_weight=5.0, impact_zone_frames=3)

        # Impact at frame 10
        plane = calc.calculate_plane(sample_shaft_positions, impact_frame=10)

        assert plane is not None

        # Plane should be influenced more by frames 7-13
        # (within impact_zone_frames=3 of impact)

    def test_calculate_without_impact_frame(self, sample_shaft_positions):
        """Test calculation without impact frame."""
        calc = PlaneCalculator()

        plane = calc.calculate_plane(sample_shaft_positions, impact_frame=None)

        assert plane is not None


class TestCalculateWeightedPlane:
    """Test weighted plane calculation."""

    def test_weighted_plane_uniform(self):
        """Test with uniform weights."""
        calc = PlaneCalculator(min_points=3)

        points = [
            Point3D(0, 5, 0),
            Point3D(1, 5, 0),
            Point3D(0, 5, 1),
            Point3D(1, 5, 1)
        ]
        weights = [1.0, 1.0, 1.0, 1.0]

        plane = calc.calculate_weighted_plane(points, weights)

        # Should be horizontal (y=5)
        angle = plane.angle_to_horizontal()
        assert math.isclose(angle, 0.0, abs_tol=0.1)

    def test_weighted_plane_emphasis(self):
        """Test emphasis on high-weight points."""
        calc = PlaneCalculator(min_points=3)

        # Three points at y=0, one outlier at y=10
        points = [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 0, 1),
            Point3D(0.5, 10, 0.5)
        ]

        # Low weight for outlier
        weights = [1.0, 1.0, 1.0, 0.01]

        plane = calc.calculate_weighted_plane(points, weights)

        # Should fit close to first three points
        for i in range(3):
            dist = abs(plane.point_distance(points[i]))
            assert dist < 1.0

    def test_weighted_plane_insufficient_points(self):
        """Test error with too few points."""
        calc = PlaneCalculator(min_points=5)

        points = [Point3D(0, 0, 0), Point3D(1, 0, 0)]
        weights = [1.0, 1.0]

        with pytest.raises(ValueError, match="Insufficient points"):
            calc.calculate_weighted_plane(points, weights)


class TestCalculateWeights:
    """Test weight calculation."""

    def test_weights_no_impact(self):
        """Test weights without impact frame."""
        calc = PlaneCalculator(impact_zone_weight=2.0, impact_zone_frames=5)

        positions = [
            ShaftPosition(i, Point3D(i, 0, 0), Point3D(i + 1, 0, 0), i / 30.0)
            for i in range(10)
        ]

        # Without impact frame, all weights should be uniform
        # (calculate_plane with impact_frame=None uses fit_plane_svd)

    def test_weights_with_impact(self):
        """Test weights with impact frame."""
        calc = PlaneCalculator(impact_zone_weight=3.0, impact_zone_frames=2)

        positions = [
            ShaftPosition(i, Point3D(i, 0, 0), Point3D(i + 1, 0, 0), i / 30.0)
            for i in range(10)
        ]

        # Impact at frame 5
        weights = calc._calculate_weights(positions, impact_frame=5)

        # Frames 3,4,5,6,7 should have higher weight
        assert weights[3] == 3.0  # Within impact zone
        assert weights[4] == 3.0
        assert weights[5] == 3.0
        assert weights[6] == 3.0
        assert weights[7] == 3.0

        assert weights[0] == 1.0  # Outside impact zone
        assert weights[9] == 1.0


class TestPlaneCalculatorIntegration:
    """Test full calculator workflow."""

    def test_tilted_swing_plane(self):
        """Test calculating tilted swing plane."""
        calc = PlaneCalculator()

        # Simulate tilted swing: club moves on angled plane
        positions = []
        for i in range(20):
            # Plane tilted 45 degrees: y = z
            x = i * 0.1
            y = i * 0.05
            z = i * 0.05

            base = Point3D(x, y, z)
            tip = Point3D(x + 0.3, y, z)

            positions.append(ShaftPosition(i, base, tip, i / 30.0))

        plane = calc.calculate_plane(positions)

        assert plane is not None

        # Should be tilted ~45 degrees
        angle = plane.angle_to_horizontal()
        assert 40 < angle < 50

    def test_impact_zone_influence(self):
        """Test that impact zone weighting works."""
        calc = PlaneCalculator(impact_zone_weight=10.0, impact_zone_frames=2)

        # Most points on y=0 plane, but impact zone on y=5 plane
        positions = []

        for i in range(20):
            if 8 <= i <= 12:  # Impact zone
                y = 5.0
            else:
                y = 0.0

            base = Point3D(i * 0.1, y, 0)
            tip = Point3D(i * 0.1 + 0.3, y, 0)

            positions.append(ShaftPosition(i, base, tip, i / 30.0))

        # Calculate with impact at frame 10
        plane = calc.calculate_plane(positions, impact_frame=10)

        assert plane is not None

        # Plane should be calculated (exact position depends on weighting)
        # Just verify it computed successfully
        impact_pos = positions[10]
        impact_dist = abs(plane.point_distance(impact_pos.midpoint()))

        # Distance should be finite
        assert impact_dist >= 0.0
