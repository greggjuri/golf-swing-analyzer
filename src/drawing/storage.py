"""Save and load drawing data to/from files."""

import json
import logging
import time
from typing import List, Optional, Tuple
from pathlib import Path

from .shapes import (
    DrawingShape, Line, Angle, Circle, Arc, TextAnnotation
)

logger = logging.getLogger(__name__)


class DrawingStorage:
    """Save and load drawing data.

    Drawings are saved as JSON files with the .drawings.json extension.

    Example:
        # Save
        DrawingStorage.save_drawings(
            shapes,
            "video.drawings.json",
            video_path="video.mp4"
        )

        # Load
        shapes, video_path = DrawingStorage.load_drawings("video.drawings.json")
    """

    VERSION = "1.0"

    @staticmethod
    def save_drawings(
        shapes: List[DrawingShape],
        filepath: str,
        video_path: Optional[str] = None
    ):
        """Save drawings to JSON file.

        Args:
            shapes: List of shapes to save
            filepath: Output JSON file path
            video_path: Optional associated video path

        Raises:
            IOError: If file cannot be written
        """
        # Build data structure
        data = {
            'version': DrawingStorage.VERSION,
            'video_path': video_path,
            'created_at': time.time(),
            'shape_count': len(shapes),
            'shapes': []
        }

        # Serialize all shapes
        for shape in shapes:
            shape_dict = shape.to_dict()
            data['shapes'].append(shape_dict)

        # Write to file
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(shapes)} shapes to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save drawings: {e}")
            raise IOError(f"Failed to save drawings: {e}")

    @staticmethod
    def load_drawings(filepath: str) -> Tuple[List[DrawingShape], Optional[str]]:
        """Load drawings from JSON file.

        Args:
            filepath: Input JSON file path

        Returns:
            Tuple of (shapes list, video_path)

        Raises:
            IOError: If file cannot be read
            ValueError: If file format is invalid
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

        except Exception as e:
            logger.error(f"Failed to load drawings: {e}")
            raise IOError(f"Failed to load drawings: {e}")

        # Validate version
        version = data.get('version', '0.0')
        if version != DrawingStorage.VERSION:
            logger.warning(f"Loading drawings from version {version} (current: {DrawingStorage.VERSION})")

        # Deserialize shapes
        shapes = []
        for shape_data in data.get('shapes', []):
            try:
                shape = DrawingStorage._deserialize_shape(shape_data)
                if shape:
                    shapes.append(shape)
            except Exception as e:
                logger.warning(f"Failed to deserialize shape: {e}")
                continue

        video_path = data.get('video_path')

        logger.info(f"Loaded {len(shapes)} shapes from {filepath}")

        return shapes, video_path

    @staticmethod
    def _deserialize_shape(data: dict) -> Optional[DrawingShape]:
        """Deserialize a shape from dictionary.

        Args:
            data: Shape data dictionary

        Returns:
            DrawingShape instance or None if type unknown
        """
        shape_type = data.get('type')

        if shape_type == 'line':
            return Line.from_dict(data)
        elif shape_type == 'angle':
            return Angle.from_dict(data)
        elif shape_type == 'circle':
            return Circle.from_dict(data)
        elif shape_type == 'arc':
            return Arc.from_dict(data)
        elif shape_type == 'text':
            return TextAnnotation.from_dict(data)
        else:
            logger.warning(f"Unknown shape type: {shape_type}")
            return None

    @staticmethod
    def get_default_filename(video_path: str) -> str:
        """Get default drawings filename for a video.

        Args:
            video_path: Path to video file

        Returns:
            Default drawings filename (e.g., "video.drawings.json")
        """
        video_name = Path(video_path).stem
        return f"{video_name}.drawings.json"

    @staticmethod
    def auto_load_drawings(video_path: str) -> Optional[List[DrawingShape]]:
        """Attempt to auto-load drawings for a video.

        Looks for a .drawings.json file with the same name as the video.

        Args:
            video_path: Path to video file

        Returns:
            List of shapes if found, None otherwise
        """
        drawings_path = DrawingStorage.get_default_filename(video_path)

        if not Path(drawings_path).exists():
            # Try in same directory as video
            video_dir = Path(video_path).parent
            drawings_path = video_dir / f"{Path(video_path).stem}.drawings.json"

        if Path(drawings_path).exists():
            try:
                shapes, _ = DrawingStorage.load_drawings(str(drawings_path))
                logger.info(f"Auto-loaded {len(shapes)} drawings for {video_path}")
                return shapes
            except Exception as e:
                logger.warning(f"Failed to auto-load drawings: {e}")

        return None

    @staticmethod
    def export_shapes_by_frame(
        shapes: List[DrawingShape]
    ) -> dict:
        """Export shapes grouped by frame number.

        Args:
            shapes: List of shapes

        Returns:
            Dictionary mapping frame_number -> list of shape dicts
        """
        shapes_by_frame = {}

        for shape in shapes:
            frame_num = shape.frame_number

            if frame_num not in shapes_by_frame:
                shapes_by_frame[frame_num] = []

            shapes_by_frame[frame_num].append(shape.to_dict())

        return shapes_by_frame

    @staticmethod
    def import_shapes_by_frame(
        shapes_by_frame: dict
    ) -> List[DrawingShape]:
        """Import shapes from frame-grouped dictionary.

        Args:
            shapes_by_frame: Dictionary mapping frame_number -> list of shape dicts

        Returns:
            List of DrawingShape objects
        """
        shapes = []

        for frame_num, shape_dicts in shapes_by_frame.items():
            for shape_data in shape_dicts:
                shape = DrawingStorage._deserialize_shape(shape_data)
                if shape:
                    shapes.append(shape)

        return shapes
