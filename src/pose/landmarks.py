"""Pose landmark definitions and utilities.

Defines the 33 MediaPipe pose landmarks and their relationships.
"""

from enum import Enum
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass


class PoseLandmark(Enum):
    """MediaPipe pose landmarks (33 points)."""

    # Face
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10

    # Upper body
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22

    # Lower body
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


@dataclass
class LandmarkPoint:
    """Single landmark point with position and confidence."""

    x: float  # Normalized 0-1 (or pixel coordinates)
    y: float  # Normalized 0-1 (or pixel coordinates)
    z: float  # Depth (for world landmarks)
    visibility: float  # 0-1 confidence
    presence: float  # 0-1 likelihood of being in frame


# Pose skeleton connections (for drawing)
POSE_CONNECTIONS: List[Tuple[PoseLandmark, PoseLandmark]] = [
    # Face
    (PoseLandmark.NOSE, PoseLandmark.LEFT_EYE_INNER),
    (PoseLandmark.LEFT_EYE_INNER, PoseLandmark.LEFT_EYE),
    (PoseLandmark.LEFT_EYE, PoseLandmark.LEFT_EYE_OUTER),
    (PoseLandmark.LEFT_EYE_OUTER, PoseLandmark.LEFT_EAR),
    (PoseLandmark.NOSE, PoseLandmark.RIGHT_EYE_INNER),
    (PoseLandmark.RIGHT_EYE_INNER, PoseLandmark.RIGHT_EYE),
    (PoseLandmark.RIGHT_EYE, PoseLandmark.RIGHT_EYE_OUTER),
    (PoseLandmark.RIGHT_EYE_OUTER, PoseLandmark.RIGHT_EAR),
    (PoseLandmark.MOUTH_LEFT, PoseLandmark.MOUTH_RIGHT),

    # Torso
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER),
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP),
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP),
    (PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP),

    # Left arm
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW),
    (PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST),
    (PoseLandmark.LEFT_WRIST, PoseLandmark.LEFT_PINKY),
    (PoseLandmark.LEFT_WRIST, PoseLandmark.LEFT_INDEX),
    (PoseLandmark.LEFT_WRIST, PoseLandmark.LEFT_THUMB),
    (PoseLandmark.LEFT_PINKY, PoseLandmark.LEFT_INDEX),

    # Right arm
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW),
    (PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST),
    (PoseLandmark.RIGHT_WRIST, PoseLandmark.RIGHT_PINKY),
    (PoseLandmark.RIGHT_WRIST, PoseLandmark.RIGHT_INDEX),
    (PoseLandmark.RIGHT_WRIST, PoseLandmark.RIGHT_THUMB),
    (PoseLandmark.RIGHT_PINKY, PoseLandmark.RIGHT_INDEX),

    # Left leg
    (PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE),
    (PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE),
    (PoseLandmark.LEFT_ANKLE, PoseLandmark.LEFT_HEEL),
    (PoseLandmark.LEFT_ANKLE, PoseLandmark.LEFT_FOOT_INDEX),
    (PoseLandmark.LEFT_HEEL, PoseLandmark.LEFT_FOOT_INDEX),

    # Right leg
    (PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE),
    (PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE),
    (PoseLandmark.RIGHT_ANKLE, PoseLandmark.RIGHT_HEEL),
    (PoseLandmark.RIGHT_ANKLE, PoseLandmark.RIGHT_FOOT_INDEX),
    (PoseLandmark.RIGHT_HEEL, PoseLandmark.RIGHT_FOOT_INDEX),
]


# Body segment groups (for analysis)
BODY_SEGMENTS: Dict[str, List[PoseLandmark]] = {
    'face': [
        PoseLandmark.NOSE,
        PoseLandmark.LEFT_EYE,
        PoseLandmark.RIGHT_EYE,
        PoseLandmark.LEFT_EAR,
        PoseLandmark.RIGHT_EAR,
        PoseLandmark.MOUTH_LEFT,
        PoseLandmark.MOUTH_RIGHT,
    ],
    'torso': [
        PoseLandmark.LEFT_SHOULDER,
        PoseLandmark.RIGHT_SHOULDER,
        PoseLandmark.RIGHT_HIP,
        PoseLandmark.LEFT_HIP,
    ],
    'left_arm': [
        PoseLandmark.LEFT_SHOULDER,
        PoseLandmark.LEFT_ELBOW,
        PoseLandmark.LEFT_WRIST,
    ],
    'right_arm': [
        PoseLandmark.RIGHT_SHOULDER,
        PoseLandmark.RIGHT_ELBOW,
        PoseLandmark.RIGHT_WRIST,
    ],
    'left_hand': [
        PoseLandmark.LEFT_WRIST,
        PoseLandmark.LEFT_THUMB,
        PoseLandmark.LEFT_INDEX,
        PoseLandmark.LEFT_PINKY,
    ],
    'right_hand': [
        PoseLandmark.RIGHT_WRIST,
        PoseLandmark.RIGHT_THUMB,
        PoseLandmark.RIGHT_INDEX,
        PoseLandmark.RIGHT_PINKY,
    ],
    'left_leg': [
        PoseLandmark.LEFT_HIP,
        PoseLandmark.LEFT_KNEE,
        PoseLandmark.LEFT_ANKLE,
    ],
    'right_leg': [
        PoseLandmark.RIGHT_HIP,
        PoseLandmark.RIGHT_KNEE,
        PoseLandmark.RIGHT_ANKLE,
    ],
    'left_foot': [
        PoseLandmark.LEFT_ANKLE,
        PoseLandmark.LEFT_HEEL,
        PoseLandmark.LEFT_FOOT_INDEX,
    ],
    'right_foot': [
        PoseLandmark.RIGHT_ANKLE,
        PoseLandmark.RIGHT_HEEL,
        PoseLandmark.RIGHT_FOOT_INDEX,
    ],
}


# Key landmarks for golf swing analysis
GOLF_KEY_LANDMARKS: Set[PoseLandmark] = {
    # Head
    PoseLandmark.NOSE,

    # Shoulders
    PoseLandmark.LEFT_SHOULDER,
    PoseLandmark.RIGHT_SHOULDER,

    # Arms
    PoseLandmark.LEFT_ELBOW,
    PoseLandmark.RIGHT_ELBOW,
    PoseLandmark.LEFT_WRIST,
    PoseLandmark.RIGHT_WRIST,

    # Hips
    PoseLandmark.LEFT_HIP,
    PoseLandmark.RIGHT_HIP,

    # Legs
    PoseLandmark.LEFT_KNEE,
    PoseLandmark.RIGHT_KNEE,
    PoseLandmark.LEFT_ANKLE,
    PoseLandmark.RIGHT_ANKLE,
}


def get_landmark_name(landmark: PoseLandmark) -> str:
    """Get human-readable name for landmark.

    Args:
        landmark: PoseLandmark enum value

    Returns:
        Human-readable name (e.g., "Left Shoulder")
    """
    name = landmark.name.replace('_', ' ').title()
    return name


def is_left_side(landmark: PoseLandmark) -> bool:
    """Check if landmark is on left side of body.

    Args:
        landmark: PoseLandmark enum value

    Returns:
        True if left-side landmark
    """
    return 'LEFT' in landmark.name


def is_right_side(landmark: PoseLandmark) -> bool:
    """Check if landmark is on right side of body.

    Args:
        landmark: PoseLandmark enum value

    Returns:
        True if right-side landmark
    """
    return 'RIGHT' in landmark.name


def get_landmark_pair(landmark: PoseLandmark) -> PoseLandmark:
    """Get corresponding landmark on opposite side.

    Args:
        landmark: PoseLandmark enum value

    Returns:
        Corresponding landmark on opposite side

    Raises:
        ValueError: If landmark has no pair (e.g., NOSE)
    """
    name = landmark.name

    if 'LEFT' in name:
        pair_name = name.replace('LEFT', 'RIGHT')
    elif 'RIGHT' in name:
        pair_name = name.replace('RIGHT', 'LEFT')
    else:
        raise ValueError(f"Landmark {landmark.name} has no pair")

    return PoseLandmark[pair_name]
