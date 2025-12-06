"""Club angle calculations for swing analysis.

This module provides utilities to calculate club shaft angles and
swing plane measurements.
"""

import logging
from typing import Tuple, Optional

import numpy as np

from .angles import (
    Point2D,
    Angle,
    angle_from_horizontal,
    angle_from_vertical,
)

logger = logging.getLogger(__name__)


class ClubAngleCalculator:
    """Calculate club shaft and swing plane angles.

    All angles returned in degrees.

    Example:
        calc = ClubAngleCalculator()
        shaft_angle = calc.shaft_angle_to_ground(grip, club_head)
    """

    def shaft_angle_to_ground(
        self,
        grip_point: Point2D,
        club_head: Point2D,
        ground_reference: Optional[Tuple[Point2D, Point2D]] = None
    ) -> Angle:
        """Calculate club shaft angle relative to ground.

        Args:
            grip_point: Position of club grip
            club_head: Position of club head
            ground_reference: Optional horizontal ground line
                            (defaults to horizontal through club head)

        Returns:
            Angle in degrees from ground (0-90)

        Raises:
            ValueError: If grip and club head are at same position
        """
        # Calculate angle from horizontal
        shaft_angle = angle_from_horizontal(club_head, grip_point)

        # Convert to angle from ground (absolute value, 0-90 range)
        angle_from_ground = abs(shaft_angle)

        # Ensure we're measuring the acute angle
        if angle_from_ground > 90:
            angle_from_ground = 180 - angle_from_ground

        return angle_from_ground

    def shaft_angle_to_vertical(
        self,
        grip_point: Point2D,
        club_head: Point2D
    ) -> Angle:
        """Calculate club shaft angle from vertical.

        Args:
            grip_point: Position of club grip
            club_head: Position of club head

        Returns:
            Angle in degrees from vertical (0-90)

        Raises:
            ValueError: If grip and club head are at same position
        """
        # Calculate angle from vertical (measuring from club head to grip)
        shaft_angle = angle_from_vertical(club_head, grip_point)

        # Normalize to [0, 90] range
        shaft_angle = abs(shaft_angle)
        if shaft_angle > 90:
            shaft_angle = 180 - shaft_angle

        return shaft_angle

    def shaft_angle_to_target_line(
        self,
        grip_point: Point2D,
        club_head: Point2D,
        target_line: Tuple[Point2D, Point2D]
    ) -> Angle:
        """Calculate club shaft angle relative to target line.

        Args:
            grip_point: Position of club grip
            club_head: Position of club head
            target_line: Line toward target (start, end)

        Returns:
            Angle in degrees (0-90)

        Raises:
            ValueError: If points are invalid
        """
        # Convert points to vectors
        shaft_vec = np.array(grip_point, dtype=float) - np.array(club_head, dtype=float)
        target_vec = np.array(target_line[1], dtype=float) - np.array(target_line[0], dtype=float)

        # Normalize vectors
        shaft_norm = np.linalg.norm(shaft_vec)
        target_norm = np.linalg.norm(target_vec)

        if shaft_norm == 0:
            raise ValueError("Grip and club head are at same position")
        if target_norm == 0:
            raise ValueError("Target line has zero length")

        shaft_unit = shaft_vec / shaft_norm
        target_unit = target_vec / target_norm

        # Calculate angle using dot product
        dot_product = np.dot(shaft_unit, target_unit)
        dot_product = np.clip(dot_product, -1.0, 1.0)

        angle_rad = np.arccos(abs(dot_product))
        angle_deg = float(np.degrees(angle_rad))

        return angle_deg

    def lie_angle(
        self,
        shaft_grip: Point2D,
        shaft_hosel: Point2D,
        club_head_toe: Point2D,
        ground_reference: Tuple[Point2D, Point2D]
    ) -> Angle:
        """Calculate lie angle (club sole to ground when shaft at address).

        The lie angle is measured between the shaft and the ground plane
        when the club sole is flush with the ground.

        Args:
            shaft_grip: Top of shaft (grip)
            shaft_hosel: Bottom of shaft (hosel)
            club_head_toe: Toe of club head
            ground_reference: Horizontal ground line

        Returns:
            Lie angle in degrees (typical: 60-65 degrees)

        Raises:
            ValueError: If points are invalid
        """
        # For lie angle, we measure the angle between:
        # 1. The shaft line (hosel to grip)
        # 2. The ground plane

        # Calculate shaft angle to ground
        shaft_angle = self.shaft_angle_to_ground(
            shaft_grip,
            shaft_hosel,
            ground_reference
        )

        return shaft_angle

    def swing_plane_angle(
        self,
        hands_at_address: Point2D,
        hands_at_top: Point2D,
        ball_position: Point2D
    ) -> Angle:
        """Calculate swing plane angle.

        Measures angle of swing plane relative to ground.
        The swing plane is defined by the line from the ball through
        the hands at various positions in the swing.

        Args:
            hands_at_address: Hand position at address
            hands_at_top: Hand position at top of backswing
            ball_position: Ball position on ground

        Returns:
            Swing plane angle in degrees (typical: 45-60 degrees)

        Raises:
            ValueError: If points are invalid
        """
        # Create swing plane line from ball through hands
        # Use the address position as reference
        plane_angle = angle_from_horizontal(ball_position, hands_at_address)

        # Normalize to acute angle (0-90 degrees)
        plane_angle = abs(plane_angle)
        if plane_angle > 90:
            plane_angle = 180 - plane_angle

        return plane_angle
