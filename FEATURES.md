# Golf Swing Analyzer - Feature Guide

## Complete Feature List

### 🎥 Video Analysis
- ✅ **Video Loading**: Support for MP4, MOV, AVI formats
- ✅ **Frame Extraction**: Lazy loading with LRU cache for performance
- ✅ **Playback Controls**: Play, pause, stop, frame-by-frame navigation
- ✅ **Variable Speed**: 0.25x, 0.5x, 1x, 2x playback speed
- ✅ **Timeline Scrubber**: Seek to any frame instantly
- ✅ **Key Position Detection**: Auto-detect P1, P4, P7 (address, top, impact, follow-through)

### 🏌️ Swing Detection & Analysis
- ✅ **Club Detection**: Canny edge + Hough transform for shaft detection
- ✅ **Pose Detection**: MediaPipe-ready architecture (33-point skeleton)
- ✅ **Temporal Smoothing**: Kalman filtering for club and pose tracking
- ✅ **Swing Plane Analysis**: 3D plane fitting with SVD
  - Attack angle, swing path, on-plane deviation
  - Separate planes for backswing/downswing

### 📐 Angle Measurements
- ✅ **Joint Angles**: Elbows, knees, spine tilt
- ✅ **Club Angles**: Shaft angle relative to ground
- ✅ **Shoulder/Hip Rotation**: Rotation angles through swing
- ✅ **X-Factor**: Shoulder-hip separation

### 📊 Angle Tracking Graphs ⭐ NEW
- ✅ **Interactive Graphs**: Click to seek, real-time frame marker
- ✅ **Multiple Angles**: Spine, elbows, knees, club shaft, rotation
- ✅ **Key Position Markers**: Visual markers at P1, P4, P7
- ✅ **Export**: Save graphs as PNG/SVG
- ✅ **Statistics**: Min, max, mean, std for each angle
- ✅ **F1 Styling**: Professional matplotlib integration
- **Keyboard**: Ctrl+G to toggle graphs

### 🎨 Visual Overlays
- ✅ **Club Track**: Shaft line and club head marker
- ✅ **Skeleton**: Full body pose skeleton
- ✅ **Joint Angles**: Visual angle arcs with measurements
- ✅ **Swing Plane**: Plane visualization with color coding
- ✅ **Key Position Labels**: P1, P4, P7 labels on video

### ✏️ Manual Drawing Tools
- ✅ **Drawing Tools**: Line, angle, circle, text annotation
- ✅ **Per-Frame Storage**: Different drawings on each frame
- ✅ **Undo/Redo**: Unlimited undo/redo stack
- ✅ **Persistence**: Save/load drawings to JSON
- ✅ **Export Integration**: Drawings appear in exported videos
- **Keyboard**: Ctrl+D to toggle drawing mode

### 🔄 Comparison Mode ⭐ NEW
- ✅ **Side-by-Side View**: Compare two swings simultaneously
- ✅ **Synchronized Playback**: Link/unlink playback
- ✅ **Frame Offset Calibration**: Align swings at impact or other positions
- ✅ **Independent Overlays**: Different overlays per side
- ✅ **Swap Videos**: Quickly swap left/right
- ✅ **Screenshot**: Capture side-by-side comparison
- **Keyboard**: Ctrl+M to toggle comparison mode

### 🎭 Overlay Mode ⭐ NEW
- ✅ **Alpha Blending**: Overlay two videos with transparency
- ✅ **4 Blend Modes**: Normal, Difference, Multiply, Screen
- ✅ **Transparency Slider**: 0-100% adjustable
- ✅ **Color Tinting**: Red/green tints to distinguish videos
- ✅ **Frame Alignment**: Auto-align different resolutions
- ✅ **Real-time Rendering**: Smooth playback in overlay mode

### 💾 Export Features
- ✅ **Frame Export**: Export current frame as PNG/JPEG
- ✅ **Video Export**: Export annotated video with overlays
- ✅ **Codec Support**: MJPEG, XVID, MP4V
- ✅ **Progress Tracking**: Progress bar with ETA
- ✅ **Quality Control**: Adjustable JPEG quality, PNG compression

### 🎨 User Interface
- ✅ **F1 Design Aesthetic**: Professional black/silver/white theme
- ✅ **Glass Morphism**: Semi-transparent panels with blur
- ✅ **Responsive Layout**: Resizable panels with splitters
- ✅ **Status Bar**: Real-time feedback on operations
- ✅ **Tooltips**: Helpful hints on all controls

### ⌨️ Keyboard Shortcuts
- `Ctrl+O`: Open video
- `Ctrl+E`: Export video
- `Ctrl+A`: Analyze current frame
- `Ctrl+Shift+A`: Analyze full video
- `Ctrl+D`: Toggle drawing mode
- `Ctrl+Z/Y`: Undo/Redo
- `Ctrl+M`: Toggle comparison mode
- `Ctrl+G`: Toggle angle graphs ⭐ NEW
- `Ctrl+Shift+S/O`: Save/load drawings

## Quick Start Guide

### Basic Analysis Workflow
1. **Open Video**: File → Open Video (Ctrl+O)
2. **Analyze**: Analysis → Analyze Full Video (Ctrl+Shift+A)
3. **View Overlays**: Toggle overlays in Analysis Panel
4. **View Graphs**: View → Angle Graphs (Ctrl+G)
5. **Export**: File → Export Video (Ctrl+E)

### Comparison Workflow
1. **Enable Comparison**: View → Comparison Mode (Ctrl+M)
2. **Load Videos**: Click "Load Left Video" and "Load Right Video"
3. **Calibrate Sync**: Seek to matching frames, click "Calibrate Sync"
4. **Choose View**: Toggle "Side-by-Side" or "Overlay"
5. **Adjust Settings**: Use transparency slider, blend modes, tints

### Drawing Workflow
1. **Enable Drawing**: Draw → Enable Drawing Mode (Ctrl+D)
2. **Select Tool**: Choose Line, Angle, Circle, or Text
3. **Draw**: Click and drag on video
4. **Save**: Draw → Save Drawings (Ctrl+Shift+S)

## Performance Tips
- Use frame downsampling (0.5x) for faster analysis on long videos
- Clear cache between videos to free memory
- Export with MJPEG codec for faster encoding (larger files)
- Use MP4V for smaller files (slower encoding)

## Troubleshooting

### Video Won't Load
- Ensure codec is supported (H.264, HEVC work best)
- Try converting to MP4 with standard codec
- Check file isn't corrupted

### Analysis is Slow
- Reduce video resolution before import
- Use frame downsampling
- Analyze shorter clips first

### Overlays Not Showing
- Ensure analysis has been run first
- Check overlay toggles are enabled
- Refresh display (seek to another frame and back)

### Graphs Not Showing Data
- Run full video analysis first
- Toggle graphs on with Ctrl+G
- Check that pose/club detection succeeded

## Advanced Features

### Swing Plane Analysis
After running full video analysis:
- Plane results available in metrics panel
- Shows attack angle, swing path, deviation
- Separate backswing/downswing planes if detected

### Key Position Detection
Analysis → Detect Key Positions:
- Auto-detects address, top of backswing, impact, follow-through
- Marks positions on timeline with colors
- Use for sync calibration in comparison mode

### Color Tinting in Overlay Mode
- Red tint for left video helps distinguish it
- Green tint for right video provides contrast
- Adjust transparency to balance visibility
- Difference mode highlights changes automatically

## Known Limitations
- MediaPipe pose detection requires Python <3.13 (placeholder implementation included)
- Very long videos (>10 min) may require patience for full analysis
- 4K videos should be downsampled for real-time playback
- Manual drawings are frame-specific (not auto-interpolated)

## What's Next
Potential future enhancements:
- Swing tempo analysis (backswing:downswing ratio)
- Club face angle detection
- PDF/HTML analysis reports
- Swing template library (pro swings)
- Batch video processing
- 3D visualization
- Machine learning swing classification

## Credits
Built with:
- PyQt5 for GUI
- OpenCV for video/image processing
- Matplotlib for graphing
- MediaPipe (ready) for pose detection
- NumPy/SciPy for analysis

Generated with ❤️ by Claude Code
