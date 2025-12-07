"""Comparison toolbar with controls for side-by-side view."""

import logging

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QCheckBox, QLabel, QFrame
)
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger(__name__)


class ComparisonToolbar(QWidget):
    """Toolbar for comparison view controls.

    Provides buttons for loading videos, swapping sides,
    toggling sync, and taking comparison screenshots.

    Signals:
        load_left_requested(): Load video on left side
        load_right_requested(): Load video on right side
        swap_requested(): Swap left and right videos
        sync_toggled(bool): Sync enabled/disabled
        screenshot_requested(): Take comparison screenshot
        calibrate_requested(): Calibrate sync points
    """

    load_left_requested = pyqtSignal()
    load_right_requested = pyqtSignal()
    swap_requested = pyqtSignal()
    sync_toggled = pyqtSignal(bool)
    screenshot_requested = pyqtSignal()
    calibrate_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize comparison toolbar."""
        super().__init__(parent)

        self._setup_ui()

        logger.debug("Initialized ComparisonToolbar")

    def _setup_ui(self):
        """Set up toolbar UI."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 5, 10, 5)

        # Load buttons
        self.load_left_btn = QPushButton("Load Left Video")
        self.load_left_btn.setToolTip("Load video on left side (Ctrl+L)")
        self.load_left_btn.clicked.connect(self.load_left_requested.emit)
        layout.addWidget(self.load_left_btn)

        self.load_right_btn = QPushButton("Load Right Video")
        self.load_right_btn.setToolTip("Load video on right side (Ctrl+R)")
        self.load_right_btn.clicked.connect(self.load_right_requested.emit)
        layout.addWidget(self.load_right_btn)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)

        # Swap button
        self.swap_btn = QPushButton("⇄ Swap")
        self.swap_btn.setToolTip("Swap left and right videos (Ctrl+W)")
        self.swap_btn.clicked.connect(self.swap_requested.emit)
        self.swap_btn.setEnabled(False)  # Disabled until both videos loaded
        layout.addWidget(self.swap_btn)

        # Sync toggle
        self.sync_toggle = QCheckBox("Link Playback 🔗")
        self.sync_toggle.setToolTip("Synchronize playback (Ctrl+K)")
        self.sync_toggle.setChecked(True)
        self.sync_toggle.toggled.connect(self._on_sync_toggled)
        layout.addWidget(self.sync_toggle)

        # Offset display
        self.offset_label = QLabel("Aligned")
        self.offset_label.setStyleSheet("color: #C0C0C0; font-size: 11px;")
        layout.addWidget(self.offset_label)

        # Calibrate button
        self.calibrate_btn = QPushButton("⚙ Calibrate Sync")
        self.calibrate_btn.setToolTip("Calibrate sync from current positions")
        self.calibrate_btn.clicked.connect(self.calibrate_requested.emit)
        self.calibrate_btn.setEnabled(False)  # Disabled until both videos loaded
        layout.addWidget(self.calibrate_btn)

        # Stretch to push screenshot to right
        layout.addStretch()

        # Screenshot button
        self.screenshot_btn = QPushButton("📷 Screenshot")
        self.screenshot_btn.setToolTip("Take comparison screenshot")
        self.screenshot_btn.clicked.connect(self.screenshot_requested.emit)
        self.screenshot_btn.setEnabled(False)  # Disabled until videos loaded
        layout.addWidget(self.screenshot_btn)

        self.setLayout(layout)

        # Apply F1 styling
        self._apply_styling()

    def _apply_styling(self):
        """Apply F1-inspired styling to toolbar."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #E8E8E8;
            }
            QPushButton {
                background-color: #2A2A2A;
                color: #E8E8E8;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px 15px;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
                border: 1px solid #C0C0C0;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
            QPushButton:disabled {
                background-color: #1A1A1A;
                color: #555555;
                border: 1px solid #2A2A2A;
            }
            QCheckBox {
                color: #E8E8E8;
                spacing: 5px;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                background-color: #2A2A2A;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #C0C0C0;
            }
            QCheckBox::indicator:checked {
                background-color: #C0C0C0;
                border: 1px solid #E8E8E8;
            }
        """)

    def _on_sync_toggled(self, checked: bool):
        """Handle sync toggle.

        Args:
            checked: Whether sync is enabled
        """
        self.sync_toggled.emit(checked)

        # Update visual indicator
        if checked:
            self.sync_toggle.setText("Link Playback 🔗")
            self.sync_toggle.setStyleSheet("color: #00FF00;")  # Green when linked
        else:
            self.sync_toggle.setText("Link Playback ⛓️‍💥")
            self.sync_toggle.setStyleSheet("color: #888888;")  # Grey when unlinked

    def set_videos_loaded(self, left_loaded: bool, right_loaded: bool):
        """Update button states based on loaded videos.

        Args:
            left_loaded: Whether left video is loaded
            right_loaded: Whether right video is loaded
        """
        both_loaded = left_loaded and right_loaded
        any_loaded = left_loaded or right_loaded

        self.swap_btn.setEnabled(both_loaded)
        self.calibrate_btn.setEnabled(both_loaded)
        self.screenshot_btn.setEnabled(any_loaded)

    def set_sync_offset_display(self, offset_text: str):
        """Update offset display label.

        Args:
            offset_text: Text to display (e.g., "Right +5 frames")
        """
        self.offset_label.setText(offset_text)

    def get_sync_enabled(self) -> bool:
        """Get current sync state.

        Returns:
            True if sync is enabled
        """
        return self.sync_toggle.isChecked()

    def set_sync_enabled(self, enabled: bool):
        """Set sync state.

        Args:
            enabled: Whether to enable sync
        """
        self.sync_toggle.setChecked(enabled)
