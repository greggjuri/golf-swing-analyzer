"""Export module for saving annotated frames and videos.

This module provides tools to export analysis results as images and videos
with visualization overlays.

Main classes:
    FrameExporter: Export single frames as images
    VideoExporter: Export videos with rendered overlays
    BatchExporter: Batch export multiple frames
    ProgressTracker: Track export progress

Example:
    from src.export import FrameExporter, VideoExporter

    # Export single frame
    frame_exporter = FrameExporter()
    frame_exporter.export_frame(frame, "output.jpg", quality=95)

    # Export video
    with VideoExporter("output.mp4", fps=30, resolution=(1920, 1080)) as exporter:
        for frame in frames:
            exporter.write_frame(frame)
"""

from .frame_exporter import FrameExporter
from .video_exporter import VideoExporter
from .batch_exporter import BatchExporter
from .progress import ProgressTracker

__all__ = [
    'FrameExporter',
    'VideoExporter',
    'BatchExporter',
    'ProgressTracker',
]
