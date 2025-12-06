# PRP: Club Tracking System

## Overview
Implement a computer vision system to detect and track the golf club (shaft and head) in video frames using edge detection and Hough line transform.

## Context
- We have video loading and frame extraction working
- Angle calculation utilities are available for shaft angle analysis
- Need to detect club position/orientation for swing analysis
- Will use OpenCV (already a dependency)

## Requirements

### Functional Requirements
1. **Club Shaft Detection**
   - Detect club shaft as a line in the frame
   - Use Canny edge detection + Hough line transform
   - Filter lines by length, angle, and position
   - Return shaft endpoints (grip, club head connection)

2. **Club Head Detection**
   - Detect club head position (circular/elliptical object)
   - Use edge detection + contour finding or Hough circles
   - Return center point and approximate radius

3. **Frame Preprocessing**
   - Convert to grayscale
   - Apply Gaussian blur for noise reduction
   - Adjust contrast/brightness if needed
   - ROI (region of interest) cropping to focus on swing area

4. **Multi-frame Tracking**
   - Track club across multiple frames
   - Use temporal consistency (previous frame context)
   - Handle occlusion (club behind body)
   - Return confidence scores

5. **Configuration**
   - Adjustable detection parameters (thresholds, line length, angles)
   - Debug mode to visualize intermediate steps
   - Presets for different video qualities

### Non-Functional Requirements
1. **Performance**: Process frames at 10+ fps on typical hardware
2. **Accuracy**: Detect shaft in 80%+ of frames where visible
3. **Robustness**: Handle varying lighting, backgrounds, club types
4. **Test Coverage**: >85% code coverage
5. **Code Quality**: Pass flake8, mypy validation

## Technical Design

### Module Structure
```
src/detection/
├── __init__.py
├── club_detector.py      # Main ClubDetector class
├── preprocessing.py      # Image preprocessing utilities
└── tracking.py          # Multi-frame tracking logic
```

### Core Classes

#### 1. ClubDetector
```python
class ClubDetector:
    """Detect golf club shaft and head in video frames.

    Uses edge detection and Hough transform for shaft detection,
    contour/circle detection for club head.

    Example:
        detector = ClubDetector()
        result = detector.detect(frame)
        if result.shaft_detected:
            print(f"Shaft: {result.shaft_line}")
    """

    def __init__(
        self,
        canny_low: int = 50,
        canny_high: int = 150,
        hough_threshold: int = 50,
        min_line_length: int = 100,
        max_line_gap: int = 10,
        debug: bool = False
    ):
        """Initialize detector with parameters."""

    def detect(self, frame: np.ndarray) -> DetectionResult:
        """Detect club in single frame.

        Args:
            frame: Input frame (BGR format from OpenCV)

        Returns:
            DetectionResult with shaft line, club head, confidence
        """

    def detect_shaft(
        self,
        edges: np.ndarray,
        roi: Optional[tuple] = None
    ) -> Optional[Line]:
        """Detect club shaft using Hough line transform.

        Args:
            edges: Edge-detected image
            roi: Optional (x, y, w, h) region of interest

        Returns:
            Line (x1, y1, x2, y2) or None if not detected
        """

    def detect_club_head(
        self,
        frame: np.ndarray,
        shaft_line: Optional[Line] = None
    ) -> Optional[ClubHead]:
        """Detect club head position.

        Args:
            frame: Input frame
            shaft_line: Optional shaft line to constrain search

        Returns:
            ClubHead with center point and radius, or None
        """
```

#### 2. DetectionResult
```python
@dataclass
class DetectionResult:
    """Result from club detection."""
    shaft_detected: bool
    shaft_line: Optional[Line]  # (x1, y1, x2, y2)
    shaft_angle: Optional[float]  # Angle from horizontal in degrees
    club_head_detected: bool
    club_head_center: Optional[Point2D]
    club_head_radius: Optional[float]
    confidence: float  # 0.0 to 1.0
    debug_image: Optional[np.ndarray]  # If debug=True
```

#### 3. FramePreprocessor
```python
class FramePreprocessor:
    """Preprocess frames for club detection."""

    def __init__(
        self,
        blur_kernel: int = 5,
        roi: Optional[tuple] = None
    ):
        """Initialize preprocessor."""

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Apply preprocessing pipeline.

        Args:
            frame: Input BGR frame

        Returns:
            Grayscale, blurred, optionally cropped frame
        """

    def apply_roi(self, frame: np.ndarray, roi: tuple) -> np.ndarray:
        """Extract region of interest."""

    def enhance_contrast(self, frame: np.ndarray) -> np.ndarray:
        """Apply CLAHE for contrast enhancement."""
```

#### 4. ClubTracker
```python
class ClubTracker:
    """Track club across multiple frames using temporal consistency."""

    def __init__(self, smoothing_window: int = 3):
        """Initialize tracker with smoothing window."""

    def update(self, detection: DetectionResult) -> DetectionResult:
        """Update tracker with new detection.

        Uses previous detections to smooth results and fill gaps.

        Args:
            detection: Current frame detection

        Returns:
            Smoothed/refined detection result
        """

    def reset(self):
        """Reset tracking history."""
```

### Type Definitions
```python
# Basic types
Line = Tuple[int, int, int, int]  # (x1, y1, x2, y2)
Point2D = Tuple[float, float]  # Already defined in analysis module

@dataclass
class ClubHead:
    """Club head detection info."""
    center: Point2D
    radius: float
    confidence: float
```

### Algorithm Details

#### Shaft Detection Pipeline
1. **Preprocessing**
   - Convert to grayscale
   - Apply Gaussian blur (5x5 kernel)
   - Optional: Apply ROI mask
   - Optional: CLAHE for contrast

2. **Edge Detection**
   - Canny edge detection (low=50, high=150)
   - Morphological operations to clean up edges

3. **Line Detection**
   - Probabilistic Hough Line Transform
   - Filter by:
     - Length (min 100 pixels)
     - Angle (exclude nearly horizontal/vertical lines that are likely background)
     - Position (prioritize lines in expected club region)
   - Select best candidate based on length, straightness, position

4. **Validation**
   - Check line doesn't overlap with detected body (future integration)
   - Verify angle is reasonable for golf club (not horizontal)
   - Assign confidence based on edge strength along line

#### Club Head Detection Pipeline
1. **Region Definition**
   - If shaft detected: search near shaft endpoint
   - Otherwise: search lower portion of frame

2. **Detection Methods** (try in order)
   - **Method A**: Hough Circle Transform
     - Detect circular objects
     - Filter by size (typical club head 20-50px radius)
   - **Method B**: Contour Detection
     - Find closed contours
     - Filter by circularity and size
     - Use bounding circle

3. **Validation**
   - Check proximity to shaft endpoint
   - Verify size is reasonable
   - Assign confidence

### Performance Considerations
- Use ROI to reduce search space (2x faster)
- Cache preprocessed frames for multi-pass detection
- Use NumPy vectorization for line filtering
- Optimize Hough parameters for speed vs accuracy tradeoff

### Error Handling
- Return `shaft_detected=False` if no valid lines found
- Log warnings for unexpected conditions
- Raise ValueError for invalid input (wrong image format, empty frame)
- Handle edge cases (all-black frames, extremely bright/dark)

## Implementation Steps

1. ✅ Create module structure and __init__.py
2. ✅ Implement FramePreprocessor class
3. ✅ Implement basic ClubDetector class (shaft detection only)
4. ✅ Add club head detection to ClubDetector
5. ✅ Implement DetectionResult dataclass and types
6. ✅ Add line filtering and selection logic
7. ✅ Implement ClubTracker for multi-frame tracking
8. ✅ Add debug visualization mode
9. ✅ Write unit tests for preprocessing
10. ✅ Write unit tests for shaft detection
11. ✅ Write unit tests for club head detection
12. ✅ Write integration tests with real video frames
13. ✅ Create demo script
14. ✅ Performance testing and optimization
15. ✅ Documentation and examples

## Success Criteria

### Must Have
- [x] ClubDetector class detects shaft in test frames
- [x] Returns shaft line as (x1, y1, x2, y2) coordinates
- [x] Calculates shaft angle from horizontal
- [x] Club head detection returns center point
- [x] Preprocessing pipeline reduces noise effectively
- [x] Test coverage >85%
- [x] All tests pass
- [x] Passes flake8 and mypy validation
- [x] Demo script shows detection on sample frames

### Should Have
- [x] ClubTracker smooths results across frames
- [x] Confidence scores for detections
- [x] Debug mode with visualization
- [x] ROI support for focused detection
- [x] Multiple detection strategies (fallback if primary fails)

### Nice to Have
- [ ] Auto-calibration for different video qualities
- [ ] Club type detection (driver vs iron)
- [ ] Grip position detection
- [ ] Performance profiling results

## Test Strategy

### Unit Tests
1. **Preprocessing**
   - Test grayscale conversion
   - Test blur application
   - Test ROI extraction
   - Test contrast enhancement

2. **Shaft Detection**
   - Test with synthetic images (drawn lines)
   - Test with no lines present
   - Test with multiple lines (selection logic)
   - Test angle calculation

3. **Club Head Detection**
   - Test with synthetic circles
   - Test with no circles
   - Test size filtering

4. **Tracking**
   - Test smoothing logic
   - Test gap filling
   - Test reset functionality

### Integration Tests
1. Use real video frames from test_swing.mp4
2. Verify detection on frames where club is clearly visible
3. Test performance on batch of frames
4. Verify integration with angle calculation module

### Performance Tests
1. Measure fps on typical frame (should be >10 fps)
2. Test with different resolutions
3. Profile bottlenecks

## Dependencies
- OpenCV (cv2) - already in requirements.txt
- NumPy - already in requirements.txt
- pytest - for testing
- Pillow - for test image generation

## Example Usage
```python
from src.detection import ClubDetector, ClubTracker
from src.video import VideoLoader, FrameExtractor

# Initialize detector
detector = ClubDetector(debug=True)
tracker = ClubTracker(smoothing_window=3)

# Load video
with VideoLoader("swing.mp4") as video:
    extractor = FrameExtractor(video)

    # Detect in each frame
    for frame_num in range(0, video.frame_count, 5):
        frame = extractor.extract_frame(frame_num)

        # Detect club
        result = detector.detect(frame)

        # Smooth with tracker
        smoothed = tracker.update(result)

        if smoothed.shaft_detected:
            print(f"Frame {frame_num}: Shaft at {smoothed.shaft_angle:.1f}°")
            print(f"  Confidence: {smoothed.confidence:.2f}")
```

## Risk Assessment
1. **Lighting variations** - Mitigate with preprocessing and adaptive thresholds
2. **Club behind body** - Tracker can interpolate during occlusion
3. **Background clutter** - ROI and line filtering reduce false positives
4. **Different club types** - Parameter tuning may be needed per club

## Future Enhancements
- Machine learning-based detection (YOLO, etc.)
- 3D club path reconstruction
- Automatic parameter tuning based on video analysis
- Real-time detection optimization
