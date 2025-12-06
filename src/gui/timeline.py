"""Timeline scrubber widget with key position markers."""

import logging
from typing import Optional, Dict

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

from .theme import F1Theme

logger = logging.getLogger(__name__)


class TimelineWidget(QWidget):
    """Timeline scrubber with key position markers.

    Provides frame-by-frame navigation with visual markers
    for P1, P4, P7 positions and analysis events.

    Signals:
        frame_selected(int): Emitted when user selects a frame
    """

    frame_selected = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize timeline widget."""
        super().__init__(parent)

        self.total_frames = 0
        self.current_frame = 0
        self.key_positions = {}  # {name: (frame, color)}

        self._setup_ui()

        logger.debug("Initialized TimelineWidget")

    def _setup_ui(self):
        """Set up timeline UI."""
        layout = QHBoxLayout()
        layout.setSpacing(F1Theme.PADDING_MEDIUM)
        layout.setContentsMargins(
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_SMALL,
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_SMALL
        )

        # Current frame label
        self.frame_label = QLabel("0 / 0")
        self.frame_label.setStyleSheet(f"color: {F1Theme.WHITE_TEXT};")
        self.frame_label.setMinimumWidth(100)
        font = QFont(F1Theme.FONT_FAMILY)
        font.setPixelSize(F1Theme.FONT_SIZE_NORMAL)
        self.frame_label.setFont(font)

        # Timeline scrubber
        self.scrubber = QSlider(Qt.Horizontal)
        self.scrubber.setMinimum(0)
        self.scrubber.setMaximum(0)
        self.scrubber.setValue(0)
        self.scrubber.setTickPosition(QSlider.NoTicks)
        self.scrubber.valueChanged.connect(self._on_scrubber_changed)

        # Time/duration label
        self.time_label = QLabel("00:00.0 / 00:00.0")
        self.time_label.setStyleSheet(f"color: {F1Theme.WHITE_MUTED};")
        self.time_label.setMinimumWidth(140)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font = QFont(F1Theme.FONT_FAMILY)
        font.setPixelSize(F1Theme.FONT_SIZE_SMALL)
        self.time_label.setFont(font)

        # Add to layout
        layout.addWidget(self.frame_label)
        layout.addWidget(self.scrubber, stretch=1)
        layout.addWidget(self.time_label)

        self.setLayout(layout)

        # Set background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {F1Theme.BLACK_SECONDARY};
                border-top: 1px solid {F1Theme.BLACK_ELEVATED};
            }}
        """)

    def set_total_frames(self, total: int, fps: float = 30.0):
        """Set total number of frames.

        Args:
            total: Total frame count
            fps: Frames per second for time calculation
        """
        self.total_frames = total
        self.fps = fps
        self.scrubber.setMaximum(max(0, total - 1))
        self._update_labels()

        logger.debug(f"Timeline set to {total} frames @ {fps} fps")

    def set_current_frame(self, frame: int):
        """Set current frame position.

        Args:
            frame: Frame number
        """
        if 0 <= frame < self.total_frames:
            self.current_frame = frame
            # Block signals to prevent recursion
            self.scrubber.blockSignals(True)
            self.scrubber.setValue(frame)
            self.scrubber.blockSignals(False)
            self._update_labels()

    def add_key_position(self, name: str, frame: int, color: str = None):
        """Add key position marker.

        Args:
            name: Position name (e.g., "P1", "P4", "P7", "Impact")
            frame: Frame number
            color: Marker color (hex or name), defaults to cyan
        """
        if color is None:
            color = F1Theme.ACCENT_CYAN

        self.key_positions[name] = (frame, color)
        self.update()  # Trigger repaint

        logger.debug(f"Added key position: {name} at frame {frame}")

    def clear_key_positions(self):
        """Clear all key position markers."""
        self.key_positions.clear()
        self.update()

    def _on_scrubber_changed(self, value: int):
        """Handle scrubber value change.

        Args:
            value: New frame number
        """
        self.current_frame = value
        self._update_labels()
        self.frame_selected.emit(value)

    def _update_labels(self):
        """Update frame and time labels."""
        # Frame counter
        self.frame_label.setText(f"{self.current_frame} / {self.total_frames}")

        # Time display
        if hasattr(self, 'fps') and self.fps > 0:
            current_time = self.current_frame / self.fps
            total_time = self.total_frames / self.fps

            current_str = self._format_time(current_time)
            total_str = self._format_time(total_time)

            self.time_label.setText(f"{current_str} / {total_str}")

    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS.F.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:04.1f}"

    def paintEvent(self, event):
        """Custom paint for timeline with key position markers.

        Args:
            event: Paint event
        """
        super().paintEvent(event)

        if not self.key_positions or self.total_frames == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get scrubber geometry
        scrubber_rect = self.scrubber.geometry()

        # Calculate marker positions
        for name, (frame, color) in self.key_positions.items():
            # Calculate x position
            if self.total_frames > 1:
                position = frame / (self.total_frames - 1)
            else:
                position = 0

            x = scrubber_rect.left() + int(position * scrubber_rect.width())
            y_top = scrubber_rect.top()
            y_bottom = scrubber_rect.bottom()

            # Draw marker line
            pen = QPen(QColor(color))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(x, y_top, x, y_bottom)

            # Draw marker label
            painter.setFont(QFont(F1Theme.FONT_FAMILY, 8))
            painter.drawText(x - 10, y_top - 5, name)
