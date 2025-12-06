"""Manual drawing tools for annotating golf swing videos.

This module provides interactive tools for users to manually draw lines,
angles, circles, and annotations on video frames.

Main components:
- Drawing shapes: Line, Angle, Circle, Arc, TextAnnotation
- Drawing tools: LineTool, AngleTool, CircleTool, TextTool
- DrawingCanvas: Interactive widget for drawing
- DrawingToolbar: Tool selection and settings
- DrawingRenderer: Render drawings on frames
- DrawingManager: Manage drawing state and undo/redo
- DrawingStorage: Save/load drawings

Example:
    from src.drawing import DrawingManager, LineTool, DrawingRenderer

    manager = DrawingManager()
    tool = LineTool(color=(255, 255, 0), thickness=2)

    # User draws a line
    tool.start_drawing(Point2D(100, 100), frame_number=0)
    tool.update_drawing(Point2D(200, 200))
    shape = tool.finish_drawing()

    manager.add_shape(shape)

    # Render on frame
    renderer = DrawingRenderer()
    shapes = manager.get_shapes_for_frame(0)
    annotated = renderer.render(frame, shapes)
"""

from .shapes import (
    Point2D,
    DrawingShape,
    Line,
    Angle,
    Circle,
    Arc,
    TextAnnotation,
)

from .tools import (
    DrawingTool,
    LineTool,
    AngleTool,
    CircleTool,
    TextTool,
)

from .renderer import DrawingRenderer
from .manager import DrawingManager
from .storage import DrawingStorage
from .canvas import DrawingCanvas
from .toolbar import DrawingToolbar

__all__ = [
    # Point
    'Point2D',

    # Shapes
    'DrawingShape',
    'Line',
    'Angle',
    'Circle',
    'Arc',
    'TextAnnotation',

    # Tools
    'DrawingTool',
    'LineTool',
    'AngleTool',
    'CircleTool',
    'TextTool',

    # Components
    'DrawingRenderer',
    'DrawingManager',
    'DrawingStorage',

    # GUI Widgets
    'DrawingCanvas',
    'DrawingToolbar',
]
