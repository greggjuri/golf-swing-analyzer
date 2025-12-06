"""Analysis utilities for golf swing measurements."""

from .angles import (
    angle_between_points,
    angle_between_vectors,
    angle_from_horizontal,
    angle_from_vertical,
    normalize_angle,
    degrees_to_radians,
    radians_to_degrees,
    distance_between_points,
    line_slope,
    point_to_line_distance,
    project_point_onto_line,
    line_intersection,
)
from .joint_angles import JointAngleCalculator, BodyLandmark
from .club_angles import ClubAngleCalculator

__all__ = [
    # Core angles
    'angle_between_points',
    'angle_between_vectors',
    'angle_from_horizontal',
    'angle_from_vertical',
    'normalize_angle',
    'degrees_to_radians',
    'radians_to_degrees',
    # Geometry
    'distance_between_points',
    'line_slope',
    'point_to_line_distance',
    'project_point_onto_line',
    'line_intersection',
    # Calculators
    'JointAngleCalculator',
    'ClubAngleCalculator',
    'BodyLandmark',
]
