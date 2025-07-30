"""
Core measurement functionality for polygon measurement tool.
"""

import cv2
import numpy as np
import time
import platform
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

from ..config import *
from ..ui.display import (
    draw_crosshair,
    draw_measurement_line,
    draw_grid,
    draw_instructions,
)
from ..utils.file_utils import (
    load_yolo_polygons,
    get_matching_files,
    save_measurements_to_csv,
    create_output_directory,
    prepare_measurement_data,
    create_empty_measurement_data,
)
from .geometry import (
    calculate_polygon_measurements,
    calculate_distance,
    calculate_measurement_statistics,
)


class EnhancedPolygonMeasurementTool:
    """Enhanced polygon measurement tool with improved UI and functionality."""

    def __init__(
        self, images_dir: str, labels_dir: str, output_dir: str = "measurements"
    ):
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)
        self.output_dir = Path(output_dir)
        create_output_directory(self.output_dir)

        # Scale measurement variables
        self.scale_pixels_per_cm = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.current_image = None
        self.display_image = None

        # Reference measurement tracking
        self.reference_measurements = []
        self.current_measurement = 1
        self.max_measurements = MAX_MEASUREMENTS

        # UI enhancement variables
        self.mouse_pos = (0, 0)
        self.window_name = WINDOW_NAME
        self.show_grid = False

        # Performance optimization
        self.last_update_time = 0
        self.update_interval = UPDATE_INTERVAL

        # Platform-specific settings
        self.is_macos = platform.system() == "Darwin"

    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for drawing reference lines."""
        self.mouse_pos = (x, y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            self.update_display()

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
            self.update_display()

        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, y)
                self.update_display()

    def update_display(self):
        """Update display with rate limiting for better performance."""
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return

        self.last_update_time = current_time

        if self.current_image is None:
            return

        # Start with current image
        self.display_image = self.current_image.copy()

        # Draw grid if enabled
        if self.show_grid:
            draw_grid(self.display_image)

        # Draw measurement line
        if self.start_point and self.end_point:
            draw_measurement_line(self.display_image, self.start_point, self.end_point)

        # Draw crosshair at mouse position
        draw_crosshair(self.display_image, self.mouse_pos)

        # Draw UI elements
        draw_instructions(
            self.display_image,
            self.current_measurement,
            self.max_measurements,
            self.start_point,
            self.end_point,
            self.reference_measurements,
        )

        # Show the image
        cv2.imshow(self.window_name, self.display_image)

    def set_scale_from_image(self, image_path: Path) -> bool:
        """Set scale by averaging three reference measurements."""
        print(f"\n" + "=" * 80)
        print(f"SETTING REFERENCE SCALE: {image_path.name}")
        print("=" * 80)
        self._print_setup_instructions()

        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Error: Could not load image {image_path}")
            return False

        self.current_image = image.copy()
        self.show_grid = False

        # Reset measurement tracking
        self.reference_measurements = []
        self.current_measurement = 1

        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(self.window_name, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # Initial display update
        self.update_display()

        return self._collect_measurements()

    def _print_setup_instructions(self):
        """Print setup instructions for the scale setting process."""
        print("IMPORTANT: You need to draw 3 reference lines for accuracy!")
        print("Each line should represent exactly 1 cm on the ruler")
        print("REMEMBER: Press 'S' after drawing each line to save it!")
        print("\nPROCESS:")
        print("   1. Draw first reference line (1 cm)")
        print("   2. Press 'S' to save → Tool will ask for second line")
        print("   3. Draw second reference line (1 cm)")
        print("   4. Press 'S' to save → Tool will ask for third line")
        print("   5. Draw third reference line (1 cm)")
        print("   6. Press 'S' to save → Tool calculates average scale")
        print("\nCONTROLS:")
        print("   • 'S' = SAVE current measurement (MUST press after each line!)")
        print("   • 'R' = Reset/redraw current line")
        print("   • 'G' = Toggle grid overlay")
        print("   • 'Q' = Quit/skip this image")
        print("   • ESC = Exit tool")
        print("\nStarting measurement process...")

    def _collect_measurements(self) -> bool:
        """Collect the three reference measurements."""
        while self.current_measurement <= self.max_measurements:
            key = cv2.waitKey(30) & 0xFF

            # Check if window was closed
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                cv2.destroyAllWindows()
                return False

            if key == ord("s") and self.start_point and self.end_point:
                if self._save_current_measurement():
                    if self.current_measurement > self.max_measurements:
                        break
            elif key == ord("r"):
                self._reset_current_measurement()
            elif key == ord("g"):
                self._toggle_grid()
            elif key == ord("q") or key == 27:  # 'q' or ESC
                cv2.destroyAllWindows()
                return False

        return self._finalize_scale_calculation()

    def _save_current_measurement(self) -> bool:
        """Save the current measurement."""
        length = calculate_distance(self.start_point, self.end_point)
        self.reference_measurements.append(length)

        print(f"\n SAVED Measurement {self.current_measurement}/3: {length:.2f} pixels")

        if self.current_measurement < self.max_measurements:
            next_measurement = self.current_measurement + 1
            print(
                f" Now draw measurement {next_measurement}/3 (remember to press 'S' to save!)"
            )
        else:
            print(" All 3 measurements collected! Calculating average...")

        # Reset for next measurement
        self.start_point = None
        self.end_point = None
        self.current_measurement += 1
        self.update_display()
        return True

    def _reset_current_measurement(self):
        """Reset the current measurement."""
        self.start_point = None
        self.end_point = None
        self.update_display()

    def _toggle_grid(self):
        """Toggle grid display."""
        self.show_grid = not self.show_grid
        self.update_display()

    def _finalize_scale_calculation(self) -> bool:
        """Finalize the scale calculation from collected measurements."""
        if len(self.reference_measurements) != MAX_MEASUREMENTS:
            print("Error: Could not collect 3 measurements")
            cv2.destroyAllWindows()
            return False

        # Calculate statistics
        stats = calculate_measurement_statistics(self.reference_measurements)

        print(f"\n" + "=" * 60)
        print("REFERENCE SCALE ANALYSIS")
        print("=" * 60)
        print("Your 3 measurements:")
        for i, measurement in enumerate(self.reference_measurements, 1):
            print(f"   Measurement {i}: {measurement:.2f} pixels")

        print(f"\nAVERAGE: {stats['mean']:.2f} pixels per cm")
        print(f"Standard deviation: {stats['std_dev']:.2f} pixels")

        # Check measurement consistency
        if stats["coefficient_of_variation"] > MAX_COEFFICIENT_VARIATION:
            print(
                f"\nWARNING: High variation ({stats['coefficient_of_variation']:.1f}%) between measurements!"
            )
            print("   Consider retaking measurements for better accuracy")
        else:
            print(
                f"Good consistency! Variation: {stats['coefficient_of_variation']:.1f}%"
            )

        self.scale_pixels_per_cm = stats["mean"]
        print(f"\nSCALE SUCCESSFULLY SET: {self.scale_pixels_per_cm:.2f} pixels = 1 cm")
        print("=" * 60)
        cv2.destroyAllWindows()
        return True

    def process_image(self, image_path: Path, label_path: Path):
        """Process a single image and its corresponding label file."""
        print(f"\n" + "=" * 60)
        print(f"Processing: {image_path.name}")
        print("=" * 60)

        # Load image to get dimensions
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Error: Could not load image {image_path}")
            return

        # Set scale for this specific image
        print(f"\nSetting scale for: {image_path.name}")
        if not self.set_scale_from_image(image_path):
            print(f"Skipping {image_path.name} - scale not set")
            return

        # Load polygons from label file
        polygons = load_yolo_polygons(label_path)
        csv_data = self._process_polygons(polygons, image, image_path)

        # Save CSV for this image
        output_csv = self.output_dir / f"{image_path.stem}_measurements.csv"
        save_measurements_to_csv(csv_data, output_csv)

        print(f"Scale used: {self.scale_pixels_per_cm:.2f} pixels per cm")

        # Reset scale for next image
        self.scale_pixels_per_cm = None

    def _process_polygons(
        self, polygons: List[Dict[str, Any]], image: np.ndarray, image_path: Path
    ) -> List[Dict[str, Any]]:
        """Process polygons and calculate measurements."""
        csv_data = []

        if not polygons:
            print(f"No polygons found in {image_path.name}")
            csv_data.append(
                create_empty_measurement_data(image_path.name, self.scale_pixels_per_cm)
            )
        else:
            print(f"Found {len(polygons)} polygons")

            for i, polygon in enumerate(polygons):
                measurements = calculate_polygon_measurements(
                    polygon["points"], image.shape
                )

                measurement_data = prepare_measurement_data(
                    image_path.name,
                    len(polygons),
                    i + 1,
                    measurements,
                    self.scale_pixels_per_cm,
                )
                csv_data.append(measurement_data)

                # Print measurements
                print(f"  Polygon {i+1}:")
                print(
                    f"    Length: {measurement_data['max_length_cm']:.2f} cm "
                    f"({measurements['max_length']:.1f} px)"
                )
                print(
                    f"    Width:  {measurement_data['max_width_cm']:.2f} cm "
                    f"({measurements['max_width']:.1f} px)"
                )
                print(
                    f"    Area:   {measurement_data['area_cm2']:.2f} cm² "
                    f"({measurements['area']:.1f} px²)"
                )

        return csv_data

    def run(self):
        """Main execution function."""
        print("=== Polygon Measurement Tool ===")
        print(f"Images directory: {self.images_dir}")
        print(f"Labels directory: {self.labels_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Platform: {platform.system()}")

        # Get matching image and label files
        matching_pairs = get_matching_files(self.images_dir, self.labels_dir)

        if not matching_pairs:
            print("Error: No matching image and label file pairs found!")
            return

        self._print_feature_summary(len(matching_pairs))

        # Process all images
        processed_count = 0
        total_polygons = 0

        for i, (image_path, label_path) in enumerate(matching_pairs, 1):
            print(f"\n[Image {i}/{len(matching_pairs)}]")

            # Count polygons for summary
            polygons = load_yolo_polygons(label_path)
            original_scale = self.scale_pixels_per_cm

            # Process the image
            self.process_image(image_path, label_path)

            # Check if processing was successful
            if (
                self.scale_pixels_per_cm is not None
                or original_scale != self.scale_pixels_per_cm
            ):
                processed_count += 1
                total_polygons += len(polygons)

        # Create summary report
        self._create_summary_report(processed_count, total_polygons)

    def _print_feature_summary(self, pair_count: int):
        """Print summary of enhanced features."""
        print(f"Found {pair_count} matching image-label pairs")
        print("\nEnhanced UI Features:")
        print("  - Crosshair cursor overlay for better visibility")
        print("  - Three-measurement reference scale averaging for accuracy")
        print("  - Real-time measurement preview")
        print("  - Grid overlay (toggle with 'g')")
        print("  - Enhanced visual feedback with larger fonts")
        print("  - Directory selection dialog")
        print("  - Statistical analysis of measurement consistency")
        print("\nFor each image:")
        print("  1. Draw 3 reference lines on the ruler (each = 1 cm)")
        print("  2. Press 's' to save each measurement")
        print("  3. Tool will automatically calculate average scale")
        print("  4. Press 'q' to skip the image")
        print("\nStarting processing automatically...")

    def _create_summary_report(self, processed_count: int, total_polygons: int):
        """Create a summary report of all processed images."""
        print(f"\nProcessing complete!")
        print(f"Total images processed: {processed_count}")
        print(f"Total polygons measured: {total_polygons}")
        print(f"Individual CSV files are in: {self.output_dir}")
        print(f"Note: Each image had its own scale reference set by the user")
