"""Specialized renderers for different overlay types."""

import logging
from typing import Optional, Dict

import cv2
import numpy as np

from ..analysis import Point2D, JointAngleCalculator, BodyLandmark
from ..detection import DetectionResult
from .styles import StyleConfig
from .utils import (
    draw_text_with_background,
    draw_angle_arc,
    draw_confidence_bar,
)

logger = logging.getLogger(__name__)


class ClubRenderer:
    """Render club shaft and head overlays.

    Example:
        renderer = ClubRenderer(style)
        frame = renderer.draw_shaft(frame, shaft_line, angle=45.0)
        frame = renderer.draw_club_head(frame, center, radius)
    """

    def __init__(self, style: StyleConfig):
        """Initialize renderer with style configuration.

        Args:
            style: Style configuration
        """
        self.style = style
        logger.debug("Initialized ClubRenderer")

    def draw_shaft(
        self,
        frame: np.ndarray,
        shaft_line: tuple,
        shaft_angle: Optional[float] = None,
        confidence: Optional[float] = None,
        show_angle: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """Draw club shaft line with optional annotations.

        Args:
            frame: Frame to draw on
            shaft_line: Shaft endpoints (x1, y1, x2, y2)
            shaft_angle: Optional shaft angle in degrees
            confidence: Optional confidence score (0-1)
            show_angle: Whether to show angle label
            show_confidence: Whether to show confidence score

        Returns:
            Frame with shaft drawn
        """
        x1, y1, x2, y2 = shaft_line

        # Draw shaft line
        line_type = cv2.LINE_AA if self.style.antialiasing else cv2.LINE_8
        cv2.line(
            frame,
            (x1, y1),
            (x2, y2),
            self.style.shaft_color,
            self.style.shaft_thickness,
            lineType=line_type
        )

        # Draw angle label if provided
        if show_angle and shaft_angle is not None:
            # Position label near middle of shaft
            label_x = (x1 + x2) // 2 + 15
            label_y = (y1 + y2) // 2

            angle_text = f"{shaft_angle:.1f}°"
            frame = draw_text_with_background(
                frame,
                angle_text,
                (label_x, label_y),
                self.style.font,
                self.style.font_scale,
                self.style.text_color,
                self.style.text_bg_color,
                self.style.font_thickness,
                self.style.text_bg_alpha,
                self.style.text_padding
            )

        # Draw confidence bar if provided
        if show_confidence and confidence is not None:
            # Position bar near shaft start (grip end)
            bar_x = x1 - 110
            bar_y = y1 - 25

            # Ensure bar is within frame
            if bar_x >= 0 and bar_y >= 0:
                frame = draw_confidence_bar(
                    frame,
                    (bar_x, bar_y),
                    confidence,
                    width=100,
                    height=8,
                    color=self.style.shaft_color
                )

                # Add "Conf:" label
                conf_text = "Conf:"
                frame = draw_text_with_background(
                    frame,
                    conf_text,
                    (bar_x, bar_y - 5),
                    self.style.font,
                    self.style.font_scale * 0.7,
                    self.style.text_color,
                    self.style.text_bg_color,
                    1,
                    self.style.text_bg_alpha,
                    3
                )

        return frame

    def draw_club_head(
        self,
        frame: np.ndarray,
        center: Point2D,
        radius: float
    ) -> np.ndarray:
        """Draw club head circle.

        Args:
            frame: Frame to draw on
            center: Club head center point (x, y)
            radius: Club head radius in pixels

        Returns:
            Frame with club head drawn
        """
        center_pt = (int(center[0]), int(center[1]))
        radius_int = int(radius)

        line_type = cv2.LINE_AA if self.style.antialiasing else cv2.LINE_8

        # Draw circle
        cv2.circle(
            frame,
            center_pt,
            radius_int,
            self.style.club_head_color,
            self.style.club_head_thickness,
            lineType=line_type
        )

        # Draw center point
        cv2.circle(
            frame,
            center_pt,
            3,
            self.style.club_head_color,
            -1,
            lineType=line_type
        )

        return frame

    def render(
        self,
        frame: np.ndarray,
        detection: DetectionResult,
        show_angles: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """Render complete club overlay from detection result.

        Args:
            frame: Frame to draw on
            detection: Club detection result
            show_angles: Whether to show angle measurements
            show_confidence: Whether to show confidence scores

        Returns:
            Frame with club overlay
        """
        # Check confidence threshold
        if detection.confidence < self.style.confidence_threshold:
            logger.debug(
                f"Skipping club render, confidence {detection.confidence:.2f} "
                f"below threshold {self.style.confidence_threshold}"
            )
            return frame

        # Draw shaft if detected
        if detection.shaft_detected and detection.shaft_line is not None:
            frame = self.draw_shaft(
                frame,
                detection.shaft_line,
                detection.shaft_angle,
                detection.confidence,
                show_angles,
                show_confidence
            )

        # Draw club head if detected
        if (detection.club_head_detected and
                detection.club_head_center is not None and
                detection.club_head_radius is not None):
            frame = self.draw_club_head(
                frame,
                detection.club_head_center,
                detection.club_head_radius
            )

        return frame


class AngleRenderer:
    """Render angle arcs and measurements.

    Example:
        renderer = AngleRenderer(style)
        frame = renderer.draw_angle_arc(frame, vertex, p1, p2, angle=90.0)
    """

    def __init__(self, style: StyleConfig):
        """Initialize renderer with style configuration.

        Args:
            style: Style configuration
        """
        self.style = style
        logger.debug("Initialized AngleRenderer")

    def draw_angle_with_arc(
        self,
        frame: np.ndarray,
        vertex: Point2D,
        point1: Point2D,
        point2: Point2D,
        angle: float,
        radius: Optional[int] = None,
        show_label: bool = True,
        label_prefix: str = ""
    ) -> np.ndarray:
        """Draw angle arc between three points with label.

        Args:
            frame: Frame to draw on
            vertex: Vertex point of angle
            point1: First point
            point2: Second point
            angle: Angle in degrees
            radius: Arc radius (uses style default if None)
            show_label: Whether to show angle label
            label_prefix: Optional prefix for label (e.g., "Elbow: ")

        Returns:
            Frame with angle arc drawn
        """
        if radius is None:
            radius = self.style.angle_arc_radius

        # Calculate start and end angles for arc
        # Angle from vertex to point1
        dx1 = point1[0] - vertex[0]
        dy1 = point1[1] - vertex[1]
        start_angle = np.degrees(np.arctan2(-dy1, dx1))  # -dy for image coords

        # Angle from vertex to point2
        dx2 = point2[0] - vertex[0]
        dy2 = point2[1] - vertex[1]
        end_angle = np.degrees(np.arctan2(-dy2, dx2))

        # Draw arc
        frame = draw_angle_arc(
            frame,
            vertex,
            radius,
            start_angle,
            end_angle,
            self.style.angle_arc_color,
            self.style.angle_thickness
        )

        # Draw angle label
        if show_label:
            # Position label slightly outside arc
            label_angle_rad = np.radians((start_angle + end_angle) / 2)
            label_distance = radius + 20
            label_x = vertex[0] + label_distance * np.cos(label_angle_rad)
            label_y = vertex[1] - label_distance * np.sin(label_angle_rad)

            label_text = f"{label_prefix}{angle:.0f}°"
            frame = draw_text_with_background(
                frame,
                label_text,
                (label_x, label_y),
                self.style.font,
                self.style.font_scale * 0.8,
                self.style.text_color,
                self.style.text_bg_color,
                self.style.font_thickness,
                self.style.text_bg_alpha,
                self.style.text_padding
            )

        return frame


class BodyRenderer:
    """Render body skeleton and joint overlays.

    Example:
        renderer = BodyRenderer(style, handedness="right")
        frame = renderer.draw_skeleton(frame, landmarks)
        frame = renderer.draw_joint_angles(frame, landmarks, calculator)
    """

    # Skeleton connections (MediaPipe format)
    SKELETON_CONNECTIONS = [
        # Torso
        (BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER),
        (BodyLandmark.LEFT_SHOULDER, BodyLandmark.LEFT_HIP),
        (BodyLandmark.RIGHT_SHOULDER, BodyLandmark.RIGHT_HIP),
        (BodyLandmark.LEFT_HIP, BodyLandmark.RIGHT_HIP),
        # Left arm
        (BodyLandmark.LEFT_SHOULDER, BodyLandmark.LEFT_ELBOW),
        (BodyLandmark.LEFT_ELBOW, BodyLandmark.LEFT_WRIST),
        # Right arm
        (BodyLandmark.RIGHT_SHOULDER, BodyLandmark.RIGHT_ELBOW),
        (BodyLandmark.RIGHT_ELBOW, BodyLandmark.RIGHT_WRIST),
        # Left leg
        (BodyLandmark.LEFT_HIP, BodyLandmark.LEFT_KNEE),
        (BodyLandmark.LEFT_KNEE, BodyLandmark.LEFT_ANKLE),
        # Right leg
        (BodyLandmark.RIGHT_HIP, BodyLandmark.RIGHT_KNEE),
        (BodyLandmark.RIGHT_KNEE, BodyLandmark.RIGHT_ANKLE),
    ]

    def __init__(self, style: StyleConfig, handedness: str = "right"):
        """Initialize renderer with style configuration.

        Args:
            style: Style configuration
            handedness: Golfer handedness ("right" or "left")
        """
        self.style = style
        self.handedness = handedness
        logger.debug(f"Initialized BodyRenderer for {handedness}-handed golfer")

    def draw_skeleton(
        self,
        frame: np.ndarray,
        landmarks: Dict[int, Point2D]
    ) -> np.ndarray:
        """Draw full body skeleton.

        Args:
            frame: Frame to draw on
            landmarks: Dictionary mapping landmark indices to (x, y) positions

        Returns:
            Frame with skeleton drawn
        """
        line_type = cv2.LINE_AA if self.style.antialiasing else cv2.LINE_8

        # Draw connections
        for landmark1_idx, landmark2_idx in self.SKELETON_CONNECTIONS:
            if landmark1_idx in landmarks and landmark2_idx in landmarks:
                pt1 = landmarks[landmark1_idx]
                pt2 = landmarks[landmark2_idx]

                # Use left/right specific colors if available
                color = self.style.skeleton_color
                if landmark1_idx in [
                    BodyLandmark.LEFT_SHOULDER, BodyLandmark.LEFT_ELBOW,
                    BodyLandmark.LEFT_WRIST, BodyLandmark.LEFT_HIP,
                    BodyLandmark.LEFT_KNEE, BodyLandmark.LEFT_ANKLE
                ]:
                    color = self.style.left_side_color
                elif landmark1_idx in [
                    BodyLandmark.RIGHT_SHOULDER, BodyLandmark.RIGHT_ELBOW,
                    BodyLandmark.RIGHT_WRIST, BodyLandmark.RIGHT_HIP,
                    BodyLandmark.RIGHT_KNEE, BodyLandmark.RIGHT_ANKLE
                ]:
                    color = self.style.right_side_color

                cv2.line(
                    frame,
                    (int(pt1[0]), int(pt1[1])),
                    (int(pt2[0]), int(pt2[1])),
                    color,
                    self.style.skeleton_thickness,
                    lineType=line_type
                )

        # Draw joint points
        for landmark_idx, position in landmarks.items():
            cv2.circle(
                frame,
                (int(position[0]), int(position[1])),
                self.style.joint_radius,
                self.style.joint_color,
                -1,
                lineType=line_type
            )

        return frame

    def draw_joint_angles(
        self,
        frame: np.ndarray,
        landmarks: Dict[int, Point2D],
        joint_calculator: JointAngleCalculator,
        angle_renderer: AngleRenderer,
        show_labels: bool = True
    ) -> np.ndarray:
        """Draw joint angles with arcs and labels.

        Args:
            frame: Frame to draw on
            landmarks: Body landmark positions
            joint_calculator: Calculator for joint angles
            angle_renderer: AngleRenderer instance
            show_labels: Whether to show angle labels

        Returns:
            Frame with joint angles drawn
        """
        # Draw elbow angle (if landmarks available)
        if (BodyLandmark.LEFT_SHOULDER in landmarks and
                BodyLandmark.LEFT_ELBOW in landmarks and
                BodyLandmark.LEFT_WRIST in landmarks):

            shoulder = landmarks[BodyLandmark.LEFT_SHOULDER]
            elbow = landmarks[BodyLandmark.LEFT_ELBOW]
            wrist = landmarks[BodyLandmark.LEFT_WRIST]

            angle = joint_calculator.elbow_angle(shoulder, elbow, wrist)

            frame = angle_renderer.draw_angle_with_arc(
                frame,
                vertex=elbow,
                point1=shoulder,
                point2=wrist,
                angle=angle,
                show_label=show_labels,
                label_prefix="Elbow: "
            )

        # Draw knee angle (if landmarks available)
        if (BodyLandmark.LEFT_HIP in landmarks and
                BodyLandmark.LEFT_KNEE in landmarks and
                BodyLandmark.LEFT_ANKLE in landmarks):

            hip = landmarks[BodyLandmark.LEFT_HIP]
            knee = landmarks[BodyLandmark.LEFT_KNEE]
            ankle = landmarks[BodyLandmark.LEFT_ANKLE]

            angle = joint_calculator.knee_angle(hip, knee, ankle)

            frame = angle_renderer.draw_angle_with_arc(
                frame,
                vertex=knee,
                point1=hip,
                point2=ankle,
                angle=angle,
                show_label=show_labels,
                label_prefix="Knee: "
            )

        return frame
