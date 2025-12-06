"""Toggle button widget with F1 styling."""

import logging
from typing import Optional

from PyQt5.QtWidgets import QCheckBox, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..theme import F1Theme

logger = logging.getLogger(__name__)


class ToggleButton(QCheckBox):
    """Styled toggle button for overlay controls.

    Custom checkbox styled as a modern toggle with F1 aesthetic.

    Signals:
        toggled(bool): Emitted when toggle state changes

    Example:
        club_toggle = ToggleButton("Club Track")
        club_toggle.toggled.connect(on_club_toggled)
        club_toggle.setChecked(True)
    """

    def __init__(
        self,
        text: str = "",
        parent: Optional[QWidget] = None
    ):
        """Initialize toggle button.

        Args:
            text: Button label text
            parent: Parent widget
        """
        super().__init__(text, parent)

        self._setup_style()

        logger.debug(f"Initialized ToggleButton: {text}")

    def _setup_style(self):
        """Apply F1 toggle button styling."""
        # Set font
        font = QFont(F1Theme.FONT_FAMILY)
        font.setPixelSize(F1Theme.FONT_SIZE_NORMAL)
        self.setFont(font)

        # Apply custom stylesheet for modern toggle appearance
        self.setStyleSheet(f"""
            QCheckBox {{
                spacing: {F1Theme.PADDING_SMALL}px;
                color: {F1Theme.WHITE_TEXT};
                padding: {F1Theme.PADDING_SMALL}px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: 3px;
                background-color: {F1Theme.BLACK_PANEL};
            }}

            QCheckBox::indicator:hover {{
                border: 1px solid {F1Theme.SILVER_DARK};
                background-color: {F1Theme.BLACK_ELEVATED};
            }}

            QCheckBox::indicator:checked {{
                background-color: {F1Theme.SILVER_MID};
                border: 1px solid {F1Theme.SILVER_LIGHT};
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {F1Theme.SILVER_LIGHT};
            }}

            QCheckBox:disabled {{
                color: #555555;
            }}

            QCheckBox::indicator:disabled {{
                border: 1px solid #2A2A2A;
                background-color: {F1Theme.BLACK_PANEL};
            }}
        """)
