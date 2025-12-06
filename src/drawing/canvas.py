"""Interactive drawing canvas widget for PyQt5."""

import logging
from typing import Optional

from PyQt5.QtWidgets import QWidget, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush

from .shapes import Point2D, DrawingShape
from .tools import DrawingTool, LineTool, AngleTool, CircleTool, TextTool
from .manager import DrawingManager

logger = logging.getLogger(__name__)


class DrawingCanvas(QWidget):
    """Interactive canvas for drawing on video frames.

    Overlays on top of video player to capture mouse events
    for drawing operations. Transparent except for preview drawings.

    Signals:
        shape_added(DrawingShape): Emitted when shape is completed
        shape_selected(str): Emitted when shape is selected
        shape_deleted(str): Emitted when shape is deleted
        drawing_changed(): Emitted when drawing state changes
    """

    shape_added = pyqtSignal(object)
    shape_selected = pyqtSignal(str)
    shape_deleted = pyqtSignal(object)
    drawing_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize drawing canvas.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.current_tool = None
        self.drawing_enabled = False
        self.current_frame = 0
        self.selected_shape_id = None

        # Make widget transparent for mouse events when not drawing
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Set size policy
        self.setMinimumSize(100, 100)

        logger.debug("Initialized DrawingCanvas")

    def set_tool(self, tool: Optional[DrawingTool]):
        """Set active drawing tool.

        Args:
            tool: Drawing tool or None
        """
        # Cancel any current drawing
        if self.current_tool and self.current_tool.is_drawing():
            self.current_tool.cancel_drawing()

        self.current_tool = tool
        self.update()  # Redraw to clear preview

        logger.debug(f"Set tool to {type(tool).__name__ if tool else None}")

    def enable_drawing(self, enabled: bool):
        """Enable/disable drawing mode.

        Args:
            enabled: True to enable drawing
        """
        self.drawing_enabled = enabled

        # Enable/disable mouse event handling
        self.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)

        if not enabled:
            # Cancel any current drawing
            if self.current_tool and self.current_tool.is_drawing():
                self.current_tool.cancel_drawing()

        self.update()
        logger.debug(f"Drawing {'enabled' if enabled else 'disabled'}")

    def set_current_frame(self, frame_number: int):
        """Set current frame number.

        Args:
            frame_number: Frame number
        """
        self.current_frame = frame_number

    def mousePressEvent(self, event):
        """Handle mouse press for drawing start or selection.

        Args:
            event: Mouse event
        """
        if not self.drawing_enabled or not self.current_tool:
            return

        # Get point in widget coordinates
        point = Point2D(event.x(), event.y())

        # Check if it's a tool that needs special handling
        if isinstance(self.current_tool, AngleTool):
            # AngleTool needs 3 clicks
            if self.current_tool.click_count == 0:
                self.current_tool.start_drawing(point, self.current_frame)
            elif self.current_tool.click_count == 1:
                self.current_tool.add_point(point)
            elif self.current_tool.click_count == 2:
                self.current_tool.add_point(point)
                # Finish on third click
                shape = self.current_tool.finish_drawing()
                if shape:
                    self.shape_added.emit(shape)
                    self.drawing_changed.emit()

        elif isinstance(self.current_tool, TextTool):
            # TextTool needs text input
            self.current_tool.start_drawing(point, self.current_frame)
            text, ok = QInputDialog.getText(
                self,
                "Add Text",
                "Enter text:"
            )
            if ok and text:
                self.current_tool.set_text(text)
                shape = self.current_tool.finish_drawing()
                if shape:
                    self.shape_added.emit(shape)
                    self.drawing_changed.emit()
            else:
                self.current_tool.cancel_drawing()

        else:
            # LineTool, CircleTool: start on press
            self.current_tool.start_drawing(point, self.current_frame)

        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move for drawing preview.

        Args:
            event: Mouse event
        """
        if not self.drawing_enabled or not self.current_tool:
            return

        if self.current_tool.is_drawing():
            # Update tool with current position
            point = Point2D(event.x(), event.y())
            self.current_tool.update_drawing(point)
            self.update()  # Redraw preview

    def mouseReleaseEvent(self, event):
        """Handle mouse release for drawing completion.

        Args:
            event: Mouse event
        """
        if not self.drawing_enabled or not self.current_tool:
            return

        # Only finish for tools that complete on release
        if isinstance(self.current_tool, (LineTool, CircleTool)):
            if self.current_tool.is_drawing():
                shape = self.current_tool.finish_drawing()
                if shape:
                    self.shape_added.emit(shape)
                    self.drawing_changed.emit()

        self.update()

    def paintEvent(self, event):
        """Draw preview of current drawing.

        Args:
            event: Paint event
        """
        if not self.drawing_enabled or not self.current_tool:
            return

        # Get preview shape
        preview = self.current_tool.get_preview_shape()
        if not preview:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw preview based on shape type
        self._draw_preview_shape(painter, preview)

    def _draw_preview_shape(self, painter: QPainter, shape: DrawingShape):
        """Draw a preview shape.

        Args:
            painter: QPainter instance
            shape: Shape to draw
        """
        from .shapes import Line, Angle, Circle

        # Set pen with preview color (semi-transparent)
        color = QColor(*shape.color)
        color.setAlpha(150)  # Semi-transparent
        pen = QPen(color)
        pen.setWidth(max(1, shape.thickness - 1))
        painter.setPen(pen)

        if isinstance(shape, Line):
            painter.drawLine(
                int(shape.start.x), int(shape.start.y),
                int(shape.end.x), int(shape.end.y)
            )

        elif isinstance(shape, Angle):
            # Draw lines
            painter.drawLine(
                int(shape.point1.x), int(shape.point1.y),
                int(shape.vertex.x), int(shape.vertex.y)
            )
            painter.drawLine(
                int(shape.vertex.x), int(shape.vertex.y),
                int(shape.point3.x), int(shape.point3.y)
            )

        elif isinstance(shape, Circle):
            # Set brush for circle (no fill for preview)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(
                QPoint(int(shape.center.x), int(shape.center.y)),
                int(shape.radius),
                int(shape.radius)
            )

    def keyPressEvent(self, event):
        """Handle keyboard events.

        Args:
            event: Key event
        """
        if event.key() == Qt.Key_Escape:
            # Cancel current drawing
            if self.current_tool and self.current_tool.is_drawing():
                self.current_tool.cancel_drawing()
                self.update()
                logger.debug("Drawing cancelled with Escape")
