"""Tests for plane analyzer module."""

import pytest
import math

from src.plane.geometry import Point3D, Plane3D
from src.plane.calculator import ShaftPosition
from src.plane.analyzer import SwingPlaneAnalyzer, SwingPlaneAnalysis


@pytest.fixture
def sample_swing_positions():
    """Create sample swing positions."""
    positions = []

    # Simple swing: club moves along y-axis
    for i in range(30):
        y = i * 0.05
        base = Point3D(0.5, y, 0)
        tip = Point3D(0.8, y + 0.1, 0)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    return positions


class TestSwingPlaneAnalysis:
    """Test SwingPlaneAnalysis dataclass."""

    def test_create_analysis(self):
        """Test creating analysis result."""
        from src.plane.detector import SwingPlaneResult
        from src.plane.metrics import SwingMetrics

        analysis = SwingPlaneAnalysis(
            planes=SwingPlaneResult(
                address_plane=None,
                backswing_plane=None,
                downswing_plane=None,
                full_swing_plane=None,
                impact_position=None,
                top_position=None
            ),
            metrics=SwingMetrics(
                attack_angle=0.0,
                swing_path=0.0,
                plane_angle=0.0,
                plane_shift=None,
                max_deviation=0.0,
                avg_deviation=0.0,
                deviation_at_impact=0.0
            ),
            deviations=[],
            success=True
        )

        assert analysis.success is True
        assert analysis.error_message is None


class TestSwingPlaneAnalyzerInit:
    """Test SwingPlaneAnalyzer initialization."""

    def test_init_default(self):
        """Test default initialization."""
        analyzer = SwingPlaneAnalyzer()

        assert analyzer.calculator is not None
        assert analyzer.detector is not None
        assert analyzer.metrics_calculator is not None

    def test_init_custom_components(self):
        """Test with custom components."""
        from src.plane.calculator import PlaneCalculator
        from src.plane.detector import PlaneDetector
        from src.plane.metrics import PlaneMetrics

        calc = PlaneCalculator(min_points=5)
        detector = PlaneDetector(min_phase_points=3)
        metrics = PlaneMetrics()

        analyzer = SwingPlaneAnalyzer(
            calculator=calc,
            detector=detector,
            metrics_calculator=metrics
        )

        assert analyzer.calculator is calc
        assert analyzer.detector is detector
        assert analyzer.metrics_calculator is metrics


class TestAnalyze:
    """Test analyze method."""

    def test_analyze_empty_positions(self):
        """Test with empty shaft positions."""
        analyzer = SwingPlaneAnalyzer()

        result = analyzer.analyze([])

        assert result.success is False
        assert result.error_message == "No shaft positions provided"
        assert result.deviations == []

    def test_analyze_valid_swing(self, sample_swing_positions):
        """Test with valid swing positions."""
        analyzer = SwingPlaneAnalyzer()

        result = analyzer.analyze(sample_swing_positions)

        assert result.success is True
        assert result.error_message is None

        # Should have calculated planes
        assert result.planes.full_swing_plane is not None

        # Should have metrics
        assert isinstance(result.metrics.attack_angle, float)
        assert isinstance(result.metrics.swing_path, float)
        assert isinstance(result.metrics.plane_angle, float)

        # Should have deviations for each position
        assert len(result.deviations) == len(sample_swing_positions)

    def test_analyze_insufficient_points(self):
        """Test with insufficient points."""
        analyzer = SwingPlaneAnalyzer()

        # Only 2 positions
        positions = [
            ShaftPosition(i, Point3D(i, 0, 0), Point3D(i + 1, 0, 0), i / 30.0)
            for i in range(2)
        ]

        result = analyzer.analyze(positions)

        # Should fail gracefully
        assert result.success is False
        assert "Could not calculate swing plane" in result.error_message

    def test_analyze_horizontal_swing(self):
        """Test analyzing horizontal swing."""
        analyzer = SwingPlaneAnalyzer()

        # Horizontal swing at y=0
        positions = [
            ShaftPosition(i, Point3D(i * 0.1, 0, 0), Point3D(i * 0.1 + 0.3, 0, 0), i / 30.0)
            for i in range(20)
        ]

        result = analyzer.analyze(positions)

        assert result.success is True

        # Plane should be roughly horizontal
        assert result.metrics.plane_angle < 10.0

        # Deviations should be small
        assert result.metrics.avg_deviation < 0.5

    def test_analyze_with_downswing_plane(self, sample_swing_positions):
        """Test uses downswing plane when available."""
        analyzer = SwingPlaneAnalyzer()

        result = analyzer.analyze(sample_swing_positions)

        # Should use downswing plane if detected
        if result.planes.downswing_plane is not None:
            # Metrics should be based on downswing plane
            assert result.success is True

    def test_analyze_calculates_all_metrics(self, sample_swing_positions):
        """Test all metrics are calculated."""
        analyzer = SwingPlaneAnalyzer()

        result = analyzer.analyze(sample_swing_positions)

        assert result.success is True

        # All metric fields should be populated
        assert isinstance(result.metrics.attack_angle, float)
        assert isinstance(result.metrics.swing_path, float)
        assert isinstance(result.metrics.plane_angle, float)
        assert isinstance(result.metrics.max_deviation, float)
        assert isinstance(result.metrics.avg_deviation, float)
        assert isinstance(result.metrics.deviation_at_impact, float)

        # Deviations list should match positions
        assert len(result.deviations) == len(sample_swing_positions)


class TestAnalyzeWithPlane:
    """Test analyze_with_plane method."""

    def test_analyze_with_custom_plane(self, sample_swing_positions):
        """Test analyzing with custom plane."""
        analyzer = SwingPlaneAnalyzer()

        # Horizontal plane
        plane = Plane3D(0, 1, 0, 0)

        result = analyzer.analyze_with_plane(sample_swing_positions, plane)

        assert result.success is True
        assert result.planes.full_swing_plane is plane

    def test_analyze_with_plane_empty_positions(self):
        """Test with empty positions."""
        analyzer = SwingPlaneAnalyzer()

        plane = Plane3D(0, 1, 0, 0)

        result = analyzer.analyze_with_plane([], plane)

        assert result.success is False
        assert result.error_message == "No shaft positions provided"

    def test_analyze_with_plane_and_impact_frame(self, sample_swing_positions):
        """Test with specific impact frame."""
        analyzer = SwingPlaneAnalyzer()

        plane = Plane3D(0, 1, 0, 0)

        result = analyzer.analyze_with_plane(
            sample_swing_positions,
            plane,
            impact_frame=15
        )

        assert result.success is True

        # Impact position should be frame 15
        assert result.planes.impact_position is not None
        assert result.planes.impact_position.frame_number == 15

    def test_analyze_with_plane_no_impact_frame(self, sample_swing_positions):
        """Test without impact frame uses last position."""
        analyzer = SwingPlaneAnalyzer()

        plane = Plane3D(0, 1, 0, 0)

        result = analyzer.analyze_with_plane(sample_swing_positions, plane)

        assert result.success is True

        # Should use last position as impact
        assert result.planes.impact_position is not None
        assert result.planes.impact_position == sample_swing_positions[-1]

    def test_analyze_with_plane_calculates_deviations(self, sample_swing_positions):
        """Test deviations are calculated."""
        analyzer = SwingPlaneAnalyzer()

        # Horizontal plane at y=0
        plane = Plane3D(0, 1, 0, 0)

        result = analyzer.analyze_with_plane(sample_swing_positions, plane)

        assert result.success is True

        # Should have deviations for each position
        assert len(result.deviations) == len(sample_swing_positions)

        # All deviations should be positive
        assert all(d >= 0 for d in result.deviations)


class TestSwingPlaneAnalyzerIntegration:
    """Test full analyzer workflow."""

    def test_complete_swing_analysis(self):
        """Test complete swing analysis workflow."""
        analyzer = SwingPlaneAnalyzer()

        # Create realistic swing
        positions = []

        # Backswing (rising)
        for i in range(15):
            y = 0.8 - i * 0.05  # Rising (y decreasing in screen coords)
            base = Point3D(0.5, y, 0)
            tip = Point3D(0.8, y - 0.1, 0)
            positions.append(ShaftPosition(i, base, tip, i / 30.0))

        # Downswing (falling)
        for i in range(15, 30):
            y = (i - 15) * 0.05  # Falling (y increasing)
            base = Point3D(0.5, y, 0)
            tip = Point3D(0.8, y + 0.1, 0)
            positions.append(ShaftPosition(i, base, tip, i / 30.0))

        # Analyze
        result = analyzer.analyze(positions)

        # Should successfully analyze
        assert result.success is True

        # Should detect key positions
        assert result.planes.top_position is not None

        # Should have full swing plane
        assert result.planes.full_swing_plane is not None

        # Metrics should be reasonable
        assert -90 <= result.metrics.attack_angle <= 90
        assert -180 <= result.metrics.swing_path <= 180
        assert 0 <= result.metrics.plane_angle <= 90

    def test_compare_with_ideal_plane(self, sample_swing_positions):
        """Test comparing swing to ideal plane."""
        analyzer = SwingPlaneAnalyzer()

        # Analyze actual swing
        actual_result = analyzer.analyze(sample_swing_positions)

        # Compare to ideal horizontal plane
        ideal_plane = Plane3D(0, 1, 0, 0)
        ideal_result = analyzer.analyze_with_plane(sample_swing_positions, ideal_plane)

        # Both should succeed
        assert actual_result.success is True
        assert ideal_result.success is True

        # Can compare deviations
        assert len(actual_result.deviations) == len(ideal_result.deviations)

    def test_error_handling(self):
        """Test error handling."""
        analyzer = SwingPlaneAnalyzer()

        # Empty list
        result = analyzer.analyze([])
        assert result.success is False
        assert result.error_message is not None

        # Very few points
        positions = [
            ShaftPosition(0, Point3D(0, 0, 0), Point3D(1, 0, 0), 0.0)
        ]
        result = analyzer.analyze(positions)
        assert result.success is False

    def test_metrics_consistency(self, sample_swing_positions):
        """Test metrics are internally consistent."""
        analyzer = SwingPlaneAnalyzer()

        result = analyzer.analyze(sample_swing_positions)

        assert result.success is True

        # Max deviation should be >= average
        assert result.metrics.max_deviation >= result.metrics.avg_deviation

        # Impact deviation should be >= 0
        assert result.metrics.deviation_at_impact >= 0

        # Deviations should match
        assert len(result.deviations) == len(sample_swing_positions)
        assert math.isclose(
            max(result.deviations),
            result.metrics.max_deviation,
            abs_tol=0.01
        )

    def test_different_swing_styles(self):
        """Test analyzing different swing styles."""
        analyzer = SwingPlaneAnalyzer()

        # Flat swing
        flat_positions = [
            ShaftPosition(i, Point3D(i * 0.1, 0, i * 0.05), Point3D(i * 0.1 + 0.3, 0, i * 0.05), i / 30.0)
            for i in range(20)
        ]

        flat_result = analyzer.analyze(flat_positions)
        assert flat_result.success is True

        # Steep swing
        steep_positions = [
            ShaftPosition(i, Point3D(i * 0.05, 0, i * 0.1), Point3D(i * 0.05, 0, i * 0.1 + 0.3), i / 30.0)
            for i in range(20)
        ]

        steep_result = analyzer.analyze(steep_positions)
        assert steep_result.success is True

        # Both should analyze successfully
        # (Actual plane angles would differ but both valid)
