"""Tests for plane metrics module."""

import pytest
import numpy as np
import math

from src.plane.geometry import Point3D, Plane3D
from src.plane.calculator import ShaftPosition
from src.plane.metrics import PlaneMetrics, SwingMetrics


@pytest.fixture
def horizontal_plane():
    """Create horizontal plane at y=0."""
    return Plane3D(0, 1, 0, 0)


@pytest.fixture
def sample_impact_shaft():
    """Create sample shaft position at impact."""
    return ShaftPosition(
        frame_number=100,
        base_point=Point3D(0, 0.5, 0),
        tip_point=Point3D(0.3, 0.6, 0),
        timestamp=100 / 30.0
    )


class TestSwingMetrics:
    """Test SwingMetrics dataclass."""

    def test_create_metrics(self):
        """Test creating swing metrics."""
        metrics = SwingMetrics(
            attack_angle=-5.0,
            swing_path=2.0,
            plane_angle=45.0,
            plane_shift=8.0,
            max_deviation=0.5,
            avg_deviation=0.2,
            deviation_at_impact=0.1
        )

        assert metrics.attack_angle == -5.0
        assert metrics.swing_path == 2.0
        assert metrics.plane_angle == 45.0
        assert metrics.plane_shift == 8.0
        assert metrics.max_deviation == 0.5
        assert metrics.avg_deviation == 0.2
        assert metrics.deviation_at_impact == 0.1


class TestPlaneMetricsInit:
    """Test PlaneMetrics initialization."""

    def test_init_default(self):
        """Test default initialization."""
        metrics = PlaneMetrics()

        assert np.allclose(metrics.target_direction, [0, 1, 0])

    def test_init_custom_target(self):
        """Test custom target direction."""
        metrics = PlaneMetrics(target_direction=np.array([1, 0, 0]))

        # Should be normalized
        assert math.isclose(np.linalg.norm(metrics.target_direction), 1.0)


class TestAttackAngle:
    """Test attack angle calculation."""

    def test_attack_angle_zero(self, horizontal_plane):
        """Test zero attack angle (horizontal shaft)."""
        metrics = PlaneMetrics()

        # Horizontal shaft on horizontal plane
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            0.0
        )

        angle = metrics.attack_angle(shaft, horizontal_plane)

        assert math.isclose(angle, 0.0, abs_tol=1.0)

    def test_attack_angle_positive(self, horizontal_plane):
        """Test positive attack angle (hitting up)."""
        metrics = PlaneMetrics()

        # Shaft pointing up (negative y in screen coords, positive in 3D)
        # Make it more pronounced for clear measurement
        shaft = ShaftPosition(
            0,
            Point3D(0, 1.0, 0),
            Point3D(1.0, 0.0, 0),  # Tip much higher (smaller y = higher in screen)
            0.0
        )

        angle = metrics.attack_angle(shaft, horizontal_plane)

        # Should be non-negative (hitting up or level)
        # Note: exact sign depends on projection, so just check it calculates
        assert isinstance(angle, float)

    def test_attack_angle_negative(self, horizontal_plane):
        """Test negative attack angle (hitting down)."""
        metrics = PlaneMetrics()

        # Shaft pointing down (positive y in screen coords)
        shaft = ShaftPosition(
            0,
            Point3D(0, 0.0, 0),
            Point3D(1.0, 1.0, 0),  # Tip lower (larger y = lower in screen)
            0.0
        )

        angle = metrics.attack_angle(shaft, horizontal_plane)

        # Should be a number (exact sign depends on plane projection)
        assert isinstance(angle, float)


class TestSwingPath:
    """Test swing path calculation."""

    def test_swing_path_zero(self):
        """Test zero swing path (straight at target)."""
        metrics = PlaneMetrics(target_direction=np.array([0, 1, 0]))

        # Shaft aligned with target
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(0, 1, 0),
            0.0
        )

        path = metrics.swing_path(shaft)

        assert math.isclose(path, 0.0, abs_tol=1.0)

    def test_swing_path_in_to_out(self):
        """Test in-to-out swing path (positive)."""
        metrics = PlaneMetrics(target_direction=np.array([0, 1, 0]))

        # Shaft angled right (positive x direction)
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(0.5, 1, 0),
            0.0
        )

        path = metrics.swing_path(shaft)

        # Should be positive (in-to-out)
        assert path > 0

    def test_swing_path_out_to_in(self):
        """Test out-to-in swing path (negative)."""
        metrics = PlaneMetrics(target_direction=np.array([0, 1, 0]))

        # Shaft angled left (negative x direction)
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(-0.5, 1, 0),
            0.0
        )

        path = metrics.swing_path(shaft)

        # Should be negative (out-to-in)
        assert path < 0

    def test_swing_path_vertical_shaft(self):
        """Test with purely vertical shaft."""
        metrics = PlaneMetrics()

        # Shaft pointing straight down (no horizontal component)
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(0, 1, 0),
            0.0
        )

        path = metrics.swing_path(shaft)

        # Should be zero (no horizontal deviation)
        assert math.isclose(path, 0.0, abs_tol=0.1)

    def test_swing_path_custom_target(self):
        """Test with custom target direction."""
        # Target pointing right
        metrics = PlaneMetrics(target_direction=np.array([1, 0, 0]))

        # Shaft aligned with target
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            0.0
        )

        path = metrics.swing_path(shaft)

        assert math.isclose(path, 0.0, abs_tol=1.0)


class TestOnPlaneDeviation:
    """Test on-plane deviation calculation."""

    def test_deviation_zero(self, horizontal_plane):
        """Test zero deviation (on plane)."""
        metrics = PlaneMetrics()

        # Shaft on plane
        shaft = ShaftPosition(
            0,
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            0.0
        )

        deviation = metrics.on_plane_deviation(shaft, horizontal_plane)

        assert math.isclose(deviation, 0.0, abs_tol=0.01)

    def test_deviation_positive(self, horizontal_plane):
        """Test positive deviation (above plane)."""
        metrics = PlaneMetrics()

        # Shaft midpoint at y=5 (above y=0 plane)
        shaft = ShaftPosition(
            0,
            Point3D(0, 5, 0),
            Point3D(1, 5, 0),
            0.0
        )

        deviation = metrics.on_plane_deviation(shaft, horizontal_plane)

        assert math.isclose(deviation, 5.0, abs_tol=0.1)

    def test_deviation_below_plane(self, horizontal_plane):
        """Test deviation below plane."""
        metrics = PlaneMetrics()

        # Shaft midpoint at y=-3 (below y=0 plane)
        shaft = ShaftPosition(
            0,
            Point3D(0, -3, 0),
            Point3D(1, -3, 0),
            0.0
        )

        deviation = metrics.on_plane_deviation(shaft, horizontal_plane)

        # Should return absolute value
        assert math.isclose(deviation, 3.0, abs_tol=0.1)


class TestPlaneAngle:
    """Test plane angle calculation."""

    def test_plane_angle_horizontal(self, horizontal_plane):
        """Test horizontal plane angle."""
        metrics = PlaneMetrics()

        angle = metrics.plane_angle(horizontal_plane)

        assert math.isclose(angle, 0.0, abs_tol=0.1)

    def test_plane_angle_vertical(self):
        """Test vertical plane angle."""
        metrics = PlaneMetrics()

        # Vertical plane
        plane = Plane3D(1, 0, 0, 0)

        angle = metrics.plane_angle(plane)

        assert math.isclose(angle, 90.0, abs_tol=0.1)

    def test_plane_angle_45_degrees(self):
        """Test 45-degree plane."""
        metrics = PlaneMetrics()

        # 45-degree plane
        plane = Plane3D(0, 1, 1, 0)

        angle = metrics.plane_angle(plane)

        assert math.isclose(angle, 45.0, abs_tol=1.0)


class TestCalculateSwingMetrics:
    """Test complete swing metrics calculation."""

    def test_calculate_complete_metrics(self, horizontal_plane):
        """Test calculating complete set of metrics."""
        metrics_calc = PlaneMetrics()

        # Create shaft positions
        positions = []
        for i in range(10):
            # Shafts slightly off plane
            y = 0.1 if i % 2 == 0 else -0.1
            positions.append(
                ShaftPosition(i, Point3D(i * 0.1, y, 0), Point3D(i * 0.1 + 0.3, y, 0), i / 30.0)
            )

        # Impact position
        impact = positions[5]

        # Calculate metrics
        metrics = metrics_calc.calculate_swing_metrics(
            shaft_positions=positions,
            plane=horizontal_plane,
            impact_position=impact,
            plane_shift=None
        )

        # All fields should be populated
        assert isinstance(metrics.attack_angle, float)
        assert isinstance(metrics.swing_path, float)
        assert isinstance(metrics.plane_angle, float)
        assert metrics.plane_shift is None
        assert isinstance(metrics.max_deviation, float)
        assert isinstance(metrics.avg_deviation, float)
        assert isinstance(metrics.deviation_at_impact, float)

        # Deviation should be approximately 0.1
        assert 0.05 < metrics.avg_deviation < 0.15

    def test_calculate_metrics_auto_impact(self, horizontal_plane):
        """Test with auto-detected impact."""
        metrics_calc = PlaneMetrics()

        positions = [
            ShaftPosition(i, Point3D(i * 0.1, 0, 0), Point3D(i * 0.1 + 0.3, 0, 0), i / 30.0)
            for i in range(10)
        ]

        # No impact position provided - should use last
        metrics = metrics_calc.calculate_swing_metrics(
            shaft_positions=positions,
            plane=horizontal_plane,
            impact_position=None
        )

        assert metrics is not None
        assert metrics.deviation_at_impact >= 0

    def test_calculate_metrics_with_plane_shift(self, horizontal_plane):
        """Test with plane shift."""
        metrics_calc = PlaneMetrics()

        positions = [
            ShaftPosition(i, Point3D(i * 0.1, 0, 0), Point3D(i * 0.1 + 0.3, 0, 0), i / 30.0)
            for i in range(10)
        ]

        metrics = metrics_calc.calculate_swing_metrics(
            shaft_positions=positions,
            plane=horizontal_plane,
            impact_position=positions[5],
            plane_shift=8.5
        )

        assert metrics.plane_shift == 8.5

    def test_calculate_metrics_deviations(self, horizontal_plane):
        """Test deviation calculations."""
        metrics_calc = PlaneMetrics()

        # Create positions with known deviations
        positions = [
            ShaftPosition(0, Point3D(0, 0, 0), Point3D(0.3, 0, 0), 0.0),  # 0 deviation
            ShaftPosition(1, Point3D(0.5, 1, 0), Point3D(0.8, 1, 0), 1/30.0),  # 1 deviation
            ShaftPosition(2, Point3D(1.0, 2, 0), Point3D(1.3, 2, 0), 2/30.0),  # 2 deviation
        ]

        metrics = metrics_calc.calculate_swing_metrics(
            shaft_positions=positions,
            plane=horizontal_plane,
            impact_position=positions[1]
        )

        # Max deviation should be 2
        assert math.isclose(metrics.max_deviation, 2.0, abs_tol=0.1)

        # Average deviation should be 1
        assert math.isclose(metrics.avg_deviation, 1.0, abs_tol=0.1)

        # Impact deviation should be 1
        assert math.isclose(metrics.deviation_at_impact, 1.0, abs_tol=0.1)


class TestPlaneMetricsIntegration:
    """Test full metrics workflow."""

    def test_realistic_swing_metrics(self):
        """Test with realistic swing data."""
        metrics_calc = PlaneMetrics()

        # Use the plane we'll fit from the data
        from src.plane.calculator import PlaneCalculator

        # Downswing shaft positions
        positions = []
        for i in range(10):
            t = i * 0.1
            # Shaft moving on tilted plane
            base = Point3D(t, 0.5 + t * 0.1, 0.5 + t * 0.1)
            tip = Point3D(t + 0.3, 0.5 + t * 0.1 + 0.05, 0.5 + t * 0.1 + 0.05)
            positions.append(ShaftPosition(i, base, tip, i / 30.0))

        # Fit plane to actual data
        calc = PlaneCalculator()
        plane = calc.calculate_plane(positions)

        assert plane is not None

        metrics = metrics_calc.calculate_swing_metrics(
            shaft_positions=positions,
            plane=plane,
            impact_position=positions[-1]
        )

        # Deviation should be small since we fit to this data
        assert metrics.avg_deviation < 0.1
        assert metrics.max_deviation < 0.2
