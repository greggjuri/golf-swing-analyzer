#!/usr/bin/env python3
"""Demo script showing angle calculation utilities."""

from src.analysis import (
    angle_between_points,
    angle_from_horizontal,
    angle_from_vertical,
    normalize_angle,
    distance_between_points,
    JointAngleCalculator,
    ClubAngleCalculator,
    BodyLandmark,
)


def main():
    """Run angle calculation demonstrations."""
    print("=" * 70)
    print("Golf Swing Analyzer - Angle Calculation Demo")
    print("=" * 70)

    # Demo 1: Basic angle calculations
    print("\n" + "-" * 70)
    print("1. Basic Angle Calculations")
    print("-" * 70)

    # Calculate angle between three points
    p1 = (0, 0)
    vertex = (1, 0)
    p2 = (1, 1)
    angle = angle_between_points(p1, vertex, p2)
    print(f"\nAngle between points {p1}, {vertex}, {p2}: {angle:.1f}°")

    # Calculate distance
    dist = distance_between_points(p1, p2)
    print(f"Distance from {p1} to {p2}: {dist:.2f} pixels")

    # Angle from horizontal
    line_start = (100, 100)
    line_end = (150, 75)
    horiz_angle = angle_from_horizontal(line_start, line_end)
    print(f"\nAngle from horizontal: {horiz_angle:.1f}°")

    # Angle from vertical
    vert_angle = angle_from_vertical(line_start, line_end)
    print(f"Angle from vertical: {vert_angle:.1f}°")

    # Angle normalization
    print(f"\nNormalizing 450° to [0-360]: {normalize_angle(450, '0-360'):.1f}°")
    print(f"Normalizing 270° to [-180-180]: {normalize_angle(270, '-180-180'):.1f}°")

    # Demo 2: Joint angle calculations
    print("\n" + "-" * 70)
    print("2. Joint Angle Calculations")
    print("-" * 70)

    joint_calc = JointAngleCalculator(handedness="right")
    print(f"\nInitialized for right-handed golfer")

    # Simulate detected body landmarks (in pixel coordinates)
    shoulder = (300, 150)
    elbow = (350, 250)
    wrist = (380, 280)

    elbow_angle = joint_calc.elbow_angle(shoulder, elbow, wrist)
    print(f"\nElbow angle: {elbow_angle:.1f}°")
    print(f"  (180° = full extension, <180° = flexion)")

    # Knee angle at address
    hip = (320, 200)
    knee = (335, 300)
    ankle = (340, 400)

    knee_angle = joint_calc.knee_angle(hip, knee, ankle)
    print(f"\nKnee flex angle: {knee_angle:.1f}°")

    # Check if in typical range
    ranges = joint_calc.get_typical_ranges()
    min_knee, max_knee = ranges['knee_flex_address']
    if min_knee <= knee_angle <= max_knee:
        print(f"  ✓ Within typical range ({min_knee:.0f}°-{max_knee:.0f}°)")
    else:
        print(f"  ✗ Outside typical range ({min_knee:.0f}°-{max_knee:.0f}°)")

    # Spine angle
    shoulder_mid = (300, 150)
    hip_mid = (310, 200)

    spine_tilt = joint_calc.spine_angle(shoulder_mid, hip_mid)
    print(f"\nSpine tilt: {spine_tilt:.1f}° from vertical")

    # Wrist hinge
    club_grip = (400, 300)
    wrist_hinge = joint_calc.wrist_hinge_angle(elbow, wrist, club_grip)
    print(f"\nWrist hinge angle: {wrist_hinge:.1f}°")
    print(f"  (90° = maximum hinge)")

    # Show typical ranges
    print("\nTypical Ranges for Golf Swing:")
    print(f"  Knee flex at address: {ranges['knee_flex_address']}")
    print(f"  Spine tilt at address: {ranges['spine_tilt_address']}")
    print(f"  Wrist hinge at top: {ranges['wrist_hinge_top']}")

    # Demo 3: Club angle calculations
    print("\n" + "-" * 70)
    print("3. Club Angle Calculations")
    print("-" * 70)

    club_calc = ClubAngleCalculator()

    # Club shaft angle at address
    grip = (380, 280)
    club_head = (420, 380)

    shaft_to_ground = club_calc.shaft_angle_to_ground(grip, club_head)
    print(f"\nShaft angle to ground: {shaft_to_ground:.1f}°")
    print(f"  (Typical 7-iron: ~65°)")

    shaft_to_vertical = club_calc.shaft_angle_to_vertical(grip, club_head)
    print(f"Shaft angle from vertical: {shaft_to_vertical:.1f}°")

    # Shaft angle to target line
    target_line = ((0, 350), (500, 350))  # Horizontal target line
    target_angle = club_calc.shaft_angle_to_target_line(
        grip, club_head, target_line
    )
    print(f"Shaft angle to target: {target_angle:.1f}°")

    # Swing plane angle
    ball = (450, 400)
    hands_address = (400, 300)
    hands_top = (350, 200)

    plane_angle = club_calc.swing_plane_angle(
        hands_address, hands_top, ball
    )
    print(f"\nSwing plane angle: {plane_angle:.1f}°")
    print(f"  (Typical range: 45°-60°)")

    # Demo 4: Body landmark constants
    print("\n" + "-" * 70)
    print("4. Body Landmark Indices (for pose detection)")
    print("-" * 70)

    print(f"\nLeft shoulder index: {BodyLandmark.LEFT_SHOULDER}")
    print(f"Right shoulder index: {BodyLandmark.RIGHT_SHOULDER}")
    print(f"Left elbow index: {BodyLandmark.LEFT_ELBOW}")
    print(f"Left wrist index: {BodyLandmark.LEFT_WRIST}")
    print(f"Left knee index: {BodyLandmark.LEFT_KNEE}")
    print(f"Left ankle index: {BodyLandmark.LEFT_ANKLE}")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
