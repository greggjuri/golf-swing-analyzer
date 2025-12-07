# Golf Swing Analyzer - Testing Guide

## Prerequisites

### Video Requirements
- **Format**: MP4, MOV, or AVI
- **Recommended Resolution**: 720p or 1080p (4K will be slower)
- **Recommended Length**: 5-30 seconds per swing
- **Content**: Full body visible, clear view of club
- **Lighting**: Good lighting for better detection

### Sample Videos Needed
1. **Basic swing video** - Single swing, front-on view
2. **Side view swing** - Profile/side angle
3. **Multiple swings** - Several swings in one video
4. **Different golfer** - For comparison testing
5. **Various quality** - Test with different lighting/resolution

## Test Workflow Checklist

### 1. Basic Video Loading and Playback
- [ ] Open video (Ctrl+O or File → Open Video)
- [ ] Verify video metadata displays (fps, frame count, duration, resolution)
- [ ] Test playback controls:
  - [ ] Play/pause (spacebar)
  - [ ] Stop button
  - [ ] Timeline scrubbing (click and drag)
  - [ ] Frame-by-frame navigation (← → keys)
- [ ] Test playback speeds:
  - [ ] 0.25x (slow motion)
  - [ ] 0.5x (half speed)
  - [ ] 1x (normal)
  - [ ] 2x (double speed)
- [ ] Check status bar for feedback

**Expected Results**: Smooth playback, accurate timeline, no crashes

---

### 2. Single Frame Analysis
- [ ] Load video and seek to address position
- [ ] Run Analysis → Analyze Current Frame (Ctrl+A)
- [ ] Check status bar for "Analyzing frame..." message
- [ ] Verify overlays appear on video:
  - [ ] Club track (if club detected)
  - [ ] Skeleton (if pose detected)
  - [ ] Joint angles (if pose detected)
- [ ] Toggle overlays on/off in Analysis Panel
- [ ] Check metrics display for angle values

**Expected Results**: Club and pose detected, overlays render correctly, metrics update

**Known Limitations**: Pose detection uses placeholder (MediaPipe not available on Python 3.13)

---

### 3. Full Video Analysis
- [ ] Run Analysis → Analyze Full Video (Ctrl+Shift+A)
- [ ] Watch progress bar in status bar
- [ ] Wait for "Analysis complete" message
- [ ] Scrub through timeline - verify overlays on all frames
- [ ] Check for key position detection:
  - [ ] P1 (Address) marker on timeline
  - [ ] P4 (Top of backswing) marker
  - [ ] P7 (Impact) marker
  - [ ] Follow-through marker

**Expected Results**: All frames analyzed, key positions auto-detected, smooth overlay display

**Performance Notes**:
- 720p 30fps 10-second video: ~30-60 seconds
- 1080p 60fps 30-second video: 2-5 minutes
- Use frame downsampling (0.5x) for faster analysis on long videos

---

### 4. Angle Tracking Graphs
- [ ] After full video analysis, open graphs (Ctrl+G or View → Angle Graphs)
- [ ] Verify graph panel appears below video
- [ ] Test angle selector dropdown:
  - [ ] Spine Angle
  - [ ] Left Elbow
  - [ ] Right Elbow
  - [ ] Left Knee
  - [ ] Right Knee
  - [ ] Shoulder Rotation
  - [ ] Club Shaft Angle
- [ ] Check graph displays:
  - [ ] Line plot with F1 styling (black background, silver grid)
  - [ ] X-axis: Frame numbers
  - [ ] Y-axis: Angle in degrees
- [ ] Test key position markers:
  - [ ] Gold vertical lines at P1, P4, P7
  - [ ] Labels at top of lines
  - [ ] Toggle "Show Key Positions" checkbox
- [ ] Test interactivity:
  - [ ] Click on graph - video seeks to that frame
  - [ ] Play video - white vertical marker tracks current frame
  - [ ] Select different angle - graph updates
- [ ] Export graph:
  - [ ] Click "📷 Export Graph"
  - [ ] Save as PNG
  - [ ] Save as SVG
  - [ ] Verify exported file

**Expected Results**: Smooth graphs, accurate data, interactive seek works, exports successful

---

### 5. Comparison Mode (Side-by-Side)
- [ ] Enable comparison mode (Ctrl+M or View → Comparison Mode)
- [ ] Interface switches to dual-video layout
- [ ] Load left video (click "Load Left Video")
- [ ] Load right video (click "Load Right Video")
- [ ] Both videos display side-by-side
- [ ] Test independent playback:
  - [ ] Play left video only
  - [ ] Play right video only
  - [ ] Different speeds per side
- [ ] Test synchronized playback:
  - [ ] Click "Link Playback" button (🔗)
  - [ ] Play - both videos play together
  - [ ] Seek - both videos seek together
- [ ] Test sync calibration:
  - [ ] Seek left video to impact frame
  - [ ] Seek right video to impact frame
  - [ ] Click "Calibrate Sync" button
  - [ ] Frame offset displays in status
  - [ ] Linked playback now synchronized at impact
- [ ] Test overlay toggles per side:
  - [ ] Enable club track on left only
  - [ ] Enable skeleton on right only
  - [ ] Different overlays per video
- [ ] Swap videos:
  - [ ] Click "Swap L/R" button (⇄)
  - [ ] Videos exchange positions
- [ ] Screenshot:
  - [ ] Click "Screenshot" button (📸)
  - [ ] Save image
  - [ ] Verify side-by-side frame saved

**Expected Results**: Dual playback works, sync calibration accurate, independent controls functional

---

### 6. Overlay Mode (Alpha Blending)
- [ ] In comparison mode, switch view mode:
  - [ ] Toggle "Overlay" radio button
  - [ ] Videos now blend into single view
- [ ] Test transparency slider:
  - [ ] Move slider from 0% to 100%
  - [ ] 0% = left video only
  - [ ] 50% = equal blend
  - [ ] 100% = right video only
- [ ] Test blend modes:
  - [ ] **Normal**: Standard alpha blending
  - [ ] **Difference**: Highlights differences (good for alignment check)
  - [ ] **Multiply**: Darker blend
  - [ ] **Screen**: Lighter blend
- [ ] Test color tints:
  - [ ] Enable "Red Tint (Left)" - left video tinted red
  - [ ] Enable "Green Tint (Right)" - right video tinted green
  - [ ] Both tints - videos distinguishable by color
- [ ] Play in overlay mode:
  - [ ] Smooth playback
  - [ ] Real-time blending during playback
- [ ] Screenshot overlay:
  - [ ] Capture blended frame
  - [ ] Verify export

**Expected Results**: Smooth overlay rendering, blend modes work correctly, tints help distinguish videos

**Use Cases**:
- **Difference mode**: Check if swings are aligned
- **Normal + Red/Green tints**: Compare swing paths side-by-side
- **50% transparency**: See both swings simultaneously

---

### 7. Manual Drawing Tools
- [ ] Load video and seek to specific frame
- [ ] Enable drawing mode (Ctrl+D or Draw → Enable Drawing Mode)
- [ ] Drawing toolbar appears
- [ ] Test line tool:
  - [ ] Select line tool
  - [ ] Click start point, drag, release
  - [ ] Line appears with measurement label
  - [ ] Verify angle measurement if applicable
- [ ] Test angle tool:
  - [ ] Select angle tool
  - [ ] Click three points (vertex in middle)
  - [ ] Angle arc and degree label appears
- [ ] Test circle tool:
  - [ ] Select circle tool
  - [ ] Click center, drag radius, release
  - [ ] Circle appears with radius label
- [ ] Test text tool:
  - [ ] Select text tool
  - [ ] Click position
  - [ ] Enter text in dialog
  - [ ] Text appears on frame
- [ ] Test color picker:
  - [ ] Change drawing color
  - [ ] New drawings use new color
- [ ] Test thickness slider:
  - [ ] Adjust line thickness
  - [ ] New drawings use new thickness
- [ ] Test per-frame storage:
  - [ ] Draw on frame 100
  - [ ] Seek to frame 200
  - [ ] Draw different shapes
  - [ ] Seek back to frame 100 - original drawings still there
  - [ ] Seek to frame 200 - second set of drawings there
- [ ] Test undo/redo:
  - [ ] Draw several shapes
  - [ ] Undo (Ctrl+Z) - last shape disappears
  - [ ] Redo (Ctrl+Y) - shape reappears
  - [ ] Multiple undo levels work
- [ ] Test save/load:
  - [ ] Draw annotations on multiple frames
  - [ ] Save drawings (Ctrl+Shift+S or Draw → Save Drawings)
  - [ ] Save to JSON file
  - [ ] Close video
  - [ ] Reopen video
  - [ ] Load drawings (Ctrl+Shift+O or Draw → Load Drawings)
  - [ ] All drawings restored
- [ ] Test shape selection and deletion:
  - [ ] Click on existing shape to select
  - [ ] Shape highlights
  - [ ] Press Delete key
  - [ ] Shape removed

**Expected Results**: All tools work, per-frame storage accurate, persistence works

---

### 8. Export Features

#### 8a. Export Current Frame
- [ ] Load video and analyze frame
- [ ] Enable overlays (club, skeleton, angles)
- [ ] Draw manual annotations
- [ ] Export frame (File → Export Frame → PNG)
- [ ] Save file
- [ ] Open exported image:
  - [ ] Overlays visible
  - [ ] Drawings visible
  - [ ] High quality
- [ ] Test JPEG export:
  - [ ] File → Export Frame → JPEG
  - [ ] Adjust quality slider
  - [ ] Export and verify

**Expected Results**: Frame exports with all overlays and drawings

#### 8b. Export Annotated Video
- [ ] Load video and run full analysis
- [ ] Enable desired overlays
- [ ] Add drawings on key frames
- [ ] Export video (Ctrl+E or File → Export Video)
- [ ] Choose codec (MJPEG, XVID, or MP4V)
- [ ] Choose output file
- [ ] Watch progress bar with ETA
- [ ] Wait for "Export complete" message
- [ ] Open exported video:
  - [ ] Overlays rendered on all frames
  - [ ] Drawings appear on correct frames
  - [ ] Playback smooth
  - [ ] No corruption

**Expected Results**: Video exports successfully with all annotations

**Codec Notes**:
- **MJPEG**: Fastest encoding, larger files (~500MB for 30sec 1080p)
- **MP4V**: Smaller files, slower encoding
- **XVID**: Good balance of size/speed

**Export Times** (estimate):
- 10-second 720p video: 30-60 seconds
- 30-second 1080p video: 2-5 minutes

---

### 9. Swing Plane Analysis
- [ ] Load video with visible club throughout swing
- [ ] Run full video analysis
- [ ] Check metrics panel for plane results:
  - [ ] Attack Angle (degrees)
  - [ ] Swing Path (degrees)
  - [ ] Plane Angle (degrees)
  - [ ] On-Plane Deviation (degrees)
- [ ] Enable "Swing Plane" overlay toggle
- [ ] Verify plane visualization:
  - [ ] Plane line/surface rendered
  - [ ] Color coding for backswing/downswing
  - [ ] Deviation markers if applicable

**Expected Results**: Plane metrics calculated, visualization appears

**Note**: Requires good club detection throughout swing

---

### 10. Keyboard Shortcuts
Test all shortcuts work:
- [ ] Ctrl+O - Open video
- [ ] Ctrl+E - Export video
- [ ] Ctrl+A - Analyze current frame
- [ ] Ctrl+Shift+A - Analyze full video
- [ ] Ctrl+D - Toggle drawing mode
- [ ] Ctrl+Z - Undo
- [ ] Ctrl+Y - Redo
- [ ] Ctrl+M - Toggle comparison mode
- [ ] Ctrl+G - Toggle angle graphs
- [ ] Ctrl+Shift+S - Save drawings
- [ ] Ctrl+Shift+O - Load drawings
- [ ] Spacebar - Play/pause
- [ ] ← → - Previous/next frame

---

## Performance Testing

### Video Specs to Test
1. **Short 720p** (5sec, 30fps) - Should be instant
2. **Medium 1080p** (15sec, 60fps) - Should be under 2 minutes
3. **Long 1080p** (60sec, 30fps) - May take 5-10 minutes
4. **4K** (10sec, 30fps) - Will be slow, recommend downsampling

### Memory Usage
- [ ] Check system memory during analysis
- [ ] Long videos should not cause memory leak
- [ ] Closing video should free memory

### Playback Performance
- [ ] 720p real-time playback at 1x speed
- [ ] 1080p playback smooth (may drop frames on slower systems)
- [ ] Overlay mode maintains smooth playback
- [ ] Graph updates don't stutter playback

---

## Bug Reporting Template

If you encounter issues, document:

```
**Issue**: Brief description
**Steps to Reproduce**:
1. Load video X
2. Click Y
3. Do Z
**Expected**: What should happen
**Actual**: What actually happened
**Video**: Resolution, fps, duration, format
**System**: OS, Python version
**Logs**: Check console output
**Screenshot**: If applicable
```

---

## Known Limitations

1. **Pose Detection**: Currently uses placeholder (MediaPipe not available for Python 3.13)
   - Skeleton and pose-based angles may show mock data
   - Will be fully functional when MediaPipe supports Python 3.13

2. **Club Detection**: Works best with:
   - High contrast (club vs background)
   - Clear shaft visibility throughout swing
   - Minimal motion blur

3. **Performance**:
   - Very long videos (>10 min) require patience
   - 4K videos should be downsampled for real-time playback

4. **Manual Drawings**: Frame-specific, not auto-interpolated between frames

---

## Success Criteria

The application is working correctly if:

✅ Videos load without errors
✅ Playback is smooth at normal speed
✅ Full analysis completes without crashes
✅ Overlays render correctly
✅ Angle graphs display accurate data
✅ Comparison mode synchronizes videos
✅ Overlay blending works in all modes
✅ Drawing tools create persistent annotations
✅ Export produces valid video/image files
✅ No memory leaks during extended use
✅ UI remains responsive during analysis

---

## Next Steps After Testing

1. **Document bugs** found during testing
2. **Prioritize fixes** based on severity
3. **Optimize performance** bottlenecks identified
4. **Enhance features** based on real-world usage
5. **Create demo video** showcasing key features

---

## Tips for Best Results

- **Camera Setup**: Front-on or side view, tripod-mounted
- **Framing**: Full body in frame, head to feet
- **Background**: Plain background helps club detection
- **Lighting**: Even lighting, avoid shadows
- **Clothing**: Contrasting colors help pose detection
- **Club**: Dark shaft against light background (or vice versa)

Happy testing! Report all findings so we can make this the best golf swing analyzer possible.
