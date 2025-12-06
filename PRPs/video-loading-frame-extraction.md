# Product Requirements Prompt: Video Loading and Frame Extraction

## 1. Context

### Feature Overview
This feature implements the foundational video processing layer for the Golf Swing Analyzer application. It provides the ability to load iPhone video files, extract frames efficiently, navigate through video content, and automatically detect key swing positions based on motion analysis.

### Architecture Integration
This module is the **first layer** in the application architecture (see PLANNING.md):
- Located in `src/video/` package
- Provides data to downstream modules:
  - `src/detection/` will consume frames for pose/club detection
  - `src/gui/` will use VideoLoader for playback controls
  - `src/analysis/` will use key position data for swing analysis

### Dependencies
- **External**: OpenCV (cv2), NumPy
- **Internal**: None (foundational module)
- **System**: Python 3.10+, sufficient RAM for frame caching

### iPhone Video Requirements
- Formats: `.mov` (preferred), `.mp4`
- Codecs: H.264 (older iPhones), HEVC/H.265 (iPhone 7+)
- Resolutions: 1080p to 4K (3840x2160)
- Frame rates: 30fps or 60fps
- Rotation metadata: May include EXIF orientation tags

## 2. Technical Specification

### 2.1 Data Structures and Types

```python
from typing import Iterator, Dict, Optional, Tuple
import numpy as np
from numpy.typing import NDArray

# Type aliases
Frame = NDArray[np.uint8]  # Shape: (height, width, 3), BGR format
FrameNumber = int
Timestamp = float  # seconds
ScaleFactor = float  # 0.25, 0.5, or 1.0

# Video metadata
class VideoMetadata:
    """Container for video properties."""
    fps: float
    frame_count: int
    width: int
    height: int
    duration: float  # seconds
    codec: str

# Key position mapping
KeyPositions = Dict[str, FrameNumber]  # e.g., {"P1": 0, "P4": 45, "P7": 78}
```

### 2.2 Class Signatures

#### VideoLoader (`src/video/loader.py`)

```python
class VideoLoader:
    """Handles video file loading and provides frame access interface.

    Supports lazy loading - does not load entire video into memory.
    Validates video format and provides metadata.
    """

    def __init__(self, file_path: str) -> None:
        """Initialize video loader.

        Args:
            file_path: Absolute path to video file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported
            RuntimeError: If OpenCV cannot open the video
        """

    def get_metadata(self) -> VideoMetadata:
        """Get video properties."""

    def seek(self, frame_number: FrameNumber) -> bool:
        """Move to specific frame position.

        Args:
            frame_number: 0-indexed frame number

        Returns:
            True if seek successful, False otherwise
        """

    def read_frame(self) -> Optional[Frame]:
        """Read current frame and advance position.

        Returns:
            Frame as BGR numpy array, or None if end of video
        """

    def get_frame_at(self, frame_number: FrameNumber) -> Optional[Frame]:
        """Get specific frame without changing current position.

        Args:
            frame_number: 0-indexed frame number

        Returns:
            Frame as BGR numpy array, or None if invalid frame number
        """

    def __iter__(self) -> Iterator[Tuple[FrameNumber, Frame]]:
        """Iterate through all frames.

        Yields:
            Tuple of (frame_number, frame_array)
        """

    def release(self) -> None:
        """Release video file resources."""

    def __enter__(self):
        """Context manager entry."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures release() is called."""
```

#### FrameExtractor (`src/video/frame_extractor.py`)

```python
class FrameExtractor:
    """Extract and process frames with caching and downsampling.

    Provides efficient frame access with LRU cache and optional scaling.
    """

    def __init__(
        self,
        video_loader: VideoLoader,
        cache_size: int = 50,
        default_scale: ScaleFactor = 1.0
    ) -> None:
        """Initialize frame extractor.

        Args:
            video_loader: VideoLoader instance
            cache_size: Maximum frames to cache (LRU eviction)
            default_scale: Default scaling factor for extracted frames
        """

    def extract_frame(
        self,
        frame_number: FrameNumber,
        scale: Optional[ScaleFactor] = None
    ) -> Frame:
        """Extract single frame with optional scaling.

        Args:
            frame_number: 0-indexed frame number
            scale: Scale factor (overrides default_scale if provided)

        Returns:
            Processed frame as BGR numpy array

        Raises:
            ValueError: If frame_number is out of range or scale is invalid
        """

    def extract_range(
        self,
        start_frame: FrameNumber,
        end_frame: FrameNumber,
        step: int = 1,
        scale: Optional[ScaleFactor] = None
    ) -> list[Frame]:
        """Extract range of frames.

        Args:
            start_frame: Starting frame number (inclusive)
            end_frame: Ending frame number (exclusive)
            step: Frame skip interval (1 = every frame)
            scale: Scale factor for all frames

        Returns:
            List of frame arrays

        Raises:
            ValueError: If range is invalid
        """

    def clear_cache(self) -> None:
        """Clear the frame cache."""

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics.

        Returns:
            Dict with keys: 'hits', 'misses', 'size'
        """
```

#### KeyPositionDetector (`src/video/frame_extractor.py`)

```python
class KeyPositionDetector:
    """Detect key swing positions (P1-P8) using motion analysis.

    Uses frame differencing and optical flow magnitude to identify
    characteristic points in the golf swing.
    """

    def __init__(self, video_loader: VideoLoader) -> None:
        """Initialize key position detector.

        Args:
            video_loader: VideoLoader instance
        """

    def detect_positions(
        self,
        downsample_factor: int = 4
    ) -> KeyPositions:
        """Analyze video to find key swing positions.

        Detects:
        - P1 (Address): Low motion period before swing starts
        - P4 (Top of backswing): Motion direction change
        - P7 (Impact): Highest velocity point

        Args:
            downsample_factor: Process every Nth frame for speed

        Returns:
            Dictionary mapping position names to frame numbers

        Note:
            Other positions (P2, P3, P5, P6, P8) can be interpolated
            or manually adjusted by user in GUI later.
        """

    def _calculate_motion_magnitude(
        self,
        frames: list[Frame]
    ) -> NDArray[np.float32]:
        """Calculate motion magnitude between consecutive frames.

        Args:
            frames: List of frame arrays

        Returns:
            Array of motion magnitudes (one per frame transition)
        """

    def _find_low_motion_region(
        self,
        motion: NDArray[np.float32],
        window_size: int = 10
    ) -> FrameNumber:
        """Find address position (sustained low motion).

        Args:
            motion: Array of motion magnitudes
            window_size: Frames to average for stability

        Returns:
            Frame number of detected address position
        """

    def _find_direction_change(
        self,
        motion: NDArray[np.float32],
        start_frame: FrameNumber
    ) -> FrameNumber:
        """Find top of backswing (motion direction change).

        Args:
            motion: Array of motion magnitudes
            start_frame: Frame to start searching from (after address)

        Returns:
            Frame number of detected top position
        """

    def _find_peak_velocity(
        self,
        motion: NDArray[np.float32],
        start_frame: FrameNumber
    ) -> FrameNumber:
        """Find impact position (peak velocity).

        Args:
            motion: Array of motion magnitudes
            start_frame: Frame to start searching from (after top)

        Returns:
            Frame number of detected impact position
        """
```

### 2.3 File Locations

New files to create:
- `src/video/__init__.py` - Package initialization, exports main classes
- `src/video/loader.py` - VideoLoader class (~150 lines)
- `src/video/frame_extractor.py` - FrameExtractor and KeyPositionDetector (~300 lines)
- `tests/test_video_loader.py` - VideoLoader tests (~200 lines)
- `tests/test_frame_extractor.py` - FrameExtractor and KeyPositionDetector tests (~250 lines)

## 3. Implementation Steps

### Step 1: Project Structure Setup
Create the basic directory structure and empty files.

```bash
mkdir -p src/video tests
touch src/__init__.py
touch src/video/__init__.py
touch src/video/loader.py
touch src/video/frame_extractor.py
touch tests/__init__.py
touch tests/test_video_loader.py
touch tests/test_frame_extractor.py
```

**Validation**: All files exist and are importable.

### Step 2: Implement VideoLoader Core
In `src/video/loader.py`, implement the VideoLoader class.

**Key requirements**:
- Validate file path exists and has supported extension (`.mov`, `.mp4`)
- Use `cv2.VideoCapture` for video access
- Extract metadata using `cv2.CAP_PROP_*` constants
- Implement context manager protocol (`__enter__`, `__exit__`)
- Handle HEVC codec (may require `opencv-python` with HEVC support)
- Add proper logging for errors and warnings

**Code pattern**:
```python
import cv2
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {'.mov', '.mp4'}

class VideoLoader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

        # Validation
        if not self.file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        if self.file_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {self.file_path.suffix}")

        # Open video
        self.cap = cv2.VideoCapture(str(self.file_path))
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video: {file_path}")

        logger.info(f"Loaded video: {file_path}")

        # Extract metadata
        self._metadata = self._extract_metadata()
```

**Validation**: Can instantiate VideoLoader with valid video path.

### Step 3: Implement VideoLoader Frame Access
Add frame reading, seeking, and iteration methods.

**Key requirements**:
- `seek()` should use `cv2.CAP_PROP_POS_FRAMES`
- `read_frame()` returns BGR numpy array
- `get_frame_at()` preserves current position (seek, read, seek back)
- Iterator yields `(frame_number, frame)` tuples
- Handle end-of-video gracefully (return None)

**Edge cases**:
- Seeking beyond video length
- Seeking to negative frame numbers
- Reading when video is at end

**Validation**: Can seek to specific frames and read them correctly.

### Step 4: Write VideoLoader Tests
In `tests/test_video_loader.py`, write comprehensive tests.

**Test cases**:
- File not found raises `FileNotFoundError`
- Unsupported format raises `ValueError`
- Valid video loads successfully
- Metadata extraction (fps, frame_count, etc.)
- Seeking to valid frame
- Seeking to invalid frame (negative, beyond length)
- Reading frames sequentially
- Context manager properly releases resources
- Iterator protocol works correctly

**Required**: Create a small test video file or use a fixture.

**Validation**: `pytest tests/test_video_loader.py -v` passes all tests.

### Step 5: Implement FrameExtractor with Caching
In `src/video/frame_extractor.py`, implement the FrameExtractor class.

**Key requirements**:
- Use `functools.lru_cache` or custom LRU cache for frames
- Implement downsampling with `cv2.resize(frame, None, fx=scale, fy=scale)`
- Cache key should include frame number and scale factor
- `extract_frame()` should check cache before reading from video
- `extract_range()` should reuse `extract_frame()` for caching benefit

**Code pattern**:
```python
from functools import lru_cache
import cv2
import numpy as np

class FrameExtractor:
    def __init__(self, video_loader, cache_size=50, default_scale=1.0):
        self.video_loader = video_loader
        self.default_scale = default_scale
        self.cache_size = cache_size
        self._cache = {}
        self._cache_order = []  # For LRU tracking
        self.hits = 0
        self.misses = 0

    def extract_frame(self, frame_number, scale=None):
        scale = scale or self.default_scale
        cache_key = (frame_number, scale)

        # Check cache
        if cache_key in self._cache:
            self.hits += 1
            return self._cache[cache_key]

        # Cache miss - extract frame
        self.misses += 1
        frame = self.video_loader.get_frame_at(frame_number)

        if frame is None:
            raise ValueError(f"Invalid frame number: {frame_number}")

        # Apply scaling
        if scale != 1.0:
            frame = cv2.resize(frame, None, fx=scale, fy=scale)

        # Add to cache (LRU eviction)
        self._add_to_cache(cache_key, frame)

        return frame
```

**Validation**: Cache correctly stores and retrieves frames.

### Step 6: Implement KeyPositionDetector
In `src/video/frame_extractor.py`, implement the KeyPositionDetector class.

**Key requirements**:
- Use frame differencing: `cv2.absdiff(gray1, gray2)` for motion
- Calculate motion magnitude: `np.sum(diff)` per frame
- Smooth motion signal with moving average or Gaussian filter
- P1 detection: Find first sustained low-motion region
- P4 detection: Find first major motion direction change (peak followed by valley)
- P7 detection: Find global motion peak in downswing region

**Algorithm outline**:
```python
def detect_positions(self, downsample_factor=4):
    # 1. Extract frames at reduced rate
    metadata = self.video_loader.get_metadata()
    frame_indices = range(0, metadata.frame_count, downsample_factor)
    frames = [self.video_loader.get_frame_at(i) for i in frame_indices]

    # 2. Convert to grayscale and calculate motion
    motion = self._calculate_motion_magnitude(frames)

    # 3. Detect key positions
    p1_frame = self._find_low_motion_region(motion)
    p4_frame = self._find_direction_change(motion, start_frame=p1_frame)
    p7_frame = self._find_peak_velocity(motion, start_frame=p4_frame)

    # 4. Map back to original frame numbers
    return {
        "P1": frame_indices[p1_frame],
        "P4": frame_indices[p4_frame],
        "P7": frame_indices[p7_frame]
    }
```

**Validation**: Detects reasonable positions in test swing video.

### Step 7: Write FrameExtractor Tests
In `tests/test_frame_extractor.py`, test FrameExtractor.

**Test cases**:
- Extract single frame at different scales
- Cache hit/miss statistics
- Extract frame range with step
- Cache size limit enforcement (LRU eviction)
- Invalid frame numbers raise ValueError
- Invalid scale factors raise ValueError
- Cache clearing

**Validation**: `pytest tests/test_frame_extractor.py::TestFrameExtractor -v` passes.

### Step 8: Write KeyPositionDetector Tests
In `tests/test_frame_extractor.py`, test KeyPositionDetector.

**Test cases**:
- Mock video with known motion patterns
- Detect P1 in low-motion region
- Detect P4 at direction change
- Detect P7 at peak velocity
- Handle videos with no clear positions gracefully
- Downsample factor affects performance but not accuracy

**Mocking strategy**: Create synthetic video with predictable motion.

**Validation**: `pytest tests/test_frame_extractor.py::TestKeyPositionDetector -v` passes.

### Step 9: Integration Testing
Test the full workflow with a real iPhone video.

**Test script** (`tests/integration_test_video.py`):
```python
from src.video.loader import VideoLoader
from src.video.frame_extractor import FrameExtractor, KeyPositionDetector

# Load video
video_path = "path/to/test_swing.mov"
with VideoLoader(video_path) as loader:
    # Get metadata
    meta = loader.get_metadata()
    print(f"Video: {meta.fps}fps, {meta.frame_count} frames, {meta.duration}s")

    # Extract frames
    extractor = FrameExtractor(loader, cache_size=100)
    frame = extractor.extract_frame(0, scale=0.5)
    print(f"Frame shape: {frame.shape}")

    # Detect key positions
    detector = KeyPositionDetector(loader)
    positions = detector.detect_positions()
    print(f"Key positions: {positions}")
```

**Validation**: Script runs without errors and produces sensible output.

### Step 10: Package Initialization
In `src/video/__init__.py`, export public classes.

```python
"""Video loading and frame extraction module."""

from .loader import VideoLoader
from .frame_extractor import FrameExtractor, KeyPositionDetector

__all__ = ['VideoLoader', 'FrameExtractor', 'KeyPositionDetector']
```

**Validation**: Can import from package: `from src.video import VideoLoader`.

### Step 11: Performance Optimization
Profile and optimize for performance requirements.

**Key metrics**:
- Single frame extraction: <50ms
- Memory usage: <500MB for 4K video
- Key position detection: <10s for 5-second video

**Profiling approach**:
```python
import time
import memory_profiler

# Test frame extraction speed
start = time.time()
frame = extractor.extract_frame(100)
elapsed = time.time() - start
assert elapsed < 0.050, f"Frame extraction too slow: {elapsed}s"

# Test memory usage
# Use memory_profiler to monitor peak memory
```

**Optimizations**:
- Ensure VideoLoader doesn't load entire video into memory
- Limit cache size appropriately
- Use smaller scale factors during key position detection
- Consider keyframe-only seeking for faster navigation

**Validation**: Performance tests pass.

### Step 12: Documentation and Logging
Add comprehensive docstrings and logging.

**Requirements**:
- All public methods have Google-style docstrings
- Module-level docstrings explain purpose
- Logging at INFO level for important operations
- Logging at WARNING for recoverable issues
- Logging at ERROR for failures

**Example**:
```python
logger.info(f"Extracting frame {frame_number} at scale {scale}")
logger.warning(f"Frame {frame_number} not in cache, reading from disk")
logger.error(f"Failed to seek to frame {frame_number}")
```

**Validation**: Documentation is clear and logging is helpful.

## 4. Validation Gates

### After Step 2
```bash
python -c "from src.video.loader import VideoLoader; print('VideoLoader imports successfully')"
```

### After Step 4
```bash
pytest tests/test_video_loader.py -v
```
**Expected**: All tests pass (minimum 10 test cases).

### After Step 5
```bash
pytest tests/test_frame_extractor.py::TestFrameExtractor -v
```
**Expected**: All FrameExtractor tests pass.

### After Step 8
```bash
pytest tests/test_frame_extractor.py -v
```
**Expected**: All tests pass with >80% coverage.

### Code Coverage Check
```bash
pytest tests/ --cov=src/video --cov-report=term-missing
```
**Expected**: >90% coverage for this module.

### Linting
```bash
flake8 src/video/ --max-line-length=100
mypy src/video/
```
**Expected**: No errors.

### Full Test Suite
```bash
pytest tests/ -v
```
**Expected**: All tests pass.

## 5. Success Criteria

### Functional Requirements
- ✅ Can load `.mov` file from iPhone without errors
- ✅ Can load `.mp4` file from iPhone without errors
- ✅ Supports both H.264 and HEVC codecs
- ✅ Can navigate to any frame by frame number (0-indexed)
- ✅ Can iterate through all frames
- ✅ Can extract frame ranges with step parameter
- ✅ Supports downsampling (0.25x, 0.5x, 1.0x)
- ✅ Automatically detects P1, P4, P7 positions

### Performance Requirements
- ✅ Frame extraction takes <50ms for single frame
- ✅ Memory usage stays under 500MB even for 4K videos
- ✅ Key position detection completes in <10 seconds for 5-second swing video (150 frames at 30fps)
- ✅ Cache provides >70% hit rate for sequential access

### Quality Requirements
- ✅ All tests pass with >90% coverage
- ✅ No linting errors (flake8, mypy)
- ✅ All public methods have docstrings
- ✅ Proper error handling with clear messages
- ✅ Logging for important operations

### Example Usage
```python
from src.video import VideoLoader, FrameExtractor, KeyPositionDetector

# Load iPhone video
video_path = "/path/to/swing.mov"
with VideoLoader(video_path) as loader:
    # Get video info
    meta = loader.get_metadata()
    print(f"{meta.fps}fps, {meta.frame_count} frames, {meta.width}x{meta.height}")

    # Extract and cache frames
    extractor = FrameExtractor(loader, cache_size=100, default_scale=0.5)

    # Get specific frame
    frame_10 = extractor.extract_frame(10)  # Half resolution due to default_scale

    # Get range of frames
    frames = extractor.extract_range(0, 30, step=2)  # Every other frame

    # Auto-detect key positions
    detector = KeyPositionDetector(loader)
    positions = detector.detect_positions()
    # Output: {'P1': 0, 'P4': 45, 'P7': 78}

    # Extract frames at key positions
    address_frame = extractor.extract_frame(positions['P1'], scale=1.0)
    impact_frame = extractor.extract_frame(positions['P7'], scale=1.0)

    # Check cache performance
    stats = extractor.get_cache_stats()
    print(f"Cache: {stats['hits']} hits, {stats['misses']} misses")
```

**Expected output**:
```
30.0fps, 150 frames, 1920x1080
Cache: 5 hits, 3 misses
```

## 6. Code Examples and Patterns

### Pattern 1: Context Manager for Resource Management
```python
# Always use context manager to ensure video resources are released
with VideoLoader("video.mov") as loader:
    frame = loader.read_frame()
    # Resources automatically released on exit
```

### Pattern 2: Error Handling
```python
# Fail fast with clear error messages
try:
    loader = VideoLoader("video.mov")
except FileNotFoundError as e:
    logger.error(f"Video file not found: {e}")
    raise
except ValueError as e:
    logger.error(f"Invalid video format: {e}")
    raise
```

### Pattern 3: Type Hints
```python
# Use type hints for all function signatures
def extract_frame(
    self,
    frame_number: FrameNumber,
    scale: Optional[ScaleFactor] = None
) -> Frame:
    """Extract single frame with optional scaling."""
```

### Pattern 4: Numpy Array Handling
```python
# OpenCV returns BGR format, ensure correct dtype
frame = cap.read()[1]
assert frame.dtype == np.uint8
assert frame.shape[2] == 3  # BGR channels
```

### Pattern 5: Logging
```python
import logging

logger = logging.getLogger(__name__)

# Log at appropriate levels
logger.info(f"Loaded video: {file_path}")
logger.warning(f"Slow seek detected for frame {n}")
logger.error(f"Failed to read frame: {e}")
```

## 7. Additional Implementation Notes

### Handling iPhone Video Rotation
Some iPhone videos have rotation metadata (EXIF). OpenCV may not respect this.

**Solution**: Check for rotation and apply transformation:
```python
# Check rotation metadata (requires reading EXIF)
# Apply rotation if needed
if rotation == 90:
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
```

### Optimizing Video Seeking
`cv2.VideoCapture.set(cv2.CAP_PROP_POS_FRAMES, n)` can be slow for non-keyframes.

**Workaround**:
- For forward seeks close to current position, use sequential reads
- For backward seeks or large jumps, use `set()` and accept latency
- Consider building a keyframe index for faster seeking

### Motion Detection Algorithm Details
For KeyPositionDetector:

**Frame differencing**:
```python
def _calculate_motion_magnitude(self, frames):
    motion = []
    for i in range(len(frames) - 1):
        gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray1, gray2)
        motion_value = np.sum(diff)
        motion.append(motion_value)
    return np.array(motion)
```

**Smoothing for stability**:
```python
from scipy.ndimage import gaussian_filter1d
smoothed_motion = gaussian_filter1d(motion, sigma=2)
```

### Test Video Creation
For testing, create a synthetic video:
```python
import cv2
import numpy as np

# Create 5-second test video at 30fps
fps = 30
duration = 5
frame_count = fps * duration

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_swing.mp4', fourcc, fps, (640, 480))

for i in range(frame_count):
    # Create blank frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Simulate motion (moving circle)
    x = int(320 + 200 * np.sin(2 * np.pi * i / frame_count))
    y = 240
    cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)

    out.write(frame)

out.release()
```

---

## Summary Checklist

- [ ] All classes implemented with type hints
- [ ] All methods have docstrings
- [ ] VideoLoader handles iPhone formats (H.264, HEVC)
- [ ] FrameExtractor implements LRU caching
- [ ] KeyPositionDetector finds P1, P4, P7
- [ ] All tests pass (>90% coverage)
- [ ] Performance requirements met (<50ms frame extraction)
- [ ] Memory requirements met (<500MB for 4K)
- [ ] Linting passes (flake8, mypy)
- [ ] Integration test with real iPhone video succeeds
- [ ] Package exports properly configured

**End of PRP**
