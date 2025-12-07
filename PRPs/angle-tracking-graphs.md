# PRP: Angle Tracking Graphs

## Overview
Add interactive graphs that visualize how angles change throughout the golf swing. This provides powerful analytical insight into swing mechanics, helping identify critical positions and deviations.

## Goals
- Plot angle values over time (frame-by-frame)
- Support multiple angle types (spine, club shaft, joints, swing plane)
- Interactive graphs with zoom, pan, hover tooltips
- Compare angles between two swings (overlay graphs)
- Highlight key positions (address, top of backswing, impact, follow-through)
- Export graphs as images (PNG, SVG)
- Real-time graph updates as video plays

## Use Cases

### 1. Spine Angle Analysis
User wants to see if spine angle stays consistent:
- Run full video analysis
- Open angle graph panel
- Select "Spine Angle" from dropdown
- See graph showing spine angle from P1 → P7
- Identify frames where spine lifts or dips
- Click on graph to jump to that frame in video

### 2. Club Shaft Angle Progression
Coach analyzes club shaft angles through swing:
- Graph shows shaft angle relative to ground
- Identify shallow vs steep positions
- Compare backswing plane to downswing plane
- See exact angle at impact

### 3. Before/After Comparison
Student compares swing before and after lesson:
- Load two videos in comparison mode
- Generate graphs for both swings
- Overlay spine angle curves (red vs green)
- See exactly how swing changed

### 4. X-Factor Analysis
Analyze shoulder vs hip rotation differential:
- Plot shoulder rotation angle
- Plot hip rotation angle
- Graph shows X-Factor (difference) over time
- Identify maximum X-Factor at top of backswing

## Architecture

### Components

```
src/analysis/
├── angle_tracker.py (new)
│   └── AngleTracker: Collects angle data over frames
│
src/gui/
├── angle_graph_widget.py (new)
│   ├── AngleGraphWidget: Main graph display
│   ├── AngleSelector: Dropdown for angle selection
│   └── GraphToolbar: Export, zoom, reset controls
│
Integration:
├── MainWindow: Add graph panel
└── ComparisonView: Add dual graph display
```

### AngleTracker
New class in `src/analysis/angle_tracker.py`:

```python
class AngleTracker:
    """Tracks angles across video frames.

    Collects angle measurements from analysis results
    and provides data for graphing.
    """

    def __init__(self):
        self.angle_data = {}  # angle_name -> {frame_num: value}

    def add_frame_data(self, frame_num: int, angles: dict):
        """Add angle measurements for a frame."""

    def get_angle_series(self, angle_name: str) -> tuple:
        """Get (frames, values) for graphing."""

    def get_available_angles(self) -> list:
        """Get list of tracked angle names."""
```

**Supported Angles:**
- **Body Angles:**
  - Spine angle (torso tilt)
  - Shoulder rotation
  - Hip rotation
  - X-Factor (shoulder - hip rotation)
  - Left/right elbow angle
  - Left/right knee angle
  - Left/right wrist angle

- **Club Angles:**
  - Club shaft angle (relative to ground)
  - Club shaft angle (relative to target line)
  - Club face angle (if detected)
  - Swing plane angle

### AngleGraphWidget
New widget in `src/gui/angle_graph_widget.py`:

Uses **matplotlib** for plotting (already available with cv2):

```python
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class AngleGraphWidget(QWidget):
    """Interactive angle graph display."""

    # Signals
    frame_clicked = pyqtSignal(int)  # User clicked on graph

    def __init__(self):
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)

    def plot_angle(self, frames, values, angle_name,
                   key_positions=None, color='#00FF00'):
        """Plot angle data."""

    def plot_comparison(self, data1, data2, angle_name,
                       labels=('Swing 1', 'Swing 2')):
        """Plot two angle series for comparison."""

    def add_key_position_markers(self, positions):
        """Add vertical lines for P1, P4, P7, etc."""

    def export_image(self, filepath):
        """Export graph as PNG/SVG."""
```

**Graph Features:**
- Line plot with smooth curves
- Grid lines for readability
- Axis labels with units (degrees)
- Legend showing angle name
- Vertical markers for key positions
- Interactive hover tooltips showing frame and value
- Click to jump to frame in video

## UI/UX Design

### Main Window with Graph Panel

```
┌─────────────────────────────────────────────────────────────┐
│ File  View  Analysis  Draw  Help                            │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ [Open] [Export] [Analyze]                                   │
└─────────────────────────────────────────────────────────────┘
┌──────────────────────────┬──────────────────────────────────┐
│                          │  ANALYSIS PANEL                  │
│                          │  ┌────────────────────────────┐  │
│      Video Display       │  │ Overlays                   │  │
│                          │  │ ☑ Club Track               │  │
│      (Main View)         │  │ ☑ Skeleton                 │  │
│                          │  │ ☑ Angles                   │  │
│                          │  └────────────────────────────┘  │
│                          │  ┌────────────────────────────┐  │
│                          │  │ Metrics                    │  │
│                          │  │ Attack Angle: -3.2°        │  │
│                          │  │ Swing Path: 2.1° in-to-out │  │
│                          │  └────────────────────────────┘  │
├──────────────────────────┴──────────────────────────────────┤
│ ☑ Show Angle Graphs                                         │
├─────────────────────────────────────────────────────────────┤
│ ANGLE GRAPHS                                                │
│ Angle: [Spine Angle ▼]  [📷 Export] [🔍 Zoom] [↻ Reset]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 40°┤         ╱╲                                         │ │
│ │    │        ╱  ╲                                        │ │
│ │ 30°┤       ╱    ╲___                                    │ │
│ │    │      ╱         ╲                                   │ │
│ │ 20°┤     ╱           ╲___                               │ │
│ │    │    ╱                ╲                              │ │
│ │ 10°┤___╱                  ╲____                         │ │
│ │    ├────┬────┬────┬────┬────┬────┬───                  │ │
│ │    P1   P2   P3   P4   P5   P6   P7                    │ │
│ │         (Key Positions Marked)                          │ │
│ └─────────────────────────────────────────────────────────┘ │
│ Frame 45 / 120  |  Spine Angle: 28.5°                      │
└─────────────────────────────────────────────────────────────┘
│ Timeline: [==========●==============]  Frame 45 / 120       │
└─────────────────────────────────────────────────────────────┘
```

### Comparison Mode with Dual Graphs

```
┌─────────────────────────────────────────────────────────────┐
│ COMPARISON - ANGLE GRAPHS                                   │
│ Angle: [Spine Angle ▼]  [📷 Export]                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 40°┤         ╱╲        ╱╲                              │ │
│ │    │        ╱  ╲      ╱  ╲     Left (Red)              │ │
│ │ 30°┤       ╱    ╲    ╱    ╲    Right (Green)           │ │
│ │    │      ╱      ╲__╱      ╲                           │ │
│ │ 20°┤     ╱                  ╲                          │ │
│ │    │    ╱                    ╲                         │ │
│ │ 10°┤___╱                      ╲____                    │ │
│ │    ├────┬────┬────┬────┬────┬────┬───                 │ │
│ │    0    20   40   60   80   100  120 (frames)         │ │
│ └─────────────────────────────────────────────────────────┘ │
│ Difference at impact (frame 65): 3.2° (Left > Right)       │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: AngleTracker Core
1. Create `AngleTracker` class
2. Methods to add frame data
3. Methods to retrieve angle series
4. Extract angles from existing analysis results

### Phase 2: Basic Graph Widget
1. Create `AngleGraphWidget` with matplotlib
2. Basic line plot functionality
3. Axis labels and grid
4. Frame-to-value display

### Phase 3: Interactive Features
1. Click on graph to jump to frame
2. Hover tooltips showing value
3. Key position markers (vertical lines)
4. Current frame indicator (moving vertical line)

### Phase 4: Angle Selector & Controls
1. Dropdown for angle selection
2. Export button (save as PNG/SVG)
3. Zoom/pan controls
4. Reset view button

### Phase 5: Integration
1. Add graph panel to MainWindow
2. Toggle show/hide graphs
3. Auto-update graph as video plays
4. Connect click events to seek video

### Phase 6: Comparison Mode
1. Dual angle plotting
2. Color coding (red/green)
3. Difference calculation
4. Legend with labels

## Technical Details

### Matplotlib Integration with PyQt5

```python
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, NavigationToolbar2QT
)
from matplotlib.figure import Figure

class AngleGraphWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 4), facecolor='#1A1A1A')
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Create axes
        self.axes = self.figure.add_subplot(111)
        self.axes.set_facecolor('#0A0A0A')

        # Style for F1 theme
        self.axes.tick_params(colors='#C0C0C0')
        self.axes.spines['bottom'].set_color('#C0C0C0')
        self.axes.spines['left'].set_color('#C0C0C0')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
```

### Extracting Angles from Analysis Results

```python
def extract_angles_from_pose(landmarks):
    """Extract body angles from pose landmarks."""
    from ..analysis.angles import JointAngleCalculator

    calculator = JointAngleCalculator()

    angles = {}

    # Spine angle (torso tilt)
    if all(p in landmarks for p in ['left_shoulder', 'left_hip', 'left_knee']):
        angles['spine_angle'] = calculator.calculate_torso_angle(
            landmarks['left_shoulder'],
            landmarks['left_hip'],
            landmarks['left_knee']
        )

    # Shoulder rotation (relative to hips)
    # ... more angle calculations

    return angles
```

### Real-Time Graph Updates

```python
def _on_frame_changed(self, frame_number):
    """Update graph indicator when video frame changes."""
    if self.show_graphs and self.angle_graph:
        # Update vertical line showing current frame
        self.angle_graph.update_current_frame_marker(frame_number)
```

### Click to Seek

```python
def _on_graph_clicked(self, event):
    """Handle click on graph - seek video to that frame."""
    if event.xdata is not None:
        frame_number = int(event.xdata)
        self.video_player.seek(frame_number)
```

## Data Structure

### Angle Data Format

```python
angle_tracker.angle_data = {
    'spine_angle': {
        0: 15.2,
        1: 15.5,
        2: 15.8,
        # ... frame_num: angle_value
        120: 32.1
    },
    'club_shaft_angle': {
        0: 45.0,
        1: 46.2,
        # ...
    },
    # ... more angles
}

key_positions = {
    'address': 0,
    'top_of_backswing': 45,
    'impact': 65,
    'follow_through': 95
}
```

## API Examples

### Basic Usage

```python
# In MainWindow after full video analysis
from ..analysis import AngleTracker
from ..gui import AngleGraphWidget

# Create tracker
self.angle_tracker = AngleTracker()

# Populate with data from analysis results
for frame_num in range(total_frames):
    if frame_num in self.pose_results:
        landmarks = self.pose_results[frame_num]
        angles = extract_angles_from_pose(landmarks)
        self.angle_tracker.add_frame_data(frame_num, angles)

    if frame_num in self.club_results:
        club_data = self.club_results[frame_num]
        club_angles = extract_club_angles(club_data)
        self.angle_tracker.add_frame_data(frame_num, club_angles)

# Create graph widget
self.angle_graph = AngleGraphWidget()
self.angle_graph.frame_clicked.connect(self.video_player.seek)

# Plot spine angle
frames, values = self.angle_tracker.get_angle_series('spine_angle')
self.angle_graph.plot_angle(
    frames, values,
    angle_name='Spine Angle',
    key_positions=self.key_positions,
    color='#00FF00'
)
```

### Comparison Mode

```python
# In ComparisonView
left_frames, left_values = left_tracker.get_angle_series('spine_angle')
right_frames, right_values = right_tracker.get_angle_series('spine_angle')

self.angle_graph.plot_comparison(
    (left_frames, left_values),
    (right_frames, right_values),
    angle_name='Spine Angle',
    labels=('Before', 'After'),
    colors=('#FF6B6B', '#51CF66')
)
```

## File Structure

```
src/analysis/
├── __init__.py
├── angles/              # Existing
│   ├── core.py
│   ├── joint_angles.py
│   └── club_angles.py
└── angle_tracker.py     # NEW: Angle data collection

src/gui/
├── __init__.py
├── main_window.py       # Modified: Add graph panel
├── angle_graph_widget.py  # NEW: Graph display
└── widgets.py           # Existing
```

## Testing Plan

1. **Unit Tests** (`tests/test_angle_tracker.py`)
   - Test data collection
   - Test series retrieval
   - Test angle extraction functions

2. **Integration Tests**
   - Test graph plotting
   - Test click events
   - Test real-time updates

3. **Manual Testing**
   - Test with real video analysis
   - Test graph export
   - Test comparison mode graphs
   - Test performance with long videos

## Success Criteria

✅ Graphs display angle progression smoothly
✅ At least 5 angle types supported (spine, club shaft, elbows, knees, shoulders)
✅ Interactive features work (click to seek, hover tooltips)
✅ Key positions marked clearly on graph
✅ Export to PNG/SVG works correctly
✅ Comparison mode shows both swings overlaid
✅ Real-time updates during playback
✅ F1 styling matches app aesthetic
✅ Performance: Graph updates at >30 fps

## Timeline Estimate

- **Phase 1** (AngleTracker): 1-2 hours
- **Phase 2** (Basic graph): 1-2 hours
- **Phase 3** (Interactive): 1-2 hours
- **Phase 4** (Controls): 1 hour
- **Phase 5** (Integration): 1-2 hours
- **Phase 6** (Comparison): 1 hour

**Total**: ~6-10 hours of development time

## Future Enhancements

- **Multi-Angle View**: Show 2-4 graphs simultaneously
- **Angle Velocity**: Graph rate of change (angular velocity)
- **Statistical Overlays**: Show mean, std dev bands
- **Video Sync**: Play video alongside graph with synchronized cursor
- **3D Angle Visualization**: Show angles in 3D space
- **Machine Learning**: Detect anomalies in angle patterns
