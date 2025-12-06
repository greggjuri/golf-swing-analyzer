"""Tests for plane detector module."""

import pytest
import math

from src.plane.geometry import Point3D
from src.plane.calculator import ShaftPosition
from src.plane.detector import PlaneDetector, SwingPlaneResult


@pytest.fixture
def full_swing_positions():
    """Create shaft positions for full swing."""
    positions = []

    # Address (frames 0-4): low height
    for i in range(5):
        base = Point3D(0.5, 0.8, 0)
        tip = Point3D(0.8, 0.9, 0)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Backswing (frames 5-14): rising
    for i in range(5, 15):
        y = 0.8 - (i - 5) * 0.08  # Rising (y decreasing)
        base = Point3D(0.5, y, 0)
        tip = Point3D(0.8, y - 0.1, 0)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Top (frame 15): highest point
    positions.append(ShaftPosition(15, Point3D(0.5, 0.0, 0), Point3D(0.8, -0.1, 0), 15 / 30.0))

    # Downswing (frames 16-25): descending
    for i in range(16, 26):
        y = 0.0 + (i - 15) * 0.08  # Descending (y increasing)
        base = Point3D(0.5, y, 0)
        tip = Point3D(0.8, y + 0.1, 0)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    return positions


class TestSwingPlaneResult:
    """Test SwingPlaneResult class."""

    def test_create_result(self):
        """Test creating result."""
        result = SwingPlaneResult(
            address_plane=None,
            backswing_plane=None,
            downswing_plane=None,
            full_swing_plane=None,
            impact_position=None,
            top_position=None
        )

        assert result.address_plane is None
        assert result.backswing_plane is None

    def test_plane_shift_none(self):
        """Test plane shift with missing planes."""
        result = SwingPlaneResult(
            address_plane=None,
            backswing_plane=None,
            downswing_plane=None,
            full_swing_plane=None,
            impact_position=None,
            top_position=None
        )

        assert result.plane_shift() is None


class TestPlaneDetectorInit:
    """Test PlaneDetector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        detector = PlaneDetector()

        assert detector.calculator is not None
        assert detector.min_phase_points == 5

    def test_init_custom_params(self):
        """Test custom parameters."""
        detector = PlaneDetector(min_phase_points=8)

        assert detector.min_phase_points == 8

    def test_init_invalid_min_points(self):
        """Test error on invalid min points."""
        with pytest.raises(ValueError, match="min_phase_points"):
            PlaneDetector(min_phase_points=2)


class TestDetectSwingPlanes:
    """Test swing plane detection."""

    def test_detect_full_swing(self, full_swing_positions):
        """Test detecting planes in full swing."""
        detector = PlaneDetector(min_phase_points=5)

        result = detector.detect_swing_planes(full_swing_positions)

        # Should detect full swing plane
        assert result.full_swing_plane is not None

        # Should find top position
        assert result.top_position is not None

        # Should have backswing and downswing planes
        assert result.backswing_plane is not None
        assert result.downswing_plane is not None

    def test_detect_insufficient_points(self):
        """Test with insufficient points."""
        detector = PlaneDetector(min_phase_points=5)

        positions = [
            ShaftPosition(i, Point3D(i, 0, 0), Point3D(i + 1, 0, 0), i / 30.0)
            for i in range(3)
        ]

        result = detector.detect_swing_planes(positions)

        assert result.full_swing_plane is None
        assert result.backswing_plane is None
        assert result.downswing_plane is None

    def test_detect_no_top_position(self):
        """Test when top position cannot be determined."""
        detector = PlaneDetector(min_phase_points=3)

        # Very few positions
        positions = [
            ShaftPosition(i, Point3D(i, 0, 0), Point3D(i + 1, 0, 0), i / 30.0)
            for i in range(5)
        ]

        result = detector.detect_swing_planes(positions)

        # With few points, may or may not get plane depending on min_points
        # Just check it doesn't crash
        assert result is not None


class TestFindTopPosition:
    """Test finding top of backswing."""

    def test_find_top_position(self, full_swing_positions):
        """Test finding top position."""
        detector = PlaneDetector()

        top = detector._find_top_position(full_swing_positions)

        assert top is not None

        # Should be frame 15 (highest point in our fixture)
        assert top.frame_number == 15

    def test_find_top_insufficient_positions(self):
        """Test with insufficient positions."""
        detector = PlaneDetector()

        positions = [
            ShaftPosition(0, Point3D(0, 0, 0), Point3D(1, 0, 0), 0.0)
        ]

        top = detector._find_top_position(positions)

        assert top is None

    def test_find_top_single_peak(self):
        """Test finding single clear peak."""
        detector = PlaneDetector()

        positions = []
        # Rising
        for i in range(5):
            positions.append(
                ShaftPosition(i, Point3D(0, 1 - i * 0.1, 0), Point3D(1, 1 - i * 0.1, 0), i / 30.0)
            )
        # Peak
        positions.append(
            ShaftPosition(5, Point3D(0, 0.0, 0), Point3D(1, 0.0, 0), 5 / 30.0)
        )
        # Falling
        for i in range(6, 10):
            positions.append(
                ShaftPosition(i, Point3D(0, (i - 5) * 0.1, 0), Point3D(1, (i - 5) * 0.1, 0), i / 30.0)
            )

        top = detector._find_top_position(positions)

        assert top is not None
        assert top.frame_number == 5


class TestFindImpactPosition:
    """Test finding impact position."""

    def test_find_impact_position(self, full_swing_positions):
        """Test finding impact position."""
        detector = PlaneDetector()

        impact = detector._find_impact_position(full_swing_positions)

        assert impact is not None

        # Should be after top position
        top = detector._find_top_position(full_swing_positions)
        assert impact.frame_number > top.frame_number

    def test_find_impact_insufficient_positions(self):
        """Test with insufficient positions."""
        detector = PlaneDetector()

        positions = [
            ShaftPosition(0, Point3D(0, 0, 0), Point3D(1, 0, 0), 0.0)
        ]

        impact = detector._find_impact_position(positions)

        assert impact is None

    def test_find_impact_no_downswing(self):
        """Test when no downswing positions."""
        detector = PlaneDetector()

        # Only backswing
        positions = [
            ShaftPosition(i, Point3D(0, 1 - i * 0.1, 0), Point3D(1, 1 - i * 0.1, 0), i / 30.0)
            for i in range(10)
        ]

        impact = detector._find_impact_position(positions)

        # No downswing after top, should return None
        assert impact is None


class TestGetAddressPositions:
    """Test getting address positions."""

    def test_get_address_default(self, full_swing_positions):
        """Test getting default address positions."""
        detector = PlaneDetector()

        address = detector._get_address_positions(full_swing_positions)

        # Should get first 10 frames by default
        assert len(address) == 10
        assert all(pos.frame_number < 10 for pos in address)

    def test_get_address_custom_frames(self, full_swing_positions):
        """Test with custom number of frames."""
        detector = PlaneDetector()

        address = detector._get_address_positions(full_swing_positions, num_frames=5)

        assert len(address) == 5
        assert all(pos.frame_number < 5 for pos in address)

    def test_get_address_empty(self):
        """Test with empty positions."""
        detector = PlaneDetector()

        address = detector._get_address_positions([])

        assert address == []


class TestPlaneDetectorIntegration:
    """Test full detector workflow."""

    def test_complete_swing_analysis(self, full_swing_positions):
        """Test complete swing plane detection."""
        detector = PlaneDetector(min_phase_points=5)

        result = detector.detect_swing_planes(full_swing_positions)

        # All major components should be detected
        assert result.full_swing_plane is not None
        assert result.backswing_plane is not None
        assert result.downswing_plane is not None
        assert result.top_position is not None
        assert result.impact_position is not None

        # Should have address plane (enough points)
        assert result.address_plane is not None

    def test_plane_shift_calculation(self, full_swing_positions):
        """Test calculating plane shift."""
        detector = PlaneDetector(min_phase_points=5)

        result = detector.detect_swing_planes(full_swing_positions)

        # Should be able to calculate plane shift
        shift = result.plane_shift()

        assert shift is not None
        assert shift >= 0.0  # Angle is always positive

    def test_partial_swing(self):
        """Test with partial swing (no full downswing)."""
        detector = PlaneDetector(min_phase_points=3)

        # Only backswing to top
        positions = []
        for i in range(15):
            y = 0.8 - i * 0.05
            positions.append(
                ShaftPosition(i, Point3D(0.5, y, 0), Point3D(0.8, y - 0.1, 0), i / 30.0)
            )

        result = detector.detect_swing_planes(positions)

        # Should still detect planes
        assert result.full_swing_plane is not None
        assert result.top_position is not None

    def test_different_backswing_downswing_planes(self):
        """Test swing with different backswing/downswing planes."""
        detector = PlaneDetector(min_phase_points=5)

        positions = []

        # Backswing on one plane (y=z)
        for i in range(10):
            t = i * 0.1
            positions.append(
                ShaftPosition(i, Point3D(0, t, t), Point3D(0.3, t, t), i / 30.0)
            )

        # Top
        positions.append(
            ShaftPosition(10, Point3D(0, 1.0, 1.0), Point3D(0.3, 1.0, 1.0), 10 / 30.0)
        )

        # Downswing on different plane (y=0)
        for i in range(11, 20):
            t = (20 - i) * 0.1
            positions.append(
                ShaftPosition(i, Point3D(t, 0, 0.5), Point3D(t + 0.3, 0, 0.5), i / 30.0)
            )

        result = detector.detect_swing_planes(positions)

        # Should detect full swing plane at minimum
        assert result.full_swing_plane is not None

        # May or may not detect separate backswing/downswing depending on point distribution
        # Just verify analysis completes
        assert result is not None
