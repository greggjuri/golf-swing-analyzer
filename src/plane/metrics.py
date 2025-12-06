"""Calculate golf-specific swing plane metrics.

This module provides tools for calculating attack angle, swing path,
on-plane deviation, and other golf-specific measurements.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List
import math

import numpy as np

from .geometry import Plane3D
from .calculator import ShaftPosition

logger = logging.getLogger(__name__)


@dataclass
class SwingMetrics:
    """Complete swing plane metrics.

    All angles in degrees.
    """

    attack_angle: float           # Impact attack angle (degrees)
    swing_path: float             # Swing path at impact (degrees)
    plane_angle: float            # Plane tilt from horizontal
    plane_shift: Optional[float]  # Backswing to downswing shift

    max_deviation: float          # Maximum off-plane distance
    avg_deviation: float          # Average off-plane distance
    deviation_at_impact: float    # Off-plane at impact


class PlaneMetrics:
    """Calculate swing plane metrics for analysis.

    Computes attack angle, swing path, on-plane deviation,
    and other golf-specific measurements.

    Example:
        metrics = PlaneMetrics()

        attack = metrics.attack_angle(impact_shaft, plane)
        path = metrics.swing_path(impact_shaft)
        deviation = metrics.on_plane_deviation(shaft_position, plane)

        print(f"Attack: {attack:.1f}°")
        print(f"Path: {path:.1f}°")
        print(f"Deviation: {deviation:.2f}")
    """

    def __init__(
        self,
        target_direction: np.ndarray = np.array([0, 1, 0])  # Down-target
    ):
        """Initialize metrics calculator.

        Args:
            target_direction: Direction to target (default: [0, 1, 0])
        """
        # Normalize target direction
        self.target_direction = target_direction / np.linalg.norm(target_direction)

        logger.debug(
            f"Initialized PlaneMetrics: target={self.target_direction}"
        )

    def attack_angle(
        self,
        impact_shaft: ShaftPosition,
        plane: Plane3D
    ) -> float:
        """Calculate attack angle at impact.

        Attack angle is the vertical angle of the club shaft at impact.
        - Positive = hitting up on ball
        - Negative = hitting down on ball

        Args:
            impact_shaft: Shaft position at impact
            plane: Swing plane

        Returns:
            Attack angle in degrees
        """
        # Get shaft direction
        shaft_dir = impact_shaft.direction()

        # Project shaft onto swing plane
        plane_normal = plane.normalize().normal_vector()

        # Remove component perpendicular to plane
        shaft_in_plane = shaft_dir - np.dot(shaft_dir, plane_normal) * plane_normal

        # Normalize
        shaft_in_plane = shaft_in_plane / np.linalg.norm(shaft_in_plane)

        # Angle from horizontal (in screen coordinates, y increases downward)
        # Horizontal reference in plane
        horizontal = np.array([1, 0, 0])

        # Project horizontal onto plane
        horiz_in_plane = horizontal - np.dot(horizontal, plane_normal) * plane_normal
        horiz_in_plane = horiz_in_plane / np.linalg.norm(horiz_in_plane)

        # Calculate angle
        dot_product = np.dot(shaft_in_plane, horiz_in_plane)
        dot_product = np.clip(dot_product, -1.0, 1.0)

        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)

        # Determine sign based on vertical component
        # Positive if shaft pointing up (negative y in screen coords)
        if shaft_in_plane[1] > 0:  # Pointing down
            angle_deg = -angle_deg

        return angle_deg

    def swing_path(
        self,
        impact_shaft: ShaftPosition,
        target_direction: Optional[np.ndarray] = None
    ) -> float:
        """Calculate swing path at impact.

        Swing path is the horizontal angle of club travel relative to target.
        - Positive = in-to-out (right for right-handed)
        - Negative = out-to-in (left for right-handed)

        Args:
            impact_shaft: Shaft position at impact
            target_direction: Optional target direction override

        Returns:
            Swing path angle in degrees
        """
        target = target_direction if target_direction is not None else self.target_direction

        # Get club travel direction (shaft direction)
        travel_dir = impact_shaft.direction()

        # Project to horizontal plane (remove y component)
        travel_horizontal = np.array([travel_dir[0], 0, travel_dir[2]])

        # Check for zero horizontal movement
        if np.linalg.norm(travel_horizontal) < 1e-10:
            # Purely vertical swing - path is 0
            return 0.0

        travel_horizontal = travel_horizontal / np.linalg.norm(travel_horizontal)

        # Project target to horizontal
        target_horizontal = np.array([target[0], 0, target[2]])
        if np.linalg.norm(target_horizontal) < 1e-10:
            # Target is vertical - use default
            target_horizontal = np.array([0, 0, 1])
        else:
            target_horizontal = target_horizontal / np.linalg.norm(target_horizontal)

        # Calculate angle
        dot_product = np.dot(travel_horizontal, target_horizontal)
        dot_product = np.clip(dot_product, -1.0, 1.0)

        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)

        # Determine sign using cross product
        # Cross product y-component tells us in/out direction
        cross = np.cross(target_horizontal, travel_horizontal)

        if cross[1] < 0:  # Out-to-in
            angle_deg = -angle_deg

        return angle_deg

    def on_plane_deviation(
        self,
        shaft_position: ShaftPosition,
        plane: Plane3D
    ) -> float:
        """Calculate perpendicular distance from shaft to plane.

        Measures how far the shaft deviates from the ideal plane.

        Args:
            shaft_position: Shaft position to measure
            plane: Reference plane

        Returns:
            Distance in same units as input points
        """
        # Use shaft midpoint
        midpoint = shaft_position.midpoint()

        # Calculate perpendicular distance to plane
        return abs(plane.point_distance(midpoint))

    def plane_angle(
        self,
        plane: Plane3D
    ) -> float:
        """Calculate plane angle from horizontal.

        Args:
            plane: Plane to measure

        Returns:
            Angle in degrees (0 = flat, 90 = vertical)
        """
        return plane.angle_to_horizontal()

    def calculate_swing_metrics(
        self,
        shaft_positions: List[ShaftPosition],
        plane: Plane3D,
        impact_position: Optional[ShaftPosition] = None,
        plane_shift: Optional[float] = None
    ) -> SwingMetrics:
        """Calculate complete set of swing metrics.

        Args:
            shaft_positions: All shaft positions
            plane: Swing plane (typically downswing plane)
            impact_position: Position at impact (auto-detected if None)
            plane_shift: Backswing to downswing plane shift

        Returns:
            Complete SwingMetrics
        """
        # Find impact if not provided
        if impact_position is None:
            # Use last position as impact approximation
            impact_position = shaft_positions[-1]

        # Calculate deviations for all positions
        deviations = [
            self.on_plane_deviation(pos, plane)
            for pos in shaft_positions
        ]

        # Calculate metrics
        attack = self.attack_angle(impact_position, plane)
        path = self.swing_path(impact_position)
        angle = self.plane_angle(plane)

        max_dev = max(deviations) if deviations else 0.0
        avg_dev = sum(deviations) / len(deviations) if deviations else 0.0
        impact_dev = self.on_plane_deviation(impact_position, plane)

        return SwingMetrics(
            attack_angle=attack,
            swing_path=path,
            plane_angle=angle,
            plane_shift=plane_shift,
            max_deviation=max_dev,
            avg_deviation=avg_dev,
            deviation_at_impact=impact_dev
        )
