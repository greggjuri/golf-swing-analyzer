# PRP: GUI Main Window Layout

## Overview
Build the main application window with F1 design studio aesthetic - sleek, modern, high-tech with glass morphism effects, black/white/silver color scheme, and premium feel inspired by McLaren mission control.

## Objectives
1. Create main application window with modern F1 aesthetic
2. Implement video player widget with professional controls
3. Build analysis control panel with real-time metrics display
4. Add timeline scrubber with key position markers
5. Design glass morphism UI with black/white/silver theme
6. Integrate all existing analysis features into unified interface

## Design Philosophy

### F1 Design Studio Aesthetic
- **Glass Morphism**: Frosted glass effects with blur and transparency
- **Color Scheme**:
  - Primary: Deep black (#0A0A0A, #121212)
  - Secondary: Pure white (#FFFFFF, #F5F5F5)
  - Accent: Metallic silver (#C0C0C0, #E8E8E8)
  - Highlights: Chrome/platinum (#BEBEBE)
- **Typography**: Sharp, modern sans-serif (Segoe UI, Roboto)
- **Spacing**: Clean, generous white space for premium feel
- **Shadows**: Subtle depth with soft shadows
- **Animations**: Smooth 60fps transitions

### Visual Elements
- Glossy panels with subtle reflections
- Thin, precise divider lines
- Rounded corners (4-8px radius)
- Subtle gradients for depth
- Metallic sheen on active elements

## Architecture

### Module Structure
```
src/gui/
├── __init__.py              # Module exports
├── theme.py                 # F1 theme and style sheets
├── main_window.py           # MainWindow - application shell
├── video_player.py          # VideoPlayerWidget - video display and controls
├── analysis_panel.py        # AnalysisPanelWidget - metrics and settings
├── timeline.py              # TimelineWidget - scrubber and markers
├── widgets/
│   ├── __init__.py
│   ├── glass_panel.py       # GlassPanel - frosted glass container
│   ├── metric_display.py    # MetricDisplay - numeric value display
│   ├── toggle_button.py     # ToggleButton - styled toggle control
│   └── slider.py            # StyledSlider - custom slider with F1 style
└── utils/
    ├── __init__.py
    └── icons.py             # Icon loading and management
```

## Core Components

### 1. F1 Theme System (theme.py)

**F1Theme Class:**
```python
class F1Theme:
    """F1 design studio color theme and styles.

    Provides color palette, style sheets, and visual constants
    for the premium F1 aesthetic.
    """

    # Color Palette
    BLACK_PRIMARY = "#0A0A0A"
    BLACK_SECONDARY = "#121212"
    BLACK_PANEL = "#1A1A1A"

    WHITE_PRIMARY = "#FFFFFF"
    WHITE_SECONDARY = "#F5F5F5"
    WHITE_TEXT = "#E8E8E8"

    SILVER_LIGHT = "#E8E8E8"
    SILVER_MID = "#C0C0C0"
    SILVER_DARK = "#BEBEBE"

    ACCENT_CYAN = "#00D9FF"      # Optional tech accent
    ACCENT_RED = "#FF003D"       # Optional warning/record

    # Glass Morphism
    GLASS_BACKGROUND = "rgba(26, 26, 26, 0.7)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.1)"
    GLASS_BLUR = 10  # pixels

    # Shadows
    SHADOW_SOFT = "0 2px 8px rgba(0, 0, 0, 0.3)"
    SHADOW_ELEVATED = "0 4px 16px rgba(0, 0, 0, 0.5)"

    # Spacing
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24

    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 6
    RADIUS_LARGE = 8

    @staticmethod
    def get_main_stylesheet() -> str:
        """Get main application stylesheet."""

    @staticmethod
    def get_glass_panel_stylesheet() -> str:
        """Get glass morphism panel stylesheet."""

    @staticmethod
    def get_button_stylesheet() -> str:
        """Get button stylesheet."""
```

**Style Sheets:**
```css
/* Main Window */
QMainWindow {
    background-color: #0A0A0A;
    color: #E8E8E8;
}

/* Glass Panel */
.GlassPanel {
    background: rgba(26, 26, 26, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    backdrop-filter: blur(10px);
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2A2A2A, stop:1 #1A1A1A);
    border: 1px solid #3A3A3A;
    border-radius: 4px;
    color: #E8E8E8;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3A3A3A, stop:1 #2A2A2A);
    border: 1px solid #C0C0C0;
}

QPushButton:pressed {
    background: #1A1A1A;
}

/* Sliders */
QSlider::groove:horizontal {
    background: #2A2A2A;
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #E8E8E8, stop:1 #C0C0C0);
    border: 1px solid #BEBEBE;
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
```

### 2. Main Window (main_window.py)

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────┐
│ Menu Bar: File | View | Analysis | Help                │
├─────────────────────────────────────────────────────────┤
│ Tool Bar: [Open] [Play] [Stop] [Export] ...            │
├────────────────────────────┬────────────────────────────┤
│                            │                            │
│                            │   Analysis Panel           │
│                            │   ┌──────────────────────┐ │
│                            │   │ METRICS              │ │
│   Video Player             │   │ ───────────────────  │ │
│   (Central Widget)         │   │ Attack: -5.2°        │ │
│                            │   │ Path: +2.1°          │ │
│   ┌──────────────────────┐ │   │ Plane: 47.3°         │ │
│   │                      │ │   └──────────────────────┘ │
│   │   [Video Display]    │ │   ┌──────────────────────┐ │
│   │                      │ │   │ OVERLAYS             │ │
│   │                      │ │   │ ☑ Club Track         │ │
│   └──────────────────────┘ │   │ ☑ Swing Plane        │ │
│                            │   │ ☐ Skeleton           │ │
│   [Timeline & Scrubber]    │   └──────────────────────┘ │
│                            │                            │
├────────────────────────────┴────────────────────────────┤
│ Status Bar: Ready | Frame 120/300 | 30 fps             │
└─────────────────────────────────────────────────────────┘
```

**MainWindow Class:**
```python
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

        self.setWindowTitle("Golf Swing Analyzer - F1 Studio")
        self.setMinimumSize(1280, 720)

        # Apply F1 theme
        self.setStyleSheet(F1Theme.get_main_stylesheet())

        # Create UI components
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()
        self._create_status_bar()

        # State
        self.current_video = None
        self.current_frame = 0
        self.is_playing = False

    def _create_menu_bar(self):
        """Create menu bar with File, View, Analysis, Help."""

    def _create_tool_bar(self):
        """Create tool bar with common actions."""

    def _create_central_widget(self):
        """Create central layout with video player and panels."""

    def _create_status_bar(self):
        """Create status bar with info display."""

    def open_video(self, filepath: str):
        """Load video file and initialize analysis."""

    def play_pause(self):
        """Toggle video playback."""

    def stop(self):
        """Stop playback and reset to start."""

    def seek_frame(self, frame_number: int):
        """Jump to specific frame."""

    def export_video(self):
        """Export annotated video with overlays."""
```

### 3. Video Player Widget (video_player.py)

**VideoPlayerWidget Class:**
```python
class VideoPlayerWidget(QWidget):
    """Video player with playback controls and display.

    Displays video frames with analysis overlays and provides
    professional playback controls.

    Signals:
        frame_changed(int): Emitted when frame changes
        playback_started(): Emitted when playback starts
        playback_stopped(): Emitted when playback stops
    """

    frame_changed = pyqtSignal(int)
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize video player widget."""
        super().__init__(parent)

        # Components
        self.video_display = VideoDisplayLabel()  # QLabel for frame
        self.playback_controls = PlaybackControlsWidget()

        # Playback state
        self.video_loader = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.playback_timer = QTimer()

        self._setup_ui()
        self._connect_signals()

    def load_video(self, filepath: str):
        """Load video file."""

    def play(self):
        """Start playback."""

    def pause(self):
        """Pause playback."""

    def stop(self):
        """Stop and reset."""

    def next_frame(self):
        """Advance one frame."""

    def previous_frame(self):
        """Go back one frame."""

    def seek(self, frame_number: int):
        """Seek to frame."""

    def set_playback_speed(self, speed: float):
        """Set playback speed (0.25x, 0.5x, 1x, 2x)."""

    def set_overlays(self, overlays: dict):
        """Set which overlays to display."""
```

**PlaybackControlsWidget:**
```python
class PlaybackControlsWidget(QWidget):
    """Professional playback controls with F1 styling.

    Provides play/pause, stop, frame navigation, and speed control.
    """

    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    next_frame_clicked = pyqtSignal()
    prev_frame_clicked = pyqtSignal()
    speed_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        """Initialize playback controls."""

        # Buttons
        self.play_pause_btn = QPushButton("▶")  # Play/Pause toggle
        self.stop_btn = QPushButton("■")
        self.prev_frame_btn = QPushButton("◀◀")
        self.next_frame_btn = QPushButton("▶▶")

        # Speed selector
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x"])
        self.speed_combo.setCurrentText("1x")
```

### 4. Analysis Panel (analysis_panel.py)

**AnalysisPanelWidget Class:**
```python
class AnalysisPanelWidget(QWidget):
    """Analysis control panel with metrics and overlay toggles.

    Displays real-time swing metrics and allows toggling
    analysis overlays.
    """

    overlay_toggled = pyqtSignal(str, bool)  # (overlay_name, enabled)

    def __init__(self, parent=None):
        """Initialize analysis panel."""
        super().__init__(parent)

        # Metric displays
        self.attack_angle_display = MetricDisplay("Attack Angle", "°")
        self.swing_path_display = MetricDisplay("Swing Path", "°")
        self.plane_angle_display = MetricDisplay("Plane Angle", "°")
        self.club_speed_display = MetricDisplay("Club Speed", "mph")

        # Overlay toggles
        self.club_track_toggle = ToggleButton("Club Track")
        self.swing_plane_toggle = ToggleButton("Swing Plane")
        self.skeleton_toggle = ToggleButton("Skeleton")
        self.angles_toggle = ToggleButton("Angles")

        self._setup_ui()

    def update_metrics(self, metrics: dict):
        """Update displayed metrics."""

    def get_enabled_overlays(self) -> dict:
        """Get which overlays are enabled."""
```

**MetricDisplay Widget:**
```python
class MetricDisplay(QWidget):
    """Large numeric display for a single metric.

    F1-style metric display with label, value, and unit.
    """

    def __init__(self, label: str, unit: str = "", parent=None):
        """Initialize metric display.

        Args:
            label: Metric name (e.g., "Attack Angle")
            unit: Unit symbol (e.g., "°", "mph")
        """
        super().__init__(parent)

        self.label = label
        self.unit = unit
        self.value = 0.0

        # Styling
        self.setStyleSheet("""
            QWidget {
                background: rgba(26, 26, 26, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 16px;
            }
        """)

    def set_value(self, value: float):
        """Update displayed value."""

    def paintEvent(self, event):
        """Custom paint for F1 styling."""
```

### 5. Timeline Widget (timeline.py)

**TimelineWidget Class:**
```python
class TimelineWidget(QWidget):
    """Timeline scrubber with key position markers.

    Provides frame-by-frame navigation with visual markers
    for P1, P4, P7 positions and analysis events.
    """

    frame_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize timeline widget."""
        super().__init__(parent)

        self.total_frames = 0
        self.current_frame = 0
        self.key_positions = {}  # {position_name: frame_number}

        # Scrubber
        self.scrubber = QSlider(Qt.Horizontal)
        self.scrubber.setMinimum(0)

        # Frame display
        self.frame_label = QLabel("0 / 0")

        self._setup_ui()

    def set_total_frames(self, total: int):
        """Set total number of frames."""

    def set_current_frame(self, frame: int):
        """Set current frame position."""

    def add_key_position(self, name: str, frame: int, color: str):
        """Add key position marker (P1, P4, P7, Impact, etc.)."""

    def clear_key_positions(self):
        """Clear all key position markers."""

    def paintEvent(self, event):
        """Custom paint for timeline with markers."""
```

### 6. Glass Panel Widget (widgets/glass_panel.py)

**GlassPanel Class:**
```python
class GlassPanel(QWidget):
    """Frosted glass panel with blur effect.

    Container widget with F1 glass morphism styling.
    Uses semi-transparent background with blur for
    premium aesthetic.
    """

    def __init__(self, parent=None, blur_radius: int = 10):
        """Initialize glass panel.

        Args:
            blur_radius: Blur intensity (pixels)
        """
        super().__init__(parent)

        self.blur_radius = blur_radius

        # Enable transparency
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Apply glass styling
        self.setStyleSheet(F1Theme.get_glass_panel_stylesheet())

    def paintEvent(self, event):
        """Paint glass effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw semi-transparent background
        # Draw subtle border
        # Add highlight edge for depth
```

## Integration Points

### With Existing Modules

**Video Loading:**
```python
from src.video import VideoLoader, FrameExtractor

def open_video(self, filepath: str):
    self.video_loader = VideoLoader(filepath)
    metadata = self.video_loader.get_metadata()

    self.video_player.load_video(filepath)
    self.timeline.set_total_frames(metadata.frame_count)
```

**Analysis Integration:**
```python
from src.detection import ClubDetector, ClubTracker
from src.plane import SwingPlaneAnalyzer
from src.pose import PoseDetector
from src.visualization import VisualizationEngine

def analyze_current_frame(self):
    frame = self.video_loader.get_frame_at(self.current_frame)

    # Detect club
    club_detection = self.club_detector.detect(frame)

    # Detect pose
    pose_result = self.pose_detector.detect(frame)

    # Update metrics
    metrics = self._calculate_metrics(club_detection, pose_result)
    self.analysis_panel.update_metrics(metrics)

    # Render with overlays
    overlays = self.analysis_panel.get_enabled_overlays()
    annotated = self.viz_engine.render(frame, club_detection, pose_result)

    self.video_player.display_frame(annotated)
```

**Export:**
```python
from src.export import VideoExporter

def export_video(self):
    dialog = QFileDialog()
    output_path = dialog.getSaveFileName(filter="Video (*.avi *.mp4)")

    with VideoExporter(output_path, self.fps, self.resolution) as exporter:
        for frame_num in range(self.total_frames):
            frame = self._get_annotated_frame(frame_num)
            exporter.write_frame(frame)
```

## User Interactions

### Primary Workflows

1. **Load and Analyze Video:**
   - File → Open Video
   - Video loads in player
   - Auto-detect key positions
   - Enable desired overlays
   - Review swing metrics

2. **Frame Navigation:**
   - Click timeline to jump to frame
   - Use ◀◀ / ▶▶ buttons for step
   - Play/pause for review
   - Markers show P1, P4, P7

3. **Analysis Configuration:**
   - Toggle overlays on/off
   - Metrics update in real-time
   - Adjust playback speed

4. **Export Results:**
   - Analysis → Export Video
   - Choose codec and quality
   - Progress bar shows status

## Testing Strategy

### Manual Testing
- Visual inspection of F1 aesthetic
- Interaction responsiveness
- Glass morphism rendering
- Animation smoothness

### Automated Tests
- Widget initialization
- Signal/slot connections
- State management
- Layout calculations

### Integration Tests
- Video playback
- Analysis updates
- Export functionality

## Success Criteria

1. **Visual Quality**
   - F1 aesthetic matches design mockups
   - Glass morphism renders correctly
   - Smooth 60fps animations
   - No visual glitches

2. **Functionality**
   - Video loads and plays correctly
   - Analysis overlays work
   - Timeline navigation is precise
   - Export produces valid videos

3. **Performance**
   - <16ms frame render time (60fps)
   - Responsive UI interactions
   - No blocking operations

4. **Usability**
   - Intuitive controls
   - Clear metric displays
   - Obvious interaction points

## Future Enhancements

1. **Advanced Features**
   - Side-by-side comparison view
   - Slow motion with interpolation
   - Custom overlay configurations
   - Annotation tools

2. **Workflow Improvements**
   - Project save/load
   - Batch processing
   - Preset configurations
   - Keyboard shortcuts

3. **Visual Enhancements**
   - Animated transitions
   - Particle effects
   - Dynamic backgrounds
   - Customizable themes
