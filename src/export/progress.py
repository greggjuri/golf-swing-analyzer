"""Progress tracking for export operations."""

import time
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track and report export progress.

    Tracks progress through a sequence of items and provides percentage
    complete and estimated time remaining.

    Example:
        tracker = ProgressTracker(total_items=100)

        for i in range(100):
            process_item(i)
            tracker.update(i + 1, callback=lambda p: print(f"{p:.0f}%"))
    """

    def __init__(self, total_items: int):
        """Initialize progress tracker.

        Args:
            total_items: Total number of items to process

        Raises:
            ValueError: If total_items is not positive
        """
        if total_items <= 0:
            raise ValueError(f"total_items must be positive, got {total_items}")

        self.total_items = total_items
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

        logger.debug(f"Initialized ProgressTracker for {total_items} items")

    def update(
        self,
        current: int,
        callback: Optional[Callable[[float], None]] = None
    ):
        """Update progress.

        Args:
            current: Current item count (0 to total_items)
            callback: Optional callback function receiving percentage (0-100)

        Raises:
            ValueError: If current is negative or exceeds total
        """
        if current < 0:
            raise ValueError(f"current cannot be negative, got {current}")

        if current > self.total_items:
            raise ValueError(
                f"current ({current}) exceeds total ({self.total_items})"
            )

        self.current = current
        self.last_update_time = time.time()

        if callback is not None:
            percentage = self.get_percentage()
            callback(percentage)

    def get_percentage(self) -> float:
        """Get current progress percentage.

        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if self.total_items == 0:
            return 100.0

        return (self.current / self.total_items) * 100.0

    def get_eta_seconds(self) -> Optional[float]:
        """Get estimated time remaining in seconds.

        Returns:
            Estimated seconds remaining, or None if cannot be estimated
        """
        if self.current == 0:
            return None

        elapsed = time.time() - self.start_time
        rate = self.current / elapsed  # items per second

        if rate == 0:
            return None

        remaining_items = self.total_items - self.current
        eta = remaining_items / rate

        return eta

    def get_eta_string(self) -> str:
        """Get formatted ETA string.

        Returns:
            Formatted ETA (e.g., "2m 30s") or "Unknown"
        """
        eta = self.get_eta_seconds()

        if eta is None:
            return "Unknown"

        # Format as minutes and seconds
        minutes = int(eta // 60)
        seconds = int(eta % 60)

        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def reset(self):
        """Reset progress tracking."""
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

        logger.debug("Progress tracker reset")

    def is_complete(self) -> bool:
        """Check if progress is complete.

        Returns:
            True if current equals total_items
        """
        return self.current >= self.total_items

    def get_elapsed_seconds(self) -> float:
        """Get total elapsed time in seconds.

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.start_time

    def get_rate(self) -> float:
        """Get processing rate in items per second.

        Returns:
            Items processed per second
        """
        elapsed = self.get_elapsed_seconds()

        if elapsed == 0:
            return 0.0

        return self.current / elapsed
