"""
Geometry utilities for polygon measurements.
"""

import numpy as np
from typing import List, Tuple, Dict


def calculate_polygon_measurements(
    polygon_points: List[Tuple[float, float]], image_shape: Tuple[int, int]
) -> Dict[str, float]:
    """
    Calculate max length, max width, and area of polygon.

    Args:
        polygon_points: List of (x, y) tuples in normalized coordinates
        image_shape: (height, width) of the image

    Returns:
        Dictionary with max_length, max_width, and area in pixels
    """
    if len(polygon_points) < 3:
        return {"max_length": 0, "max_width": 0, "area": 0}

    # Convert normalized coordinates to pixel coordinates
    height, width = image_shape[:2]
    pixel_points = []
    for x_norm, y_norm in polygon_points:
        x_pixel = x_norm * width
        y_pixel = y_norm * height
        pixel_points.append((x_pixel, y_pixel))

    pixel_points = np.array(pixel_points)

    # Find maximum distance between any two points (max length)
    max_length = _calculate_max_distance(pixel_points)

    # Calculate max width (perpendicular to the longest dimension)
    max_width = _calculate_max_width(pixel_points)

    # Calculate area using Shoelace formula
    area = _calculate_polygon_area(pixel_points)

    return {"max_length": max_length, "max_width": max_width, "area": area}


def _calculate_max_distance(pixel_points: np.ndarray) -> float:
    """Calculate maximum distance between any two points."""
    max_length = 0
    for i in range(len(pixel_points)):
        for j in range(i + 1, len(pixel_points)):
            x1, y1 = pixel_points[i]
            x2, y2 = pixel_points[j]
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            max_length = max(max_length, distance)
    return max_length


def _calculate_max_width(pixel_points: np.ndarray) -> float:
    """Calculate maximum width perpendicular to the longest dimension."""
    max_width = 0
    if len(pixel_points) >= 2:
        try:
            from scipy.spatial import ConvexHull

            # Use convex hull to find the minimum bounding rectangle
            hull = ConvexHull(pixel_points)
            hull_points = pixel_points[hull.vertices]

            # Calculate all possible widths perpendicular to edges
            for i in range(len(hull_points)):
                p1 = hull_points[i]
                p2 = hull_points[(i + 1) % len(hull_points)]

                # Edge vector
                edge_vec = p2 - p1
                edge_length = np.linalg.norm(edge_vec)
                if edge_length == 0:
                    continue

                # Unit vector along edge
                edge_unit = edge_vec / edge_length

                # Project all points onto perpendicular to this edge
                perp_vec = np.array([-edge_unit[1], edge_unit[0]])
                projections = [np.dot(point, perp_vec) for point in hull_points]
                width = max(projections) - min(projections)
                max_width = max(max_width, width)

        except ImportError:
            # Fallback: use simple approach if scipy not available
            max_width = _calculate_max_width_simple(pixel_points)
        except Exception:
            # Fallback: use simple approach if convex hull fails
            max_width = _calculate_max_width_simple(pixel_points)

    return max_width


def _calculate_max_width_simple(pixel_points: np.ndarray) -> float:
    """Simple fallback method for calculating max width."""
    min_x, max_x = np.min(pixel_points[:, 0]), np.max(pixel_points[:, 0])
    min_y, max_y = np.min(pixel_points[:, 1]), np.max(pixel_points[:, 1])
    width_x = max_x - min_x
    width_y = max_y - min_y
    return min(width_x, width_y)


def _calculate_polygon_area(pixel_points: np.ndarray) -> float:
    """Calculate area using Shoelace formula."""
    area = 0
    if len(pixel_points) >= 3:
        x = pixel_points[:, 0]
        y = pixel_points[:, 1]
        area = 0.5 * abs(
            sum(
                x[i] * y[(i + 1) % len(x)] - x[(i + 1) % len(x)] * y[i]
                for i in range(len(x))
            )
        )
    return area


def calculate_distance(
    point1: Tuple[float, float], point2: Tuple[float, float]
) -> float:
    """Calculate Euclidean distance between two points."""
    return np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


def calculate_measurement_statistics(measurements: List[float]) -> Dict[str, float]:
    """
    Calculate statistics for a list of measurements.

    Args:
        measurements: List of measurement values

    Returns:
        Dictionary with mean, std_dev, and coefficient_of_variation
    """
    if not measurements:
        return {"mean": 0, "std_dev": 0, "coefficient_of_variation": 0}

    measurements = np.array(measurements)
    mean = np.mean(measurements)
    std_dev = np.std(measurements)

    coefficient_of_variation = (std_dev / mean) * 100 if mean > 0 else 100

    return {
        "mean": mean,
        "std_dev": std_dev,
        "coefficient_of_variation": coefficient_of_variation,
    }
