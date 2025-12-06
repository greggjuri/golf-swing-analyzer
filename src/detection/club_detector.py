"""Club detection using edge detection and Hough transforms.

This module implements the core club detection logic for identifying the
golf club shaft and head in video frames.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List

import cv2
import numpy as np

from ..analysis import angle_from_horizontal, Point2D
from .preprocessing import FramePreprocessor, create_edge_mask, clean_edge_mask

logger = logging.getLogger(__name__)

# Type aliases
Line = Tuple[int, int, int, int]  # (x1, y1, x2, y2)
ROI = Tuple[int, int, int, int]  # (x, y, width, height)


@dataclass
class ClubHead:
    """Club head detection information.

    Attributes:
        center: Center point (x, y) of club head
        radius: Approximate radius in pixels
        confidence: Detection confidence (0.0 to 1.0)
    """
    center: Point2D
    radius: float
    confidence: float


@dataclass
class DetectionResult:
    """Result from club detection in a single frame.

    Attributes:
        shaft_detected: Whether shaft was detected
        shaft_line: Shaft endpoints (x1, y1, x2, y2) or None
        shaft_angle: Angle from horizontal in degrees or None
        club_head_detected: Whether club head was detected
        club_head_center: Club head center point or None
        club_head_radius: Club head radius in pixels or None
        confidence: Overall detection confidence (0.0 to 1.0)
        debug_image: Debug visualization if enabled, or None
    """
    shaft_detected: bool
    shaft_line: Optional[Line]
    shaft_angle: Optional[float]
    club_head_detected: bool
    club_head_center: Optional[Point2D]
    club_head_radius: Optional[float]
    confidence: float
    debug_image: Optional[np.ndarray] = None


class ClubDetector:
    """Detect golf club shaft and head in video frames.

    Uses Canny edge detection and Hough line transform for shaft detection,
    and Hough circle transform or contour detection for club head.

    Example:
        detector = ClubDetector(debug=True)
        result = detector.detect(frame)

        if result.shaft_detected:
            x1, y1, x2, y2 = result.shaft_line
            print(f"Shaft: ({x1},{y1}) to ({x2},{y2})")
            print(f"Angle: {result.shaft_angle:.1f}°")
    """

    def __init__(
        self,
        canny_low: int = 50,
        canny_high: int = 150,
        hough_threshold: int = 50,
        min_line_length: int = 100,
        max_line_gap: int = 10,
        min_shaft_angle: float = 15.0,
        max_shaft_angle: float = 165.0,
        debug: bool = False,
        roi: Optional[ROI] = None
    ):
        """Initialize club detector.

        Args:
            canny_low: Low threshold for Canny edge detection
            canny_high: High threshold for Canny edge detection
            hough_threshold: Threshold for Hough line detection
            min_line_length: Minimum line length in pixels
            max_line_gap: Maximum gap between line segments
            min_shaft_angle: Minimum shaft angle from horizontal (degrees)
            max_shaft_angle: Maximum shaft angle from horizontal (degrees)
            debug: Enable debug visualization
            roi: Optional region of interest (x, y, width, height)

        Raises:
            ValueError: If parameters are invalid
        """
        if canny_low <= 0 or canny_high <= 0 or canny_low >= canny_high:
            raise ValueError(
                f"Invalid Canny thresholds: low={canny_low}, high={canny_high}"
            )

        if hough_threshold <= 0:
            raise ValueError(f"hough_threshold must be positive, got {hough_threshold}")

        if min_line_length <= 0:
            raise ValueError(f"min_line_length must be positive, got {min_line_length}")

        self.canny_low = canny_low
        self.canny_high = canny_high
        self.hough_threshold = hough_threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap
        self.min_shaft_angle = min_shaft_angle
        self.max_shaft_angle = max_shaft_angle
        self.debug = debug
        self.roi = roi

        # Create preprocessor
        self.preprocessor = FramePreprocessor(
            blur_kernel=5,
            roi=roi,
            enhance_contrast=False
        )

        logger.info(
            f"Initialized ClubDetector: canny=({canny_low},{canny_high}), "
            f"hough_thresh={hough_threshold}, min_len={min_line_length}"
        )

    def detect(self, frame: np.ndarray) -> DetectionResult:
        """Detect club shaft and head in frame.

        Args:
            frame: Input frame (BGR format from OpenCV)

        Returns:
            DetectionResult with detection information

        Raises:
            ValueError: If frame is invalid
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")

        # Preprocess frame
        preprocessed = self.preprocessor.preprocess(frame)

        # Detect edges
        edges = create_edge_mask(preprocessed, self.canny_low, self.canny_high)
        edges = clean_edge_mask(edges, kernel_size=3)

        # Detect shaft
        shaft_line = self.detect_shaft(edges)
        shaft_angle = None
        shaft_confidence = 0.0

        if shaft_line is not None:
            # Calculate angle
            x1, y1, x2, y2 = shaft_line
            shaft_angle = angle_from_horizontal((x1, y1), (x2, y2))

            # Calculate confidence based on line length
            line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            shaft_confidence = min(1.0, line_length / 300.0)  # Normalize to 300px

        # Detect club head
        club_head = self.detect_club_head(preprocessed, shaft_line)

        # Overall confidence
        if shaft_line is not None and club_head is not None:
            confidence = (shaft_confidence + club_head.confidence) / 2
        elif shaft_line is not None:
            confidence = shaft_confidence
        elif club_head is not None:
            confidence = club_head.confidence
        else:
            confidence = 0.0

        # Create debug image if requested
        debug_image = None
        if self.debug:
            debug_image = self._create_debug_image(
                frame, edges, shaft_line, club_head
            )

        return DetectionResult(
            shaft_detected=shaft_line is not None,
            shaft_line=shaft_line,
            shaft_angle=shaft_angle,
            club_head_detected=club_head is not None,
            club_head_center=club_head.center if club_head else None,
            club_head_radius=club_head.radius if club_head else None,
            confidence=confidence,
            debug_image=debug_image
        )

    def detect_shaft(self, edges: np.ndarray) -> Optional[Line]:
        """Detect club shaft using Hough line transform.

        Args:
            edges: Edge-detected image (binary mask)

        Returns:
            Shaft line (x1, y1, x2, y2) or None if not detected
        """
        # Use probabilistic Hough line transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap
        )

        if lines is None or len(lines) == 0:
            logger.debug("No lines detected by Hough transform")
            return None

        # Filter and select best line
        valid_lines = self._filter_lines(lines)

        if len(valid_lines) == 0:
            logger.debug("No valid lines after filtering")
            return None

        # Select longest line as shaft
        best_line = self._select_best_line(valid_lines)

        logger.debug(f"Detected shaft: {best_line}")
        return best_line

    def _filter_lines(self, lines: np.ndarray) -> List[Line]:
        """Filter lines by angle and length criteria.

        Args:
            lines: Lines from Hough transform (Nx1x4 array)

        Returns:
            List of valid lines as tuples
        """
        valid_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calculate angle from horizontal
            try:
                angle = abs(angle_from_horizontal((x1, y1), (x2, y2)))
            except ValueError:
                continue

            # Filter by angle (exclude nearly horizontal/vertical)
            if not (self.min_shaft_angle <= angle <= self.max_shaft_angle):
                continue

            # Calculate length
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            if length >= self.min_line_length:
                valid_lines.append((x1, y1, x2, y2))

        return valid_lines

    def _select_best_line(self, lines: List[Line]) -> Line:
        """Select best line from candidates based on length.

        Args:
            lines: List of candidate lines

        Returns:
            Best line (longest)
        """
        # Select longest line
        best_line = max(
            lines,
            key=lambda line: np.sqrt(
                (line[2] - line[0])**2 + (line[3] - line[1])**2
            )
        )
        return best_line

    def detect_club_head(
        self,
        frame: np.ndarray,
        shaft_line: Optional[Line] = None
    ) -> Optional[ClubHead]:
        """Detect club head using Hough circle transform.

        Args:
            frame: Preprocessed grayscale frame
            shaft_line: Optional shaft line to constrain search

        Returns:
            ClubHead information or None if not detected
        """
        # Define search region
        if shaft_line is not None:
            # Search near shaft endpoint (club head end)
            x1, y1, x2, y2 = shaft_line
            # Assume club head is at the end further from top of frame
            if y1 > y2:
                search_center = (x1, y1)
            else:
                search_center = (x2, y2)

            # Create ROI around endpoint
            search_radius = 100
            x_min = max(0, search_center[0] - search_radius)
            y_min = max(0, search_center[1] - search_radius)
            x_max = min(frame.shape[1], search_center[0] + search_radius)
            y_max = min(frame.shape[0], search_center[1] + search_radius)

            search_roi = frame[y_min:y_max, x_min:x_max]
            roi_offset = (x_min, y_min)
        else:
            # Search entire frame
            search_roi = frame
            roi_offset = (0, 0)

        # Try Hough circle detection
        circles = cv2.HoughCircles(
            search_roi,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=50
        )

        if circles is None or len(circles) == 0:
            logger.debug("No club head detected")
            return None

        # Take the first detected circle
        circle = circles[0][0]
        cx, cy, radius = circle

        # Adjust coordinates for ROI offset
        center = (cx + roi_offset[0], cy + roi_offset[1])

        # Simple confidence based on circle strength
        confidence = 0.7  # Default confidence for circle detection

        logger.debug(f"Detected club head at {center}, radius={radius:.1f}")

        return ClubHead(
            center=center,
            radius=float(radius),
            confidence=confidence
        )

    def _create_debug_image(
        self,
        frame: np.ndarray,
        edges: np.ndarray,
        shaft_line: Optional[Line],
        club_head: Optional[ClubHead]
    ) -> np.ndarray:
        """Create debug visualization image.

        Args:
            frame: Original frame
            edges: Edge mask
            shaft_line: Detected shaft line or None
            club_head: Detected club head or None

        Returns:
            Debug visualization image
        """
        # Create color version of frame
        if len(frame.shape) == 2:
            debug = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        else:
            debug = frame.copy()

        # Draw edges in blue
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        debug = cv2.addWeighted(debug, 0.7, edges_color, 0.3, 0)

        # Draw shaft line in green
        if shaft_line is not None:
            x1, y1, x2, y2 = shaft_line
            cv2.line(debug, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Draw club head in red
        if club_head is not None:
            center = (int(club_head.center[0]), int(club_head.center[1]))
            radius = int(club_head.radius)
            cv2.circle(debug, center, radius, (0, 0, 255), 2)
            cv2.circle(debug, center, 3, (0, 0, 255), -1)

        return debug
