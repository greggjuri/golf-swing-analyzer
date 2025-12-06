"""Club detection module for golf swing analysis.

This module provides computer vision tools to detect and track the golf club
(shaft and head) in video frames using edge detection, Hough transforms, and
temporal tracking.

Main classes:
    ClubDetector: Detect club shaft and head in single frames
    ClubTracker: Track club across multiple frames
    FramePreprocessor: Preprocess frames for better detection

Example:
    from src.detection import ClubDetector, ClubTracker

    detector = ClubDetector()
    tracker = ClubTracker()

    result = detector.detect(frame)
    smoothed = tracker.update(result)

    if smoothed.shaft_detected:
        print(f"Shaft angle: {smoothed.shaft_angle:.1f}°")
"""

from .preprocessing import FramePreprocessor
from .club_detector import (
    ClubDetector,
    DetectionResult,
    ClubHead,
    Line,
)
from .tracking import ClubTracker

__all__ = [
    'ClubDetector',
    'DetectionResult',
    'ClubHead',
    'ClubTracker',
    'FramePreprocessor',
    'Line',
]
