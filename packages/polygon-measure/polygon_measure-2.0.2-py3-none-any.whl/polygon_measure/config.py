"""
Configuration constants and settings for polygon measurement tool.
"""

# Visual feedback settings
CROSSHAIR_SIZE = 25
LINE_COLOR = (0, 255, 0)  # Green
CROSSHAIR_COLOR = (255, 255, 0)  # Yellow
TEXT_COLOR = (0, 255, 0)  # Green
GRID_COLOR = (128, 128, 128)  # Gray

# Font settings - increased for better readability
FONT_SCALE_LARGE = 1.2
FONT_SCALE_MEDIUM = 0.8
FONT_SCALE_SMALL = 0.6
FONT_THICKNESS_LARGE = 3
FONT_THICKNESS_MEDIUM = 2
FONT_THICKNESS_SMALL = 1

# Performance settings
UPDATE_INTERVAL = 1 / 60  # 60 FPS target

# Reference measurement settings
MAX_MEASUREMENTS = 3
MIN_MEASUREMENTS = 3

# File extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

# UI window settings
WINDOW_NAME = "Reference Scale Setting Tool"
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900

# Measurement validation
MAX_COEFFICIENT_VARIATION = 10  # Maximum acceptable variation percentage

# Grid settings
GRID_SPACING = 50

# UI colors for different elements
INSTRUCTION_PANEL_COLOR = (0, 0, 0)  # Black background
INSTRUCTION_BORDER_COLOR = (0, 255, 255)  # Cyan border
MEASUREMENT_PANEL_COLOR = (0, 0, 0)  # Black background
MEASUREMENT_BORDER_COLOR = (255, 255, 0)  # Yellow border

# Text positioning
PANEL_PADDING = 10
TEXT_PADDING = 25
LINE_SPACING_BASE = 25
