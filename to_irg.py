#!/usr/bin/env python3
import io

# This file should convert the jpeg from the HTI cameras to a Infiray IRG file

from thermo.structures import ThermoImage, ThermoMetadata
import struct

def generate_irg_header(thermo : ThermoImage, vis_jpeg_bytes: bytes) -> bytes:
    """
    Generates the header of the IRG file
    These header are exactly 128 bytes long
    :param thermo:
    :param vis_jpeg_bytes: A JPEG encoded bytes object of the visible image
    :return:
    """

    # First we start with a header denoting the camera model (we use BA AB here, which seems to be used in Vevor SC240M)
    # See https://github.com/jelle737/Vevor-Thermal-Utilities/tree/main
    out = bytes([0xBA, 0xAB])

    # Next 0x80 0x00 bytes which are always the same
    out += bytes([0x80, 0x00])

    # Then the length of our grayscale image follows (as uint32)
    out += struct.pack("<I", len(thermo.gray_scale))
    # Next the height of the grayscale image as uint16 integer
    out += struct.pack("<H", len(thermo.gray_scale[0]))
    # And the width of the grayscale image as uint16 integer
    out += struct.pack("<H", len(thermo.gray_scale))

    # Then a zero byte as seperator
    out += bytes([0x00])
    # We should have 13 bytes now
    assert len(out) == 13

    # Then the length of the temperature data follows (as uint32), we have to multiply it by 2 as we have 2 bytes per pixel
    out += struct.pack("<I", len(thermo.temperature) * 2)
    # Next the height of the temperature data as uint16 integer
    out += struct.pack("<H", len(thermo.temperature[0]))
    # And the width of the temperature data as uint16 integer
    out += struct.pack("<H", len(thermo.temperature))

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

def generate_irg_file_bytes(thermo: ThermoImage) -> bytes:
    out = bytes()

    # Convert the visible image to a JPEG
    bytes_io = io.BytesIO()
    thermo.visible.save(bytes_io, format="JPEG")
    vis_jpeg_bytes = bytes_io.getvalue()

    # Generate the header
    out += generate_irg_header(thermo, vis_jpeg_bytes)

    # Next the grayscale image as uint8 bytes follow
    # The data needs to be transposed to be in the correct format
    for row in thermo.gray_scale.transpose():
        for pixel in row:
            out += struct.pack("<B", pixel)

    # Next the temperature data as uint16 bytes follow (in deci kelvin)
    for row in thermo.temperature_kelvin().transpose():
        for pixel in row:
            out += struct.pack("<H", int(pixel * 10))

    # Finally the visible image as JPEG bytes follow
    out += vis_jpeg_bytes

    return out

# Read in the thermo image
path = "data/p1.jpg"



# Load the image
picture = ThermoImage.from_path(path)

# Open the IRG file for writing
with open("data/p1.irg", "wb") as f:
    # Write the IRG file
    f.write(generate_irg_file_bytes(picture))