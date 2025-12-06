"""Detect swing plane for different swing phases.

This module identifies swing phases (address, backswing, downswing)
and calculates separate planes for each phase.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

from .geometry import Plane3D
from .calculator import PlaneCalculator, ShaftPosition

logger = logging.getLogger(__name__)


@dataclass
class SwingPlaneResult:
    """Result of swing plane detection.

    Contains planes for different swing phases and key positions.
    """

    address_plane: Optional[Plane3D]
    backswing_plane: Optional[Plane3D]
    downswing_plane: Optional[Plane3D]
    full_swing_plane: Optional[Plane3D]

    impact_position: Optional[ShaftPosition]
    top_position: Optional[ShaftPosition]

    def plane_shift(self) -> Optional[float]:
        """Angle between backswing and downswing planes.

        A common swing characteristic is shifting planes between
        backswing and downswing.

        Returns:
            Angle in degrees, or None if planes not available
        """
        if self.backswing_plane is None or self.downswing_plane is None:
            return None

        from .geometry import angle_between_planes
        return angle_between_planes(self.backswing_plane, self.downswing_plane)


class PlaneDetector:
    """Detect swing plane for different swing phases.

    Identifies backswing, downswing, and impact positions,
    then calculates separate planes for each phase.

    Example:
        detector = PlaneDetector()

        result = detector.detect_swing_planes(shaft_positions)

        if result.downswing_plane:
            print(f"Downswing plane angle: "
                  f"{result.downswing_plane.angle_to_horizontal():.1f}°")

        if result.plane_shift():
            print(f"Plane shift: {result.plane_shift():.1f}°")
    """

    def __init__(
        self,
        calculator: Optional[PlaneCalculator] = None,
        min_phase_points: int = 5
    ):
        """Initialize detector.

        Args:
            calculator: PlaneCalculator to use (creates default if None)
            min_phase_points: Minimum points required per phase

        Raises:
            ValueError: If min_phase_points < 3
        """
        if min_phase_points < 3:
            raise ValueError(
                f"min_phase_points must be >= 3, got {min_phase_points}"
            )

        self.calculator = calculator or PlaneCalculator()
        self.min_phase_points = min_phase_points

        logger.debug(
            f"Initialized PlaneDetector: min_phase_points={min_phase_points}"
        )

    def detect_swing_planes(
        self,
        shaft_positions: List[ShaftPosition]
    ) -> SwingPlaneResult:
        """Detect planes for all swing phases.

        Args:
            shaft_positions: Club shaft positions across swing

        Returns:
            SwingPlaneResult with planes for each phase
        """
        if len(shaft_positions) < self.min_phase_points:
            logger.warning(
                f"Insufficient shaft positions: {len(shaft_positions)}"
            )
            return SwingPlaneResult(
                address_plane=None,
                backswing_plane=None,
                downswing_plane=None,
                full_swing_plane=None,
                impact_position=None,
                top_position=None
            )

        # Find key positions
        top_position = self._find_top_position(shaft_positions)
        impact_position = self._find_impact_position(shaft_positions)

        # Calculate full swing plane
        full_swing_plane = self.calculator.calculate_plane(shaft_positions)

        # Split into phases if we have top position
        if top_position is not None:
            # Address plane (first few frames)
            address_positions = self._get_address_positions(shaft_positions)
            address_plane = (
                self.calculator.calculate_plane(address_positions)
                if len(address_positions) >= self.min_phase_points
                else None
            )

            # Backswing plane (start to top)
            backswing_positions = [
                pos for pos in shaft_positions
                if pos.frame_number <= top_position.frame_number
            ]
            backswing_plane = (
                self.calculator.calculate_plane(backswing_positions)
                if len(backswing_positions) >= self.min_phase_points
                else None
            )

            # Downswing plane (top to end)
            downswing_positions = [
                pos for pos in shaft_positions
                if pos.frame_number >= top_position.frame_number
            ]
            downswing_plane = (
                self.calculator.calculate_plane(
                    downswing_positions,
                    impact_frame=impact_position.frame_number if impact_position else None
                )
                if len(downswing_positions) >= self.min_phase_points
                else None
            )
        else:
            # No top position - use full swing for all
            address_plane = None
            backswing_plane = full_swing_plane
            downswing_plane = full_swing_plane

        return SwingPlaneResult(
            address_plane=address_plane,
            backswing_plane=backswing_plane,
            downswing_plane=downswing_plane,
            full_swing_plane=full_swing_plane,
            impact_position=impact_position,
            top_position=top_position
        )

    def _find_top_position(
        self,
        shaft_positions: List[ShaftPosition]
    ) -> Optional[ShaftPosition]:
        """Find top of backswing position.

        The top is typically where the club head reaches maximum height
        and changes direction.

        Args:
            shaft_positions: List of shaft positions

        Returns:
            Position at top of backswing, or None if cannot determine
        """
        if len(shaft_positions) < 3:
            return None

        # Find position with maximum club head height (minimum y, since y increases down)
        min_y = float('inf')
        top_position = None

        for pos in shaft_positions:
            # Use club head (tip) y-coordinate
            if pos.tip_point.y < min_y:
                min_y = pos.tip_point.y
                top_position = pos

        return top_position

    def _find_impact_position(
        self,
        shaft_positions: List[ShaftPosition]
    ) -> Optional[ShaftPosition]:
        """Find impact position.

        Impact is typically where the club head reaches maximum speed
        in the downswing. For now, we approximate this as the position
        with steepest shaft angle after the top.

        Args:
            shaft_positions: List of shaft positions

        Returns:
            Position at impact, or None if cannot determine
        """
        if len(shaft_positions) < 3:
            return None

        # Find top first
        top_position = self._find_top_position(shaft_positions)
        if top_position is None:
            return None

        # Look for steepest shaft angle after top
        downswing_positions = [
            pos for pos in shaft_positions
            if pos.frame_number > top_position.frame_number
        ]

        if not downswing_positions:
            return None

        # Find position with most vertical shaft (largest |dy|/dx ratio)
        max_steepness = 0.0
        impact_position = None

        for pos in downswing_positions:
            dx = abs(pos.tip_point.x - pos.base_point.x)
            dy = abs(pos.tip_point.y - pos.base_point.y)

            # Avoid division by zero
            if dx < 1e-6:
                steepness = float('inf')
            else:
                steepness = dy / dx

            if steepness > max_steepness:
                max_steepness = steepness
                impact_position = pos

        return impact_position

    def _get_address_positions(
        self,
        shaft_positions: List[ShaftPosition],
        num_frames: int = 10
    ) -> List[ShaftPosition]:
        """Get address positions (first few frames).

        Args:
            shaft_positions: List of shaft positions
            num_frames: Number of frames to consider as address

        Returns:
            List of address positions
        """
        if not shaft_positions:
            return []

        # Get first N frames
        first_frame = shaft_positions[0].frame_number
        address_end = first_frame + num_frames

        return [
            pos for pos in shaft_positions
            if pos.frame_number < address_end
        ]
