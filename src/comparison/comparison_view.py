"""Main comparison view widget with dual video players."""

import logging

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QFileDialog, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from ..gui.timeline import TimelineWidget
from ..gui.video_player import VideoDisplayLabel
from .video_side import VideoSide
from .sync_controller import SyncController
from .comparison_toolbar import ComparisonToolbar
from .overlay_renderer import OverlayRenderer
from .overlay_panel import OverlayPanel

logger = logging.getLogger(__name__)


class ComparisonView(QWidget):
    """Side-by-side video comparison widget.

    Displays two videos side by side with synchronized playback
    and independent overlay controls.

    Signals:
        videos_loaded(bool, bool): Emitted when videos load (left, right)
        sync_changed(bool): Emitted when sync state changes
    """

    videos_loaded = pyqtSignal(bool, bool)
    sync_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialize comparison view."""
        super().__init__(parent)

        # Video sides
        self.left_side = VideoSide("Left")
        self.right_side = VideoSide("Right")

        # Synchronization controller
        self.sync_controller = SyncController()

        # Comparison toolbar
        self.comparison_toolbar = ComparisonToolbar()

        # Shared timeline for synchronized playback
        self.shared_timeline = TimelineWidget()

        # Overlay mode components
        self.overlay_renderer = OverlayRenderer()
        self.overlay_panel = OverlayPanel()
        self.overlay_display = VideoDisplayLabel()

        # View mode state
        self.view_mode = 'side-by-side'  # 'side-by-side' or 'overlay'

        # Playback state
        self.is_playing = False
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._advance_frame)

        self._setup_ui()
        self._connect_signals()

        logger.info("Initialized ComparisonView")

    def _setup_ui(self):
        """Set up comparison layout."""
        from PyQt5.QtWidgets import QHBoxLayout, QRadioButton, QButtonGroup

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Comparison toolbar at top
        main_layout.addWidget(self.comparison_toolbar)

        # View mode toggle
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(10, 5, 10, 5)

        mode_label = QLabel("View Mode:")
        mode_label.setStyleSheet("color: #C0C0C0; font-weight: 600;")
        mode_layout.addWidget(mode_label)

        self.view_mode_group = QButtonGroup(self)
        self.side_by_side_radio = QRadioButton("Side-by-Side")
        self.overlay_radio = QRadioButton("Overlay")
        self.side_by_side_radio.setChecked(True)

        self.view_mode_group.addButton(self.side_by_side_radio, 0)
        self.view_mode_group.addButton(self.overlay_radio, 1)

        mode_layout.addWidget(self.side_by_side_radio)
        mode_layout.addWidget(self.overlay_radio)
        mode_layout.addStretch()

        main_layout.addLayout(mode_layout)

        # Horizontal splitter for two videos (side-by-side mode)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_side)
        self.splitter.addWidget(self.right_side)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # Style the splitter handle
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #C0C0C0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #E8E8E8;
            }
        """)

        main_layout.addWidget(self.splitter, stretch=1)

        # Overlay mode container (hidden by default)
        overlay_container = QWidget()
        overlay_layout = QHBoxLayout()
        overlay_layout.setSpacing(5)
        overlay_layout.setContentsMargins(0, 0, 0, 0)

        # Overlay display (center)
        self.overlay_display.setMinimumSize(600, 400)
        overlay_layout.addWidget(self.overlay_display, stretch=1)

        # Overlay controls (right side)
        self.overlay_panel.setMaximumWidth(250)
        overlay_layout.addWidget(self.overlay_panel)

        overlay_container.setLayout(overlay_layout)
        self.overlay_container = overlay_container
        self.overlay_container.setVisible(False)  # Hidden by default

        main_layout.addWidget(self.overlay_container, stretch=1)

        # Shared timeline at bottom
        main_layout.addWidget(self.shared_timeline)

        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect widget signals to slots."""
        # Toolbar signals
        self.comparison_toolbar.load_left_requested.connect(self.load_left_video_dialog)
        self.comparison_toolbar.load_right_requested.connect(self.load_right_video_dialog)
        self.comparison_toolbar.swap_requested.connect(self.swap_videos)
        self.comparison_toolbar.sync_toggled.connect(self._on_sync_toggled)
        self.comparison_toolbar.screenshot_requested.connect(self.take_screenshot)
        self.comparison_toolbar.calibrate_requested.connect(self.calibrate_sync)

        # Video side signals
        self.left_side.video_loaded.connect(self._on_left_video_loaded)
        self.right_side.video_loaded.connect(self._on_right_video_loaded)
        self.left_side.play_requested.connect(self.play)
        self.right_side.play_requested.connect(self.play)
        self.left_side.pause_requested.connect(self.pause)
        self.right_side.pause_requested.connect(self.pause)

        # Timeline signals
        self.shared_timeline.frame_selected.connect(self.seek_to_frame)

        # View mode signals
        self.view_mode_group.buttonClicked.connect(self._on_view_mode_changed)

        # Overlay panel signals
        self.overlay_panel.alpha_changed.connect(self._on_overlay_settings_changed)
        self.overlay_panel.blend_mode_changed.connect(self._on_overlay_settings_changed)
        self.overlay_panel.left_tint_toggled.connect(self._on_overlay_settings_changed)
        self.overlay_panel.right_tint_toggled.connect(self._on_overlay_settings_changed)

    def _on_view_mode_changed(self):
        """Handle view mode toggle between side-by-side and overlay."""
        if self.side_by_side_radio.isChecked():
            self.view_mode = 'side-by-side'
            self.splitter.setVisible(True)
            self.overlay_container.setVisible(False)
            logger.info("Switched to side-by-side mode")
        else:
            self.view_mode = 'overlay'
            self.splitter.setVisible(False)
            self.overlay_container.setVisible(True)
            self._update_overlay_display()
            logger.info("Switched to overlay mode")

    def _on_overlay_settings_changed(self, *args):
        """Handle overlay settings change (alpha, blend mode, tints).

        Args:
            *args: Variable arguments from different signals (ignored)
        """
        if self.view_mode == 'overlay':
            self._update_overlay_display()

    def _update_overlay_display(self):
        """Update overlay display with current frame blended."""
        if not (self.left_side.is_video_loaded() and
                self.right_side.is_video_loaded()):
            return

        # Get current frame from both sides
        frame_num = self.left_side.get_current_frame()

        left_frame = self.left_side.get_frame(frame_num)
        if self.sync_controller.is_sync_enabled():
            right_frame_num = self.sync_controller.get_synced_frame(
                frame_num,
                max_frame=self.right_side.get_total_frames() - 1
            )
        else:
            right_frame_num = self.right_side.get_current_frame()

        right_frame = self.right_side.get_frame(right_frame_num)

        if left_frame is None or right_frame is None:
            return

        # Get overlay settings
        alpha = self.overlay_panel.get_alpha()
        blend_mode = self.overlay_panel.get_blend_mode()

        # Get tint settings
        tint1 = (255, 100, 100) if self.overlay_panel.is_left_tint_enabled() else None
        tint2 = (100, 255, 100) if self.overlay_panel.is_right_tint_enabled() else None

        # Render blended frame
        try:
            blended = self.overlay_renderer.render(
                left_frame, right_frame,
                alpha=alpha,
                blend_mode=blend_mode,
                tint1=tint1,
                tint2=tint2
            )

            # Display blended frame
            self.overlay_display.set_frame(blended)

        except Exception as e:
            logger.error(f"Error rendering overlay: {e}", exc_info=True)

    def load_left_video_dialog(self):
        """Open file dialog to load left video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Left Video",
            "",
            "Video Files (*.mp4 *.mov *.avi);;All Files (*)"
        )

        if file_path:
            self.load_left_video(file_path)

    def load_right_video_dialog(self):
        """Open file dialog to load right video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Right Video",
            "",
            "Video Files (*.mp4 *.mov *.avi);;All Files (*)"
        )

        if file_path:
            self.load_right_video(file_path)

    def load_left_video(self, video_path: str):
        """Load video on left side.

        Args:
            video_path: Path to video file
        """
        try:
            self.left_side.load_video(video_path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Video",
                f"Failed to load left video:\n{str(e)}"
            )

    def load_right_video(self, video_path: str):
        """Load video on right side.

        Args:
            video_path: Path to video file
        """
        try:
            self.right_side.load_video(video_path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Video",
                f"Failed to load right video:\n{str(e)}"
            )

    def _on_left_video_loaded(self, video_path: str):
        """Handle left video loaded.

        Args:
            video_path: Path to loaded video
        """
        self._update_timeline()
        self._update_toolbar_state()
        self.videos_loaded.emit(True, self.right_side.is_video_loaded())

    def _on_right_video_loaded(self, video_path: str):
        """Handle right video loaded.

        Args:
            video_path: Path to loaded video
        """
        self._update_timeline()
        self._update_toolbar_state()
        self.videos_loaded.emit(self.left_side.is_video_loaded(), True)

    def _update_timeline(self):
        """Update shared timeline based on loaded videos."""
        if self.left_side.is_video_loaded():
            # Use left video for timeline
            self.shared_timeline.set_total_frames(
                self.left_side.get_total_frames(),
                self.left_side.fps
            )
        elif self.right_side.is_video_loaded():
            # Use right video if only right is loaded
            self.shared_timeline.set_total_frames(
                self.right_side.get_total_frames(),
                self.right_side.fps
            )

    def _update_toolbar_state(self):
        """Update toolbar button states based on loaded videos."""
        self.comparison_toolbar.set_videos_loaded(
            self.left_side.is_video_loaded(),
            self.right_side.is_video_loaded()
        )

    def swap_videos(self):
        """Swap left and right videos."""
        # Store paths
        left_path = self.left_side.get_video_path()
        right_path = self.right_side.get_video_path()

        if not (left_path and right_path):
            return

        # Reload in swapped positions
        self.load_right_video(left_path)
        self.load_left_video(right_path)

        logger.info("Swapped left and right videos")

    def _on_sync_toggled(self, enabled: bool):
        """Handle sync toggle.

        Args:
            enabled: Whether sync is enabled
        """
        self.sync_controller.set_sync_enabled(enabled)
        self.sync_changed.emit(enabled)

        logger.debug(f"Sync {'enabled' if enabled else 'disabled'}")

    def play(self):
        """Play both videos (if synced) or active video."""
        if self.is_playing:
            return

        self.is_playing = True

        # Update playback controls
        self.left_side.controls.set_playing(True)
        if self.sync_controller.is_sync_enabled():
            self.right_side.controls.set_playing(True)

        # Start playback timer
        # Use left video's fps
        if self.left_side.is_video_loaded():
            interval_ms = int(1000.0 / self.left_side.fps)
            self.playback_timer.start(interval_ms)

        logger.debug("Playback started")

    def pause(self):
        """Pause both videos."""
        if not self.is_playing:
            return

        self.is_playing = False
        self.playback_timer.stop()

        # Update playback controls
        self.left_side.controls.set_playing(False)
        self.right_side.controls.set_playing(False)

        logger.debug("Playback paused")

    def _advance_frame(self):
        """Advance to next frame during playback."""
        if not self.is_playing:
            return

        # Advance left
        if self.left_side.is_video_loaded():
            left_frame = self.left_side.get_current_frame()
            if left_frame < self.left_side.get_total_frames() - 1:
                self.left_side.seek(left_frame + 1)
                self.shared_timeline.set_current_frame(left_frame + 1)
            else:
                # Reached end
                self.pause()
                return

        # Advance right (if synced)
        if self.sync_controller.is_sync_enabled() and self.right_side.is_video_loaded():
            right_frame = self.sync_controller.get_synced_frame(
                self.left_side.get_current_frame(),
                max_frame=self.right_side.get_total_frames() - 1
            )
            self.right_side.seek(right_frame)

        # Update overlay display if in overlay mode
        if self.view_mode == 'overlay':
            self._update_overlay_display()

    def seek_to_frame(self, frame_number: int):
        """Seek both videos to frame (if synced).

        Args:
            frame_number: Frame number to seek to
        """
        # Seek left
        if self.left_side.is_video_loaded():
            self.left_side.seek(frame_number)

        # Seek right (if synced)
        if self.sync_controller.is_sync_enabled() and self.right_side.is_video_loaded():
            right_frame = self.sync_controller.get_synced_frame(
                frame_number,
                max_frame=self.right_side.get_total_frames() - 1
            )
            self.right_side.seek(right_frame)

        # Update overlay display if in overlay mode
        if self.view_mode == 'overlay':
            self._update_overlay_display()

    def calibrate_sync(self):
        """Calibrate sync from current positions."""
        if not (self.left_side.is_video_loaded() and self.right_side.is_video_loaded()):
            return

        left_frame = self.left_side.get_current_frame()
        right_frame = self.right_side.get_current_frame()

        self.sync_controller.calibrate_sync(left_frame, right_frame)

        # Update display
        offset_text = self.sync_controller.get_offset_display()
        self.comparison_toolbar.set_sync_offset_display(offset_text)

        QMessageBox.information(
            self,
            "Sync Calibrated",
            f"Sync calibrated:\nLeft frame {left_frame} = "
            f"Right frame {right_frame}\n\n{offset_text}"
        )

        logger.info(f"Sync calibrated: left {left_frame} = right {right_frame}")

    def take_screenshot(self):
        """Take comparison screenshot."""
        import cv2
        import numpy as np
        from PyQt5.QtWidgets import QFileDialog

        # Get current frames
        left_frame = None
        right_frame = None

        if self.left_side.is_video_loaded():
            left_frame = self.left_side.get_frame(self.left_side.get_current_frame())

        if self.right_side.is_video_loaded():
            right_frame = self.right_side.get_frame(self.right_side.get_current_frame())

        if left_frame is None and right_frame is None:
            return

        # Create side-by-side image
        if left_frame is not None and right_frame is not None:
            # Both sides loaded - concatenate horizontally
            comparison_image = np.hstack([left_frame, right_frame])
        elif left_frame is not None:
            # Only left loaded
            comparison_image = left_frame
        else:
            # Only right loaded
            comparison_image = right_frame

        # Save dialog
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Comparison Screenshot",
            "comparison.png",
            "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)"
        )

        if filepath:
            try:
                # Convert BGR to RGB for saving
                comparison_rgb = cv2.cvtColor(comparison_image, cv2.COLOR_BGR2RGB)
                cv2.imwrite(filepath, comparison_rgb)

                QMessageBox.information(
                    self,
                    "Screenshot Saved",
                    f"Comparison screenshot saved to:\n{filepath}"
                )

                logger.info(f"Comparison screenshot saved to {filepath}")

            except Exception as e:
                logger.error(f"Failed to save screenshot: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save screenshot:\n{str(e)}"
                )
