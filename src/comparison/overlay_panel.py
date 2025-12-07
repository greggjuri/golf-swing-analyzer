"""Control panel for overlay mode settings."""

import logging

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QComboBox, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)


class OverlayPanel(QWidget):
    """Control panel for overlay mode configuration.

    Provides controls for transparency, blend mode, and color tinting
    when overlaying two videos.

    Signals:
        alpha_changed(float): Transparency changed (0.0 to 1.0)
        blend_mode_changed(str): Blend mode changed
        left_tint_toggled(bool): Left video tint enabled/disabled
        right_tint_toggled(bool): Right video tint enabled/disabled
    """

    alpha_changed = pyqtSignal(float)
    blend_mode_changed = pyqtSignal(str)
    left_tint_toggled = pyqtSignal(bool)
    right_tint_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialize overlay control panel."""
        super().__init__(parent)

        self._setup_ui()
        self._connect_signals()

        logger.debug("Initialized OverlayPanel")

    def _setup_ui(self):
        """Set up overlay panel UI."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # === TITLE ===
        title = QLabel("OVERLAY CONTROLS")
        title.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #E8E8E8;
            letter-spacing: 1px;
            padding: 5px;
        """)
        layout.addWidget(title)

        # === TRANSPARENCY SLIDER ===
        transparency_group = QGroupBox("Transparency")
        transparency_layout = QVBoxLayout()

        # Slider (0-100)
        slider_layout = QHBoxLayout()

        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(100)
        self.alpha_slider.setValue(50)  # Default 50%
        self.alpha_slider.setTickPosition(QSlider.TicksBelow)
        self.alpha_slider.setTickInterval(10)

        self.alpha_label = QLabel("50%")
        self.alpha_label.setMinimumWidth(40)
        self.alpha_label.setStyleSheet("font-weight: 600;")

        slider_layout.addWidget(self.alpha_slider)
        slider_layout.addWidget(self.alpha_label)

        # Labels
        labels_layout = QHBoxLayout()
        left_label = QLabel("Left Video")
        left_label.setStyleSheet("font-size: 10px; color: #C0C0C0;")
        right_label = QLabel("Right Video")
        right_label.setStyleSheet("font-size: 10px; color: #C0C0C0;")
        right_label.setAlignment(Qt.AlignRight)

        labels_layout.addWidget(left_label)
        labels_layout.addStretch()
        labels_layout.addWidget(right_label)

        transparency_layout.addLayout(slider_layout)
        transparency_layout.addLayout(labels_layout)
        transparency_group.setLayout(transparency_layout)
        layout.addWidget(transparency_group)

        # === BLEND MODE ===
        blend_group = QGroupBox("Blend Mode")
        blend_layout = QVBoxLayout()

        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems([
            "Normal",
            "Difference",
            "Multiply",
            "Screen"
        ])
        self.blend_mode_combo.setCurrentText("Normal")

        blend_layout.addWidget(self.blend_mode_combo)
        blend_group.setLayout(blend_layout)
        layout.addWidget(blend_group)

        # === COLOR TINTS ===
        tint_group = QGroupBox("Color Tints")
        tint_layout = QVBoxLayout()

        self.left_tint_checkbox = QCheckBox("Tint Left Video (Red)")
        self.left_tint_checkbox.setChecked(False)

        self.right_tint_checkbox = QCheckBox("Tint Right Video (Green)")
        self.right_tint_checkbox.setChecked(False)

        tint_layout.addWidget(self.left_tint_checkbox)
        tint_layout.addWidget(self.right_tint_checkbox)
        tint_group.setLayout(tint_layout)
        layout.addWidget(tint_group)

        # === INFO TEXT ===
        info_label = QLabel(
            "💡 Tip: Use color tints to distinguish overlaid videos. "
            "Difference mode highlights changes."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            font-size: 10px;
            color: #A0A0A0;
            padding: 10px;
            background-color: #1A1A1A;
            border-radius: 3px;
        """)
        layout.addWidget(info_label)

        # Stretch to push everything to top
        layout.addStretch()

        self.setLayout(layout)

        # Apply F1 styling
        self._apply_styling()

    def _apply_styling(self):
        """Apply F1-inspired styling to panel."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #E8E8E8;
            }
            QGroupBox {
                font-size: 11px;
                font-weight: 600;
                border: 1px solid #3A3A3A;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #C0C0C0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3A3A3A;
                height: 8px;
                background: #2A2A2A;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #C0C0C0;
                border: 1px solid #E8E8E8;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #E8E8E8;
            }
            QComboBox {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox:hover {
                border: 1px solid #C0C0C0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #C0C0C0;
                margin-right: 5px;
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

    def _connect_signals(self):
        """Connect widget signals to slots."""
        self.alpha_slider.valueChanged.connect(self._on_alpha_changed)
        self.blend_mode_combo.currentTextChanged.connect(self._on_blend_mode_changed)
        self.left_tint_checkbox.toggled.connect(self.left_tint_toggled.emit)
        self.right_tint_checkbox.toggled.connect(self.right_tint_toggled.emit)

    def _on_alpha_changed(self, value: int):
        """Handle alpha slider change.

        Args:
            value: Slider value (0-100)
        """
        # Update label
        self.alpha_label.setText(f"{value}%")

        # Emit signal with normalized value (0.0-1.0)
        alpha = value / 100.0
        self.alpha_changed.emit(alpha)

    def _on_blend_mode_changed(self, mode_text: str):
        """Handle blend mode change.

        Args:
            mode_text: Display text (e.g., "Normal", "Difference")
        """
        # Convert display text to internal mode name
        mode_map = {
            "Normal": "normal",
            "Difference": "difference",
            "Multiply": "multiply",
            "Screen": "screen"
        }

        mode = mode_map.get(mode_text, "normal")
        self.blend_mode_changed.emit(mode)

    def get_alpha(self) -> float:
        """Get current transparency value.

        Returns:
            Alpha value (0.0 to 1.0)
        """
        return self.alpha_slider.value() / 100.0

    def set_alpha(self, alpha: float):
        """Set transparency value.

        Args:
            alpha: Alpha value (0.0 to 1.0)
        """
        value = int(alpha * 100)
        self.alpha_slider.setValue(value)

    def get_blend_mode(self) -> str:
        """Get current blend mode.

        Returns:
            Blend mode name ('normal', 'difference', 'multiply', 'screen')
        """
        mode_text = self.blend_mode_combo.currentText()
        mode_map = {
            "Normal": "normal",
            "Difference": "difference",
            "Multiply": "multiply",
            "Screen": "screen"
        }
        return mode_map.get(mode_text, "normal")

    def is_left_tint_enabled(self) -> bool:
        """Check if left video tint is enabled.

        Returns:
            True if tint is enabled
        """
        return self.left_tint_checkbox.isChecked()

    def is_right_tint_enabled(self) -> bool:
        """Check if right video tint is enabled.

        Returns:
            True if tint is enabled
        """
        return self.right_tint_checkbox.isChecked()
