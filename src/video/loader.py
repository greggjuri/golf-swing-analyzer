"""Video file loading and access interface.

This module provides the VideoLoader class for loading video files,
extracting metadata, and providing frame-by-frame access.
"""

import logging
from pathlib import Path
from typing import Iterator, Optional, Tuple

import cv2
import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# Type aliases
Frame = NDArray[np.uint8]
FrameNumber = int

SUPPORTED_FORMATS = {'.mov', '.mp4'}


class VideoMetadata:
    """Container for video properties."""

    def __init__(
        self,
        fps: float,
        frame_count: int,
        width: int,
        height: int,
        duration: float,
        codec: str
    ):
        """Initialize video metadata.

        Args:
            fps: Frames per second
            frame_count: Total number of frames
            width: Frame width in pixels
            height: Frame height in pixels
            duration: Video duration in seconds
            codec: Video codec identifier
        """
        self.fps = fps
        self.frame_count = frame_count
        self.width = width
        self.height = height
        self.duration = duration
        self.codec = codec

    def __repr__(self) -> str:
        return (
            f"VideoMetadata(fps={self.fps}, frame_count={self.frame_count}, "
            f"width={self.width}, height={self.height}, duration={self.duration}s)"
        )


class VideoLoader:
    """Handles video file loading and provides frame access interface.

    Supports lazy loading - does not load entire video into memory.
    Validates video format and provides metadata.

    Example:
        with VideoLoader("video.mov") as loader:
            meta = loader.get_metadata()
            frame = loader.read_frame()
    """

    def __init__(self, file_path: str) -> None:
        """Initialize video loader.

        Args:
            file_path: Absolute path to video file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported
            RuntimeError: If OpenCV cannot open the video
        """
        self.file_path = Path(file_path)

        # Validation
        if not self.file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        if self.file_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {self.file_path.suffix}. "
                f"Supported formats: {SUPPORTED_FORMATS}"
            )

        # Open video
        self.cap = cv2.VideoCapture(str(self.file_path))
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video: {file_path}")

        logger.info(f"Loaded video: {file_path}")

        # Extract metadata
        self._metadata = self._extract_metadata()

    def _extract_metadata(self) -> VideoMetadata:
        """Extract video metadata from cv2.VideoCapture.

        Returns:
            VideoMetadata object with video properties
        """
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))

        # Convert fourcc code to string
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        # Calculate duration
        duration = frame_count / fps if fps > 0 else 0.0

        return VideoMetadata(
            fps=fps,
            frame_count=frame_count,
            width=width,
            height=height,
            duration=duration,
            codec=codec
        )

    def get_metadata(self) -> VideoMetadata:
        """Get video properties.

        Returns:
            VideoMetadata object with fps, frame_count, width, height, etc.
        """
        return self._metadata

    def seek(self, frame_number: FrameNumber) -> bool:
        """Move to specific frame position.

        Args:
            frame_number: 0-indexed frame number

        Returns:
            True if seek successful, False otherwise
        """
        if frame_number < 0:
            logger.warning(f"Invalid negative frame number: {frame_number}")
            return False

        if frame_number >= self._metadata.frame_count:
            logger.warning(
                f"Frame number {frame_number} exceeds video length "
                f"({self._metadata.frame_count})"
            )
            return False

        success = self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        return success

    def read_frame(self) -> Optional[Frame]:
        """Read current frame and advance position.

        Returns:
            Frame as BGR numpy array, or None if end of video
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame  # type: ignore[return-value]

    def get_frame_at(self, frame_number: FrameNumber) -> Optional[Frame]:
        """Get specific frame without changing current position.

        Args:
            frame_number: 0-indexed frame number

        Returns:
            Frame as BGR numpy array, or None if invalid frame number
        """
        # Save current position (before read, which advances position)
        current_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

        # Seek to desired frame
        if not self.seek(frame_number):
            # Restore position even if seek failed
            if current_pos < self._metadata.frame_count:
                self.seek(current_pos)
            return None

        # Read frame (this advances position to frame_number + 1)
        frame = self.read_frame()

        # Restore original position
        if current_pos < self._metadata.frame_count:
            self.seek(current_pos)

        return frame

    def __iter__(self) -> Iterator[Tuple[FrameNumber, Frame]]:
        """Iterate through all frames.

        Yields:
            Tuple of (frame_number, frame_array)
        """
        # Reset to beginning
        self.seek(0)

        frame_number = 0
        while True:
            frame = self.read_frame()
            if frame is None:
                break
            yield (frame_number, frame)
            frame_number += 1

    def release(self) -> None:
        """Release video file resources."""
        if self.cap is not None:
            self.cap.release()
            logger.info(f"Released video: {self.file_path}")

    def __enter__(self):
        """Context manager entry.

        Returns:
            self
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures release() is called.

        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.release()
