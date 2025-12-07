# PRP: Video Overlay Mode (Alpha Blending)

## Overview
Add overlay mode to the comparison view, allowing two videos to be blended on top of each other with adjustable transparency. This provides a direct visual comparison of swing paths, body positions, and timing differences.

## Goals
- Overlay two videos with alpha blending for direct visual comparison
- Adjustable transparency slider (0-100%)
- Support for different blend modes (normal, difference, highlight)
- Frame alignment controls for proper sync
- Visual color tinting to distinguish videos
- Toggle between side-by-side and overlay modes

## Use Cases

### 1. Before/After Comparison
User wants to see exactly how their swing changed after a lesson:
- Load before video on left, after video on right
- Toggle to overlay mode
- Adjust transparency to 50%
- Apply color tints (before=red, after=green)
- Scrub through to see differences at each position

### 2. Student vs Pro Comparison
Coach overlays student swing with professional swing:
- Load student video and pro template
- Calibrate sync to align at impact
- Use overlay mode to see exact path differences
- Adjust transparency to focus on specific positions

### 3. Multi-Club Comparison
Analyze swing differences between clubs:
- Overlay driver swing vs iron swing
- See difference in swing plane and attack angle
- Identify consistent vs variable elements

## Architecture

### Components

```
ComparisonView
├── View Mode Toggle (Side-by-Side / Overlay)
├── OverlayPanel (new)
│   ├── Transparency Slider (0-100%)
│   ├── Blend Mode Selector
│   ├── Color Tint Toggles
│   └── Alignment Controls
└── OverlayRenderer (new)
    ├── Frame Blending
    ├── Color Tinting
    └── Resize/Alignment
```

### OverlayRenderer
New class in `src/comparison/overlay_renderer.py`:

```python
class OverlayRenderer:
    """Renders two video frames blended together."""

    def render(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        alpha: float = 0.5,
        blend_mode: str = 'normal',
        tint1: Optional[tuple] = None,
        tint2: Optional[tuple] = None
    ) -> np.ndarray:
        """Blend two frames together.

        Args:
            frame1: First video frame
            frame2: Second video frame
            alpha: Transparency (0.0 = only frame1, 1.0 = only frame2)
            blend_mode: 'normal', 'difference', 'multiply', 'screen'
            tint1: RGB color tint for frame1 (e.g., (255, 0, 0) for red)
            tint2: RGB color tint for frame2 (e.g., (0, 255, 0) for green)

        Returns:
            Blended frame
        """
```

**Blend Modes:**
- **Normal**: Standard alpha blending: `result = frame1 * (1-alpha) + frame2 * alpha`
- **Difference**: Highlight differences: `result = abs(frame1 - frame2)`
- **Multiply**: Darker blend: `result = (frame1 * frame2) / 255`
- **Screen**: Lighter blend: `result = 255 - ((255 - frame1) * (255 - frame2)) / 255`

### OverlayPanel
New widget in `src/comparison/overlay_panel.py`:

```python
class OverlayPanel(QWidget):
    """Control panel for overlay mode settings."""

    # Signals
    alpha_changed = pyqtSignal(float)  # 0.0 to 1.0
    blend_mode_changed = pyqtSignal(str)
    tint_toggled = pyqtSignal(str, bool)  # 'left'/'right', enabled

    def __init__(self):
        # Transparency slider (0-100)
        self.alpha_slider = QSlider(Qt.Horizontal)

        # Blend mode dropdown
        self.blend_mode_combo = QComboBox()
        # Options: Normal, Difference, Multiply, Screen

        # Color tint toggles
        self.left_tint_toggle = QCheckBox("Tint Left (Red)")
        self.right_tint_toggle = QCheckBox("Tint Right (Green)")
```

## UI/UX Design

### Comparison View with Overlay Mode

```
┌─────────────────────────────────────────────────────────────┐
│ [Load Left] [Load Right] [⇄ Swap] [🔗 Linked] [📷 Screenshot]│
│                                                              │
│  View: ◉ Side-by-Side  ○ Overlay                           │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│                    [Overlaid Video Display]                  │
│                                                              │
│                 (Both videos blended together)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ OVERLAY CONTROLS                                             │
│ Transparency: [====●====] 50%                                │
│ Blend Mode: [Normal ▼]                                       │
│ ☑ Tint Left (Red)    ☑ Tint Right (Green)                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Timeline: [==========●==============]  Frame 45 / 120       │
└─────────────────────────────────────────────────────────────┘
```

### Mode Toggle Interaction

**Side-by-Side Mode:**
- Shows both videos in splitter
- Independent overlay controls per side
- Comparison toolbar visible

**Overlay Mode:**
- Single blended video display
- Overlay controls panel visible
- Both videos play synchronized
- Transparency slider prominent

## Implementation Plan

### Phase 1: Core Blending (OverlayRenderer)
1. Create `OverlayRenderer` class
2. Implement normal alpha blending
3. Add frame resizing/alignment
4. Handle different frame sizes

### Phase 2: Advanced Blend Modes
1. Implement difference mode
2. Implement multiply mode
3. Implement screen mode
4. Add color tinting

### Phase 3: UI Controls (OverlayPanel)
1. Create overlay controls panel
2. Add transparency slider
3. Add blend mode selector
4. Add color tint toggles

### Phase 4: Integration with ComparisonView
1. Add view mode toggle (side-by-side / overlay)
2. Add overlay display area
3. Connect controls to renderer
4. Update playback to show overlaid frames

### Phase 5: Polish
1. Add keyboard shortcuts (Ctrl+O for overlay toggle)
2. Save/restore overlay settings
3. Export overlaid video option
4. Performance optimization

## Technical Details

### Frame Alignment
When videos have different resolutions:
```python
def align_frames(frame1, frame2, alignment='center'):
    """Resize and align frames for overlay.

    Args:
        frame1, frame2: Input frames
        alignment: 'center', 'top-left', 'scale-to-fit'

    Returns:
        (aligned_frame1, aligned_frame2): Same size frames
    """
    # Get target size (use larger frame or max of both)
    target_h = max(frame1.shape[0], frame2.shape[0])
    target_w = max(frame1.shape[1], frame2.shape[1])

    # Resize both to target size with padding
    # or scale one to match the other
```

### Color Tinting
Apply subtle color tints to distinguish videos:
```python
def apply_tint(frame, color, intensity=0.3):
    """Apply color tint to frame.

    Args:
        frame: Input frame (BGR)
        color: RGB color tuple (e.g., (255, 0, 0) for red)
        intensity: Tint strength (0.0-1.0)

    Returns:
        Tinted frame
    """
    # Convert color to BGR
    # Blend with original using intensity
    # Return tinted frame
```

### Performance Considerations
- Cache blended frames for smooth playback
- Use numpy operations for fast blending
- Consider GPU acceleration for real-time blending
- Limit cache size based on memory

## API Examples

### Basic Overlay
```python
# In ComparisonView
overlay_renderer = OverlayRenderer()

# Get frames from both sides
frame1 = left_side.get_frame(frame_num)
frame2 = right_side.get_frame(frame_num)

# Blend with 50% transparency
blended = overlay_renderer.render(
    frame1, frame2,
    alpha=0.5,
    blend_mode='normal'
)

# Display blended frame
overlay_display.set_frame(blended)
```

### With Color Tints
```python
# Apply red tint to left, green tint to right
blended = overlay_renderer.render(
    frame1, frame2,
    alpha=0.5,
    tint1=(255, 100, 100),  # Red tint
    tint2=(100, 255, 100)   # Green tint
)
```

### Difference Mode
```python
# Highlight differences between videos
blended = overlay_renderer.render(
    frame1, frame2,
    blend_mode='difference'
)
# Differences show as bright regions
```

## File Structure

```
src/comparison/
├── __init__.py
├── sync_controller.py
├── comparison_toolbar.py
├── comparison_view.py
├── video_side.py
├── overlay_renderer.py     # NEW: Blending engine
└── overlay_panel.py        # NEW: Control panel UI
```

## Future Enhancements

### Advanced Alignment
- Manual alignment controls (shift X/Y pixels)
- Rotation adjustment
- Scale adjustment per video

### Onion Skinning
- Show previous/next frames as ghost images
- See motion flow across multiple frames

### Split Screen Overlay
- Half-and-half overlay (left side from video 1, right from video 2)
- Useful for seeing impact position vs follow-through

### Heat Map Mode
- Accumulate multiple frames to show path density
- Visualize swing consistency

## Testing Plan

1. **Unit Tests** (`tests/test_overlay_renderer.py`)
   - Test alpha blending accuracy
   - Test blend mode calculations
   - Test frame alignment
   - Test color tinting

2. **Integration Tests**
   - Test overlay mode toggle
   - Test transparency slider
   - Test synchronized playback in overlay mode

3. **Manual Testing**
   - Test with different video resolutions
   - Test with different frame rates
   - Test playback performance
   - Test export of overlaid video

## Success Criteria

✅ Users can toggle between side-by-side and overlay modes
✅ Transparency slider smoothly blends videos (0-100%)
✅ At least 3 blend modes work correctly (normal, difference, multiply)
✅ Color tinting helps distinguish overlaid videos
✅ Videos stay synchronized in overlay mode
✅ Overlay renders at acceptable frame rate (>15 fps)
✅ Export overlaid video works correctly
✅ All code passes linting and has proper documentation

## Timeline Estimate

- **Phase 1** (OverlayRenderer core): 2-3 hours
- **Phase 2** (Blend modes & tinting): 1-2 hours
- **Phase 3** (OverlayPanel UI): 2 hours
- **Phase 4** (Integration): 2-3 hours
- **Phase 5** (Polish & testing): 1-2 hours

**Total**: ~8-12 hours of development time
