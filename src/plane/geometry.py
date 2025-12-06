"""3D plane geometry and mathematical operations.

This module provides the foundational mathematics for working with
3D planes, including plane fitting, point projections, and geometric
calculations.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List
import math

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Point3D:
    """3D point in space.

    Coordinates use standard camera/screen coordinate system:
    - X-axis: Left (-) to Right (+)
    - Y-axis: Top (-) to Bottom (+) in screen space
    - Z-axis: Away from camera (-) to Toward camera (+)
    """

    x: float
    y: float
    z: float

    def to_array(self) -> np.ndarray:
        """Convert to numpy array.

        Returns:
            Array of [x, y, z]
        """
        return np.array([self.x, self.y, self.z])

    def distance_to(self, other: 'Point3D') -> float:
        """Calculate Euclidean distance to another point.

        Args:
            other: Target point

        Returns:
            Distance between points
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)


@dataclass
class Plane3D:
    """3D plane in normal form: ax + by + cz + d = 0.

    The plane is defined by its normal vector (a, b, c) and
    distance from origin d. The normal vector should be unit length.
    """

    a: float  # Normal vector x component
    b: float  # Normal vector y component
    c: float  # Normal vector z component
    d: float  # Distance from origin

    def normal_vector(self) -> np.ndarray:
        """Get unit normal vector.

        Returns:
            Unit normal vector as [a, b, c]
        """
        return np.array([self.a, self.b, self.c])

    def normalize(self) -> 'Plane3D':
        """Return plane with normalized normal vector.

        Returns:
            New Plane3D with unit normal vector
        """
        magnitude = math.sqrt(self.a * self.a + self.b * self.b + self.c * self.c)

        if magnitude < 1e-10:
            raise ValueError("Cannot normalize plane with zero normal vector")

        return Plane3D(
            self.a / magnitude,
            self.b / magnitude,
            self.c / magnitude,
            self.d / magnitude
        )

    def point_distance(self, point: Point3D) -> float:
        """Calculate perpendicular distance from point to plane.

        Args:
            point: Point to measure distance from

        Returns:
            Signed distance (positive = above plane, negative = below)
        """
        # Ensure normalized
        normalized = self.normalize()

        # Distance = |ax + by + cz + d| / sqrt(a² + b² + c²)
        # Since normalized, denominator = 1
        return (
            normalized.a * point.x +
            normalized.b * point.y +
            normalized.c * point.z +
            normalized.d
        )

    def project_point(self, point: Point3D) -> Point3D:
        """Project point onto plane.

        Args:
            point: Point to project

        Returns:
            Closest point on plane
        """
        # Distance from point to plane
        dist = self.point_distance(point)

        # Normal vector
        normal = self.normalize().normal_vector()

        # Projected point = original - distance * normal
        projected = point.to_array() - dist * normal

        return Point3D(projected[0], projected[1], projected[2])

    def angle_to_horizontal(self) -> float:
        """Angle of plane relative to horizontal ground.

        Returns:
            Angle in degrees (0 = horizontal, 90 = vertical)
        """
        normal = self.normalize().normal_vector()

        # Horizontal plane has normal [0, 1, 0] (pointing up in screen coords)
        horizontal_normal = np.array([0, 1, 0])

        # Angle between normals
        cos_angle = np.dot(normal, horizontal_normal)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)

        angle_rad = math.acos(abs(cos_angle))
        return math.degrees(angle_rad)

    def angle_to_target_line(self, target_direction: np.ndarray) -> float:
        """Angle of plane relative to target direction.

        Args:
            target_direction: Direction vector to target (e.g., [0, 1, 0])

        Returns:
            Angle in degrees
        """
        normal = self.normalize().normal_vector()

        # Normalize target direction
        target_norm = target_direction / np.linalg.norm(target_direction)

        # Angle between normal and target
        cos_angle = np.dot(normal, target_norm)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)

        angle_rad = math.acos(abs(cos_angle))
        return math.degrees(angle_rad)


def fit_plane_svd(points: List[Point3D]) -> Plane3D:
    """Fit best-fit plane using SVD (Singular Value Decomposition).

    Uses principal component analysis to find the plane that minimizes
    perpendicular distance to all points.

    Args:
        points: List of 3D points to fit plane to

    Returns:
        Best-fit Plane3D

    Raises:
        ValueError: If fewer than 3 points provided
    """
    if len(points) < 3:
        raise ValueError(f"Need at least 3 points to fit plane, got {len(points)}")

    # Convert to numpy array
    point_array = np.array([[p.x, p.y, p.z] for p in points])

    # Calculate centroid
    centroid = np.mean(point_array, axis=0)

    # Center points
    centered = point_array - centroid

    # SVD decomposition: centered = U * S * V^T
    # Normal vector is the right singular vector with smallest singular value
    _, _, Vt = np.linalg.svd(centered)

    # Normal is last row of V^T (corresponds to smallest singular value)
    normal = Vt[-1]
    a, b, c = normal

    # Calculate d: plane passes through centroid
    # ax + by + cz + d = 0
    # d = -(ax + by + cz) for centroid
    d = -np.dot(normal, centroid)

    return Plane3D(a, b, c, d)


def plane_line_intersection(
    plane: Plane3D,
    line_point: Point3D,
    line_direction: np.ndarray
) -> Optional[Point3D]:
    """Find intersection of plane and line.

    Args:
        plane: Plane to intersect with
        line_point: Point on the line
        line_direction: Direction vector of line

    Returns:
        Intersection point, or None if line is parallel to plane
    """
    # Normalize plane
    normalized = plane.normalize()
    normal = normalized.normal_vector()

    # Check if line is parallel to plane
    # Line parallel if direction perpendicular to normal
    denominator = np.dot(normal, line_direction)

    if abs(denominator) < 1e-10:
        # Line parallel to plane
        return None

    # Calculate parameter t where line intersects plane
    # Line: P = line_point + t * line_direction
    # Plane: dot(normal, P) + d = 0
    # Solving: dot(normal, line_point + t * line_direction) + d = 0
    numerator = -(
        normal[0] * line_point.x +
        normal[1] * line_point.y +
        normal[2] * line_point.z +
        normalized.d
    )
    t = numerator / denominator

    # Calculate intersection point
    intersection = line_point.to_array() + t * line_direction

    return Point3D(intersection[0], intersection[1], intersection[2])


def angle_between_planes(plane1: Plane3D, plane2: Plane3D) -> float:
    """Calculate angle between two planes.

    Args:
        plane1: First plane
        plane2: Second plane

    Returns:
        Angle in degrees (0-90)
    """
    # Normalize planes
    normal1 = plane1.normalize().normal_vector()
    normal2 = plane2.normalize().normal_vector()

    # Angle between normals
    cos_angle = np.dot(normal1, normal2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angle_rad = math.acos(abs(cos_angle))
    return math.degrees(angle_rad)


def weighted_plane_fit(
    points: List[Point3D],
    weights: List[float]
) -> Plane3D:
    """Fit plane with weighted points.

    Points with higher weights have more influence on the fitted plane.

    Args:
        points: List of 3D points
        weights: Weight for each point (must be same length as points)

    Returns:
        Best-fit weighted Plane3D

    Raises:
        ValueError: If points and weights have different lengths
        ValueError: If fewer than 3 points provided
    """
    if len(points) != len(weights):
        raise ValueError(
            f"Points and weights must have same length: "
            f"{len(points)} != {len(weights)}"
        )

    if len(points) < 3:
        raise ValueError(f"Need at least 3 points to fit plane, got {len(points)}")

    # Convert to numpy arrays
    point_array = np.array([[p.x, p.y, p.z] for p in points])
    weight_array = np.array(weights)

    # Normalize weights
    weight_sum = np.sum(weight_array)
    if weight_sum < 1e-10:
        raise ValueError("Total weight must be positive")

    normalized_weights = weight_array / weight_sum

    # Calculate weighted centroid
    centroid = np.sum(
        point_array * normalized_weights[:, np.newaxis],
        axis=0
    )

    # Center points
    centered = point_array - centroid

    # Weight the centered points
    weighted_centered = centered * np.sqrt(normalized_weights)[:, np.newaxis]

    # SVD on weighted points
    _, _, Vt = np.linalg.svd(weighted_centered)

    # Normal is last row of V^T
    normal = Vt[-1]
    a, b, c = normal

    # Calculate d using centroid
    d = -np.dot(normal, centroid)

    return Plane3D(a, b, c, d)
