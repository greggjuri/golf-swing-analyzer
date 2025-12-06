"""Extract positions, angles, and metrics from pose landmarks."""

import logging
from typing import Optional
import math
from dataclasses import dataclass

from .landmarks import PoseLandmark
from .detector import PoseResult
from ..analysis.angles import angle_between_points

logger = logging.getLogger(__name__)


@dataclass
class Point2D:
    """2D point with x,y coordinates."""

    x: float
    y: float


@dataclass
class Line2D:
    """2D line in slope-intercept form: y = mx + b."""

    m: float  # Slope
    b: float  # Y-intercept


def line_from_points(p1: Point2D, p2: Point2D) -> Line2D:
    """Create line from two points.

    Args:
        p1: First point
        p2: Second point

    Returns:
        Line2D in slope-intercept form
    """
    # Calculate slope
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if abs(dx) < 1e-10:
        # Vertical line - use very large slope
        m = 1e10 if dy > 0 else -1e10
    else:
        m = dy / dx

    # Calculate y-intercept: b = y - mx
    b = p1.y - m * p1.x

    return Line2D(m, b)


class LandmarkExtractor:
    """Extract positions, angles, and measurements from pose landmarks.

    Converts normalized landmark coordinates to pixel positions and
    calculates various body metrics useful for golf swing analysis.

    Example:
        extractor = LandmarkExtractor(1920, 1080)

        result = detector.detect(frame)
        if result:
            # Get pixel position
            shoulder = extractor.get_pixel_position(result, PoseLandmark.LEFT_SHOULDER)

            # Calculate joint angle
            elbow_angle = extractor.get_joint_angle(
                result,
                PoseLandmark.LEFT_ELBOW,
                PoseLandmark.LEFT_SHOULDER,
                PoseLandmark.LEFT_WRIST
            )

            # Get spine angle
            spine_angle = extractor.get_spine_angle(result)
    """

    def __init__(self, frame_width: int, frame_height: int):
        """Initialize extractor with frame dimensions.

        Args:
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels

        Raises:
            ValueError: If dimensions are not positive
        """
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError(
                f"Frame dimensions must be positive, got {frame_width}x{frame_height}"
            )

        self.frame_width = frame_width
        self.frame_height = frame_height

        logger.debug(f"Initialized LandmarkExtractor: {frame_width}x{frame_height}")

    def get_pixel_position(
        self,
        pose_result: PoseResult,
        landmark: PoseLandmark
    ) -> Optional[Point2D]:
        """Convert normalized position to pixel coordinates.

        Args:
            pose_result: Pose detection result
            landmark: Landmark to get position for

        Returns:
            Point2D in pixel coordinates, or None if landmark not detected
        """
        norm_pos = pose_result.get_position(landmark)

        if norm_pos is None:
            return None

        x = norm_pos[0] * self.frame_width
        y = norm_pos[1] * self.frame_height

        return Point2D(x, y)

    def get_joint_angle(
        self,
        pose_result: PoseResult,
        joint: PoseLandmark,
        reference1: PoseLandmark,
        reference2: PoseLandmark
    ) -> Optional[float]:
        """Calculate angle at joint formed by three landmarks.

        Calculates the angle at 'joint' formed by the lines:
        reference1->joint and joint->reference2

        Args:
            pose_result: Pose detection result
            joint: Center landmark (where angle is measured)
            reference1: First reference point
            reference2: Second reference point

        Returns:
            Angle in degrees (0-180), or None if any landmark missing

        Example:
            # Calculate elbow angle
            angle = extractor.get_joint_angle(
                result,
                PoseLandmark.LEFT_ELBOW,      # joint
                PoseLandmark.LEFT_SHOULDER,   # reference1
                PoseLandmark.LEFT_WRIST       # reference2
            )
        """
        # Get pixel positions
        p_joint = self.get_pixel_position(pose_result, joint)
        p_ref1 = self.get_pixel_position(pose_result, reference1)
        p_ref2 = self.get_pixel_position(pose_result, reference2)

        if p_joint is None or p_ref1 is None or p_ref2 is None:
            return None

        # Check visibility
        if not pose_result.is_visible(joint, min_visibility=0.5):
            return None
        if not pose_result.is_visible(reference1, min_visibility=0.5):
            return None
        if not pose_result.is_visible(reference2, min_visibility=0.5):
            return None

        # Calculate angle (convert Point2D to tuples for angle_between_points)
        return angle_between_points(
            (p_ref1.x, p_ref1.y),
            (p_joint.x, p_joint.y),
            (p_ref2.x, p_ref2.y)
        )

    def get_body_center(self, pose_result: PoseResult) -> Optional[Point2D]:
        """Calculate center point between hips.

        Args:
            pose_result: Pose detection result

        Returns:
            Center point in pixel coordinates, or None if hips not detected
        """
        left_hip = self.get_pixel_position(pose_result, PoseLandmark.LEFT_HIP)
        right_hip = self.get_pixel_position(pose_result, PoseLandmark.RIGHT_HIP)

        if left_hip is None or right_hip is None:
            return None

        center_x = (left_hip.x + right_hip.x) / 2
        center_y = (left_hip.y + right_hip.y) / 2

        return Point2D(center_x, center_y)

    def get_shoulder_line(self, pose_result: PoseResult) -> Optional[Line2D]:
        """Get line through shoulders.

        Args:
            pose_result: Pose detection result

        Returns:
            Line2D through shoulders, or None if shoulders not detected
        """
        left_shoulder = self.get_pixel_position(pose_result, PoseLandmark.LEFT_SHOULDER)
        right_shoulder = self.get_pixel_position(pose_result, PoseLandmark.RIGHT_SHOULDER)

        if left_shoulder is None or right_shoulder is None:
            return None

        if not pose_result.is_visible(PoseLandmark.LEFT_SHOULDER, 0.5):
            return None
        if not pose_result.is_visible(PoseLandmark.RIGHT_SHOULDER, 0.5):
            return None

        return line_from_points(left_shoulder, right_shoulder)

    def get_hip_line(self, pose_result: PoseResult) -> Optional[Line2D]:
        """Get line through hips.

        Args:
            pose_result: Pose detection result

        Returns:
            Line2D through hips, or None if hips not detected
        """
        left_hip = self.get_pixel_position(pose_result, PoseLandmark.LEFT_HIP)
        right_hip = self.get_pixel_position(pose_result, PoseLandmark.RIGHT_HIP)

        if left_hip is None or right_hip is None:
            return None

        if not pose_result.is_visible(PoseLandmark.LEFT_HIP, 0.5):
            return None
        if not pose_result.is_visible(PoseLandmark.RIGHT_HIP, 0.5):
            return None

        return line_from_points(left_hip, right_hip)

    def get_spine_angle(self, pose_result: PoseResult) -> Optional[float]:
        """Calculate spine angle from vertical.

        Measures the angle of the line from hip center to shoulder center
        relative to vertical (90 degrees = upright, <90 = leaning forward).

        Args:
            pose_result: Pose detection result

        Returns:
            Spine angle in degrees from vertical, or None if cannot calculate
        """
        # Get hip center
        hip_center = self.get_body_center(pose_result)
        if hip_center is None:
            return None

        # Get shoulder center
        left_shoulder = self.get_pixel_position(pose_result, PoseLandmark.LEFT_SHOULDER)
        right_shoulder = self.get_pixel_position(pose_result, PoseLandmark.RIGHT_SHOULDER)

        if left_shoulder is None or right_shoulder is None:
            return None

        shoulder_center = Point2D(
            (left_shoulder.x + right_shoulder.x) / 2,
            (left_shoulder.y + right_shoulder.y) / 2
        )

        # Calculate angle from vertical
        # Vertical line goes down (positive y), so we measure from (0, 1) vector
        dx = shoulder_center.x - hip_center.x
        dy = shoulder_center.y - hip_center.y

        # Angle from vertical (in image coordinates, y increases downward)
        angle_rad = math.atan2(dx, -dy)  # -dy because y increases downward
        angle_deg = math.degrees(angle_rad)

        # Normalize to 0-180 range (0 = leaning far forward, 90 = upright, 180 = leaning back)
        angle_deg = 90 - angle_deg

        return angle_deg

    def get_shoulder_rotation(self, pose_result: PoseResult) -> Optional[float]:
        """Calculate shoulder rotation from horizontal.

        Measures how much the shoulders are rotated (useful for tracking
        shoulder turn in golf swing).

        Args:
            pose_result: Pose detection result

        Returns:
            Shoulder rotation in degrees (0 = level, +/- indicates direction)
        """
        shoulder_line = self.get_shoulder_line(pose_result)

        if shoulder_line is None:
            return None

        # Calculate angle from horizontal
        # Line equation: y = mx + b, where m is slope
        # Angle = arctan(m)
        angle_rad = math.atan(shoulder_line.m)
        angle_deg = math.degrees(angle_rad)

        return angle_deg

    def get_hip_rotation(self, pose_result: PoseResult) -> Optional[float]:
        """Calculate hip rotation from horizontal.

        Args:
            pose_result: Pose detection result

        Returns:
            Hip rotation in degrees (0 = level, +/- indicates direction)
        """
        hip_line = self.get_hip_line(pose_result)

        if hip_line is None:
            return None

        angle_rad = math.atan(hip_line.m)
        angle_deg = math.degrees(angle_rad)

        return angle_deg

    def get_x_factor(self, pose_result: PoseResult) -> Optional[float]:
        """Calculate X-Factor (shoulder-hip separation).

        The X-Factor is the difference between shoulder rotation and
        hip rotation - a key metric in golf swing analysis.

        Args:
            pose_result: Pose detection result

        Returns:
            X-Factor in degrees, or None if cannot calculate
        """
        shoulder_rot = self.get_shoulder_rotation(pose_result)
        hip_rot = self.get_hip_rotation(pose_result)

        if shoulder_rot is None or hip_rot is None:
            return None

        return abs(shoulder_rot - hip_rot)
