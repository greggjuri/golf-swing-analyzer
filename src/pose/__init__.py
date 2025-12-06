"""Pose detection and landmark extraction.

This module provides pose detection using MediaPipe (when available)
and tools for extracting body positions, joint angles, and golf-specific
measurements.

NOTE: MediaPipe is not yet available for Python 3.13. This module currently
uses a placeholder implementation for testing. When MediaPipe becomes available,
the implementation will be updated without changing the public API.

Main components:
- PoseDetector: Detect human pose in images
- PoseResult: Container for detected landmarks
- LandmarkExtractor: Extract positions and calculate angles
- PoseTracker: Multi-frame tracking with smoothing
- PoseLandmark: Enum of 33 body landmarks

Example:
    from src.pose import PoseDetector, LandmarkExtractor, PoseLandmark

    # Detect pose
    detector = PoseDetector()
    result = detector.detect(frame)

    # Extract measurements
    extractor = LandmarkExtractor(frame.shape[1], frame.shape[0])

    if result:
        spine_angle = extractor.get_spine_angle(result)
        elbow_angle = extractor.get_joint_angle(
            result,
            PoseLandmark.LEFT_ELBOW,
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.LEFT_WRIST
        )

    detector.close()
"""

from .landmarks import (
    PoseLandmark,
    LandmarkPoint,
    POSE_CONNECTIONS,
    BODY_SEGMENTS,
    GOLF_KEY_LANDMARKS,
    get_landmark_name,
    is_left_side,
    is_right_side,
    get_landmark_pair,
)

from .detector import (
    PoseDetector,
    PoseResult,
)

from .extractor import (
    LandmarkExtractor,
)

from .tracker import (
    PoseTracker,
)

__all__ = [
    # Landmarks
    'PoseLandmark',
    'LandmarkPoint',
    'POSE_CONNECTIONS',
    'BODY_SEGMENTS',
    'GOLF_KEY_LANDMARKS',
    'get_landmark_name',
    'is_left_side',
    'is_right_side',
    'get_landmark_pair',

    # Detection
    'PoseDetector',
    'PoseResult',

    # Extraction
    'LandmarkExtractor',

    # Tracking
    'PoseTracker',
]
