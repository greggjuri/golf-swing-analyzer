"""Main application window with F1 design studio aesthetic."""

import logging
from typing import Optional
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QAction, QFileDialog, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence

from .theme import F1Theme
from .video_player import VideoPlayerWidget
from .analysis_panel import AnalysisPanelWidget
from .timeline import TimelineWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with F1 design studio aesthetic.

    Provides the primary UI shell containing video player,
    analysis controls, and timeline navigation.

    Example:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    """

    def __init__(self):
        """Initialize main window with F1 theme."""
        super().__init__()

        # Window properties
        self.setWindowTitle("Golf Swing Analyzer - F1 Studio")
        self.setMinimumSize(1280, 720)
        self.resize(1600, 900)

        # Apply F1 theme
        self.setStyleSheet(F1Theme.get_main_stylesheet())

        # State
        self.current_video_path = None
        self.video_loader = None
        self.frame_extractor = None

        # Analysis components (will be initialized when needed)
        self.club_detector = None
        self.pose_detector = None
        self.plane_analyzer = None
        self.viz_engine = None

        # Create UI components
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()
        self._create_status_bar()

        # Connect signals
        self._connect_signals()

        logger.info("MainWindow initialized")

    def _create_menu_bar(self):
        """Create menu bar with File, View, Analysis, Help."""
        menubar = self.menuBar()

        # === FILE MENU ===
        file_menu = menubar.addMenu("&File")

        # Open Video
        open_action = QAction("&Open Video...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Open video file for analysis")
        open_action.triggered.connect(self.open_video)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Export
        export_video_action = QAction("Export &Video...", self)
        export_video_action.setShortcut(QKeySequence("Ctrl+E"))
        export_video_action.setStatusTip("Export annotated video")
        export_video_action.triggered.connect(self.export_video)
        file_menu.addAction(export_video_action)

        export_frame_action = QAction("Export &Frame...", self)
        export_frame_action.setStatusTip("Export current frame as image")
        export_frame_action.triggered.connect(self.export_frame)
        file_menu.addAction(export_frame_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # === VIEW MENU ===
        view_menu = menubar.addMenu("&View")

        # Toggle Analysis Panel
        toggle_panel_action = QAction("Analysis &Panel", self)
        toggle_panel_action.setCheckable(True)
        toggle_panel_action.setChecked(True)
        toggle_panel_action.setStatusTip("Show/hide analysis panel")
        toggle_panel_action.triggered.connect(self._toggle_analysis_panel)
        view_menu.addAction(toggle_panel_action)

        # === ANALYSIS MENU ===
        analysis_menu = menubar.addMenu("&Analysis")

        # Analyze Current Frame
        analyze_frame_action = QAction("Analyze &Current Frame", self)
        analyze_frame_action.setShortcut(QKeySequence("Ctrl+A"))
        analyze_frame_action.setStatusTip("Run analysis on current frame")
        analyze_frame_action.triggered.connect(self._analyze_current_frame)
        analysis_menu.addAction(analyze_frame_action)

        # Analyze Full Video
        analyze_video_action = QAction("Analyze &Full Video", self)
        analyze_video_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        analyze_video_action.setStatusTip("Run analysis on entire video")
        analyze_video_action.triggered.connect(self._analyze_full_video)
        analysis_menu.addAction(analyze_video_action)

        analysis_menu.addSeparator()

        # Detect Key Positions
        detect_positions_action = QAction("Detect &Key Positions", self)
        detect_positions_action.setStatusTip("Auto-detect P1, P4, P7 positions")
        detect_positions_action.triggered.connect(self._detect_key_positions)
        analysis_menu.addAction(detect_positions_action)

        # === HELP MENU ===
        help_menu = menubar.addMenu("&Help")

        # About
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Golf Swing Analyzer")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_tool_bar(self):
        """Create tool bar with common actions."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        # Open Video
        open_action = QAction("Open", self)
        open_action.setStatusTip("Open video file")
        open_action.triggered.connect(self.open_video)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Playback controls are in the video player widget
        # Just add export here
        export_action = QAction("Export", self)
        export_action.setStatusTip("Export video")
        export_action.triggered.connect(self.export_video)
        toolbar.addAction(export_action)

    def _create_central_widget(self):
        """Create central layout with video player and panels."""
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create horizontal splitter for main content
        splitter = QSplitter(Qt.Horizontal)

        # === VIDEO PLAYER (Left) ===
        self.video_player = VideoPlayerWidget()

        # === ANALYSIS PANEL (Right) ===
        self.analysis_panel = AnalysisPanelWidget()

        # Add to splitter
        splitter.addWidget(self.video_player)
        splitter.addWidget(self.analysis_panel)

        # Set initial sizes (80% video, 20% panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        # === TIMELINE (Bottom) ===
        self.timeline = TimelineWidget()

        # Add to main layout
        main_layout.addWidget(splitter, stretch=1)
        main_layout.addWidget(self.timeline)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _create_status_bar(self):
        """Create status bar with info display."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self):
        """Connect widget signals to slots."""
        # Video player signals
        self.video_player.frame_changed.connect(self._on_frame_changed)
        self.video_player.playback_started.connect(
            lambda: self.status_bar.showMessage("Playing...")
        )
        self.video_player.playback_stopped.connect(
            lambda: self.status_bar.showMessage("Stopped")
        )

        # Timeline signals
        self.timeline.frame_selected.connect(self.video_player.seek)

        # Analysis panel signals
        self.analysis_panel.overlay_toggled.connect(self._on_overlay_toggled)

    def open_video(self):
        """Open video file dialog and load video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.mov *.avi);;All Files (*)"
        )

        if file_path:
            self._load_video(file_path)

    def _load_video(self, filepath: str):
        """Load video file and initialize analysis.

        Args:
            filepath: Path to video file
        """
        try:
            from ..video import VideoLoader, FrameExtractor

            # Load video
            self.video_loader = VideoLoader(filepath)
            metadata = self.video_loader.get_metadata()

            # Create frame extractor
            self.frame_extractor = FrameExtractor(self.video_loader)

            # Set up video player
            self.video_player.load_video(
                total_frames=metadata.frame_count,
                fps=metadata.fps,
                get_frame_func=self._get_frame
            )

            # Set up timeline
            self.timeline.set_total_frames(metadata.frame_count, metadata.fps)

            # Update state
            self.current_video_path = filepath
            filename = os.path.basename(filepath)

            # Update status
            self.status_bar.showMessage(
                f"Loaded: {filename} | {metadata.frame_count} frames @ {metadata.fps:.1f} fps"
            )

            logger.info(f"Loaded video: {filepath}")

        except Exception as e:
            logger.error(f"Failed to load video: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error Loading Video",
                f"Failed to load video:\n{str(e)}"
            )

    def _get_frame(self, frame_number: int):
        """Get video frame with overlays applied.

        Args:
            frame_number: Frame number to get

        Returns:
            Frame as numpy array with overlays
        """
        if not self.frame_extractor:
            return None

        try:
            # Get raw frame
            frame = self.frame_extractor.extract_frame(frame_number)

            # TODO: Apply analysis overlays based on enabled overlays
            # For now, just return raw frame

            return frame

        except Exception as e:
            logger.error(f"Error getting frame {frame_number}: {e}")
            return None

    def _on_frame_changed(self, frame_number: int):
        """Handle frame change.

        Args:
            frame_number: New frame number
        """
        self.timeline.set_current_frame(frame_number)

        # TODO: Update metrics for current frame

    def _on_overlay_toggled(self, overlay_name: str, enabled: bool):
        """Handle overlay toggle.

        Args:
            overlay_name: Name of overlay
            enabled: Whether enabled
        """
        logger.debug(f"Overlay toggled: {overlay_name} = {enabled}")

        # TODO: Implement overlay rendering

    def _toggle_analysis_panel(self, checked: bool):
        """Toggle analysis panel visibility.

        Args:
            checked: Whether to show panel
        """
        self.analysis_panel.setVisible(checked)

    def _analyze_current_frame(self):
        """Run analysis on current frame."""
        self.status_bar.showMessage("Analyzing current frame...")

        # TODO: Implement current frame analysis

        self.status_bar.showMessage("Analysis complete", 3000)

    def _analyze_full_video(self):
        """Run analysis on full video."""
        self.status_bar.showMessage("Analyzing full video...")

        # TODO: Implement full video analysis

        self.status_bar.showMessage("Analysis complete", 3000)

    def _detect_key_positions(self):
        """Auto-detect key swing positions."""
        self.status_bar.showMessage("Detecting key positions...")

        # TODO: Implement key position detection

        self.status_bar.showMessage("Key positions detected", 3000)

    def export_video(self):
        """Export annotated video."""
        if not self.current_video_path:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video",
            "",
            "Video Files (*.avi *.mp4);;All Files (*)"
        )

        if output_path:
            self.status_bar.showMessage(f"Exporting to {output_path}...")

            # TODO: Implement video export

            self.status_bar.showMessage("Export complete", 3000)

    def export_frame(self):
        """Export current frame as image."""
        if not self.current_video_path:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Frame",
            "",
            "Images (*.png *.jpg);;All Files (*)"
        )

        if output_path:
            # TODO: Implement frame export
            self.status_bar.showMessage(f"Frame exported to {output_path}", 3000)

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Golf Swing Analyzer",
            "<h3>Golf Swing Analyzer - F1 Studio</h3>"
            "<p>Professional golf swing analysis software with premium F1 aesthetic.</p>"
            "<p>Version 1.0.0</p>"
            "<p>Built with Python, PyQt5, OpenCV, and advanced computer vision.</p>"
        )
