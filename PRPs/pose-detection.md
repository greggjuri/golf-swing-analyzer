# PRP: Pose Detection Integration

## Overview
Integrate MediaPipe pose detection to identify body landmarks in golf swing videos. This enables analysis of body positioning, joint angles, and swing mechanics.

## Objectives
1. Detect 33 body landmarks using MediaPipe Pose
2. Extract landmark positions with confidence scores
3. Track poses across frames with temporal smoothing
4. Calculate key joint angles and body metrics
5. Provide robust error handling for detection failures

## Architecture

### Module Structure
```
src/pose/
├── __init__.py           # Module exports
├── detector.py           # PoseDetector - MediaPipe wrapper
├── landmarks.py          # Landmark definitions and utilities
├── extractor.py          # LandmarkExtractor - position/angle extraction
└── tracker.py            # PoseTracker - multi-frame smoothing
```

### Key Components

#### 1. PoseDetector (detector.py)
MediaPipe integration for single-frame detection.

**Responsibilities:**
- Initialize MediaPipe Pose model
- Process frames and detect landmarks
- Return normalized landmark positions
- Provide visibility and confidence scores
- Handle detection failures gracefully

**Interface:**
```python
class PoseDetector:
    def __init__(
        self,
        model_complexity: int = 1,      # 0=Lite, 1=Full, 2=Heavy
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        enable_segmentation: bool = False
    ):
        """Initialize MediaPipe Pose detector."""

    def detect(self, frame: np.ndarray) -> Optional[PoseResult]:
        """Detect pose in single frame.

        Returns:
            PoseResult with landmarks, or None if no pose detected
        """

    def close(self):
        """Release MediaPipe resources."""
```

**PoseResult:**
```python
@dataclass
class PoseResult:
    landmarks: Dict[PoseLandmark, LandmarkPoint]  # 33 landmarks
    world_landmarks: Dict[PoseLandmark, LandmarkPoint]  # 3D coordinates
    timestamp: float
    detection_confidence: float

    def is_visible(self, landmark: PoseLandmark) -> bool:
        """Check if landmark is visible."""

    def get_position(self, landmark: PoseLandmark) -> Tuple[float, float]:
        """Get 2D position (normalized 0-1)."""
```

#### 2. Landmarks (landmarks.py)
Landmark definitions and groupings.

**PoseLandmark Enum:**
```python
class PoseLandmark(Enum):
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
```

**Landmark Groups:**
```python
POSE_CONNECTIONS = [
    (NOSE, LEFT_EYE_INNER),
    (LEFT_EYE_INNER, LEFT_EYE),
    # ... full skeleton connections
]

BODY_SEGMENTS = {
    'torso': [LEFT_SHOULDER, RIGHT_SHOULDER, RIGHT_HIP, LEFT_HIP],
    'left_arm': [LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST],
    'right_arm': [RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST],
    'left_leg': [LEFT_HIP, LEFT_KNEE, LEFT_ANKLE],
    'right_leg': [RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE],
}
```

#### 3. LandmarkExtractor (extractor.py)
Extract positions, angles, and metrics from landmarks.

**Responsibilities:**
- Convert normalized coordinates to pixel positions
- Calculate joint angles
- Measure body segment lengths
- Compute center points and orientations

**Interface:**
```python
class LandmarkExtractor:
    def __init__(self, frame_width: int, frame_height: int):
        """Initialize extractor with frame dimensions."""

    def get_pixel_position(
        self,
        pose_result: PoseResult,
        landmark: PoseLandmark
    ) -> Point2D:
        """Convert normalized position to pixels."""

    def get_joint_angle(
        self,
        pose_result: PoseResult,
        joint: PoseLandmark,
        reference1: PoseLandmark,
        reference2: PoseLandmark
    ) -> Optional[float]:
        """Calculate angle at joint formed by three landmarks.

        Example: elbow angle using shoulder-elbow-wrist
        """

    def get_body_center(self, pose_result: PoseResult) -> Point2D:
        """Calculate center point between hips."""

    def get_shoulder_line(self, pose_result: PoseResult) -> Optional[Line2D]:
        """Get line through shoulders."""

    def get_hip_line(self, pose_result: PoseResult) -> Optional[Line2D]:
        """Get line through hips."""

    def get_spine_angle(self, pose_result: PoseResult) -> Optional[float]:
        """Calculate spine angle from vertical."""
```

#### 4. PoseTracker (tracker.py)
Multi-frame tracking with temporal smoothing.

**Responsibilities:**
- Track poses across multiple frames
- Smooth landmark positions using moving average
- Interpolate missing detections
- Maintain pose history

**Interface:**
```python
class PoseTracker:
    def __init__(
        self,
        smoothing_window: int = 5,
        max_gap_frames: int = 10,
        confidence_threshold: float = 0.5
    ):
        """Initialize pose tracker."""

    def update(
        self,
        frame_number: int,
        pose_result: Optional[PoseResult]
    ) -> Optional[PoseResult]:
        """Update tracker with new detection.

        Returns smoothed pose result or interpolated result if detection failed.
        """

    def get_history(
        self,
        landmark: PoseLandmark,
        num_frames: int = 10
    ) -> List[Point2D]:
        """Get position history for landmark."""

    def reset(self):
        """Clear tracking history."""
```

## Data Structures

### LandmarkPoint
```python
@dataclass
class LandmarkPoint:
    x: float              # Normalized 0-1 (or pixel coords)
    y: float              # Normalized 0-1 (or pixel coords)
    z: float              # Depth (for world landmarks)
    visibility: float     # 0-1 confidence
    presence: float       # 0-1 likelihood of being in frame
```

## Dependencies

### New Requirements
```
mediapipe>=0.10.0    # Pose detection
```

### MediaPipe Model
- Download happens automatically on first use
- Model file: ~30MB
- Supports CPU and GPU inference

## Golf-Specific Metrics

The system should support calculating golf-specific measurements:

1. **Address Position**
   - Spine angle at address
   - Hip-shoulder alignment
   - Knee flex angle
   - Weight distribution (left/right foot)

2. **Backswing**
   - Shoulder rotation
   - Hip rotation
   - X-Factor (shoulder-hip separation)
   - Left arm extension
   - Head stability

3. **Impact**
   - Hip rotation at impact
   - Spine angle at impact
   - Weight transfer
   - Head position

4. **Follow-through**
   - Hip rotation through impact
   - Shoulder rotation
   - Balance/finish position

## Error Handling

1. **No Pose Detected**
   - Return None from detector
   - Tracker attempts interpolation
   - Log warning if gap exceeds threshold

2. **Low Confidence Landmarks**
   - Filter landmarks below visibility threshold
   - Use interpolation from adjacent frames
   - Provide partial results with available landmarks

3. **Occlusion**
   - MediaPipe handles partial occlusion
   - Use world landmarks for 3D reasoning
   - Fallback to tracking-based prediction

## Performance Considerations

1. **Model Complexity**
   - Lite (0): Fast, less accurate, ~33ms/frame
   - Full (1): Balanced, default, ~50ms/frame
   - Heavy (2): Most accurate, slower, ~100ms/frame

2. **Optimization**
   - Process at reduced resolution for speed
   - Use tracking mode for video (faster than detection)
   - Batch process frames when real-time not needed

3. **Memory**
   - Limit pose history length
   - Clear old tracking data
   - Release MediaPipe resources when done

## Testing Strategy

### Unit Tests

1. **PoseDetector**
   - Detect pose in synthetic image
   - Handle frames with no person
   - Return correct landmark count
   - Validate confidence scores
   - Test model complexity options

2. **LandmarkExtractor**
   - Convert normalized to pixel coordinates
   - Calculate joint angles correctly
   - Handle missing landmarks
   - Compute body center
   - Calculate spine angle

3. **PoseTracker**
   - Smooth landmark positions
   - Interpolate gaps
   - Maintain correct history length
   - Reset properly

4. **Landmarks**
   - Enum values correct
   - Connection definitions valid
   - Body segment groups complete

### Integration Tests

1. **Full Pipeline**
   - Detect → Extract → Track workflow
   - Process video sequence
   - Handle detection failures
   - Verify smoothing improves stability

2. **Edge Cases**
   - Person enters/exits frame
   - Multiple people in frame
   - Extreme poses
   - Low lighting conditions

### Test Fixtures

1. **Test Images**
   - Person in address position
   - Person in backswing
   - Person at impact
   - Empty frame (no person)

2. **Synthetic Data**
   - Known landmark positions
   - Test joint angle calculations
   - Verify coordinate transformations

## Usage Examples

### Basic Detection
```python
from src.pose import PoseDetector

detector = PoseDetector(model_complexity=1)

# Process frame
result = detector.detect(frame)

if result:
    # Get specific landmark
    left_shoulder = result.get_position(PoseLandmark.LEFT_SHOULDER)

    # Check visibility
    if result.is_visible(PoseLandmark.LEFT_ELBOW):
        print("Left elbow visible")

detector.close()
```

### Extract Joint Angles
```python
from src.pose import PoseDetector, LandmarkExtractor, PoseLandmark

detector = PoseDetector()
extractor = LandmarkExtractor(frame.shape[1], frame.shape[0])

result = detector.detect(frame)

if result:
    # Calculate elbow angle
    elbow_angle = extractor.get_joint_angle(
        result,
        PoseLandmark.LEFT_ELBOW,
        PoseLandmark.LEFT_SHOULDER,
        PoseLandmark.LEFT_WRIST
    )

    # Get spine angle
    spine_angle = extractor.get_spine_angle(result)

    print(f"Elbow: {elbow_angle:.1f}°, Spine: {spine_angle:.1f}°")
```

### Track Across Frames
```python
from src.pose import PoseDetector, PoseTracker
from src.video import VideoLoader

detector = PoseDetector()
tracker = PoseTracker(smoothing_window=5)

with VideoLoader("swing.mp4") as video:
    for i in range(video.get_metadata().frame_count):
        frame = video.get_frame_at(i)

        # Detect
        result = detector.detect(frame)

        # Track (smooths and interpolates)
        smoothed = tracker.update(i, result)

        if smoothed:
            print(f"Frame {i}: {len(smoothed.landmarks)} landmarks")

detector.close()
```

### Golf Swing Analysis
```python
from src.pose import PoseDetector, LandmarkExtractor, PoseLandmark

detector = PoseDetector()
extractor = LandmarkExtractor(1920, 1080)

result = detector.detect(address_frame)

# Address position metrics
spine_angle = extractor.get_spine_angle(result)
hip_line = extractor.get_hip_line(result)
shoulder_line = extractor.get_shoulder_line(result)

# Knee flex
left_knee_angle = extractor.get_joint_angle(
    result,
    PoseLandmark.LEFT_KNEE,
    PoseLandmark.LEFT_HIP,
    PoseLandmark.LEFT_ANKLE
)

print(f"Spine: {spine_angle:.1f}°")
print(f"Left knee flex: {180 - left_knee_angle:.1f}°")
```

## Success Criteria

1. **Accuracy**
   - Detect pose in >95% of frames with person present
   - Landmark positions accurate within 5 pixels at 1080p
   - Joint angles accurate within 3 degrees

2. **Performance**
   - Process 1080p frame in <100ms (model complexity=1)
   - Support real-time video analysis (>15 fps)

3. **Robustness**
   - Handle partial occlusion gracefully
   - Interpolate gaps up to 10 frames
   - Work with various lighting conditions

4. **Coverage**
   - 95%+ test coverage for all modules
   - All edge cases tested
   - Integration tests for full pipeline

5. **Documentation**
   - Clear API documentation
   - Usage examples for common scenarios
   - Demo script showing golf swing analysis

## Future Enhancements

1. **3D Pose Estimation**
   - Use world landmarks for depth
   - Calculate 3D joint angles
   - Estimate swing plane in 3D

2. **Pose Classification**
   - Classify swing phases (address, backswing, etc.)
   - Detect common swing faults
   - Compare to ideal pose models

3. **Multi-Person**
   - Handle multiple golfers in frame
   - Track specific person across frames
   - Support side-by-side comparison

4. **Custom Training**
   - Fine-tune on golf-specific poses
   - Improve accuracy for golf positions
   - Add golf-specific landmarks
