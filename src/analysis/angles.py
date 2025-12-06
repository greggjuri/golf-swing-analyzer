"""Core angle calculation utilities.

This module provides fundamental angle calculation functions for analyzing
golf swing mechanics. All angles are in degrees unless otherwise specified.
"""

import logging
from typing import Tuple, Optional, Union

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# Type aliases
Point2D = Union[Tuple[float, float], NDArray[np.float64]]
Vector2D = NDArray[np.float64]
Angle = float
AngleRadians = float


def degrees_to_radians(degrees: Angle) -> AngleRadians:
    """Convert degrees to radians.

    Args:
        degrees: Angle in degrees

    Returns:
        Angle in radians
    """
    return float(np.radians(degrees))


def radians_to_degrees(radians: AngleRadians) -> Angle:
    """Convert radians to degrees.

    Args:
        radians: Angle in radians

    Returns:
        Angle in degrees
    """
    return float(np.degrees(radians))


def distance_between_points(point1: Point2D, point2: Point2D) -> float:
    """Calculate Euclidean distance between two points.

    Args:
        point1: First point (x, y)
        point2: Second point (x, y)

    Returns:
        Distance between points
    """
    p1 = np.array(point1, dtype=float)
    p2 = np.array(point2, dtype=float)
    return float(np.linalg.norm(p2 - p1))


def angle_between_vectors(vector1: Vector2D, vector2: Vector2D) -> Angle:
    """Calculate angle between two vectors.

    Args:
        vector1: First vector as 2D numpy array
        vector2: Second vector as 2D numpy array

    Returns:
        Angle in degrees (0-180)

    Raises:
        ValueError: If either vector has zero length
    """
    v1 = np.array(vector1, dtype=float)
    v2 = np.array(vector2, dtype=float)

    # Calculate norms
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    if v1_norm == 0:
        raise ValueError("First vector has zero length")
    if v2_norm == 0:
        raise ValueError("Second vector has zero length")

    # Normalize vectors
    v1_unit = v1 / v1_norm
    v2_unit = v2 / v2_norm

    # Calculate dot product
    dot_product = np.dot(v1_unit, v2_unit)

    # Clamp to [-1, 1] to handle floating point errors
    dot_product = np.clip(dot_product, -1.0, 1.0)

    # Calculate angle in radians, convert to degrees
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)

    return float(angle_deg)


def angle_between_points(
    point1: Point2D,
    vertex: Point2D,
    point2: Point2D
) -> Angle:
    """Calculate angle formed by three points.

    The angle is measured at the vertex point.

    Args:
        point1: First point
        vertex: Vertex point (angle measured here)
        point2: Third point

    Returns:
        Angle in degrees (0-180)

    Raises:
        ValueError: If any points are duplicate or collinear
    """
    # Convert to numpy arrays
    p1 = np.array(point1, dtype=float)
    v = np.array(vertex, dtype=float)
    p2 = np.array(point2, dtype=float)

    # Create vectors from vertex to other points
    vec1 = p1 - v
    vec2 = p2 - v

    # Check for duplicate points
    if np.linalg.norm(vec1) == 0:
        raise ValueError("point1 and vertex are identical")
    if np.linalg.norm(vec2) == 0:
        raise ValueError("point2 and vertex are identical")

    # Calculate angle using vector method
    return angle_between_vectors(vec1, vec2)


def angle_from_horizontal(line_start: Point2D, line_end: Point2D) -> Angle:
    """Calculate angle of line relative to horizontal.

    Args:
        line_start: Starting point of line
        line_end: Ending point of line

    Returns:
        Angle in degrees (-90 to 90, positive = counterclockwise from horizontal)

    Raises:
        ValueError: If points are identical
    """
    p1 = np.array(line_start, dtype=float)
    p2 = np.array(line_end, dtype=float)

    # Calculate direction vector
    direction = p2 - p1

    if np.linalg.norm(direction) == 0:
        raise ValueError("line_start and line_end are identical")

    # Use atan2 for proper quadrant handling
    angle_rad = np.arctan2(direction[1], direction[0])
    angle_deg = np.degrees(angle_rad)

    return float(angle_deg)


def angle_from_vertical(line_start: Point2D, line_end: Point2D) -> Angle:
    """Calculate angle of line relative to vertical.

    In image coordinates where y increases downward, vertical is downward.

    Args:
        line_start: Starting point of line
        line_end: Ending point of line

    Returns:
        Angle in degrees (-90 to 90, positive = clockwise from vertical)

    Raises:
        ValueError: If points are identical
    """
    p1 = np.array(line_start, dtype=float)
    p2 = np.array(line_end, dtype=float)

    # Calculate direction vector
    direction = p2 - p1

    if np.linalg.norm(direction) == 0:
        raise ValueError("line_start and line_end are identical")

    # In image coordinates, y increases downward
    # Vertical reference vector is (0, 1) pointing down
    # Angle from vertical using atan2(x, y)
    angle_rad = np.arctan2(direction[0], direction[1])
    angle_deg = np.degrees(angle_rad)

    return float(angle_deg)


def normalize_angle(angle: Angle, range_type: str = "0-360") -> Angle:
    """Normalize angle to specified range.

    Args:
        angle: Angle in degrees
        range_type: One of "0-360", "-180-180", or "0-180"

    Returns:
        Normalized angle in specified range

    Raises:
        ValueError: If range_type is invalid
    """
    if range_type == "0-360":
        # Normalize to [0, 360)
        return float(angle % 360.0)

    elif range_type == "-180-180":
        # Normalize to [-180, 180)
        normalized = angle % 360.0
        if normalized > 180.0:
            normalized -= 360.0
        return float(normalized)

    elif range_type == "0-180":
        # Normalize to [0, 180]
        # Take absolute value and wrap to [0, 180]
        normalized = abs(angle) % 360.0
        if normalized > 180.0:
            normalized = 360.0 - normalized
        return float(normalized)

    else:
        raise ValueError(
            f"Invalid range_type: {range_type}. "
            f"Must be '0-360', '-180-180', or '0-180'"
        )


def line_slope(point1: Point2D, point2: Point2D) -> Optional[float]:
    """Calculate slope of line through two points.

    Args:
        point1: First point
        point2: Second point

    Returns:
        Slope value, or None if line is vertical

    Raises:
        ValueError: If points are identical
    """
    p1 = np.array(point1, dtype=float)
    p2 = np.array(point2, dtype=float)

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    if dx == 0 and dy == 0:
        raise ValueError("Points are identical")

    if dx == 0:
        # Vertical line
        return None

    return float(dy / dx)


def point_to_line_distance(
    point: Point2D,
    line_start: Point2D,
    line_end: Point2D
) -> float:
    """Calculate perpendicular distance from point to line.

    Args:
        point: Point to measure distance from
        line_start: Starting point of line
        line_end: Ending point of line

    Returns:
        Perpendicular distance from point to line

    Raises:
        ValueError: If line start and end are identical
    """
    # Convert to numpy arrays
    p = np.array(point, dtype=float)
    l1 = np.array(line_start, dtype=float)
    l2 = np.array(line_end, dtype=float)

    # Line direction vector
    line_vec = l2 - l1
    line_len = np.linalg.norm(line_vec)

    if line_len == 0:
        raise ValueError("line_start and line_end are identical")

    # Vector from line start to point
    point_vec = p - l1

    # Cross product in 2D gives signed area of parallelogram
    # cross = x1*y2 - y1*x2
    cross = line_vec[0] * point_vec[1] - line_vec[1] * point_vec[0]

    # Distance = |area| / base
    distance = abs(cross) / line_len

    return float(distance)


def project_point_onto_line(
    point: Point2D,
    line_start: Point2D,
    line_end: Point2D
) -> Point2D:
    """Project point onto line (find closest point on line).

    Args:
        point: Point to project
        line_start: Starting point of line
        line_end: Ending point of line

    Returns:
        Projected point on the line

    Raises:
        ValueError: If line start and end are identical
    """
    # Convert to numpy arrays
    p = np.array(point, dtype=float)
    l1 = np.array(line_start, dtype=float)
    l2 = np.array(line_end, dtype=float)

    # Line direction vector
    line_vec = l2 - l1
    line_len_sq = np.dot(line_vec, line_vec)

    if line_len_sq == 0:
        raise ValueError("line_start and line_end are identical")

    # Vector from line start to point
    point_vec = p - l1

    # Project point_vec onto line_vec
    # t = dot(point_vec, line_vec) / ||line_vec||^2
    t = np.dot(point_vec, line_vec) / line_len_sq

    # Calculate projection point
    projection = l1 + t * line_vec

    return tuple(projection)  # type: ignore[return-value]


def line_intersection(
    line1_start: Point2D,
    line1_end: Point2D,
    line2_start: Point2D,
    line2_end: Point2D
) -> Optional[Point2D]:
    """Find intersection point of two lines.

    Uses parametric line equations to find intersection.

    Args:
        line1_start: Start of first line
        line1_end: End of first line
        line2_start: Start of second line
        line2_end: End of second line

    Returns:
        Intersection point as tuple (x, y), or None if lines are parallel

    Raises:
        ValueError: If either line has zero length
    """
    # Convert to numpy arrays
    p1 = np.array(line1_start, dtype=float)
    p2 = np.array(line1_end, dtype=float)
    p3 = np.array(line2_start, dtype=float)
    p4 = np.array(line2_end, dtype=float)

    # Direction vectors
    d1 = p2 - p1
    d2 = p4 - p3

    if np.linalg.norm(d1) == 0:
        raise ValueError("First line has zero length")
    if np.linalg.norm(d2) == 0:
        raise ValueError("Second line has zero length")

    # Solve parametric equations:
    # p1 + t*d1 = p3 + s*d2
    # Rearrange: t*d1 - s*d2 = p3 - p1

    # This gives us a 2x2 system:
    # d1[0]*t - d2[0]*s = (p3-p1)[0]
    # d1[1]*t - d2[1]*s = (p3-p1)[1]

    # Coefficient matrix
    A = np.array([[d1[0], -d2[0]],
                  [d1[1], -d2[1]]])

    # Right-hand side
    b = p3 - p1

    # Check if lines are parallel (determinant = 0)
    det = np.linalg.det(A)
    if abs(det) < 1e-10:
        return None

    # Solve for t and s
    params = np.linalg.solve(A, b)
    t = params[0]

    # Calculate intersection point
    intersection = p1 + t * d1

    return tuple(intersection)  # type: ignore[return-value]
