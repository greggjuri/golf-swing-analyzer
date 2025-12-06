"""Tests for FrameExporter."""

import os
import tempfile
import pytest
import numpy as np
import cv2

from src.export.frame_exporter import FrameExporter


@pytest.fixture
def test_frame():
    """Create test frame."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw some content
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), -1)
    cv2.circle(frame, (320, 240), 50, (255, 0, 0), -1)
    return frame


@pytest.fixture
def exporter():
    """Create FrameExporter instance."""
    return FrameExporter()


class TestFrameExporterInit:
    """Test FrameExporter initialization."""

    def test_init(self):
        """Test initialization."""
        exporter = FrameExporter()
        assert exporter is not None


class TestFrameExporterExportJPEG:
    """Test JPEG export."""

    def test_export_jpg(self, exporter, test_frame):
        """Test export as JPG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            success = exporter.export_frame(test_frame, output_path)
            assert success
            assert os.path.exists(output_path)

            # Verify file can be read
            loaded = cv2.imread(output_path)
            assert loaded is not None
            assert loaded.shape == test_frame.shape

    def test_export_jpeg(self, exporter, test_frame):
        """Test export with .jpeg extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpeg")
            success = exporter.export_frame(test_frame, output_path)
            assert success
            assert os.path.exists(output_path)

    def test_jpeg_quality_high(self, exporter, test_frame):
        """Test JPEG with high quality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            success = exporter.export_frame(test_frame, output_path, quality=100)
            assert success

            high_quality_size = os.path.getsize(output_path)

            # Lower quality should produce smaller file
            output_path2 = os.path.join(tmpdir, "frame2.jpg")
            exporter.export_frame(test_frame, output_path2, quality=50)
            low_quality_size = os.path.getsize(output_path2)

            assert high_quality_size > low_quality_size

    def test_jpeg_quality_invalid(self, exporter, test_frame):
        """Test error on invalid JPEG quality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")

            with pytest.raises(ValueError, match="JPEG quality must be 0-100"):
                exporter.export_frame(test_frame, output_path, quality=101)

            with pytest.raises(ValueError, match="JPEG quality must be 0-100"):
                exporter.export_frame(test_frame, output_path, quality=-1)


class TestFrameExporterExportPNG:
    """Test PNG export."""

    def test_export_png(self, exporter, test_frame):
        """Test export as PNG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.png")
            success = exporter.export_frame(test_frame, output_path, quality=5)
            assert success
            assert os.path.exists(output_path)

            # Verify file can be read
            loaded = cv2.imread(output_path)
            assert loaded is not None
            assert loaded.shape == test_frame.shape

    def test_png_compression(self, exporter, test_frame):
        """Test PNG compression levels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path1 = os.path.join(tmpdir, "frame1.png")
            exporter.export_frame(test_frame, output_path1, quality=0)
            size_low = os.path.getsize(output_path1)

            output_path2 = os.path.join(tmpdir, "frame2.png")
            exporter.export_frame(test_frame, output_path2, quality=9)
            size_high = os.path.getsize(output_path2)

            # Higher compression should produce smaller file
            assert size_high < size_low

    def test_png_quality_invalid(self, exporter, test_frame):
        """Test error on invalid PNG compression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.png")

            with pytest.raises(ValueError, match="PNG compression must be 0-9"):
                exporter.export_frame(test_frame, output_path, quality=10)

            with pytest.raises(ValueError, match="PNG compression must be 0-9"):
                exporter.export_frame(test_frame, output_path, quality=-1)


class TestFrameExporterOtherFormats:
    """Test other image formats."""

    def test_export_bmp(self, exporter, test_frame):
        """Test export as BMP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.bmp")
            success = exporter.export_frame(test_frame, output_path)
            assert success
            assert os.path.exists(output_path)

    def test_export_tiff(self, exporter, test_frame):
        """Test export as TIFF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.tiff")
            success = exporter.export_frame(test_frame, output_path)
            assert success
            assert os.path.exists(output_path)

    def test_unsupported_format(self, exporter, test_frame):
        """Test error on unsupported format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.gif")
            with pytest.raises(ValueError, match="Unsupported format"):
                exporter.export_frame(test_frame, output_path)


class TestFrameExporterValidation:
    """Test input validation."""

    def test_none_frame(self, exporter):
        """Test error on None frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            with pytest.raises(ValueError, match="Frame is empty or None"):
                exporter.export_frame(None, output_path)

    def test_empty_frame(self, exporter):
        """Test error on empty frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            empty_frame = np.array([])
            with pytest.raises(ValueError, match="Frame is empty or None"):
                exporter.export_frame(empty_frame, output_path)

    def test_invalid_dimensions(self, exporter):
        """Test error on invalid frame dimensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            # 1D array
            invalid_frame = np.zeros((100,), dtype=np.uint8)
            with pytest.raises(ValueError, match="Frame must be 2D or 3D array"):
                exporter.export_frame(invalid_frame, output_path)

    def test_grayscale_frame(self, exporter):
        """Test export of grayscale frame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            gray_frame = np.zeros((480, 640), dtype=np.uint8)
            success = exporter.export_frame(gray_frame, output_path)
            assert success
            assert os.path.exists(output_path)


class TestFrameExporterPaths:
    """Test path handling."""

    def test_creates_parent_directories(self, exporter, test_frame):
        """Test parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir1", "subdir2", "frame.jpg")
            success = exporter.export_frame(test_frame, output_path)
            assert success
            assert os.path.exists(output_path)

    def test_overwrites_existing(self, exporter, test_frame):
        """Test overwrites existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")

            # Write first time
            exporter.export_frame(test_frame, output_path, quality=50)
            size1 = os.path.getsize(output_path)

            # Overwrite with different quality
            exporter.export_frame(test_frame, output_path, quality=100)
            size2 = os.path.getsize(output_path)

            # File should exist and have different size
            assert os.path.exists(output_path)
            assert size2 != size1


class TestFrameExporterWithVisualization:
    """Test export with visualization."""

    def test_export_with_visualization(self, exporter, test_frame):
        """Test export frame with visualization overlays."""
        # Create mock engine
        class MockEngine:
            def render(self, frame, **kwargs):
                # Draw something on frame
                output = frame.copy()
                cv2.line(output, (0, 0), (100, 100), (255, 255, 0), 2)
                return output

        engine = MockEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "frame.jpg")
            success = exporter.export_frame_with_visualization(
                test_frame,
                output_path,
                engine
            )
            assert success
            assert os.path.exists(output_path)

            # Verify visualization was applied
            loaded = cv2.imread(output_path)
            assert not np.array_equal(loaded, test_frame)
