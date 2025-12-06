#!/usr/bin/env python3
"""Demonstration of swing plane analysis functionality.

This script demonstrates the complete swing plane analysis pipeline:
1. Creating synthetic swing data
2. Detecting swing planes
3. Calculating metrics
4. Analyzing deviations

Run with: python examples/plane_demo.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.plane import (
    Point3D,
    Plane3D,
    SwingPlaneAnalyzer,
    ShaftPosition,
    PlaneCalculator,
    PlaneDetector,
    PlaneMetrics
)


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_basic_plane_fitting():
    """Demonstrate basic plane fitting from points."""
    print_header("Demo 1: Basic Plane Fitting")

    from src.plane.geometry import fit_plane_svd

    # Create points on a tilted plane
    points = [
        Point3D(0, 0, 0),
        Point3D(1, 0.5, 0),
        Point3D(0, 0, 1),
        Point3D(1, 0.5, 1),
        Point3D(0.5, 0.25, 0.5)
    ]

    print("Points to fit:")
    for i, p in enumerate(points):
        print(f"  Point {i+1}: ({p.x:.2f}, {p.y:.2f}, {p.z:.2f})")

    # Fit plane
    plane = fit_plane_svd(points)
    print(f"\nFitted plane equation: {plane.a:.3f}x + {plane.b:.3f}y + "
          f"{plane.c:.3f}z + {plane.d:.3f} = 0")
    print(f"Plane angle from horizontal: {plane.angle_to_horizontal():.1f}°")

    # Calculate deviations
    print("\nPoint deviations from plane:")
    for i, p in enumerate(points):
        dev = abs(plane.point_distance(p))
        print(f"  Point {i+1}: {dev:.4f}")


def demo_shaft_positions():
    """Demonstrate creating and analyzing shaft positions."""
    print_header("Demo 2: Shaft Positions and Plane Calculation")

    # Create shaft positions for a simple swing
    positions = []
    for i in range(20):
        t = i * 0.1
        # Shaft moving along tilted plane
        base = Point3D(t, 0.5 + t * 0.1, 0.3)
        tip = Point3D(t + 0.3, 0.5 + t * 0.1 + 0.05, 0.3)

        positions.append(ShaftPosition(
            frame_number=i,
            base_point=base,
            tip_point=tip,
            timestamp=i / 30.0
        ))

    print(f"Created {len(positions)} shaft positions")
    print(f"First position: frame {positions[0].frame_number}, "
          f"base ({positions[0].base_point.x:.2f}, {positions[0].base_point.y:.2f})")
    print(f"Last position: frame {positions[-1].frame_number}, "
          f"base ({positions[-1].base_point.x:.2f}, {positions[-1].base_point.y:.2f})")

    # Calculate plane
    calculator = PlaneCalculator()
    plane = calculator.calculate_plane(positions)

    print(f"\nCalculated swing plane:")
    print(f"  Equation: {plane.a:.3f}x + {plane.b:.3f}y + "
          f"{plane.c:.3f}z + {plane.d:.3f} = 0")
    print(f"  Angle from horizontal: {plane.angle_to_horizontal():.1f}°")

    # Calculate deviations
    deviations = [abs(plane.point_distance(pos.midpoint())) for pos in positions]
    print(f"\nDeviation statistics:")
    print(f"  Maximum: {max(deviations):.4f}")
    print(f"  Average: {sum(deviations) / len(deviations):.4f}")


def demo_full_swing_analysis():
    """Demonstrate complete swing analysis with phases."""
    print_header("Demo 3: Full Swing Analysis with Phases")

    # Create realistic full swing
    positions = []

    # Backswing (rising)
    print("Creating backswing positions...")
    for i in range(15):
        y = 0.8 - i * 0.05  # Rising (y decreasing in screen coords)
        base = Point3D(0.5, y, 0.2)
        tip = Point3D(0.8, y - 0.1, 0.2)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Downswing (falling)
    print("Creating downswing positions...")
    for i in range(15, 30):
        y = (i - 15) * 0.05  # Falling (y increasing)
        base = Point3D(0.5, y, 0.2)
        tip = Point3D(0.8, y + 0.1, 0.2)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Analyze with detector
    detector = PlaneDetector()
    result = detector.detect_swing_planes(positions)

    print(f"\nSwing phase detection:")
    print(f"  Full swing plane: {'✓' if result.full_swing_plane else '✗'}")
    print(f"  Backswing plane: {'✓' if result.backswing_plane else '✗'}")
    print(f"  Downswing plane: {'✓' if result.downswing_plane else '✗'}")
    print(f"  Address plane: {'✓' if result.address_plane else '✗'}")

    if result.top_position:
        print(f"\n  Top position: frame {result.top_position.frame_number}")

    if result.impact_position:
        print(f"  Impact position: frame {result.impact_position.frame_number}")

    if result.plane_shift():
        print(f"\n  Plane shift (backswing→downswing): {result.plane_shift():.1f}°")


def demo_metrics_calculation():
    """Demonstrate swing metrics calculation."""
    print_header("Demo 4: Swing Metrics Calculation")

    # Create downswing positions
    positions = []
    for i in range(20):
        t = i * 0.1
        base = Point3D(t, 0.5 + t * 0.08, 0.3)
        tip = Point3D(t + 0.3, 0.5 + t * 0.08 + 0.05, 0.3)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Fit plane
    calculator = PlaneCalculator()
    plane = calculator.calculate_plane(positions)

    # Calculate metrics
    metrics_calc = PlaneMetrics()
    impact_position = positions[-1]

    attack = metrics_calc.attack_angle(impact_position, plane)
    path = metrics_calc.swing_path(impact_position)
    angle = metrics_calc.plane_angle(plane)

    print("Swing metrics:")
    print(f"  Attack angle: {attack:.1f}°")
    print(f"  Swing path: {path:.1f}°")
    print(f"  Plane angle: {angle:.1f}°")

    # Calculate all deviations
    deviations = [
        metrics_calc.on_plane_deviation(pos, plane)
        for pos in positions
    ]

    print(f"\nDeviation analysis:")
    print(f"  Maximum deviation: {max(deviations):.3f}")
    print(f"  Average deviation: {sum(deviations) / len(deviations):.3f}")
    print(f"  At impact: {deviations[-1]:.3f}")


def demo_complete_analyzer():
    """Demonstrate the high-level analyzer interface."""
    print_header("Demo 5: Complete SwingPlaneAnalyzer")

    # Create realistic swing
    positions = []

    # Backswing
    for i in range(12):
        y = 0.9 - i * 0.06
        base = Point3D(0.4, y, 0.2)
        tip = Point3D(0.7, y - 0.12, 0.2)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Top
    positions.append(ShaftPosition(
        12, Point3D(0.4, 0.2, 0.2), Point3D(0.7, 0.08, 0.2), 12 / 30.0
    ))

    # Downswing
    for i in range(13, 25):
        y = (i - 13) * 0.06
        base = Point3D(0.4, y, 0.2)
        tip = Point3D(0.7, y + 0.12, 0.2)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    # Analyze
    analyzer = SwingPlaneAnalyzer()
    result = analyzer.analyze(positions)

    if result.success:
        print("Analysis successful!\n")

        print("Detected planes:")
        print(f"  Full swing: {'✓' if result.planes.full_swing_plane else '✗'}")
        print(f"  Backswing: {'✓' if result.planes.backswing_plane else '✗'}")
        print(f"  Downswing: {'✓' if result.planes.downswing_plane else '✗'}")

        print(f"\nKey positions:")
        if result.planes.top_position:
            print(f"  Top: frame {result.planes.top_position.frame_number}")
        if result.planes.impact_position:
            print(f"  Impact: frame {result.planes.impact_position.frame_number}")

        print(f"\nMetrics:")
        print(f"  Attack angle: {result.metrics.attack_angle:.1f}°")
        print(f"  Swing path: {result.metrics.swing_path:.1f}°")
        print(f"  Plane angle: {result.metrics.plane_angle:.1f}°")

        if result.metrics.plane_shift:
            print(f"  Plane shift: {result.metrics.plane_shift:.1f}°")

        print(f"\nDeviations:")
        print(f"  Maximum: {result.metrics.max_deviation:.3f}")
        print(f"  Average: {result.metrics.avg_deviation:.3f}")
        print(f"  At impact: {result.metrics.deviation_at_impact:.3f}")

    else:
        print(f"Analysis failed: {result.error_message}")


def demo_compare_to_ideal():
    """Demonstrate comparing swing to ideal plane."""
    print_header("Demo 6: Compare Swing to Ideal Plane")

    # Create swing with slight deviations
    positions = []
    for i in range(20):
        t = i * 0.1
        # Add small random-like deviations
        deviation = 0.05 if i % 3 == 0 else 0.0

        base = Point3D(t, 0.5 + deviation, 0)
        tip = Point3D(t + 0.3, 0.5 + deviation, 0)
        positions.append(ShaftPosition(i, base, tip, i / 30.0))

    analyzer = SwingPlaneAnalyzer()

    # Analyze actual swing
    actual = analyzer.analyze(positions)

    # Compare to ideal horizontal plane
    ideal_plane = Plane3D(0, 1, 0, -0.5)
    ideal = analyzer.analyze_with_plane(positions, ideal_plane)

    print("Actual swing vs Ideal plane comparison:\n")

    print("Actual swing:")
    print(f"  Plane angle: {actual.metrics.plane_angle:.1f}°")
    print(f"  Average deviation: {actual.metrics.avg_deviation:.3f}")
    print(f"  Maximum deviation: {actual.metrics.max_deviation:.3f}")

    print("\nDeviation from ideal:")
    print(f"  Average: {ideal.metrics.avg_deviation:.3f}")
    print(f"  Maximum: {ideal.metrics.max_deviation:.3f}")

    improvement_pct = (
        (ideal.metrics.avg_deviation - actual.metrics.avg_deviation) /
        ideal.metrics.avg_deviation * 100
    )
    print(f"\nActual swing is {improvement_pct:.1f}% closer to ideal than deviations")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("  SWING PLANE ANALYSIS DEMONSTRATION")
    print("="*70)

    try:
        demo_basic_plane_fitting()
        demo_shaft_positions()
        demo_full_swing_analysis()
        demo_metrics_calculation()
        demo_complete_analyzer()
        demo_compare_to_ideal()

        print_header("All Demos Complete!")
        print("The swing plane analysis system is fully functional.")
        print("See the PRP at PRPs/swing-plane-analysis.md for full documentation.\n")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
