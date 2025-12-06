"""Metric display widget with large F1-style numeric values."""

import logging
from typing import Optional

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtGui import QFont

from ..theme import F1Theme

logger = logging.getLogger(__name__)


class MetricDisplay(QWidget):
    """Large numeric display for a single metric with F1 styling.

    Displays metric name, value, and unit in a premium glass panel
    with large, easy-to-read numbers.

    Example:
        attack_display = MetricDisplay("Attack Angle", "°")
        attack_display.set_value(-5.2)
    """

    def __init__(
        self,
        label: str,
        unit: str = "",
        parent: Optional[QWidget] = None
    ):
        """Initialize metric display.

        Args:
            label: Metric name (e.g., "Attack Angle")
            unit: Unit symbol (e.g., "°", "mph", "m/s")
            parent: Parent widget
        """
        super().__init__(parent)

        self.label_text = label
        self.unit_text = unit
        self._value = 0.0

        self._setup_ui()

        logger.debug(f"Initialized MetricDisplay: {label} ({unit})")

    def _setup_ui(self):
        """Set up metric display UI."""
        # Apply glass panel styling
        self.setStyleSheet(F1Theme.get_metric_display_stylesheet())

        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_MEDIUM
        )

        # Label (metric name)
        self.label_widget = QLabel(self.label_text.upper())
        self.label_widget.setObjectName("metric-label")
        label_font = QFont(F1Theme.FONT_FAMILY)
        label_font.setPixelSize(F1Theme.FONT_SIZE_SMALL)
        label_font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        self.label_widget.setFont(label_font)
        self.label_widget.setStyleSheet(f"color: {F1Theme.WHITE_MUTED};")

        # Value display
        value_layout = QVBoxLayout()
        value_layout.setSpacing(0)

        self.value_widget = QLabel("0.0")
        self.value_widget.setObjectName("metric-value")
        value_font = QFont(F1Theme.FONT_FAMILY)
        value_font.setPixelSize(F1Theme.FONT_SIZE_METRIC)
        value_font.setWeight(QFont.DemiBold)
        self.value_widget.setFont(value_font)
        self.value_widget.setStyleSheet(f"color: {F1Theme.WHITE_PRIMARY};")
        self.value_widget.setAlignment(Qt.AlignCenter)

        # Unit label
        if self.unit_text:
            self.unit_widget = QLabel(self.unit_text)
            self.unit_widget.setObjectName("metric-unit")
            unit_font = QFont(F1Theme.FONT_FAMILY)
            unit_font.setPixelSize(F1Theme.FONT_SIZE_LARGE)
            self.unit_widget.setFont(unit_font)
            self.unit_widget.setStyleSheet(f"color: {F1Theme.SILVER_MID};")
            self.unit_widget.setAlignment(Qt.AlignCenter)
        else:
            self.unit_widget = None

        # Assemble layout
        layout.addWidget(self.label_widget)
        layout.addStretch()
        layout.addWidget(self.value_widget)
        if self.unit_widget:
            layout.addWidget(self.unit_widget)
        layout.addStretch()

        self.setLayout(layout)

        # Set minimum size for proper display
        self.setMinimumSize(140, 100)

    def set_value(self, value: float):
        """Update displayed value.

        Args:
            value: New metric value
        """
        self._value = value
        self.value_widget.setText(f"{value:.1f}")

    @pyqtProperty(float)
    def value(self) -> float:
        """Get current value.

        Returns:
            Current metric value
        """
        return self._value

    def set_label(self, label: str):
        """Update metric label.

        Args:
            label: New label text
        """
        self.label_text = label
        self.label_widget.setText(label.upper())

    def set_unit(self, unit: str):
        """Update unit display.

        Args:
            unit: New unit symbol
        """
        self.unit_text = unit
        if self.unit_widget:
            self.unit_widget.setText(unit)
