"""Frame extraction and key position detection.

This module provides FrameExtractor for efficient frame caching and scaling,
and KeyPositionDetector for automatic detection of key swing positions.
"""

import logging
from typing import Dict, Optional

import cv2
import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import gaussian_filter1d

from .loader import VideoLoader, Frame, FrameNumber

logger = logging.getLogger(__name__)

# Type aliases
ScaleFactor = float
KeyPositions = Dict[str, FrameNumber]


class FrameExtractor:
    """Extract and process frames with caching and downsampling.

    Provides efficient frame access with LRU cache and optional scaling.

    Example:
        extractor = FrameExtractor(loader, cache_size=100, default_scale=0.5)
        frame = extractor.extract_frame(10)  # Half resolution
        frames = extractor.extract_range(0, 30, step=2)
    """

    def __init__(
        self,
        video_loader: VideoLoader,
        cache_size: int = 50,
        default_scale: ScaleFactor = 1.0
    ) -> None:
        """Initialize frame extractor.

        Args:
            video_loader: VideoLoader instance
            cache_size: Maximum frames to cache (LRU eviction)
            default_scale: Default scaling factor for extracted frames
        """
        self.video_loader = video_loader
        self.default_scale = default_scale
        self.cache_size = cache_size

        # LRU cache implementation
        self._cache: Dict[tuple, Frame] = {}
        self._cache_order: list = []

        # Cache statistics
        self.hits = 0
        self.misses = 0

    def extract_frame(
        self,
        frame_number: FrameNumber,
        scale: Optional[ScaleFactor] = None
    ) -> Frame:
        """Extract single frame with optional scaling.

        Args:
            frame_number: 0-indexed frame number
            scale: Scale factor (overrides default_scale if provided)

        Returns:
            Processed frame as BGR numpy array

        Raises:
            ValueError: If frame_number is out of range or scale is invalid
        """
        # Use default scale if None, but allow explicit 0 for validation
        if scale is None:
            scale = self.default_scale

        # Validate scale
        if scale <= 0:
            raise ValueError(f"Invalid scale factor: {scale}. Must be > 0")

        cache_key = (frame_number, scale)

        # Check cache
        if cache_key in self._cache:
            self.hits += 1
            # Move to end of order list (most recently used)
            self._cache_order.remove(cache_key)
            self._cache_order.append(cache_key)
            return self._cache[cache_key].copy()

        # Cache miss - extract frame
        self.misses += 1
        frame = self.video_loader.get_frame_at(frame_number)

        if frame is None:
            raise ValueError(f"Invalid frame number: {frame_number}")

        # Apply scaling
        if scale != 1.0:
            new_width = int(frame.shape[1] * scale)
            new_height = int(frame.shape[0] * scale)
            frame = cv2.resize(frame, (new_width, new_height))  # type: ignore[assignment]

        # Add to cache (with LRU eviction)
        self._add_to_cache(cache_key, frame)

        return frame.copy()

    def _add_to_cache(self, cache_key: tuple, frame: Frame) -> None:
        """Add frame to cache with LRU eviction.

        Args:
            cache_key: Tuple of (frame_number, scale)
            frame: Frame array to cache
        """
        # Evict oldest if cache is full
        if len(self._cache) >= self.cache_size:
            oldest_key = self._cache_order.pop(0)
            del self._cache[oldest_key]

        # Add new frame
        self._cache[cache_key] = frame.copy()
        self._cache_order.append(cache_key)

    def extract_range(
        self,
        start_frame: FrameNumber,
        end_frame: FrameNumber,
        step: int = 1,
        scale: Optional[ScaleFactor] = None
    ) -> list[Frame]:
        """Extract range of frames.

        Args:
            start_frame: Starting frame number (inclusive)
            end_frame: Ending frame number (exclusive)
            step: Frame skip interval (1 = every frame)
            scale: Scale factor for all frames

        Returns:
            List of frame arrays

        Raises:
            ValueError: If range is invalid
        """
        if start_frame < 0:
            raise ValueError(f"Invalid start_frame: {start_frame}")

        if end_frame <= start_frame:
            raise ValueError(
                f"Invalid range: end_frame ({end_frame}) must be > "
                f"start_frame ({start_frame})"
            )

        if step < 1:
            raise ValueError(f"Invalid step: {step}. Must be >= 1")

        frames = []
        for frame_num in range(start_frame, end_frame, step):
            frame = self.extract_frame(frame_num, scale)
            frames.append(frame)

        return frames

    def clear_cache(self) -> None:
        """Clear the frame cache."""
        self._cache.clear()
        self._cache_order.clear()
        logger.info("Frame cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics.

        Returns:
            Dict with keys: 'hits', 'misses', 'size'
        """
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': len(self._cache)
        }


class KeyPositionDetector:
    """Detect key swing positions (P1-P8) using motion analysis.

    Uses frame differencing and optical flow magnitude to identify
    characteristic points in the golf swing.

    Example:
        detector = KeyPositionDetector(loader)
        positions = detector.detect_positions()
        # Returns: {"P1": 0, "P4": 45, "P7": 78}
    """

    def __init__(self, video_loader: VideoLoader) -> None:
        """Initialize key position detector.

        Args:
            video_loader: VideoLoader instance
        """
        self.video_loader = video_loader

    def detect_positions(
        self,
        downsample_factor: int = 4
    ) -> KeyPositions:
        """Analyze video to find key swing positions.

        Detects:
        - P1 (Address): Low motion period before swing starts
        - P4 (Top of backswing): Motion direction change
        - P7 (Impact): Highest velocity point

        Args:
            downsample_factor: Process every Nth frame for speed

        Returns:
            Dictionary mapping position names to frame numbers

        Note:
            Other positions (P2, P3, P5, P6, P8) can be interpolated
            or manually adjusted by user in GUI later.
        """
        logger.info(
            f"Detecting key positions with downsample factor {downsample_factor}"
        )

        # Extract frames at reduced rate
        metadata = self.video_loader.get_metadata()
        frame_indices = list(range(0, metadata.frame_count, downsample_factor))

        frames = []
        for idx in frame_indices:
            frame = self.video_loader.get_frame_at(idx)
            if frame is not None:
                frames.append(frame)

        if len(frames) < 3:
            logger.warning("Too few frames for key position detection")
            return {"P1": 0, "P4": 0, "P7": 0}

        # Calculate motion magnitude
        motion = self._calculate_motion_magnitude(frames)

        # Smooth motion signal for better detection
        smoothed_motion = gaussian_filter1d(motion, sigma=2)

        # Detect key positions
        p1_idx = self._find_low_motion_region(smoothed_motion)
        p4_idx = self._find_direction_change(smoothed_motion, start_frame=p1_idx)
        p7_idx = self._find_peak_velocity(smoothed_motion, start_frame=p4_idx)

        # Map back to original frame numbers
        positions = {
            "P1": frame_indices[min(p1_idx, len(frame_indices) - 1)],
            "P4": frame_indices[min(p4_idx, len(frame_indices) - 1)],
            "P7": frame_indices[min(p7_idx, len(frame_indices) - 1)]
        }

        logger.info(f"Detected positions: {positions}")
        return positions

    def _calculate_motion_magnitude(
        self,
        frames: list[Frame]
    ) -> NDArray[np.float32]:
        """Calculate motion magnitude between consecutive frames.

        Args:
            frames: List of frame arrays

        Returns:
            Array of motion magnitudes (one per frame transition)
        """
        motion = []

        for i in range(len(frames) - 1):
            # Convert to grayscale
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)

            # Calculate absolute difference
            diff = cv2.absdiff(gray1, gray2)

            # Sum of all pixel differences as motion magnitude
            motion_value = float(np.sum(diff))
            motion.append(motion_value)

        return np.array(motion, dtype=np.float32)

    def _find_low_motion_region(
        self,
        motion: NDArray[np.float32],
        window_size: int = 10
    ) -> FrameNumber:
        """Find address position (sustained low motion).

        Args:
            motion: Array of motion magnitudes
            window_size: Frames to average for stability

        Returns:
            Frame number of detected address position
        """
        if len(motion) < window_size:
            return 0

        # Calculate rolling average
        min_avg = float('inf')
        min_idx = 0

        for i in range(len(motion) - window_size + 1):
            window_avg = float(np.mean(motion[i:i + window_size]))
            if window_avg < min_avg:
                min_avg = window_avg
                min_idx = i

        # Return middle of the low-motion window
        return min_idx + window_size // 2

    def _find_direction_change(
        self,
        motion: NDArray[np.float32],
        start_frame: FrameNumber
    ) -> FrameNumber:
        """Find top of backswing (motion direction change).

        Args:
            motion: Array of motion magnitudes
            start_frame: Frame to start searching from (after address)

        Returns:
            Frame number of detected top position
        """
        # Look for first local maximum after start frame
        search_start = min(start_frame, len(motion) - 2)

        for i in range(search_start + 1, len(motion) - 1):
            # Check if this is a local maximum
            if motion[i] > motion[i - 1] and motion[i] > motion[i + 1]:
                # Additional check: should have decent magnitude
                if motion[i] > np.mean(motion):
                    return i

        # Fallback: find global maximum in first 60% of motion
        search_end = int(len(motion) * 0.6)
        if search_end > search_start:
            return search_start + int(np.argmax(motion[search_start:search_end]))

        return min(start_frame + 10, len(motion) - 1)

    def _find_peak_velocity(
        self,
        motion: NDArray[np.float32],
        start_frame: FrameNumber
    ) -> FrameNumber:
        """Find impact position (peak velocity).

        Args:
            motion: Array of motion magnitudes
            start_frame: Frame to start searching from (after top)

        Returns:
            Frame number of detected impact position
        """
        # Search in region after top of backswing
        search_start = min(start_frame, len(motion) - 1)

        if search_start >= len(motion) - 1:
            return len(motion) - 1

        # Find global maximum in remaining portion
        remaining_motion = motion[search_start:]
        peak_idx = int(np.argmax(remaining_motion))

        return search_start + peak_idx
