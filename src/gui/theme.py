"""F1 design studio theme and style sheets.

Provides color palette, typography, and Qt style sheets for the
premium F1 aesthetic with glass morphism and metallic accents.
"""

import logging

logger = logging.getLogger(__name__)


class F1Theme:
    """F1 design studio color theme and styling constants.

    Inspired by McLaren mission control - sleek, modern, high-tech
    with glass morphism effects and black/white/silver palette.
    """

    # Color Palette - Blacks
    BLACK_PRIMARY = "#0A0A0A"
    BLACK_SECONDARY = "#121212"
    BLACK_PANEL = "#1A1A1A"
    BLACK_ELEVATED = "#2A2A2A"

    # Color Palette - Whites
    WHITE_PRIMARY = "#FFFFFF"
    WHITE_SECONDARY = "#F5F5F5"
    WHITE_TEXT = "#E8E8E8"
    WHITE_MUTED = "#CCCCCC"

    # Color Palette - Silvers/Metallics
    SILVER_LIGHT = "#E8E8E8"
    SILVER_MID = "#C0C0C0"
    SILVER_DARK = "#BEBEBE"
    CHROME = "#B8B8B8"

    # Accent Colors (optional tech highlights)
    ACCENT_CYAN = "#00D9FF"
    ACCENT_RED = "#FF003D"
    ACCENT_GREEN = "#00FF88"

    # Glass Morphism
    GLASS_BACKGROUND = "rgba(26, 26, 26, 0.7)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.1)"
    GLASS_HIGHLIGHT = "rgba(255, 255, 255, 0.05)"
    GLASS_BLUR = 10  # pixels

    # Shadows
    SHADOW_SOFT = "0 2px 8px rgba(0, 0, 0, 0.3)"
    SHADOW_ELEVATED = "0 4px 16px rgba(0, 0, 0, 0.5)"
    SHADOW_DEEP = "0 8px 32px rgba(0, 0, 0, 0.7)"

    # Spacing
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24
    PADDING_XLARGE = 32

    # Border Radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 6
    RADIUS_LARGE = 8
    RADIUS_XLARGE = 12

    # Typography
    FONT_FAMILY = "Segoe UI, Roboto, sans-serif"
    FONT_SIZE_SMALL = 11
    FONT_SIZE_NORMAL = 13
    FONT_SIZE_LARGE = 15
    FONT_SIZE_XLARGE = 18
    FONT_SIZE_METRIC = 32

    # Animation
    TRANSITION_FAST = 150  # ms
    TRANSITION_NORMAL = 250  # ms
    TRANSITION_SLOW = 400  # ms

    @staticmethod
    def get_main_stylesheet() -> str:
        """Get main application stylesheet with F1 aesthetic.

        Returns:
            Complete Qt stylesheet string for main application
        """
        return f"""
            /* Main Window */
            QMainWindow {{
                background-color: {F1Theme.BLACK_PRIMARY};
                color: {F1Theme.WHITE_TEXT};
            }}

            /* General Widget Defaults */
            QWidget {{
                font-family: {F1Theme.FONT_FAMILY};
                font-size: {F1Theme.FONT_SIZE_NORMAL}px;
                color: {F1Theme.WHITE_TEXT};
            }}

            /* Menu Bar */
            QMenuBar {{
                background-color: {F1Theme.BLACK_SECONDARY};
                color: {F1Theme.WHITE_TEXT};
                border-bottom: 1px solid {F1Theme.BLACK_ELEVATED};
                padding: 4px;
            }}

            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 16px;
                margin: 0px 2px;
                border-radius: {F1Theme.RADIUS_SMALL}px;
            }}

            QMenuBar::item:selected {{
                background-color: {F1Theme.BLACK_ELEVATED};
            }}

            QMenuBar::item:pressed {{
                background-color: {F1Theme.BLACK_PANEL};
            }}

            /* Menu Dropdowns */
            QMenu {{
                background-color: {F1Theme.BLACK_PANEL};
                color: {F1Theme.WHITE_TEXT};
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: {F1Theme.RADIUS_SMALL}px;
                padding: 4px;
            }}

            QMenu::item {{
                padding: 8px 32px 8px 16px;
                border-radius: {F1Theme.RADIUS_SMALL}px;
            }}

            QMenu::item:selected {{
                background-color: {F1Theme.BLACK_ELEVATED};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {F1Theme.BLACK_ELEVATED};
                margin: 4px 8px;
            }}

            /* Tool Bar */
            QToolBar {{
                background-color: {F1Theme.BLACK_SECONDARY};
                border: none;
                spacing: 8px;
                padding: 8px;
            }}

            QToolBar::separator {{
                width: 1px;
                background-color: {F1Theme.BLACK_ELEVATED};
                margin: 4px 8px;
            }}

            /* Status Bar */
            QStatusBar {{
                background-color: {F1Theme.BLACK_SECONDARY};
                color: {F1Theme.WHITE_MUTED};
                border-top: 1px solid {F1Theme.BLACK_ELEVATED};
                padding: 4px 8px;
            }}

            /* Buttons */
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {F1Theme.BLACK_ELEVATED},
                                            stop:1 {F1Theme.BLACK_PANEL});
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: {F1Theme.RADIUS_SMALL}px;
                color: {F1Theme.WHITE_TEXT};
                padding: 8px 16px;
                font-weight: 500;
                min-width: 80px;
            }}

            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3A3A3A,
                                            stop:1 {F1Theme.BLACK_ELEVATED});
                border: 1px solid {F1Theme.SILVER_DARK};
            }}

            QPushButton:pressed {{
                background: {F1Theme.BLACK_PANEL};
                border: 1px solid {F1Theme.SILVER_MID};
            }}

            QPushButton:disabled {{
                background: {F1Theme.BLACK_PANEL};
                color: #555555;
                border: 1px solid #2A2A2A;
            }}

            /* Tool Buttons */
            QToolButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: {F1Theme.RADIUS_SMALL}px;
                padding: 6px;
                color: {F1Theme.WHITE_TEXT};
            }}

            QToolButton:hover {{
                background-color: {F1Theme.BLACK_ELEVATED};
                border: 1px solid {F1Theme.BLACK_ELEVATED};
            }}

            QToolButton:pressed {{
                background-color: {F1Theme.BLACK_PANEL};
            }}

            /* Labels */
            QLabel {{
                color: {F1Theme.WHITE_TEXT};
                background-color: transparent;
            }}

            /* Sliders */
            QSlider::groove:horizontal {{
                background: {F1Theme.BLACK_ELEVATED};
                height: 4px;
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 {F1Theme.SILVER_LIGHT},
                                            stop:1 {F1Theme.SILVER_MID});
                border: 1px solid {F1Theme.SILVER_DARK};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}

            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 {F1Theme.WHITE_PRIMARY},
                                            stop:1 {F1Theme.SILVER_LIGHT});
            }}

            /* Combo Box */
            QComboBox {{
                background-color: {F1Theme.BLACK_PANEL};
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: {F1Theme.RADIUS_SMALL}px;
                padding: 6px 12px;
                color: {F1Theme.WHITE_TEXT};
                min-width: 80px;
            }}

            QComboBox:hover {{
                border: 1px solid {F1Theme.SILVER_DARK};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {F1Theme.WHITE_TEXT};
                margin-right: 8px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {F1Theme.BLACK_PANEL};
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                selection-background-color: {F1Theme.BLACK_ELEVATED};
                color: {F1Theme.WHITE_TEXT};
            }}

            /* Spin Box */
            QSpinBox, QDoubleSpinBox {{
                background-color: {F1Theme.BLACK_PANEL};
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: {F1Theme.RADIUS_SMALL}px;
                padding: 6px;
                color: {F1Theme.WHITE_TEXT};
            }}

            QSpinBox:hover, QDoubleSpinBox:hover {{
                border: 1px solid {F1Theme.SILVER_DARK};
            }}

            /* Check Box */
            QCheckBox {{
                spacing: 8px;
                color: {F1Theme.WHITE_TEXT};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: 3px;
                background-color: {F1Theme.BLACK_PANEL};
            }}

            QCheckBox::indicator:hover {{
                border: 1px solid {F1Theme.SILVER_DARK};
            }}

            QCheckBox::indicator:checked {{
                background-color: {F1Theme.SILVER_MID};
                border: 1px solid {F1Theme.SILVER_LIGHT};
            }}

            /* Scroll Bar */
            QScrollBar:vertical {{
                background: {F1Theme.BLACK_PANEL};
                width: 12px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {F1Theme.BLACK_ELEVATED};
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {F1Theme.SILVER_DARK};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            /* Splitter */
            QSplitter::handle {{
                background-color: {F1Theme.BLACK_ELEVATED};
                width: 1px;
            }}

            QSplitter::handle:hover {{
                background-color: {F1Theme.SILVER_DARK};
            }}

            /* Group Box */
            QGroupBox {{
                border: 1px solid {F1Theme.BLACK_ELEVATED};
                border-radius: {F1Theme.RADIUS_MEDIUM}px;
                margin-top: 12px;
                padding-top: 12px;
                color: {F1Theme.WHITE_TEXT};
                font-weight: 500;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                background-color: {F1Theme.BLACK_PRIMARY};
            }}
        """

    @staticmethod
    def get_glass_panel_stylesheet() -> str:
        """Get glass morphism panel stylesheet.

        Returns:
            Qt stylesheet for glass panel effect
        """
        return f"""
            background: {F1Theme.GLASS_BACKGROUND};
            border: 1px solid {F1Theme.GLASS_BORDER};
            border-radius: {F1Theme.RADIUS_MEDIUM}px;
        """

    @staticmethod
    def get_metric_display_stylesheet() -> str:
        """Get metric display panel stylesheet.

        Returns:
            Qt stylesheet for large metric displays
        """
        return f"""
            QWidget {{
                background: {F1Theme.GLASS_BACKGROUND};
                border: 1px solid {F1Theme.GLASS_BORDER};
                border-radius: {F1Theme.RADIUS_LARGE}px;
                padding: {F1Theme.PADDING_MEDIUM}px;
            }}

            QLabel {{
                color: {F1Theme.WHITE_TEXT};
                background: transparent;
            }}

            .metric-label {{
                font-size: {F1Theme.FONT_SIZE_SMALL}px;
                color: {F1Theme.WHITE_MUTED};
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .metric-value {{
                font-size: {F1Theme.FONT_SIZE_METRIC}px;
                font-weight: 600;
                color: {F1Theme.WHITE_PRIMARY};
            }}

            .metric-unit {{
                font-size: {F1Theme.FONT_SIZE_LARGE}px;
                color: {F1Theme.SILVER_MID};
            }}
        """

    @staticmethod
    def get_video_display_stylesheet() -> str:
        """Get video display area stylesheet.

        Returns:
            Qt stylesheet for video player display
        """
        return f"""
            background-color: {F1Theme.BLACK_PRIMARY};
            border: 1px solid {F1Theme.BLACK_ELEVATED};
            border-radius: {F1Theme.RADIUS_MEDIUM}px;
        """
