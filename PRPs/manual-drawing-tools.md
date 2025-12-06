# PRP: Manual Drawing Tools

## Overview
Implement interactive manual drawing tools that allow users to draw lines, angles, circles, and annotations directly on video frames. This complements automated analysis by giving users control to mark up frames when automatic detection fails or to add custom measurements.

## Goals
1. Allow users to manually draw lines, angles, and shapes on frames
2. Display measurements (angles in degrees, lengths in pixels/calibrated units)
3. Support undo/redo for drawing operations
4. Save/load drawings per frame or across video
5. Integrate seamlessly with existing video player
6. Maintain F1 design aesthetic

## Non-Goals
- Advanced image editing (filters, effects, etc.)
- Freehand drawing (just geometric shapes)
- Video editing (trimming, splicing)
- Automatic shape recognition

## Architecture

### Module Structure
```
src/drawing/
├── __init__.py
├── shapes.py          # Drawing shape data structures
├── tools.py           # Drawing tool implementations
├── canvas.py          # Interactive drawing canvas widget
├── toolbar.py         # Drawing toolbar widget
├── renderer.py        # Render drawings on frames
├── storage.py         # Save/load drawing data
└── measurements.py    # Calculate measurements from shapes
```

### Core Components

#### 1. Shape Data Structures (`shapes.py`)

**Base Shape Class:**
```python
@dataclass
class DrawingShape:
    """Base class for all drawing shapes."""
    id: str
    type: str
    color: Tuple[int, int, int]
    thickness: int
    frame_number: int
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize from dictionary."""
```

**Concrete Shape Types:**
```python
@dataclass
class Line(DrawingShape):
    """Straight line between two points."""
    start: Point2D
    end: Point2D
    label: str = ""

    def length(self) -> float:
        """Calculate line length in pixels."""

    def angle_from_horizontal(self) -> float:
        """Calculate angle from horizontal."""

@dataclass
class Angle(DrawingShape):
    """Angle defined by three points (vertex in middle)."""
    point1: Point2D
    vertex: Point2D
    point3: Point2D
    label: str = ""
    show_arc: bool = True
    arc_radius: int = 50

    def measure(self) -> float:
        """Calculate angle in degrees."""

@dataclass
class Circle(DrawingShape):
    """Circle defined by center and radius."""
    center: Point2D
    radius: float
    label: str = ""
    fill: bool = False

@dataclass
class Arc(DrawingShape):
    """Arc segment of a circle."""
    center: Point2D
    radius: float
    start_angle: float
    end_angle: float
    label: str = ""

@dataclass
class TextAnnotation(DrawingShape):
    """Text annotation at a point."""
    position: Point2D
    text: str
    font_scale: float = 1.0
    background: bool = True
```

#### 2. Drawing Tools (`tools.py`)

**Base Tool Class:**
```python
class DrawingTool:
    """Base class for drawing tools."""

    def __init__(self, color: Tuple[int, int, int], thickness: int):
        self.color = color
        self.thickness = thickness
        self.is_active = False
        self.current_shape = None

    def start_drawing(self, point: Point2D, frame_number: int):
        """Start drawing at point."""

    def update_drawing(self, point: Point2D):
        """Update drawing with new point."""

    def finish_drawing(self) -> Optional[DrawingShape]:
        """Finish drawing and return shape."""

    def cancel_drawing(self):
        """Cancel current drawing."""

    def get_preview_shape(self) -> Optional[DrawingShape]:
        """Get preview of current drawing."""
```

**Concrete Tool Implementations:**
```python
class LineTool(DrawingTool):
    """Tool for drawing straight lines."""

    def start_drawing(self, point: Point2D, frame_number: int):
        self.start_point = point
        self.is_active = True

    def update_drawing(self, point: Point2D):
        self.end_point = point

    def finish_drawing(self) -> Line:
        return Line(
            id=generate_id(),
            type="line",
            color=self.color,
            thickness=self.thickness,
            frame_number=self.frame_number,
            created_at=time.time(),
            start=self.start_point,
            end=self.end_point
        )

class AngleTool(DrawingTool):
    """Tool for measuring angles (3 clicks)."""
    # Click 1: first point
    # Click 2: vertex
    # Click 3: third point

class CircleTool(DrawingTool):
    """Tool for drawing circles (click center, drag radius)."""

class TextTool(DrawingTool):
    """Tool for adding text annotations."""
```

#### 3. Drawing Canvas (`canvas.py`)

**Interactive Canvas Widget:**
```python
class DrawingCanvas(QWidget):
    """Interactive canvas for drawing on video frames.

    Overlays on top of video player to capture mouse events
    for drawing operations.

    Signals:
        shape_added(DrawingShape): Emitted when shape is completed
        shape_selected(str): Emitted when shape is selected
        shape_deleted(str): Emitted when shape is deleted
    """

    shape_added = pyqtSignal(object)
    shape_selected = pyqtSignal(str)
    shape_deleted = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_tool = None
        self.shapes = {}  # shape_id -> DrawingShape
        self.selected_shape_id = None
        self.drawing_enabled = False

        # Make transparent except for drawings
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def set_tool(self, tool: DrawingTool):
        """Set active drawing tool."""

    def enable_drawing(self, enabled: bool):
        """Enable/disable drawing mode."""

    def add_shape(self, shape: DrawingShape):
        """Add a shape to the canvas."""

    def remove_shape(self, shape_id: str):
        """Remove a shape from the canvas."""

    def get_shapes_for_frame(self, frame_number: int) -> List[DrawingShape]:
        """Get all shapes for a specific frame."""

    def mousePressEvent(self, event):
        """Handle mouse press for drawing start or selection."""

    def mouseMoveEvent(self, event):
        """Handle mouse move for drawing preview."""

    def mouseReleaseEvent(self, event):
        """Handle mouse release for drawing completion."""

    def paintEvent(self, event):
        """Draw all shapes on the canvas."""
```

#### 4. Drawing Toolbar (`toolbar.py`)

**Tool Selection Toolbar:**
```python
class DrawingToolbar(QWidget):
    """Toolbar for selecting drawing tools and settings.

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
        super().__init__(parent)

        # Tool buttons
        self.tools = {
            'select': QToolButton(),    # Selection/move tool
            'line': QToolButton(),       # Line tool
            'angle': QToolButton(),      # Angle tool
            'circle': QToolButton(),     # Circle tool
            'text': QToolButton(),       # Text tool
        }

        # Color picker
        self.color_button = QPushButton()

        # Thickness slider
        self.thickness_slider = QSlider(Qt.Horizontal)

        # Undo/Redo/Clear buttons
        self.undo_button = QPushButton("↶ Undo")
        self.redo_button = QPushButton("↷ Redo")
        self.clear_button = QPushButton("Clear Frame")

        self._setup_ui()

    def _setup_ui(self):
        """Set up toolbar UI with F1 styling."""

    def set_active_tool(self, tool_name: str):
        """Set the active tool (updates button states)."""
```

#### 5. Drawing Renderer (`renderer.py`)

**Render Drawings on Frames:**
```python
class DrawingRenderer:
    """Renders drawing shapes onto video frames."""

    def __init__(self, style_config: Optional[StyleConfig] = None):
        self.style = style_config or StyleConfig()

    def render(
        self,
        frame: np.ndarray,
        shapes: List[DrawingShape],
        show_measurements: bool = True,
        selected_shape_id: Optional[str] = None
    ) -> np.ndarray:
        """Render all shapes onto frame.

        Args:
            frame: Input frame
            shapes: List of shapes to render
            show_measurements: Whether to show angle/length measurements
            selected_shape_id: ID of selected shape (highlighted)

        Returns:
            Frame with drawings rendered
        """
        output = frame.copy()

        for shape in shapes:
            # Highlight selected shape
            thickness = shape.thickness
            if shape.id == selected_shape_id:
                thickness *= 2

            if isinstance(shape, Line):
                self._render_line(output, shape, thickness, show_measurements)
            elif isinstance(shape, Angle):
                self._render_angle(output, shape, thickness, show_measurements)
            elif isinstance(shape, Circle):
                self._render_circle(output, shape, thickness)
            elif isinstance(shape, TextAnnotation):
                self._render_text(output, shape)

        return output

    def _render_line(self, frame, line: Line, thickness: int, show_label: bool):
        """Render a line with optional length label."""
        import cv2

        cv2.line(
            frame,
            (int(line.start.x), int(line.start.y)),
            (int(line.end.x), int(line.end.y)),
            line.color,
            thickness
        )

        if show_label:
            length = line.length()
            angle = line.angle_from_horizontal()

            # Draw label at midpoint
            mid_x = (line.start.x + line.end.x) / 2
            mid_y = (line.start.y + line.end.y) / 2

            label = f"{length:.0f}px @ {angle:.1f}°"
            if line.label:
                label = f"{line.label}: {label}"

            draw_text_with_background(
                frame,
                label,
                (int(mid_x), int(mid_y) - 10),
                scale=0.5,
                color=line.color
            )

    def _render_angle(self, frame, angle: Angle, thickness: int, show_measurement: bool):
        """Render an angle with arc and measurement."""
        import cv2

        # Draw lines to vertex
        cv2.line(frame,
                 (int(angle.point1.x), int(angle.point1.y)),
                 (int(angle.vertex.x), int(angle.vertex.y)),
                 angle.color, thickness)
        cv2.line(frame,
                 (int(angle.vertex.x), int(angle.vertex.y)),
                 (int(angle.point3.x), int(angle.point3.y)),
                 angle.color, thickness)

        if angle.show_arc:
            # Draw arc between the two lines
            # (Calculate start/end angles and draw arc)
            pass

        if show_measurement:
            degrees = angle.measure()
            label = f"{degrees:.1f}°"
            if angle.label:
                label = f"{angle.label}: {label}"

            draw_text_with_background(
                frame,
                label,
                (int(angle.vertex.x) + 20, int(angle.vertex.y) - 20),
                scale=0.6,
                color=angle.color
            )
```

#### 6. Storage System (`storage.py`)

**Save/Load Drawings:**
```python
class DrawingStorage:
    """Save and load drawing data."""

    @staticmethod
    def save_drawings(
        shapes: List[DrawingShape],
        filepath: str,
        video_path: Optional[str] = None
    ):
        """Save drawings to JSON file.

        Args:
            shapes: List of shapes to save
            filepath: Output JSON file path
            video_path: Optional associated video path
        """
        data = {
            'version': '1.0',
            'video_path': video_path,
            'created_at': time.time(),
            'shapes': [shape.to_dict() for shape in shapes]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_drawings(filepath: str) -> Tuple[List[DrawingShape], Optional[str]]:
        """Load drawings from JSON file.

        Returns:
            Tuple of (shapes list, video_path)
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        shapes = []
        for shape_data in data['shapes']:
            shape_type = shape_data['type']

            if shape_type == 'line':
                shape = Line.from_dict(shape_data)
            elif shape_type == 'angle':
                shape = Angle.from_dict(shape_data)
            # ... etc

            shapes.append(shape)

        return shapes, data.get('video_path')
```

#### 7. Drawing Manager (`manager.py`)

**Coordinate Drawing State:**
```python
class DrawingManager:
    """Manages drawing state, undo/redo, and frame-specific drawings."""

    def __init__(self):
        self.shapes_by_frame = {}  # frame_num -> List[DrawingShape]
        self.undo_stack = []
        self.redo_stack = []
        self.current_tool = None
        self.current_color = (255, 255, 0)  # Yellow default
        self.current_thickness = 2

    def add_shape(self, shape: DrawingShape):
        """Add a shape and push to undo stack."""
        frame_num = shape.frame_number

        if frame_num not in self.shapes_by_frame:
            self.shapes_by_frame[frame_num] = []

        self.shapes_by_frame[frame_num].append(shape)

        # Add to undo stack
        self.undo_stack.append(('add', shape))
        self.redo_stack.clear()

    def remove_shape(self, shape: DrawingShape):
        """Remove a shape and push to undo stack."""
        frame_num = shape.frame_number

        if frame_num in self.shapes_by_frame:
            self.shapes_by_frame[frame_num].remove(shape)

        self.undo_stack.append(('remove', shape))
        self.redo_stack.clear()

    def undo(self):
        """Undo last operation."""
        if not self.undo_stack:
            return

        action, shape = self.undo_stack.pop()

        if action == 'add':
            # Undo add = remove
            self.shapes_by_frame[shape.frame_number].remove(shape)
        elif action == 'remove':
            # Undo remove = add back
            self.shapes_by_frame[shape.frame_number].append(shape)

        self.redo_stack.append((action, shape))

    def redo(self):
        """Redo last undone operation."""
        if not self.redo_stack:
            return

        action, shape = self.redo_stack.pop()

        if action == 'add':
            # Redo add
            self.shapes_by_frame[shape.frame_number].append(shape)
        elif action == 'remove':
            # Redo remove
            self.shapes_by_frame[shape.frame_number].remove(shape)

        self.undo_stack.append((action, shape))

    def get_shapes_for_frame(self, frame_number: int) -> List[DrawingShape]:
        """Get all shapes for a specific frame."""
        return self.shapes_by_frame.get(frame_number, [])

    def clear_frame(self, frame_number: int):
        """Clear all shapes from a frame."""
        if frame_number in self.shapes_by_frame:
            shapes = self.shapes_by_frame[frame_number].copy()
            self.shapes_by_frame[frame_number].clear()

            # Batch undo
            self.undo_stack.append(('clear', shapes))
            self.redo_stack.clear()

    def get_all_shapes(self) -> List[DrawingShape]:
        """Get all shapes across all frames."""
        all_shapes = []
        for shapes in self.shapes_by_frame.values():
            all_shapes.extend(shapes)
        return all_shapes
```

## GUI Integration

### MainWindow Changes

**Add Drawing Mode Toggle:**
```python
# In menu bar
draw_menu = menubar.addMenu("&Draw")

enable_drawing_action = QAction("Enable &Drawing Mode", self)
enable_drawing_action.setCheckable(True)
enable_drawing_action.setShortcut(QKeySequence("Ctrl+D"))
enable_drawing_action.triggered.connect(self._toggle_drawing_mode)
draw_menu.addAction(enable_drawing_action)

# Tool selection submenu
tools_menu = draw_menu.addMenu("Select &Tool")
# ... add tool actions

# Save/Load drawings
save_drawings_action = QAction("&Save Drawings...", self)
save_drawings_action.triggered.connect(self._save_drawings)
draw_menu.addAction(save_drawings_action)

load_drawings_action = QAction("&Load Drawings...", self)
load_drawings_action.triggered.connect(self._load_drawings)
draw_menu.addAction(load_drawings_action)
```

**Add Drawing Toolbar:**
```python
# Add to main window layout
self.drawing_toolbar = DrawingToolbar()
self.drawing_toolbar.setVisible(False)  # Hidden by default

# Connect signals
self.drawing_toolbar.tool_selected.connect(self._on_tool_selected)
self.drawing_toolbar.undo_requested.connect(self.drawing_manager.undo)
# ...
```

**Overlay Drawing Canvas on Video Player:**
```python
# In VideoPlayerWidget
self.drawing_canvas = DrawingCanvas(self)
# Position canvas to overlay video display
```

**Update Frame Rendering:**
```python
def _get_frame(self, frame_number: int):
    # ... existing code ...

    # Apply analysis overlays
    if self.viz_engine:
        frame = self._apply_overlays(frame, frame_number)

    # Apply manual drawings
    if self.drawing_renderer:
        shapes = self.drawing_manager.get_shapes_for_frame(frame_number)
        frame = self.drawing_renderer.render(frame, shapes)

    return frame
```

## User Workflow

### Drawing a Line
1. User clicks "Draw" menu → "Enable Drawing Mode" (or Ctrl+D)
2. Drawing toolbar appears
3. User clicks "Line" tool button
4. User clicks on frame to set start point
5. User moves mouse (line preview follows)
6. User clicks again to set end point
7. Line is drawn with length and angle displayed
8. Line is saved to current frame

### Drawing an Angle
1. User selects "Angle" tool
2. User clicks first point
3. User clicks vertex (middle point)
4. User clicks third point
5. Angle is drawn with arc and degree measurement
6. Label can be added (e.g., "Spine Angle")

### Undo/Redo
- User clicks ↶ Undo button or presses Ctrl+Z
- Last drawing operation is undone
- User clicks ↷ Redo button or presses Ctrl+Y to redo

### Saving Drawings
1. User clicks "Draw" → "Save Drawings..."
2. Dialog asks for filename (defaults to video name + .drawings.json)
3. All drawings across all frames are saved
4. File includes video path for automatic loading

### Loading Drawings
1. User clicks "Draw" → "Load Drawings..."
2. User selects .drawings.json file
3. All drawings are loaded and displayed on corresponding frames

## F1 Styling

### Toolbar Style
- Glass panel background (consistent with analysis panel)
- Tool buttons with metallic gradients
- Active tool highlighted with silver accent
- Color picker with modern color wheel dialog
- Thickness slider with F1 styling

### Drawing Style Defaults
- Default color: Yellow (#FFFF00) - high visibility
- Default thickness: 2px
- Font: Segoe UI, consistent with theme
- Measurements with semi-transparent background boxes

### Color Palette for Drawings
```python
DRAWING_COLORS = {
    'yellow': (255, 255, 0),    # Default
    'red': (255, 0, 0),         # Important/corrections
    'green': (0, 255, 0),       # Good/target
    'cyan': (0, 255, 255),      # Reference
    'white': (255, 255, 255),   # General
}
```

## Testing Strategy

### Unit Tests
- Test shape data structures (serialization, measurements)
- Test tool logic (state transitions, shape creation)
- Test undo/redo stack operations
- Test storage (save/load round-trip)
- Test measurements (angle calculations, lengths)

### Integration Tests
- Test canvas mouse event handling
- Test toolbar signal connections
- Test drawing manager state management
- Test frame-specific shape retrieval

### Manual Testing
- Draw on various frame sizes
- Test undo/redo extensively
- Test save/load with different videos
- Verify measurements are accurate
- Test tool switching mid-drawing

## File Changes Summary

### New Files
- `src/drawing/__init__.py`
- `src/drawing/shapes.py` (~300 lines)
- `src/drawing/tools.py` (~400 lines)
- `src/drawing/canvas.py` (~350 lines)
- `src/drawing/toolbar.py` (~300 lines)
- `src/drawing/renderer.py` (~400 lines)
- `src/drawing/storage.py` (~150 lines)
- `src/drawing/manager.py` (~250 lines)
- `tests/test_drawing_shapes.py`
- `tests/test_drawing_tools.py`
- `tests/test_drawing_manager.py`
- `examples/drawing_demo.py`

### Modified Files
- `src/gui/main_window.py` (+150 lines for drawing integration)
- `src/gui/video_player.py` (+50 lines for canvas overlay)
- `TASK.md` (update with completed feature)

**Total New Code:** ~2,500 lines
**Tests:** ~800 lines

## Implementation Phases

### Phase 1: Core Infrastructure (Foundation)
- Implement shape data structures
- Implement basic tools (Line, Angle)
- Implement drawing renderer
- Basic save/load functionality

### Phase 2: Interactive Canvas (User Interaction)
- Implement drawing canvas widget
- Mouse event handling
- Tool preview during drawing
- Shape selection/deletion

### Phase 3: GUI Integration (Polish)
- Drawing toolbar widget
- Integrate with main window
- Undo/redo functionality
- F1 styling

### Phase 4: Advanced Features (Nice-to-Have)
- Circle and arc tools
- Text annotations
- Copy/paste shapes
- Apply drawing to multiple frames

## Success Criteria

✓ Users can draw lines, angles, circles on any frame
✓ Measurements are displayed accurately
✓ Undo/redo works reliably
✓ Drawings persist across sessions (save/load)
✓ Tool switching is intuitive
✓ Performance is smooth (no lag during drawing)
✓ F1 aesthetic is maintained
✓ 80%+ test coverage for drawing module

## Open Questions

1. **Frame Persistence**: Should drawings on one frame automatically apply to adjacent frames?
   - Decision: No, each frame has independent drawings (cleaner, more predictable)

2. **Calibration**: Should we ask user to calibrate measurements on first use?
   - Decision: Add calibration later (Phase 4), use pixels for now

3. **Shape Limits**: Should we limit number of shapes per frame?
   - Decision: No hard limit, but warn if performance degrades (>100 shapes)

4. **Export**: Should drawings be included in video export?
   - Decision: Yes, drawings should be rendered in export by default (with toggle option)
