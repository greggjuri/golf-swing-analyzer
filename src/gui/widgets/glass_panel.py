"""Glass morphism panel widget with F1 styling."""

import logging
from typing import Optional

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

from ..theme import F1Theme

logger = logging.getLogger(__name__)


class GlassPanel(QWidget):
    """Frosted glass panel with blur effect and F1 styling.

    Container widget with glass morphism aesthetic - semi-transparent
    background with border and subtle highlight for premium feel.

    Example:
        panel = GlassPanel()
        layout = QVBoxLayout()
        layout.addWidget(some_widget)
        panel.setLayout(layout)
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        padding: int = F1Theme.PADDING_MEDIUM
    ):
        """Initialize glass panel.

        Args:
            parent: Parent widget
            padding: Internal padding in pixels
        """
        super().__init__(parent)

        self.padding = padding

        # Apply glass styling
        self.setStyleSheet(F1Theme.get_glass_panel_stylesheet())

        # Set default layout with padding
        layout = QVBoxLayout()
        layout.setContentsMargins(padding, padding, padding, padding)
        self.setLayout(layout)

        logger.debug(f"Initialized GlassPanel with padding={padding}")

    def paintEvent(self, event):
        """Paint glass effect with subtle highlight.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget rect
        rect = self.rect()

        # Create rounded rect path
        path = QPainterPath()
        path.addRoundedRect(
            rect.x(), rect.y(),
            rect.width(), rect.height(),
            F1Theme.RADIUS_MEDIUM, F1Theme.RADIUS_MEDIUM
        )

        # Fill semi-transparent background
        bg_color = QColor(F1Theme.BLACK_PANEL)
        bg_color.setAlpha(int(0.7 * 255))
        painter.fillPath(path, QBrush(bg_color))

        # Draw border
        border_color = QColor(255, 255, 255, int(0.1 * 255))
        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

        # Draw subtle top highlight for depth
        highlight_color = QColor(255, 255, 255, int(0.05 * 255))
        highlight_rect = rect.adjusted(1, 1, -1, -rect.height() // 2)
        highlight_path = QPainterPath()
        highlight_path.addRoundedRect(
            highlight_rect.x(), highlight_rect.y(),
            highlight_rect.width(), highlight_rect.height() // 2,
            F1Theme.RADIUS_MEDIUM, F1Theme.RADIUS_MEDIUM
        )
        painter.fillPath(highlight_path, QBrush(highlight_color))
