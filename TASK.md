# Current Tasks

## In Progress
(none)

## Backlog
- [ ] Pose detection integration (MediaPipe)
- [ ] Swing plane line drawing
- [ ] GUI main window layout (PyQt5)
- [ ] Video player widget
- [ ] Manual line drawing tools
- [ ] Visualization overlays (lines, angles, annotations)
- [ ] Export annotated frames and videos

## Completed
- [x] Initial project setup and structure
- [x] Video loading and format handling
  - VideoLoader class with support for .mov/.mp4 files
  - Metadata extraction (fps, frame count, resolution, duration)
  - Context manager support
- [x] Frame extraction with caching
  - FrameExtractor class with LRU cache
  - Downsampling support (0.25x, 0.5x, 1.0x)
  - Batch extraction with step parameter
- [x] Key position detection
  - KeyPositionDetector class
  - Motion-based analysis to find P1, P4, P7 positions
- [x] Basic angle calculation utilities
  - Core angle functions (12 functions for angles, geometry)
  - JointAngleCalculator for body landmark analysis
  - ClubAngleCalculator for club shaft measurements
  - 74 tests with 98% coverage
  - Demo script with usage examples
- [x] Club tracking system
  - ClubDetector using Canny edge detection + Hough line transform
  - FramePreprocessor with ROI and contrast enhancement
  - ClubTracker for multi-frame smoothing and gap interpolation
  - Shaft and club head detection
  - 51 tests with 94-98% module coverage
  - Demo script with synthetic and real video examples
- [x] Comprehensive test suite
  - 166 tests total with 97% coverage
  - All linting checks pass (flake8, mypy)
- [x] Project documentation
  - README.md with usage examples
  - requirements.txt with dependencies
  - Virtual environment setup