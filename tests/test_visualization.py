"""Tests for visualization module."""

import pytest
import numpy as np
import cv2

from src.visualization import (
    VisualizationEngine,
    ClubRenderer,
    BodyRenderer,
    AngleRenderer,
    StyleConfig,
    Annotation,
)
from src.visualization.utils import (
    draw_text_with_background,
    draw_angle_arc,
    blend_overlay,
    draw_confidence_bar,
    get_text_size,
)
from src.detection import DetectionResult, ClubHead
from src.analysis import JointAngleCalculator, BodyLandmark


class TestStyleConfig:
    """Tests for StyleConfig."""

    def test_default_initialization(self):
        """Test default style config."""
        style = StyleConfig()
        assert style.shaft_color == (0, 255, 0)
        assert style.shaft_thickness == 3
        assert style.antialiasing is True

    def test_custom_initialization(self):
        """Test custom style config."""
        style = StyleConfig(
            shaft_color=(255, 0, 0),
            shaft_thickness=5
        )
        assert style.shaft_color == (255, 0, 0)
        assert style.shaft_thickness == 5

    def test_high_contrast_preset(self):
        """Test high-contrast color scheme."""
        style = StyleConfig.high_contrast()
        assert style.shaft_thickness == 4
        assert style.font_scale == 0.7

    def test_colorblind_friendly_preset(self):
        """Test colorblind-friendly color scheme."""
        style = StyleConfig.colorblind_friendly()
        assert style.shaft_color != StyleConfig().shaft_color

    def test_minimal_preset(self):
        """Test minimal color scheme."""
        style = StyleConfig.minimal()
        assert style.shaft_thickness < StyleConfig().shaft_thickness


class TestAnnotation:
    """Tests for Annotation dataclass."""

    def test_basic_annotation(self):
        """Test creating basic annotation."""
        ann = Annotation(text="Test", position=(100, 100))
        assert ann.text == "Test"
        assert ann.position == (100, 100)
        assert ann.background is True
        assert ann.alignment == 'left'

    def test_custom_annotation(self):
        """Test annotation with custom settings."""
        ann = Annotation(
            text="Custom",
            position=(50, 50),
            font_scale=1.0,
            color=(255, 0, 0),
            background=False,
            alignment='center'
        )
        assert ann.font_scale == 1.0
        assert ann.color == (255, 0, 0)
        assert ann.background is False
        assert ann.alignment == 'center'

    def test_invalid_alignment_raises_error(self):
        """Test that invalid alignment raises error."""
        with pytest.raises(ValueError, match="alignment must be"):
            Annotation(text="Test", position=(0, 0), alignment='invalid')


class TestDrawingUtils:
    """Tests for drawing utility functions."""

    def test_draw_text_with_background(self):
        """Test text with background rendering."""
        frame = np.zeros((200, 200, 3), dtype=np.uint8)

        result = draw_text_with_background(
            frame,
            "Test",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            (0, 0, 0),
            bg_alpha=0.7
        )

        # Should have drawn something
        assert not np.array_equal(result, frame)

    def test_draw_text_invalid_alpha_raises_error(self):
        """Test that invalid alpha raises error."""
        frame = np.zeros((200, 200, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="bg_alpha must be"):
            draw_text_with_background(
                frame, "Test", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), (0, 0, 0),
                bg_alpha=1.5
            )

    def test_draw_angle_arc(self):
        """Test angle arc drawing."""
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        frame_copy = frame.copy()

        result = draw_angle_arc(
            frame,
            (100, 100),
            30,
            0,
            90,
            (255, 0, 0),
            2
        )

        # Should have drawn something (compare to original copy)
        assert not np.array_equal(result, frame_copy)

    def test_blend_overlay(self):
        """Test overlay blending."""
        frame = np.full((100, 100, 3), 100, dtype=np.uint8)
        overlay = np.full((100, 100, 3), 200, dtype=np.uint8)

        result = blend_overlay(frame, overlay, 0.5)

        # Result should be between frame and overlay
        assert np.all(result > frame)
        assert np.all(result < overlay)

    def test_blend_overlay_invalid_shapes_raises_error(self):
        """Test that mismatched shapes raise error."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        overlay = np.zeros((50, 50, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="same shape"):
            blend_overlay(frame, overlay, 0.5)

    def test_blend_overlay_invalid_alpha_raises_error(self):
        """Test that invalid alpha raises error."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="alpha must be"):
            blend_overlay(frame, frame, 1.5)

    def test_draw_confidence_bar(self):
        """Test confidence bar drawing."""
        frame = np.zeros((100, 200, 3), dtype=np.uint8)
        frame_copy = frame.copy()

        result = draw_confidence_bar(
            frame,
            (10, 10),
            0.75,
            width=100,
            height=10
        )

        # Should have drawn something (compare to original copy)
        assert not np.array_equal(result, frame_copy)

    def test_draw_confidence_bar_invalid_confidence_raises_error(self):
        """Test that invalid confidence raises error."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="confidence must be"):
            draw_confidence_bar(frame, (10, 10), 1.5)

    def test_get_text_size(self):
        """Test get_text_size utility."""
        width, height = get_text_size(
            "Test",
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            2
        )

        assert width > 0
        assert height > 0


class TestClubRenderer:
    """Tests for ClubRenderer."""

    def test_initialization(self):
        """Test club renderer initialization."""
        style = StyleConfig()
        renderer = ClubRenderer(style)
        assert renderer.style == style

    def test_draw_shaft(self):
        """Test drawing shaft."""
        style = StyleConfig()
        renderer = ClubRenderer(style)

        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        shaft_line = (50, 50, 200, 250)

        result = renderer.draw_shaft(frame, shaft_line, shaft_angle=45.0)

        # Should have drawn something
        assert not np.array_equal(result, frame)

    def test_draw_club_head(self):
        """Test drawing club head."""
        style = StyleConfig()
        renderer = ClubRenderer(style)

        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        frame_copy = frame.copy()

        result = renderer.draw_club_head(frame, (150, 150), 25.0)

        # Should have drawn something (compare to original copy)
        assert not np.array_equal(result, frame_copy)

    def test_render_full_detection(self):
        """Test rendering complete detection result."""
        style = StyleConfig()
        renderer = ClubRenderer(style)

        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        detection = DetectionResult(
            shaft_detected=True,
            shaft_line=(50, 50, 200, 250),
            shaft_angle=45.0,
            club_head_detected=True,
            club_head_center=(210, 260),
            club_head_radius=20.0,
            confidence=0.85
        )

        result = renderer.render(frame, detection)

        # Should have drawn something
        assert not np.array_equal(result, frame)

    def test_render_low_confidence_skips(self):
        """Test that low confidence detections are skipped."""
        style = StyleConfig(confidence_threshold=0.5)
        renderer = ClubRenderer(style)

        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        detection = DetectionResult(
            shaft_detected=True,
            shaft_line=(50, 50, 200, 250),
            shaft_angle=45.0,
            club_head_detected=False,
            club_head_center=None,
            club_head_radius=None,
            confidence=0.2  # Below threshold
        )

        result = renderer.render(frame, detection)

        # Should not have drawn (below threshold)
        assert np.array_equal(result, frame)


class TestAngleRenderer:
    """Tests for AngleRenderer."""

    def test_initialization(self):
        """Test angle renderer initialization."""
        style = StyleConfig()
        renderer = AngleRenderer(style)
        assert renderer.style == style

    def test_draw_angle_with_arc(self):
        """Test drawing angle arc."""
        style = StyleConfig()
        renderer = AngleRenderer(style)

        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        result = renderer.draw_angle_with_arc(
            frame,
            vertex=(150, 150),
            point1=(100, 150),
            point2=(150, 100),
            angle=90.0
        )

        # Should have drawn something
        assert not np.array_equal(result, frame)


class TestBodyRenderer:
    """Tests for BodyRenderer."""

    def test_initialization(self):
        """Test body renderer initialization."""
        style = StyleConfig()
        renderer = BodyRenderer(style, handedness="right")
        assert renderer.style == style
        assert renderer.handedness == "right"

    def test_draw_skeleton(self):
        """Test drawing skeleton."""
        style = StyleConfig()
        renderer = BodyRenderer(style)

        frame = np.zeros((400, 300, 3), dtype=np.uint8)
        frame_copy = frame.copy()

        # Create minimal landmark set
        landmarks = {
            BodyLandmark.LEFT_SHOULDER: (100, 100),
            BodyLandmark.RIGHT_SHOULDER: (200, 100),
            BodyLandmark.LEFT_ELBOW: (90, 150),
            BodyLandmark.LEFT_WRIST: (85, 200),
        }

        result = renderer.draw_skeleton(frame, landmarks)

        # Should have drawn something (compare to original copy)
        assert not np.array_equal(result, frame_copy)

    def test_draw_joint_angles(self):
        """Test drawing joint angles."""
        style = StyleConfig()
        renderer = BodyRenderer(style)
        angle_renderer = AngleRenderer(style)
        joint_calc = JointAngleCalculator()

        frame = np.zeros((400, 300, 3), dtype=np.uint8)

        # Create landmarks for elbow angle
        landmarks = {
            BodyLandmark.LEFT_SHOULDER: (100, 100),
            BodyLandmark.LEFT_ELBOW: (120, 150),
            BodyLandmark.LEFT_WRIST: (130, 200),
        }

        result = renderer.draw_joint_angles(
            frame,
            landmarks,
            joint_calc,
            angle_renderer
        )

        # Should have drawn something
        assert not np.array_equal(result, frame)


class TestVisualizationEngine:
    """Tests for VisualizationEngine."""

    def test_initialization_default(self):
        """Test default initialization."""
        engine = VisualizationEngine()
        assert engine.style is not None
        assert engine.handedness == "right"

    def test_initialization_custom_style(self):
        """Test initialization with custom style."""
        style = StyleConfig.high_contrast()
        engine = VisualizationEngine(style=style)
        assert engine.style == style

    def test_render_empty_frame_raises_error(self):
        """Test that empty frame raises error."""
        engine = VisualizationEngine()

        with pytest.raises(ValueError, match="empty or None"):
            engine.render(np.array([]))

    def test_render_with_club_detection(self):
        """Test rendering with club detection."""
        engine = VisualizationEngine()

        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        detection = DetectionResult(
            shaft_detected=True,
            shaft_line=(50, 50, 200, 250),
            shaft_angle=45.0,
            club_head_detected=True,
            club_head_center=(210, 260),
            club_head_radius=20.0,
            confidence=0.85
        )

        result = engine.render(frame, club_detection=detection)

        # Should have drawn something
        assert not np.array_equal(result, frame)
        # Original should be unchanged
        assert np.array_equal(frame, np.zeros((300, 300, 3), dtype=np.uint8))

    def test_render_with_body_landmarks(self):
        """Test rendering with body landmarks."""
        engine = VisualizationEngine()

        frame = np.zeros((400, 300, 3), dtype=np.uint8)

        landmarks = {
            BodyLandmark.LEFT_SHOULDER: (100, 100),
            BodyLandmark.RIGHT_SHOULDER: (200, 100),
            BodyLandmark.LEFT_ELBOW: (90, 150),
        }

        result = engine.render(frame, body_landmarks=landmarks)

        # Should have drawn something
        assert not np.array_equal(result, frame)

    def test_render_with_annotations(self):
        """Test rendering with text annotations."""
        engine = VisualizationEngine()

        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        annotations = [
            Annotation(text="Test 1", position=(50, 50)),
            Annotation(text="Test 2", position=(50, 100)),
        ]

        result = engine.render(frame, annotations=annotations)

        # Should have drawn something
        assert not np.array_equal(result, frame)

    def test_render_frame_info(self):
        """Test rendering frame info."""
        engine = VisualizationEngine()

        frame = np.zeros((300, 300, 3), dtype=np.uint8)

        result = engine.render_frame_info(frame, frame_number=100, fps=30.0)

        # Should have drawn something
        assert not np.array_equal(result, frame)

    def test_set_style(self):
        """Test updating style."""
        engine = VisualizationEngine()
        old_style = engine.style

        new_style = StyleConfig.high_contrast()
        engine.set_style(new_style)

        assert engine.style == new_style
        assert engine.style != old_style
