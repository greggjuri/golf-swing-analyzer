"""Joint angle calculations for body landmark analysis.

This module provides utilities to calculate joint angles from body
landmark positions detected by pose detection systems.
"""

import logging
from typing import Tuple, Optional

from .angles import (
    Point2D,
    Angle,
    angle_between_points,
    angle_from_vertical,
)

logger = logging.getLogger(__name__)


class BodyLandmark:
    """Standard body landmark indices for pose detection.

    These indices match MediaPipe Pose landmark convention.
    """

    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28


class JointAngleCalculator:
    """Calculate joint angles from body landmark positions.

    Supports both left-handed and right-handed golfers.
    All angles returned in degrees.

    Example:
        calc = JointAngleCalculator(handedness="right")
        knee_angle = calc.knee_angle(hip, knee, ankle)
    """

    def __init__(self, handedness: str = "right"):
        """Initialize calculator.

        Args:
            handedness: "right" or "left" for golfer handedness

        Raises:
            ValueError: If handedness is invalid
        """
        if handedness not in ["right", "left"]:
            raise ValueError(
                f"Invalid handedness: {handedness}. Must be 'right' or 'left'"
            )
        self.handedness = handedness
        logger.info(f"Initialized JointAngleCalculator for {handedness}-handed golfer")

    def shoulder_angle(
        self,
        shoulder: Point2D,
        elbow: Point2D,
        hip: Point2D
    ) -> Angle:
        """Calculate shoulder angle (upper arm to torso).

        Measures angle between upper arm and torso line.

        Args:
            shoulder: Shoulder landmark position
            elbow: Elbow landmark position
            hip: Hip landmark position

        Returns:
            Angle in degrees (0-180)

        Raises:
            ValueError: If points are invalid
        """
        return angle_between_points(elbow, shoulder, hip)

    def elbow_angle(
        self,
        shoulder: Point2D,
        elbow: Point2D,
        wrist: Point2D
    ) -> Angle:
        """Calculate elbow flexion angle.

        Args:
            shoulder: Shoulder landmark position
            elbow: Elbow landmark position
            wrist: Wrist landmark position

        Returns:
            Angle in degrees (0-180, 180 = full extension)

        Raises:
            ValueError: If points are invalid
        """
        return angle_between_points(shoulder, elbow, wrist)

    def knee_angle(
        self,
        hip: Point2D,
        knee: Point2D,
        ankle: Point2D
    ) -> Angle:
        """Calculate knee flexion angle.

        Args:
            hip: Hip landmark position
            knee: Knee landmark position
            ankle: Ankle landmark position

        Returns:
            Angle in degrees (0-180, 180 = full extension)

        Raises:
            ValueError: If points are invalid
        """
        return angle_between_points(hip, knee, ankle)

    def hip_angle(
        self,
        shoulder: Point2D,
        hip: Point2D,
        knee: Point2D
    ) -> Angle:
        """Calculate hip flexion angle.

        Args:
            shoulder: Shoulder landmark position
            hip: Hip landmark position
            knee: Knee landmark position

        Returns:
            Angle in degrees (0-180)

        Raises:
            ValueError: If points are invalid
        """
        return angle_between_points(shoulder, hip, knee)

    def spine_angle(
        self,
        shoulder: Point2D,
        hip: Point2D,
        reference_vertical: Optional[Tuple[Point2D, Point2D]] = None
    ) -> Angle:
        """Calculate spine tilt angle from vertical.

        In image coordinates, measures the deviation from a perfectly vertical line.

        Args:
            shoulder: Shoulder landmark position (or midpoint of shoulders)
            hip: Hip landmark position (or midpoint of hips)
            reference_vertical: Optional vertical reference line
                               (defaults to vertical through hip)

        Returns:
            Angle in degrees from vertical (0-90, positive = forward tilt)

        Raises:
            ValueError: If points are invalid
        """
        # Calculate the angle - note we measure from hip to shoulder
        # to get spine direction (upward in image coords)
        spine_tilt = angle_from_vertical(hip, shoulder)

        # The angle might be close to 180 if spine points upward
        # Normalize to [0, 90] range
        spine_tilt = abs(spine_tilt)
        if spine_tilt > 90:
            spine_tilt = 180 - spine_tilt

        return spine_tilt

    def wrist_hinge_angle(
        self,
        elbow: Point2D,
        wrist: Point2D,
        club_grip_end: Point2D
    ) -> Angle:
        """Calculate wrist hinge angle (wrist cock).

        Measures angle between forearm and club shaft at wrist.

        Args:
            elbow: Elbow landmark position
            wrist: Wrist landmark position
            club_grip_end: End of club grip position

        Returns:
            Angle in degrees (0-180, 90 = maximum hinge)

        Raises:
            ValueError: If points are invalid
        """
        return angle_between_points(elbow, wrist, club_grip_end)

    def get_typical_ranges(self) -> dict[str, Tuple[float, float]]:
        """Get typical angle ranges for proper golf swing mechanics.

        Returns:
            Dictionary mapping measurement names to (min, max) ranges in degrees

        Example:
            >>> calc = JointAngleCalculator()
            >>> ranges = calc.get_typical_ranges()
            >>> ranges['knee_flex_address']
            (140, 160)
        """
        return {
            # Address position
            'knee_flex_address': (140.0, 160.0),
            'spine_tilt_address': (30.0, 40.0),
            'elbow_extension_address': (160.0, 175.0),
            'hip_angle_address': (140.0, 160.0),

            # Top of backswing
            'wrist_hinge_top': (80.0, 110.0),
            'elbow_flex_top': (140.0, 170.0),
            'spine_tilt_top': (30.0, 45.0),

            # Impact
            'knee_flex_impact': (150.0, 170.0),
            'spine_tilt_impact': (25.0, 35.0),
            'elbow_extension_impact': (170.0, 180.0),

            # General ranges
            'full_extension': (170.0, 180.0),
            'right_angle': (85.0, 95.0),
        }
