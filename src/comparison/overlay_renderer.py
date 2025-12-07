"""Overlay renderer for blending two video frames together."""

import logging
from typing import Optional, Tuple
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class OverlayRenderer:
    """Renders two video frames blended together with various modes.

    Supports alpha blending, different blend modes, color tinting,
    and automatic frame alignment for overlaying videos.

    Example:
        renderer = OverlayRenderer()
        blended = renderer.render(
            frame1, frame2,
            alpha=0.5,
            blend_mode='normal',
            tint1=(255, 100, 100),
            tint2=(100, 255, 100)
        )
    """

    BLEND_MODES = ['normal', 'difference', 'multiply', 'screen']

    def __init__(self):
        """Initialize overlay renderer."""
        self.alignment_mode = 'center'  # 'center', 'top-left', 'scale-to-fit'
        logger.debug("Initialized OverlayRenderer")

    def render(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        alpha: float = 0.5,
        blend_mode: str = 'normal',
        tint1: Optional[Tuple[int, int, int]] = None,
        tint2: Optional[Tuple[int, int, int]] = None,
        alignment: Optional[str] = None
    ) -> np.ndarray:
        """Blend two frames together.

        Args:
            frame1: First video frame (BGR format)
            frame2: Second video frame (BGR format)
            alpha: Transparency (0.0 = only frame1, 1.0 = only frame2)
            blend_mode: Blending mode ('normal', 'difference', 'multiply', 'screen')
            tint1: RGB color tint for frame1 (e.g., (255, 0, 0) for red)
            tint2: RGB color tint for frame2 (e.g., (0, 255, 0) for green)
            alignment: Frame alignment mode (None uses default)

        Returns:
            Blended frame as numpy array (BGR format)

        Raises:
            ValueError: If blend_mode is not supported
        """
        if blend_mode not in self.BLEND_MODES:
            raise ValueError(f"Unsupported blend mode: {blend_mode}. "
                             f"Supported: {self.BLEND_MODES}")

        # Align frames to same size
        alignment_mode = alignment or self.alignment_mode
        aligned1, aligned2 = self._align_frames(frame1, frame2, alignment_mode)

        # Apply color tints if specified
        if tint1 is not None:
            aligned1 = self._apply_tint(aligned1, tint1)
        if tint2 is not None:
            aligned2 = self._apply_tint(aligned2, tint2)

        # Blend frames based on mode
        if blend_mode == 'normal':
            blended = self._blend_normal(aligned1, aligned2, alpha)
        elif blend_mode == 'difference':
            blended = self._blend_difference(aligned1, aligned2)
        elif blend_mode == 'multiply':
            blended = self._blend_multiply(aligned1, aligned2)
        elif blend_mode == 'screen':
            blended = self._blend_screen(aligned1, aligned2)

        return blended

    def _align_frames(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        mode: str = 'center'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Align two frames to the same size.

        Args:
            frame1: First frame
            frame2: Second frame
            mode: Alignment mode ('center', 'top-left', 'scale-to-fit')

        Returns:
            Tuple of (aligned_frame1, aligned_frame2) with same dimensions
        """
        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]

        if mode == 'scale-to-fit':
            # Scale both to the larger dimensions
            target_h = max(h1, h2)
            target_w = max(w1, w2)

            aligned1 = cv2.resize(frame1, (target_w, target_h))
            aligned2 = cv2.resize(frame2, (target_w, target_h))

        elif mode == 'center':
            # Use larger dimensions, center smaller frame with padding
            target_h = max(h1, h2)
            target_w = max(w1, w2)

            aligned1 = self._pad_to_size(frame1, target_h, target_w, center=True)
            aligned2 = self._pad_to_size(frame2, target_h, target_w, center=True)

        elif mode == 'top-left':
            # Use larger dimensions, align top-left with padding
            target_h = max(h1, h2)
            target_w = max(w1, w2)

            aligned1 = self._pad_to_size(frame1, target_h, target_w, center=False)
            aligned2 = self._pad_to_size(frame2, target_h, target_w, center=False)

        else:
            raise ValueError(f"Unknown alignment mode: {mode}")

        return aligned1, aligned2

    def _pad_to_size(
        self,
        frame: np.ndarray,
        target_h: int,
        target_w: int,
        center: bool = True
    ) -> np.ndarray:
        """Pad frame to target size.

        Args:
            frame: Input frame
            target_h: Target height
            target_w: Target width
            center: If True, center the frame; if False, align top-left

        Returns:
            Padded frame
        """
        h, w = frame.shape[:2]

        if h == target_h and w == target_w:
            return frame.copy()

        # Calculate padding
        if center:
            pad_top = (target_h - h) // 2
            pad_bottom = target_h - h - pad_top
            pad_left = (target_w - w) // 2
            pad_right = target_w - w - pad_left
        else:
            pad_top = 0
            pad_bottom = target_h - h
            pad_left = 0
            pad_right = target_w - w

        # Pad with black
        padded = cv2.copyMakeBorder(
            frame,
            pad_top, pad_bottom, pad_left, pad_right,
            cv2.BORDER_CONSTANT,
            value=(0, 0, 0)
        )

        return padded

    def _apply_tint(
        self,
        frame: np.ndarray,
        tint_color: Tuple[int, int, int],
        intensity: float = 0.3
    ) -> np.ndarray:
        """Apply color tint to frame.

        Args:
            frame: Input frame (BGR)
            tint_color: RGB color tuple (e.g., (255, 0, 0) for red)
            intensity: Tint strength (0.0-1.0)

        Returns:
            Tinted frame
        """
        # Convert RGB to BGR
        tint_bgr = (tint_color[2], tint_color[1], tint_color[0])

        # Create tint layer
        tint_layer = np.full_like(frame, tint_bgr, dtype=np.uint8)

        # Blend original with tint
        tinted = cv2.addWeighted(
            frame, 1.0 - intensity,
            tint_layer, intensity,
            0
        )

        return tinted

    def _blend_normal(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        alpha: float
    ) -> np.ndarray:
        """Normal alpha blending.

        Args:
            frame1: First frame
            frame2: Second frame
            alpha: Blend factor (0.0 = frame1, 1.0 = frame2)

        Returns:
            Blended frame
        """
        # Clamp alpha to valid range
        alpha = np.clip(alpha, 0.0, 1.0)

        # Standard alpha blending: result = frame1 * (1-alpha) + frame2 * alpha
        blended = cv2.addWeighted(
            frame1, 1.0 - alpha,
            frame2, alpha,
            0
        )

        return blended

    def _blend_difference(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray
    ) -> np.ndarray:
        """Difference blend mode (highlights differences).

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Difference frame (bright areas show differences)
        """
        # Absolute difference
        diff = cv2.absdiff(frame1, frame2)

        # Optionally amplify differences for better visibility
        # Scale by factor of 2 and clip
        diff = np.clip(diff.astype(np.float32) * 2.0, 0, 255).astype(np.uint8)

        return diff

    def _blend_multiply(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray
    ) -> np.ndarray:
        """Multiply blend mode (darker blend).

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Multiplied frame
        """
        # Multiply: result = (frame1 * frame2) / 255
        # Convert to float for calculation
        f1 = frame1.astype(np.float32)
        f2 = frame2.astype(np.float32)

        multiplied = (f1 * f2) / 255.0

        return multiplied.astype(np.uint8)

    def _blend_screen(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray
    ) -> np.ndarray:
        """Screen blend mode (lighter blend).

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Screened frame
        """
        # Screen: result = 255 - ((255 - frame1) * (255 - frame2)) / 255
        # Inverted multiply
        f1 = frame1.astype(np.float32)
        f2 = frame2.astype(np.float32)

        screened = 255.0 - ((255.0 - f1) * (255.0 - f2)) / 255.0

        return screened.astype(np.uint8)

    def set_alignment_mode(self, mode: str):
        """Set default alignment mode.

        Args:
            mode: Alignment mode ('center', 'top-left', 'scale-to-fit')

        Raises:
            ValueError: If mode is not valid
        """
        valid_modes = ['center', 'top-left', 'scale-to-fit']
        if mode not in valid_modes:
            raise ValueError(f"Invalid alignment mode: {mode}. "
                             f"Valid: {valid_modes}")

        self.alignment_mode = mode
        logger.debug(f"Alignment mode set to: {mode}")
