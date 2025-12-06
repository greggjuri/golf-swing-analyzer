"""Multi-frame club tracking with temporal smoothing.

This module provides tracking functionality to smooth club detection results
across multiple frames and handle temporary occlusions.
"""

import logging
from collections import deque
from typing import Deque, Optional

import numpy as np

from .club_detector import DetectionResult, Line, ClubHead

logger = logging.getLogger(__name__)


class ClubTracker:
    """Track club across multiple frames using temporal consistency.

    Maintains a history of recent detections and applies smoothing to
    reduce jitter and fill gaps during temporary occlusions.

    Example:
        tracker = ClubTracker(smoothing_window=5)

        for frame in frames:
            result = detector.detect(frame)
            smoothed = tracker.update(result)
            print(f"Smoothed angle: {smoothed.shaft_angle:.1f}°")
    """

    def __init__(self, smoothing_window: int = 3, max_gap_frames: int = 5):
        """Initialize tracker.

        Args:
            smoothing_window: Number of frames to average for smoothing
            max_gap_frames: Maximum frames to interpolate during occlusion

        Raises:
            ValueError: If parameters are invalid
        """
        if smoothing_window < 1:
            raise ValueError(
                f"smoothing_window must be at least 1, got {smoothing_window}"
            )

        if max_gap_frames < 0:
            raise ValueError(
                f"max_gap_frames must be non-negative, got {max_gap_frames}"
            )

        self.smoothing_window = smoothing_window
        self.max_gap_frames = max_gap_frames

        # History queues
        self.shaft_history: Deque[Optional[Line]] = deque(maxlen=smoothing_window)
        self.angle_history: Deque[Optional[float]] = deque(maxlen=smoothing_window)
        self.head_history: Deque[Optional[ClubHead]] = deque(maxlen=smoothing_window)

        # Gap tracking
        self.frames_since_detection = 0

        logger.info(
            f"Initialized ClubTracker: window={smoothing_window}, "
            f"max_gap={max_gap_frames}"
        )

    def update(self, detection: DetectionResult) -> DetectionResult:
        """Update tracker with new detection and return smoothed result.

        Args:
            detection: Current frame detection result

        Returns:
            Smoothed detection result
        """
        # Add to history
        self.shaft_history.append(detection.shaft_line)
        self.angle_history.append(detection.shaft_angle)

        # Only create ClubHead if detected (to satisfy type checker)
        if detection.club_head_detected and detection.club_head_center is not None:
            club_head = ClubHead(
                center=detection.club_head_center,
                radius=detection.club_head_radius if detection.club_head_radius else 0.0,
                confidence=detection.confidence
            )
            self.head_history.append(club_head)
        else:
            self.head_history.append(None)

        # Track gap
        if detection.shaft_detected:
            self.frames_since_detection = 0
        else:
            self.frames_since_detection += 1

        # Apply smoothing
        if detection.shaft_detected:
            # Smooth current detection
            smoothed = self._smooth_detection(detection)
        elif self.frames_since_detection <= self.max_gap_frames:
            # Interpolate during short gap
            smoothed = self._interpolate_detection(detection)
        else:
            # Gap too long, return original (no detection)
            smoothed = detection

        return smoothed

    def _smooth_detection(self, detection: DetectionResult) -> DetectionResult:
        """Apply temporal smoothing to detection.

        Args:
            detection: Current detection

        Returns:
            Smoothed detection
        """
        # Smooth shaft line by averaging endpoints
        smoothed_line = self._smooth_shaft_line()

        # Smooth angle
        smoothed_angle = self._smooth_angle()

        # Smooth club head
        smoothed_head = self._smooth_club_head()

        return DetectionResult(
            shaft_detected=True,
            shaft_line=smoothed_line,
            shaft_angle=smoothed_angle,
            club_head_detected=smoothed_head is not None,
            club_head_center=smoothed_head.center if smoothed_head else None,
            club_head_radius=smoothed_head.radius if smoothed_head else None,
            confidence=detection.confidence,
            debug_image=detection.debug_image
        )

    def _smooth_shaft_line(self) -> Optional[Line]:
        """Average shaft line endpoints across history.

        Returns:
            Smoothed shaft line or None
        """
        valid_lines = [line for line in self.shaft_history if line is not None]

        if not valid_lines:
            return None

        # Average endpoints
        x1_avg = int(np.mean([line[0] for line in valid_lines]))
        y1_avg = int(np.mean([line[1] for line in valid_lines]))
        x2_avg = int(np.mean([line[2] for line in valid_lines]))
        y2_avg = int(np.mean([line[3] for line in valid_lines]))

        return (x1_avg, y1_avg, x2_avg, y2_avg)

    def _smooth_angle(self) -> Optional[float]:
        """Average shaft angle across history.

        Returns:
            Smoothed angle in degrees or None
        """
        valid_angles = [angle for angle in self.angle_history if angle is not None]

        if not valid_angles:
            return None

        # Use circular mean for angles to handle wraparound
        angles_rad = np.deg2rad(valid_angles)
        sin_mean = np.mean(np.sin(angles_rad))
        cos_mean = np.mean(np.cos(angles_rad))
        mean_angle = np.rad2deg(np.arctan2(sin_mean, cos_mean))

        return float(mean_angle)

    def _smooth_club_head(self) -> Optional[ClubHead]:
        """Average club head position and radius across history.

        Returns:
            Smoothed club head or None
        """
        valid_heads = [head for head in self.head_history if head is not None]

        if not valid_heads:
            return None

        # Average center position
        cx_avg = np.mean([head.center[0] for head in valid_heads])
        cy_avg = np.mean([head.center[1] for head in valid_heads])

        # Average radius
        radius_avg = np.mean([head.radius for head in valid_heads])

        # Average confidence
        confidence_avg = np.mean([head.confidence for head in valid_heads])

        return ClubHead(
            center=(float(cx_avg), float(cy_avg)),
            radius=float(radius_avg),
            confidence=float(confidence_avg)
        )

    def _interpolate_detection(self, detection: DetectionResult) -> DetectionResult:
        """Interpolate detection during temporary occlusion.

        Uses last valid detection with reduced confidence.

        Args:
            detection: Current (failed) detection

        Returns:
            Interpolated detection
        """
        # Get last valid detection from history
        last_line = next((line for line in reversed(self.shaft_history) if line), None)
        last_angle = next(
            (angle for angle in reversed(self.angle_history) if angle), None
        )
        last_head = next((head for head in reversed(self.head_history) if head), None)

        if last_line is None:
            # No history to interpolate from
            return detection

        # Reduce confidence based on gap length
        confidence_penalty = 1.0 - (self.frames_since_detection / self.max_gap_frames)

        return DetectionResult(
            shaft_detected=True,
            shaft_line=last_line,
            shaft_angle=last_angle,
            club_head_detected=last_head is not None,
            club_head_center=last_head.center if last_head else None,
            club_head_radius=last_head.radius if last_head else None,
            confidence=detection.confidence * confidence_penalty,
            debug_image=detection.debug_image
        )

    def reset(self):
        """Reset tracking history.

        Clears all history queues and gap counter.
        """
        self.shaft_history.clear()
        self.angle_history.clear()
        self.head_history.clear()
        self.frames_since_detection = 0

        logger.debug("Tracker history reset")
