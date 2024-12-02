#!/usr/bin/env python3

import argparse
from thermo.structures import ThermoImage, ThermoMetadata
import matplotlib.pyplot as plt

def print_info(image: ThermoImage) -> None:
    metadata = image.info

    print("====== Picture info =======")
    print(f"Camera: {metadata.model} (Firmware {metadata.firmware})")
    print(f"Thermal resolution: {image.thermal_resolution[0]}x{image.thermal_resolution[1]}")
    print(f"Visible resolution: {image.visible_resolution[0]}x{image.visible_resolution[1]}")
    print(f"Capture time: {metadata.capture_time}")
    print("")
    print(f"Center: {metadata.spot_center.value_formatted()} (x={metadata.spot_center.x}, y={metadata.spot_center.y})")
    print(f"Min temperature: {metadata.spot_min.value_formatted()} (x={metadata.spot_min.x}, y={metadata.spot_min.y})")
    print(f"Max temperature: {metadata.spot_max.value_formatted()} (x={metadata.spot_max.x}, y={metadata.spot_max.y})")
    print("")
    print(f"Palette: {metadata.selected_palette.name}")
    print(f"Emissivity: {metadata.emissivity}")
    print(f"Unit: {metadata.selected_unit.name}")
    print(f"Mixing factor: {metadata.mix_factor}")
    print(f"Image margins: {metadata.image_margins}")
    print("")
    print(f"Max temperature in temperature data: {image.temperature_celsius.max()} °C")
    print(f"Min temperature in temperature data: {image.temperature_celsius.min()} °C")
    print("===========================")


# Parse argument file path
parser = argparse.ArgumentParser(description="Parse a HTI JPEG image")
parser.add_argument("path", type=str, help="Path to the JPEG image")
args = parser.parse_args()

path = args.path

# Load the image
picture = ThermoImage.from_path(path)

# Display the contained mixed and visible image
picture.mixed.show()
picture.visible.show()

# Print the metadata
print_info(picture)

# Plot the temperature data
plt.imshow(picture.temperature_celsius.transpose())
plt.title("Temperature data (°C)")
plt.colorbar()
plt.show()

# Plot the gray scale data
plt.imshow(picture.gray_scale.transpose(), cmap="gray")
plt.title("Gray scale data")
plt.colorbar()
plt.show()

