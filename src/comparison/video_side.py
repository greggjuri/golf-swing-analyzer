"""Video side widget for comparison view."""

import logging
from typing import Optional
import numpy as np

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal

from ..gui.widgets import ToggleButton
from ..gui.video_player import VideoDisplayLabel, PlaybackControlsWidget

logger = logging.getLogger(__name__)


class CompactOverlayPanel(QWidget):
    """Compact overlay controls for comparison side.

    Signals:
        overlay_toggled(str, bool): Overlay toggled (name, enabled)
    """

    overlay_toggled = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        """Initialize compact overlay panel."""
        super().__init__(parent)

        self.toggles = {}
        self._setup_ui()

    def _setup_ui(self):
        """Set up compact overlay panel."""
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("OVERLAYS")
        title.setStyleSheet("""
            font-size: 10px;
            font-weight: 600;
            color: #C0C0C0;
            letter-spacing: 1px;
        """)
        layout.addWidget(title)

        # Overlay toggles (compact)
        overlays = [
            ('club_track', 'Club', True),
            ('skeleton', 'Skeleton', False),
            ('angles', 'Angles', False),
            ('swing_plane', 'Plane', False),
        ]

        for key, label, default in overlays:
            toggle = ToggleButton(label)
            toggle.setChecked(default)
            toggle.toggled.connect(
                lambda checked, k=key: self.overlay_toggled.emit(k, checked)
            )
            self.toggles[key] = toggle
            layout.addWidget(toggle)

        layout.addStretch()
        self.setLayout(layout)

    def get_enabled_overlays(self) -> dict:
        """Get enabled overlays.

        Returns:
            Dictionary of overlay_name -> enabled
        """
        return {
            key: toggle.isChecked()
            for key, toggle in self.toggles.items()
        }


class VideoSide(QWidget):
    """One side of the comparison view.

    Contains video player, playback controls, and overlay toggles
    for a single video.

    Signals:
        frame_changed(int): Emitted when frame changes
        video_loaded(str): Emitted when video loads (with path)
        play_requested(): Emitted when play is clicked
        pause_requested(): Emitted when pause is clicked
    """

    frame_changed = pyqtSignal(int)
    video_loaded = pyqtSignal(str)
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()

    def __init__(self, side_name: str, parent=None):
        """Initialize video side.

        Args:
            side_name: "Left" or "Right"
            parent: Parent widget
        """
        super().__init__(parent)

        self.side_name = side_name
        self.video_path = None
        self.video_loader = None
        self.frame_extractor = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30.0

        # Analysis components (independent per side)
        self.viz_engine = None
        self.drawing_manager = None
        self.drawing_renderer = None
        self.club_results = {}
        self.pose_results = {}

        # UI components
        self.video_display = None
        self.controls = None
        self.overlay_panel = None
        self.frame_label = None

        self._setup_ui()

        logger.debug(f"Initialized VideoSide: {side_name}")

    def _setup_ui(self):
        """Set up video side UI."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Title bar
        title_layout = QHBoxLayout()
        title = QLabel(f"{self.side_name} Video")
        title.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #E8E8E8;
            padding: 5px;
        """)
        title_layout.addWidget(title)

        # Frame counter
        self.frame_label = QLabel("No video")
        self.frame_label.setStyleSheet("""
            font-size: 10px;
            color: #C0C0C0;
            padding: 5px;
        """)
        title_layout.addStretch()
        title_layout.addWidget(self.frame_label)

        main_layout.addLayout(title_layout)

        # Horizontal layout for video + overlay panel
        content_layout = QHBoxLayout()
        content_layout.setSpacing(5)

        # Video display area
        video_layout = QVBoxLayout()
        video_layout.setSpacing(5)

        self.video_display = VideoDisplayLabel()
        self.video_display.setMinimumSize(400, 300)
        video_layout.addWidget(self.video_display, stretch=1)

        # Playback controls
        self.controls = PlaybackControlsWidget()
        self.controls.play_clicked.connect(self.play_requested.emit)
        self.controls.pause_clicked.connect(self.pause_requested.emit)
        self.controls.prev_frame_clicked.connect(self.previous_frame)
        self.controls.next_frame_clicked.connect(self.next_frame)
        video_layout.addWidget(self.controls)

        content_layout.addLayout(video_layout, stretch=1)

        # Overlay panel (compact, on the side)
        self.overlay_panel = CompactOverlayPanel()
        self.overlay_panel.overlay_toggled.connect(self._on_overlay_toggled)
        self.overlay_panel.setMaximumWidth(120)
        content_layout.addWidget(self.overlay_panel)

        main_layout.addLayout(content_layout, stretch=1)

        self.setLayout(main_layout)

        # Apply styling
        self.setStyleSheet("""
            VideoSide {
                background-color: #1A1A1A;
                border: 1px solid #2A2A2A;
                border-radius: 5px;
            }
        """)

    def load_video(self, video_path: str):
        """Load a video on this side.

        Args:
            video_path: Path to video file
        """
        try:
            from ..video import VideoLoader, FrameExtractor
            from ..visualization import VisualizationEngine
            from ..drawing import DrawingManager, DrawingRenderer

            # Load video
            self.video_loader = VideoLoader(video_path)
            metadata = self.video_loader.get_metadata()

            # Create frame extractor
            self.frame_extractor = FrameExtractor(self.video_loader)

            # Store video info
            self.video_path = video_path
            self.total_frames = metadata.frame_count
            self.fps = metadata.fps
            self.current_frame = 0

            # Initialize analysis components
            self.viz_engine = VisualizationEngine()
            self.drawing_manager = DrawingManager()
            self.drawing_renderer = DrawingRenderer()

            # Update display
            self._update_frame_label()
            self.seek(0)  # Show first frame

            # Emit signal
            self.video_loaded.emit(video_path)

            logger.info(f"{self.side_name}: Loaded video {video_path} "
                        f"({metadata.frame_count} frames @ {metadata.fps:.1f} fps)")

        except Exception as e:
            logger.error(f"{self.side_name}: Failed to load video: {e}", exc_info=True)
            raise

    def get_frame(self, frame_number: int) -> Optional[np.ndarray]:
        """Get frame with overlays applied.

        Args:
            frame_number: Frame number to get

        Returns:
            Frame as numpy array or None
        """
        if not self.frame_extractor:
            return None

        try:
            # Get raw frame
            frame = self.frame_extractor.extract_frame(frame_number)

            if frame is None:
                return None

            # Apply overlays if enabled
            if self.viz_engine:
                enabled = self.overlay_panel.get_enabled_overlays()

                # Get analysis data for this frame
                club_data = (self.club_results.get(frame_number)
                             if enabled.get('club_track') else None)
                pose_data = (self.pose_results.get(frame_number)
                             if enabled.get('skeleton') else None)

                # Render overlays
                frame = self.viz_engine.render(
                    frame,
                    club_detection=club_data,
                    body_landmarks=pose_data,
                    show_angles=enabled.get('angles', False),
                    show_skeleton=enabled.get('skeleton', False)
                )

            # Apply manual drawings
            if self.drawing_renderer and self.drawing_manager:
                shapes = self.drawing_manager.get_shapes_for_frame(frame_number)
                if shapes:
                    frame = self.drawing_renderer.render(frame, shapes)

            return frame

        except Exception as e:
            logger.error(f"{self.side_name}: Error getting frame {frame_number}: {e}")
            return None

    def seek(self, frame_number: int):
        """Seek to specific frame.

        Args:
            frame_number: Frame number to seek to
        """
        if not self.video_loader:
            return

        # Clamp to valid range
        frame_number = max(0, min(frame_number, self.total_frames - 1))

        self.current_frame = frame_number

        # Get and display frame
        frame = self.get_frame(frame_number)
        if frame is not None:
            self.video_display.set_frame(frame)

        # Update display
        self._update_frame_label()

        # Emit signal
        self.frame_changed.emit(frame_number)

    def next_frame(self):
        """Advance one frame."""
        if self.current_frame < self.total_frames - 1:
            self.seek(self.current_frame + 1)

    def previous_frame(self):
        """Go back one frame."""
        if self.current_frame > 0:
            self.seek(self.current_frame - 1)

    def refresh(self):
        """Refresh current frame display."""
        self.seek(self.current_frame)

    def _update_frame_label(self):
        """Update frame counter label."""
        if self.video_loader:
            self.frame_label.setText(
                f"Frame {self.current_frame + 1} / {self.total_frames}"
            )
        else:
            self.frame_label.setText("No video")

    def _on_overlay_toggled(self, overlay_name: str, enabled: bool):
        """Handle overlay toggle.

        Args:
            overlay_name: Name of overlay
            enabled: Whether enabled
        """
        self.refresh()

    def get_current_frame(self) -> int:
        """Get current frame number.

        Returns:
            Current frame number
        """
        return self.current_frame

    def get_total_frames(self) -> int:
        """Get total frame count.

        Returns:
            Total frames
        """
        return self.total_frames

    def is_video_loaded(self) -> bool:
        """Check if video is loaded.

        Returns:
            True if video is loaded
        """
        return self.video_loader is not None

    def get_video_path(self) -> Optional[str]:
        """Get loaded video path.

        Returns:
            Video path or None
        """
        return self.video_path
