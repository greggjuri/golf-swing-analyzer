# Current Tasks

## In Progress
(none)

## Backlog
- [ ] Pose detection integration (MediaPipe)
- [ ] Club tracking (edge detection + Hough transform)
- [ ] Basic angle calculation utilities
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
- [x] Comprehensive test suite
  - 41 tests with 98% coverage
  - All linting checks pass (flake8, mypy)
- [x] Project documentation
  - README.md with usage examples
  - requirements.txt with dependencies
  - Virtual environment setup