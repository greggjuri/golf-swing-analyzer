"""Video player widget with professional playback controls."""

import logging
from typing import Optional
import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont

from .theme import F1Theme

logger = logging.getLogger(__name__)


class VideoDisplayLabel(QLabel):
    """Custom label for displaying video frames with scaling."""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize video display label."""
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(F1Theme.get_video_display_stylesheet())
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setScaledContents(False)

        # Placeholder text
        self.setText("No Video Loaded")
        font = QFont(F1Theme.FONT_FAMILY)
        font.setPixelSize(F1Theme.FONT_SIZE_LARGE)
        self.setFont(font)

    def set_frame(self, frame: np.ndarray):
        """Display a video frame.

        Args:
            frame: Video frame as numpy array (BGR format)
        """
        if frame is None or frame.size == 0:
            return

        # Convert BGR to RGB
        rgb_frame = frame[:, :, ::-1] if len(frame.shape) == 3 else frame

        # Get frame dimensions
        height, width = rgb_frame.shape[:2]
        bytes_per_line = 3 * width if len(rgb_frame.shape) == 3 else width

        # Convert to QImage
        if len(rgb_frame.shape) == 3:
            q_image = QImage(
                rgb_frame.data,
                width, height,
                bytes_per_line,
                QImage.Format_RGB888
            )
        else:
            q_image = QImage(
                rgb_frame.data,
                width, height,
                bytes_per_line,
                QImage.Format_Grayscale8
            )

        # Scale to fit label while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)


class PlaybackControlsWidget(QWidget):
    """Professional playback controls with F1 styling."""

    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    next_frame_clicked = pyqtSignal()
    prev_frame_clicked = pyqtSignal()
    speed_changed = pyqtSignal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize playback controls."""
        super().__init__(parent)

        self.is_playing = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up control buttons UI."""
        layout = QHBoxLayout()
        layout.setSpacing(F1Theme.PADDING_SMALL)
        layout.setContentsMargins(0, 0, 0, 0)

        # Previous frame button
        self.prev_btn = QPushButton("◀◀")
        self.prev_btn.setToolTip("Previous Frame")
        self.prev_btn.setMaximumWidth(50)
        self.prev_btn.clicked.connect(self.prev_frame_clicked.emit)

        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setToolTip("Play")
        self.play_pause_btn.setMaximumWidth(60)
        self.play_pause_btn.clicked.connect(self._on_play_pause_clicked)

        # Stop button
        self.stop_btn = QPushButton("■")
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.setMaximumWidth(50)
        self.stop_btn.clicked.connect(self._on_stop_clicked)

        # Next frame button
        self.next_btn = QPushButton("▶▶")
        self.next_btn.setToolTip("Next Frame")
        self.next_btn.setMaximumWidth(50)
        self.next_btn.clicked.connect(self.next_frame_clicked.emit)

        # Speed selector
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet(f"color: {F1Theme.WHITE_MUTED};")

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.setMaximumWidth(80)
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)

        # Add to layout
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.play_pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.next_btn)
        layout.addStretch()
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_combo)

        self.setLayout(layout)

    def _on_play_pause_clicked(self):
        """Handle play/pause button click."""
        if self.is_playing:
            self.pause_clicked.emit()
            self.set_playing(False)
        else:
            self.play_clicked.emit()
            self.set_playing(True)

    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_clicked.emit()
        self.set_playing(False)

    def _on_speed_changed(self, speed_text: str):
        """Handle speed change.

        Args:
            speed_text: Speed as string (e.g., "1x")
        """
        speed = float(speed_text.replace("x", ""))
        self.speed_changed.emit(speed)

    def set_playing(self, playing: bool):
        """Update play/pause button state.

        Args:
            playing: True if playing, False if paused
        """
        self.is_playing = playing
        if playing:
            self.play_pause_btn.setText("⏸")
            self.play_pause_btn.setToolTip("Pause")
        else:
            self.play_pause_btn.setText("▶")
            self.play_pause_btn.setToolTip("Play")


class VideoPlayerWidget(QWidget):
    """Video player with playback controls and display.

    Displays video frames with analysis overlays and provides
    professional playback controls.

    Signals:
        frame_changed(int): Emitted when frame changes
        playback_started(): Emitted when playback starts
        playback_stopped(): Emitted when playback stops
    """

    frame_changed = pyqtSignal(int)
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize video player widget."""
        super().__init__(parent)

        # Playback state
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30.0
        self.playback_speed = 1.0
        self.is_playing = False

        # Timer for playback
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._advance_frame)

        # Video data (will be set externally)
        self.get_frame_callback = None  # Function to get frame by number

        self._setup_ui()
        self._connect_signals()

        logger.debug("Initialized VideoPlayerWidget")

    def _setup_ui(self):
        """Set up video player UI."""
        layout = QVBoxLayout()
        layout.setSpacing(F1Theme.PADDING_MEDIUM)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video display
        self.video_display = VideoDisplayLabel()

        # Playback controls
        self.controls = PlaybackControlsWidget()

        # Add to layout
        layout.addWidget(self.video_display, stretch=1)
        layout.addWidget(self.controls)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect internal signals."""
        self.controls.play_clicked.connect(self.play)
        self.controls.pause_clicked.connect(self.pause)
        self.controls.stop_clicked.connect(self.stop)
        self.controls.next_frame_clicked.connect(self.next_frame)
        self.controls.prev_frame_clicked.connect(self.previous_frame)
        self.controls.speed_changed.connect(self.set_playback_speed)

    def load_video(self, total_frames: int, fps: float, get_frame_func):
        """Load video for playback.

        Args:
            total_frames: Total number of frames
            fps: Frames per second
            get_frame_func: Callback function(frame_number) -> numpy array
        """
        self.total_frames = total_frames
        self.fps = fps
        self.get_frame_callback = get_frame_func

        # Reset to first frame
        self.current_frame = 0
        self._update_display()

        logger.info(f"Loaded video: {total_frames} frames @ {fps} fps")

    def play(self):
        """Start playback."""
        if not self.get_frame_callback or self.total_frames == 0:
            return

        self.is_playing = True
        self.controls.set_playing(True)

        # Calculate interval based on fps and speed
        interval_ms = int((1000.0 / self.fps) / self.playback_speed)
        self.playback_timer.start(interval_ms)

        self.playback_started.emit()
        logger.debug("Playback started")

    def pause(self):
        """Pause playback."""
        self.is_playing = False
        self.controls.set_playing(False)
        self.playback_timer.stop()
        logger.debug("Playback paused")

    def stop(self):
        """Stop and reset to start."""
        self.is_playing = False
        self.controls.set_playing(False)
        self.playback_timer.stop()

        self.current_frame = 0
        self._update_display()

        self.playback_stopped.emit()
        logger.debug("Playback stopped")

    def next_frame(self):
        """Advance one frame."""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self._update_display()

    def previous_frame(self):
        """Go back one frame."""
        if self.current_frame > 0:
            self.current_frame -= 1
            self._update_display()

    def seek(self, frame_number: int):
        """Seek to specific frame.

        Args:
            frame_number: Target frame number
        """
        if 0 <= frame_number < self.total_frames:
            self.current_frame = frame_number
            self._update_display()

    def set_playback_speed(self, speed: float):
        """Set playback speed.

        Args:
            speed: Speed multiplier (0.25, 0.5, 1.0, 2.0)
        """
        self.playback_speed = speed

        # Update timer if playing
        if self.is_playing:
            interval_ms = int((1000.0 / self.fps) / self.playback_speed)
            self.playback_timer.setInterval(interval_ms)

        logger.debug(f"Playback speed set to {speed}x")

    def _advance_frame(self):
        """Advance to next frame during playback."""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self._update_display()
        else:
            # Reached end, stop playback
            self.pause()

    def _update_display(self):
        """Update video display with current frame."""
        if self.get_frame_callback:
            frame = self.get_frame_callback(self.current_frame)
            if frame is not None:
                self.video_display.set_frame(frame)

        self.frame_changed.emit(self.current_frame)

    def get_current_frame(self) -> int:
        """Get current frame number.

        Returns:
            Current frame number
        """
        return self.current_frame

    def refresh(self):
        """Refresh current frame display (e.g., after overlay toggle)."""
        self._update_display()
