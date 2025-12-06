# Feature Request: Angle Calculation Utilities

## FEATURE:
Create the angle calculation utilities module. This should:

1. Calculate angles between points, lines, and vectors
2. Measure joint angles (shoulder, elbow, knee, hip, spine)
3. Calculate club shaft angles relative to ground/vertical
4. Support both 2D (pixel coordinates) and normalized coordinates
5. Handle edge cases (parallel lines, zero-length vectors)
6. Provide utility functions for common golf swing measurements

## TECHNICAL REQUIREMENTS:

### AngleCalculator class
- Calculate angle between three points (vertex at middle point)
- Calculate angle between two vectors
- Calculate angle between two lines
- Convert between degrees and radians
- Normalize angles to specific ranges (0-360, -180 to 180, 0-180)

### JointAngleCalculator class
- Calculate joint angles from landmark points:
  - Shoulder angle (upper arm to torso)
  - Elbow angle (forearm to upper arm)
  - Knee angle (lower leg to upper leg)
  - Hip angle (torso to upper leg)
  - Spine angle (relative to vertical)
  - Wrist hinge angle

### ClubAngleCalculator class
- Calculate club shaft angle relative to:
  - Ground (horizontal)
  - Vertical
  - Target line
- Calculate lie angle (club head to shaft)
- Calculate swing plane angle

### Utility Functions
- Distance between two points
- Slope of a line between two points
- Perpendicular distance from point to line
- Project point onto line
- Find intersection of two lines

## FILES TO CREATE:
- src/analysis/__init__.py
- src/analysis/angles.py (AngleCalculator, utility functions)
- src/analysis/joint_angles.py (JointAngleCalculator)
- src/analysis/club_angles.py (ClubAngleCalculator)
- tests/test_angles.py
- tests/test_joint_angles.py
- tests/test_club_angles.py

## EXAMPLES:
Common usage patterns for golf swing analysis

## DOCUMENTATION:
- NumPy documentation for vector operations
- Geometry formulas for angle calculations

## SUCCESS CRITERIA:
1. Can calculate angle between three points accurately
2. Can calculate joint angles from landmark coordinates
3. Can calculate club angles relative to reference lines
4. All angle measurements accurate to ±0.1 degrees
5. Handles edge cases without crashing (parallel lines, zero vectors)
6. All tests pass with >90% coverage
7. Performance: <1ms per angle calculation

## DATA STRUCTURES:
- Point: Tuple[float, float] or np.ndarray for (x, y) coordinates
- Vector: np.ndarray for 2D vectors
- Line: Defined by two points or point + slope
- Angle: float in degrees (primary) with conversion to radians

## KEY MEASUREMENTS FOR GOLF SWING:
- Spine angle at address: ~30-40 degrees from vertical
- Knee flex at address: ~140-160 degrees
- Arm extension at address: ~160-170 degrees
- Wrist hinge at top: ~90 degrees
- Club shaft angle at address: ~60-70 degrees from ground
- Swing plane angle: varies by club, typically 45-60 degrees

## OTHER CONSIDERATIONS:
- All calculations should work with pixel coordinates from video frames
- Support for left-handed and right-handed golfers
- Angles measured consistently (clockwise/counterclockwise)
- Return None or raise exception for invalid inputs (document which approach)
