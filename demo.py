#!/usr/bin/env python3
"""Demo script showing video loading and frame extraction features."""

from pathlib import Path
from src.video import VideoLoader, FrameExtractor, KeyPositionDetector


def main():
    """Run demo of video loading and frame extraction."""
    print("=" * 70)
    print("Golf Swing Analyzer - Video Loading Demo")
    print("=" * 70)

    # Use test video
    video_path = Path("tests/test_data/test_swing.mp4")

    if not video_path.exists():
        print(f"\nError: Test video not found at {video_path}")
        print("Run: python tests/create_test_video.py")
        return

    print(f"\nLoading video: {video_path}")

    with VideoLoader(str(video_path)) as loader:
        # Get and display metadata
        meta = loader.get_metadata()
        print("\nVideo Metadata:")
        print(f"  Resolution: {meta.width}x{meta.height}")
        print(f"  FPS: {meta.fps}")
        print(f"  Frame Count: {meta.frame_count}")
        print(f"  Duration: {meta.duration:.2f} seconds")
        print(f"  Codec: {meta.codec}")

        # Test frame extraction
        print("\n" + "-" * 70)
        print("Testing Frame Extraction")
        print("-" * 70)

        extractor = FrameExtractor(loader, cache_size=50, default_scale=1.0)

        # Extract single frame
        print("\nExtracting frame 0...")
        frame = extractor.extract_frame(0)
        print(f"  Frame shape: {frame.shape}")
        print(f"  Frame dtype: {frame.dtype}")

        # Extract with different scales
        print("\nExtracting frame 10 at different scales:")
        for scale in [1.0, 0.5, 0.25]:
            frame_scaled = extractor.extract_frame(10, scale=scale)
            print(f"  Scale {scale}x: {frame_scaled.shape}")

        # Extract range
        print("\nExtracting frames 0-20 (every 5th frame)...")
        frames = extractor.extract_range(0, 20, step=5)
        print(f"  Extracted {len(frames)} frames")

        # Cache statistics
        stats = extractor.get_cache_stats()
        print(f"\nCache Statistics:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Size: {stats['size']}")
        if stats['hits'] + stats['misses'] > 0:
            hit_rate = stats['hits'] / (stats['hits'] + stats['misses']) * 100
            print(f"  Hit Rate: {hit_rate:.1f}%")

        # Key position detection
        print("\n" + "-" * 70)
        print("Testing Key Position Detection")
        print("-" * 70)

        detector = KeyPositionDetector(loader)
        print("\nDetecting key swing positions...")
        positions = detector.detect_positions(downsample_factor=4)

        print("\nDetected Positions:")
        for pos_name, frame_num in sorted(positions.items()):
            timestamp = frame_num / meta.fps
            print(f"  {pos_name}: Frame {frame_num} ({timestamp:.2f}s)")

        # Verify ordering
        print("\nPosition Order Validation:")
        if positions['P1'] <= positions['P4'] <= positions['P7']:
            print("  ✓ Positions are in correct chronological order")
        else:
            print("  ✗ Warning: Positions may not be in correct order")

        # Extract frames at key positions
        print("\nExtracting frames at key positions...")
        for pos_name in ['P1', 'P4', 'P7']:
            frame_num = positions[pos_name]
            key_frame = extractor.extract_frame(frame_num, scale=0.5)
            print(f"  {pos_name} (frame {frame_num}): {key_frame.shape}")

        # Final cache stats
        final_stats = extractor.get_cache_stats()
        print(f"\nFinal Cache Statistics:")
        print(f"  Total Accesses: {final_stats['hits'] + final_stats['misses']}")
        print(f"  Cache Size: {final_stats['size']}")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
