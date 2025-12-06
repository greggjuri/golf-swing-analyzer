"""Tests for export utility functions."""

import os
import tempfile
import pytest

from src.export.utils import (
    get_codec_fourcc,
    validate_output_path,
    estimate_video_size,
    get_image_format
)


class TestGetCodecFourcc:
    """Test codec fourcc conversion."""

    def test_h264_codec(self):
        """Test H264 codec conversion."""
        fourcc = get_codec_fourcc('H264')
        assert isinstance(fourcc, int)

    def test_mjpeg_codec(self):
        """Test MJPEG codec conversion."""
        fourcc = get_codec_fourcc('MJPEG')
        assert isinstance(fourcc, int)

    def test_xvid_codec(self):
        """Test XVID codec conversion."""
        fourcc = get_codec_fourcc('XVID')
        assert isinstance(fourcc, int)

    def test_case_insensitive(self):
        """Test codec names are case insensitive."""
        upper = get_codec_fourcc('H264')
        lower = get_codec_fourcc('h264')
        mixed = get_codec_fourcc('H264')
        assert upper == lower == mixed

    def test_codec_aliases(self):
        """Test codec aliases map correctly."""
        h264 = get_codec_fourcc('H264')
        avc = get_codec_fourcc('AVC')
        h264_dot = get_codec_fourcc('H.264')
        assert h264 == avc == h264_dot

    def test_unsupported_codec(self):
        """Test error on unsupported codec."""
        with pytest.raises(ValueError, match="Unsupported codec"):
            get_codec_fourcc('INVALID')


class TestValidateOutputPath:
    """Test output path validation."""

    def test_valid_path(self):
        """Test valid output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "output.mp4")
            result = validate_output_path(path)
            assert os.path.isabs(result)
            assert result.endswith("output.mp4")

    def test_creates_parent_directories(self):
        """Test parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "subdir1", "subdir2", "output.mp4")
            result = validate_output_path(path, create_dirs=True)
            assert os.path.isdir(os.path.dirname(result))

    def test_no_create_dirs_missing_parent(self):
        """Test error when parent missing and create_dirs=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "missing", "output.mp4")
            with pytest.raises(ValueError, match="Parent directory does not exist"):
                validate_output_path(path, create_dirs=False)

    def test_empty_path(self):
        """Test error on empty path."""
        with pytest.raises(ValueError, match="Output path cannot be empty"):
            validate_output_path("")

    def test_path_is_directory(self):
        """Test error when path is existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Path is a directory"):
                validate_output_path(tmpdir)

    def test_relative_to_absolute(self):
        """Test relative path converted to absolute."""
        result = validate_output_path("output.mp4", create_dirs=False)
        assert os.path.isabs(result)


class TestEstimateVideoSize:
    """Test video size estimation."""

    def test_with_bitrate(self):
        """Test size estimation with specified bitrate."""
        size = estimate_video_size(
            frame_count=300,
            resolution=(1920, 1080),
            fps=30.0,
            codec='H264',
            bitrate=5_000_000  # 5 Mbps
        )
        # 300 frames / 30 fps = 10 seconds
        # 5 Mbps * 10s = 50 Mb = 6.25 MB
        expected = int((5_000_000 / 8) * 10)
        assert size == expected

    def test_h264_estimation(self):
        """Test H264 codec size estimation."""
        size = estimate_video_size(
            frame_count=300,
            resolution=(1920, 1080),
            fps=30.0,
            codec='H264'
        )
        # H264 uses 0.1 bpp
        # 1920 * 1080 * 30 * 0.1 = 6,220,800 bps
        # 10 seconds = 62,208,000 bits = 7,776,000 bytes
        assert size > 0
        assert isinstance(size, int)

    def test_mjpeg_estimation(self):
        """Test MJPEG codec size estimation."""
        h264_size = estimate_video_size(
            frame_count=300,
            resolution=(1920, 1080),
            fps=30.0,
            codec='H264'
        )
        mjpeg_size = estimate_video_size(
            frame_count=300,
            resolution=(1920, 1080),
            fps=30.0,
            codec='MJPEG'
        )
        # MJPEG should be larger than H264
        assert mjpeg_size > h264_size

    def test_resolution_scaling(self):
        """Test size scales with resolution."""
        small = estimate_video_size(
            frame_count=100,
            resolution=(640, 480),
            fps=30.0,
            codec='H264'
        )
        large = estimate_video_size(
            frame_count=100,
            resolution=(1920, 1080),
            fps=30.0,
            codec='H264'
        )
        assert large > small


class TestGetImageFormat:
    """Test image format detection."""

    def test_jpg_format(self):
        """Test JPG format detection."""
        assert get_image_format("output.jpg") == "jpg"

    def test_jpeg_format(self):
        """Test JPEG normalized to jpg."""
        assert get_image_format("output.jpeg") == "jpg"

    def test_png_format(self):
        """Test PNG format detection."""
        assert get_image_format("output.png") == "png"

    def test_bmp_format(self):
        """Test BMP format detection."""
        assert get_image_format("output.bmp") == "bmp"

    def test_tiff_format(self):
        """Test TIFF format detection."""
        assert get_image_format("output.tiff") == "tiff"

    def test_case_insensitive(self):
        """Test format detection is case insensitive."""
        assert get_image_format("output.JPG") == "jpg"
        assert get_image_format("output.PNG") == "png"

    def test_path_with_directories(self):
        """Test format detection with directory path."""
        assert get_image_format("/path/to/output.jpg") == "jpg"

    def test_no_extension(self):
        """Test error when no extension."""
        with pytest.raises(ValueError, match="Cannot determine image format"):
            get_image_format("output")

    def test_multiple_dots(self):
        """Test format detection with multiple dots in filename."""
        assert get_image_format("my.file.name.png") == "png"
