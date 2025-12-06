#!/usr/bin/env python3
"""Demo script showing club detection and tracking."""

import sys
import cv2
import numpy as np

from src.detection import ClubDetector, ClubTracker
from src.video import VideoLoader, FrameExtractor


def create_synthetic_test_frames():
    """Create synthetic frames with simulated club movement.

    Returns:
        List of synthetic frames showing club motion
    """
    frames = []

    # Create frames with moving line (simulating club shaft)
    for i in range(20):
        frame = np.zeros((400, 600, 3), dtype=np.uint8)

        # Add some background noise
        noise = np.random.randint(0, 30, frame.shape, dtype=np.uint8)
        frame = cv2.add(frame, noise)

        # Draw club shaft (moving across frames)
        angle = 30 + i * 3  # Gradually changing angle
        x1 = 200 + i * 5
        y1 = 100
        length = 200

        x2 = int(x1 + length * np.cos(np.deg2rad(angle)))
        y2 = int(y1 + length * np.sin(np.deg2rad(angle)))

        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 4)

        # Draw club head
        club_head_x = int(x2 + 10)
        club_head_y = int(y2 + 10)
        cv2.circle(frame, (club_head_x, club_head_y), 20, (255, 255, 255), 2)

        frames.append(frame)

    return frames


def demo_basic_detection():
    """Demonstrate basic club detection on single frame."""
    print("=" * 70)
    print("Golf Swing Analyzer - Club Tracking Demo")
    print("=" * 70)

    print("\n" + "-" * 70)
    print("1. Basic Club Detection")
    print("-" * 70)

    # Create synthetic frame
    frame = np.zeros((400, 600, 3), dtype=np.uint8)

    # Draw club shaft
    cv2.line(frame, (200, 100), (350, 300), (255, 255, 255), 4)

    # Draw club head
    cv2.circle(frame, (360, 310), 20, (255, 255, 255), 2)

    # Initialize detector
    detector = ClubDetector(
        min_line_length=80,
        debug=True
    )

    # Detect club
    result = detector.detect(frame)

    print(f"\nDetection Results:")
    print(f"  Shaft detected: {result.shaft_detected}")

    if result.shaft_detected:
        x1, y1, x2, y2 = result.shaft_line
        print(f"  Shaft endpoints: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"  Shaft angle: {result.shaft_angle:.1f}° from horizontal")
        print(f"  Confidence: {result.confidence:.2f}")

    print(f"  Club head detected: {result.club_head_detected}")

    if result.club_head_detected:
        cx, cy = result.club_head_center
        print(f"  Club head center: ({cx:.0f}, {cy:.0f})")
        print(f"  Club head radius: {result.club_head_radius:.1f} pixels")


def demo_tracking():
    """Demonstrate multi-frame tracking with smoothing."""
    print("\n" + "-" * 70)
    print("2. Multi-Frame Tracking with Smoothing")
    print("-" * 70)

    # Create synthetic frames
    frames = create_synthetic_test_frames()

    # Initialize detector and tracker
    detector = ClubDetector(min_line_length=80)
    tracker = ClubTracker(smoothing_window=3)

    print(f"\nProcessing {len(frames)} synthetic frames...")
    print(f"Smoothing window: {tracker.smoothing_window} frames")

    detections = []
    smoothed_results = []

    for i, frame in enumerate(frames):
        # Detect club
        result = detector.detect(frame)

        # Track and smooth
        smoothed = tracker.update(result)

        detections.append(result)
        smoothed_results.append(smoothed)

        if i % 5 == 0:  # Print every 5th frame
            print(f"\nFrame {i}:")
            print(f"  Raw angle: {result.shaft_angle:.1f}°")
            print(f"  Smoothed angle: {smoothed.shaft_angle:.1f}°")
            print(f"  Confidence: {smoothed.confidence:.2f}")

    # Calculate statistics
    raw_angles = [d.shaft_angle for d in detections if d.shaft_angle is not None]
    smoothed_angles = [
        s.shaft_angle for s in smoothed_results if s.shaft_angle is not None
    ]

    if raw_angles and smoothed_angles:
        # Calculate variance to show smoothing effect
        raw_variance = np.var(np.diff(raw_angles)) if len(raw_angles) > 1 else 0
        smoothed_variance = (
            np.var(np.diff(smoothed_angles)) if len(smoothed_angles) > 1 else 0
        )

        print(f"\nSmoothing Statistics:")
        print(f"  Raw angle variance: {raw_variance:.2f}")
        print(f"  Smoothed angle variance: {smoothed_variance:.2f}")
        print(f"  Variance reduction: {(1 - smoothed_variance/raw_variance)*100:.1f}%")


def demo_occlusion_handling():
    """Demonstrate handling of temporary occlusions."""
    print("\n" + "-" * 70)
    print("3. Occlusion Handling (Gap Interpolation)")
    print("-" * 70)

    detector = ClubDetector()
    tracker = ClubTracker(max_gap_frames=3)

    # Create detections with artificial gap
    print("\nSimulating detection sequence with 2-frame occlusion...")

    # Good detection
    detection1 = detector.detect(np.zeros((400, 600, 3), dtype=np.uint8))
    detection1.shaft_detected = True
    detection1.shaft_line = (200, 100, 350, 300)
    detection1.shaft_angle = 53.1
    detection1.confidence = 0.85

    result1 = tracker.update(detection1)
    print(f"\nFrame 1: ✓ Detected, angle={result1.shaft_angle:.1f}°")

    # Failed detections (occlusion)
    failed = detector.detect(np.zeros((400, 600, 3), dtype=np.uint8))
    failed.shaft_detected = False
    failed.shaft_line = None
    failed.shaft_angle = None
    failed.confidence = 0.0

    result2 = tracker.update(failed)
    print(f"Frame 2: ✗ Occluded -> Interpolated, angle={result2.shaft_angle:.1f}°, "
          f"confidence={result2.confidence:.2f}")

    result3 = tracker.update(failed)
    print(f"Frame 3: ✗ Occluded -> Interpolated, angle={result3.shaft_angle:.1f}°, "
          f"confidence={result3.confidence:.2f}")

    # Detection resumes
    result4 = tracker.update(detection1)
    print(f"Frame 4: ✓ Detected, angle={result4.shaft_angle:.1f}°, "
          f"confidence={result4.confidence:.2f}")

    print("\n  → Tracker successfully interpolated during 2-frame gap")
    print("  → Confidence reduced during interpolation")


def demo_real_video():
    """Demonstrate detection on real video if available."""
    print("\n" + "-" * 70)
    print("4. Real Video Detection (if available)")
    print("-" * 70)

    video_path = "tests/test_data/test_swing.mp4"

    try:
        with VideoLoader(video_path) as video:
            extractor = FrameExtractor(video)

            print(f"\nLoaded video: {video_path}")
            print(f"  Resolution: {video.width}x{video.height}")
            print(f"  Frame count: {video.frame_count}")
            print(f"  FPS: {video.fps}")

            # Initialize detector and tracker
            detector = ClubDetector(
                min_line_length=60,
                min_shaft_angle=20.0,
                max_shaft_angle=160.0
            )
            tracker = ClubTracker(smoothing_window=3)

            # Process every 10th frame
            sample_frames = range(0, min(100, video.frame_count), 10)

            print(f"\nProcessing sample frames: {list(sample_frames)}")

            detected_count = 0

            for frame_num in sample_frames:
                frame = extractor.extract_frame(frame_num)

                # Detect and track
                result = detector.detect(frame)
                smoothed = tracker.update(result)

                if smoothed.shaft_detected:
                    detected_count += 1
                    print(f"  Frame {frame_num}: ✓ angle={smoothed.shaft_angle:.1f}°, "
                          f"conf={smoothed.confidence:.2f}")
                else:
                    print(f"  Frame {frame_num}: ✗ not detected")

            print(f"\nDetection rate: {detected_count}/{len(sample_frames)} "
                  f"({detected_count/len(sample_frames)*100:.0f}%)")

    except FileNotFoundError:
        print(f"\nVideo file not found: {video_path}")
        print("Skipping real video demo.")
    except Exception as e:
        print(f"\nError processing video: {e}")
        print("Skipping real video demo.")


def main():
    """Run all demo sections."""
    demo_basic_detection()
    demo_tracking()
    demo_occlusion_handling()
    demo_real_video()

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
