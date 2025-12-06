# Golf Swing Analyzer - Architecture & Planning

## Goal
Desktop application to analyze golf swing videos taken from directly behind the golfer.
Draw lines showing swing plane, measure angles of joints/club positions, enable 
frame-by-frame analysis to identify swing issues.

## Target User
Single user (me) on Debian desktop. Videos transferred from iPhone.

## Core Features
1. **Video Import**: Load .mov/.mp4 files from iPhone
2. **Frame Extraction**: Step through video frame-by-frame or auto-detect key positions
3. **Pose Detection**: Identify body landmarks (shoulders, hips, knees, wrists, elbows)
4. **Club Detection**: Track club shaft position through swing
5. **Analysis Tools**:
   - Swing plane line (from ball through hands at address)
   - Spine angle at address/impact
   - Knee flex angle
   - Wrist hinge angle at top of backswing
   - Club shaft angle at various positions
   - Club face direction at various positions
6. **Visualization**: Draw lines/angles on frames, export annotated images/videos
7. **Comparison**: Side-by-side comparison of two swings

## Key Swing Positions to Analyze
- P1: Address
- P2: Club parallel to ground (backswing)
- P3: Arm parallel to ground (backswing)  
- P4: Top of backswing
- P5: Arm parallel (downswing)
- P6: Club parallel (downswing)
- P7: Impact
- P8: Extension/follow-through

## Architecture
golf-swing-analyzer/
├── src/
│   ├── init.py
│   ├── main.py              # Application entry point
│   ├── video/
│   │   ├── init.py
│   │   ├── loader.py        # Video file loading, format handling
│   │   └── frame_extractor.py  # Frame extraction, key position detection
│   ├── detection/
│   │   ├── init.py
│   │   ├── pose_detector.py    # MediaPipe pose detection wrapper
│   │   └── club_detector.py    # Club shaft detection (edge detection + Hough)
│   ├── analysis/
│   │   ├── init.py
│   │   ├── angles.py           # Angle calculation utilities
│   │   ├── swing_plane.py      # Swing plane analysis
│   │   └── positions.py        # Key position identification (P1-P8)
│   ├── visualization/
│   │   ├── init.py
│   │   ├── overlays.py         # Draw lines, angles, annotations
│   │   └── export.py           # Save annotated images/videos
│   └── gui/
│       ├── init.py
│       ├── main_window.py      # Main application window
│       ├── video_player.py     # Video playback widget
│       ├── analysis_panel.py   # Analysis controls and display
│       └── drawing_tools.py    # Manual line drawing tools
├── tests/
├── examples/
├── data/                    # Sample videos for testing
├── output/                  # Generated analysis outputs
├── CLAUDE.md
├── PLANNING.md
├── TASK.md
├── requirements.txt
└── README.md

## Technical Decisions
- **Pose Detection**: MediaPipe Pose (33 landmarks, real-time capable)
- **GUI Framework**: PyQt5 (mature, good OpenCV integration)
- **Video Handling**: OpenCV VideoCapture
- **Image Processing**: OpenCV + NumPy

## Constraints
- Must handle iPhone video formats (.mov, HEVC codec)
- Frame rate typically 30-60fps
- Resolution up to 4K (may need to downsample for performance)