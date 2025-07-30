"""
File utilities for polygon measurement tool.
"""

import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import pandas as pd
from ..config import IMAGE_EXTENSIONS


def load_yolo_polygons(label_path: Path) -> List[Dict[str, Any]]:
    """
    Load polygon coordinates from YOLO format label file.

    Args:
        label_path: Path to the YOLO label file

    Returns:
        List of dictionaries containing class_id and points
    """
    polygons = []

    if not label_path.exists():
        return polygons

    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:  # At least class + 3 points (6 coordinates)
                continue

            class_id = int(parts[0])
            coords = [float(x) for x in parts[1:]]

            # Convert to list of (x, y) tuples
            polygon_points = []
            for i in range(0, len(coords), 2):
                if i + 1 < len(coords):
                    polygon_points.append((coords[i], coords[i + 1]))

            polygons.append({"class_id": class_id, "points": polygon_points})

    return polygons


def get_matching_files(images_dir: Path, labels_dir: Path) -> List[Tuple[Path, Path]]:
    """
    Get matching image and label file pairs.

    Args:
        images_dir: Directory containing images
        labels_dir: Directory containing labels

    Returns:
        List of tuples (image_path, label_path) for matching pairs
    """
    image_files = []

    # Find all image files
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(list(images_dir.glob(f"*{ext}")))
        image_files.extend(list(images_dir.glob(f"*{ext.upper()}")))

    matching_pairs = []
    for image_path in image_files:
        # Find corresponding label file
        label_name = image_path.stem + ".txt"
        label_path = labels_dir / label_name

        if label_path.exists():
            matching_pairs.append((image_path, label_path))
        else:
            print(f"Warning: No label file found for {image_path.name}")

    return matching_pairs


def save_measurements_to_csv(
    measurements_data: List[Dict[str, Any]], output_path: Path
) -> None:
    """
    Save measurements data to CSV file.

    Args:
        measurements_data: List of measurement dictionaries
        output_path: Path to save the CSV file
    """
    if not measurements_data:
        print("No measurements data to save.")
        return

    df = pd.DataFrame(measurements_data)
    df.to_csv(output_path, index=False)
    print(f"Measurements saved to: {output_path}")


def create_output_directory(output_dir: Path) -> None:
    """
    Create output directory if it doesn't exist.

    Args:
        output_dir: Path to the output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)


def validate_directories(images_dir: str, labels_dir: str) -> Tuple[bool, str]:
    """
    Validate that the required directories exist.

    Args:
        images_dir: Path to images directory
        labels_dir: Path to labels directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.isdir(images_dir):
        return False, f"Images directory not found: {images_dir}"

    if not os.path.isdir(labels_dir):
        return False, f"Labels directory not found: {labels_dir}"

    return True, ""


def prepare_measurement_data(
    image_name: str,
    polygon_count: int,
    polygon_id: int,
    measurements: Dict[str, float],
    scale_pixels_per_cm: float,
) -> Dict[str, Any]:
    """
    Prepare measurement data for CSV export.

    Args:
        image_name: Name of the image file
        polygon_count: Total number of polygons in the image
        polygon_id: ID of the current polygon
        measurements: Dictionary with measurement values in pixels
        scale_pixels_per_cm: Scale factor for conversion to cm

    Returns:
        Dictionary with formatted measurement data
    """
    # Convert to cm using scale
    max_length_cm = (
        measurements["max_length"] / scale_pixels_per_cm
        if scale_pixels_per_cm > 0
        else 0
    )
    max_width_cm = (
        measurements["max_width"] / scale_pixels_per_cm
        if scale_pixels_per_cm > 0
        else 0
    )
    area_cm2 = (
        measurements["area"] / (scale_pixels_per_cm**2)
        if scale_pixels_per_cm > 0
        else 0
    )

    return {
        "image_name": image_name,
        "polygon_count": polygon_count,
        "polygon_id": polygon_id,
        "max_length_cm": max_length_cm,
        "max_length_pixels": measurements["max_length"],
        "max_width_cm": max_width_cm,
        "max_width_pixels": measurements["max_width"],
        "area_cm2": area_cm2,
        "area_pixels2": measurements["area"],
        "scale_pixels_per_cm": scale_pixels_per_cm,
    }


def create_empty_measurement_data(
    image_name: str, scale_pixels_per_cm: float
) -> Dict[str, Any]:
    """
    Create empty measurement data for images with no polygons.

    Args:
        image_name: Name of the image file
        scale_pixels_per_cm: Scale factor used

    Returns:
        Dictionary with empty measurement data
    """
    return {
        "image_name": image_name,
        "polygon_count": 0,
        "polygon_id": 0,
        "max_length_cm": 0,
        "max_length_pixels": 0,
        "max_width_cm": 0,
        "max_width_pixels": 0,
        "area_cm2": 0,
        "area_pixels2": 0,
        "scale_pixels_per_cm": scale_pixels_per_cm,
    }
