"""Calculate best-fit swing plane from club shaft positions.

This module provides tools for fitting a plane to club shaft positions
during a golf swing, with optional weighting for impact zone positions.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

import numpy as np

from .geometry import Point3D, Plane3D, fit_plane_svd, weighted_plane_fit

logger = logging.getLogger(__name__)


@dataclass
class ShaftPosition:
    """Club shaft position in 3D space at specific frame.

    Represents the club shaft as a line segment from grip (base) to
    club head (tip) at a specific point in time.
    """

    frame_number: int
    base_point: Point3D      # Grip end
    tip_point: Point3D       # Club head end
    timestamp: float

    def midpoint(self) -> Point3D:
        """Get midpoint of shaft.

        Returns:
            Point at center of shaft
        """
        return Point3D(
            (self.base_point.x + self.tip_point.x) / 2,
            (self.base_point.y + self.tip_point.y) / 2,
            (self.base_point.z + self.tip_point.z) / 2
        )

    def direction(self) -> np.ndarray:
        """Get shaft direction vector (from base to tip).

        Returns:
            Normalized direction vector
        """
        dx = self.tip_point.x - self.base_point.x
        dy = self.tip_point.y - self.base_point.y
        dz = self.tip_point.z - self.base_point.z

        direction = np.array([dx, dy, dz])
        magnitude = np.linalg.norm(direction)

        if magnitude < 1e-10:
            raise ValueError("Shaft has zero length")

        return direction / magnitude

    def length(self) -> float:
        """Get shaft length.

        Returns:
            Distance between base and tip
        """
        return self.base_point.distance_to(self.tip_point)


class PlaneCalculator:
    """Calculate swing plane from club shaft positions.

    Uses weighted regression to fit plane, with higher weights
    for positions near impact.

    Example:
        calculator = PlaneCalculator(impact_zone_weight=2.0)

        plane = calculator.calculate_plane(
            shaft_positions,
            impact_frame=150
        )

        if plane:
            print(f"Plane angle: {plane.angle_to_horizontal():.1f}°")
    """

    def __init__(
        self,
        impact_zone_weight: float = 2.0,
        impact_zone_frames: int = 10,
        min_points: int = 10
    ):
        """Initialize calculator.

        Args:
            impact_zone_weight: Weight multiplier for impact zone points
            impact_zone_frames: Number of frames around impact to weight higher
            min_points: Minimum points required to fit plane

        Raises:
            ValueError: If parameters are invalid
        """
        if impact_zone_weight < 1.0:
            raise ValueError(
                f"impact_zone_weight must be >= 1.0, got {impact_zone_weight}"
            )

        if impact_zone_frames < 1:
            raise ValueError(
                f"impact_zone_frames must be >= 1, got {impact_zone_frames}"
            )

        if min_points < 3:
            raise ValueError(
                f"min_points must be >= 3, got {min_points}"
            )

        self.impact_zone_weight = impact_zone_weight
        self.impact_zone_frames = impact_zone_frames
        self.min_points = min_points

        logger.debug(
            f"Initialized PlaneCalculator: "
            f"impact_weight={impact_zone_weight}, "
            f"impact_frames={impact_zone_frames}, "
            f"min_points={min_points}"
        )

    def calculate_plane(
        self,
        shaft_positions: List[ShaftPosition],
        impact_frame: Optional[int] = None
    ) -> Optional[Plane3D]:
        """Calculate best-fit plane from shaft positions.

        Args:
            shaft_positions: List of shaft positions with 3D points
            impact_frame: Frame number of impact (for weighting)

        Returns:
            Best-fit Plane3D or None if insufficient data
        """
        if len(shaft_positions) < self.min_points:
            logger.warning(
                f"Insufficient shaft positions: {len(shaft_positions)} < "
                f"{self.min_points}"
            )
            return None

        # Extract midpoints from shaft positions
        points = [pos.midpoint() for pos in shaft_positions]

        # Calculate weights based on distance from impact
        if impact_frame is not None:
            weights = self._calculate_weights(shaft_positions, impact_frame)
            return weighted_plane_fit(points, weights)
        else:
            # Uniform weighting
            return fit_plane_svd(points)

    def _calculate_weights(
        self,
        shaft_positions: List[ShaftPosition],
        impact_frame: int
    ) -> List[float]:
        """Calculate weights for each position based on impact proximity.

        Args:
            shaft_positions: List of shaft positions
            impact_frame: Frame number of impact

        Returns:
            List of weights (same length as shaft_positions)
        """
        weights = []

        for pos in shaft_positions:
            # Distance from impact in frames
            distance = abs(pos.frame_number - impact_frame)

            # Apply higher weight if within impact zone
            if distance <= self.impact_zone_frames:
                weights.append(self.impact_zone_weight)
            else:
                weights.append(1.0)

        return weights

    def calculate_weighted_plane(
        self,
        points: List[Point3D],
        weights: List[float]
    ) -> Plane3D:
        """Calculate weighted best-fit plane.

        Args:
            points: List of 3D points
            weights: Weight for each point

        Returns:
            Best-fit Plane3D

        Raises:
            ValueError: If points and weights have different lengths
            ValueError: If fewer than min_points provided
        """
        if len(points) < self.min_points:
            raise ValueError(
                f"Insufficient points: {len(points)} < {self.min_points}"
            )

        return weighted_plane_fit(points, weights)
