#!/usr/bin/env python3
"""Demonstration of F1-styled GUI main window.

This script launches the Golf Swing Analyzer application with
the premium F1 design studio aesthetic.

Features demonstrated:
1. F1 theme with glass morphism and metallic accents
2. Video player with professional playback controls
3. Analysis panel with metric displays and overlay toggles
4. Timeline scrubber with key position markers
5. Menu bar and toolbar for common actions

Run with: python examples/gui_demo.py [video_file]
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.gui import MainWindow


def main():
    """Launch GUI demonstration."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Golf Swing Analyzer - F1 Studio")

    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create main window
    window = MainWindow()
    window.show()

    # If video file provided as argument, load it
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if Path(video_path).exists():
            window._load_video(video_path)
        else:
            print(f"Warning: Video file not found: {video_path}")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    print("="*70)
    print("  Golf Swing Analyzer - F1 Studio")
    print("="*70)
    print("\nF1 Design Features:")
    print("  • Glass morphism with frosted blur effects")
    print("  • Black/White/Silver premium color scheme")
    print("  • Metallic button gradients and accents")
    print("  • Professional video playback controls")
    print("  • Real-time metrics display")
    print("  • Timeline scrubber with key position markers")
    print("\nUsage:")
    print("  python examples/gui_demo.py [video_file]")
    print("\nControls:")
    print("  • File → Open Video to load a video")
    print("  • ▶ / ⏸ to play/pause")
    print("  • ◀◀ / ▶▶ for frame-by-frame navigation")
    print("  • Drag timeline scrubber to seek")
    print("  • Toggle overlays in Analysis Panel")
    print("="*70)
    print()

    main()
