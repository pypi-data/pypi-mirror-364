"""
Command-line interface for polygon measurement tool.
"""

import argparse
import os
from typing import Optional, Tuple

from .core.measurement import EnhancedPolygonMeasurementTool
from .ui.directory_selector import DirectorySelector
from .utils.file_utils import validate_directories


def get_directories_from_gui() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Get directories using GUI selection dialog."""
    print("=== Polygon Measurement Tool ===")
    print("Opening directory selection dialog...")

    try:
        selector = DirectorySelector()
        return selector.show_setup_dialog()
    except Exception as e:
        print(f"Error with GUI: {e}")
        return None, None, None


def get_directories_from_args(
    args,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Get directories from command line arguments."""
    return args.images, args.labels, args.output


def validate_and_get_directories(
    args,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Validate and get directories from GUI or command line."""
    # Use GUI for directory selection if not provided via command line or if --gui flag is used
    if not args.images or not args.labels or args.gui:
        images_dir, labels_dir, output_dir = get_directories_from_gui()

        if not images_dir or not labels_dir:
            print("Setup cancelled or directories not selected.")
            return None, None, None

        if not output_dir:
            output_dir = args.output

    else:
        images_dir, labels_dir, output_dir = get_directories_from_args(args)

        # Validate directories
        is_valid, error_msg = validate_directories(images_dir, labels_dir)
        if not is_valid:
            print(f"Error: {error_msg}")
            return None, None, None

    return images_dir, labels_dir, output_dir


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Polygon Measurement Tool for YOLO segmentation dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use GUI to select directories
  polygon-measure --gui
  
  # Use command line arguments
  polygon-measure -i ./images -l ./labels -o ./measurements
  
  # Use specific directories
  polygon-measure --images /path/to/images --labels /path/to/labels

Features:
  - Enhanced UI with crosshair cursor overlay
  - Three-measurement reference scale averaging
  - Real-time measurement preview with visual feedback
  - Grid overlay (toggle with 'g')
  - Statistical analysis of measurement consistency
  - Cross-platform compatibility
  - Directory selection dialog
        """,
    )

    parser.add_argument(
        "--images",
        "-i",
        help="Path to directory containing images (optional - will show dialog if not provided)",
    )

    parser.add_argument(
        "--labels",
        "-l",
        help="Path to directory containing YOLO label files (optional - will show dialog if not provided)",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="measurements",
        help="Output directory name (default: measurements)",
    )

    parser.add_argument(
        "--gui", action="store_true", help="Force GUI directory selection dialog"
    )

    return parser


def main():
    """Main entry point for the CLI interface."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Get and validate directories
    images_dir, labels_dir, output_dir = validate_and_get_directories(args)

    if not images_dir or not labels_dir:
        return

    # Create and run the measurement tool
    try:
        tool = EnhancedPolygonMeasurementTool(images_dir, labels_dir, output_dir)
        tool.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
