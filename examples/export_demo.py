"""Demonstration of export functionality.

This script demonstrates:
1. Exporting single frames as images
2. Batch exporting frames with progress tracking
3. Exporting video with rendered overlays
4. Exporting frames from existing video
"""

import sys
import os
import numpy as np
import cv2

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.export import FrameExporter, VideoExporter, BatchExporter, ProgressTracker
from src.visualization import VisualizationEngine, StyleConfig
from src.detection import ClubDetector, FramePreprocessor


def create_demo_frames(count=30, resolution=(640, 480)):
    """Create demo frames with animated content."""
    frames = []
    for i in range(count):
        frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)

        # Draw moving circle
        x = int(100 + (i / count) * 400)
        y = int(240 + 100 * np.sin(i * 0.2))
        cv2.circle(frame, (x, y), 30, (0, 255, 0), -1)

        # Draw frame number
        cv2.putText(
            frame,
            f"Frame {i}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        frames.append(frame)

    return frames


def demo_frame_export():
    """Demo 1: Export single frames as images."""
    print("\n" + "="*60)
    print("DEMO 1: Single Frame Export")
    print("="*60)

    # Create output directory
    output_dir = "output/demo_frames"
    os.makedirs(output_dir, exist_ok=True)

    # Create sample frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(frame, (320, 240), 100, (0, 255, 0), -1)
    cv2.putText(
        frame,
        "Demo Frame",
        (200, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255, 255, 255),
        3
    )

    # Export as different formats
    exporter = FrameExporter()

    # JPEG export
    jpg_path = os.path.join(output_dir, "demo_frame.jpg")
    success = exporter.export_frame(frame, jpg_path, quality=95)
    print(f"Exported JPEG: {jpg_path} - Success: {success}")

    # PNG export
    png_path = os.path.join(output_dir, "demo_frame.png")
    success = exporter.export_frame(frame, png_path, quality=5)
    print(f"Exported PNG: {png_path} - Success: {success}")

    # BMP export
    bmp_path = os.path.join(output_dir, "demo_frame.bmp")
    success = exporter.export_frame(frame, bmp_path)
    print(f"Exported BMP: {bmp_path} - Success: {success}")


def demo_batch_export():
    """Demo 2: Batch export with progress tracking."""
    print("\n" + "="*60)
    print("DEMO 2: Batch Frame Export with Progress")
    print("="*60)

    # Create output directory
    output_dir = "output/demo_batch"
    os.makedirs(output_dir, exist_ok=True)

    # Create demo frames
    print("Creating 30 demo frames...")
    frames = create_demo_frames(30)

    # Progress callback
    def progress_callback(percentage):
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "=" * filled + "-" * (bar_length - filled)
        print(f"\rProgress: [{bar}] {percentage:.1f}%", end="", flush=True)

    # Batch export
    exporter = BatchExporter(
        output_dir,
        filename_template="frame_{:04d}.jpg",
        quality=90
    )

    print("Exporting frames...")
    count = exporter.export_frames(
        frames,
        progress_callback=progress_callback
    )
    print(f"\n\nExported {count}/{len(frames)} frames to {output_dir}")


def demo_video_export():
    """Demo 3: Export video with visualization."""
    print("\n" + "="*60)
    print("DEMO 3: Video Export with Overlays")
    print("="*60)

    # Create output directory
    output_dir = "output/demo_video"
    os.makedirs(output_dir, exist_ok=True)

    # Create demo frames
    print("Creating 60 demo frames...")
    frames = create_demo_frames(60)

    # Add simple overlays directly
    print("Adding text overlays...")
    annotated_frames = []
    for i, frame in enumerate(frames):
        # Copy frame
        annotated = frame.copy()

        # Add text overlays
        cv2.putText(
            annotated,
            f"Time: {i/30:.2f}s",
            (10, 430),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.putText(
            annotated,
            "Demo Video",
            (10, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        annotated_frames.append(annotated)

    # Progress tracking
    def progress_callback(percentage):
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "=" * filled + "-" * (bar_length - filled)
        print(f"\rExporting: [{bar}] {percentage:.1f}%", end="", flush=True)

    # Export video
    output_path = os.path.join(output_dir, "demo_video.avi")

    with VideoExporter(
        output_path,
        fps=30.0,
        resolution=(640, 480),
        codec='MJPEG',
        progress_callback=progress_callback,
        total_frames=len(annotated_frames)
    ) as exporter:
        for frame in annotated_frames:
            exporter.write_frame(frame)

    print(f"\n\nExported video to {output_path}")
    print(f"Frames written: {exporter.get_frames_written()}")


def demo_video_frame_extraction():
    """Demo 4: Extract and export frames from video."""
    print("\n" + "="*60)
    print("DEMO 4: Extract Frames from Video")
    print("="*60)

    # First create a test video
    print("Creating test video...")
    test_video_dir = "output/demo_test_video"
    os.makedirs(test_video_dir, exist_ok=True)
    test_video_path = os.path.join(test_video_dir, "test.mp4")

    frames = create_demo_frames(90)

    # Use MP4V codec for .mp4 files
    with VideoExporter(
        test_video_path,
        fps=30.0,
        resolution=(640, 480),
        codec='MP4V'
    ) as exporter:
        for frame in frames:
            exporter.write_frame(frame)

    print(f"Created test video: {test_video_path}")

    # Now extract specific frames
    print("\nExtracting specific frames...")
    output_dir = "output/demo_extracted"

    exporter = BatchExporter(
        output_dir,
        filename_template="extracted_{:04d}.jpg",
        quality=95
    )

    # Extract every 10th frame
    frame_numbers = [0, 10, 20, 30, 40, 50, 60, 70, 80]

    def progress_callback(percentage):
        print(f"  Progress: {percentage:.0f}%")

    count = exporter.export_video_frames(
        test_video_path,
        frame_numbers=frame_numbers,
        progress_callback=progress_callback
    )

    print(f"\nExtracted {count} frames to {output_dir}")


def demo_progress_tracker():
    """Demo 5: Progress tracker with ETA."""
    print("\n" + "="*60)
    print("DEMO 5: Progress Tracker with ETA")
    print("="*60)

    import time

    total_items = 100
    tracker = ProgressTracker(total_items)

    print(f"Processing {total_items} items...\n")

    for i in range(total_items):
        # Simulate work
        time.sleep(0.02)

        # Update progress
        tracker.update(i + 1)

        # Display progress every 10 items
        if (i + 1) % 10 == 0:
            percentage = tracker.get_percentage()
            eta = tracker.get_eta_string()
            rate = tracker.get_rate()
            elapsed = tracker.get_elapsed_seconds()

            print(f"Items: {i+1}/{total_items}")
            print(f"  Progress: {percentage:.1f}%")
            print(f"  ETA: {eta}")
            print(f"  Rate: {rate:.1f} items/sec")
            print(f"  Elapsed: {elapsed:.1f}s")
            print()

    print("Complete!")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("EXPORT MODULE DEMONSTRATION")
    print("="*60)

    # Run demos
    demo_frame_export()
    demo_batch_export()
    demo_video_export()
    demo_video_frame_extraction()
    demo_progress_tracker()

    print("\n" + "="*60)
    print("All demos complete!")
    print("Output files in: output/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
