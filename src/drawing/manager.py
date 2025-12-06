"""Drawing manager for state management and undo/redo."""

import logging
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from .shapes import DrawingShape, Point2D, Line, Angle, Circle, TextAnnotation
from .tools import DrawingTool

logger = logging.getLogger(__name__)


class DrawingManager:
    """Manages drawing state, undo/redo, and frame-specific drawings.

    Coordinates all drawing operations and maintains the drawing state
    across multiple video frames.

    Example:
        manager = DrawingManager()

        # Add a shape
        manager.add_shape(line_shape)

        # Undo
        manager.undo()

        # Get shapes for current frame
        shapes = manager.get_shapes_for_frame(0)
    """

    def __init__(self):
        """Initialize drawing manager."""
        self.shapes_by_frame = defaultdict(list)  # frame_num -> List[DrawingShape]
        self.undo_stack = []  # List of (action, data) tuples
        self.redo_stack = []  # List of (action, data) tuples
        self.current_tool = None  # Currently active tool
        self.current_color = (255, 255, 0)  # Default yellow
        self.current_thickness = 2

    def add_shape(self, shape: DrawingShape):
        """Add a shape and push to undo stack.

        Args:
            shape: Shape to add
        """
        frame_num = shape.frame_number
        self.shapes_by_frame[frame_num].append(shape)

        # Add to undo stack
        self.undo_stack.append(('add', shape))
        self.redo_stack.clear()  # Clear redo on new action

        logger.debug(f"Added shape {shape.type} to frame {frame_num}")

    def remove_shape(self, shape: DrawingShape):
        """Remove a shape and push to undo stack.

        Args:
            shape: Shape to remove
        """
        frame_num = shape.frame_number

        if frame_num in self.shapes_by_frame:
            try:
                self.shapes_by_frame[frame_num].remove(shape)

                # Add to undo stack
                self.undo_stack.append(('remove', shape))
                self.redo_stack.clear()

                logger.debug(f"Removed shape {shape.id} from frame {frame_num}")
            except ValueError:
                logger.warning(f"Shape {shape.id} not found in frame {frame_num}")

    def remove_shape_by_id(self, shape_id: str) -> bool:
        """Remove a shape by ID.

        Args:
            shape_id: ID of shape to remove

        Returns:
            True if shape was found and removed
        """
        # Find and remove shape
        for frame_num, shapes in self.shapes_by_frame.items():
            for shape in shapes:
                if shape.id == shape_id:
                    self.remove_shape(shape)
                    return True

        logger.warning(f"Shape {shape_id} not found")
        return False

    def undo(self) -> bool:
        """Undo last operation.

        Returns:
            True if undo was performed
        """
        if not self.undo_stack:
            logger.debug("Undo stack is empty")
            return False

        action, data = self.undo_stack.pop()

        if action == 'add':
            # Undo add = remove (without adding to undo stack)
            shape = data
            self.shapes_by_frame[shape.frame_number].remove(shape)
            logger.debug(f"Undid add of shape {shape.id}")

        elif action == 'remove':
            # Undo remove = add back (without adding to undo stack)
            shape = data
            self.shapes_by_frame[shape.frame_number].append(shape)
            logger.debug(f"Undid remove of shape {shape.id}")

        elif action == 'clear':
            # Undo clear = restore all shapes
            frame_num, shapes = data
            self.shapes_by_frame[frame_num] = shapes.copy()
            logger.debug(f"Undid clear of frame {frame_num}")

        # Push to redo stack
        self.redo_stack.append((action, data))

        return True

    def redo(self) -> bool:
        """Redo last undone operation.

        Returns:
            True if redo was performed
        """
        if not self.redo_stack:
            logger.debug("Redo stack is empty")
            return False

        action, data = self.redo_stack.pop()

        if action == 'add':
            # Redo add
            shape = data
            self.shapes_by_frame[shape.frame_number].append(shape)
            logger.debug(f"Redid add of shape {shape.id}")

        elif action == 'remove':
            # Redo remove
            shape = data
            self.shapes_by_frame[shape.frame_number].remove(shape)
            logger.debug(f"Redid remove of shape {shape.id}")

        elif action == 'clear':
            # Redo clear
            frame_num, _ = data
            self.shapes_by_frame[frame_num].clear()
            logger.debug(f"Redid clear of frame {frame_num}")

        # Push back to undo stack
        self.undo_stack.append((action, data))

        return True

    def get_shapes_for_frame(self, frame_number: int) -> List[DrawingShape]:
        """Get all shapes for a specific frame.

        Args:
            frame_number: Frame number

        Returns:
            List of shapes for that frame
        """
        return self.shapes_by_frame.get(frame_number, [])

    def clear_frame(self, frame_number: int):
        """Clear all shapes from a frame.

        Args:
            frame_number: Frame number to clear
        """
        if frame_number in self.shapes_by_frame:
            # Store shapes for undo
            shapes = self.shapes_by_frame[frame_number].copy()
            self.shapes_by_frame[frame_number].clear()

            # Add to undo stack as batch operation
            self.undo_stack.append(('clear', (frame_number, shapes)))
            self.redo_stack.clear()

            logger.debug(f"Cleared {len(shapes)} shapes from frame {frame_number}")

    def clear_all(self):
        """Clear all shapes from all frames."""
        # Store all shapes for undo
        all_shapes = {}
        for frame_num, shapes in self.shapes_by_frame.items():
            all_shapes[frame_num] = shapes.copy()

        self.shapes_by_frame.clear()

        # Add to undo stack
        self.undo_stack.append(('clear_all', all_shapes))
        self.redo_stack.clear()

        logger.debug("Cleared all shapes")

    def get_all_shapes(self) -> List[DrawingShape]:
        """Get all shapes across all frames.

        Returns:
            List of all shapes
        """
        all_shapes = []
        for shapes in self.shapes_by_frame.values():
            all_shapes.extend(shapes)
        return all_shapes

    def get_shape_count(self) -> int:
        """Get total number of shapes across all frames.

        Returns:
            Total shape count
        """
        return sum(len(shapes) for shapes in self.shapes_by_frame.values())

    def get_frame_count(self) -> int:
        """Get number of frames with drawings.

        Returns:
            Number of frames
        """
        return len(self.shapes_by_frame)

    def get_shape_by_id(self, shape_id: str) -> Optional[DrawingShape]:
        """Find a shape by ID.

        Args:
            shape_id: Shape ID

        Returns:
            Shape if found, None otherwise
        """
        for shapes in self.shapes_by_frame.values():
            for shape in shapes:
                if shape.id == shape_id:
                    return shape
        return None

    def find_shape_at_point(
        self,
        frame_number: int,
        x: int,
        y: int,
        tolerance: int = 10
    ) -> Optional[DrawingShape]:
        """Find a shape near a point on a frame.

        Args:
            frame_number: Frame number
            x: X coordinate
            y: Y coordinate
            tolerance: Distance tolerance in pixels

        Returns:
            Nearest shape if found within tolerance, None otherwise
        """
        from ..analysis import distance_between_points

        point = Point2D(x, y)
        shapes = self.get_shapes_for_frame(frame_number)

        nearest_shape = None
        nearest_distance = float('inf')

        for shape in shapes:
            # Calculate distance based on shape type
            if isinstance(shape, Line):
                # Distance to line segment
                dist = self._point_to_line_distance(point, shape.start, shape.end)
            elif isinstance(shape, Angle):
                # Distance to any of the two line segments
                dist1 = self._point_to_line_distance(point, shape.point1, shape.vertex)
                dist2 = self._point_to_line_distance(point, shape.vertex, shape.point3)
                dist = min(dist1, dist2)
            elif isinstance(shape, Circle):
                # Distance to circle perimeter
                center_dist = distance_between_points(point.to_tuple(), shape.center.to_tuple())
                dist = abs(center_dist - shape.radius)
            elif isinstance(shape, TextAnnotation):
                # Distance to text position
                dist = distance_between_points(point.to_tuple(), shape.position.to_tuple())
            else:
                continue

            if dist < nearest_distance and dist <= tolerance:
                nearest_distance = dist
                nearest_shape = shape

        return nearest_shape

    def _point_to_line_distance(
        self,
        point: Point2D,
        line_start: Point2D,
        line_end: Point2D
    ) -> float:
        """Calculate distance from point to line segment.

        Args:
            point: Point to measure from
            line_start: Line start point
            line_end: Line end point

        Returns:
            Distance in pixels
        """
        from ..analysis import distance_between_points

        # Vector from start to end
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y

        # Length squared
        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            # Line is a point
            return distance_between_points(point.to_tuple(), line_start.to_tuple())

        # Parameter t of closest point on line
        t = max(0, min(1, (
            (point.x - line_start.x) * dx +
            (point.y - line_start.y) * dy
        ) / length_sq))

        # Closest point on line segment
        closest = Point2D(
            x=line_start.x + t * dx,
            y=line_start.y + t * dy
        )

        return distance_between_points(point.to_tuple(), closest.to_tuple())

    def can_undo(self) -> bool:
        """Check if undo is available.

        Returns:
            True if undo stack is not empty
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available.

        Returns:
            True if redo stack is not empty
        """
        return len(self.redo_stack) > 0

    def set_tool(self, tool: Optional[DrawingTool]):
        """Set the current drawing tool.

        Args:
            tool: Drawing tool or None
        """
        self.current_tool = tool
        if tool:
            logger.debug(f"Set current tool to {type(tool).__name__}")

    def set_color(self, color: Tuple[int, int, int]):
        """Set the current drawing color.

        Args:
            color: RGB color tuple
        """
        self.current_color = color
        if self.current_tool:
            self.current_tool.color = color

    def set_thickness(self, thickness: int):
        """Set the current line thickness.

        Args:
            thickness: Thickness in pixels
        """
        self.current_thickness = thickness
        if self.current_tool:
            self.current_tool.thickness = thickness
