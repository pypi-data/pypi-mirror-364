"""
Polygon Measurement Tool for YOLO Segmentation Dataset

A Python package for measuring polygons in YOLO format annotation files with enhanced UI features.

Features:
- Enhanced UI with crosshair cursor overlay
- Three-measurement reference scale averaging for accuracy
- Real-time measurement preview with visual feedback
- Grid overlay and statistical analysis
- Cross-platform GUI directory selection
- Batch processing of image-label pairs
"""

__version__ = "2.0.0"
__author__ = "Polygon Measurement Tool"
__description__ = "Polygon measurement tool for YOLO segmentation datasets"

from .core.measurement import EnhancedPolygonMeasurementTool
from .ui.directory_selector import DirectorySelector
from .cli import main

__all__ = [
    "EnhancedPolygonMeasurementTool",
    "DirectorySelector",
    "main",
]
