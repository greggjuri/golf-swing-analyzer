"""Styling configuration for visualization overlays.

This module defines color schemes, fonts, and styling options for
rendering overlays on video frames.
"""

import cv2
from dataclasses import dataclass
from typing import Tuple, Optional

from ..analysis import Point2D


# Type alias for BGR color
Color = Tuple[int, int, int]


@dataclass
class StyleConfig:
    """Configuration for visualization styling.

    All colors are in BGR format (OpenCV convention).

    Example:
        # Use default style
        style = StyleConfig()

        # Use high-contrast preset
        style = StyleConfig.high_contrast()

        # Custom style
        style = StyleConfig(
            shaft_color=(0, 255, 0),
            shaft_thickness=4
        )
    """

    # Club visualization
    shaft_color: Color = (0, 255, 0)  # Green
    shaft_thickness: int = 3
    club_head_color: Color = (0, 0, 255)  # Red
    club_head_thickness: int = 2

    # Body skeleton
    skeleton_color: Color = (255, 255, 0)  # Cyan
    skeleton_thickness: int = 2
    joint_color: Color = (255, 0, 255)  # Magenta
    joint_radius: int = 5
    left_side_color: Color = (0, 255, 0)  # Green for left side
    right_side_color: Color = (0, 0, 255)  # Red for right side

    # Angle visualization
    angle_arc_color: Color = (0, 165, 255)  # Orange (BGR)
    angle_thickness: int = 2
    angle_arc_radius: int = 30

    # Text styling
    font: int = cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.6
    font_thickness: int = 2
    text_color: Color = (255, 255, 255)  # White
    text_bg_color: Color = (0, 0, 0)  # Black
    text_bg_alpha: float = 0.7
    text_padding: int = 5

    # General settings
    antialiasing: bool = True
    confidence_threshold: float = 0.3  # Don't draw if confidence below this

    @classmethod
    def high_contrast(cls) -> 'StyleConfig':
        """Create high-contrast color scheme for better visibility.

        Uses bright, saturated colors with thicker lines.

        Returns:
            StyleConfig with high-contrast settings
        """
        return cls(
            shaft_color=(0, 255, 0),  # Bright green
            shaft_thickness=4,
            club_head_color=(255, 0, 255),  # Bright magenta
            club_head_thickness=3,
            skeleton_color=(0, 255, 255),  # Bright cyan
            skeleton_thickness=3,
            joint_color=(255, 255, 0),  # Bright yellow
            joint_radius=7,
            angle_arc_color=(0, 128, 255),  # Bright orange
            angle_thickness=3,
            font_scale=0.7,
            font_thickness=2,
            text_color=(255, 255, 255),
            text_bg_color=(0, 0, 0),
            text_bg_alpha=0.8,
        )

    @classmethod
    def colorblind_friendly(cls) -> 'StyleConfig':
        """Create colorblind-friendly color scheme.

        Uses colors distinguishable by people with common color vision
        deficiencies (deuteranopia, protanopia).

        Colors based on Paul Tol's colorblind-friendly palette.

        Returns:
            StyleConfig with colorblind-friendly settings
        """
        return cls(
            shaft_color=(221, 170, 51),  # Blue (BGR)
            shaft_thickness=3,
            club_head_color=(17, 119, 51),  # Vermillion (BGR)
            club_head_thickness=2,
            skeleton_color=(204, 121, 167),  # Reddish purple
            skeleton_thickness=2,
            joint_color=(136, 204, 238),  # Orange
            joint_radius=5,
            left_side_color=(221, 170, 51),  # Blue
            right_side_color=(136, 204, 238),  # Orange
            angle_arc_color=(136, 34, 85),  # Bluish green (BGR)
            angle_thickness=2,
            font_scale=0.6,
            font_thickness=2,
            text_color=(255, 255, 255),
            text_bg_color=(0, 0, 0),
            text_bg_alpha=0.7,
        )

    @classmethod
    def minimal(cls) -> 'StyleConfig':
        """Create minimal color scheme with subtle overlays.

        Returns:
            StyleConfig with minimal settings
        """
        return cls(
            shaft_color=(100, 150, 100),  # Muted green
            shaft_thickness=2,
            club_head_color=(100, 100, 150),  # Muted red
            club_head_thickness=1,
            skeleton_color=(150, 150, 100),  # Muted cyan
            skeleton_thickness=1,
            joint_color=(150, 100, 150),  # Muted magenta
            joint_radius=3,
            angle_arc_color=(100, 130, 150),  # Muted orange
            angle_thickness=1,
            font_scale=0.5,
            font_thickness=1,
            text_color=(200, 200, 200),
            text_bg_color=(30, 30, 30),
            text_bg_alpha=0.5,
        )


@dataclass
class Annotation:
    """Text annotation to draw on frame.

    Attributes:
        text: Text string to display
        position: Position (x, y) for text
        font_scale: Optional custom font scale
        color: Optional custom text color (BGR)
        background: Whether to draw background box
        alignment: Text alignment ('left', 'center', 'right')
    """
    text: str
    position: Point2D
    font_scale: Optional[float] = None
    color: Optional[Color] = None
    background: bool = True
    alignment: str = 'left'

    def __post_init__(self):
        """Validate alignment."""
        if self.alignment not in ['left', 'center', 'right']:
            raise ValueError(
                f"alignment must be 'left', 'center', or 'right', "
                f"got '{self.alignment}'"
            )
