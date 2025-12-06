# Feature Request: Video Loading and Frame Extraction

## FEATURE:
Create the video loading and frame extraction module. This should:

1. Load video files from iPhone (.mov, .mp4) supporting HEVC codec
2. Extract individual frames as numpy arrays (BGR format for OpenCV compatibility)
3. Navigate to specific frames by frame number or timestamp
4. Auto-detect key swing positions (P1-P8) based on motion analysis
5. Handle large 4K videos efficiently (lazy loading, no full load to memory)

## TECHNICAL REQUIREMENTS:

### VideoLoader class
- Accept file path, validate format
- Get video properties: fps, frame_count, resolution, duration
- Support seeking to specific frame
- Iterator interface for frame-by-frame processing

### FrameExtractor class  
- Extract single frame as numpy array
- Extract frame range
- Downsample option (0.25, 0.5, 1.0 scale factors)
- Cache recently accessed frames (LRU cache, configurable size)

### KeyPositionDetector class
- Analyze video to find approximate timestamps for P1-P8 positions
- Use motion magnitude/optical flow to detect:
  - P1 (address): low motion before swing starts
  - P4 (top): direction change point
  - P7 (impact): high velocity point
- Return dict mapping position names to frame numbers

## FILES TO CREATE:
- src/video/__init__.py
- src/video/loader.py (VideoLoader class)
- src/video/frame_extractor.py (FrameExtractor, KeyPositionDetector classes)
- tests/test_video_loader.py
- tests/test_frame_extractor.py

## EXAMPLES:
Reference examples/sample_opencv_video.py for video handling patterns (if it exists)

## DOCUMENTATION:
- OpenCV VideoCapture: https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html
- MediaPipe: https://google.github.io/mediapipe/

## SUCCESS CRITERIA:
1. Can load a .mov file from iPhone without errors
2. Can navigate to any frame by number
3. Frame extraction takes <50ms for single frame
4. Memory usage stays under 500MB even for 4K videos
5. Key position detection completes in <10 seconds for 5-second swing video
6. All tests pass with >90% coverage

## OTHER CONSIDERATIONS:
- iPhone videos may have rotation metadata—handle correctly
- Some older iPhones use H.264, newer use HEVC—support both
- Frame numbers are 0-indexed
- Consider that cv2.VideoCapture seeking can be slow—may need keyframe-based approach