"""Tests for video.frame_extractor module."""

import pytest
import numpy as np
from pathlib import Path

from src.video.loader import VideoLoader
from src.video.frame_extractor import FrameExtractor, KeyPositionDetector


# Test video path
TEST_VIDEO_PATH = Path(__file__).parent / "test_data" / "test_swing.mp4"


class TestFrameExtractor:
    """Tests for FrameExtractor class."""

    def test_extract_frame_default_scale(self):
        """Test extracting a frame with default scale."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            frame = extractor.extract_frame(0)
            assert frame is not None
            assert isinstance(frame, np.ndarray)
            assert frame.shape == (480, 640, 3)

    def test_extract_frame_with_scaling(self):
        """Test extracting a frame with different scale factors."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # Scale to half size
            frame_half = extractor.extract_frame(0, scale=0.5)
            assert frame_half.shape == (240, 320, 3)

            # Scale to quarter size
            frame_quarter = extractor.extract_frame(0, scale=0.25)
            assert frame_quarter.shape == (120, 160, 3)

    def test_extract_frame_uses_default_scale(self):
        """Test that default scale is applied when scale not specified."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=0.5)

            frame = extractor.extract_frame(10)
            assert frame.shape == (240, 320, 3)

    def test_cache_hit(self):
        """Test that cache correctly returns cached frames."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # First access - cache miss
            frame1 = extractor.extract_frame(5)
            assert extractor.misses == 1
            assert extractor.hits == 0

            # Second access - cache hit
            frame2 = extractor.extract_frame(5)
            assert extractor.misses == 1
            assert extractor.hits == 1

            # Frames should be equal
            assert np.array_equal(frame1, frame2)

    def test_cache_different_scales(self):
        """Test that cache stores frames with different scales separately."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # Extract same frame with different scales
            frame_1x = extractor.extract_frame(5, scale=1.0)
            frame_half = extractor.extract_frame(5, scale=0.5)

            # Both should be cache misses
            assert extractor.misses == 2
            assert extractor.hits == 0

            # Access again
            frame_1x_again = extractor.extract_frame(5, scale=1.0)
            frame_half_again = extractor.extract_frame(5, scale=0.5)

            # Both should be cache hits
            assert extractor.hits == 2

    def test_cache_lru_eviction(self):
        """Test that LRU eviction works correctly."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=3, default_scale=1.0)

            # Fill cache (3 frames)
            extractor.extract_frame(0)
            extractor.extract_frame(1)
            extractor.extract_frame(2)

            assert len(extractor._cache) == 3
            assert extractor.misses == 3

            # Access frame 0 to make it recently used
            extractor.extract_frame(0)
            assert extractor.hits == 1

            # Add frame 3 - should evict frame 1 (least recently used)
            extractor.extract_frame(3)
            assert len(extractor._cache) == 3
            assert (1, 1.0) not in extractor._cache
            assert (0, 1.0) in extractor._cache  # Recently accessed
            assert (2, 1.0) in extractor._cache
            assert (3, 1.0) in extractor._cache

    def test_extract_range(self):
        """Test extracting a range of frames."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=20, default_scale=1.0)

            frames = extractor.extract_range(0, 10, step=1)

            assert len(frames) == 10
            assert all(isinstance(f, np.ndarray) for f in frames)
            assert all(f.shape == (480, 640, 3) for f in frames)

    def test_extract_range_with_step(self):
        """Test extracting range with step parameter."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=20, default_scale=1.0)

            frames = extractor.extract_range(0, 20, step=2)

            assert len(frames) == 10  # Every other frame

    def test_extract_range_with_scale(self):
        """Test extracting range with scaling."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=20, default_scale=1.0)

            frames = extractor.extract_range(0, 5, step=1, scale=0.5)

            assert len(frames) == 5
            assert all(f.shape == (240, 320, 3) for f in frames)

    def test_extract_range_invalid_start(self):
        """Test that invalid start frame raises ValueError."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            with pytest.raises(ValueError, match="Invalid start_frame"):
                extractor.extract_range(-1, 10)

    def test_extract_range_invalid_end(self):
        """Test that invalid end frame raises ValueError."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            with pytest.raises(ValueError, match="Invalid range"):
                extractor.extract_range(10, 5)  # end < start

    def test_extract_range_invalid_step(self):
        """Test that invalid step raises ValueError."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            with pytest.raises(ValueError, match="Invalid step"):
                extractor.extract_range(0, 10, step=0)

    def test_invalid_frame_number(self):
        """Test that invalid frame number raises ValueError."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)
            meta = loader.get_metadata()

            with pytest.raises(ValueError, match="Invalid frame number"):
                extractor.extract_frame(meta.frame_count + 10)

    def test_invalid_scale_factor(self):
        """Test that invalid scale factor raises ValueError."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # Test zero scale
            with pytest.raises(ValueError, match="Invalid scale factor"):
                extractor.extract_frame(0, scale=0)

        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # Test negative scale
            with pytest.raises(ValueError, match="Invalid scale factor"):
                extractor.extract_frame(0, scale=-0.5)

    def test_clear_cache(self):
        """Test clearing the cache."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # Fill cache
            extractor.extract_frame(0)
            extractor.extract_frame(1)
            extractor.extract_frame(2)

            assert len(extractor._cache) == 3

            # Clear cache
            extractor.clear_cache()

            assert len(extractor._cache) == 0
            assert len(extractor._cache_order) == 0

            # Accessing same frames should be cache misses
            initial_misses = extractor.misses
            extractor.extract_frame(0)
            assert extractor.misses == initial_misses + 1

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            extractor = FrameExtractor(loader, cache_size=10, default_scale=1.0)

            # Initial stats
            stats = extractor.get_cache_stats()
            assert stats['hits'] == 0
            assert stats['misses'] == 0
            assert stats['size'] == 0

            # After some operations
            extractor.extract_frame(0)
            extractor.extract_frame(1)
            extractor.extract_frame(0)  # Hit

            stats = extractor.get_cache_stats()
            assert stats['hits'] == 1
            assert stats['misses'] == 2
            assert stats['size'] == 2


class TestKeyPositionDetector:
    """Tests for KeyPositionDetector class."""

    def test_detect_positions(self):
        """Test that key positions are detected."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            positions = detector.detect_positions(downsample_factor=4)

            assert isinstance(positions, dict)
            assert 'P1' in positions
            assert 'P4' in positions
            assert 'P7' in positions

            # All positions should be valid frame numbers
            meta = loader.get_metadata()
            for pos_name, frame_num in positions.items():
                assert 0 <= frame_num < meta.frame_count

    def test_detect_positions_ordering(self):
        """Test that detected positions follow expected chronological order."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            positions = detector.detect_positions(downsample_factor=4)

            # P1 (address) should be before P4 (top)
            assert positions['P1'] <= positions['P4']

            # P4 (top) should be before P7 (impact)
            assert positions['P4'] <= positions['P7']

    def test_detect_positions_different_downsample(self):
        """Test detection with different downsample factors."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            positions_4 = detector.detect_positions(downsample_factor=4)
            positions_2 = detector.detect_positions(downsample_factor=2)

            # Both should return valid positions
            assert all(k in positions_4 for k in ['P1', 'P4', 'P7'])
            assert all(k in positions_2 for k in ['P1', 'P4', 'P7'])

            # Positions should be reasonably similar (within ~20% of video length)
            meta = loader.get_metadata()
            tolerance = meta.frame_count * 0.2

            for key in ['P1', 'P4', 'P7']:
                assert abs(positions_4[key] - positions_2[key]) < tolerance

    def test_calculate_motion_magnitude(self):
        """Test motion magnitude calculation."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            # Get a few frames
            frames = [loader.get_frame_at(i) for i in range(10)]

            motion = detector._calculate_motion_magnitude(frames)

            # Should have one less motion value than frames
            assert len(motion) == len(frames) - 1

            # Motion values should be non-negative
            assert all(m >= 0 for m in motion)

            # Should have some motion (not all zeros)
            assert any(m > 0 for m in motion)

    def test_find_low_motion_region(self):
        """Test finding low motion region."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            # Create synthetic motion data with clear low region
            motion = np.array([100.0] * 20 + [10.0] * 20 + [100.0] * 20,
                              dtype=np.float32)

            low_idx = detector._find_low_motion_region(motion, window_size=10)

            # Should find the low-motion region (around index 20-40)
            assert 15 < low_idx < 45

    def test_find_peak_velocity(self):
        """Test finding peak velocity."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            # Create synthetic motion data with clear peak
            motion = np.array([10.0] * 20 + [50.0, 100.0, 150.0, 100.0, 50.0] +
                              [10.0] * 20, dtype=np.float32)

            peak_idx = detector._find_peak_velocity(motion, start_frame=0)

            # Should find the peak around index 22 (where 150.0 is)
            assert 20 < peak_idx < 25

    def test_find_direction_change(self):
        """Test finding direction change (top of backswing)."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            detector = KeyPositionDetector(loader)

            # Create synthetic motion with ramp up then down
            motion = np.array(
                [10.0] * 5 +
                [20.0, 40.0, 60.0, 80.0, 70.0, 50.0, 30.0] +  # Peak at ~9
                [10.0] * 10,
                dtype=np.float32
            )

            change_idx = detector._find_direction_change(motion, start_frame=0)

            # Should find the direction change around index 8-9
            assert 5 < change_idx < 12

    def test_handles_short_video(self):
        """Test that detector handles very short videos gracefully."""
        # Create a very short test video
        import cv2
        short_video_path = Path(__file__).parent / "test_data" / "short_test.mp4"
        short_video_path.parent.mkdir(exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(short_video_path), fourcc, 30, (640, 480))

        # Only 3 frames
        for _ in range(3):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        try:
            with VideoLoader(str(short_video_path)) as loader:
                detector = KeyPositionDetector(loader)
                positions = detector.detect_positions(downsample_factor=1)

                # Should return some positions without crashing
                assert 'P1' in positions
                assert 'P4' in positions
                assert 'P7' in positions
        finally:
            # Cleanup
            if short_video_path.exists():
                short_video_path.unlink()
