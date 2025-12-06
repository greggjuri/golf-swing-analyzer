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
        self.club_tracker = None
        self.pose_detector = None
        self.pose_tracker = None
        self.plane_analyzer = None
        self.viz_engine = None
        self.key_position_detector = None

        # Analysis results cache
        self.club_results = {}  # frame_num -> club data
        self.pose_results = {}  # frame_num -> landmarks
        self.plane_results = None  # Swing plane analysis results
        self.key_positions = {}  # position_name -> frame_num

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

    def _initialize_analysis_components(self):
        """Initialize analysis components for loaded video."""
        from ..detection import ClubDetector, ClubTracker
        from ..pose import PoseDetector, PoseTracker
        from ..video import KeyPositionDetector
        from ..plane import SwingPlaneAnalyzer
        from ..visualization import VisualizationEngine

        try:
            # Initialize club tracking
            self.club_detector = ClubDetector()
            self.club_tracker = ClubTracker()

            # Initialize pose detection
            self.pose_detector = PoseDetector()
            self.pose_tracker = PoseTracker()

            # Initialize swing plane analyzer
            self.plane_analyzer = SwingPlaneAnalyzer()

            # Initialize visualization engine
            self.viz_engine = VisualizationEngine()

            # Initialize key position detector
            self.key_position_detector = KeyPositionDetector()

            logger.info("Analysis components initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize some analysis components: {e}")
            # Continue even if some components fail

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

            # Initialize analysis components
            self._initialize_analysis_components()

            # Clear previous analysis results
            self.club_results.clear()
            self.pose_results.clear()
            self.plane_results = None
            self.key_positions.clear()

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

            # Apply overlays if visualization engine is available
            if self.viz_engine and frame is not None:
                frame = self._apply_overlays(frame, frame_number)

            return frame

        except Exception as e:
            logger.error(f"Error getting frame {frame_number}: {e}")
            return None

    def _apply_overlays(self, frame, frame_number: int):
        """Apply enabled overlays to frame.

        Args:
            frame: Frame to annotate
            frame_number: Current frame number

        Returns:
            Annotated frame
        """
        import numpy as np

        # Get enabled overlays from analysis panel
        enabled_overlays = self.analysis_panel.get_enabled_overlays()

        try:
            # Prepare data for visualization engine
            club_data = None
            body_landmarks = None
            show_skeleton = enabled_overlays.get('skeleton', False)
            show_angles = enabled_overlays.get('angles', False)

            # Get club detection if enabled
            if enabled_overlays.get('club_track', False):
                if frame_number in self.club_results:
                    club_data = self.club_results[frame_number]

            # Get pose landmarks if skeleton or angles enabled
            if show_skeleton or show_angles:
                if frame_number in self.pose_results:
                    body_landmarks = self.pose_results[frame_number]

            # Render using visualization engine
            annotated_frame = self.viz_engine.render(
                frame,
                club_detection=club_data,
                body_landmarks=body_landmarks,
                show_angles=show_angles,
                show_skeleton=show_skeleton
            )

            # Add key position label if this frame is a key position
            if enabled_overlays.get('key_positions', False):
                if frame_number in self.key_positions.values():
                    position_name = next(
                        (k for k, v in self.key_positions.items() if v == frame_number),
                        None
                    )
                    if position_name:
                        # Add position label
                        import cv2
                        from .visualization import draw_text_with_background
                        try:
                            from ..visualization.utils import draw_text_with_background
                            draw_text_with_background(
                                annotated_frame,
                                position_name.replace('_', ' ').title(),
                                (20, 40),
                                scale=1.0,
                                color=(255, 255, 255),
                                thickness=2
                            )
                        except:
                            # Fallback to simple text
                            cv2.putText(
                                annotated_frame,
                                position_name.replace('_', ' ').title(),
                                (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.0,
                                (255, 255, 255),
                                2
                            )

            return annotated_frame

        except Exception as e:
            logger.error(f"Error applying overlays to frame {frame_number}: {e}")
            return frame.copy()

    def _on_frame_changed(self, frame_number: int):
        """Handle frame change.

        Args:
            frame_number: New frame number
        """
        self.timeline.set_current_frame(frame_number)

        # Update metrics for current frame
        self._update_metrics(frame_number)

    def _update_metrics(self, frame_number: int):
        """Update metrics display for current frame.

        Args:
            frame_number: Current frame number
        """
        metrics = {}

        try:
            # Get swing plane metrics if available
            if self.plane_results is not None:
                plane_metrics = self.plane_results.get('metrics', {})
                if 'attack_angle' in plane_metrics:
                    metrics['attack_angle'] = plane_metrics['attack_angle']
                if 'swing_path' in plane_metrics:
                    metrics['swing_path'] = plane_metrics['swing_path']
                if 'plane_angle' in plane_metrics:
                    metrics['plane_angle'] = plane_metrics['plane_angle']

            # Get club speed if available (would need to calculate from club positions)
            if frame_number in self.club_results:
                # Calculate club speed from recent frames
                club_speed = self._calculate_club_speed(frame_number)
                if club_speed is not None:
                    metrics['club_speed'] = club_speed

            # Update the panel
            if metrics:
                self.analysis_panel.update_metrics(metrics)

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    def _calculate_club_speed(self, frame_number: int) -> Optional[float]:
        """Calculate club head speed from recent frames.

        Args:
            frame_number: Current frame number

        Returns:
            Club speed in mph, or None if not enough data
        """
        # Need at least 2 frames to calculate speed
        if frame_number < 1:
            return None

        try:
            # Get current and previous club positions
            if frame_number not in self.club_results or (frame_number - 1) not in self.club_results:
                return None

            current = self.club_results[frame_number]
            previous = self.club_results[frame_number - 1]

            # Get club head positions
            if 'club_head' not in current or 'club_head' not in previous:
                return None

            curr_pos = current['club_head']
            prev_pos = previous['club_head']

            # Calculate distance moved in pixels
            import numpy as np
            distance_px = np.linalg.norm(
                np.array(curr_pos) - np.array(prev_pos)
            )

            # Convert to real-world units (would need calibration)
            # For now, use a rough estimate: assume 1 meter = 100 pixels
            distance_m = distance_px / 100.0

            # Calculate speed (distance per frame * fps = distance per second)
            if self.video_loader:
                metadata = self.video_loader.get_metadata()
                speed_mps = distance_m * metadata.fps

                # Convert m/s to mph
                speed_mph = speed_mps * 2.23694

                return speed_mph

        except Exception as e:
            logger.error(f"Error calculating club speed: {e}")

        return None

    def _on_overlay_toggled(self, overlay_name: str, enabled: bool):
        """Handle overlay toggle.

        Args:
            overlay_name: Name of overlay
            enabled: Whether enabled
        """
        logger.debug(f"Overlay toggled: {overlay_name} = {enabled}")

        # Refresh current frame to apply/remove overlay
        if self.video_player:
            self.video_player.refresh()

    def _toggle_analysis_panel(self, checked: bool):
        """Toggle analysis panel visibility.

        Args:
            checked: Whether to show panel
        """
        self.analysis_panel.setVisible(checked)

    def _analyze_current_frame(self):
        """Run analysis on current frame."""
        if not self.video_player or not self.frame_extractor:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        self.status_bar.showMessage("Analyzing current frame...")

        try:
            # Get current frame number
            frame_number = self.video_player.get_current_frame()
            frame = self.frame_extractor.extract_frame(frame_number)

            if frame is None:
                raise ValueError("Could not extract frame")

            # Run club detection
            if self.club_detector and self.club_tracker:
                club_data = self.club_detector.detect(frame)
                if club_data:
                    # Store in results
                    self.club_results[frame_number] = club_data
                    logger.debug(f"Club detected in frame {frame_number}")

            # Run pose detection
            if self.pose_detector and self.pose_tracker:
                landmarks = self.pose_detector.detect(frame)
                if landmarks:
                    # Store in results
                    self.pose_results[frame_number] = landmarks
                    logger.debug(f"Pose detected in frame {frame_number}")

            # Refresh display to show new overlays
            self.video_player.refresh()

            # Update metrics
            self._update_metrics(frame_number)

            self.status_bar.showMessage("Analysis complete", 3000)

        except Exception as e:
            logger.error(f"Error analyzing frame: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Failed to analyze frame:\n{str(e)}"
            )
            self.status_bar.showMessage("Analysis failed")

    def _analyze_full_video(self):
        """Run analysis on full video."""
        if not self.video_loader or not self.frame_extractor:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        # Confirm with user (this could take time)
        metadata = self.video_loader.get_metadata()
        reply = QMessageBox.question(
            self,
            "Analyze Full Video",
            f"Analyze all {metadata.frame_count} frames?\n"
            f"This may take several minutes.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.status_bar.showMessage("Analyzing full video...")

        try:
            # Clear previous results
            self.club_results.clear()
            self.pose_results.clear()

            # Process all frames
            total_frames = metadata.frame_count
            club_positions = []  # For swing plane analysis

            for frame_num in range(total_frames):
                # Update status every 10 frames
                if frame_num % 10 == 0:
                    progress = int((frame_num / total_frames) * 100)
                    self.status_bar.showMessage(
                        f"Analyzing frame {frame_num}/{total_frames} ({progress}%)"
                    )

                # Extract frame
                frame = self.frame_extractor.extract_frame(frame_num)
                if frame is None:
                    continue

                # Run club detection
                if self.club_detector:
                    club_data = self.club_detector.detect(frame)
                    if club_data:
                        self.club_results[frame_num] = club_data
                        # Collect club positions for plane analysis
                        if 'shaft_line' in club_data:
                            club_positions.append((frame_num, club_data['shaft_line']))

                # Run pose detection
                if self.pose_detector:
                    landmarks = self.pose_detector.detect(frame)
                    if landmarks:
                        self.pose_results[frame_num] = landmarks

            # Apply temporal smoothing to club tracking
            if self.club_tracker and self.club_results:
                smoothed_results = self.club_tracker.track_sequence(
                    list(self.club_results.values())
                )
                # Update with smoothed results
                for frame_num, smoothed_data in zip(self.club_results.keys(), smoothed_results):
                    if smoothed_data:
                        self.club_results[frame_num] = smoothed_data

            # Apply temporal smoothing to pose tracking
            if self.pose_tracker and self.pose_results:
                smoothed_poses = self.pose_tracker.track_sequence(
                    list(self.pose_results.values())
                )
                # Update with smoothed results
                for frame_num, smoothed_landmarks in zip(self.pose_results.keys(), smoothed_poses):
                    if smoothed_landmarks:
                        self.pose_results[frame_num] = smoothed_landmarks

            # Run swing plane analysis if we have club positions
            if self.plane_analyzer and club_positions:
                self.status_bar.showMessage("Calculating swing plane...")
                self.plane_results = self.plane_analyzer.analyze(club_positions)

            # Refresh display
            self.video_player.refresh()

            # Update metrics
            current_frame = self.video_player.get_current_frame()
            self._update_metrics(current_frame)

            self.status_bar.showMessage(
                f"Analysis complete: {len(self.club_results)} club detections, "
                f"{len(self.pose_results)} pose detections", 5000
            )

            logger.info(f"Full video analysis complete: {total_frames} frames")

        except Exception as e:
            logger.error(f"Error analyzing video: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Failed to analyze video:\n{str(e)}"
            )
            self.status_bar.showMessage("Analysis failed")

    def _detect_key_positions(self):
        """Auto-detect key swing positions."""
        if not self.video_loader or not self.key_position_detector:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        self.status_bar.showMessage("Detecting key positions...")

        try:
            # Extract all frames for analysis
            metadata = self.video_loader.get_metadata()
            frames = []
            for i in range(metadata.frame_count):
                frame = self.frame_extractor.extract_frame(i)
                if frame is not None:
                    frames.append(frame)

            # Detect key positions
            positions = self.key_position_detector.detect_positions(frames)

            # Store detected positions
            self.key_positions = positions

            # Add markers to timeline
            position_colors = {
                'address': '#00FF00',  # Green
                'top_of_backswing': '#FFFF00',  # Yellow
                'impact': '#FF0000',  # Red
                'follow_through': '#00FFFF'  # Cyan
            }

            for position_name, frame_num in positions.items():
                color = position_colors.get(position_name, '#FFFFFF')
                self.timeline.add_key_position(position_name, frame_num, color)

            self.status_bar.showMessage(
                f"Detected {len(positions)} key positions", 3000
            )

            logger.info(f"Key positions detected: {positions}")

        except Exception as e:
            logger.error(f"Error detecting key positions: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Detection Error",
                f"Failed to detect key positions:\n{str(e)}"
            )
            self.status_bar.showMessage("Detection failed")

    def export_video(self):
        """Export annotated video."""
        if not self.current_video_path or not self.video_loader:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        # Get default filename
        from pathlib import Path
        video_name = Path(self.current_video_path).stem
        default_name = f"{video_name}_annotated.avi"

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video",
            default_name,
            "AVI Video (*.avi);;MP4 Video (*.mp4);;All Files (*)"
        )

        if output_path:
            # Confirm with user (this could take time)
            metadata = self.video_loader.get_metadata()
            reply = QMessageBox.question(
                self,
                "Export Video",
                f"Export {metadata.frame_count} frames with overlays?\n"
                f"This may take several minutes.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            self.status_bar.showMessage(f"Exporting to {output_path}...")

            try:
                from ..export import VideoExporter
                import cv2

                # Determine codec based on file extension
                ext = Path(output_path).suffix.lower()
                if ext == '.mp4':
                    codec = 'mp4v'
                else:
                    codec = 'MJPG'  # Default to MJPEG for .avi

                # Get frame size from first frame
                first_frame = self._get_frame(0)
                if first_frame is None:
                    raise ValueError("Could not get first frame")

                height, width = first_frame.shape[:2]

                # Create video exporter
                with VideoExporter(
                    output_path,
                    fps=metadata.fps,
                    frame_size=(width, height),
                    codec=codec
                ) as exporter:

                    # Export all frames
                    total_frames = metadata.frame_count
                    for frame_num in range(total_frames):
                        # Update progress every 10 frames
                        if frame_num % 10 == 0:
                            progress = int((frame_num / total_frames) * 100)
                            self.status_bar.showMessage(
                                f"Exporting frame {frame_num}/{total_frames} ({progress}%)"
                            )

                        # Get frame with overlays
                        frame = self._get_frame(frame_num)
                        if frame is not None:
                            exporter.add_frame(frame)

                self.status_bar.showMessage(f"Export complete: {output_path}", 5000)
                logger.info(f"Exported video to {output_path}")

            except Exception as e:
                logger.error(f"Error exporting video: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export video:\n{str(e)}"
                )
                self.status_bar.showMessage("Export failed")

    def export_frame(self):
        """Export current frame as image."""
        if not self.current_video_path or not self.video_player:
            QMessageBox.warning(
                self,
                "No Video Loaded",
                "Please load a video first."
            )
            return

        # Get default filename
        import os
        from pathlib import Path
        video_name = Path(self.current_video_path).stem
        frame_num = self.video_player.get_current_frame()
        default_name = f"{video_name}_frame_{frame_num:04d}.png"

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Frame",
            default_name,
            "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)"
        )

        if output_path:
            try:
                from ..export import FrameExporter

                # Get current frame with overlays
                frame = self._get_frame(frame_num)

                if frame is None:
                    raise ValueError("Could not get frame")

                # Create exporter and export frame
                exporter = FrameExporter()
                exporter.export_frame(frame, output_path)

                self.status_bar.showMessage(f"Frame exported to {output_path}", 3000)
                logger.info(f"Exported frame {frame_num} to {output_path}")

            except Exception as e:
                logger.error(f"Error exporting frame: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export frame:\n{str(e)}"
                )
                self.status_bar.showMessage("Export failed")

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
