# Golf Swing Analyzer - Project Rules

## Project Overview
Python desktop application for analyzing golf swing videos. Runs on Debian Linux. 
Videos are uploaded from iPhone. The app extracts frames, detects body/club positions,
draws analysis lines and angles, and provides feedback for swing improvement.

## Before Starting Work
- Read PLANNING.md to understand architecture and goals
- Check TASK.md for current priorities
- Review examples/ folder for code patterns

## Code Organization
- Keep files under 500 lines; split into modules if approaching limit
- Use clear module separation:
  - `src/video/` - Video loading, frame extraction
  - `src/detection/` - Pose detection, club tracking
  - `src/analysis/` - Angle calculations, swing plane analysis
  - `src/visualization/` - Drawing overlays, export
  - `src/gui/` - PyQt5 interface components
- Use relative imports within packages

## Python Standards
- Python 3.10+ (use type hints)
- Follow PEP 8, max line length 100
- Use docstrings for all public functions (Google style)
- Virtual environment: use `venv/` directory

## Dependencies (Preferred Libraries)
- OpenCV (cv2) for video/image processing
- MediaPipe for pose detection
- PyQt5 for GUI
- NumPy for calculations
- Pillow for image manipulation

## Testing
- Use pytest
- Test files mirror source structure: `tests/test_*.py`
- Minimum 80% coverage for core analysis functions
- Run tests with: `pytest tests/ -v`

## Error Handling
- Fail fast with clear error messages
- Log errors with structured logging (use `logging` module)
- Never silently catch exceptions

## Git Workflow
- Meaningful commit messages
- One logical change per commit

## IMPORTANT
- Never assume file paths exist; always verify
- Videos can be large; use lazy loading / frame skipping where possible
- All angle calculations in degrees, not radians
- Preserve original video files; work on copies