"""Drawing shape data structures.

This module defines the data structures for manual drawing shapes
that users can create on video frames.
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Tuple, Dict, Any, Optional
import math

from ..analysis import angle_between_points, distance_between_points

# Point2D is a type alias for tuple, so we create a simple dataclass
from dataclasses import dataclass as _dataclass

@_dataclass
class Point2D:
    """2D point with x and y coordinates."""
    x: float
    y: float

    def to_tuple(self) -> tuple:
        """Convert to tuple."""
        return (self.x, self.y)


@dataclass
class DrawingShape:
    """Base class for all drawing shapes.

    Attributes:
        id: Unique identifier for the shape
        type: Shape type (line, angle, circle, etc.)
        color: RGB color tuple (0-255 for each channel)
        thickness: Line thickness in pixels
        frame_number: Frame number this shape belongs to
        created_at: Timestamp when shape was created
        metadata: Additional metadata dictionary
    """

    id: str
    type: str
    color: Tuple[int, int, int]
    thickness: int
    frame_number: int
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the shape
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            DrawingShape instance
        """
        return cls(**data)


@dataclass
class Line(DrawingShape):
    """Straight line between two points.

    Attributes:
        start: Starting point
        end: Ending point
        label: Optional text label
    """

    start: Point2D = field(default_factory=lambda: Point2D(0, 0))
    end: Point2D = field(default_factory=lambda: Point2D(0, 0))
    label: str = ""

    def __post_init__(self):
        """Ensure type is set correctly."""
        self.type = "line"

    def length(self) -> float:
        """Calculate line length in pixels.

        Returns:
            Length in pixels
        """
        return distance_between_points(self.start.to_tuple(), self.end.to_tuple())

    def angle_from_horizontal(self) -> float:
        """Calculate angle from horizontal axis.

        Returns:
            Angle in degrees (0-360)
        """
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Normalize to 0-360
        if angle_deg < 0:
            angle_deg += 360

        return angle_deg

    def angle_from_vertical(self) -> float:
        """Calculate angle from vertical axis.

        Returns:
            Angle in degrees
        """
        horizontal_angle = self.angle_from_horizontal()
        return abs(90 - horizontal_angle)

    def midpoint(self) -> Point2D:
        """Calculate midpoint of the line.

        Returns:
            Midpoint coordinates
        """
        return Point2D(
            x=(self.start.x + self.end.x) / 2,
            y=(self.start.y + self.end.y) / 2
        )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = super().to_dict()
        # Convert Point2D to dict
        data['start'] = {'x': self.start.x, 'y': self.start.y}
        data['end'] = {'x': self.end.x, 'y': self.end.y}
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary."""
        # Convert dict to Point2D
        data['start'] = Point2D(**data['start'])
        data['end'] = Point2D(**data['end'])
        return cls(**data)


@dataclass
class Angle(DrawingShape):
    """Angle defined by three points (vertex in middle).

    Attributes:
        point1: First point
        vertex: Vertex (middle point)
        point3: Third point
        label: Optional text label
        show_arc: Whether to draw the angle arc
        arc_radius: Radius of the angle arc in pixels
    """

    point1: Point2D = field(default_factory=lambda: Point2D(0, 0))
    vertex: Point2D = field(default_factory=lambda: Point2D(0, 0))
    point3: Point2D = field(default_factory=lambda: Point2D(0, 0))
    label: str = ""
    show_arc: bool = True
    arc_radius: int = 50

    def __post_init__(self):
        """Ensure type is set correctly."""
        self.type = "angle"

    def measure(self) -> float:
        """Calculate angle in degrees.

        Returns:
            Angle in degrees (0-180)
        """
        return angle_between_points(
            self.point1.to_tuple(),
            self.vertex.to_tuple(),
            self.point3.to_tuple()
        )

    def get_bisector(self) -> Tuple[Point2D, Point2D]:
        """Calculate angle bisector line.

        Returns:
            Tuple of (start_point, end_point) for bisector line
        """
        # Get angles from vertex to each point
        angle1 = math.atan2(
            self.point1.y - self.vertex.y,
            self.point1.x - self.vertex.x
        )
        angle3 = math.atan2(
            self.point3.y - self.vertex.y,
            self.point3.x - self.vertex.x
        )

        # Bisector angle is the average
        bisector_angle = (angle1 + angle3) / 2

        # Calculate end point of bisector
        bisector_length = 100  # Fixed length for display
        end_x = self.vertex.x + bisector_length * math.cos(bisector_angle)
        end_y = self.vertex.y + bisector_length * math.sin(bisector_angle)

        return (self.vertex, Point2D(x=end_x, y=end_y))

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = super().to_dict()
        data['point1'] = {'x': self.point1.x, 'y': self.point1.y}
        data['vertex'] = {'x': self.vertex.x, 'y': self.vertex.y}
        data['point3'] = {'x': self.point3.x, 'y': self.point3.y}
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary."""
        data['point1'] = Point2D(**data['point1'])
        data['vertex'] = Point2D(**data['vertex'])
        data['point3'] = Point2D(**data['point3'])
        return cls(**data)


@dataclass
class Circle(DrawingShape):
    """Circle defined by center and radius.

    Attributes:
        center: Center point
        radius: Radius in pixels
        label: Optional text label
        fill: Whether to fill the circle
    """

    center: Point2D = field(default_factory=lambda: Point2D(0, 0))
    radius: float = 0.0
    label: str = ""
    fill: bool = False

    def __post_init__(self):
        """Ensure type is set correctly."""
        self.type = "circle"

    def area(self) -> float:
        """Calculate circle area.

        Returns:
            Area in square pixels
        """
        return math.pi * self.radius ** 2

    def circumference(self) -> float:
        """Calculate circle circumference.

        Returns:
            Circumference in pixels
        """
        return 2 * math.pi * self.radius

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is inside the circle.

        Args:
            point: Point to check

        Returns:
            True if point is inside circle
        """
        distance = distance_between_points(self.center.to_tuple(), point.to_tuple())
        return distance <= self.radius

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = super().to_dict()
        data['center'] = {'x': self.center.x, 'y': self.center.y}
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary."""
        data['center'] = Point2D(**data['center'])
        return cls(**data)


@dataclass
class Arc(DrawingShape):
    """Arc segment of a circle.

    Attributes:
        center: Center point
        radius: Radius in pixels
        start_angle: Start angle in degrees
        end_angle: End angle in degrees
        label: Optional text label
    """

    center: Point2D = field(default_factory=lambda: Point2D(0, 0))
    radius: float = 0.0
    start_angle: float = 0.0
    end_angle: float = 0.0
    label: str = ""

    def __post_init__(self):
        """Ensure type is set correctly."""
        self.type = "arc"

    def arc_length(self) -> float:
        """Calculate arc length.

        Returns:
            Arc length in pixels
        """
        angle_diff = abs(self.end_angle - self.start_angle)
        angle_rad = math.radians(angle_diff)
        return self.radius * angle_rad

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = super().to_dict()
        data['center'] = {'x': self.center.x, 'y': self.center.y}
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary."""
        data['center'] = Point2D(**data['center'])
        return cls(**data)


@dataclass
class TextAnnotation(DrawingShape):
    """Text annotation at a point.

    Attributes:
        position: Text position (top-left corner)
        text: Text content
        font_scale: Font scale factor
        background: Whether to draw background box
    """

    position: Point2D = field(default_factory=lambda: Point2D(0, 0))
    text: str = ""
    font_scale: float = 1.0
    background: bool = True

    def __post_init__(self):
        """Ensure type is set correctly."""
        self.type = "text"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = super().to_dict()
        data['position'] = {'x': self.position.x, 'y': self.position.y}
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary."""
        data['position'] = Point2D(**data['position'])
        return cls(**data)


def generate_shape_id() -> str:
    """Generate a unique shape ID.

    Returns:
        Unique UUID string
    """
    return str(uuid.uuid4())


def create_line(
    start: Point2D,
    end: Point2D,
    frame_number: int,
    color: Tuple[int, int, int] = (255, 255, 0),
    thickness: int = 2,
    label: str = ""
) -> Line:
    """Factory function to create a Line shape.

    Args:
        start: Starting point
        end: Ending point
        frame_number: Frame number
        color: RGB color tuple
        thickness: Line thickness
        label: Optional label

    Returns:
        Line instance
    """
    return Line(
        id=generate_shape_id(),
        type="line",
        color=color,
        thickness=thickness,
        frame_number=frame_number,
        created_at=time.time(),
        start=start,
        end=end,
        label=label
    )


def create_angle(
    point1: Point2D,
    vertex: Point2D,
    point3: Point2D,
    frame_number: int,
    color: Tuple[int, int, int] = (255, 255, 0),
    thickness: int = 2,
    label: str = "",
    show_arc: bool = True
) -> Angle:
    """Factory function to create an Angle shape.

    Args:
        point1: First point
        vertex: Vertex point
        point3: Third point
        frame_number: Frame number
        color: RGB color tuple
        thickness: Line thickness
        label: Optional label
        show_arc: Whether to show arc

    Returns:
        Angle instance
    """
    return Angle(
        id=generate_shape_id(),
        type="angle",
        color=color,
        thickness=thickness,
        frame_number=frame_number,
        created_at=time.time(),
        point1=point1,
        vertex=vertex,
        point3=point3,
        label=label,
        show_arc=show_arc
    )


def create_circle(
    center: Point2D,
    radius: float,
    frame_number: int,
    color: Tuple[int, int, int] = (255, 255, 0),
    thickness: int = 2,
    label: str = "",
    fill: bool = False
) -> Circle:
    """Factory function to create a Circle shape.

    Args:
        center: Center point
        radius: Radius in pixels
        frame_number: Frame number
        color: RGB color tuple
        thickness: Line thickness
        label: Optional label
        fill: Whether to fill circle

    Returns:
        Circle instance
    """
    return Circle(
        id=generate_shape_id(),
        type="circle",
        color=color,
        thickness=thickness,
        frame_number=frame_number,
        created_at=time.time(),
        center=center,
        radius=radius,
        label=label,
        fill=fill
    )
