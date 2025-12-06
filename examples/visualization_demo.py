#!/usr/bin/env python3
"""Demo script showing visualization overlays."""

import numpy as np
import cv2

from src.visualization import (
    VisualizationEngine,
    StyleConfig,
    Annotation,
)
from src.detection import ClubDetector, DetectionResult
from src.analysis import JointAngleCalculator, BodyLandmark
from src.video import VideoLoader, FrameExtractor


def demo_basic_overlays():
    """Demonstrate basic overlay rendering."""
    print("=" * 70)
    print("Golf Swing Analyzer - Visualization Demo")
    print("=" * 70)

    print("\n" + "-" * 70)
    print("1. Basic Club Overlay")
    print("-" * 70)

    # Create synthetic frame
    frame = np.full((400, 600, 3), 50, dtype=np.uint8)

    # Draw a simple background pattern
    cv2.rectangle(frame, (0, 300), (600, 400), (30, 50, 30), -1)  # "Ground"

    # Create synthetic detection result
    detection = DetectionResult(
        shaft_detected=True,
        shaft_line=(250, 150, 350, 320),
        shaft_angle=58.3,
        club_head_detected=True,
        club_head_center=(360, 330),
        club_head_radius=22.0,
        confidence=0.87
    )

    # Initialize engine with default style
    engine = VisualizationEngine()

    # Render overlays
    result = engine.render(
        frame,
        club_detection=detection,
        show_angles=True,
        show_confidence=True
    )

    print(f"\nRendered club overlay:")
    print(f"  Shaft: {detection.shaft_line}")
    print(f"  Angle: {detection.shaft_angle:.1f}°")
    print(f"  Confidence: {detection.confidence:.2f}")

    # Save result
    cv2.imwrite("/tmp/visualization_demo_1_club.jpg", result)
    print(f"  Saved to: /tmp/visualization_demo_1_club.jpg")


def demo_color_schemes():
    """Demonstrate different color schemes."""
    print("\n" + "-" * 70)
    print("2. Color Schemes")
    print("-" * 70)

    # Create frame with club
    frame = np.full((400, 600, 3), 50, dtype=np.uint8)
    cv2.rectangle(frame, (0, 300), (600, 400), (30, 50, 30), -1)

    detection = DetectionResult(
        shaft_detected=True,
        shaft_line=(250, 150, 350, 320),
        shaft_angle=58.3,
        club_head_detected=True,
        club_head_center=(360, 330),
        club_head_radius=22.0,
        confidence=0.87
    )

    # Test different styles
    styles = [
        ("Default", StyleConfig()),
        ("High Contrast", StyleConfig.high_contrast()),
        ("Colorblind Friendly", StyleConfig.colorblind_friendly()),
        ("Minimal", StyleConfig.minimal()),
    ]

    for name, style in styles:
        engine = VisualizationEngine(style=style)
        result = engine.render(frame, club_detection=detection)

        filename = f"/tmp/visualization_demo_2_{name.lower().replace(' ', '_')}.jpg"
        cv2.imwrite(filename, result)
        print(f"  {name}: {filename}")


def demo_body_landmarks():
    """Demonstrate body skeleton rendering."""
    print("\n" + "-" * 70)
    print("3. Body Skeleton and Joint Angles")
    print("-" * 70)

    # Create frame
    frame = np.full((500, 400, 3), 50, dtype=np.uint8)

    # Create synthetic body landmarks (simple golf address pose)
    landmarks = {
        # Upper body
        BodyLandmark.LEFT_SHOULDER: (180, 150),
        BodyLandmark.RIGHT_SHOULDER: (220, 150),
        BodyLandmark.LEFT_ELBOW: (160, 200),
        BodyLandmark.RIGHT_ELBOW: (240, 200),
        BodyLandmark.LEFT_WRIST: (155, 250),
        BodyLandmark.RIGHT_WRIST: (245, 250),
        # Lower body
        BodyLandmark.LEFT_HIP: (185, 250),
        BodyLandmark.RIGHT_HIP: (215, 250),
        BodyLandmark.LEFT_KNEE: (190, 350),
        BodyLandmark.RIGHT_KNEE: (210, 350),
        BodyLandmark.LEFT_ANKLE: (193, 450),
        BodyLandmark.RIGHT_ANKLE: (207, 450),
    }

    # Initialize engine and calculator
    engine = VisualizationEngine(style=StyleConfig.high_contrast())
    joint_calc = JointAngleCalculator(handedness="right")

    # Render skeleton and angles
    result = engine.render(
        frame,
        body_landmarks=landmarks,
        joint_calculator=joint_calc,
        show_skeleton=True,
        show_angles=True
    )

    cv2.imwrite("/tmp/visualization_demo_3_body.jpg", result)
    print(f"  Rendered skeleton with {len(landmarks)} landmarks")
    print(f"  Saved to: /tmp/visualization_demo_3_body.jpg")


def demo_annotations():
    """Demonstrate text annotations."""
    print("\n" + "-" * 70)
    print("4. Text Annotations")
    print("-" * 70)

    # Create frame
    frame = np.full((400, 600, 3), 50, dtype=np.uint8)

    # Create annotations
    annotations = [
        Annotation(
            text="Address Position",
            position=(50, 50),
            alignment='left'
        ),
        Annotation(
            text="Frame 100 | 3.33s",
            position=(550, 50),
            alignment='right',
            font_scale=0.5
        ),
        Annotation(
            text="Good Setup!",
            position=(300, 200),
            alignment='center',
            color=(0, 255, 0),  # Green
            font_scale=1.0
        ),
        Annotation(
            text="Knee flex: 145°",
            position=(50, 350),
            background=True
        ),
        Annotation(
            text="Confidence: 0.92",
            position=(50, 380),
            color=(255, 255, 0)  # Cyan
        ),
    ]

    engine = VisualizationEngine()
    result = engine.render(frame, annotations=annotations)

    cv2.imwrite("/tmp/visualization_demo_4_annotations.jpg", result)
    print(f"  Rendered {len(annotations)} annotations")
    print(f"  Saved to: /tmp/visualization_demo_4_annotations.jpg")


def demo_complete_scene():
    """Demonstrate complete visualization with all elements."""
    print("\n" + "-" * 70)
    print("5. Complete Scene")
    print("-" * 70)

    # Create frame with background
    frame = np.full((500, 600, 3), 50, dtype=np.uint8)
    cv2.rectangle(frame, (0, 350), (600, 500), (30, 50, 30), -1)  # Ground

    # Club detection
    detection = DetectionResult(
        shaft_detected=True,
        shaft_line=(280, 200, 360, 340),
        shaft_angle=62.5,
        club_head_detected=True,
        club_head_center=(368, 348),
        club_head_radius=20.0,
        confidence=0.91
    )

    # Body landmarks
    landmarks = {
        BodyLandmark.LEFT_SHOULDER: (250, 180),
        BodyLandmark.RIGHT_SHOULDER: (290, 180),
        BodyLandmark.LEFT_ELBOW: (230, 230),
        BodyLandmark.LEFT_WRIST: (270, 280),
        BodyLandmark.LEFT_HIP: (255, 280),
        BodyLandmark.RIGHT_HIP: (285, 280),
        BodyLandmark.LEFT_KNEE: (260, 360),
        BodyLandmark.RIGHT_KNEE: (280, 360),
        BodyLandmark.LEFT_ANKLE: (263, 440),
        BodyLandmark.RIGHT_ANKLE: (277, 440),
    }

    # Annotations
    annotations = [
        Annotation(
            text="Backswing (P4)",
            position=(300, 30),
            alignment='center',
            font_scale=0.8
        ),
    ]

    # Render everything
    engine = VisualizationEngine(style=StyleConfig.high_contrast())
    joint_calc = JointAngleCalculator()

    result = engine.render(
        frame,
        club_detection=detection,
        body_landmarks=landmarks,
        joint_calculator=joint_calc,
        annotations=annotations,
        show_angles=True,
        show_confidence=True,
        show_skeleton=True
    )

    # Add frame info
    result = engine.render_frame_info(result, frame_number=75, fps=30.0)

    cv2.imwrite("/tmp/visualization_demo_5_complete.jpg", result)
    print(f"  Rendered complete scene with:")
    print(f"    - Club detection (shaft + head)")
    print(f"    - Body skeleton ({len(landmarks)} landmarks)")
    print(f"    - Joint angles")
    print(f"    - Text annotations")
    print(f"    - Frame info")
    print(f"  Saved to: /tmp/visualization_demo_5_complete.jpg")


def demo_real_video():
    """Demonstrate visualization on real video frames."""
    print("\n" + "-" * 70)
    print("6. Real Video Visualization")
    print("-" * 70)

    video_path = "tests/test_data/test_swing.mp4"

    try:
        with VideoLoader(video_path) as video:
            extractor = FrameExtractor(video)

            print(f"\nProcessing: {video_path}")
            print(f"  Frames: {video.frame_count}")
            print(f"  FPS: {video.fps}")

            # Initialize components
            detector = ClubDetector(min_line_length=60)
            engine = VisualizationEngine(style=StyleConfig.high_contrast())

            # Process a few frames
            sample_frames = [50, 75, 100]

            for frame_num in sample_frames:
                if frame_num >= video.frame_count:
                    continue

                frame = extractor.extract_frame(frame_num)

                # Detect club
                detection = detector.detect(frame)

                # Render overlays
                result = engine.render(
                    frame,
                    club_detection=detection,
                    show_angles=True,
                    show_confidence=True
                )

                # Add frame info
                result = engine.render_frame_info(result, frame_num, video.fps)

                filename = f"/tmp/visualization_demo_6_frame_{frame_num}.jpg"
                cv2.imwrite(filename, result)

                if detection.shaft_detected:
                    print(f"  Frame {frame_num}: ✓ detected "
                          f"(angle={detection.shaft_angle:.1f}°) -> {filename}")
                else:
                    print(f"  Frame {frame_num}: ✗ not detected -> {filename}")

    except FileNotFoundError:
        print(f"\n  Video file not found: {video_path}")
        print("  Skipping real video demo.")
    except Exception as e:
        print(f"\n  Error: {e}")
        print("  Skipping real video demo.")


def main():
    """Run all demo sections."""
    demo_basic_overlays()
    demo_color_schemes()
    demo_body_landmarks()
    demo_annotations()
    demo_complete_scene()
    demo_real_video()

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("Check /tmp/ for output images")
    print("=" * 70)


if __name__ == "__main__":
    main()
