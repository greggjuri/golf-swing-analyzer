"""GUI module for Golf Swing Analyzer.

Provides a modern F1 design studio-inspired interface with glass morphism,
black/white/silver color scheme, and premium aesthetic.

Main components:
- MainWindow: Application shell with video player and analysis panels
- VideoPlayerWidget: Professional video playback with controls
- AnalysisPanelWidget: Metrics display and overlay controls
- TimelineWidget: Frame navigation with key position markers
- F1Theme: Design system and style sheets
"""

from .theme import F1Theme
from .main_window import MainWindow
from .video_player import VideoPlayerWidget
from .analysis_panel import AnalysisPanelWidget
from .timeline import TimelineWidget

__all__ = [
    'F1Theme',
    'MainWindow',
    'VideoPlayerWidget',
    'AnalysisPanelWidget',
    'TimelineWidget',
]
