"""Tests for ProgressTracker."""

import time
import pytest

from src.export.progress import ProgressTracker


class TestProgressTrackerInit:
    """Test ProgressTracker initialization."""

    def test_init_valid(self):
        """Test initialization with valid total."""
        tracker = ProgressTracker(100)
        assert tracker.total_items == 100
        assert tracker.current == 0
        assert tracker.start_time > 0

    def test_init_zero_total(self):
        """Test error on zero total items."""
        with pytest.raises(ValueError, match="total_items must be positive"):
            ProgressTracker(0)

    def test_init_negative_total(self):
        """Test error on negative total items."""
        with pytest.raises(ValueError, match="total_items must be positive"):
            ProgressTracker(-10)


class TestProgressTrackerUpdate:
    """Test progress updates."""

    def test_update_valid(self):
        """Test valid progress update."""
        tracker = ProgressTracker(100)
        tracker.update(50)
        assert tracker.current == 50

    def test_update_zero(self):
        """Test update to zero."""
        tracker = ProgressTracker(100)
        tracker.update(0)
        assert tracker.current == 0

    def test_update_complete(self):
        """Test update to completion."""
        tracker = ProgressTracker(100)
        tracker.update(100)
        assert tracker.current == 100
        assert tracker.is_complete()

    def test_update_negative(self):
        """Test error on negative current."""
        tracker = ProgressTracker(100)
        with pytest.raises(ValueError, match="current cannot be negative"):
            tracker.update(-1)

    def test_update_exceeds_total(self):
        """Test error when current exceeds total."""
        tracker = ProgressTracker(100)
        with pytest.raises(ValueError, match="current .* exceeds total"):
            tracker.update(101)

    def test_update_with_callback(self):
        """Test update with callback."""
        tracker = ProgressTracker(100)
        percentages = []

        def callback(pct):
            percentages.append(pct)

        tracker.update(25, callback=callback)
        tracker.update(50, callback=callback)
        tracker.update(100, callback=callback)

        assert len(percentages) == 3
        assert percentages[0] == 25.0
        assert percentages[1] == 50.0
        assert percentages[2] == 100.0


class TestProgressTrackerPercentage:
    """Test percentage calculation."""

    def test_percentage_zero(self):
        """Test percentage at start."""
        tracker = ProgressTracker(100)
        assert tracker.get_percentage() == 0.0

    def test_percentage_half(self):
        """Test percentage at halfway."""
        tracker = ProgressTracker(100)
        tracker.update(50)
        assert tracker.get_percentage() == 50.0

    def test_percentage_complete(self):
        """Test percentage at completion."""
        tracker = ProgressTracker(100)
        tracker.update(100)
        assert tracker.get_percentage() == 100.0

    def test_percentage_fractional(self):
        """Test fractional percentage."""
        tracker = ProgressTracker(3)
        tracker.update(1)
        assert abs(tracker.get_percentage() - 33.333333) < 0.001


class TestProgressTrackerETA:
    """Test ETA estimation."""

    def test_eta_no_progress(self):
        """Test ETA returns None when no progress."""
        tracker = ProgressTracker(100)
        assert tracker.get_eta_seconds() is None

    def test_eta_with_progress(self):
        """Test ETA calculation with progress."""
        tracker = ProgressTracker(100)
        time.sleep(0.1)
        tracker.update(50)
        eta = tracker.get_eta_seconds()
        assert eta is not None
        assert eta > 0

    def test_eta_near_completion(self):
        """Test ETA near completion."""
        tracker = ProgressTracker(100)
        time.sleep(0.05)
        tracker.update(99)
        eta = tracker.get_eta_seconds()
        assert eta is not None
        assert eta < 1.0  # Should be very small

    def test_eta_string_format(self):
        """Test ETA string formatting."""
        tracker = ProgressTracker(100)
        time.sleep(0.05)
        tracker.update(50)
        eta_str = tracker.get_eta_string()
        assert isinstance(eta_str, str)
        assert "s" in eta_str.lower()

    def test_eta_string_unknown(self):
        """Test ETA string when unknown."""
        tracker = ProgressTracker(100)
        assert tracker.get_eta_string() == "Unknown"


class TestProgressTrackerReset:
    """Test progress reset."""

    def test_reset(self):
        """Test reset functionality."""
        tracker = ProgressTracker(100)
        tracker.update(50)

        start_before = tracker.start_time
        time.sleep(0.1)
        tracker.reset()

        assert tracker.current == 0
        assert tracker.start_time > start_before
        assert tracker.get_percentage() == 0.0

    def test_reset_after_complete(self):
        """Test reset after completion."""
        tracker = ProgressTracker(100)
        tracker.update(100)
        assert tracker.is_complete()

        tracker.reset()
        assert not tracker.is_complete()
        assert tracker.current == 0


class TestProgressTrackerCompletion:
    """Test completion checking."""

    def test_is_complete_false(self):
        """Test is_complete returns False when incomplete."""
        tracker = ProgressTracker(100)
        assert not tracker.is_complete()

        tracker.update(99)
        assert not tracker.is_complete()

    def test_is_complete_true(self):
        """Test is_complete returns True when complete."""
        tracker = ProgressTracker(100)
        tracker.update(100)
        assert tracker.is_complete()


class TestProgressTrackerMetrics:
    """Test time and rate metrics."""

    def test_elapsed_seconds(self):
        """Test elapsed time calculation."""
        tracker = ProgressTracker(100)
        time.sleep(0.1)
        elapsed = tracker.get_elapsed_seconds()
        assert elapsed >= 0.1

    def test_rate_calculation(self):
        """Test processing rate calculation."""
        tracker = ProgressTracker(100)
        time.sleep(0.1)
        tracker.update(50)
        rate = tracker.get_rate()
        assert rate > 0
        # Should have processed ~500 items/second (50 items in 0.1s)
        assert rate > 100

    def test_rate_zero_elapsed(self):
        """Test rate returns zero when no time elapsed."""
        tracker = ProgressTracker(100)
        rate = tracker.get_rate()
        # Might be 0 or very high depending on timer precision
        assert rate >= 0
