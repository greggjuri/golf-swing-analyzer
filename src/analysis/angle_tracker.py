"""Angle tracking across video frames for graphing and analysis."""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class AngleTracker:
    """Tracks angle measurements across video frames.

    Collects angle data from pose and club analysis results,
    organizing it for time-series graphing and comparison.

    Example:
        tracker = AngleTracker()

        # Add data frame by frame
        for frame_num, landmarks in pose_results.items():
            angles = extract_angles_from_pose(landmarks)
            tracker.add_frame_data(frame_num, angles)

        # Get series for graphing
        frames, values = tracker.get_angle_series('spine_angle')
        plot(frames, values)
    """

    def __init__(self):
        """Initialize angle tracker."""
        # angle_name -> {frame_num: value}
        self.angle_data: Dict[str, Dict[int, float]] = {}
        logger.debug("Initialized AngleTracker")

    def add_frame_data(self, frame_num: int, angles: Dict[str, float]):
        """Add angle measurements for a specific frame.

        Args:
            frame_num: Frame number
            angles: Dictionary of angle_name -> value (in degrees)
        """
        for angle_name, value in angles.items():
            if angle_name not in self.angle_data:
                self.angle_data[angle_name] = {}

            self.angle_data[angle_name][frame_num] = value

    def get_angle_series(
        self,
        angle_name: str,
        fill_gaps: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get time series data for a specific angle.

        Args:
            angle_name: Name of angle to retrieve
            fill_gaps: If True, interpolate missing frames

        Returns:
            Tuple of (frame_numbers, angle_values) as numpy arrays

        Raises:
            KeyError: If angle_name not found
        """
        if angle_name not in self.angle_data:
            raise KeyError(f"Angle '{angle_name}' not found in tracker")

        frame_dict = self.angle_data[angle_name]

        if not frame_dict:
            return np.array([]), np.array([])

        # Sort by frame number
        frames = np.array(sorted(frame_dict.keys()))
        values = np.array([frame_dict[f] for f in frames])

        if fill_gaps and len(frames) > 1:
            # Fill gaps with linear interpolation
            frames, values = self._fill_gaps(frames, values)

        return frames, values

    def _fill_gaps(
        self,
        frames: np.ndarray,
        values: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Fill missing frames with linear interpolation.

        Args:
            frames: Frame numbers (sorted)
            values: Angle values

        Returns:
            Tuple of (filled_frames, filled_values) with no gaps
        """
        if len(frames) < 2:
            return frames, values

        # Create continuous frame range
        start_frame = int(frames[0])
        end_frame = int(frames[-1])
        filled_frames = np.arange(start_frame, end_frame + 1)

        # Interpolate values
        filled_values = np.interp(filled_frames, frames, values)

        return filled_frames, filled_values

    def get_available_angles(self) -> List[str]:
        """Get list of all tracked angle names.

        Returns:
            List of angle names that have data
        """
        return sorted(self.angle_data.keys())

    def get_angle_at_frame(self, angle_name: str, frame_num: int) -> Optional[float]:
        """Get angle value at specific frame.

        Args:
            angle_name: Name of angle
            frame_num: Frame number

        Returns:
            Angle value in degrees, or None if not available
        """
        if angle_name not in self.angle_data:
            return None

        return self.angle_data[angle_name].get(frame_num)

    def get_angle_stats(self, angle_name: str) -> Dict[str, float]:
        """Get statistical summary of an angle.

        Args:
            angle_name: Name of angle

        Returns:
            Dictionary with min, max, mean, std
        """
        if angle_name not in self.angle_data:
            return {}

        values = list(self.angle_data[angle_name].values())

        if not values:
            return {}

        return {
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'range': float(np.max(values) - np.min(values))
        }

    def get_frame_range(self, angle_name: str) -> Optional[Tuple[int, int]]:
        """Get frame range where angle has data.

        Args:
            angle_name: Name of angle

        Returns:
            Tuple of (start_frame, end_frame) or None if no data
        """
        if angle_name not in self.angle_data or not self.angle_data[angle_name]:
            return None

        frames = list(self.angle_data[angle_name].keys())
        return (min(frames), max(frames))

    def clear(self):
        """Clear all angle data."""
        self.angle_data.clear()
        logger.debug("Cleared all angle data")

    def merge(self, other: 'AngleTracker'):
        """Merge data from another tracker.

        Args:
            other: Another AngleTracker instance
        """
        for angle_name, frame_dict in other.angle_data.items():
            if angle_name not in self.angle_data:
                self.angle_data[angle_name] = {}

            self.angle_data[angle_name].update(frame_dict)

        logger.debug("Merged data from another tracker")


def extract_angles_from_pose(landmarks: dict) -> Dict[str, float]:
    """Extract body angles from pose landmarks.

    Args:
        landmarks: Dictionary of landmark_name -> (x, y) coordinates

    Returns:
        Dictionary of angle_name -> value (degrees)
    """
    from .angles import JointAngleCalculator, angle_between_points

    calculator = JointAngleCalculator()
    angles = {}

    try:
        # Spine angle (torso tilt from vertical)
        if all(p in landmarks for p in ['left_shoulder', 'left_hip']):
            shoulder = landmarks['left_shoulder']
            hip = landmarks['left_hip']

            # Calculate angle from vertical
            # Vertical reference point (directly below shoulder)
            vertical_ref = (shoulder[0], shoulder[1] + 100)

            spine_angle = angle_between_points(vertical_ref, shoulder, hip)
            angles['spine_angle'] = spine_angle

        # Left elbow angle
        if all(p in landmarks for p in ['left_shoulder', 'left_elbow', 'left_wrist']):
            angles['left_elbow'] = calculator.calculate_joint_angle(
                landmarks['left_shoulder'],
                landmarks['left_elbow'],
                landmarks['left_wrist']
            )

        # Right elbow angle
        if all(p in landmarks for p in ['right_shoulder', 'right_elbow', 'right_wrist']):
            angles['right_elbow'] = calculator.calculate_joint_angle(
                landmarks['right_shoulder'],
                landmarks['right_elbow'],
                landmarks['right_wrist']
            )

        # Left knee angle
        if all(p in landmarks for p in ['left_hip', 'left_knee', 'left_ankle']):
            angles['left_knee'] = calculator.calculate_joint_angle(
                landmarks['left_hip'],
                landmarks['left_knee'],
                landmarks['left_ankle']
            )

        # Right knee angle
        if all(p in landmarks for p in ['right_hip', 'right_knee', 'right_ankle']):
            angles['right_knee'] = calculator.calculate_joint_angle(
                landmarks['right_hip'],
                landmarks['right_knee'],
                landmarks['right_ankle']
            )

        # Shoulder rotation (simplified - needs 3D for accuracy)
        if all(p in landmarks for p in ['left_shoulder', 'right_shoulder']):
            left_shoulder = landmarks['left_shoulder']
            right_shoulder = landmarks['right_shoulder']

            # Angle of shoulder line from horizontal
            dx = right_shoulder[0] - left_shoulder[0]
            dy = right_shoulder[1] - left_shoulder[1]
            shoulder_rotation = np.degrees(np.arctan2(dy, dx))
            angles['shoulder_rotation'] = shoulder_rotation

    except Exception as e:
        logger.error(f"Error extracting pose angles: {e}")

    return angles


def extract_club_angles(club_data: dict) -> Dict[str, float]:
    """Extract club angles from club detection data.

    Args:
        club_data: Club detection results with shaft_line, club_head, etc.

    Returns:
        Dictionary of angle_name -> value (degrees)
    """
    from .angles import ClubAngleCalculator

    calculator = ClubAngleCalculator()
    angles = {}

    try:
        # Club shaft angle from ground
        if 'shaft_line' in club_data:
            shaft_line = club_data['shaft_line']
            angles['club_shaft_angle'] = calculator.calculate_shaft_angle(shaft_line)

        # Club shaft angle from target line (if available)
        # Would need target line reference - placeholder for now

    except Exception as e:
        logger.error(f"Error extracting club angles: {e}")

    return angles
