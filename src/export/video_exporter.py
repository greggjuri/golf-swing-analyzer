"""Video export with rendered overlays."""

import logging
from typing import Tuple, Optional, Callable

import cv2
import numpy as np

from .utils import validate_output_path, get_codec_fourcc
from .progress import ProgressTracker

logger = logging.getLogger(__name__)


class VideoExporter:
    """Export videos with rendered overlays.

    Uses OpenCV VideoWriter to create video files with analysis overlays.
    Supports context manager for automatic resource cleanup.

    Example:
        with VideoExporter(
            "output.mp4",
            fps=30.0,
            resolution=(1920, 1080),
            codec='H264'
        ) as exporter:
            for frame in frames:
                exporter.write_frame(frame)
    """

    def __init__(
        self,
        output_path: str,
        fps: float,
        resolution: Tuple[int, int],
        codec: str = 'H264',
        bitrate: Optional[int] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
        total_frames: Optional[int] = None
    ):
        """Initialize video exporter.

        Args:
            output_path: Output video file path
            fps: Frames per second
            resolution: Video resolution (width, height)
            codec: Video codec ('H264', 'MJPEG', 'XVID', etc.)
            bitrate: Optional target bitrate (not directly supported by OpenCV)
            progress_callback: Optional callback for progress updates (percentage)
            total_frames: Total frames for progress tracking (if known)

        Raises:
            ValueError: If parameters are invalid
        """
        if fps <= 0:
            raise ValueError(f"FPS must be positive, got {fps}")

        width, height = resolution
        if width <= 0 or height <= 0:
            raise ValueError(f"Resolution must be positive, got {resolution}")

        self.output_path = validate_output_path(output_path, create_dirs=True)
        self.fps = fps
        self.resolution = resolution
        self.codec = codec
        self.bitrate = bitrate
        self.progress_callback = progress_callback

        # Progress tracking
        self.frames_written = 0
        self.total_frames = total_frames
        if total_frames is not None:
            self.progress_tracker = ProgressTracker(total_frames)
        else:
            self.progress_tracker = None

        # VideoWriter (created on first write or in __enter__)
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_open = False

        logger.info(
            f"Initialized VideoExporter: {output_path}, "
            f"{resolution[0]}x{resolution[1]}@{fps}fps, codec={codec}"
        )

    def open(self):
        """Open video writer for writing.

        Raises:
            RuntimeError: If writer cannot be opened
        """
        if self.is_open:
            logger.warning("VideoWriter already open")
            return

        # Get codec fourcc
        fourcc = get_codec_fourcc(self.codec)

        # Create VideoWriter
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            self.resolution
        )

        if not self.writer.isOpened():
            raise RuntimeError(
                f"Failed to open VideoWriter for {self.output_path}. "
                f"Codec {self.codec} may not be supported."
            )

        self.is_open = True
        logger.info(f"Opened VideoWriter: {self.output_path}")

    def write_frame(self, frame: np.ndarray):
        """Write single frame to video.

        Args:
            frame: Frame to write (BGR format)

        Raises:
            ValueError: If frame resolution doesn't match or frame is invalid
            RuntimeError: If writer is not open
        """
        # Validate frame
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")

        if len(frame.shape) not in [2, 3]:
            raise ValueError(
                f"Frame must be 2D or 3D array, got shape {frame.shape}"
            )

        # Check resolution
        frame_height, frame_width = frame.shape[:2]
        expected_width, expected_height = self.resolution

        if frame_width != expected_width or frame_height != expected_height:
            raise ValueError(
                f"Frame resolution ({frame_width}x{frame_height}) "
                f"doesn't match expected ({expected_width}x{expected_height})"
            )

        # Open writer if not already open
        if not self.is_open:
            self.open()

        if self.writer is None:
            raise RuntimeError("VideoWriter is not initialized")

        # Convert grayscale to BGR if needed
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # Write frame
        self.writer.write(frame)
        self.frames_written += 1

        # Update progress
        if self.progress_tracker is not None:
            self.progress_tracker.update(
                self.frames_written,
                callback=self.progress_callback
            )

    def close(self):
        """Close video writer and finalize video file."""
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            self.is_open = False
            logger.info(
                f"Closed VideoWriter: {self.output_path} "
                f"({self.frames_written} frames written)"
            )

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, ensures video is finalized."""
        self.close()
        return False  # Don't suppress exceptions

    def get_frames_written(self) -> int:
        """Get number of frames written so far.

        Returns:
            Number of frames written
        """
        return self.frames_written

    def get_progress_percentage(self) -> Optional[float]:
        """Get current progress percentage.

        Returns:
            Progress percentage (0-100) or None if total frames unknown
        """
        if self.progress_tracker is None:
            return None

        return self.progress_tracker.get_percentage()
