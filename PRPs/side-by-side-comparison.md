# PRP: Side-by-Side Comparison View

## Overview
Implement a split-screen comparison mode that allows users to view and analyze two golf swing videos simultaneously. This feature enables before/after comparisons, student vs professional comparisons, and multi-angle analysis.

## Goals
1. Display two videos side-by-side with synchronized playback
2. Independent overlay controls for each video
3. Synchronized timeline with frame-accurate scrubbing
4. Swap left/right videos easily
5. Link/unlink playback synchronization
6. Maintain F1 design aesthetic

## Non-Goals
- More than 2 videos simultaneously (keep it focused)
- Video editing/trimming (use external tools)
- Automatic swing matching/alignment (future enhancement)
- **Video overlay/blending** (noted for future feature - alpha blend two videos on top of each other)

## Use Cases

### Use Case 1: Before/After Comparison
**Actor**: Golf student
**Scenario**: Student wants to compare their swing from last month to current swing
**Flow**:
1. User opens comparison view
2. Loads "before" video on left
3. Loads "current" video on right
4. Plays both synchronized to see improvement
5. Toggles overlays independently (club track on left, skeleton on right)
6. Takes screenshot of key position comparison

### Use Case 2: Student vs Pro
**Actor**: Golf instructor
**Scenario**: Instructor wants to show student the difference between their swing and a pro's
**Flow**:
1. Opens comparison view
2. Loads student video on left
3. Loads pro video on right
4. Draws reference lines on both videos
5. Unlocks sync to find matching positions (address position)
6. Re-locks sync at that point
7. Scrubs through to compare movements

### Use Case 3: Different Club Analysis
**Actor**: Golf student
**Scenario**: Student wants to compare their driver swing vs iron swing
**Flow**:
1. Opens comparison view
2. Loads driver video on left
3. Loads 7-iron video on right
4. Enables swing plane overlay on both
5. Compares plane angles at impact
6. Exports side-by-side screenshot with measurements

## Architecture

### Module Structure
```
src/comparison/
├── __init__.py
├── comparison_view.py       # Main comparison widget
├── video_side.py            # Single side of comparison (video + controls)
├── sync_controller.py       # Synchronization logic
└── comparison_toolbar.py    # Comparison-specific controls
```

### Component Design

#### 1. ComparisonView Widget (`comparison_view.py`)

**Main container for side-by-side view:**

```python
class ComparisonView(QWidget):
    """Side-by-side video comparison widget.

    Displays two videos side by side with synchronized playback
    and independent overlay controls.

    Signals:
        videos_loaded(bool, bool): Emitted when videos load (left, right)
        sync_changed(bool): Emitted when sync state changes
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Video sides
        self.left_side = VideoSide("Left")
        self.right_side = VideoSide("Right")

        # Synchronization controller
        self.sync_controller = SyncController()

        # Comparison toolbar
        self.comparison_toolbar = ComparisonToolbar()

        # Shared timeline for synchronized playback
        self.shared_timeline = TimelineWidget()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up comparison layout."""
        main_layout = QVBoxLayout()

        # Comparison toolbar at top
        main_layout.addWidget(self.comparison_toolbar)

        # Horizontal splitter for two videos
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_side)
        splitter.addWidget(self.right_side)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, stretch=1)

        # Shared timeline at bottom
        main_layout.addWidget(self.shared_timeline)

        self.setLayout(main_layout)

    def load_left_video(self, video_path: str):
        """Load video on left side."""

    def load_right_video(self, video_path: str):
        """Load video on right side."""

    def swap_videos(self):
        """Swap left and right videos."""

    def set_sync_enabled(self, enabled: bool):
        """Enable/disable playback synchronization."""

    def play(self):
        """Play both videos (if synced) or active video."""

    def pause(self):
        """Pause both videos."""

    def seek_to_frame(self, frame_number: int):
        """Seek both videos to frame (if synced)."""
```

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  Comparison Toolbar                                        │
│  [Load Left] [Load Right] [Swap] [Link🔗] [Screenshot]    │
├──────────────────────────┬─────────────────────────────────┤
│                          │                                 │
│   Left Video             │   Right Video                   │
│   ┌──────────────────┐   │   ┌──────────────────┐         │
│   │                  │   │   │                  │         │
│   │   Video Frame    │   │   │   Video Frame    │         │
│   │                  │   │   │                  │         │
│   └──────────────────┘   │   └──────────────────┘         │
│   [▶][⏸][◀◀][▶▶]        │   [▶][⏸][◀◀][▶▶]               │
│   Analysis Panel         │   Analysis Panel                │
│   [☑ Club Track]         │   [☑ Skeleton]                  │
│   [☐ Swing Plane]        │   [☑ Angles]                    │
│                          │                                 │
├──────────────────────────┴─────────────────────────────────┤
│  Shared Timeline (if synced)                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
└────────────────────────────────────────────────────────────┘
```

#### 2. VideoSide Widget (`video_side.py`)

**Single side of comparison:**

```python
class VideoSide(QWidget):
    """One side of the comparison view.

    Contains video player, controls, and overlay toggles
    for a single video.

    Signals:
        frame_changed(int): Emitted when frame changes
        video_loaded(str): Emitted when video loads
        play_requested(): Emitted when play is clicked
        pause_requested(): Emitted when pause is clicked
    """

    def __init__(self, side_name: str, parent=None):
        """Initialize video side.

        Args:
            side_name: "Left" or "Right"
        """
        super().__init__(parent)

        self.side_name = side_name
        self.video_loader = None
        self.frame_extractor = None
        self.current_frame = 0
        self.total_frames = 0

        # Analysis components (independent per side)
        self.viz_engine = None
        self.drawing_manager = None
        self.drawing_renderer = None

        # UI components
        self.video_display = VideoDisplayLabel()
        self.controls = PlaybackControlsWidget()
        self.overlay_panel = CompactOverlayPanel()

        self._setup_ui()

    def load_video(self, video_path: str):
        """Load a video on this side."""

    def get_frame(self, frame_number: int):
        """Get frame with overlays applied."""

    def play(self):
        """Start playback on this side."""

    def pause(self):
        """Pause playback on this side."""

    def seek(self, frame_number: int):
        """Seek to frame."""

    def next_frame(self):
        """Advance one frame."""

    def previous_frame(self):
        """Go back one frame."""
```

#### 3. SyncController (`sync_controller.py`)

**Manages synchronization between two videos:**

```python
class SyncController:
    """Controls synchronization between two videos.

    Handles:
    - Linked/unlinked playback
    - Frame offset management
    - Synchronized seeking
    - Playback speed matching
    """

    def __init__(self):
        self.sync_enabled = True
        self.frame_offset = 0  # Offset between videos
        self.playback_speed = 1.0

    def set_sync_enabled(self, enabled: bool):
        """Enable/disable synchronization."""
        self.sync_enabled = enabled

    def set_frame_offset(self, offset: int):
        """Set frame offset between videos.

        Args:
            offset: Number of frames to offset (can be negative)
        """
        self.frame_offset = offset

    def get_synced_frame(self, primary_frame: int) -> int:
        """Get corresponding frame for secondary video.

        Args:
            primary_frame: Frame number on primary video

        Returns:
            Corresponding frame on secondary video
        """
        if not self.sync_enabled:
            return 0

        return max(0, primary_frame + self.frame_offset)

    def calibrate_sync(self, left_frame: int, right_frame: int):
        """Calibrate sync by marking matching frames.

        Args:
            left_frame: Frame on left video
            right_frame: Frame on right video
        """
        self.frame_offset = right_frame - left_frame
```

#### 4. ComparisonToolbar (`comparison_toolbar.py`)

**Toolbar for comparison-specific controls:**

```python
class ComparisonToolbar(QWidget):
    """Toolbar for comparison view controls.

    Signals:
        load_left_requested(): Load video on left
        load_right_requested(): Load video on right
        swap_requested(): Swap left and right
        sync_toggled(bool): Sync enabled/disabled
        screenshot_requested(): Take comparison screenshot
        calibrate_requested(): Calibrate sync points
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Buttons
        self.load_left_btn = QPushButton("Load Left Video")
        self.load_right_btn = QPushButton("Load Right Video")
        self.swap_btn = QPushButton("⇄ Swap")
        self.sync_toggle = QCheckBox("Link Playback 🔗")
        self.screenshot_btn = QPushButton("📷 Screenshot")
        self.calibrate_btn = QPushButton("⚙ Calibrate Sync")

        self._setup_ui()

    def _setup_ui(self):
        """Set up toolbar UI with F1 styling."""
        layout = QHBoxLayout()

        layout.addWidget(self.load_left_btn)
        layout.addWidget(self.load_right_btn)
        layout.addSeparator()
        layout.addWidget(self.swap_btn)
        layout.addWidget(self.sync_toggle)
        layout.addWidget(self.calibrate_btn)
        layout.addStretch()
        layout.addWidget(self.screenshot_btn)

        self.setLayout(layout)

        # Apply F1 styling
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #E8E8E8;
            }
            QPushButton {
                background-color: #2A2A2A;
                color: #E8E8E8;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
                border: 1px solid #C0C0C0;
            }
        """)
```

## Integration with MainWindow

### Add Comparison Mode Toggle

**In MainWindow menu:**
```python
# View menu
view_menu = menubar.addMenu("&View")

# Toggle Comparison Mode
comparison_action = QAction("&Comparison Mode", self)
comparison_action.setCheckable(True)
comparison_action.setShortcut(QKeySequence("Ctrl+M"))
comparison_action.setStatusTip("Toggle comparison view")
comparison_action.triggered.connect(self._toggle_comparison_mode)
view_menu.addAction(comparison_action)
```

### Switch Between Single and Comparison Views

**MainWindow state management:**
```python
def __init__(self):
    # ...existing code...

    # Views
    self.single_view = None  # Current single video player
    self.comparison_view = None  # Comparison view
    self.current_view_mode = "single"  # "single" or "comparison"

def _toggle_comparison_mode(self, enabled: bool):
    """Toggle between single and comparison view."""
    if enabled:
        # Switch to comparison mode
        if not self.comparison_view:
            self.comparison_view = ComparisonView()

        # Replace central widget
        self.setCentralWidget(self.comparison_view)
        self.current_view_mode = "comparison"

    else:
        # Switch back to single mode
        # Restore original layout
        self._create_central_widget()  # Recreate single view
        self.current_view_mode = "single"
```

## Key Features

### 1. Synchronized Playback
- When linked (🔗 enabled):
  - Both videos play at same time
  - Timeline controls both videos
  - Scrubbing moves both videos
  - Frame advance/back affects both

- When unlinked (🔗 disabled):
  - Each video plays independently
  - Each has own playback controls
  - Timeline shows active video
  - Can pause one while other plays

### 2. Frame Offset Calibration
**Workflow:**
1. User clicks "Calibrate Sync"
2. Scrubs left video to key position (e.g., impact)
3. Scrubs right video to matching position
4. Clicks "Set Sync Point"
5. System calculates offset
6. Re-enables link with offset applied

### 3. Independent Overlays
- Each side has own analysis panel
- Can show different overlays (left=club track, right=skeleton)
- Independent drawing tools per side
- Each side stores own drawings

### 4. Swap Functionality
- Swap button (⇄) exchanges left and right videos
- Swaps video sources
- Swaps all analysis data
- Swaps drawings
- Maintains sync offset

### 5. Comparison Screenshot
- Captures both sides in one image
- Shows current frame number for each
- Includes overlays and drawings
- Saves as single wide image (2x width)

## UI/UX Considerations

### Keyboard Shortcuts
- `Ctrl+M`: Toggle comparison mode
- `Ctrl+L`: Load left video
- `Ctrl+R`: Load right video
- `Ctrl+W`: Swap videos
- `Ctrl+K`: Toggle link/unlink
- `Space`: Play/pause (both if linked)
- `←/→`: Frame back/forward (both if linked)

### Visual Indicators
- **Linked**: 🔗 icon green, timeline shared
- **Unlinked**: 🔗 icon grey, each side has frame counter
- **Active side**: Border highlight when unlinked
- **Sync offset**: Display "Right +5 frames" when offset ≠ 0

### F1 Aesthetic
- Vertical separator between sides (thin silver line)
- Each side has glass panel for controls
- Shared timeline uses same F1 theme
- Comparison toolbar matches main toolbar style

## Performance Considerations

### Memory Management
- Load both videos simultaneously
- Use same frame extraction caching
- Share visualization engines where possible
- Lazy-load analysis results

### Playback Performance
- Target 30fps for both videos
- Use separate threads for frame extraction
- Cache recent frames for smooth scrubbing
- Reduce quality if performance suffers

## Future Enhancements (Not in Scope)

### Video Overlay Mode
**Description**: Blend two videos on top of each other with alpha transparency
**Use case**: See both swings overlaid to spot differences
**Implementation notes**:
```python
# Future feature - alpha blending
overlay_frame = cv2.addWeighted(
    left_frame, alpha=0.5,
    right_frame, alpha=0.5,
    gamma=0
)
```
**Priority**: High for future (very valuable for instruction)

### Automatic Sync Detection
- Auto-detect matching key positions
- Use pose detection to align address/impact
- ML-based swing phase matching

### Difference Heatmap
- Highlight areas where swings differ most
- Color-code differences

### Multi-angle Sync
- Support for 3+ camera angles
- Grid layout for multi-view

## Testing Strategy

### Manual Testing
1. Load two videos of different lengths
2. Test sync with offset
3. Test independent playback
4. Test swap functionality
5. Verify screenshot captures both sides
6. Test with different video formats
7. Test drawing tools on each side independently

### Edge Cases
- Videos of very different lengths (30 frames vs 300 frames)
- Videos of different resolutions
- Videos of different frame rates
- Loading same video on both sides
- Swapping while playing
- Sync calibration at end of shorter video

## File Summary

### New Files
- `src/comparison/__init__.py`
- `src/comparison/comparison_view.py` (~400 lines)
- `src/comparison/video_side.py` (~300 lines)
- `src/comparison/sync_controller.py` (~150 lines)
- `src/comparison/comparison_toolbar.py` (~200 lines)

### Modified Files
- `src/gui/main_window.py` (+100 lines for comparison toggle)
- `TASK.md` (update with completed feature)

**Total New Code:** ~1,150 lines

## Success Criteria

✓ Users can load two videos side-by-side
✓ Synchronized playback works smoothly
✓ Can unlink and control videos independently
✓ Swap functionality exchanges videos correctly
✓ Independent overlays work on each side
✓ Comparison screenshot captures both videos
✓ Sync calibration allows offset adjustment
✓ F1 aesthetic maintained
✓ Performance is smooth (30fps playback)

## Open Questions

1. **Frame rate mismatch**: How to handle videos with different FPS?
   - Decision: Use the video's native FPS, sync by frame number not time

2. **Resolution mismatch**: Different sized videos?
   - Decision: Scale to fit, maintain aspect ratio, add letterboxing if needed

3. **Analysis data**: Share or separate?
   - Decision: Separate - each side has independent analysis

4. **Drawings**: Share across sides?
   - Decision: Separate - each side has own drawings
