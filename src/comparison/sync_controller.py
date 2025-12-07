"""Synchronization controller for dual video playback."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SyncController:
    """Controls synchronization between two videos.

    Handles linked/unlinked playback, frame offset management,
    synchronized seeking, and playback speed matching.

    Example:
        sync = SyncController()
        sync.set_sync_enabled(True)
        sync.set_frame_offset(5)  # Right video is 5 frames ahead

        # Get corresponding frame
        right_frame = sync.get_synced_frame(left_frame=10)  # Returns 15
    """

    def __init__(self):
        """Initialize sync controller."""
        self.sync_enabled = True
        self.frame_offset = 0  # Offset between videos (can be negative)
        self.playback_speed = 1.0

        logger.debug("Initialized SyncController")

    def set_sync_enabled(self, enabled: bool):
        """Enable/disable synchronization.

        Args:
            enabled: True to enable sync, False to allow independent playback
        """
        self.sync_enabled = enabled
        logger.debug(f"Sync {'enabled' if enabled else 'disabled'}")

    def is_sync_enabled(self) -> bool:
        """Check if synchronization is enabled.

        Returns:
            True if sync is enabled
        """
        return self.sync_enabled

    def set_frame_offset(self, offset: int):
        """Set frame offset between videos.

        Positive offset means right video is ahead.
        Negative offset means left video is ahead.

        Args:
            offset: Number of frames to offset
        """
        self.frame_offset = offset
        logger.debug(f"Frame offset set to {offset}")

    def get_frame_offset(self) -> int:
        """Get current frame offset.

        Returns:
            Frame offset
        """
        return self.frame_offset

    def get_synced_frame(
        self,
        primary_frame: int,
        max_frame: Optional[int] = None
    ) -> int:
        """Get corresponding frame for secondary video.

        Args:
            primary_frame: Frame number on primary video
            max_frame: Maximum frame number (for bounds checking)

        Returns:
            Corresponding frame on secondary video
        """
        if not self.sync_enabled:
            # When unsynced, secondary doesn't follow primary
            return 0

        # Apply offset
        synced_frame = primary_frame + self.frame_offset

        # Clamp to valid range
        synced_frame = max(0, synced_frame)
        if max_frame is not None:
            synced_frame = min(synced_frame, max_frame)

        return synced_frame

    def calibrate_sync(self, left_frame: int, right_frame: int):
        """Calibrate sync by marking matching frames.

        This is used when user manually aligns videos to matching positions
        (e.g., both at impact position).

        Args:
            left_frame: Frame number on left video
            right_frame: Frame number on right video
        """
        # Calculate offset: how many frames is right ahead of left?
        self.frame_offset = right_frame - left_frame

        logger.info(f"Sync calibrated: left frame {left_frame} = "
                    f"right frame {right_frame} (offset: {self.frame_offset})")

    def set_playback_speed(self, speed: float):
        """Set playback speed for both videos.

        Args:
            speed: Speed multiplier (0.25, 0.5, 1.0, 2.0, etc.)
        """
        self.playback_speed = speed
        logger.debug(f"Playback speed set to {speed}x")

    def get_playback_speed(self) -> float:
        """Get current playback speed.

        Returns:
            Speed multiplier
        """
        return self.playback_speed

    def reset_offset(self):
        """Reset frame offset to zero."""
        self.frame_offset = 0
        logger.debug("Frame offset reset to 0")

    def get_offset_display(self) -> str:
        """Get human-readable offset description.

        Returns:
            String like "Right +5 frames" or "Aligned"
        """
        if self.frame_offset == 0:
            return "Aligned"
        elif self.frame_offset > 0:
            return f"Right +{self.frame_offset} frames"
        else:
            return f"Left +{abs(self.frame_offset)} frames"
