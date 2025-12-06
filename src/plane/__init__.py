"""Swing plane analysis module.

This module provides tools for analyzing the golf swing plane by tracking
the club shaft path through 3D space and calculating the best-fit plane.

Key components:
- Plane3D: 3D plane representation and operations
- PlaneCalculator: Fit plane to shaft positions
- PlaneDetector: Detect swing plane for different phases
- PlaneMetrics: Calculate golf-specific plane metrics
- SwingPlaneAnalyzer: High-level analysis interface
"""

from .geometry import (
    Point3D,
    Plane3D,
    fit_plane_svd,
    plane_line_intersection,
    angle_between_planes
)
from .calculator import PlaneCalculator, ShaftPosition
from .detector import PlaneDetector, SwingPlaneResult
from .metrics import PlaneMetrics, SwingMetrics
from .analyzer import SwingPlaneAnalyzer, SwingPlaneAnalysis

__all__ = [
    # Geometry
    'Point3D',
    'Plane3D',
    'fit_plane_svd',
    'plane_line_intersection',
    'angle_between_planes',

    # Calculator
    'PlaneCalculator',
    'ShaftPosition',

    # Detector
    'PlaneDetector',
    'SwingPlaneResult',

    # Metrics
    'PlaneMetrics',
    'SwingMetrics',

    # Analyzer
    'SwingPlaneAnalyzer',
    'SwingPlaneAnalysis',
]
