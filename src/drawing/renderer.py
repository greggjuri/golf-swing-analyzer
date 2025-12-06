"""Render drawing shapes onto video frames."""

import logging
import math
from typing import List, Optional

import cv2
import numpy as np

from .shapes import Point2D, DrawingShape, Line, Angle, Circle, Arc, TextAnnotation

logger = logging.getLogger(__name__)


class DrawingRenderer:
    """Renders drawing shapes onto video frames.

    Example:
        renderer = DrawingRenderer()
        annotated = renderer.render(frame, shapes, show_measurements=True)
    """

    def __init__(self):
        """Initialize drawing renderer."""
        pass

    def render(
        self,
        frame: np.ndarray,
        shapes: List[DrawingShape],
        show_measurements: bool = True,
        selected_shape_id: Optional[str] = None
    ) -> np.ndarray:
        """Render all shapes onto frame.

        Args:
            frame: Input frame (will be copied)
            shapes: List of shapes to render
            show_measurements: Whether to show angle/length measurements
            selected_shape_id: ID of selected shape (will be highlighted)

        Returns:
            Frame with drawings rendered
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")

        # Work on a copy
        output = frame.copy()

        for shape in shapes:
            # Determine thickness (highlight if selected)
            thickness = shape.thickness
            if shape.id == selected_shape_id:
                thickness = max(thickness * 2, thickness + 2)

            # Render based on shape type
            if isinstance(shape, Line):
                self._render_line(output, shape, thickness, show_measurements)
            elif isinstance(shape, Angle):
                self._render_angle(output, shape, thickness, show_measurements)
            elif isinstance(shape, Circle):
                self._render_circle(output, shape, thickness, show_measurements)
            elif isinstance(shape, Arc):
                self._render_arc(output, shape, thickness, show_measurements)
            elif isinstance(shape, TextAnnotation):
                self._render_text(output, shape)

        return output

    def _render_line(
        self,
        frame: np.ndarray,
        line: Line,
        thickness: int,
        show_label: bool
    ):
        """Render a line with optional measurement label.

        Args:
            frame: Frame to draw on (modified in place)
            line: Line shape to render
            thickness: Line thickness
            show_label: Whether to show measurements
        """
        # Draw the line
        cv2.line(
            frame,
            (int(line.start.x), int(line.start.y)),
            (int(line.end.x), int(line.end.y)),
            line.color,
            thickness,
            cv2.LINE_AA
        )

        # Draw endpoints
        cv2.circle(frame, (int(line.start.x), int(line.start.y)), 4, line.color, -1)
        cv2.circle(frame, (int(line.end.x), int(line.end.y)), 4, line.color, -1)

        if show_label:
            # Calculate measurements
            length = line.length()
            angle = line.angle_from_horizontal()

            # Build label
            if line.label:
                label = f"{line.label}: {length:.0f}px @ {angle:.1f}°"
            else:
                label = f"{length:.0f}px @ {angle:.1f}°"

            # Draw at midpoint
            midpoint = line.midpoint()
            self._draw_text_with_background(
                frame,
                label,
                (int(midpoint.x), int(midpoint.y) - 10),
                scale=0.5,
                color=line.color,
                thickness=1
            )

    def _render_angle(
        self,
        frame: np.ndarray,
        angle: Angle,
        thickness: int,
        show_measurement: bool
    ):
        """Render an angle with arc and measurement.

        Args:
            frame: Frame to draw on (modified in place)
            angle: Angle shape to render
            thickness: Line thickness
            show_measurement: Whether to show angle measurement
        """
        # Draw lines from vertex to each point
        cv2.line(
            frame,
            (int(angle.point1.x), int(angle.point1.y)),
            (int(angle.vertex.x), int(angle.vertex.y)),
            angle.color,
            thickness,
            cv2.LINE_AA
        )
        cv2.line(
            frame,
            (int(angle.vertex.x), int(angle.vertex.y)),
            (int(angle.point3.x), int(angle.point3.y)),
            angle.color,
            thickness,
            cv2.LINE_AA
        )

        # Draw points
        cv2.circle(frame, (int(angle.point1.x), int(angle.point1.y)), 4, angle.color, -1)
        cv2.circle(frame, (int(angle.vertex.x), int(angle.vertex.y)), 5, angle.color, -1)
        cv2.circle(frame, (int(angle.point3.x), int(angle.point3.y)), 4, angle.color, -1)

        # Draw arc if enabled
        if angle.show_arc:
            self._draw_angle_arc(frame, angle)

        if show_measurement:
            # Calculate angle
            degrees = angle.measure()

            # Build label
            if angle.label:
                label = f"{angle.label}: {degrees:.1f}°"
            else:
                label = f"{degrees:.1f}°"

            # Draw near vertex
            self._draw_text_with_background(
                frame,
                label,
                (int(angle.vertex.x) + 20, int(angle.vertex.y) - 20),
                scale=0.6,
                color=angle.color,
                thickness=1
            )

    def _draw_angle_arc(self, frame: np.ndarray, angle: Angle):
        """Draw the arc for an angle.

        Args:
            frame: Frame to draw on
            angle: Angle shape
        """
        # Calculate angles from vertex to each point
        angle1_rad = math.atan2(
            angle.point1.y - angle.vertex.y,
            angle.point1.x - angle.vertex.x
        )
        angle3_rad = math.atan2(
            angle.point3.y - angle.vertex.y,
            angle.point3.x - angle.vertex.x
        )

        # Convert to degrees for cv2.ellipse
        angle1_deg = math.degrees(angle1_rad)
        angle3_deg = math.degrees(angle3_rad)

        # Ensure we draw the smaller arc
        start_angle = min(angle1_deg, angle3_deg)
        end_angle = max(angle1_deg, angle3_deg)

        # If arc is > 180°, swap to get smaller arc
        if end_angle - start_angle > 180:
            start_angle, end_angle = end_angle, start_angle + 360

        # Draw arc
        try:
            cv2.ellipse(
                frame,
                (int(angle.vertex.x), int(angle.vertex.y)),
                (angle.arc_radius, angle.arc_radius),
                0,  # Rotation
                start_angle,
                end_angle,
                angle.color,
                max(1, angle.thickness - 1),
                cv2.LINE_AA
            )
        except Exception as e:
            logger.warning(f"Failed to draw angle arc: {e}")

    def _render_circle(
        self,
        frame: np.ndarray,
        circle: Circle,
        thickness: int,
        show_label: bool
    ):
        """Render a circle with optional measurement.

        Args:
            frame: Frame to draw on (modified in place)
            circle: Circle shape to render
            thickness: Line thickness
            show_label: Whether to show measurements
        """
        # Draw circle
        if circle.fill:
            cv2.circle(
                frame,
                (int(circle.center.x), int(circle.center.y)),
                int(circle.radius),
                circle.color,
                -1,  # Filled
                cv2.LINE_AA
            )
        else:
            cv2.circle(
                frame,
                (int(circle.center.x), int(circle.center.y)),
                int(circle.radius),
                circle.color,
                thickness,
                cv2.LINE_AA
            )

        # Draw center point
        cv2.circle(frame, (int(circle.center.x), int(circle.center.y)), 3, circle.color, -1)

        if show_label:
            # Build label
            if circle.label:
                label = f"{circle.label}: r={circle.radius:.0f}px"
            else:
                label = f"r={circle.radius:.0f}px"

            # Draw above center
            self._draw_text_with_background(
                frame,
                label,
                (int(circle.center.x), int(circle.center.y - circle.radius - 15)),
                scale=0.5,
                color=circle.color,
                thickness=1
            )

    def _render_arc(
        self,
        frame: np.ndarray,
        arc: Arc,
        thickness: int,
        show_label: bool
    ):
        """Render an arc with optional measurement.

        Args:
            frame: Frame to draw on (modified in place)
            arc: Arc shape to render
            thickness: Line thickness
            show_label: Whether to show measurements
        """
        # Draw arc using cv2.ellipse
        try:
            cv2.ellipse(
                frame,
                (int(arc.center.x), int(arc.center.y)),
                (int(arc.radius), int(arc.radius)),
                0,  # Rotation
                arc.start_angle,
                arc.end_angle,
                arc.color,
                thickness,
                cv2.LINE_AA
            )
        except Exception as e:
            logger.warning(f"Failed to draw arc: {e}")
            return

        # Draw center point
        cv2.circle(frame, (int(arc.center.x), int(arc.center.y)), 3, arc.color, -1)

        if show_label:
            # Calculate arc length
            arc_length = arc.arc_length()

            # Build label
            if arc.label:
                label = f"{arc.label}: {arc_length:.0f}px"
            else:
                label = f"{arc_length:.0f}px"

            # Draw above center
            self._draw_text_with_background(
                frame,
                label,
                (int(arc.center.x), int(arc.center.y - arc.radius - 15)),
                scale=0.5,
                color=arc.color,
                thickness=1
            )

    def _render_text(self, frame: np.ndarray, text: TextAnnotation):
        """Render text annotation.

        Args:
            frame: Frame to draw on (modified in place)
            text: TextAnnotation shape to render
        """
        self._draw_text_with_background(
            frame,
            text.text,
            (int(text.position.x), int(text.position.y)),
            scale=text.font_scale,
            color=text.color,
            thickness=text.thickness,
            with_background=text.background
        )

    def _draw_text_with_background(
        self,
        frame: np.ndarray,
        text: str,
        position: tuple,
        scale: float = 0.5,
        color: tuple = (255, 255, 255),
        thickness: int = 1,
        with_background: bool = True
    ):
        """Draw text with semi-transparent background.

        Args:
            frame: Frame to draw on
            text: Text to draw
            position: (x, y) position
            scale: Font scale
            color: Text color
            thickness: Text thickness
            with_background: Whether to draw background box
        """
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, scale, thickness
        )

        x, y = position

        if with_background:
            # Draw semi-transparent background
            padding = 4
            overlay = frame.copy()

            cv2.rectangle(
                overlay,
                (x - padding, y - text_height - padding),
                (x + text_width + padding, y + baseline + padding),
                (0, 0, 0),
                -1
            )

            # Blend overlay
            alpha = 0.6
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Draw text
        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            scale,
            color,
            thickness,
            cv2.LINE_AA
        )
