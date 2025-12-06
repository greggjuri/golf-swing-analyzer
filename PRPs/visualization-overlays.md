# PRP: Visualization Overlays

## Overview
Implement a visualization system to draw analysis results (club tracking, angles, body landmarks, annotations) on video frames, making detection results visible and useful.

## Context
- We have club tracking (shaft detection, club head detection)
- We have angle calculation utilities
- We have body landmark constants (for future pose detection)
- Need to visualize these results on frames for analysis
- Will use OpenCV drawing functions (already a dependency)

## Requirements

### Functional Requirements
1. **Club Visualization**
   - Draw club shaft as a colored line
   - Draw club head as a circle
   - Annotate shaft angle
   - Show confidence scores

2. **Angle Visualization**
   - Draw angle arcs between lines/points
   - Label angles with degree measurements
   - Support different angle types (joint angles, club angles)

3. **Body Landmark Visualization**
   - Draw skeleton connecting body landmarks
   - Draw joint points as circles
   - Annotate joint angles
   - Different colors for left/right side

4. **General Annotations**
   - Text labels with background boxes
   - Frame numbers, timestamps
   - Swing phase indicators (address, backswing, etc.)
   - Measurement overlays

5. **Styling and Configuration**
   - Configurable colors, line thickness, font size
   - Preset color schemes (default, high-contrast, colorblind-friendly)
   - Opacity/alpha blending support
   - Option to disable specific overlay types

### Non-Functional Requirements
1. **Performance**: Render overlays at 30+ fps
2. **Quality**: Anti-aliased drawing where possible
3. **Flexibility**: Easy to add new overlay types
4. **Test Coverage**: >85% code coverage
5. **Code Quality**: Pass flake8, mypy validation

## Technical Design

### Module Structure
```
src/visualization/
├── __init__.py
├── engine.py           # Main VisualizationEngine class
├── renderers.py        # Specialized renderers for different overlay types
├── styles.py           # Color schemes and styling configuration
└── utils.py           # Drawing utility functions
```

### Core Classes

#### 1. VisualizationEngine
```python
class VisualizationEngine:
    """Main engine for rendering overlays on frames.

    Coordinates multiple renderers and applies overlays to frames.

    Example:
        engine = VisualizationEngine()
        frame_with_overlays = engine.render(
            frame,
            club_detection=club_result,
            show_angles=True
        )
    """

    def __init__(
        self,
        style: Optional[StyleConfig] = None,
        enable_antialiasing: bool = True
    ):
        """Initialize visualization engine."""

    def render(
        self,
        frame: np.ndarray,
        club_detection: Optional[DetectionResult] = None,
        body_landmarks: Optional[dict] = None,
        annotations: Optional[List[Annotation]] = None,
        show_angles: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """Render all overlays on frame.

        Args:
            frame: Input frame
            club_detection: Club detection result
            body_landmarks: Body landmark positions
            annotations: Text annotations to draw
            show_angles: Whether to show angle measurements
            show_confidence: Whether to show confidence scores

        Returns:
            Frame with overlays
        """
```

#### 2. ClubRenderer
```python
class ClubRenderer:
    """Render club shaft and head overlays."""

    def __init__(self, style: StyleConfig):
        """Initialize renderer with style config."""

    def draw_shaft(
        self,
        frame: np.ndarray,
        shaft_line: Line,
        shaft_angle: Optional[float] = None,
        confidence: Optional[float] = None
    ) -> np.ndarray:
        """Draw club shaft line with optional angle annotation.

        Args:
            frame: Frame to draw on
            shaft_line: Shaft endpoints (x1, y1, x2, y2)
            shaft_angle: Optional shaft angle in degrees
            confidence: Optional confidence score

        Returns:
            Frame with shaft drawn
        """

    def draw_club_head(
        self,
        frame: np.ndarray,
        center: Point2D,
        radius: float
    ) -> np.ndarray:
        """Draw club head circle.

        Args:
            frame: Frame to draw on
            center: Club head center point
            radius: Club head radius

        Returns:
            Frame with club head drawn
        """
```

#### 3. BodyRenderer
```python
class BodyRenderer:
    """Render body skeleton and joint overlays."""

    # Skeleton connections (MediaPipe format)
    SKELETON_CONNECTIONS = [
        (BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER),
        (BodyLandmark.LEFT_SHOULDER, BodyLandmark.LEFT_ELBOW),
        # ... etc
    ]

    def __init__(self, style: StyleConfig, handedness: str = "right"):
        """Initialize renderer."""

    def draw_skeleton(
        self,
        frame: np.ndarray,
        landmarks: dict[int, Point2D]
    ) -> np.ndarray:
        """Draw full body skeleton.

        Args:
            frame: Frame to draw on
            landmarks: Dictionary mapping landmark indices to positions

        Returns:
            Frame with skeleton drawn
        """

    def draw_joint_angles(
        self,
        frame: np.ndarray,
        landmarks: dict[int, Point2D],
        joint_calculator: JointAngleCalculator,
        show_labels: bool = True
    ) -> np.ndarray:
        """Draw joint angles with arcs and labels.

        Args:
            frame: Frame to draw on
            landmarks: Body landmark positions
            joint_calculator: Calculator for joint angles
            show_labels: Whether to show angle labels

        Returns:
            Frame with joint angles drawn
        """
```

#### 4. AngleRenderer
```python
class AngleRenderer:
    """Render angle arcs and measurements."""

    def draw_angle_arc(
        self,
        frame: np.ndarray,
        vertex: Point2D,
        point1: Point2D,
        point2: Point2D,
        angle: float,
        radius: int = 30,
        show_label: bool = True
    ) -> np.ndarray:
        """Draw angle arc between three points.

        Args:
            frame: Frame to draw on
            vertex: Vertex point of angle
            point1: First point
            point2: Second point
            angle: Angle in degrees
            radius: Arc radius in pixels
            show_label: Whether to show angle label

        Returns:
            Frame with angle arc drawn
        """

    def draw_angle_label(
        self,
        frame: np.ndarray,
        position: Point2D,
        angle: float,
        label_prefix: str = ""
    ) -> np.ndarray:
        """Draw angle measurement label.

        Args:
            frame: Frame to draw on
            position: Label position
            angle: Angle value in degrees
            label_prefix: Optional prefix (e.g., "Elbow: ")

        Returns:
            Frame with label drawn
        """
```

#### 5. StyleConfig
```python
@dataclass
class StyleConfig:
    """Configuration for visualization styling."""

    # Club colors
    shaft_color: Tuple[int, int, int] = (0, 255, 0)  # Green
    shaft_thickness: int = 3
    club_head_color: Tuple[int, int, int] = (0, 0, 255)  # Red
    club_head_thickness: int = 2

    # Body colors
    skeleton_color: Tuple[int, int, int] = (255, 255, 0)  # Cyan
    skeleton_thickness: int = 2
    joint_color: Tuple[int, int, int] = (255, 0, 255)  # Magenta
    joint_radius: int = 5

    # Angle colors
    angle_arc_color: Tuple[int, int, int] = (255, 165, 0)  # Orange
    angle_thickness: int = 2

    # Text styling
    font: int = cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.6
    font_thickness: int = 2
    text_color: Tuple[int, int, int] = (255, 255, 255)  # White
    text_bg_color: Tuple[int, int, int] = (0, 0, 0)  # Black
    text_bg_alpha: float = 0.7

    # General
    antialiasing: bool = True

    @classmethod
    def high_contrast(cls) -> 'StyleConfig':
        """Create high-contrast color scheme."""

    @classmethod
    def colorblind_friendly(cls) -> 'StyleConfig':
        """Create colorblind-friendly color scheme."""
```

#### 6. Annotation
```python
@dataclass
class Annotation:
    """Text annotation to draw on frame."""
    text: str
    position: Point2D
    font_scale: Optional[float] = None
    color: Optional[Tuple[int, int, int]] = None
    background: bool = True
```

### Drawing Utilities

```python
def draw_text_with_background(
    frame: np.ndarray,
    text: str,
    position: Point2D,
    font: int,
    font_scale: float,
    text_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int],
    bg_alpha: float = 0.7,
    padding: int = 5
) -> np.ndarray:
    """Draw text with semi-transparent background box."""

def draw_line_with_arrow(
    frame: np.ndarray,
    start: Point2D,
    end: Point2D,
    color: Tuple[int, int, int],
    thickness: int = 2
) -> np.ndarray:
    """Draw line with arrowhead at end."""

def draw_angle_arc_cv2(
    frame: np.ndarray,
    center: Point2D,
    radius: int,
    start_angle: float,
    end_angle: float,
    color: Tuple[int, int, int],
    thickness: int = 2
) -> np.ndarray:
    """Draw angle arc using OpenCV ellipse function."""

def blend_overlay(
    frame: np.ndarray,
    overlay: np.ndarray,
    alpha: float
) -> np.ndarray:
    """Blend overlay onto frame with alpha transparency."""
```

## Implementation Steps

1. ✅ Create module structure and __init__.py
2. ✅ Implement StyleConfig dataclass
3. ✅ Implement drawing utility functions
4. ✅ Implement AngleRenderer
5. ✅ Implement ClubRenderer
6. ✅ Implement BodyRenderer
7. ✅ Implement VisualizationEngine
8. ✅ Write tests for utility functions
9. ✅ Write tests for renderers
10. ✅ Write integration tests with real detection data
11. ✅ Create demo script with video examples
12. ✅ Performance testing
13. ✅ Documentation and examples

## Success Criteria

### Must Have
- [x] ClubRenderer draws shaft and club head correctly
- [x] AngleRenderer draws angle arcs with labels
- [x] BodyRenderer draws skeleton (even without pose detection yet)
- [x] Text annotations with backgrounds
- [x] VisualizationEngine coordinates all renderers
- [x] Test coverage >85%
- [x] All tests pass
- [x] Passes flake8 and mypy validation
- [x] Demo script shows overlays on video frames

### Should Have
- [x] Multiple color schemes (high-contrast, colorblind-friendly)
- [x] Configurable styling (colors, thickness, fonts)
- [x] Anti-aliased drawing
- [x] Alpha blending support
- [x] Performance >30 fps on typical hardware

### Nice to Have
- [ ] Animated overlays (fade in/out)
- [ ] Custom overlay plugins
- [ ] Export overlay templates
- [ ] Comparison mode (side-by-side frames)

## Test Strategy

### Unit Tests
1. **Utility Functions**
   - Test text with background rendering
   - Test angle arc drawing
   - Test alpha blending

2. **Renderers**
   - Test club shaft/head drawing
   - Test skeleton drawing
   - Test angle annotation

3. **StyleConfig**
   - Test preset creation
   - Test color scheme validation

### Integration Tests
1. Use real club detection results
2. Use synthetic body landmarks
3. Test full pipeline: detection → visualization
4. Verify visual output (basic sanity checks)

### Performance Tests
1. Measure rendering time per frame
2. Test with different resolutions
3. Verify >30 fps requirement

## Dependencies
- OpenCV (cv2) - already in requirements.txt
- NumPy - already in requirements.txt
- src.analysis (for angle calculations)
- src.detection (for club detection types)

## Example Usage
```python
from src.visualization import VisualizationEngine, StyleConfig
from src.detection import ClubDetector
from src.video import VideoLoader, FrameExtractor

# Initialize components
detector = ClubDetector()
engine = VisualizationEngine(style=StyleConfig.high_contrast())

# Load video
with VideoLoader("swing.mp4") as video:
    extractor = FrameExtractor(video)
    frame = extractor.extract_frame(100)

    # Detect club
    result = detector.detect(frame)

    # Render overlays
    visualized = engine.render(
        frame,
        club_detection=result,
        show_angles=True,
        show_confidence=True
    )

    # Save or display
    cv2.imwrite("output.jpg", visualized)
```

## Risk Assessment
1. **Text rendering clarity** - Mitigate with background boxes and configurable font sizes
2. **Color visibility on different backgrounds** - Provide multiple color schemes
3. **Performance on high-res video** - Optimize drawing operations, use ROI where possible
4. **Cluttered overlays** - Make overlays toggleable, use smart label positioning

## Future Enhancements
- Interactive overlay editing in GUI
- 3D visualization of swing plane
- Overlay animation and transitions
- Comparison overlays (ideal vs actual)
- Custom measurement tools
