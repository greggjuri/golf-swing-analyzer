"""Create synthetic test video for testing video loading functionality."""

import cv2
import numpy as np
from pathlib import Path


def create_test_video(
    output_path: str,
    fps: int = 30,
    duration: int = 5,
    width: int = 640,
    height: int = 480
) -> None:
    """Create a test video with moving circle to simulate motion.

    Args:
        output_path: Path where video will be saved
        fps: Frames per second
        duration: Video duration in seconds
        width: Frame width in pixels
        height: Frame height in pixels
    """
    frame_count = fps * duration
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for i in range(frame_count):
        # Create blank frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Simulate motion with moving circle (simulates golf swing motion)
        # Phase 1 (0-30%): Slow motion (address)
        # Phase 2 (30-50%): Fast motion (backswing)
        # Phase 3 (50-70%): Very fast motion (downswing/impact)
        # Phase 4 (70-100%): Slower motion (follow-through)

        progress = i / frame_count

        if progress < 0.3:
            # Address - minimal motion
            x = int(320 + 10 * np.sin(2 * np.pi * i / frame_count))
            radius = 30
            color = (100, 100, 100)
        elif progress < 0.5:
            # Backswing - moderate motion
            phase = (progress - 0.3) / 0.2
            x = int(320 + 150 * phase)
            radius = 30
            color = (150, 150, 150)
        elif progress < 0.7:
            # Downswing/impact - high motion
            phase = (progress - 0.5) / 0.2
            x = int(470 - 300 * phase)
            radius = 35
            color = (255, 255, 255)
        else:
            # Follow-through - decreasing motion
            phase = (progress - 0.7) / 0.3
            x = int(170 + 50 * phase)
            radius = 30
            color = (200, 200, 200)

        y = 240

        # Draw circle
        cv2.circle(frame, (x, y), radius, color, -1)

        # Add frame number for debugging
        cv2.putText(
            frame,
            f"Frame {i}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        out.write(frame)

    out.release()
    print(f"Created test video: {output_path}")
    print(f"  FPS: {fps}, Duration: {duration}s, Frames: {frame_count}")
    print(f"  Resolution: {width}x{height}")


if __name__ == "__main__":
    # Create test data directory
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)

    # Create test video
    video_path = test_data_dir / "test_swing.mp4"
    create_test_video(str(video_path))
