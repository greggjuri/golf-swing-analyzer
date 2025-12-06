"""Multi-frame pose tracking with temporal smoothing."""

import logging
from typing import Optional, List, Dict, Deque
from collections import deque
import copy

import numpy as np

from .landmarks import PoseLandmark, LandmarkPoint
from .detector import PoseResult

logger = logging.getLogger(__name__)


class PoseTracker:
    """Track poses across multiple frames with temporal smoothing.

    Smooths landmark positions using a moving average window and
    interpolates missing detections for short gaps.

    Example:
        tracker = PoseTracker(smoothing_window=5)

        for frame_num, frame in enumerate(frames):
            result = detector.detect(frame)
            smoothed = tracker.update(frame_num, result)

            if smoothed:
                # Use smoothed result
                pass
    """

    def __init__(
        self,
        smoothing_window: int = 5,
        max_gap_frames: int = 10,
        confidence_threshold: float = 0.5
    ):
        """Initialize pose tracker.

        Args:
            smoothing_window: Number of frames to average for smoothing
            max_gap_frames: Maximum frames to interpolate across gaps
            confidence_threshold: Minimum confidence for valid detection

        Raises:
            ValueError: If parameters are invalid
        """
        if smoothing_window < 1:
            raise ValueError(f"smoothing_window must be >= 1, got {smoothing_window}")

        if max_gap_frames < 0:
            raise ValueError(f"max_gap_frames must be >= 0, got {max_gap_frames}")

        if not (0.0 <= confidence_threshold <= 1.0):
            raise ValueError(f"confidence_threshold must be 0-1, got {confidence_threshold}")

        self.smoothing_window = smoothing_window
        self.max_gap_frames = max_gap_frames
        self.confidence_threshold = confidence_threshold

        # History of pose results (newest first)
        self.pose_history: Deque[Optional[PoseResult]] = deque(maxlen=smoothing_window)

        # Track last valid detection
        self.last_valid_frame: Optional[int] = None
        self.last_valid_pose: Optional[PoseResult] = None

        # Current frame number
        self.current_frame = -1

        logger.debug(
            f"Initialized PoseTracker: window={smoothing_window}, "
            f"max_gap={max_gap_frames}, conf_threshold={confidence_threshold}"
        )

    def update(
        self,
        frame_number: int,
        pose_result: Optional[PoseResult]
    ) -> Optional[PoseResult]:
        """Update tracker with new detection.

        Args:
            frame_number: Current frame number
            pose_result: Pose detection result (None if no pose detected)

        Returns:
            Smoothed pose result, interpolated result, or None

        Raises:
            ValueError: If frame_number is not sequential
        """
        # Validate frame number
        if frame_number <= self.current_frame and self.current_frame >= 0:
            raise ValueError(
                f"Frame numbers must be sequential, got {frame_number} "
                f"after {self.current_frame}"
            )

        self.current_frame = frame_number

        # Check if detection is valid
        valid_detection = False
        if pose_result is not None:
            if pose_result.detection_confidence >= self.confidence_threshold:
                valid_detection = True

        if valid_detection:
            # Valid detection - add to history
            self.pose_history.append(pose_result)
            self.last_valid_frame = frame_number
            self.last_valid_pose = pose_result

            # Return smoothed result
            return self._smooth_poses()

        else:
            # No valid detection
            self.pose_history.append(None)

            # Try interpolation if gap is small
            if self.last_valid_frame is not None:
                gap = frame_number - self.last_valid_frame

                if gap <= self.max_gap_frames:
                    # Interpolate
                    return self._interpolate_pose(gap)
                else:
                    # Gap too large
                    logger.debug(
                        f"Frame {frame_number}: Gap too large ({gap} frames), "
                        f"no interpolation"
                    )
                    return None
            else:
                # No previous valid pose
                return None

    def _smooth_poses(self) -> Optional[PoseResult]:
        """Smooth landmark positions using moving average.

        Averages landmark positions from recent valid detections.

        Returns:
            Smoothed PoseResult
        """
        # Get valid poses from history
        valid_poses = [p for p in self.pose_history if p is not None]

        if not valid_poses:
            return None

        # Average landmark positions
        smoothed_landmarks = {}
        smoothed_world_landmarks = {}

        # Get all landmarks from most recent pose
        reference_pose = valid_poses[-1]

        for landmark in reference_pose.landmarks.keys():
            # Collect positions for this landmark from all valid poses
            positions = []
            visibilities = []
            presences = []

            for pose in valid_poses:
                if landmark in pose.landmarks:
                    point = pose.landmarks[landmark]
                    positions.append((point.x, point.y, point.z))
                    visibilities.append(point.visibility)
                    presences.append(point.presence)

            if positions:
                # Average positions
                avg_x = np.mean([p[0] for p in positions])
                avg_y = np.mean([p[1] for p in positions])
                avg_z = np.mean([p[2] for p in positions])
                avg_vis = np.mean(visibilities)
                avg_pres = np.mean(presences)

                smoothed_landmarks[landmark] = LandmarkPoint(
                    x=float(avg_x),
                    y=float(avg_y),
                    z=float(avg_z),
                    visibility=float(avg_vis),
                    presence=float(avg_pres)
                )

                # Same for world landmarks
                if landmark in pose.world_landmarks:
                    smoothed_world_landmarks[landmark] = LandmarkPoint(
                        x=float(avg_x),
                        y=float(avg_y),
                        z=float(avg_z),
                        visibility=float(avg_vis),
                        presence=float(avg_pres)
                    )

        # Create smoothed result
        return PoseResult(
            landmarks=smoothed_landmarks,
            world_landmarks=smoothed_world_landmarks,
            timestamp=reference_pose.timestamp,
            detection_confidence=reference_pose.detection_confidence
        )

    def _interpolate_pose(self, gap: int) -> Optional[PoseResult]:
        """Interpolate pose for missing detection.

        Uses last valid pose with reduced confidence.

        Args:
            gap: Number of frames since last valid detection

        Returns:
            Interpolated pose result
        """
        if self.last_valid_pose is None:
            return None

        # Create copy of last valid pose
        interpolated = copy.deepcopy(self.last_valid_pose)

        # Reduce confidence based on gap size
        confidence_decay = 1.0 - (gap / self.max_gap_frames)
        interpolated.detection_confidence *= confidence_decay

        # Reduce visibility of all landmarks
        for landmark in interpolated.landmarks.values():
            landmark.visibility *= confidence_decay

        logger.debug(
            f"Frame {self.current_frame}: Interpolated pose "
            f"(gap={gap}, conf={interpolated.detection_confidence:.2f})"
        )

        return interpolated

    def get_history(
        self,
        landmark: PoseLandmark,
        num_frames: int = 10
    ) -> List[tuple[float, float]]:
        """Get position history for specific landmark.

        Args:
            landmark: Landmark to get history for
            num_frames: Number of recent frames to return

        Returns:
            List of (x, y) positions (newest first)
        """
        positions = []

        for pose in list(self.pose_history)[:num_frames]:
            if pose is not None and landmark in pose.landmarks:
                point = pose.landmarks[landmark]
                positions.append((point.x, point.y))

        return positions

    def reset(self):
        """Clear tracking history.

        Useful when starting a new video or when tracking is lost.
        """
        self.pose_history.clear()
        self.last_valid_frame = None
        self.last_valid_pose = None
        self.current_frame = -1

        logger.debug("Reset PoseTracker")

    def get_tracking_stats(self) -> Dict[str, float]:
        """Get tracking statistics.

        Returns:
            Dictionary with tracking metrics:
            - detection_rate: Percentage of frames with valid detections
            - avg_confidence: Average detection confidence
            - history_size: Number of frames in history
        """
        valid_count = sum(1 for p in self.pose_history if p is not None)
        total_count = len(self.pose_history)

        detection_rate = (valid_count / total_count * 100) if total_count > 0 else 0.0

        confidences = [
            p.detection_confidence
            for p in self.pose_history
            if p is not None
        ]
        avg_confidence = np.mean(confidences) if confidences else 0.0

        return {
            'detection_rate': detection_rate,
            'avg_confidence': float(avg_confidence),
            'history_size': total_count
        }
