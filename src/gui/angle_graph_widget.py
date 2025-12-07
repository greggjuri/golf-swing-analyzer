"""Interactive angle graph widget using matplotlib."""

import logging
from typing import Optional, Dict, Tuple, List
import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QLabel, QCheckBox
)
from PyQt5.QtCore import pyqtSignal

# Matplotlib imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class AngleGraphWidget(QWidget):
    """Interactive graph for displaying angle data over time.

    Features matplotlib plotting with F1 styling, interactive
    frame selection, key position markers, and export capabilities.

    Signals:
        frame_clicked(int): User clicked on graph at frame number
        angle_selected(str): User selected different angle from dropdown
    """

    frame_clicked = pyqtSignal(int)
    angle_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize angle graph widget."""
        super().__init__(parent)

        # Graph data
        self.current_angle_name = None
        self.current_frame_marker = None

        # Key position markers
        self.key_positions = {}  # position_name -> frame_num

        # Comparison data (for dual plots)
        self.comparison_mode = False

        # Create matplotlib figure with F1 styling
        self.figure = Figure(figsize=(10, 4), facecolor='#1A1A1A')
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Create axes
        self.axes = self.figure.add_subplot(111)
        self._style_axes()

        # Connect click events
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)

        # UI components
        self.angle_selector = None
        self.export_btn = None
        self.show_markers_checkbox = None
        self.frame_info_label = None

        self._setup_ui()

        logger.debug("Initialized AngleGraphWidget")

    def _style_axes(self):
        """Apply F1-inspired styling to matplotlib axes."""
        # Background colors
        self.axes.set_facecolor('#0A0A0A')
        self.figure.patch.set_facecolor('#1A1A1A')

        # Grid
        self.axes.grid(True, alpha=0.2, color='#3A3A3A', linestyle='--')

        # Spines (borders)
        self.axes.spines['bottom'].set_color('#C0C0C0')
        self.axes.spines['left'].set_color('#C0C0C0')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        # Tick colors
        self.axes.tick_params(
            axis='both',
            colors='#C0C0C0',
            labelsize=9
        )

        # Labels
        self.axes.set_xlabel('Frame Number', color='#C0C0C0', fontsize=10)
        self.axes.set_ylabel('Angle (degrees)', color='#C0C0C0', fontsize=10)

    def _setup_ui(self):
        """Set up widget UI."""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Controls bar
        controls_layout = QHBoxLayout()

        # Angle selector
        angle_label = QLabel("Angle:")
        angle_label.setStyleSheet("color: #C0C0C0; font-weight: 600; background-color: #1A1A1A;")
        controls_layout.addWidget(angle_label)

        self.angle_selector = QComboBox()
        self.angle_selector.setMinimumWidth(150)
        self.angle_selector.currentTextChanged.connect(self._on_angle_selected)
        controls_layout.addWidget(self.angle_selector)

        controls_layout.addSpacing(10)

        # Show markers checkbox
        self.show_markers_checkbox = QCheckBox("Show Key Positions")
        self.show_markers_checkbox.setChecked(True)
        self.show_markers_checkbox.toggled.connect(lambda: self.refresh())
        controls_layout.addWidget(self.show_markers_checkbox)

        controls_layout.addStretch()

        # Export button
        self.export_btn = QPushButton("📷 Export Graph")
        self.export_btn.clicked.connect(self.export_image_dialog)
        controls_layout.addWidget(self.export_btn)

        layout.addLayout(controls_layout)

        # Canvas
        layout.addWidget(self.canvas, stretch=1)

        # Frame info label
        self.frame_info_label = QLabel("Hover over graph to see values")
        self.frame_info_label.setStyleSheet("""
            color: #A0A0A0;
            font-size: 10px;
            padding: 5px;
            background-color: #1A1A1A;
        """)
        layout.addWidget(self.frame_info_label)

        self.setLayout(layout)

        # Apply F1 styling
        self._apply_styling()

    def _apply_styling(self):
        """Apply F1-inspired styling to controls."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #E8E8E8;
            }
            QComboBox {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px;
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
            QPushButton {
                background-color: #2A2A2A;
                color: #E8E8E8;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px 15px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
                border: 1px solid #C0C0C0;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
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

    def set_angle_options(self, angle_names: List[str]):
        """Set available angle options in dropdown.

        Args:
            angle_names: List of angle names
        """
        self.angle_selector.clear()

        # Format angle names for display
        display_names = [self._format_angle_name(name) for name in angle_names]

        self.angle_selector.addItems(display_names)

        # Store mapping
        self._angle_name_map = dict(zip(display_names, angle_names))

    def _format_angle_name(self, internal_name: str) -> str:
        """Convert internal name to display name.

        Args:
            internal_name: e.g., 'spine_angle'

        Returns:
            Display name: e.g., 'Spine Angle'
        """
        return internal_name.replace('_', ' ').title()

    def _on_angle_selected(self, display_name: str):
        """Handle angle selection from dropdown.

        Args:
            display_name: Display name of selected angle
        """
        if hasattr(self, '_angle_name_map') and display_name in self._angle_name_map:
            internal_name = self._angle_name_map[display_name]
            self.angle_selected.emit(internal_name)

    def plot_angle(
        self,
        frames: np.ndarray,
        values: np.ndarray,
        angle_name: str,
        color: str = '#00FF00',
        label: Optional[str] = None
    ):
        """Plot angle data on graph.

        Args:
            frames: Frame numbers
            values: Angle values in degrees
            angle_name: Name of angle for title
            color: Line color (hex)
            label: Optional label for legend
        """
        self.axes.clear()
        self._style_axes()

        self.current_angle_name = angle_name
        self.comparison_mode = False

        if len(frames) == 0:
            self.axes.text(
                0.5, 0.5, 'No data available',
                ha='center', va='center',
                color='#C0C0C0',
                transform=self.axes.transAxes
            )
            self.canvas.draw()
            return

        # Plot line
        self.axes.plot(
            frames, values,
            color=color,
            linewidth=2,
            label=label or self._format_angle_name(angle_name)
        )

        # Set title
        self.axes.set_title(
            self._format_angle_name(angle_name),
            color='#E8E8E8',
            fontsize=12,
            fontweight='bold',
            pad=10
        )

        # Add key position markers
        if self.show_markers_checkbox.isChecked():
            self._add_key_position_markers(frames, values)

        # Legend
        self.axes.legend(
            loc='upper right',
            facecolor='#2A2A2A',
            edgecolor='#3A3A3A',
            labelcolor='#E8E8E8',
            fontsize=9
        )

        self.canvas.draw()

    def plot_comparison(
        self,
        data1: Tuple[np.ndarray, np.ndarray],
        data2: Tuple[np.ndarray, np.ndarray],
        angle_name: str,
        labels: Tuple[str, str] = ('Swing 1', 'Swing 2'),
        colors: Tuple[str, str] = ('#FF6B6B', '#51CF66')
    ):
        """Plot two angle series for comparison.

        Args:
            data1: Tuple of (frames, values) for first swing
            data2: Tuple of (frames, values) for second swing
            angle_name: Name of angle
            labels: Labels for legend
            colors: Line colors (color1, color2)
        """
        self.axes.clear()
        self._style_axes()

        self.current_angle_name = angle_name
        self.comparison_mode = True

        frames1, values1 = data1
        frames2, values2 = data2

        # Plot both lines
        if len(frames1) > 0:
            self.axes.plot(
                frames1, values1,
                color=colors[0],
                linewidth=2,
                label=labels[0]
            )

        if len(frames2) > 0:
            self.axes.plot(
                frames2, values2,
                color=colors[1],
                linewidth=2,
                label=labels[1],
                linestyle='--'  # Dashed for distinction
            )

        # Set title
        self.axes.set_title(
            f"{self._format_angle_name(angle_name)} Comparison",
            color='#E8E8E8',
            fontsize=12,
            fontweight='bold',
            pad=10
        )

        # Legend
        self.axes.legend(
            loc='upper right',
            facecolor='#2A2A2A',
            edgecolor='#3A3A3A',
            labelcolor='#E8E8E8',
            fontsize=9
        )

        self.canvas.draw()

    def _add_key_position_markers(self, frames: np.ndarray, values: np.ndarray):
        """Add vertical lines for key positions.

        Args:
            frames: Frame numbers in plot
            values: Values for y-axis range
        """
        if not self.key_positions:
            return

        for position_name, frame_num in self.key_positions.items():
            # Only show if frame is in range
            if frame_num < frames[0] or frame_num > frames[-1]:
                continue

            # Add vertical line
            self.axes.axvline(
                x=frame_num,
                color='#FFD700',  # Gold
                linestyle=':',
                linewidth=1,
                alpha=0.6
            )

            # Add label at top
            y_max = np.max(values)
            self.axes.text(
                frame_num, y_max,
                position_name.replace('_', '\n'),
                color='#FFD700',
                fontsize=8,
                ha='center',
                va='bottom',
                rotation=0
            )

    def update_current_frame_marker(self, frame_number: int):
        """Update vertical line showing current video frame.

        Args:
            frame_number: Current frame to highlight
        """
        # Remove old marker
        if self.current_frame_marker is not None:
            try:
                self.current_frame_marker.remove()
            except Exception:
                pass

        # Add new marker
        self.current_frame_marker = self.axes.axvline(
            x=frame_number,
            color='#FFFFFF',
            linestyle='-',
            linewidth=2,
            alpha=0.8
        )

        self.canvas.draw()

    def set_key_positions(self, positions: Dict[str, int]):
        """Set key swing positions for markers.

        Args:
            positions: Dictionary of position_name -> frame_number
        """
        self.key_positions = positions
        logger.debug(f"Set {len(positions)} key positions")

    def _on_canvas_click(self, event):
        """Handle click on canvas.

        Args:
            event: Matplotlib mouse event
        """
        if event.inaxes == self.axes and event.xdata is not None:
            frame_number = int(round(event.xdata))
            self.frame_clicked.emit(frame_number)
            logger.debug(f"Graph clicked at frame {frame_number}")

    def refresh(self):
        """Refresh the graph display."""
        self.canvas.draw()

    def export_image_dialog(self):
        """Open dialog to export graph as image."""
        from PyQt5.QtWidgets import QFileDialog

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Graph",
            "angle_graph.png",
            "PNG Images (*.png);;SVG Images (*.svg);;All Files (*)"
        )

        if filepath:
            self.export_image(filepath)

    def export_image(self, filepath: str):
        """Export graph to image file.

        Args:
            filepath: Output file path (.png or .svg)
        """
        try:
            self.figure.savefig(
                filepath,
                facecolor='#1A1A1A',
                edgecolor='none',
                dpi=150,
                bbox_inches='tight'
            )
            logger.info(f"Exported graph to {filepath}")

        except Exception as e:
            logger.error(f"Failed to export graph: {e}", exc_info=True)
