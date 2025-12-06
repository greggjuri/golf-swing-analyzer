"""Tests for video.loader module."""

import pytest
import numpy as np
from pathlib import Path

from src.video.loader import VideoLoader, VideoMetadata


# Test video path
TEST_VIDEO_PATH = Path(__file__).parent / "test_data" / "test_swing.mp4"


class TestVideoLoader:
    """Tests for VideoLoader class."""

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError):
            VideoLoader("/path/to/nonexistent/video.mp4")

    def test_unsupported_format(self, tmp_path):
        """Test that ValueError is raised for unsupported file format."""
        # Create a dummy file with unsupported extension
        dummy_file = tmp_path / "video.avi"
        dummy_file.touch()

        with pytest.raises(ValueError, match="Unsupported format"):
            VideoLoader(str(dummy_file))

    def test_valid_video_loads(self):
        """Test that a valid video file loads successfully."""
        loader = VideoLoader(str(TEST_VIDEO_PATH))
        assert loader is not None
        loader.release()

    def test_context_manager(self):
        """Test that context manager properly releases resources."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            assert loader.cap.isOpened()

        # After exiting context, video should be released
        assert not loader.cap.isOpened()

    def test_get_metadata(self):
        """Test that metadata is correctly extracted."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            meta = loader.get_metadata()

            assert isinstance(meta, VideoMetadata)
            assert meta.fps == 30.0
            assert meta.frame_count == 150
            assert meta.width == 640
            assert meta.height == 480
            assert abs(meta.duration - 5.0) < 0.1  # ~5 seconds

    def test_seek_valid_frame(self):
        """Test seeking to a valid frame number."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            # Seek to middle of video
            result = loader.seek(75)
            assert result is True

            # Read frame to verify we're in the right area
            # (OpenCV seeking may not be exact for some codecs)
            frame = loader.read_frame()
            assert frame is not None

    def test_seek_negative_frame(self):
        """Test that seeking to negative frame number returns False."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            result = loader.seek(-1)
            assert result is False

    def test_seek_beyond_length(self):
        """Test that seeking beyond video length returns False."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            meta = loader.get_metadata()
            result = loader.seek(meta.frame_count + 10)
            assert result is False

    def test_read_frame(self):
        """Test reading a frame."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            loader.seek(0)
            frame = loader.read_frame()

            assert frame is not None
            assert isinstance(frame, np.ndarray)
            assert frame.dtype == np.uint8
            assert frame.shape == (480, 640, 3)  # BGR format

    def test_read_frame_at_end(self):
        """Test that reading at end of video returns None."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            meta = loader.get_metadata()
            loader.seek(meta.frame_count - 1)
            loader.read_frame()  # Read last frame

            # Try to read beyond end
            frame = loader.read_frame()
            assert frame is None

    def test_get_frame_at(self):
        """Test getting frame at specific position without changing position."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            # Start at frame 10
            loader.seek(10)
            initial_pos = int(loader.cap.get(0))

            # Get frame 50
            frame = loader.get_frame_at(50)
            assert frame is not None

            # Verify position is restored (may not be exact with some codecs)
            current_pos = int(loader.cap.get(0))
            assert current_pos == initial_pos

    def test_get_frame_at_invalid(self):
        """Test that getting invalid frame returns None."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            frame = loader.get_frame_at(-1)
            assert frame is None

            meta = loader.get_metadata()
            frame = loader.get_frame_at(meta.frame_count + 10)
            assert frame is None

    def test_iterator(self):
        """Test iterator protocol."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            frames = []
            for frame_num, frame in loader:
                frames.append((frame_num, frame))
                # Only iterate first 10 frames for speed
                if frame_num >= 9:
                    break

            assert len(frames) == 10
            assert frames[0][0] == 0
            assert frames[9][0] == 9

            # Check frame properties
            for frame_num, frame in frames:
                assert isinstance(frame, np.ndarray)
                assert frame.shape == (480, 640, 3)

    def test_iterator_full_video(self):
        """Test iterating through full video."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            meta = loader.get_metadata()
            frame_count = 0

            for frame_num, frame in loader:
                frame_count += 1

            assert frame_count == meta.frame_count

    def test_read_sequential_frames(self):
        """Test reading frames sequentially."""
        with VideoLoader(str(TEST_VIDEO_PATH)) as loader:
            loader.seek(0)

            # Read first 5 frames
            frames = []
            for _ in range(5):
                frame = loader.read_frame()
                assert frame is not None
                frames.append(frame)

            # Verify each frame is different (has motion)
            # At least some frames should differ
            diffs = []
            for i in range(len(frames) - 1):
                diff = np.sum(np.abs(frames[i].astype(int) - frames[i+1].astype(int)))
                diffs.append(diff)

            # At least one frame pair should have noticeable difference
            assert any(d > 1000 for d in diffs)


class TestVideoMetadata:
    """Tests for VideoMetadata class."""

    def test_metadata_creation(self):
        """Test creating VideoMetadata instance."""
        meta = VideoMetadata(
            fps=30.0,
            frame_count=150,
            width=640,
            height=480,
            duration=5.0,
            codec="mp4v"
        )

        assert meta.fps == 30.0
        assert meta.frame_count == 150
        assert meta.width == 640
        assert meta.height == 480
        assert meta.duration == 5.0
        assert meta.codec == "mp4v"

    def test_metadata_repr(self):
        """Test string representation of VideoMetadata."""
        meta = VideoMetadata(
            fps=30.0,
            frame_count=150,
            width=640,
            height=480,
            duration=5.0,
            codec="mp4v"
        )

        repr_str = repr(meta)
        assert "VideoMetadata" in repr_str
        assert "fps=30.0" in repr_str
        assert "frame_count=150" in repr_str
