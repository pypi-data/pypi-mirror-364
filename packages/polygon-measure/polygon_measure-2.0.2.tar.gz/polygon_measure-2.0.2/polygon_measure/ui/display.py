"""
UI display functions for polygon measurement tool.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from ..config import *


def draw_crosshair(
    img: np.ndarray,
    center: Tuple[int, int],
    size: int = CROSSHAIR_SIZE,
    color: Tuple[int, int, int] = CROSSHAIR_COLOR,
    thickness: int = 3,
) -> None:
    """Draw crosshair at cursor position for better visibility."""
    x, y = center

    # Horizontal line
    cv2.line(img, (x - size, y), (x + size, y), color, thickness)
    # Vertical line
    cv2.line(img, (x, y - size), (x, y + size), color, thickness)

    # Add center dot
    cv2.circle(img, center, 4, color, -1)


def draw_measurement_line(
    img: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: Tuple[int, int, int] = LINE_COLOR,
    thickness: int = 4,
) -> None:
    """Draw measurement line with text."""
    if not start or not end:
        return

    img_height, img_width = img.shape[:2]

    # Draw line and circles
    cv2.line(img, start, end, color, thickness)
    cv2.circle(img, start, 8, color, -1)
    cv2.circle(img, end, 8, color, -1)

    # Calculate distance
    length = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)

    # Calculate midpoint for text positioning
    mid_x = (start[0] + end[0]) // 2
    mid_y = (start[1] + end[1]) // 2

    # Create measurement text
    text = f"{length:.1f}px"
    text_size = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE_MEDIUM, FONT_THICKNESS_MEDIUM
    )[0]

    # Smart text positioning
    text_x, text_y = _calculate_text_position(
        mid_x, mid_y, text_size, img_width, img_height
    )

    # Draw text background and border
    _draw_text_background(img, text_x, text_y, text_size, color, img_width, img_height)

    # Draw the text
    cv2.putText(
        img,
        text,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_MEDIUM,
        color,
        FONT_THICKNESS_MEDIUM,
    )


def draw_grid(
    img: np.ndarray,
    spacing: int = GRID_SPACING,
    color: Tuple[int, int, int] = GRID_COLOR,
) -> None:
    """Draw helpful grid lines."""
    h, w = img.shape[:2]

    # Vertical lines
    for x in range(0, w, spacing):
        cv2.line(img, (x, 0), (x, h), color, 1)

    # Horizontal lines
    for y in range(0, h, spacing):
        cv2.line(img, (0, y), (w, y), color, 1)


def draw_instructions(
    img: np.ndarray,
    current_measurement: int,
    max_measurements: int,
    start_point: Optional[Tuple[int, int]],
    end_point: Optional[Tuple[int, int]],
    reference_measurements: List[float],
) -> None:
    """Draw large, prominent instructions in top portion of the image."""
    img_height, img_width = img.shape[:2]

    # Main instruction panel
    _draw_main_instruction_panel(
        img,
        img_width,
        img_height,
        current_measurement,
        max_measurements,
        start_point,
        end_point,
    )

    # Previous measurements display
    if reference_measurements:
        _draw_measurements_panel(img, img_width, img_height, reference_measurements)


def _calculate_text_position(
    mid_x: int, mid_y: int, text_size: Tuple[int, int], img_width: int, img_height: int
) -> Tuple[int, int]:
    """Calculate optimal position for text to avoid going outside image bounds."""
    padding = PANEL_PADDING
    line_offset = 20

    # Try to position text above the line first
    text_x = mid_x - text_size[0] // 2
    text_y = mid_y - line_offset

    # Adjust if text would go outside image bounds
    if text_x < padding:
        text_x = padding
    elif text_x + text_size[0] + padding > img_width:
        text_x = img_width - text_size[0] - padding

    if text_y - text_size[1] < padding:
        # If above doesn't work, try below
        text_y = mid_y + line_offset + text_size[1]
        if text_y + padding > img_height:
            # If below doesn't work, try to the side
            text_y = mid_y + text_size[1] // 2
            text_x = mid_x + line_offset
            if text_x + text_size[0] + padding > img_width:
                text_x = mid_x - text_size[0] - line_offset

    # Final boundary check
    text_x = max(padding, min(text_x, img_width - text_size[0] - padding))
    text_y = max(text_size[1] + padding, min(text_y, img_height - padding))

    return text_x, text_y


def _draw_text_background(
    img: np.ndarray,
    text_x: int,
    text_y: int,
    text_size: Tuple[int, int],
    color: Tuple[int, int, int],
    img_width: int,
    img_height: int,
) -> None:
    """Draw background and border for text."""
    bg_padding = 6
    bg_x1 = max(0, text_x - bg_padding)
    bg_y1 = max(0, text_y - text_size[1] - bg_padding)
    bg_x2 = min(img_width, text_x + text_size[0] + bg_padding)
    bg_y2 = min(img_height, text_y + bg_padding)

    # Draw semi-transparent background
    overlay = img.copy()
    cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)

    # Draw border around text background
    cv2.rectangle(img, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2)


def _draw_main_instruction_panel(
    img: np.ndarray,
    img_width: int,
    img_height: int,
    current_measurement: int,
    max_measurements: int,
    start_point: Optional[Tuple[int, int]],
    end_point: Optional[Tuple[int, int]],
) -> None:
    """Draw the main instruction panel."""
    # Panel dimensions - 50% of image width and top 50% of height
    panel_width = int(img_width * 0.5)
    panel_height = int(img_height * 0.5)

    # Position panel in top center
    panel_x = (img_width - panel_width) // 2
    panel_y = 20

    # Ensure panel doesn't exceed image boundaries
    panel_x = max(10, min(panel_x, img_width - panel_width - 10))
    panel_y = max(10, min(panel_y, img_height - panel_height - 10))

    # Draw panel background
    overlay = img.copy()
    cv2.rectangle(
        overlay,
        (panel_x, panel_y),
        (panel_x + panel_width, panel_y + panel_height),
        INSTRUCTION_PANEL_COLOR,
        -1,
    )
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

    # Draw border
    cv2.rectangle(
        img,
        (panel_x, panel_y),
        (panel_x + panel_width, panel_y + panel_height),
        INSTRUCTION_BORDER_COLOR,
        5,
    )

    # Draw instructions
    instructions = _get_instructions_text(current_measurement, max_measurements)
    _draw_instructions_text(
        img, instructions, panel_x, panel_y, panel_width, panel_height
    )

    # Draw current measurement info
    if start_point and end_point:
        _draw_current_measurement_info(
            img,
            start_point,
            end_point,
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            current_measurement,
        )


def _draw_measurements_panel(
    img: np.ndarray,
    img_width: int,
    img_height: int,
    reference_measurements: List[float],
) -> None:
    """Draw the completed measurements panel."""
    measurements_x = 10
    measurements_y = img_height - (30 + len(reference_measurements) * 25 + 30) - 10
    measurements_width = 250
    measurements_height = 30 + len(reference_measurements) * 25 + 30

    # Draw background
    overlay = img.copy()
    cv2.rectangle(
        overlay,
        (measurements_x, measurements_y),
        (measurements_x + measurements_width, measurements_y + measurements_height),
        MEASUREMENT_PANEL_COLOR,
        -1,
    )
    cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)

    # Draw border
    cv2.rectangle(
        img,
        (measurements_x, measurements_y),
        (measurements_x + measurements_width, measurements_y + measurements_height),
        MEASUREMENT_BORDER_COLOR,
        2,
    )

    # Draw title
    cv2.putText(
        img,
        "Completed:",
        (measurements_x + 10, measurements_y + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        MEASUREMENT_BORDER_COLOR,
        2,
    )

    # Draw measurements
    for i, measurement in enumerate(reference_measurements):
        y_pos = measurements_y + 45 + i * 25
        cv2.putText(
            img,
            f"{i+1}: {measurement:.1f} px",
            (measurements_x + 15, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

    # Show average if multiple measurements
    if len(reference_measurements) > 1:
        avg = np.mean(reference_measurements)
        cv2.putText(
            img,
            f"Avg: {avg:.1f} px",
            (measurements_x + 10, measurements_y + measurements_height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            TEXT_COLOR,
            2,
        )


def _get_instructions_text(
    current_measurement: int, max_measurements: int
) -> List[str]:
    """Get the instructions text for the current measurement."""
    return [
        f"MEASUREMENT {current_measurement} OF {max_measurements}",
        "",
        "DRAW REFERENCE SCALE:",
        "- Draw a line on ruler = 1cm",
        f"- Press 'S' to SAVE measurement {current_measurement}",
        "- Press 'R' to reset current line",
        "",
        "CONTROLS:",
        "- 'G' = Toggle grid",
        "- 'Q' = Quit/Skip image",
        "",
        "PROCESS:",
        "1. Draw 3 reference lines total",
        "2. Press 'S' after each line",
        "3. Tool calculates average scale",
    ]


def _draw_instructions_text(
    img: np.ndarray,
    instructions: List[str],
    panel_x: int,
    panel_y: int,
    panel_width: int,
    panel_height: int,
) -> None:
    """Draw the instructions text on the panel."""
    # Calculate dynamic font size based on panel size
    base_font_scale = max(0.6, min(1.8, panel_width / 700))
    line_spacing = max(25, int(30 * (panel_height / 400)))

    start_y = panel_y + 35
    current_y = start_y

    for i, instruction in enumerate(instructions):
        if instruction == "":  # Skip empty lines but add spacing
            current_y += line_spacing // 2
            continue

        # Check if text will fit within panel boundaries
        if current_y + line_spacing > panel_y + panel_height - 30:
            break

        text_x = panel_x + TEXT_PADDING

        # Different colors and sizes for different types of text
        color, font_scale, thickness = _get_text_style(instruction, base_font_scale, i)

        # Ensure text fits within panel width
        text_size = cv2.getTextSize(
            instruction, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )[0]

        # Adjust font size if text is too wide
        if text_size[0] > panel_width - 50:
            font_scale *= (panel_width - 50) / text_size[0]
            thickness = max(1, int(thickness * 0.8))

        cv2.putText(
            img,
            instruction,
            (text_x, current_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
        )

        current_y += line_spacing


def _get_text_style(
    instruction: str, base_font_scale: float, index: int
) -> Tuple[Tuple[int, int, int], float, int]:
    """Get the appropriate text style based on instruction type."""
    if index == 0:  # Title
        return (0, 255, 255), base_font_scale * 1.4, max(2, int(3 * base_font_scale))
    elif any(
        instruction.startswith(prefix) for prefix in ["DRAW", "CONTROLS", "PROCESS"]
    ):
        return TEXT_COLOR, base_font_scale * 1.1, max(2, int(3 * base_font_scale))
    elif instruction.startswith("-"):
        return (255, 255, 255), base_font_scale * 0.9, max(1, int(2 * base_font_scale))
    else:
        return (200, 200, 200), base_font_scale * 0.8, max(1, int(2 * base_font_scale))


def _draw_current_measurement_info(
    img: np.ndarray,
    start_point: Tuple[int, int],
    end_point: Tuple[int, int],
    panel_x: int,
    panel_y: int,
    panel_width: int,
    panel_height: int,
    current_measurement: int,
) -> None:
    """Draw current measurement information."""
    length = np.sqrt(
        (end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2
    )

    measurement_y = panel_y + panel_height - 80
    base_font_scale = max(0.6, min(1.8, panel_width / 700))

    # Only show if there's enough space
    if measurement_y > panel_y + 50:
        cv2.putText(
            img,
            f"CURRENT LINE: {length:.1f} pixels",
            (panel_x + TEXT_PADDING, measurement_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            base_font_scale * 1.0,
            TEXT_COLOR,
            max(2, int(3 * base_font_scale)),
        )
        cv2.putText(
            img,
            f">>> PRESS 'S' TO SAVE MEASUREMENT {current_measurement} <<<",
            (panel_x + TEXT_PADDING, measurement_y + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            base_font_scale * 0.8,
            (255, 255, 0),
            max(1, int(2 * base_font_scale)),
        )
