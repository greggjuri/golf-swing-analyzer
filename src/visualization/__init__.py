"""Visualization module for rendering analysis overlays on video frames.

This module provides tools to draw club tracking results, body landmarks,
angles, and annotations on video frames.

Main classes:
    VisualizationEngine: Main engine coordinating all renderers
    ClubRenderer: Render club shaft and head overlays
    BodyRenderer: Render body skeleton and joints
    AngleRenderer: Render angle arcs and measurements
    StyleConfig: Configuration for colors and styling

Example:
    from src.visualization import VisualizationEngine, StyleConfig

    engine = VisualizationEngine(style=StyleConfig.high_contrast())
    result_frame = engine.render(frame, club_detection=club_result)
"""

from .styles import StyleConfig, Annotation
from .renderers import ClubRenderer, BodyRenderer, AngleRenderer
from .engine import VisualizationEngine

__all__ = [
    'VisualizationEngine',
    'ClubRenderer',
    'BodyRenderer',
    'AngleRenderer',
    'StyleConfig',
    'Annotation',
]
