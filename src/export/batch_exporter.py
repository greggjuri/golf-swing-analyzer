"""Batch export of multiple frames."""

import logging
from typing import List, Optional, Callable
import os

import numpy as np

from .frame_exporter import FrameExporter
from .progress import ProgressTracker

logger = logging.getLogger(__name__)


class BatchExporter:
    """Export multiple frames in batch.

    Exports sequences of frames with numbered filenames and progress tracking.

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
            output_dir: Output directory for frames
            filename_template: Filename template with format placeholder
                             (e.g., "frame_{:04d}.jpg")
            quality: Image quality (0-100 for JPEG, 0-9 for PNG)

        Raises:
            ValueError: If template is invalid
        """
        self.output_dir = output_dir
        self.filename_template = filename_template
        self.quality = quality

        # Validate template has format placeholder
        try:
            self.filename_template.format(0)
        except (KeyError, IndexError):
            raise ValueError(
                f"Filename template must contain format placeholder: "
                f"{filename_template}"
            )

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Frame exporter
        self.frame_exporter = FrameExporter()

        logger.info(f"Initialized BatchExporter: {output_dir}")

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
            progress_callback: Optional progress callback (receives percentage)

        Returns:
            Number of frames exported successfully

        Raises:
            ValueError: If frames list is empty
        """
        if not frames:
            raise ValueError("Frames list is empty")

        tracker = ProgressTracker(len(frames))
        exported_count = 0

        for i, frame in enumerate(frames):
            frame_number = start_index + i
            filename = self.filename_template.format(frame_number)
            output_path = os.path.join(self.output_dir, filename)

            try:
                success = self.frame_exporter.export_frame(
                    frame,
                    output_path,
                    quality=self.quality
                )

                if success:
                    exported_count += 1

            except Exception as e:
                logger.error(f"Error exporting frame {frame_number}: {e}")

            # Update progress
            tracker.update(i + 1, callback=progress_callback)

        logger.info(f"Batch export complete: {exported_count}/{len(frames)} frames")
        return exported_count

    def export_video_frames(
        self,
        video_path: str,
        frame_numbers: Optional[List[int]] = None,
        step: int = 1,
        engine=None,  # VisualizationEngine - avoid circular import
        progress_callback: Optional[Callable[[float], None]] = None,
        **render_kwargs
    ) -> int:
        """Export frames from video file.

        Args:
            video_path: Input video path
            frame_numbers: Specific frames to export (None = all frames with step)
            step: Frame step (export every Nth frame)
            engine: Optional VisualizationEngine for overlays
            progress_callback: Optional progress callback
            **render_kwargs: Arguments for visualization rendering

        Returns:
            Number of frames exported

        Raises:
            ValueError: If video cannot be loaded
            ImportError: If video module not available
        """
        # Import here to avoid circular dependency
        from ..video import VideoLoader, FrameExtractor

        exported_count = 0

        try:
            with VideoLoader(video_path) as video:
                extractor = FrameExtractor(video)
                metadata = video.get_metadata()

                # Determine which frames to export
                if frame_numbers is not None:
                    frames_to_export = frame_numbers
                else:
                    frames_to_export = list(range(0, metadata.frame_count, step))

                tracker = ProgressTracker(len(frames_to_export))

                for i, frame_num in enumerate(frames_to_export):
                    try:
                        # Extract frame
                        frame = extractor.extract_frame(frame_num)

                        # Apply visualization if engine provided
                        if engine is not None:
                            frame = engine.render(frame, **render_kwargs)

                        # Export frame
                        filename = self.filename_template.format(frame_num)
                        output_path = os.path.join(self.output_dir, filename)

                        success = self.frame_exporter.export_frame(
                            frame,
                            output_path,
                            quality=self.quality
                        )

                        if success:
                            exported_count += 1

                    except Exception as e:
                        logger.error(f"Error exporting frame {frame_num}: {e}")

                    # Update progress
                    tracker.update(i + 1, callback=progress_callback)

        except FileNotFoundError:
            raise ValueError(f"Video file not found: {video_path}")

        logger.info(
            f"Video frame export complete: {exported_count}/{len(frames_to_export)} frames"
        )
        return exported_count

    def get_output_path(self, frame_number: int) -> str:
        """Get output path for specific frame number.

        Args:
            frame_number: Frame number

        Returns:
            Full output path for frame
        """
        filename = self.filename_template.format(frame_number)
        return os.path.join(self.output_dir, filename)
