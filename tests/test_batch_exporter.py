"""Tests for BatchExporter."""

import os
import tempfile
import pytest
import numpy as np
import cv2

from src.export.batch_exporter import BatchExporter


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


class TestBatchExporterInit:
    """Test BatchExporter initialization."""

    def test_init_default_template(self):
        """Test initialization with default template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            assert exporter.output_dir == tmpdir
            assert exporter.filename_template == "frame_{:04d}.jpg"
            assert exporter.quality == 95
            assert os.path.isdir(tmpdir)

    def test_init_custom_template(self):
        """Test initialization with custom template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(
                tmpdir,
                filename_template="img_{:05d}.png",
                quality=90
            )
            assert exporter.filename_template == "img_{:05d}.png"
            assert exporter.quality == 90

    def test_init_creates_directory(self):
        """Test output directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "frames")
            BatchExporter(output_dir)
            assert os.path.isdir(output_dir)

    def test_init_invalid_template(self):
        """Test error on invalid filename template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Template with named placeholder instead of positional
            with pytest.raises(ValueError, match="must contain format placeholder"):
                BatchExporter(tmpdir, filename_template="frame_{name}.jpg")


class TestBatchExporterExportFrames:
    """Test batch frame export."""

    def test_export_frames(self, test_frames):
        """Test exporting list of frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_frames(test_frames)

            assert count == len(test_frames)

            # Verify all frames exported
            for i in range(len(test_frames)):
                expected_path = os.path.join(tmpdir, f"frame_{i:04d}.jpg")
                assert os.path.exists(expected_path)

    def test_export_frames_custom_start_index(self, test_frames):
        """Test export with custom start index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_frames(test_frames, start_index=100)

            assert count == len(test_frames)

            # Verify filenames start at 100
            for i in range(len(test_frames)):
                expected_path = os.path.join(tmpdir, f"frame_{100 + i:04d}.jpg")
                assert os.path.exists(expected_path)

    def test_export_empty_list(self):
        """Test error on empty frames list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            with pytest.raises(ValueError, match="Frames list is empty"):
                exporter.export_frames([])

    def test_export_with_progress_callback(self, test_frames):
        """Test export with progress callback."""
        percentages = []

        def callback(pct):
            percentages.append(pct)

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_frames(test_frames, progress_callback=callback)

            assert count == len(test_frames)
            assert len(percentages) == len(test_frames)
            assert percentages[0] == 10.0  # 1/10
            assert percentages[-1] == 100.0  # 10/10

    def test_export_partial_success(self, test_frames):
        """Test export continues on individual frame errors."""
        # Create frames with one invalid frame
        frames = test_frames[:5] + [None] + test_frames[6:]

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            # Should not raise, but count should reflect failed frame
            count = exporter.export_frames(frames)

            # All valid frames should be exported
            assert count == len(test_frames) - 1


class TestBatchExporterFilenameTemplate:
    """Test filename template handling."""

    def test_different_templates(self, test_frames):
        """Test various filename templates."""
        templates = [
            ("frame_{:04d}.jpg", "frame_0000.jpg", 95),
            ("img_{:05d}.png", "img_00000.png", 5),
            ("{:03d}_output.jpg", "000_output.jpg", 95),
        ]

        for template, expected_first, quality in templates:
            with tempfile.TemporaryDirectory() as tmpdir:
                exporter = BatchExporter(tmpdir, filename_template=template, quality=quality)
                exporter.export_frames(test_frames[:1])

                expected_path = os.path.join(tmpdir, expected_first)
                assert os.path.exists(expected_path)

    def test_template_with_leading_zeros(self, test_frames):
        """Test template produces correct leading zeros."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir, filename_template="frame_{:06d}.jpg")
            exporter.export_frames(test_frames[:1], start_index=42)

            expected_path = os.path.join(tmpdir, "frame_000042.jpg")
            assert os.path.exists(expected_path)


class TestBatchExporterGetOutputPath:
    """Test get_output_path method."""

    def test_get_output_path(self):
        """Test getting output path for frame number."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            path = exporter.get_output_path(42)

            expected = os.path.join(tmpdir, "frame_0042.jpg")
            assert path == expected

    def test_get_output_path_custom_template(self):
        """Test get_output_path with custom template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(
                tmpdir,
                filename_template="img_{:05d}.png"
            )
            path = exporter.get_output_path(100)

            expected = os.path.join(tmpdir, "img_00100.png")
            assert path == expected


class TestBatchExporterExportVideoFrames:
    """Test exporting frames from video file."""

    @pytest.fixture
    def test_video(self, test_frames):
        """Create test video file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "test_video.mp4")

            # Create test video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))

            for frame in test_frames:
                out.write(frame)

            out.release()

            yield video_path

    def test_export_all_frames(self, test_video):
        """Test exporting all frames from video."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_video_frames(test_video, step=1)

            # Should export all frames
            assert count > 0
            assert os.path.exists(os.path.join(tmpdir, "frame_0000.jpg"))

    def test_export_specific_frames(self, test_video):
        """Test exporting specific frame numbers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            frame_numbers = [0, 2, 4, 6]
            count = exporter.export_video_frames(
                test_video,
                frame_numbers=frame_numbers
            )

            assert count == len(frame_numbers)

            # Verify correct frames exported
            for frame_num in frame_numbers:
                expected_path = os.path.join(tmpdir, f"frame_{frame_num:04d}.jpg")
                assert os.path.exists(expected_path)

    def test_export_with_step(self, test_video):
        """Test exporting every Nth frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_video_frames(test_video, step=2)

            # Should export every 2nd frame
            assert count > 0

    def test_export_video_not_found(self):
        """Test error on non-existent video."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            with pytest.raises(ValueError, match="Video file not found"):
                exporter.export_video_frames("nonexistent.mp4")

    def test_export_with_visualization_engine(self, test_video):
        """Test exporting with visualization engine."""
        class MockEngine:
            def render(self, frame, **kwargs):
                # Draw something on frame
                output = frame.copy()
                cv2.line(output, (0, 0), (100, 100), (255, 255, 0), 2)
                return output

        engine = MockEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_video_frames(
                test_video,
                frame_numbers=[0, 1],
                engine=engine
            )

            assert count == 2

            # Verify files exist
            assert os.path.exists(os.path.join(tmpdir, "frame_0000.jpg"))
            assert os.path.exists(os.path.join(tmpdir, "frame_0001.jpg"))

    def test_export_video_with_progress(self, test_video):
        """Test video export with progress callback."""
        percentages = []

        def callback(pct):
            percentages.append(pct)

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_video_frames(
                test_video,
                frame_numbers=[0, 1, 2],
                progress_callback=callback
            )

            assert count == 3
            assert len(percentages) == 3
            assert percentages[-1] == 100.0


class TestBatchExporterQuality:
    """Test quality settings."""

    def test_jpeg_quality(self, test_frames):
        """Test JPEG quality affects file size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # High quality
            exporter_high = BatchExporter(tmpdir, quality=100)
            exporter_high.export_frames(test_frames[:1])
            high_size = os.path.getsize(os.path.join(tmpdir, "frame_0000.jpg"))

        with tempfile.TemporaryDirectory() as tmpdir:
            # Low quality
            exporter_low = BatchExporter(tmpdir, quality=50)
            exporter_low.export_frames(test_frames[:1])
            low_size = os.path.getsize(os.path.join(tmpdir, "frame_0000.jpg"))

        # High quality should produce larger file
        assert high_size > low_size

    def test_png_quality(self, test_frames):
        """Test PNG compression affects file size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Low compression
            exporter_low = BatchExporter(
                tmpdir,
                filename_template="frame_{:04d}.png",
                quality=0
            )
            exporter_low.export_frames(test_frames[:1])
            low_comp_size = os.path.getsize(os.path.join(tmpdir, "frame_0000.png"))

        with tempfile.TemporaryDirectory() as tmpdir:
            # High compression
            exporter_high = BatchExporter(
                tmpdir,
                filename_template="frame_{:04d}.png",
                quality=9
            )
            exporter_high.export_frames(test_frames[:1])
            high_comp_size = os.path.getsize(os.path.join(tmpdir, "frame_0000.png"))

        # Higher compression should produce smaller file
        assert high_comp_size < low_comp_size


class TestBatchExporterErrorHandling:
    """Test error handling."""

    def test_handles_individual_frame_errors(self):
        """Test batch export continues on individual errors."""
        # Create mix of valid and invalid frames
        frames = [
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.zeros((100, 100, 3), dtype=np.uint8),  # Different size
            np.zeros((480, 640, 3), dtype=np.uint8),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            count = exporter.export_frames(frames)

            # All frames should export (frame size validation happens in FrameExporter)
            assert count == len(frames)

    def test_logs_errors(self):
        """Test errors are logged."""
        # This test verifies error logging doesn't crash the export
        frames = [
            np.zeros((480, 640, 3), dtype=np.uint8),
            None,  # Will cause error
            np.zeros((480, 640, 3), dtype=np.uint8),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BatchExporter(tmpdir)
            # Should not raise exception
            count = exporter.export_frames(frames)
            # Two valid frames
            assert count == 2
