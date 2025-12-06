# PRP: Export Annotated Frames and Videos

## Overview
Implement an export system to save visualized frames as images and render annotated videos with analysis overlays.

## Context
- We have visualization overlays working (club, body, angles, annotations)
- We have video loading and frame extraction
- Need to save analysis results for sharing and review
- Will use OpenCV VideoWriter (already a dependency)

## Requirements

### Functional Requirements
1. **Single Frame Export**
   - Save individual frames as images (JPEG, PNG)
   - Configurable quality/compression
   - Metadata embedding (frame number, timestamp)
   - Multiple image format support

2. **Video Export**
   - Export full videos with overlays
   - Frame-by-frame rendering with visualization
   - Codec selection (H.264, MPEG-4, etc.)
   - Preserve original video resolution and FPS
   - Optional: different output resolution

3. **Batch Frame Export**
   - Export multiple frames as image sequence
   - Filename templates with frame numbers
   - Progress tracking for long exports
   - Parallel processing for performance

4. **Progress Reporting**
   - Callback-based progress updates
   - Percentage complete
   - Estimated time remaining
   - Cancellation support

5. **Quality Control**
   - Configurable compression quality
   - Bitrate control for videos
   - Resolution scaling options
   - Frame rate control

### Non-Functional Requirements
1. **Performance**: Export at 15+ fps for typical video
2. **Quality**: No visual degradation from original
3. **Reliability**: Handle long videos (1000+ frames) without memory issues
4. **Test Coverage**: >85% code coverage
5. **Code Quality**: Pass flake8, mypy validation

## Technical Design

### Module Structure
```
src/export/
├── __init__.py
├── frame_exporter.py    # Single frame export
├── video_exporter.py    # Video export with rendering
├── batch_exporter.py    # Batch frame export
└── progress.py          # Progress tracking utilities
```

### Core Classes

#### 1. FrameExporter
```python
class FrameExporter:
    """Export single frames as images.

    Supports multiple image formats with configurable quality.

    Example:
        exporter = FrameExporter()
        exporter.export_frame(
            frame,
            "output/frame_0100.jpg",
            quality=95
        )
    """

    def export_frame(
        self,
        frame: np.ndarray,
        output_path: str,
        format: Optional[str] = None,
        quality: int = 95,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export single frame to image file.

        Args:
            frame: Frame to export (BGR format)
            output_path: Output file path
            format: Image format ('jpg', 'png', 'bmp') - auto-detected from path if None
            quality: JPEG quality (0-100) or PNG compression (0-9)
            metadata: Optional metadata to embed

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If frame is invalid or format unsupported
        """

    def export_frame_with_visualization(
        self,
        frame: np.ndarray,
        output_path: str,
        engine: VisualizationEngine,
        club_detection: Optional[DetectionResult] = None,
        body_landmarks: Optional[Dict] = None,
        **render_kwargs
    ) -> bool:
        """Export frame with visualization overlays.

        Args:
            frame: Original frame
            output_path: Output file path
            engine: VisualizationEngine for rendering
            club_detection: Optional club detection result
            body_landmarks: Optional body landmarks
            **render_kwargs: Additional arguments for engine.render()

        Returns:
            True if successful
        """
```

#### 2. VideoExporter
```python
class VideoExporter:
    """Export videos with rendered overlays.

    Example:
        exporter = VideoExporter(
            output_path="output/analysis.mp4",
            fps=30.0,
            resolution=(1920, 1080),
            codec='H264'
        )

        with exporter:
            for frame in frames:
                result = engine.render(frame, club_detection=detection)
                exporter.write_frame(result)
    """

    def __init__(
        self,
        output_path: str,
        fps: float,
        resolution: Tuple[int, int],
        codec: str = 'H264',
        bitrate: Optional[int] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        """Initialize video exporter.

        Args:
            output_path: Output video file path
            fps: Frames per second
            resolution: Video resolution (width, height)
            codec: Video codec ('H264', 'MJPEG', 'XVID', etc.)
            bitrate: Optional target bitrate (bps)
            progress_callback: Optional callback for progress updates
        """

    def write_frame(self, frame: np.ndarray):
        """Write single frame to video.

        Args:
            frame: Frame to write (BGR format)

        Raises:
            ValueError: If frame resolution doesn't match
        """

    def __enter__(self):
        """Context manager entry."""

    def __exit__(self, *args):
        """Context manager exit, ensures video is finalized."""
```

#### 3. BatchExporter
```python
class BatchExporter:
    """Export multiple frames in batch.

    Example:
        exporter = BatchExporter(
            output_dir="output/frames",
            filename_template="frame_{:04d}.jpg"
        )

        exporter.export_frames(
            frames,
            progress_callback=lambda p: print(f"{p:.0f}%")
        )
    """

    def __init__(
        self,
        output_dir: str,
        filename_template: str = "frame_{:04d}.jpg",
        quality: int = 95
    ):
        """Initialize batch exporter.

        Args:
            output_dir: Output directory
            filename_template: Filename template with format placeholder
            quality: Image quality (0-100)
        """

    def export_frames(
        self,
        frames: List[np.ndarray],
        start_index: int = 0,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> int:
        """Export multiple frames.

        Args:
            frames: List of frames to export
            start_index: Starting frame number for filenames
            progress_callback: Optional progress callback

        Returns:
            Number of frames exported successfully
        """

    def export_video_frames(
        self,
        video_path: str,
        frame_numbers: Optional[List[int]] = None,
        step: int = 1,
        engine: Optional[VisualizationEngine] = None,
        **render_kwargs
    ) -> int:
        """Export frames from video file.

        Args:
            video_path: Input video path
            frame_numbers: Specific frames to export (None = all frames)
            step: Frame step (export every Nth frame)
            engine: Optional VisualizationEngine for overlays
            **render_kwargs: Arguments for rendering

        Returns:
            Number of frames exported
        """
```

#### 4. Progress Tracking
```python
class ProgressTracker:
    """Track and report export progress.

    Example:
        tracker = ProgressTracker(total_frames=100)

        for i, frame in enumerate(frames):
            export_frame(frame)
            tracker.update(i + 1, callback=lambda p: print(f"{p:.0f}%"))
    """

    def __init__(self, total_items: int):
        """Initialize tracker.

        Args:
            total_items: Total number of items to process
        """

    def update(
        self,
        current: int,
        callback: Optional[Callable[[float], None]] = None
    ):
        """Update progress.

        Args:
            current: Current item count
            callback: Optional callback with percentage (0-100)
        """

    def get_percentage(self) -> float:
        """Get current progress percentage (0-100)."""

    def get_eta_seconds(self) -> Optional[float]:
        """Get estimated time remaining in seconds."""

    def reset(self):
        """Reset progress tracking."""
```

### Helper Functions

```python
def get_codec_fourcc(codec_name: str) -> int:
    """Get OpenCV fourcc code for codec name.

    Args:
        codec_name: Codec name ('H264', 'MJPEG', 'XVID', etc.)

    Returns:
        Fourcc code for cv2.VideoWriter

    Raises:
        ValueError: If codec not supported
    """

def validate_output_path(path: str, create_dirs: bool = True) -> str:
    """Validate and prepare output path.

    Args:
        path: Output file path
        create_dirs: Whether to create parent directories

    Returns:
        Validated absolute path

    Raises:
        ValueError: If path is invalid
    """

def estimate_video_size(
    frame_count: int,
    resolution: Tuple[int, int],
    fps: float,
    codec: str,
    bitrate: Optional[int] = None
) -> int:
    """Estimate output video file size in bytes.

    Args:
        frame_count: Number of frames
        resolution: Video resolution
        fps: Frames per second
        codec: Video codec
        bitrate: Target bitrate (if specified)

    Returns:
        Estimated file size in bytes
    """
```

## Implementation Steps

1. ✅ Create module structure and __init__.py
2. ✅ Implement codec helper functions
3. ✅ Implement FrameExporter class
4. ✅ Implement VideoExporter class
5. ✅ Implement ProgressTracker
6. ✅ Implement BatchExporter class
7. ✅ Write tests for FrameExporter
8. ✅ Write tests for VideoExporter
9. ✅ Write tests for BatchExporter
10. ✅ Write integration tests
11. ✅ Create demo script
12. ✅ Performance testing
13. ✅ Documentation

## Success Criteria

### Must Have
- [x] FrameExporter saves images in JPEG/PNG formats
- [x] VideoExporter creates valid video files
- [x] Progress tracking with callbacks
- [x] Batch export with filename templates
- [x] Test coverage >85%
- [x] All tests pass
- [x] Passes flake8 and mypy validation
- [x] Demo script shows all export capabilities

### Should Have
- [x] Multiple codec support (H.264, MJPEG)
- [x] Quality/compression control
- [x] Resolution scaling
- [x] Error handling for disk space, permissions
- [x] Context manager support for VideoExporter

### Nice to Have
- [ ] Parallel batch export
- [ ] Preview generation (thumbnails)
- [ ] Video metadata embedding
- [ ] Format conversion utilities

## Test Strategy

### Unit Tests
1. **FrameExporter**
   - Test JPEG export with quality settings
   - Test PNG export
   - Test invalid inputs
   - Test with visualization

2. **VideoExporter**
   - Test video creation
   - Test frame writing
   - Test context manager
   - Test codec selection

3. **BatchExporter**
   - Test filename templating
   - Test batch export
   - Test progress callbacks

### Integration Tests
1. Export complete video with club tracking
2. Export frame sequence from video
3. Test with real detection data
4. Verify output file integrity

### Performance Tests
1. Measure export speed (fps)
2. Test with large videos (500+ frames)
3. Verify memory usage stays reasonable

## Dependencies
- OpenCV (cv2) - already in requirements
- NumPy - already in requirements
- src.visualization - for rendering overlays
- src.video - for video loading

## Example Usage
```python
from src.export import FrameExporter, VideoExporter, BatchExporter
from src.visualization import VisualizationEngine
from src.detection import ClubDetector
from src.video import VideoLoader, FrameExtractor

# Export single frame
frame_exporter = FrameExporter()
frame_exporter.export_frame(frame, "output/frame.jpg", quality=95)

# Export video with overlays
detector = ClubDetector()
engine = VisualizationEngine()

with VideoLoader("input.mp4") as video:
    with VideoExporter(
        "output/analysis.mp4",
        fps=video.fps,
        resolution=(video.width, video.height)
    ) as exporter:

        extractor = FrameExtractor(video)

        for i in range(video.frame_count):
            frame = extractor.extract_frame(i)
            detection = detector.detect(frame)
            result = engine.render(frame, club_detection=detection)
            exporter.write_frame(result)

# Batch export frames
batch_exporter = BatchExporter("output/frames")
batch_exporter.export_video_frames(
    "input.mp4",
    step=10,  # Every 10th frame
    engine=engine
)
```

## Risk Assessment
1. **Large video memory usage** - Mitigate with frame-by-frame processing
2. **Codec compatibility** - Provide fallback codecs, clear error messages
3. **Disk space** - Check available space before export
4. **Export speed** - Optimize rendering pipeline, provide progress feedback

## Future Enhancements
- GPU-accelerated encoding
- Cloud export (S3, Google Drive)
- GIF export for highlights
- Video trimming/editing tools
