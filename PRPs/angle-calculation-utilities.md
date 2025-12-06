# Product Requirements Prompt: Angle Calculation Utilities

## 1. Context

### Feature Overview
This feature implements the mathematical foundation for analyzing golf swings. It provides utilities to calculate angles between points, lines, and vectors, measure joint angles from body landmarks, and calculate club positions relative to reference lines. This module is essential for quantifying swing mechanics and identifying technical issues.

### Architecture Integration
This module is part of the **analysis layer** in the application architecture (see PLANNING.md):
- Located in `src/analysis/` package
- Provides utilities to downstream modules:
  - `src/detection/` will provide landmark coordinates to analyze
  - `src/visualization/` will use angle measurements to draw overlays
  - `src/gui/` will display angle measurements to users
- Independent of video processing (pure mathematical calculations)

### Dependencies
- **External**: NumPy (for vector/matrix operations)
- **Internal**: None (foundational module with no internal dependencies)
- **System**: Python 3.10+

### Golf Swing Context
The module will calculate key measurements:
- **Body angles**: spine tilt, knee flex, hip angle, shoulder rotation
- **Club angles**: shaft angle to ground, lie angle, swing plane
- **Reference measurements**: typical ranges for proper swing mechanics

## 2. Technical Specification

### 2.1 Data Structures and Types

```python
from typing import Tuple, Optional, Union
import numpy as np
from numpy.typing import NDArray

# Type aliases
Point2D = Union[Tuple[float, float], NDArray[np.float64]]  # (x, y)
Vector2D = NDArray[np.float64]  # 2-element array
Angle = float  # Degrees (primary unit)
AngleRadians = float  # Radians (for internal calculations)

# Landmark indices (for pose detection compatibility)
class BodyLandmark:
    """Standard body landmark indices for pose detection."""
    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
```

### 2.2 Class and Function Signatures

#### Core Angle Utilities (`src/analysis/angles.py`)

```python
def angle_between_points(
    point1: Point2D,
    vertex: Point2D,
    point2: Point2D
) -> Angle:
    """Calculate angle formed by three points.

    Args:
        point1: First point
        vertex: Vertex point (angle measured here)
        point2: Third point

    Returns:
        Angle in degrees (0-180)

    Raises:
        ValueError: If points are collinear or duplicate
    """


def angle_between_vectors(
    vector1: Vector2D,
    vector2: Vector2D
) -> Angle:
    """Calculate angle between two vectors.

    Args:
        vector1: First vector
        vector2: Second vector

    Returns:
        Angle in degrees (0-180)

    Raises:
        ValueError: If either vector has zero length
    """


def angle_from_horizontal(line_start: Point2D, line_end: Point2D) -> Angle:
    """Calculate angle of line relative to horizontal.

    Args:
        line_start: Starting point of line
        line_end: Ending point of line

    Returns:
        Angle in degrees (-90 to 90, positive = counterclockwise)

    Raises:
        ValueError: If points are identical
    """


def angle_from_vertical(line_start: Point2D, line_end: Point2D) -> Angle:
    """Calculate angle of line relative to vertical.

    Args:
        line_start: Starting point of line
        line_end: Ending point of line

    Returns:
        Angle in degrees (-90 to 90, positive = counterclockwise from vertical)

    Raises:
        ValueError: If points are identical
    """


def normalize_angle(
    angle: Angle,
    range_type: str = "0-360"
) -> Angle:
    """Normalize angle to specified range.

    Args:
        angle: Angle in degrees
        range_type: "0-360", "-180-180", or "0-180"

    Returns:
        Normalized angle in specified range

    Raises:
        ValueError: If range_type is invalid
    """


def degrees_to_radians(degrees: Angle) -> AngleRadians:
    """Convert degrees to radians."""


def radians_to_degrees(radians: AngleRadians) -> Angle:
    """Convert radians to degrees."""


# Geometry utilities

def distance_between_points(point1: Point2D, point2: Point2D) -> float:
    """Calculate Euclidean distance between two points."""


def line_slope(point1: Point2D, point2: Point2D) -> Optional[float]:
    """Calculate slope of line through two points.

    Returns:
        Slope value, or None if line is vertical
    """


def point_to_line_distance(
    point: Point2D,
    line_start: Point2D,
    line_end: Point2D
) -> float:
    """Calculate perpendicular distance from point to line."""


def project_point_onto_line(
    point: Point2D,
    line_start: Point2D,
    line_end: Point2D
) -> Point2D:
    """Project point onto line (find closest point on line)."""


def line_intersection(
    line1_start: Point2D,
    line1_end: Point2D,
    line2_start: Point2D,
    line2_end: Point2D
) -> Optional[Point2D]:
    """Find intersection point of two lines.

    Returns:
        Intersection point, or None if lines are parallel
    """
```

#### Joint Angle Calculator (`src/analysis/joint_angles.py`)

```python
class JointAngleCalculator:
    """Calculate joint angles from body landmark positions.

    Supports both left-handed and right-handed golfers.
    """

    def __init__(self, handedness: str = "right"):
        """Initialize calculator.

        Args:
            handedness: "right" or "left" for golfer handedness

        Raises:
            ValueError: If handedness is invalid
        """

    def shoulder_angle(
        self,
        shoulder: Point2D,
        elbow: Point2D,
        hip: Point2D
    ) -> Angle:
        """Calculate shoulder angle (upper arm to torso).

        Measures angle between upper arm and torso line.

        Args:
            shoulder: Shoulder landmark position
            elbow: Elbow landmark position
            hip: Hip landmark position

        Returns:
            Angle in degrees (0-180)
        """

    def elbow_angle(
        self,
        shoulder: Point2D,
        elbow: Point2D,
        wrist: Point2D
    ) -> Angle:
        """Calculate elbow flexion angle.

        Args:
            shoulder: Shoulder landmark position
            elbow: Elbow landmark position
            wrist: Wrist landmark position

        Returns:
            Angle in degrees (0-180, 180 = full extension)
        """

    def knee_angle(
        self,
        hip: Point2D,
        knee: Point2D,
        ankle: Point2D
    ) -> Angle:
        """Calculate knee flexion angle.

        Args:
            hip: Hip landmark position
            knee: Knee landmark position
            ankle: Ankle landmark position

        Returns:
            Angle in degrees (0-180, 180 = full extension)
        """

    def hip_angle(
        self,
        shoulder: Point2D,
        hip: Point2D,
        knee: Point2D
    ) -> Angle:
        """Calculate hip flexion angle.

        Args:
            shoulder: Shoulder landmark position
            hip: Hip landmark position
            knee: Knee landmark position

        Returns:
            Angle in degrees (0-180)
        """

    def spine_angle(
        self,
        shoulder: Point2D,
        hip: Point2D,
        reference_vertical: Optional[Tuple[Point2D, Point2D]] = None
    ) -> Angle:
        """Calculate spine tilt angle from vertical.

        Args:
            shoulder: Shoulder landmark position (midpoint of shoulders)
            hip: Hip landmark position (midpoint of hips)
            reference_vertical: Optional vertical reference line
                               (defaults to vertical through hip)

        Returns:
            Angle in degrees from vertical (0-90, positive = forward tilt)
        """

    def wrist_hinge_angle(
        self,
        elbow: Point2D,
        wrist: Point2D,
        club_grip_end: Point2D
    ) -> Angle:
        """Calculate wrist hinge angle (wrist cock).

        Measures angle between forearm and club shaft at wrist.

        Args:
            elbow: Elbow landmark position
            wrist: Wrist landmark position
            club_grip_end: End of club grip position

        Returns:
            Angle in degrees (0-180, 90 = maximum hinge)
        """

    def get_typical_ranges(self) -> dict[str, Tuple[float, float]]:
        """Get typical angle ranges for proper golf swing mechanics.

        Returns:
            Dictionary mapping measurement names to (min, max) ranges
        """
```

#### Club Angle Calculator (`src/analysis/club_angles.py`)

```python
class ClubAngleCalculator:
    """Calculate club shaft and swing plane angles."""

    def shaft_angle_to_ground(
        self,
        grip_point: Point2D,
        club_head: Point2D,
        ground_reference: Optional[Tuple[Point2D, Point2D]] = None
    ) -> Angle:
        """Calculate club shaft angle relative to ground.

        Args:
            grip_point: Position of club grip
            club_head: Position of club head
            ground_reference: Optional horizontal ground line
                            (defaults to horizontal through club head)

        Returns:
            Angle in degrees from ground (0-90)
        """

    def shaft_angle_to_vertical(
        self,
        grip_point: Point2D,
        club_head: Point2D
    ) -> Angle:
        """Calculate club shaft angle from vertical.

        Args:
            grip_point: Position of club grip
            club_head: Position of club head

        Returns:
            Angle in degrees from vertical (0-90)
        """

    def shaft_angle_to_target_line(
        self,
        grip_point: Point2D,
        club_head: Point2D,
        target_line: Tuple[Point2D, Point2D]
    ) -> Angle:
        """Calculate club shaft angle relative to target line.

        Args:
            grip_point: Position of club grip
            club_head: Position of club head
            target_line: Line toward target (start, end)

        Returns:
            Angle in degrees (0-90)
        """

    def lie_angle(
        self,
        shaft_grip: Point2D,
        shaft_hosel: Point2D,
        club_head_toe: Point2D,
        ground_reference: Tuple[Point2D, Point2D]
    ) -> Angle:
        """Calculate lie angle (club sole to ground when shaft at address).

        Args:
            shaft_grip: Top of shaft (grip)
            shaft_hosel: Bottom of shaft (hosel)
            club_head_toe: Toe of club head
            ground_reference: Horizontal ground line

        Returns:
            Lie angle in degrees (typical: 60-65 degrees)
        """

    def swing_plane_angle(
        self,
        hands_at_address: Point2D,
        hands_at_top: Point2D,
        ball_position: Point2D
    ) -> Angle:
        """Calculate swing plane angle.

        Measures angle of swing plane relative to ground.

        Args:
            hands_at_address: Hand position at address
            hands_at_top: Hand position at top of backswing
            ball_position: Ball position on ground

        Returns:
            Swing plane angle in degrees (typical: 45-60 degrees)
        """
```

### 2.3 File Locations

New files to create:
- `src/analysis/__init__.py` - Package initialization
- `src/analysis/angles.py` - Core angle calculation functions (~200 lines)
- `src/analysis/joint_angles.py` - JointAngleCalculator class (~150 lines)
- `src/analysis/club_angles.py` - ClubAngleCalculator class (~150 lines)
- `tests/test_angles.py` - Tests for core angle functions (~300 lines)
- `tests/test_joint_angles.py` - Tests for joint angles (~200 lines)
- `tests/test_club_angles.py` - Tests for club angles (~200 lines)

## 3. Implementation Steps

### Step 1: Create Module Structure
Create the analysis package and empty files.

```bash
mkdir -p src/analysis
touch src/analysis/__init__.py
touch src/analysis/angles.py
touch src/analysis/joint_angles.py
touch src/analysis/club_angles.py
touch tests/test_angles.py
touch tests/test_joint_angles.py
touch tests/test_club_angles.py
```

**Validation**: All files exist and package is importable.

### Step 2: Implement Core Angle Functions
In `src/analysis/angles.py`, implement fundamental angle calculations.

**Key requirements**:
- Use NumPy for vector operations
- All calculations in degrees (convert internally to radians as needed)
- Proper error handling for edge cases (zero-length vectors, collinear points)
- Type hints for all functions
- Google-style docstrings

**Implementation order**:
1. Helper functions: `degrees_to_radians`, `radians_to_degrees`
2. Basic distance: `distance_between_points`
3. `angle_between_vectors` (using np.arccos(dot product))
4. `angle_between_points` (convert to vectors, use above)
5. `angle_from_horizontal` (using np.arctan2)
6. `angle_from_vertical` (transform horizontal calculation)
7. `normalize_angle`

**Code pattern for angle_between_vectors**:
```python
import numpy as np

def angle_between_vectors(vector1: Vector2D, vector2: Vector2D) -> Angle:
    """Calculate angle between two vectors."""
    # Normalize vectors
    v1_norm = np.linalg.norm(vector1)
    v2_norm = np.linalg.norm(vector2)

    if v1_norm == 0 or v2_norm == 0:
        raise ValueError("Zero-length vector")

    v1_unit = vector1 / v1_norm
    v2_unit = vector2 / v2_norm

    # Dot product approach
    dot_product = np.dot(v1_unit, v2_unit)

    # Clamp to [-1, 1] to handle floating point errors
    dot_product = np.clip(dot_product, -1.0, 1.0)

    # Calculate angle in radians, convert to degrees
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)

    return float(angle_deg)
```

**Validation**: Unit tests for basic angle calculations pass.

### Step 3: Implement Geometry Utilities
In `src/analysis/angles.py`, add geometric helper functions.

**Functions to implement**:
- `line_slope` - handle vertical lines (slope = infinity)
- `point_to_line_distance` - perpendicular distance formula
- `project_point_onto_line` - vector projection
- `line_intersection` - solve system of linear equations

**Code pattern for point_to_line_distance**:
```python
def point_to_line_distance(
    point: Point2D,
    line_start: Point2D,
    line_end: Point2D
) -> float:
    """Calculate perpendicular distance from point to line."""
    # Convert to numpy arrays
    p = np.array(point)
    l1 = np.array(line_start)
    l2 = np.array(line_end)

    # Line direction vector
    line_vec = l2 - l1
    line_len = np.linalg.norm(line_vec)

    if line_len == 0:
        # Line is actually a point
        return float(np.linalg.norm(p - l1))

    # Vector from line start to point
    point_vec = p - l1

    # Cross product in 2D (gives area of parallelogram)
    cross = line_vec[0] * point_vec[1] - line_vec[1] * point_vec[0]

    # Distance = area / base
    distance = abs(cross) / line_len

    return float(distance)
```

**Validation**: Geometry utility tests pass.

### Step 4: Implement JointAngleCalculator
In `src/analysis/joint_angles.py`, create the joint angle calculator class.

**Key requirements**:
- Support both left-handed and right-handed golfers
- Use core angle functions from angles.py
- Provide typical range information for each measurement
- Clear documentation of what each angle represents

**Implementation approach**:
- Most joint angles use `angle_between_points`
- Spine angle uses `angle_from_vertical`
- Store handedness to select appropriate landmarks

**Code pattern**:
```python
from .angles import angle_between_points, angle_from_vertical

class JointAngleCalculator:
    def __init__(self, handedness: str = "right"):
        if handedness not in ["right", "left"]:
            raise ValueError(f"Invalid handedness: {handedness}")
        self.handedness = handedness

    def elbow_angle(self, shoulder, elbow, wrist):
        """Calculate elbow flexion angle."""
        return angle_between_points(shoulder, elbow, wrist)

    def spine_angle(self, shoulder, hip, reference_vertical=None):
        """Calculate spine tilt from vertical."""
        spine_angle = angle_from_vertical(hip, shoulder)
        return abs(spine_angle)  # Return positive value
```

**Validation**: Joint angle tests pass.

### Step 5: Implement ClubAngleCalculator
In `src/analysis/club_angles.py`, create the club angle calculator class.

**Key requirements**:
- Calculate shaft angles relative to various references
- Support custom reference lines (ground, target line)
- Provide typical ranges for club angles

**Implementation approach**:
- Use `angle_from_horizontal` for shaft to ground
- Use `angle_from_vertical` for shaft to vertical
- Use vector angle calculations for shaft to target line

**Validation**: Club angle tests pass.

### Step 6: Write Comprehensive Tests for Core Angles
In `tests/test_angles.py`, create tests for all core functions.

**Test categories**:
1. **Basic angle calculations**
   - Known angle values (30°, 45°, 60°, 90°)
   - Right angles
   - Straight lines (180°)

2. **Edge cases**
   - Zero-length vectors
   - Collinear points
   - Duplicate points
   - Parallel lines

3. **Angle normalization**
   - Different range types
   - Negative angles
   - Angles > 360°

4. **Geometry utilities**
   - Distance calculations
   - Perpendicular distance
   - Line intersections (parallel, perpendicular, skew)

**Test pattern**:
```python
import pytest
import numpy as np
from src.analysis.angles import angle_between_points

def test_right_angle():
    """Test 90-degree angle calculation."""
    p1 = (0, 0)
    vertex = (1, 0)
    p2 = (1, 1)

    angle = angle_between_points(p1, vertex, p2)
    assert abs(angle - 90.0) < 0.01

def test_zero_length_vector_raises_error():
    """Test that zero-length vector raises ValueError."""
    with pytest.raises(ValueError, match="Zero-length"):
        angle_between_points((0, 0), (0, 0), (1, 1))
```

**Validation**: `pytest tests/test_angles.py -v` passes all tests.

### Step 7: Write Tests for Joint Angles
In `tests/test_joint_angles.py`, test joint angle calculations.

**Test cases**:
- Known joint configurations (full extension, 90° flex)
- Left vs right handedness
- Typical golf swing positions
- Spine angle calculations
- Wrist hinge measurements

**Validation**: `pytest tests/test_joint_angles.py -v` passes.

### Step 8: Write Tests for Club Angles
In `tests/test_club_angles.py`, test club angle calculations.

**Test cases**:
- Shaft angle at address (~60-70°)
- Vertical shaft (putter)
- Horizontal club (top of backswing)
- Swing plane angles
- Custom reference lines

**Validation**: `pytest tests/test_club_angles.py -v` passes.

### Step 9: Package Configuration
In `src/analysis/__init__.py`, export public API.

```python
"""Analysis utilities for golf swing measurements."""

from .angles import (
    angle_between_points,
    angle_between_vectors,
    angle_from_horizontal,
    angle_from_vertical,
    normalize_angle,
    degrees_to_radians,
    radians_to_degrees,
    distance_between_points,
    line_slope,
    point_to_line_distance,
    project_point_onto_line,
    line_intersection,
)
from .joint_angles import JointAngleCalculator, BodyLandmark
from .club_angles import ClubAngleCalculator

__all__ = [
    # Core angles
    'angle_between_points',
    'angle_between_vectors',
    'angle_from_horizontal',
    'angle_from_vertical',
    'normalize_angle',
    'degrees_to_radians',
    'radians_to_degrees',
    # Geometry
    'distance_between_points',
    'line_slope',
    'point_to_line_distance',
    'project_point_onto_line',
    'line_intersection',
    # Calculators
    'JointAngleCalculator',
    'ClubAngleCalculator',
    'BodyLandmark',
]
```

**Validation**: Can import from package.

### Step 10: Performance Testing
Create performance tests to ensure <1ms per calculation.

**Test approach**:
```python
import time
import numpy as np

def test_angle_calculation_performance():
    """Test that angle calculation is fast (<1ms)."""
    # Generate test data
    p1 = (0, 0)
    vertex = (1, 0)
    p2 = (1, 1)

    # Measure time for 1000 calculations
    start = time.time()
    for _ in range(1000):
        angle = angle_between_points(p1, vertex, p2)
    elapsed = time.time() - start

    avg_time = elapsed / 1000
    assert avg_time < 0.001, f"Too slow: {avg_time*1000:.2f}ms"
```

**Validation**: Performance tests pass.

### Step 11: Documentation and Examples
Create usage examples and update documentation.

**Example script** (`examples/angle_calculations.py`):
```python
"""Example usage of angle calculation utilities."""

from src.analysis import (
    angle_between_points,
    JointAngleCalculator,
    ClubAngleCalculator
)

# Example 1: Calculate knee flex angle
hip = (320, 200)
knee = (340, 300)
ankle = (350, 400)

knee_angle = angle_between_points(hip, knee, ankle)
print(f"Knee flex angle: {knee_angle:.1f}°")

# Example 2: Using JointAngleCalculator
calc = JointAngleCalculator(handedness="right")

shoulder = (300, 150)
elbow = (350, 250)
wrist = (380, 280)

elbow_angle = calc.elbow_angle(shoulder, elbow, wrist)
print(f"Elbow angle: {elbow_angle:.1f}°")

# Example 3: Club shaft angle
club_calc = ClubAngleCalculator()
grip = (380, 280)
club_head = (420, 380)

shaft_angle = club_calc.shaft_angle_to_ground(grip, club_head)
print(f"Shaft angle: {shaft_angle:.1f}° from ground")
```

**Validation**: Example script runs successfully.

### Step 12: Integration with Existing Code
Verify the module integrates well with existing video module.

**Integration test**:
```python
from src.video import VideoLoader, FrameExtractor
from src.analysis import angle_between_points

# Load video and extract frame
with VideoLoader("tests/test_data/test_swing.mp4") as loader:
    extractor = FrameExtractor(loader)
    frame = extractor.extract_frame(0)

    # Simulate detected points (in future, from pose detector)
    p1 = (320, 200)
    vertex = (340, 300)
    p2 = (350, 400)

    angle = angle_between_points(p1, vertex, p2)
    print(f"Angle: {angle:.1f}°")
```

**Validation**: Integration works smoothly.

## 4. Validation Gates

### After Step 2
```bash
python -c "from src.analysis.angles import angle_between_points; print('Core angles import OK')"
pytest tests/test_angles.py::test_angle_between_points -v
```
**Expected**: Import succeeds, basic tests pass.

### After Step 4
```bash
pytest tests/test_joint_angles.py -v
```
**Expected**: All joint angle tests pass.

### After Step 5
```bash
pytest tests/test_club_angles.py -v
```
**Expected**: All club angle tests pass.

### Full Test Suite
```bash
pytest tests/test_angles.py tests/test_joint_angles.py tests/test_club_angles.py -v
```
**Expected**: All tests pass.

### Code Coverage
```bash
pytest tests/test_angles.py tests/test_joint_angles.py tests/test_club_angles.py \
  --cov=src/analysis --cov-report=term-missing
```
**Expected**: >90% coverage for all analysis modules.

### Linting
```bash
flake8 src/analysis/ --max-line-length=100
mypy src/analysis/ --ignore-missing-imports
```
**Expected**: No errors.

### Performance Benchmark
```bash
pytest tests/test_angles.py::test_performance -v
```
**Expected**: All calculations <1ms.

## 5. Success Criteria

### Functional Requirements
- ✅ Can calculate angle between three points accurately
- ✅ Can calculate angle between two vectors
- ✅ Can calculate angles relative to horizontal/vertical
- ✅ Can calculate joint angles from landmark coordinates
- ✅ Can calculate club shaft angles
- ✅ Handles edge cases gracefully (raises ValueError with clear messages)
- ✅ Supports both left and right-handed golfers

### Accuracy Requirements
- ✅ All angle measurements accurate to ±0.1 degrees
- ✅ Validated against known geometric configurations
- ✅ Cross-validated with multiple test cases

### Performance Requirements
- ✅ Each angle calculation completes in <1ms
- ✅ No memory leaks or excessive allocations
- ✅ Efficient NumPy operations

### Quality Requirements
- ✅ All tests pass with >90% coverage
- ✅ No linting errors (flake8, mypy)
- ✅ All public functions have docstrings
- ✅ Proper error handling with clear messages

### Example Usage

```python
from src.analysis import (
    angle_between_points,
    JointAngleCalculator,
    ClubAngleCalculator,
    BodyLandmark
)

# Basic angle calculation
p1 = (0, 0)
vertex = (1, 0)
p2 = (1, 1)
angle = angle_between_points(p1, vertex, p2)
# Output: 90.0

# Joint angle measurement
joint_calc = JointAngleCalculator(handedness="right")

# Knee flex
hip = (320, 200)
knee = (340, 300)
ankle = (350, 400)
knee_flex = joint_calc.knee_angle(hip, knee, ankle)
# Output: ~160.0 (good address position)

# Spine tilt
shoulder = (300, 150)
hip = (320, 200)
spine_tilt = joint_calc.spine_angle(shoulder, hip)
# Output: ~35.0 degrees (typical for iron shot)

# Club angle
club_calc = ClubAngleCalculator()
grip = (380, 280)
club_head = (420, 380)
shaft_angle = club_calc.shaft_angle_to_ground(grip, club_head)
# Output: ~65.0 degrees (typical 7-iron)

# Typical ranges
ranges = joint_calc.get_typical_ranges()
# Output: {
#   'knee_flex_address': (140, 160),
#   'spine_tilt_address': (30, 40),
#   'elbow_extension_address': (160, 175),
#   ...
# }
```

## 6. Code Examples and Patterns

### Pattern 1: Error Handling for Invalid Inputs

```python
def angle_between_points(point1, vertex, point2):
    """Calculate angle with proper error handling."""
    # Convert to numpy arrays
    p1 = np.array(point1, dtype=float)
    v = np.array(vertex, dtype=float)
    p2 = np.array(point2, dtype=float)

    # Create vectors
    vec1 = p1 - v
    vec2 = p2 - v

    # Check for zero-length vectors
    if np.linalg.norm(vec1) == 0:
        raise ValueError("Point1 and vertex are identical")
    if np.linalg.norm(vec2) == 0:
        raise ValueError("Point2 and vertex are identical")

    # Calculate angle
    return angle_between_vectors(vec1, vec2)
```

### Pattern 2: Flexible Input Types

```python
def distance_between_points(point1: Point2D, point2: Point2D) -> float:
    """Accept both tuples and numpy arrays."""
    p1 = np.array(point1, dtype=float)
    p2 = np.array(point2, dtype=float)

    return float(np.linalg.norm(p2 - p1))
```

### Pattern 3: Angle Normalization

```python
def normalize_angle(angle: Angle, range_type: str = "0-360") -> Angle:
    """Normalize to different ranges."""
    if range_type == "0-360":
        return angle % 360.0
    elif range_type == "-180-180":
        angle = angle % 360.0
        return angle - 360.0 if angle > 180.0 else angle
    elif range_type == "0-180":
        angle = abs(angle) % 360.0
        return min(angle, 360.0 - angle)
    else:
        raise ValueError(f"Invalid range_type: {range_type}")
```

### Pattern 4: Logging for Debugging

```python
import logging

logger = logging.getLogger(__name__)

def swing_plane_angle(self, hands_address, hands_top, ball):
    """Calculate swing plane angle with logging."""
    logger.debug(
        f"Calculating swing plane: address={hands_address}, "
        f"top={hands_top}, ball={ball}"
    )

    # Create line from ball through hands at address
    plane_angle = angle_from_horizontal(ball, hands_address)

    logger.info(f"Swing plane angle: {plane_angle:.1f}°")
    return plane_angle
```

### Pattern 5: Type Annotations

```python
from typing import Tuple, Optional
import numpy as np
from numpy.typing import NDArray

Point2D = Union[Tuple[float, float], NDArray[np.float64]]

def angle_from_horizontal(
    line_start: Point2D,
    line_end: Point2D
) -> float:
    """Fully typed function signature."""
    ...
```

## 7. Additional Implementation Notes

### Floating Point Precision

When using `np.arccos`, clamp the dot product to avoid domain errors:

```python
dot_product = np.dot(v1_unit, v2_unit)
dot_product = np.clip(dot_product, -1.0, 1.0)
angle_rad = np.arccos(dot_product)
```

### Coordinate System Consistency

- **X-axis**: Horizontal, increases to the right
- **Y-axis**: Vertical, increases downward (image coordinates)
- **Angles**: Measured counterclockwise from reference
- **Positive angles**: Counterclockwise rotation
- **Negative angles**: Clockwise rotation

### Golf-Specific Conventions

- **Spine angle**: Always positive, measured from vertical
- **Knee flex**: 180° = full extension, smaller = more flex
- **Club shaft**: Measured from ground, 90° = vertical
- **Handedness**: Affects which shoulder/hip/knee to use

### Test Data Generation

Create realistic test data using known geometric configurations:

```python
def create_right_angle_points():
    """Create three points forming exact 90° angle."""
    return (0, 0), (1, 0), (1, 1)

def create_knee_flex_160_degrees():
    """Create typical address position knee angle."""
    # Use law of cosines to compute third point
    # given two segments and desired angle
    ...
```

### Performance Optimization

- Use NumPy vectorized operations
- Avoid Python loops where possible
- Reuse normalized vectors
- Cache expensive calculations if called repeatedly

---

## Summary Checklist

- [ ] All core angle functions implemented with type hints
- [ ] All geometry utilities implemented
- [ ] JointAngleCalculator class with all joint measurements
- [ ] ClubAngleCalculator class with all club measurements
- [ ] All functions have Google-style docstrings
- [ ] Comprehensive test suite (>90% coverage)
- [ ] All edge cases handled with clear error messages
- [ ] Performance requirements met (<1ms per calculation)
- [ ] Linting passes (flake8, mypy)
- [ ] Integration with existing video module verified
- [ ] Example usage documented
- [ ] Package exports properly configured

**End of PRP**
