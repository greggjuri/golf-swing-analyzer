"""Single frame export to image files."""

import logging
from typing import Optional, Dict, Any

import cv2
import numpy as np

from .utils import validate_output_path, get_image_format

logger = logging.getLogger(__name__)


class FrameExporter:
    """Export single frames as images.

    Supports multiple image formats (JPEG, PNG, BMP) with configurable
    quality and compression settings.

    Example:
        exporter = FrameExporter()

        # Export as JPEG
        exporter.export_frame(frame, "output/frame.jpg", quality=95)

        # Export as PNG
        exporter.export_frame(frame, "output/frame.png", quality=9)
    """

    # Supported image formats
    SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']

    def __init__(self):
        """Initialize frame exporter."""
        logger.info("Initialized FrameExporter")

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
            frame: Frame to export (BGR format from OpenCV)
            output_path: Output file path
            format: Image format - auto-detected from path if None
            quality: JPEG quality (0-100, higher=better) or
                    PNG compression (0-9, higher=more compression)
            metadata: Optional metadata (currently not used)

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If frame is invalid, format unsupported, or quality out of range
        """
        # Validate frame
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")

        if len(frame.shape) not in [2, 3]:
            raise ValueError(
                f"Frame must be 2D or 3D array, got shape {frame.shape}"
            )

        # Validate and prepare output path
        output_path = validate_output_path(output_path, create_dirs=True)

        # Determine format
        if format is None:
            format = get_image_format(output_path)
        else:
            format = format.lower()

        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Validate quality based on format
        if format in ['jpg', 'jpeg']:
            if not (0 <= quality <= 100):
                raise ValueError(f"JPEG quality must be 0-100, got {quality}")
            params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif format == 'png':
            if not (0 <= quality <= 9):
                raise ValueError(f"PNG compression must be 0-9, got {quality}")
            params = [cv2.IMWRITE_PNG_COMPRESSION, quality]
        else:
            params = []

        # Write image
        try:
            success = cv2.imwrite(output_path, frame, params)

            if success:
                logger.info(f"Exported frame to: {output_path}")
                return True
            else:
                logger.error(f"Failed to write frame to: {output_path}")
                return False

        except Exception as e:
            logger.error(f"Error exporting frame: {e}")
            return False

    def export_frame_with_visualization(
        self,
        frame: np.ndarray,
        output_path: str,
        engine,  # VisualizationEngine - avoid circular import
        club_detection=None,
        body_landmarks: Optional[Dict] = None,
        quality: int = 95,
        **render_kwargs
    ) -> bool:
        """Export frame with visualization overlays.

        Args:
            frame: Original frame
            output_path: Output file path
            engine: VisualizationEngine for rendering
            club_detection: Optional club detection result
            body_landmarks: Optional body landmarks
            quality: Image quality
            **render_kwargs: Additional arguments for engine.render()

        Returns:
            True if successful

        Raises:
            ValueError: If inputs are invalid
        """
        # Render overlays
        rendered = engine.render(
            frame,
            club_detection=club_detection,
            body_landmarks=body_landmarks,
            **render_kwargs
        )

        # Export rendered frame
        return self.export_frame(rendered, output_path, quality=quality)
