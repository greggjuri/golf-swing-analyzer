# PRP: Swing Plane Analysis

## Overview
Analyze the golf swing plane by tracking the club shaft path through 3D space and calculating the best-fit plane. Provides key metrics like attack angle, swing path, and on-plane deviation for swing analysis.

## Objectives
1. Calculate best-fit swing plane from club shaft positions
2. Measure attack angle, swing path, and face angle
3. Calculate on-plane vs off-plane deviations
4. Provide plane visualization for overlays
5. Integrate with existing club tracking and visualization systems

## Background

### What is the Swing Plane?
The swing plane is the tilted surface that the golf club travels along during the swing. Think of it as an inclined sheet of glass that the club shaft passes through. Key concepts:

- **Address plane**: Initial plane at address position
- **Backswing plane**: Plane during backswing
- **Downswing plane**: Plane during downswing (often different from backswing)
- **Attack angle**: Angle of approach at impact (up/down)
- **Swing path**: Direction of club travel at impact (in-to-out/out-to-in)

### Why It Matters
- **Ball flight**: Swing plane determines ball trajectory
- **Consistency**: Staying on-plane produces repeatable shots
- **Power**: Efficient plane maximizes clubhead speed
- **Common faults**: Most swing issues relate to plane deviations

## Architecture

### Module Structure
```
src/plane/
├── __init__.py           # Module exports
├── geometry.py           # 3D plane mathematics
├── calculator.py         # PlaneCalculator - fit plane to points
├── detector.py           # PlaneDetector - detect swing plane
├── metrics.py            # PlaneMetrics - angles and deviations
└── analyzer.py           # SwingPlaneAnalyzer - high-level interface
```

### Key Components

#### 1. Plane Geometry (geometry.py)
3D plane mathematics and operations.

**Plane3D Class:**
```python
@dataclass
class Plane3D:
    """3D plane in normal form: ax + by + cz + d = 0."""

    a: float  # Normal vector x component
    b: float  # Normal vector y component
    c: float  # Normal vector z component
    d: float  # Distance from origin

    def normal_vector(self) -> np.ndarray:
        """Get unit normal vector."""
        return np.array([self.a, self.b, self.c])

    def point_distance(self, point: Point3D) -> float:
        """Calculate perpendicular distance from point to plane."""

    def project_point(self, point: Point3D) -> Point3D:
        """Project point onto plane."""

    def angle_to_horizontal(self) -> float:
        """Angle of plane relative to horizontal ground."""

    def angle_to_target_line(self, target_direction: np.ndarray) -> float:
        """Angle of plane relative to target direction."""
```

**Helper Functions:**
```python
def fit_plane_svd(points: List[Point3D]) -> Plane3D:
    """Fit best-fit plane using SVD (Singular Value Decomposition).

    Uses principal component analysis to find plane that minimizes
    perpendicular distance to all points.
    """

def plane_line_intersection(
    plane: Plane3D,
    line_point: Point3D,
    line_direction: np.ndarray
) -> Optional[Point3D]:
    """Find intersection of plane and line."""

def angle_between_planes(plane1: Plane3D, plane2: Plane3D) -> float:
    """Calculate angle between two planes."""
```

#### 2. Plane Calculator (calculator.py)
Calculate best-fit plane from shaft positions.

**Interface:**
```python
class PlaneCalculator:
    """Calculate swing plane from club shaft positions.

    Uses weighted regression to fit plane, with higher weights
    for positions near impact.
    """

    def __init__(
        self,
        impact_zone_weight: float = 2.0,
        min_points: int = 10
    ):
        """Initialize calculator.

        Args:
            impact_zone_weight: Weight multiplier for impact zone points
            min_points: Minimum points required to fit plane
        """

    def calculate_plane(
        self,
        shaft_positions: List[ShaftPosition],
        impact_frame: Optional[int] = None
    ) -> Optional[Plane3D]:
        """Calculate best-fit plane from shaft positions.

        Args:
            shaft_positions: List of shaft positions with 3D points
            impact_frame: Frame number of impact (for weighting)

        Returns:
            Best-fit Plane3D or None if insufficient data
        """

    def calculate_weighted_plane(
        self,
        points: List[Point3D],
        weights: List[float]
    ) -> Plane3D:
        """Calculate weighted best-fit plane."""

@dataclass
class ShaftPosition:
    """Club shaft position in 3D space at specific frame."""

    frame_number: int
    base_point: Point3D      # Grip end
    tip_point: Point3D       # Club head end
    timestamp: float

    def midpoint(self) -> Point3D:
        """Get midpoint of shaft."""

    def direction(self) -> np.ndarray:
        """Get shaft direction vector."""
```

#### 3. Plane Detector (detector.py)
Detect swing phases and their planes.

**Interface:**
```python
class PlaneDetector:
    """Detect swing plane for different swing phases.

    Identifies backswing, downswing, and impact positions,
    then calculates separate planes for each phase.
    """

    def __init__(
        self,
        phase_detector: Optional[SwingPhaseDetector] = None
    ):
        """Initialize detector."""

    def detect_swing_planes(
        self,
        shaft_positions: List[ShaftPosition]
    ) -> SwingPlaneResult:
        """Detect planes for all swing phases.

        Returns:
            SwingPlaneResult with planes for each phase
        """

@dataclass
class SwingPlaneResult:
    """Result of swing plane detection."""

    address_plane: Optional[Plane3D]
    backswing_plane: Optional[Plane3D]
    downswing_plane: Optional[Plane3D]
    full_swing_plane: Optional[Plane3D]

    impact_position: Optional[ShaftPosition]
    top_position: Optional[ShaftPosition]

    def plane_shift(self) -> Optional[float]:
        """Angle between backswing and downswing planes."""
```

#### 4. Plane Metrics (metrics.py)
Calculate golf-specific plane metrics.

**Interface:**
```python
class PlaneMetrics:
    """Calculate swing plane metrics for analysis.

    Computes attack angle, swing path, on-plane deviation,
    and other golf-specific measurements.
    """

    def __init__(
        self,
        target_direction: np.ndarray = np.array([0, 1, 0])  # Down-target
    ):
        """Initialize metrics calculator."""

    def attack_angle(
        self,
        impact_shaft: ShaftPosition,
        plane: Plane3D
    ) -> float:
        """Calculate attack angle at impact.

        Positive = hitting up on ball
        Negative = hitting down on ball

        Returns:
            Attack angle in degrees
        """

    def swing_path(
        self,
        impact_shaft: ShaftPosition,
        target_direction: np.ndarray
    ) -> float:
        """Calculate swing path at impact.

        Positive = in-to-out
        Negative = out-to-in

        Returns:
            Swing path angle in degrees
        """

    def on_plane_deviation(
        self,
        shaft_position: ShaftPosition,
        plane: Plane3D
    ) -> float:
        """Calculate perpendicular distance from shaft to plane.

        Returns:
            Distance in same units as input points
        """

    def plane_angle(
        self,
        plane: Plane3D
    ) -> float:
        """Calculate plane angle from horizontal.

        Returns:
            Angle in degrees (0 = flat, 90 = vertical)
        """

@dataclass
class SwingMetrics:
    """Complete swing plane metrics."""

    attack_angle: float           # Impact attack angle (degrees)
    swing_path: float             # Swing path at impact (degrees)
    plane_angle: float            # Plane tilt from horizontal
    plane_shift: Optional[float]  # Backswing to downswing shift

    max_deviation: float          # Maximum off-plane distance
    avg_deviation: float          # Average off-plane distance
    deviation_at_impact: float    # Off-plane at impact
```

#### 5. Swing Plane Analyzer (analyzer.py)
High-level interface combining all components.

**Interface:**
```python
class SwingPlaneAnalyzer:
    """High-level swing plane analysis interface.

    Combines plane detection, calculation, and metrics
    into a single easy-to-use interface.

    Example:
        analyzer = SwingPlaneAnalyzer()

        # Analyze swing
        result = analyzer.analyze(shaft_positions)

        # Get metrics
        print(f"Attack angle: {result.metrics.attack_angle:.1f}°")
        print(f"Swing path: {result.metrics.swing_path:.1f}°")
        print(f"Plane angle: {result.metrics.plane_angle:.1f}°")
    """

    def __init__(
        self,
        calculator: Optional[PlaneCalculator] = None,
        detector: Optional[PlaneDetector] = None,
        metrics_calculator: Optional[PlaneMetrics] = None
    ):
        """Initialize analyzer with optional custom components."""

    def analyze(
        self,
        shaft_positions: List[ShaftPosition]
    ) -> SwingPlaneAnalysis:
        """Perform complete swing plane analysis.

        Args:
            shaft_positions: Club shaft positions across swing

        Returns:
            Complete analysis with planes, metrics, and deviations
        """

@dataclass
class SwingPlaneAnalysis:
    """Complete swing plane analysis result."""

    planes: SwingPlaneResult
    metrics: SwingMetrics
    deviations: List[float]  # Deviation for each shaft position

    success: bool
    error_message: Optional[str] = None
```

## Data Flow

```
Club Tracking → ShaftPositions → PlaneDetector → SwingPlaneResult
                                       ↓
                                 PlaneCalculator → Plane3D
                                       ↓
                                  PlaneMetrics → SwingMetrics
                                       ↓
                              SwingPlaneAnalyzer → Complete Analysis
```

## 3D Coordinate System

Using standard camera/screen coordinates:
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Top (-) to Bottom (+) (screen space)
- **Z-axis**: Away from camera (-) to Toward camera (+)

**Important**: Since we're working from 2D video, Z-coordinates will be estimated based on:
- Club shaft angle (steep = more depth)
- Position in frame (center = neutral, edges = depth)
- Known club length as scale reference

## Key Algorithms

### 1. Best-Fit Plane (SVD Method)

```python
def fit_plane_svd(points: np.ndarray) -> Plane3D:
    """
    1. Center points: subtract centroid
    2. Compute covariance matrix
    3. SVD decomposition
    4. Normal vector = smallest singular vector
    5. Calculate d using centroid
    """
    centroid = np.mean(points, axis=0)
    centered = points - centroid

    # SVD: centered = U * S * V^T
    U, S, Vt = np.linalg.svd(centered)

    # Normal is last row of V^T (smallest singular value)
    normal = Vt[-1]
    a, b, c = normal

    # d = -(ax + by + cz) for centroid
    d = -np.dot(normal, centroid)

    return Plane3D(a, b, c, d)
```

### 2. Attack Angle Calculation

```python
def attack_angle(shaft: ShaftPosition, plane: Plane3D) -> float:
    """
    Attack angle = angle between shaft and horizontal plane
    Measured in plane of swing

    Positive = hitting up
    Negative = hitting down
    """
    # Project shaft onto swing plane
    shaft_dir = shaft.direction()
    plane_normal = plane.normal_vector()

    # Remove component perpendicular to plane
    shaft_in_plane = shaft_dir - np.dot(shaft_dir, plane_normal) * plane_normal

    # Angle from horizontal
    horizontal = np.array([1, 0, 0])  # Assume horizontal is X-axis
    angle = angle_between_vectors(shaft_in_plane, horizontal)

    # Sign based on vertical component
    if shaft_in_plane[1] > 0:  # Pointing down
        angle = -angle

    return angle
```

### 3. Swing Path Calculation

```python
def swing_path(shaft: ShaftPosition, target: np.ndarray) -> float:
    """
    Swing path = horizontal angle of club travel relative to target

    Positive = in-to-out (right for right-handed)
    Negative = out-to-in (left for right-handed)
    """
    # Get club travel direction (from shaft movement)
    travel_dir = shaft.direction()

    # Project to horizontal plane
    travel_horizontal = np.array([travel_dir[0], 0, travel_dir[2]])
    travel_horizontal = travel_horizontal / np.linalg.norm(travel_horizontal)

    # Angle from target line
    angle = angle_between_vectors(travel_horizontal, target)

    # Sign based on cross product
    cross = np.cross(target, travel_horizontal)
    if cross[1] < 0:  # Y-component determines in/out
        angle = -angle

    return angle
```

## Integration Points

### With Club Tracking
```python
from src.detection import ClubDetector, ClubTracker
from src.plane import SwingPlaneAnalyzer, ShaftPosition

# Track club
detector = ClubDetector()
tracker = ClubTracker()

shaft_positions = []
for frame_num, frame in enumerate(frames):
    detection = detector.detect(frame)
    if detection and detection.shaft_detected:
        # Convert to 3D (estimate Z from angle)
        shaft_pos = ShaftPosition(
            frame_number=frame_num,
            base_point=estimate_3d_point(detection.shaft_line.base),
            tip_point=estimate_3d_point(detection.shaft_line.tip),
            timestamp=frame_num / fps
        )
        shaft_positions.append(shaft_pos)

# Analyze plane
analyzer = SwingPlaneAnalyzer()
analysis = analyzer.analyze(shaft_positions)
```

### With Visualization
```python
from src.visualization import VisualizationEngine
from src.plane import SwingPlaneAnalyzer

# Analyze swing
analysis = analyzer.analyze(shaft_positions)

# Visualize plane
engine = VisualizationEngine()

# Draw plane line
plane_line = project_plane_to_frame(analysis.planes.downswing_plane, frame)
frame_with_plane = engine.render(
    frame,
    annotations=[
        {'type': 'line', 'line': plane_line, 'color': (0, 255, 255), 'thickness': 3},
        {'type': 'text', 'text': f"Attack: {analysis.metrics.attack_angle:.1f}°"},
    ]
)
```

## Testing Strategy

### Unit Tests

1. **Plane Geometry**
   - Fit plane to known points
   - Calculate point distances
   - Project points onto plane
   - Plane-line intersections

2. **Plane Calculator**
   - Calculate from synthetic shaft positions
   - Handle weighted points
   - Minimum points validation
   - Edge cases (collinear points)

3. **Plane Metrics**
   - Attack angle calculation
   - Swing path calculation
   - On-plane deviation
   - Known club positions → known metrics

4. **Integration**
   - Full pipeline with real tracking data
   - Multiple swing phases
   - Visualization integration

### Test Fixtures

1. **Synthetic Swing Data**
   - Perfect on-plane swing
   - Known attack angle
   - Known swing path
   - Off-plane swing with deviation

2. **Edge Cases**
   - Insufficient points
   - Flat/vertical planes
   - Extreme attack angles

## Visualization Output

The system should support rendering:

1. **Plane Line**: Line showing plane intersection with frame
2. **Deviation Indicators**: Color-coded markers for on/off plane
3. **Metrics Overlay**: Text showing angles and measurements
4. **Plane Trace**: Path of club through swing
5. **Reference Lines**: Target line, horizontal reference

## Success Criteria

1. **Accuracy**
   - Plane fit within 2° of ground truth
   - Attack angle within 1° of measured
   - Swing path within 2° of measured

2. **Robustness**
   - Handle 10+ shaft positions
   - Work with partial swings
   - Handle noisy tracking data

3. **Performance**
   - Calculate plane in <10ms
   - Full analysis in <50ms
   - Support real-time visualization

4. **Coverage**
   - 95%+ test coverage
   - All edge cases handled
   - Integration tests pass

## Future Enhancements

1. **Dynamic Plane**
   - Plane evolution through swing
   - Transition points
   - Plane consistency metrics

2. **Comparison**
   - Compare to ideal plane
   - Compare to professional swings
   - Historical trend analysis

3. **Advanced Metrics**
   - Cast angle
   - Shaft lean
   - Low point location
   - Entry angle

4. **Machine Learning**
   - Auto-detect swing faults
   - Predict ball flight
   - Personalized recommendations
