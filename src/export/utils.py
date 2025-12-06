"""Utility functions for export operations."""

import os
import logging
from typing import Tuple, Optional

import cv2

logger = logging.getLogger(__name__)


# Codec name to fourcc mapping
CODEC_MAP = {
    'H264': 'H264',
    'H.264': 'H264',
    'AVC': 'H264',
    'MJPEG': 'MJPG',
    'MJPG': 'MJPG',
    'XVID': 'XVID',
    'MP4V': 'MP4V',
    'MPEG4': 'MP4V',
    'X264': 'X264',
}


def get_codec_fourcc(codec_name: str) -> int:
    """Get OpenCV fourcc code for codec name.

    Args:
        codec_name: Codec name ('H264', 'MJPEG', 'XVID', etc.)

    Returns:
        Fourcc code for cv2.VideoWriter

    Raises:
        ValueError: If codec not supported
    """
    codec_upper = codec_name.upper()

    if codec_upper not in CODEC_MAP:
        raise ValueError(
            f"Unsupported codec: {codec_name}. "
            f"Supported codecs: {', '.join(CODEC_MAP.keys())}"
        )

    fourcc_str = CODEC_MAP[codec_upper]
    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)

    logger.debug(f"Codec {codec_name} -> fourcc {fourcc_str}")

    return fourcc


def validate_output_path(path: str, create_dirs: bool = True) -> str:
    """Validate and prepare output path.

    Args:
        path: Output file path
        create_dirs: Whether to create parent directories

    Returns:
        Validated absolute path

    Raises:
        ValueError: If path is invalid
        OSError: If directory creation fails
    """
    if not path:
        raise ValueError("Output path cannot be empty")

    # Convert to absolute path
    abs_path = os.path.abspath(path)

    # Get parent directory
    parent_dir = os.path.dirname(abs_path)

    if create_dirs and parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
        logger.debug(f"Created directory: {parent_dir}")

    # Check if parent directory exists
    if parent_dir and not os.path.isdir(parent_dir):
        raise ValueError(f"Parent directory does not exist: {parent_dir}")

    # Check if path already exists as directory
    if os.path.isdir(abs_path):
        raise ValueError(f"Path is a directory: {abs_path}")

    return abs_path


def estimate_video_size(
    frame_count: int,
    resolution: Tuple[int, int],
    fps: float,
    codec: str,
    bitrate: Optional[int] = None
) -> int:
    """Estimate output video file size in bytes.

    Args:
        frame_count: Number of frames
        resolution: Video resolution (width, height)
        fps: Frames per second
        codec: Video codec
        bitrate: Target bitrate in bps (if specified)

    Returns:
        Estimated file size in bytes
    """
    width, height = resolution
    duration_seconds = frame_count / fps

    # If bitrate specified, use it directly
    if bitrate is not None:
        size_bytes = (bitrate / 8) * duration_seconds
        return int(size_bytes)

    # Estimate bitrate based on resolution and codec
    pixels = width * height

    # Rough bitrate estimates (bits per pixel per second)
    if codec.upper() in ['MJPEG', 'MJPG']:
        # MJPEG is less efficient
        bpp = 0.5
    elif codec.upper() in ['H264', 'H.264', 'AVC', 'X264']:
        # H.264 is more efficient
        bpp = 0.1
    else:
        # Default conservative estimate
        bpp = 0.3

    estimated_bitrate = pixels * fps * bpp
    size_bytes = (estimated_bitrate / 8) * duration_seconds

    return int(size_bytes)


def get_image_format(path: str) -> str:
    """Get image format from file extension.

    Args:
        path: File path

    Returns:
        Image format ('jpg', 'png', 'bmp', etc.)

    Raises:
        ValueError: If format cannot be determined
    """
    _, ext = os.path.splitext(path)

    if not ext:
        raise ValueError(f"Cannot determine image format from path: {path}")

    # Remove leading dot and convert to lowercase
    format_str = ext[1:].lower()

    # Normalize JPEG extensions
    if format_str in ['jpeg', 'jpe']:
        format_str = 'jpg'

    return format_str
