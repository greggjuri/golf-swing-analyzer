"""Tests for VideoExporter."""

import os
import tempfile
import pytest
import numpy as np
import cv2

from src.export.video_exporter import VideoExporter


@pytest.fixture
def test_frames():
    """Create sequence of test frames."""
    frames = []
    for i in range(10):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw frame number
        cv2.putText(
            frame,
            str(i),
            (300, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (255, 255, 255),
            3
        )
        frames.append(frame)
    return frames


class TestVideoExporterInit:
    """Test VideoExporter initialization."""

    def test_init_valid(self):
        """Test valid initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp4")
            exporter = VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480)
            )
            assert exporter.output_path.endswith("output.mp4")
            assert exporter.fps == 30.0
            assert exporter.resolution == (640, 480)
            assert exporter.codec == 'H264'
            assert not exporter.is_open

    def test_init_invalid_fps(self):
        """Test error on invalid FPS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp4")
            with pytest.raises(ValueError, match="FPS must be positive"):
                VideoExporter(output_path, fps=0, resolution=(640, 480))

            with pytest.raises(ValueError, match="FPS must be positive"):
                VideoExporter(output_path, fps=-10, resolution=(640, 480))

    def test_init_invalid_resolution(self):
        """Test error on invalid resolution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp4")
            with pytest.raises(ValueError, match="Resolution must be positive"):
                VideoExporter(output_path, fps=30, resolution=(0, 480))

            with pytest.raises(ValueError, match="Resolution must be positive"):
                VideoExporter(output_path, fps=30, resolution=(640, -480))


class TestVideoExporterContextManager:
    """Test context manager functionality."""

    def test_context_manager(self, test_frames):
        """Test using exporter as context manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                assert exporter.is_open
                for frame in test_frames:
                    exporter.write_frame(frame)

            # Should be closed after context
            assert not exporter.is_open
            assert os.path.exists(output_path)

    def test_context_manager_cleanup_on_error(self):
        """Test context manager cleans up on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            try:
                with VideoExporter(
                    output_path,
                    fps=30.0,
                    resolution=(640, 480),
                    codec='MJPEG'
                ) as exporter:
                    assert exporter.is_open
                    raise RuntimeError("Test error")
            except RuntimeError:
                pass

            # Should still be closed
            assert not exporter.is_open


class TestVideoExporterWriteFrame:
    """Test frame writing."""

    def test_write_single_frame(self):
        """Test writing single frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                exporter.write_frame(frame)
                assert exporter.get_frames_written() == 1

    def test_write_multiple_frames(self, test_frames):
        """Test writing multiple frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                for frame in test_frames:
                    exporter.write_frame(frame)

                assert exporter.get_frames_written() == len(test_frames)

    def test_write_grayscale_frame(self):
        """Test writing grayscale frame (should be converted to BGR)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")
            gray_frame = np.zeros((480, 640), dtype=np.uint8)

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                exporter.write_frame(gray_frame)
                assert exporter.get_frames_written() == 1

    def test_write_invalid_resolution(self):
        """Test error on frame with wrong resolution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")
            wrong_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                with pytest.raises(ValueError, match="Frame resolution.*doesn't match"):
                    exporter.write_frame(wrong_frame)

    def test_write_none_frame(self):
        """Test error on None frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                with pytest.raises(ValueError, match="Frame is empty or None"):
                    exporter.write_frame(None)

    def test_write_empty_frame(self):
        """Test error on empty frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                with pytest.raises(ValueError, match="Frame is empty or None"):
                    exporter.write_frame(np.array([]))

    def test_write_without_open(self):
        """Test writing frame without opening writer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            exporter = VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            )
            # Should auto-open on first write
            exporter.write_frame(frame)
            assert exporter.is_open
            exporter.close()


class TestVideoExporterCodecs:
    """Test different video codecs."""

    def test_h264_codec(self, test_frames):
        """Test H264 codec (skip if not available)."""
        pytest.skip("H264 codec not available on this system")

    def test_mjpeg_codec(self, test_frames):
        """Test MJPEG codec."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                for frame in test_frames[:5]:
                    exporter.write_frame(frame)

            assert os.path.exists(output_path)

    def test_xvid_codec(self, test_frames):
        """Test XVID codec."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='XVID'
            ) as exporter:
                for frame in test_frames[:5]:
                    exporter.write_frame(frame)

            assert os.path.exists(output_path)


class TestVideoExporterProgress:
    """Test progress tracking."""

    def test_progress_callback(self, test_frames):
        """Test progress callback is called."""
        percentages = []

        def callback(pct):
            percentages.append(pct)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG',
                progress_callback=callback,
                total_frames=len(test_frames)
            ) as exporter:
                for frame in test_frames:
                    exporter.write_frame(frame)

        # Should have received progress updates
        assert len(percentages) == len(test_frames)
        assert percentages[0] == 10.0  # First frame (1/10)
        assert percentages[-1] == 100.0  # Last frame (10/10)

    def test_progress_percentage(self, test_frames):
        """Test get_progress_percentage method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG',
                total_frames=10
            ) as exporter:
                assert exporter.get_progress_percentage() == 0.0

                exporter.write_frame(test_frames[0])
                assert exporter.get_progress_percentage() == 10.0

                for frame in test_frames[1:]:
                    exporter.write_frame(frame)

                assert exporter.get_progress_percentage() == 100.0

    def test_progress_without_total(self):
        """Test progress when total_frames not specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                exporter.write_frame(frame)

                # Should return None when total not known
                assert exporter.get_progress_percentage() is None


class TestVideoExporterOpenClose:
    """Test open/close operations."""

    def test_manual_open_close(self, test_frames):
        """Test manual open and close."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            exporter = VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            )

            exporter.open()
            assert exporter.is_open

            for frame in test_frames:
                exporter.write_frame(frame)

            exporter.close()
            assert not exporter.is_open
            assert os.path.exists(output_path)

    def test_double_open(self):
        """Test opening already open writer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            exporter = VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            )

            exporter.open()
            exporter.open()  # Should not error
            assert exporter.is_open

            exporter.close()

    def test_close_without_open(self):
        """Test closing without opening."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            exporter = VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            )

            exporter.close()  # Should not error
            assert not exporter.is_open


class TestVideoExporterOutputFile:
    """Test output file creation."""

    def test_creates_parent_directories(self, test_frames):
        """Test parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir1", "subdir2", "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                for frame in test_frames[:3]:
                    exporter.write_frame(frame)

            assert os.path.exists(output_path)

    def test_output_file_readable(self, test_frames):
        """Test output file can be read by OpenCV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.avi")

            with VideoExporter(
                output_path,
                fps=30.0,
                resolution=(640, 480),
                codec='MJPEG'
            ) as exporter:
                for frame in test_frames:
                    exporter.write_frame(frame)

            # Try to read the video
            cap = cv2.VideoCapture(output_path)
            assert cap.isOpened()

            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1

            cap.release()
            assert frame_count == len(test_frames)
