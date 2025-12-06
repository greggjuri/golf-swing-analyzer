"""Main visualization engine coordinating all renderers."""

import logging
from typing import Optional, Dict, List

import numpy as np

from ..analysis import Point2D, JointAngleCalculator
from ..detection import DetectionResult
from .styles import StyleConfig, Annotation
from .renderers import ClubRenderer, BodyRenderer, AngleRenderer
from .utils import draw_text_with_background

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """Main engine for rendering overlays on frames.

    Coordinates multiple renderers and applies overlays to frames.

    Example:
        engine = VisualizationEngine(style=StyleConfig.high_contrast())

        result_frame = engine.render(
            frame,
            club_detection=club_result,
            show_angles=True,
            show_confidence=True
        )
    """

    def __init__(
        self,
        style: Optional[StyleConfig] = None,
        handedness: str = "right"
    ):
        """Initialize visualization engine.

        Args:
            style: Optional style configuration (uses default if None)
            handedness: Golfer handedness for body rendering ("right" or "left")
        """
        self.style = style if style is not None else StyleConfig()
        self.handedness = handedness

        # Initialize renderers
        self.club_renderer = ClubRenderer(self.style)
        self.angle_renderer = AngleRenderer(self.style)
        self.body_renderer = BodyRenderer(self.style, handedness)

        logger.info(f"Initialized VisualizationEngine with {handedness}-handed config")

    def render(
        self,
        frame: np.ndarray,
        club_detection: Optional[DetectionResult] = None,
        body_landmarks: Optional[Dict[int, Point2D]] = None,
        joint_calculator: Optional[JointAngleCalculator] = None,
        annotations: Optional[List[Annotation]] = None,
        show_angles: bool = True,
        show_confidence: bool = True,
        show_skeleton: bool = True
    ) -> np.ndarray:
        """Render all overlays on frame.

        Args:
            frame: Input frame (will be copied, not modified)
            club_detection: Optional club detection result
            body_landmarks: Optional body landmark positions
            joint_calculator: Optional joint angle calculator for body angles
            annotations: Optional text annotations to draw
            show_angles: Whether to show angle measurements
            show_confidence: Whether to show confidence scores
            show_skeleton: Whether to show body skeleton

        Returns:
            Frame with overlays (new array, input not modified)

        Raises:
            ValueError: If frame is invalid
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")

        # Work on a copy to avoid modifying input
        output = frame.copy()

        # Render club detection
        if club_detection is not None:
            output = self.club_renderer.render(
                output,
                club_detection,
                show_angles=show_angles,
                show_confidence=show_confidence
            )

        # Render body landmarks
        if body_landmarks is not None and len(body_landmarks) > 0:
            if show_skeleton:
                output = self.body_renderer.draw_skeleton(output, body_landmarks)

            # Draw joint angles if calculator provided
            if joint_calculator is not None and show_angles:
                output = self.body_renderer.draw_joint_angles(
                    output,
                    body_landmarks,
                    joint_calculator,
                    self.angle_renderer,
                    show_labels=True
                )

        # Render text annotations
        if annotations is not None:
            for annotation in annotations:
                output = self._render_annotation(output, annotation)

        return output

    def _render_annotation(
        self,
        frame: np.ndarray,
        annotation: Annotation
    ) -> np.ndarray:
        """Render a single text annotation.

        Args:
            frame: Frame to draw on
            annotation: Annotation to render

        Returns:
            Frame with annotation
        """
        font_scale = annotation.font_scale if annotation.font_scale else self.style.font_scale
        color = annotation.color if annotation.color else self.style.text_color

        # Adjust position based on alignment
        position = annotation.position
        if annotation.alignment != 'left':
            # Calculate text width for centering/right alignment
            from .utils import get_text_size
            text_width, _ = get_text_size(
                annotation.text,
                self.style.font,
                font_scale,
                self.style.font_thickness
            )

            if annotation.alignment == 'center':
                position = (position[0] - text_width / 2, position[1])
            elif annotation.alignment == 'right':
                position = (position[0] - text_width, position[1])

        if annotation.background:
            frame = draw_text_with_background(
                frame,
                annotation.text,
                position,
                self.style.font,
                font_scale,
                color,
                self.style.text_bg_color,
                self.style.font_thickness,
                self.style.text_bg_alpha,
                self.style.text_padding
            )
        else:
            # Draw text without background
            import cv2
            cv2.putText(
                frame,
                annotation.text,
                (int(position[0]), int(position[1])),
                self.style.font,
                font_scale,
                color,
                self.style.font_thickness,
                lineType=cv2.LINE_AA if self.style.antialiasing else cv2.LINE_8
            )

        return frame

    def render_frame_info(
        self,
        frame: np.ndarray,
        frame_number: int,
        fps: Optional[float] = None,
        position: Optional[Point2D] = None
    ) -> np.ndarray:
        """Render frame number and timestamp info.

        Args:
            frame: Frame to draw on
            frame_number: Frame number
            fps: Optional frames per second for timestamp calculation
            position: Optional position (defaults to top-left)

        Returns:
            Frame with info overlay
        """
        if position is None:
            position = (10, 30)

        # Create frame info text
        info_text = f"Frame: {frame_number}"
        if fps is not None and fps > 0:
            timestamp = frame_number / fps
            info_text += f" | Time: {timestamp:.2f}s"

        annotation = Annotation(
            text=info_text,
            position=position,
            font_scale=self.style.font_scale * 0.9,
            background=True
        )

        return self._render_annotation(frame, annotation)

    def set_style(self, style: StyleConfig):
        """Update style configuration and reinitialize renderers.

        Args:
            style: New style configuration
        """
        self.style = style
        self.club_renderer = ClubRenderer(style)
        self.angle_renderer = AngleRenderer(style)
        self.body_renderer = BodyRenderer(style, self.handedness)

        logger.info("Updated visualization style")
