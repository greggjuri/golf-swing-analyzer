"""High-level swing plane analysis interface.

This module combines plane detection, calculation, and metrics
into a single easy-to-use interface.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

from .geometry import Plane3D
from .calculator import PlaneCalculator, ShaftPosition
from .detector import PlaneDetector, SwingPlaneResult
from .metrics import PlaneMetrics, SwingMetrics

logger = logging.getLogger(__name__)


@dataclass
class SwingPlaneAnalysis:
    """Complete swing plane analysis result.

    Contains all planes, metrics, and deviation measurements
    for a golf swing.
    """

    planes: SwingPlaneResult
    metrics: SwingMetrics
    deviations: List[float]  # Deviation for each shaft position

    success: bool
    error_message: Optional[str] = None


class SwingPlaneAnalyzer:
    """High-level swing plane analysis interface.

    Combines plane detection, calculation, and metrics
    into a single easy-to-use interface.

    Example:
        analyzer = SwingPlaneAnalyzer()

        # Analyze swing
        result = analyzer.analyze(shaft_positions)

        if result.success:
            # Get metrics
            print(f"Attack angle: {result.metrics.attack_angle:.1f}°")
            print(f"Swing path: {result.metrics.swing_path:.1f}°")
            print(f"Plane angle: {result.metrics.plane_angle:.1f}°")

            # Check plane shift
            if result.metrics.plane_shift:
                print(f"Plane shift: {result.metrics.plane_shift:.1f}°")

            # Deviation stats
            print(f"Max deviation: {result.metrics.max_deviation:.2f}")
            print(f"Avg deviation: {result.metrics.avg_deviation:.2f}")
        else:
            print(f"Analysis failed: {result.error_message}")
    """

    def __init__(
        self,
        calculator: Optional[PlaneCalculator] = None,
        detector: Optional[PlaneDetector] = None,
        metrics_calculator: Optional[PlaneMetrics] = None
    ):
        """Initialize analyzer with optional custom components.

        Args:
            calculator: PlaneCalculator (creates default if None)
            detector: PlaneDetector (creates default if None)
            metrics_calculator: PlaneMetrics (creates default if None)
        """
        self.calculator = calculator or PlaneCalculator()
        self.detector = detector or PlaneDetector(calculator=self.calculator)
        self.metrics_calculator = metrics_calculator or PlaneMetrics()

        logger.debug("Initialized SwingPlaneAnalyzer")

    def analyze(
        self,
        shaft_positions: List[ShaftPosition]
    ) -> SwingPlaneAnalysis:
        """Perform complete swing plane analysis.

        Args:
            shaft_positions: Club shaft positions across swing

        Returns:
            Complete analysis with planes, metrics, and deviations
        """
        # Validate input
        if not shaft_positions:
            return SwingPlaneAnalysis(
                planes=SwingPlaneResult(
                    address_plane=None,
                    backswing_plane=None,
                    downswing_plane=None,
                    full_swing_plane=None,
                    impact_position=None,
                    top_position=None
                ),
                metrics=SwingMetrics(
                    attack_angle=0.0,
                    swing_path=0.0,
                    plane_angle=0.0,
                    plane_shift=None,
                    max_deviation=0.0,
                    avg_deviation=0.0,
                    deviation_at_impact=0.0
                ),
                deviations=[],
                success=False,
                error_message="No shaft positions provided"
            )

        try:
            # Detect swing planes
            plane_result = self.detector.detect_swing_planes(shaft_positions)

            # Use downswing plane if available, otherwise full swing
            analysis_plane = (
                plane_result.downswing_plane or
                plane_result.full_swing_plane
            )

            if analysis_plane is None:
                return SwingPlaneAnalysis(
                    planes=plane_result,
                    metrics=SwingMetrics(
                        attack_angle=0.0,
                        swing_path=0.0,
                        plane_angle=0.0,
                        plane_shift=None,
                        max_deviation=0.0,
                        avg_deviation=0.0,
                        deviation_at_impact=0.0
                    ),
                    deviations=[],
                    success=False,
                    error_message="Could not calculate swing plane"
                )

            # Calculate metrics
            metrics = self.metrics_calculator.calculate_swing_metrics(
                shaft_positions=shaft_positions,
                plane=analysis_plane,
                impact_position=plane_result.impact_position,
                plane_shift=plane_result.plane_shift()
            )

            # Calculate deviations for each position
            deviations = [
                self.metrics_calculator.on_plane_deviation(pos, analysis_plane)
                for pos in shaft_positions
            ]

            return SwingPlaneAnalysis(
                planes=plane_result,
                metrics=metrics,
                deviations=deviations,
                success=True
            )

        except Exception as e:
            logger.error(f"Swing plane analysis failed: {e}", exc_info=True)

            return SwingPlaneAnalysis(
                planes=SwingPlaneResult(
                    address_plane=None,
                    backswing_plane=None,
                    downswing_plane=None,
                    full_swing_plane=None,
                    impact_position=None,
                    top_position=None
                ),
                metrics=SwingMetrics(
                    attack_angle=0.0,
                    swing_path=0.0,
                    plane_angle=0.0,
                    plane_shift=None,
                    max_deviation=0.0,
                    avg_deviation=0.0,
                    deviation_at_impact=0.0
                ),
                deviations=[],
                success=False,
                error_message=str(e)
            )

    def analyze_with_plane(
        self,
        shaft_positions: List[ShaftPosition],
        plane: 'Plane3D',
        impact_frame: Optional[int] = None
    ) -> SwingPlaneAnalysis:
        """Analyze swing using a provided plane.

        Useful for comparing to ideal plane or analyzing specific phases.

        Args:
            shaft_positions: Club shaft positions
            plane: Pre-calculated plane to use
            impact_frame: Optional impact frame number

        Returns:
            Analysis using provided plane
        """
        if not shaft_positions:
            return SwingPlaneAnalysis(
                planes=SwingPlaneResult(
                    address_plane=None,
                    backswing_plane=None,
                    downswing_plane=None,
                    full_swing_plane=plane,
                    impact_position=None,
                    top_position=None
                ),
                metrics=SwingMetrics(
                    attack_angle=0.0,
                    swing_path=0.0,
                    plane_angle=0.0,
                    plane_shift=None,
                    max_deviation=0.0,
                    avg_deviation=0.0,
                    deviation_at_impact=0.0
                ),
                deviations=[],
                success=False,
                error_message="No shaft positions provided"
            )

        try:
            # Find impact position
            impact_position = None
            if impact_frame is not None:
                for pos in shaft_positions:
                    if pos.frame_number == impact_frame:
                        impact_position = pos
                        break

            # Use last position if no impact frame specified
            if impact_position is None:
                impact_position = shaft_positions[-1]

            # Calculate metrics
            metrics = self.metrics_calculator.calculate_swing_metrics(
                shaft_positions=shaft_positions,
                plane=plane,
                impact_position=impact_position,
                plane_shift=None
            )

            # Calculate deviations
            deviations = [
                self.metrics_calculator.on_plane_deviation(pos, plane)
                for pos in shaft_positions
            ]

            return SwingPlaneAnalysis(
                planes=SwingPlaneResult(
                    address_plane=None,
                    backswing_plane=None,
                    downswing_plane=None,
                    full_swing_plane=plane,
                    impact_position=impact_position,
                    top_position=None
                ),
                metrics=metrics,
                deviations=deviations,
                success=True
            )

        except Exception as e:
            logger.error(f"Swing plane analysis failed: {e}", exc_info=True)

            return SwingPlaneAnalysis(
                planes=SwingPlaneResult(
                    address_plane=None,
                    backswing_plane=None,
                    downswing_plane=None,
                    full_swing_plane=plane,
                    impact_position=None,
                    top_position=None
                ),
                metrics=SwingMetrics(
                    attack_angle=0.0,
                    swing_path=0.0,
                    plane_angle=0.0,
                    plane_shift=None,
                    max_deviation=0.0,
                    avg_deviation=0.0,
                    deviation_at_impact=0.0
                ),
                deviations=[],
                success=False,
                error_message=str(e)
            )
