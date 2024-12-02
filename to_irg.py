#!/usr/bin/env python3
import io
import os

import numpy

# This file should convert the jpeg from the HTI cameras to a Infiray IRG file

from thermo.structures import ThermoImage, ThermoMetadata
import struct

def generate_irg_header(thermo : ThermoImage, vis_jpeg_bytes: bytes, mode: str = "upscale") -> bytes:
    """
    Generates the header of the IRG file
    These header are exactly 128 bytes long
    :param mode:
    :param thermo:
    :param vis_jpeg_bytes: A JPEG encoded bytes object of the visible image
    :param upscale_factor: The factor by which all ir resolutions should be upscaled
    :return:
    """

    if mode == "upscale":
        upscale_factor = thermo.visible_resolution[0] // thermo.thermal_resolution[0]
    else:
        upscale_factor = 1

    # First we start with a header denoting the camera model (we use BA AB here, which seems to be used in Vevor SC240M)
    # See https://github.com/jelle737/Vevor-Thermal-Utilities/tree/main
    out = bytes([0xBA, 0xAB])

    # Next 0x80 0x00 bytes which are always the same
    out += bytes([0x80, 0x00])

    # Then the length of our grayscale image follows (as uint32)
    out += struct.pack("<I", thermo.gray_scale.size * upscale_factor**2)
    # Next the height of the grayscale image as uint16 integer
    out += struct.pack("<H", len(thermo.gray_scale[0]) * upscale_factor)
    # And the width of the grayscale image as uint16 integer
    out += struct.pack("<H", len(thermo.gray_scale) * upscale_factor)

    # Then a zero byte as seperator
    out += bytes([0x00])
    # We should have 13 bytes now
    assert len(out) == 13

    # Then the length of the temperature data follows (as uint32), we have to multiply it by 2 as we have 2 bytes per pixel
    out += struct.pack("<I", thermo.temperature.size * 2 * upscale_factor**2)
    # Next the height of the temperature data as uint16 integer
    out += struct.pack("<H", len(thermo.temperature[0]) * upscale_factor)
    # And the width of the temperature data as uint16 integer
    out += struct.pack("<H", len(thermo.temperature) * upscale_factor)

    # Then a zero byte as seperator (or maybe 1?)
    out += bytes([0x00])
    # We should have 22 bytes now
    assert len(out) == 22

    # Then the length of the visible image follows (as uint32)
    out += struct.pack("<I", len(vis_jpeg_bytes))
    vis_width, vis_height = thermo.visible.size
    # Next the height of the visible image as uint16 integer
    out += struct.pack("<H", vis_height)
    # And the width of the visible image as uint16 integer
    out += struct.pack("<H", vis_width)

    # We should have 30 bytes now
    assert len(out) == 30

    # Then the emissivity times 10000 follows (as uint32)
    out += struct.pack("<I", int(thermo.info.emissivity * 10000))

    # Then the reflective temperature times 10000 follows (as uint32) (in celsius)
    # Just use a fixed value here
    out += struct.pack("<I", int((24.9 + 273) * 10000))

    # Then the ambient temperature times 10000 follows (as uint32) (in celsius)
    # Just use a fixed value here
    out += struct.pack("<I", int((24.9 + 273) * 10000))

    # Then the distance times 1000 follows (as uint32) (in meters)
    # Just use a fixed value here
    out += struct.pack("<I", int(5.0 * 1000))

    # Then 4000 as uint32 follows
    out += struct.pack("<I", 4000)

    # We should have 50 bytes now
    assert len(out) == 50

    # Then the transmittivity times 10000 follows (as uint32)
    # Just use a fixed value here
    out += struct.pack("<I", int(1.0 * 10000))

    # Then 4 zero bytes follow
    out += bytes([0x00, 0x00, 0x00, 0x00])

    # Then a 10000 as uint32 follows
    out += struct.pack("<I", 10000)

    # We should have 62 bytes now
    assert len(out) == 62

    # Then a few zero bytes follow until offset 70
    out += bytes([0x00] * 8)

    # We should have 70 bytes now
    assert len(out) == 70

    # Then either 4 or 1026 as uint32 follows
    out += struct.pack("<I", 4)

    # Then the temperature unit as uint8 follows (0 = Celsius, 1 = Kelvin, 2 = Fahrenheit)
    # We just use kelvin here
    out += bytes([0x01])

    # We should have 75 bytes now
    assert len(out) == 75

    # Then a lot of zero bytes follow until offset 126
    out += bytes([0x00] * 51)

    # The header ends with 0xAC 0xCA
    out += bytes([0xAC, 0xCA])

    # We should have 128 bytes now
    assert len(out) == 128

    return out

def upscale_img(img: numpy.ndarray, factor: int) -> numpy.ndarray:
    """
    Upscale the given image by the given factor
    :param img:
    :param factor:
    :return:
    """
    return numpy.repeat(numpy.repeat(img, factor, axis=0), factor, axis=1)

def generate_irg_file_bytes(thermo: ThermoImage, mode: str = "upscale") -> bytes:
    """
    Generates the IRG file bytes for the given ThermoImage
    :param thermo:
    :param mode: How to treat the difference between the visible and thermal resolution.
        * "downscale" will downscale the visible image to the thermal resolution
        * 'upscale' will upscale the thermal image to the visible resolution
    :return:
    """

    out = bytes()

    # Convert the visible image to a JPEG
    bytes_io = io.BytesIO()

    if mode == "downscale":
        # Downscale the visible image to the thermal resolution
        visible = thermo.visible.resize(thermo.thermal_resolution, resample=0)
    else:
        visible = thermo.visible

    visible.save(bytes_io, format="JPEG")
    vis_jpeg_bytes = bytes_io.getvalue()

    # Generate the header
    out += generate_irg_header(thermo, vis_jpeg_bytes)

    upscale_factor = thermo.visible_resolution[0] // thermo.thermal_resolution[0]

    # The data needs to be transposed to be in the correct format
    if mode == "upscale":
        # Upscale the grayscale image to the visible resolution
        gray_scale = upscale_img(thermo.gray_scale, factor=upscale_factor)
    else:
        gray_scale = thermo.gray_scale

    for row in gray_scale.transpose():
        for pixel in row:
            out += struct.pack("<B", int(pixel))

    if mode == "upscale":
        # Upscale the temperature data to the visible resolution
        temperature = upscale_img(thermo.temperature_kelvin(), factor=upscale_factor)
    else:
        temperature = thermo.temperature_kelvin()

    # Next the temperature data as uint16 bytes follow (in deci kelvin)
    for row in temperature.transpose():
        for pixel in row:
            # For some reason the temperature data is always 0.1 kelvin too low, probably because of an indexing issue
            # We just add one to the value to fix this
            out += struct.pack("<H", int(pixel * 10) + 1)

    # Finally the visible image as JPEG bytes follow
    out += vis_jpeg_bytes

    return out

# Read in the thermo image
path = "input/"

# If path is a folder, iterate over all jpg files in the folder
if os.path.isdir(path):
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            # Load the image
            picture = ThermoImage.from_path(path + file)

            # Open the IRG file for writing
            with open("input/" + file.replace(".jpg", ".irg"), "wb") as f:
                # Write the IRG file
                f.write(generate_irg_file_bytes(picture, mode="upscale"))


# Load the image
#picture = ThermoImage.from_path(path)

# Open the IRG file for writing
#with open("data/p1.irg", "wb") as f:
#    # Write the IRG file
#    f.write(generate_irg_file_bytes(picture))