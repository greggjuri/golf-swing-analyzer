"""Analysis control panel with metrics and overlay toggles."""

import logging
from typing import Optional, Dict

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from .theme import F1Theme
from .widgets import GlassPanel, MetricDisplay, ToggleButton

logger = logging.getLogger(__name__)


class AnalysisPanelWidget(QWidget):
    """Analysis control panel with metrics and overlay toggles.

    Displays real-time swing metrics and allows toggling
    analysis overlays.

    Signals:
        overlay_toggled(str, bool): Emitted when overlay toggled (name, enabled)
    """

    overlay_toggled = pyqtSignal(str, bool)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize analysis panel."""
        super().__init__(parent)

        # Metric displays
        self.metrics = {}

        # Overlay toggles
        self.toggles = {}

        self._setup_ui()

        logger.debug("Initialized AnalysisPanelWidget")

    def _setup_ui(self):
        """Set up analysis panel UI."""
        # Main layout with scroll area for many metrics
        main_layout = QVBoxLayout()
        main_layout.setSpacing(F1Theme.PADDING_MEDIUM)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        # Content widget
        content = QWidget()
        content.setStyleSheet(f"QWidget {{ background-color: {F1Theme.BLACK_PANEL}; }}")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(F1Theme.PADDING_LARGE)
        content_layout.setContentsMargins(
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_MEDIUM,
            F1Theme.PADDING_MEDIUM
        )

        # === METRICS SECTION ===
        metrics_group = self._create_metrics_section()
        content_layout.addWidget(metrics_group)

        # === OVERLAYS SECTION ===
        overlays_group = self._create_overlays_section()
        content_layout.addWidget(overlays_group)

        # === SETTINGS SECTION ===
        settings_group = self._create_settings_section()
        content_layout.addWidget(settings_group)

        content_layout.addStretch()

        content.setLayout(content_layout)
        scroll.setWidget(content)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        # Set fixed width for panel
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        # Apply F1 styling with dark background
        self.setStyleSheet(f"""
            AnalysisPanelWidget {{
                background-color: {F1Theme.BLACK_PANEL};
            }}
        """)

    def _create_metrics_section(self) -> QWidget:
        """Create metrics display section.

        Returns:
            Metrics section widget
        """
        group = QGroupBox("METRICS")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {F1Theme.FONT_SIZE_SMALL}px;
                font-weight: 600;
                color: {F1Theme.SILVER_LIGHT};
                letter-spacing: 1px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(F1Theme.PADDING_MEDIUM)

        # Create metric displays
        self.metrics['attack_angle'] = MetricDisplay("Attack Angle", "°")
        self.metrics['swing_path'] = MetricDisplay("Swing Path", "°")
        self.metrics['plane_angle'] = MetricDisplay("Plane Angle", "°")
        self.metrics['club_speed'] = MetricDisplay("Club Speed", "mph")

        for metric in self.metrics.values():
            layout.addWidget(metric)

        group.setLayout(layout)
        return group

    def _create_overlays_section(self) -> QWidget:
        """Create overlay toggles section.

        Returns:
            Overlays section widget
        """
        group = QGroupBox("OVERLAYS")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {F1Theme.FONT_SIZE_SMALL}px;
                font-weight: 600;
                color: {F1Theme.SILVER_LIGHT};
                letter-spacing: 1px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(F1Theme.PADDING_SMALL)

        # Create overlay toggles
        overlays = [
            ('club_track', 'Club Track', True),
            ('swing_plane', 'Swing Plane', True),
            ('skeleton', 'Skeleton', False),
            ('angles', 'Joint Angles', False),
            ('key_positions', 'Key Positions', True),
        ]

        for key, label, default in overlays:
            toggle = ToggleButton(label)
            toggle.setChecked(default)
            toggle.toggled.connect(
                lambda checked, k=key: self.overlay_toggled.emit(k, checked)
            )
            self.toggles[key] = toggle
            layout.addWidget(toggle)

        group.setLayout(layout)
        return group

    def _create_settings_section(self) -> QWidget:
        """Create settings section.

        Returns:
            Settings section widget
        """
        group = QGroupBox("SETTINGS")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {F1Theme.FONT_SIZE_SMALL}px;
                font-weight: 600;
                color: {F1Theme.SILVER_LIGHT};
                letter-spacing: 1px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(F1Theme.PADDING_SMALL)

        # Detection confidence threshold
        conf_label = QLabel("Detection Confidence:")
        conf_label.setStyleSheet(f"color: {F1Theme.WHITE_MUTED};")
        layout.addWidget(conf_label)

        # Add more settings as needed
        info_label = QLabel("More settings coming soon...")
        info_label.setStyleSheet(f"color: {F1Theme.WHITE_MUTED}; font-style: italic;")
        layout.addWidget(info_label)

        group.setLayout(layout)
        return group

    def update_metrics(self, metrics: Dict[str, float]):
        """Update displayed metrics.

        Args:
            metrics: Dictionary of metric name -> value
        """
        for key, value in metrics.items():
            if key in self.metrics:
                self.metrics[key].set_value(value)

    def get_enabled_overlays(self) -> Dict[str, bool]:
        """Get which overlays are enabled.

        Returns:
            Dictionary of overlay name -> enabled state
        """
        return {
            key: toggle.isChecked()
            for key, toggle in self.toggles.items()
        }

    def set_overlay_enabled(self, overlay: str, enabled: bool):
        """Enable or disable an overlay.

        Args:
            overlay: Overlay name
            enabled: Whether to enable
        """
        if overlay in self.toggles:
            self.toggles[overlay].setChecked(enabled)
