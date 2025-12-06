"""Drawing toolbar widget with tool selection and settings."""

import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QToolButton, QPushButton,
    QSlider, QLabel, QColorDialog, QButtonGroup, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QIcon

logger = logging.getLogger(__name__)


class DrawingToolbar(QWidget):
    """Toolbar for selecting drawing tools and settings.

    Provides tool buttons, color picker, thickness slider,
    and undo/redo/clear actions.

    Signals:
        tool_selected(str): Emitted when tool is selected
        color_changed(tuple): Emitted when color changes
        thickness_changed(int): Emitted when thickness changes
        undo_requested(): Emitted when undo is clicked
        redo_requested(): Emitted when redo is clicked
        clear_requested(): Emitted when clear is clicked
    """

    tool_selected = pyqtSignal(str)
    color_changed = pyqtSignal(tuple)
    thickness_changed = pyqtSignal(int)
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize drawing toolbar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.current_tool = None
        self.current_color = (255, 255, 0)  # Yellow
        self.current_thickness = 2

        self._setup_ui()

        logger.debug("Initialized DrawingToolbar")

    def _setup_ui(self):
        """Set up toolbar UI."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 5, 10, 5)

        # === TOOL SELECTION ===
        tool_group = QButtonGroup(self)
        tool_group.setExclusive(True)

        # Selection tool
        self.select_btn = QToolButton()
        self.select_btn.setText("Select")
        self.select_btn.setToolTip("Selection tool (Esc)")
        self.select_btn.setCheckable(True)
        self.select_btn.setChecked(True)
        self.select_btn.clicked.connect(lambda: self.tool_selected.emit("select"))
        tool_group.addButton(self.select_btn)
        layout.addWidget(self.select_btn)

        # Line tool
        self.line_btn = QToolButton()
        self.line_btn.setText("Line")
        self.line_btn.setToolTip("Draw line (L)")
        self.line_btn.setCheckable(True)
        self.line_btn.clicked.connect(lambda: self.tool_selected.emit("line"))
        tool_group.addButton(self.line_btn)
        layout.addWidget(self.line_btn)

        # Angle tool
        self.angle_btn = QToolButton()
        self.angle_btn.setText("Angle")
        self.angle_btn.setToolTip("Measure angle (A)")
        self.angle_btn.setCheckable(True)
        self.angle_btn.clicked.connect(lambda: self.tool_selected.emit("angle"))
        tool_group.addButton(self.angle_btn)
        layout.addWidget(self.angle_btn)

        # Circle tool
        self.circle_btn = QToolButton()
        self.circle_btn.setText("Circle")
        self.circle_btn.setToolTip("Draw circle (C)")
        self.circle_btn.setCheckable(True)
        self.circle_btn.clicked.connect(lambda: self.tool_selected.emit("circle"))
        tool_group.addButton(self.circle_btn)
        layout.addWidget(self.circle_btn)

        # Text tool
        self.text_btn = QToolButton()
        self.text_btn.setText("Text")
        self.text_btn.setToolTip("Add text (T)")
        self.text_btn.setCheckable(True)
        self.text_btn.clicked.connect(lambda: self.tool_selected.emit("text"))
        tool_group.addButton(self.text_btn)
        layout.addWidget(self.text_btn)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)

        # === COLOR PICKER ===
        color_layout = QVBoxLayout()
        color_layout.setSpacing(2)

        color_label = QLabel("Color:")
        color_label.setStyleSheet("font-size: 10px;")
        color_layout.addWidget(color_label)

        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(40, 20)
        self.color_btn.setStyleSheet(self._get_color_button_style())
        self.color_btn.clicked.connect(self._on_color_clicked)
        self.color_btn.setToolTip("Click to choose color")
        color_layout.addWidget(self.color_btn)

        layout.addLayout(color_layout)

        # === THICKNESS SLIDER ===
        thickness_layout = QVBoxLayout()
        thickness_layout.setSpacing(2)

        thickness_label = QLabel("Thickness:")
        thickness_label.setStyleSheet("font-size: 10px;")
        thickness_layout.addWidget(thickness_label)

        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setMinimum(1)
        self.thickness_slider.setMaximum(10)
        self.thickness_slider.setValue(2)
        self.thickness_slider.setFixedWidth(100)
        self.thickness_slider.valueChanged.connect(self._on_thickness_changed)
        self.thickness_slider.setToolTip("Line thickness")
        thickness_layout.addWidget(self.thickness_slider)

        layout.addLayout(thickness_layout)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)

        # === UNDO/REDO/CLEAR ===
        self.undo_btn = QPushButton("↶ Undo")
        self.undo_btn.setToolTip("Undo last drawing (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("↷ Redo")
        self.redo_btn.setToolTip("Redo (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        layout.addWidget(self.redo_btn)

        self.clear_btn = QPushButton("Clear Frame")
        self.clear_btn.setToolTip("Clear all drawings on current frame")
        self.clear_btn.clicked.connect(self.clear_requested.emit)
        layout.addWidget(self.clear_btn)

        # Stretch to push buttons to the left
        layout.addStretch()

        self.setLayout(layout)

        # Apply styling
        self._apply_styling()

    def _apply_styling(self):
        """Apply F1-inspired styling to toolbar."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #E8E8E8;
            }
            QToolButton {
                background-color: #2A2A2A;
                color: #E8E8E8;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 11px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #3A3A3A;
                border: 1px solid #C0C0C0;
            }
            QToolButton:checked {
                background-color: #C0C0C0;
                color: #0A0A0A;
                border: 1px solid #E8E8E8;
            }
            QPushButton {
                background-color: #2A2A2A;
                color: #E8E8E8;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
                border: 1px solid #C0C0C0;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3A3A3A;
                height: 4px;
                background: #2A2A2A;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #C0C0C0;
                border: 1px solid #E8E8E8;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #E8E8E8;
            }
            QLabel {
                color: #C0C0C0;
                font-size: 10px;
            }
        """)

    def _get_color_button_style(self) -> str:
        """Get stylesheet for color button.

        Returns:
            CSS stylesheet string
        """
        r, g, b = self.current_color
        return f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid #E8E8E8;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid white;
            }}
        """

    def _on_color_clicked(self):
        """Handle color button click."""
        # Open color dialog
        initial_color = QColor(*self.current_color)
        color = QColorDialog.getColor(
            initial_color,
            self,
            "Choose Drawing Color"
        )

        if color.isValid():
            self.current_color = (color.red(), color.green(), color.blue())
            self.color_btn.setStyleSheet(self._get_color_button_style())
            self.color_changed.emit(self.current_color)

            logger.debug(f"Color changed to {self.current_color}")

    def _on_thickness_changed(self, value: int):
        """Handle thickness slider change.

        Args:
            value: New thickness value
        """
        self.current_thickness = value
        self.thickness_changed.emit(value)

    def set_active_tool(self, tool_name: str):
        """Set the active tool (updates button states).

        Args:
            tool_name: Tool name ("select", "line", "angle", "circle", "text")
        """
        self.current_tool = tool_name

        # Update button checked states
        if tool_name == "select":
            self.select_btn.setChecked(True)
        elif tool_name == "line":
            self.line_btn.setChecked(True)
        elif tool_name == "angle":
            self.angle_btn.setChecked(True)
        elif tool_name == "circle":
            self.circle_btn.setChecked(True)
        elif tool_name == "text":
            self.text_btn.setChecked(True)

    def set_undo_enabled(self, enabled: bool):
        """Enable/disable undo button.

        Args:
            enabled: Whether to enable
        """
        self.undo_btn.setEnabled(enabled)

    def set_redo_enabled(self, enabled: bool):
        """Enable/disable redo button.

        Args:
            enabled: Whether to enable
        """
        self.redo_btn.setEnabled(enabled)

    def get_current_color(self) -> tuple:
        """Get current color.

        Returns:
            RGB color tuple
        """
        return self.current_color

    def get_current_thickness(self) -> int:
        """Get current thickness.

        Returns:
            Thickness in pixels
        """
        return self.current_thickness
