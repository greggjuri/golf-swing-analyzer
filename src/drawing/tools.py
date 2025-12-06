"""Drawing tool implementations for interactive drawing."""

import logging
from typing import Optional, Tuple
from enum import Enum

from .shapes import (
    Point2D,
    DrawingShape, Line, Angle, Circle, TextAnnotation,
    create_line, create_angle, create_circle, generate_shape_id
)

logger = logging.getLogger(__name__)


class ToolState(Enum):
    """Drawing tool states."""
    IDLE = "idle"
    DRAWING = "drawing"
    COMPLETE = "complete"


class DrawingTool:
    """Base class for drawing tools.

    Attributes:
        color: RGB color tuple for drawing
        thickness: Line thickness in pixels
        state: Current tool state
        frame_number: Current frame number
    """

    def __init__(self, color: Tuple[int, int, int] = (255, 255, 0), thickness: int = 2):
        """Initialize drawing tool.

        Args:
            color: RGB color tuple (default yellow)
            thickness: Line thickness in pixels
        """
        self.color = color
        self.thickness = thickness
        self.state = ToolState.IDLE
        self.frame_number = 0

    def start_drawing(self, point: Point2D, frame_number: int):
        """Start drawing at point.

        Args:
            point: Starting point
            frame_number: Current frame number
        """
        self.frame_number = frame_number
        self.state = ToolState.DRAWING

    def update_drawing(self, point: Point2D):
        """Update drawing with new point.

        Args:
            point: Current mouse position
        """
        pass

    def finish_drawing(self) -> Optional[DrawingShape]:
        """Finish drawing and return shape.

        Returns:
            Completed DrawingShape or None if cancelled
        """
        self.state = ToolState.COMPLETE
        return None

    def cancel_drawing(self):
        """Cancel current drawing operation."""
        self.state = ToolState.IDLE

    def get_preview_shape(self) -> Optional[DrawingShape]:
        """Get preview of current drawing state.

        Returns:
            Preview DrawingShape or None
        """
        return None

    def is_drawing(self) -> bool:
        """Check if currently drawing.

        Returns:
            True if in DRAWING state
        """
        return self.state == ToolState.DRAWING

    def reset(self):
        """Reset tool to idle state."""
        self.state = ToolState.IDLE


class LineTool(DrawingTool):
    """Tool for drawing straight lines.

    User workflow:
    1. Click to set start point
    2. Move mouse to see preview
    3. Click again to set end point
    """

    def __init__(self, color: Tuple[int, int, int] = (255, 255, 0), thickness: int = 2):
        """Initialize line tool."""
        super().__init__(color, thickness)
        self.start_point = None
        self.end_point = None

    def start_drawing(self, point: Point2D, frame_number: int):
        """Start drawing line at point."""
        super().start_drawing(point, frame_number)
        self.start_point = point
        self.end_point = point
        logger.debug(f"LineTool: Started at {point}")

    def update_drawing(self, point: Point2D):
        """Update line end point."""
        if self.state == ToolState.DRAWING:
            self.end_point = point

    def finish_drawing(self) -> Optional[Line]:
        """Finish drawing and create Line shape."""
        if self.start_point is None or self.end_point is None:
            self.reset()
            return None

        # Create line shape
        line = create_line(
            start=self.start_point,
            end=self.end_point,
            frame_number=self.frame_number,
            color=self.color,
            thickness=self.thickness
        )

        logger.debug(f"LineTool: Finished line with length {line.length():.1f}px")

        # Reset state
        self.reset()
        self.start_point = None
        self.end_point = None

        return line

    def get_preview_shape(self) -> Optional[Line]:
        """Get preview of current line."""
        if self.state == ToolState.DRAWING and self.start_point and self.end_point:
            return create_line(
                start=self.start_point,
                end=self.end_point,
                frame_number=self.frame_number,
                color=self.color,
                thickness=self.thickness
            )
        return None

    def cancel_drawing(self):
        """Cancel line drawing."""
        super().cancel_drawing()
        self.start_point = None
        self.end_point = None


class AngleTool(DrawingTool):
    """Tool for measuring angles (3-point click).

    User workflow:
    1. Click first point
    2. Click vertex (middle point)
    3. Click third point
    """

    def __init__(self, color: Tuple[int, int, int] = (255, 255, 0), thickness: int = 2):
        """Initialize angle tool."""
        super().__init__(color, thickness)
        self.point1 = None
        self.vertex = None
        self.point3 = None
        self.click_count = 0

    def start_drawing(self, point: Point2D, frame_number: int):
        """Start angle with first point."""
        super().start_drawing(point, frame_number)
        self.point1 = point
        self.click_count = 1
        logger.debug("AngleTool: First point set")

    def add_point(self, point: Point2D):
        """Add a point to the angle.

        Args:
            point: Point to add (vertex or third point)
        """
        if self.click_count == 1:
            self.vertex = point
            self.click_count = 2
            logger.debug("AngleTool: Vertex set")
        elif self.click_count == 2:
            self.point3 = point
            self.click_count = 3
            logger.debug("AngleTool: Third point set")

    def finish_drawing(self) -> Optional[Angle]:
        """Finish angle drawing."""
        if self.click_count != 3 or not all([self.point1, self.vertex, self.point3]):
            self.reset()
            return None

        # Create angle shape
        angle = create_angle(
            point1=self.point1,
            vertex=self.vertex,
            point3=self.point3,
            frame_number=self.frame_number,
            color=self.color,
            thickness=self.thickness,
            show_arc=True
        )

        logger.debug(f"AngleTool: Finished angle {angle.measure():.1f}°")

        # Reset state
        self.reset()
        self.point1 = None
        self.vertex = None
        self.point3 = None
        self.click_count = 0

        return angle

    def get_preview_shape(self) -> Optional[Angle]:
        """Get preview of current angle."""
        if self.state == ToolState.DRAWING and self.click_count >= 2:
            # Show partial angle
            p3 = self.point3 if self.point3 else self.vertex
            return create_angle(
                point1=self.point1,
                vertex=self.vertex,
                point3=p3,
                frame_number=self.frame_number,
                color=self.color,
                thickness=max(1, self.thickness - 1),  # Thinner for preview
                show_arc=(self.click_count == 3)
            )
        return None

    def cancel_drawing(self):
        """Cancel angle drawing."""
        super().cancel_drawing()
        self.point1 = None
        self.vertex = None
        self.point3 = None
        self.click_count = 0


class CircleTool(DrawingTool):
    """Tool for drawing circles.

    User workflow:
    1. Click to set center
    2. Drag to set radius
    3. Release to finish
    """

    def __init__(self, color: Tuple[int, int, int] = (255, 255, 0), thickness: int = 2):
        """Initialize circle tool."""
        super().__init__(color, thickness)
        self.center = None
        self.radius = 0.0

    def start_drawing(self, point: Point2D, frame_number: int):
        """Start circle at center point."""
        super().start_drawing(point, frame_number)
        self.center = point
        self.radius = 0.0
        logger.debug(f"CircleTool: Center set at {point}")

    def update_drawing(self, point: Point2D):
        """Update circle radius based on distance from center."""
        if self.state == ToolState.DRAWING and self.center:
            # Calculate radius as distance from center
            from ..analysis import distance_between_points
            self.radius = distance_between_points(self.center.to_tuple(), point.to_tuple())

    def finish_drawing(self) -> Optional[Circle]:
        """Finish circle drawing."""
        if self.center is None or self.radius < 5:  # Minimum radius
            self.reset()
            return None

        # Create circle shape
        circle = create_circle(
            center=self.center,
            radius=self.radius,
            frame_number=self.frame_number,
            color=self.color,
            thickness=self.thickness,
            fill=False
        )

        logger.debug(f"CircleTool: Finished circle with radius {self.radius:.1f}px")

        # Reset state
        self.reset()
        self.center = None
        self.radius = 0.0

        return circle

    def get_preview_shape(self) -> Optional[Circle]:
        """Get preview of current circle."""
        if self.state == ToolState.DRAWING and self.center and self.radius > 0:
            return create_circle(
                center=self.center,
                radius=self.radius,
                frame_number=self.frame_number,
                color=self.color,
                thickness=max(1, self.thickness - 1)
            )
        return None

    def cancel_drawing(self):
        """Cancel circle drawing."""
        super().cancel_drawing()
        self.center = None
        self.radius = 0.0


class TextTool(DrawingTool):
    """Tool for adding text annotations.

    User workflow:
    1. Click to set position
    2. Enter text in dialog
    3. Text is added to frame
    """

    def __init__(self, color: Tuple[int, int, int] = (255, 255, 255), thickness: int = 2):
        """Initialize text tool."""
        super().__init__(color, thickness)
        self.position = None
        self.text = ""
        self.font_scale = 1.0

    def start_drawing(self, point: Point2D, frame_number: int):
        """Start text annotation at point."""
        super().start_drawing(point, frame_number)
        self.position = point
        logger.debug(f"TextTool: Position set at {point}")

    def set_text(self, text: str, font_scale: float = 1.0):
        """Set text content.

        Args:
            text: Text content
            font_scale: Font scale factor
        """
        self.text = text
        self.font_scale = font_scale

    def finish_drawing(self) -> Optional[TextAnnotation]:
        """Finish text annotation."""
        if self.position is None or not self.text:
            self.reset()
            return None

        # Create text annotation
        import time
        annotation = TextAnnotation(
            id=generate_shape_id(),
            type="text",
            color=self.color,
            thickness=self.thickness,
            frame_number=self.frame_number,
            created_at=time.time(),
            position=self.position,
            text=self.text,
            font_scale=self.font_scale,
            background=True
        )

        logger.debug(f"TextTool: Finished text '{self.text}'")

        # Reset state
        self.reset()
        self.position = None
        self.text = ""

        return annotation

    def cancel_drawing(self):
        """Cancel text annotation."""
        super().cancel_drawing()
        self.position = None
        self.text = ""
