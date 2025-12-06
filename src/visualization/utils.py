"""Drawing utility functions for visualization overlays."""

import logging
from typing import Tuple

import cv2
import numpy as np

from ..analysis import Point2D
from .styles import Color

logger = logging.getLogger(__name__)


def draw_text_with_background(
    frame: np.ndarray,
    text: str,
    position: Point2D,
    font: int,
    font_scale: float,
    text_color: Color,
    bg_color: Color,
    thickness: int = 2,
    bg_alpha: float = 0.7,
    padding: int = 5
) -> np.ndarray:
    """Draw text with semi-transparent background box.

    Args:
        frame: Frame to draw on
        text: Text string to display
        position: Bottom-left corner of text
        font: OpenCV font type
        font_scale: Font scale factor
        text_color: Text color (BGR)
        bg_color: Background color (BGR)
        thickness: Text thickness
        bg_alpha: Background transparency (0=transparent, 1=opaque)
        padding: Padding around text in pixels

    Returns:
        Frame with text drawn

    Raises:
        ValueError: If alpha is not in [0, 1]
    """
    if not (0 <= bg_alpha <= 1):
        raise ValueError(f"bg_alpha must be in [0, 1], got {bg_alpha}")

    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )

    x, y = int(position[0]), int(position[1])

    # Calculate background rectangle
    bg_x1 = x - padding
    bg_y1 = y - text_height - padding
    bg_x2 = x + text_width + padding
    bg_y2 = y + baseline + padding

    # Ensure within frame bounds
    h, w = frame.shape[:2]
    bg_x1 = max(0, bg_x1)
    bg_y1 = max(0, bg_y1)
    bg_x2 = min(w, bg_x2)
    bg_y2 = min(h, bg_y2)

    if bg_x2 <= bg_x1 or bg_y2 <= bg_y1:
        # Background box would be invalid, skip drawing
        logger.warning("Text background box out of frame bounds")
        return frame

    # Create overlay for background
    overlay = frame.copy()
    cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)

    # Blend overlay with frame
    frame = cv2.addWeighted(overlay, bg_alpha, frame, 1 - bg_alpha, 0)

    # Draw text
    cv2.putText(
        frame, text, (x, y),
        font, font_scale, text_color, thickness,
        lineType=cv2.LINE_AA
    )

    return frame


def draw_line_with_arrow(
    frame: np.ndarray,
    start: Point2D,
    end: Point2D,
    color: Color,
    thickness: int = 2,
    tip_length: float = 0.1
) -> np.ndarray:
    """Draw line with arrowhead at end.

    Args:
        frame: Frame to draw on
        start: Start point (x, y)
        end: End point (x, y)
        color: Line color (BGR)
        thickness: Line thickness
        tip_length: Arrow tip length as fraction of line length

    Returns:
        Frame with arrow drawn
    """
    start_pt = (int(start[0]), int(start[1]))
    end_pt = (int(end[0]), int(end[1]))

    cv2.arrowedLine(
        frame, start_pt, end_pt, color, thickness,
        tipLength=tip_length,
        line_type=cv2.LINE_AA
    )

    return frame


def draw_angle_arc(
    frame: np.ndarray,
    center: Point2D,
    radius: int,
    start_angle: float,
    end_angle: float,
    color: Color,
    thickness: int = 2
) -> np.ndarray:
    """Draw angle arc using OpenCV ellipse function.

    Draws an arc to visualize an angle. Handles angle wraparound.

    Args:
        frame: Frame to draw on
        center: Center point of arc (x, y)
        radius: Arc radius in pixels
        start_angle: Start angle in degrees (0=right, increases counter-clockwise)
        end_angle: End angle in degrees
        color: Arc color (BGR)
        thickness: Arc thickness

    Returns:
        Frame with arc drawn
    """
    # Work on a copy to avoid unexpected side effects
    result = frame.copy() if not frame.flags.writeable else frame

    # Convert angles to OpenCV format (0=right, increases clockwise)
    # Our angles: 0=right, increases counter-clockwise (math convention)
    # OpenCV angles: 0=right, increases clockwise
    cv_start_angle = -start_angle
    cv_end_angle = -end_angle

    # Ensure start < end for OpenCV
    if cv_start_angle > cv_end_angle:
        cv_start_angle, cv_end_angle = cv_end_angle, cv_start_angle

    center_pt = (int(center[0]), int(center[1]))

    cv2.ellipse(
        result,
        center_pt,
        (radius, radius),
        0,  # Angle of ellipse (rotation)
        cv_start_angle,
        cv_end_angle,
        color,
        thickness,
        lineType=cv2.LINE_AA
    )

    return result


def blend_overlay(
    frame: np.ndarray,
    overlay: np.ndarray,
    alpha: float
) -> np.ndarray:
    """Blend overlay onto frame with alpha transparency.

    Args:
        frame: Base frame
        overlay: Overlay frame (same size as frame)
        alpha: Overlay opacity (0=transparent, 1=opaque)

    Returns:
        Blended frame

    Raises:
        ValueError: If frames have different shapes or alpha not in [0, 1]
    """
    if frame.shape != overlay.shape:
        raise ValueError(
            f"Frame and overlay must have same shape, "
            f"got {frame.shape} and {overlay.shape}"
        )

    if not (0 <= alpha <= 1):
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")

    blended = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    return blended


def draw_confidence_bar(
    frame: np.ndarray,
    position: Point2D,
    confidence: float,
    width: int = 100,
    height: int = 10,
    color: Color = (0, 255, 0),
    bg_color: Color = (50, 50, 50)
) -> np.ndarray:
    """Draw confidence score as horizontal bar.

    Args:
        frame: Frame to draw on
        position: Top-left corner of bar
        confidence: Confidence score (0-1)
        width: Bar width in pixels
        height: Bar height in pixels
        color: Bar fill color (BGR)
        bg_color: Bar background color (BGR)

    Returns:
        Frame with confidence bar drawn

    Raises:
        ValueError: If confidence not in [0, 1]
    """
    if not (0 <= confidence <= 1):
        raise ValueError(f"confidence must be in [0, 1], got {confidence}")

    x, y = int(position[0]), int(position[1])

    # Draw background
    cv2.rectangle(frame, (x, y), (x + width, y + height), bg_color, -1)

    # Draw filled portion
    filled_width = int(width * confidence)
    if filled_width > 0:
        cv2.rectangle(frame, (x, y), (x + filled_width, y + height), color, -1)

    # Draw border
    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 1)

    return frame


def get_text_size(
    text: str,
    font: int,
    font_scale: float,
    thickness: int
) -> Tuple[int, int]:
    """Get size of text when rendered.

    Args:
        text: Text string
        font: OpenCV font type
        font_scale: Font scale factor
        thickness: Text thickness

    Returns:
        Tuple of (width, height) in pixels
    """
    (text_width, text_height), _ = cv2.getTextSize(
        text, font, font_scale, thickness
    )
    return (text_width, text_height)
