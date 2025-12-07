"""Side-by-side video comparison module.

This module provides tools for comparing two golf swing videos
side-by-side with synchronized playback and independent analysis.

Main components:
- ComparisonView: Main comparison widget with dual video players
- VideoSide: Single side of comparison (video + controls)
- SyncController: Synchronization logic
- ComparisonToolbar: Comparison-specific controls

Example:
    from src.comparison import ComparisonView

    comparison = ComparisonView()
    comparison.load_left_video("swing1.mp4")
    comparison.load_right_video("swing2.mp4")
    comparison.play()
"""

from .sync_controller import SyncController
from .comparison_toolbar import ComparisonToolbar
from .video_side import VideoSide
from .comparison_view import ComparisonView

__all__ = [
    'SyncController',
    'ComparisonToolbar',
    'VideoSide',
    'ComparisonView',
]
