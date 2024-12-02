from __future__ import annotations

import io

from PIL import Image
from numpy import ndarray
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import struct

"""
Represents a spot in an image, containing temperature data
"""
@dataclass
class ThermoSpot:

    # X position
    x: int

    # Y position
    y: int

    # The temperature value in deci celsius
    value: int

    """
    Returns the temperature value in celsius
    """
    @property
    def value_celsius(self) -> float:
        return self.value / 10

    def value_formatted(self) -> str:
        return f"{self.value_celsius:.1f} °C"

    @classmethod
    def from_bytes(cls, data: bytes) -> ThermoSpot:
        # The first two bytes is the x position
        x = struct.unpack("<H", data[:2])[0]
        # The second 2 byte is the y position
        y = struct.unpack("<H", data[2:4])[0]
        # The next 4 bytes are the temperature value
        value = struct.unpack("<i", data[4:8])[0]
        return cls(x=x, y=y, value=value)

"""
This enum represents the available color palettes in the thermal cameras
"""
class ThermoPalette(Enum):
    SPECTRA = 0x0
    IRON = 0x1
    COOL = 0x2
    WHITEHOT = 0x3
    BLACKHOT = 0x4

class ThermoUnit(Enum):
    CELSIUS = 0x0
    FAHRENHEIT = 0x1

"""
This class represents the metadata of a thermal image (called t_IRInfo in hki code)
"""
@dataclass()
class ThermoMetadata:

    # The size of the metadata in bytes (this can be used as some kind of version number of the metadata format)
    byte_size: int

    # The camera model (e.g. "HT-04D") (called devType internally)
    model: str

    # The camera firmware version (called devVersion internally)
    firmware: str

    # The time the image was taken (called captureTime internally)
    capture_time: datetime

    # The spot representing the center spot
    spot_center: ThermoSpot

    # The spot representing the minimum temperature spot
    spot_min: ThermoSpot

    # The spot representing the maximum temperature spot
    spot_max: ThermoSpot

    # The emissivity that was configured in the camera
    emissivity: int

    # The color palette that was chosen in the camera for the picture
    selected_palette: ThermoPalette

    # The unit that was chosen in the camera for the picture
    selected_unit: ThermoUnit

    # The mix grade between the ir and vis picture in percentage (0 means only ir, 100 means only vis)
    mix_factor: int

    # Image margins of the visible picture [top, right, bottom, left] in pixels
    image_margins: tuple[int, int, int, int]

    """
    Returns the center temperature in celsius
    """
    @property
    def center_temperature(self) -> float:
        return self.spot_center.value_celsius

    """
    Returns the minimum temperature in celsius
    """
    @property
    def min_temperature(self) -> float:
        return self.spot_min.value_celsius

    """
    Returns the maximum temperature in celsius
    """
    @property
    def max_temperature(self) -> float:
        return self.spot_max.value_celsius

    @classmethod
    def from_bytes(cls, data: bytes) -> ThermoMetadata:
        # The first 4 bytes is the size of the following metadata (as uint32)
        size = struct.unpack("<I", data[:4])[0]
        data = data[4:]
        # If the size is not 112 bytes (or 104), we do not know this format
        # The 104 size is used in the HT-19 model with firmware (2.1.19)
        if size != 112 and size != 104:
            raise ValueError(f"Unknown metadata size: {size}")

        # Afterwards 20 bytes for the model follows
        model = data[:20].decode("utf-8").strip().rstrip("\x00")
        data = data[20:]

        # Afterwards 20 bytes for the firmware version follows
        firmware = data[:20].decode("utf-8").rstrip("\x00")
        data = data[20:]

        # The next 20 bytes are the capture datetime as string
        captureTime = datetime.strptime(data[:20].decode("utf-8").rstrip("\x00"), "%Y/%m/%d-%H:%M:%S")
        data = data[20:]

        # Then 8 bytes for the center spot follow
        spotCenter = ThermoSpot.from_bytes(data[:8])
        data = data[8:]

        # Then 8 bytes for max spot follow
        spotMax = ThermoSpot.from_bytes(data[:8])
        data = data[8:]

        # Then 8 bytes for min spot follow
        spotMin = ThermoSpot.from_bytes(data[:8])
        data = data[8:]

        # then 4 bytes for the emissivity follow (as uint32)
        emissivity = struct.unpack("<I", data[:4])[0] / 100
        data = data[4:]

        # Then 4 bytes for the selected palette follow
        selectedPalette = ThermoPalette(struct.unpack("<I", data[:4])[0])
        data = data[4:]

        # Then 4 bytes for the unit follow
        unit = ThermoUnit(struct.unpack("<I", data[:4])[0])
        data = data[4:]

        # Then 4 bytes for the mix factor follow
        mixFactor = struct.unpack("<I", data[:4])[0]
        data = data[4:]

        # If we have the newer metadata format, we have 8 bytes for the image margin
        if size == 112:
            # Then 8 bytes for the image margin follow (2 for each side)
            imageMargin = struct.unpack("<HHHH", data[:8])
            data = data[8:]
        else:
            imageMargin = (0, 0, 0, 0)

        return cls(model=model, firmware=firmware, capture_time=captureTime, spot_center=spotCenter, spot_min=spotMin, spot_max=spotMax, emissivity=emissivity, selected_palette=selectedPalette, mix_factor=mixFactor, image_margins=imageMargin, selected_unit=unit, byte_size=size)


"""
This class describes the full data contained in the special JPEG contained by the HTI camera.
This is the mixed picture directly visible, the visible picture, thermal data and various metadata.
"""
@dataclass()
class ThermoImage:

    # The mixed image, shown on the camera display (visible + thermal) (saves as JPEG)
    mixed: Image.Image

    # The visible image, as seen by the camera (saved as JPEG)
    visible: Image.Image

    # The thermal resolution of the camera (width, height)
    thermal_resolution: tuple[int, int]

    # The temperature data [x, y] (0 upper left) for each pixel in the image (two-dimensional array, w x h), in deci Celsius (°C * 10)
    temperature: ndarray[int, int]

    # A gray scale representation [x, y] (0 upper left) of the temperature data (two-dimensional array, w x h), between 0 and 256
    gray_scale: ndarray[int, int]

    # The metadata / info of the image,
    info: ThermoMetadata

    """
    Returns the temperature data in celsius
    """
    @property
    def temperature_celsius(self):
        return self.temperature / 10

    """
    Returns the temperature data in kelvin
    """
    def temperature_kelvin(self):
        return self.temperature_celsius + 273.15

    """
    Returns the resolution of the visible image
    """
    @property
    def visible_resolution(self):
        return self.visible.size

    @classmethod
    def from_bytes(cls, data: bytes) -> ThermoImage:
        # Mixed image
        # The first available image is the mixed image
        mixed = Image.open(io.BytesIO(data))

        # Search for the JPEG end marker and new JPEG start marker
        # This is the point where the mixed image ends and the visible image starts
        mixedEnd = data.find(b"\xFF\xD9\xFF\xD8")
        # Move the data pointer to the end of the mixed image, so we can read the visible image next
        data = data[mixedEnd + 2:]

        # Create a new image object from a bytes object
        visible = Image.open(io.BytesIO(data))

        # Move the data pointer to the end of the visible image, so we can read the thermal data next
        visibleEnd = data.find(b"\xFF\xD9")  # Find the JPEG end marker
        data = data[visibleEnd + 2:]

        # The next 4 bytes are the width and height of the thermal image
        (w, h) = struct.unpack("<HH", data[:4])
        data = data[4:]

        # Now 2 * w * h bytes follow, representing the temperature data
        # The temperature data is stored in 2 bytes per pixel
        temperature = ndarray((w, h), dtype=int)
        for y in range(h):
            for x in range(w):
                temperature[x, y] = struct.unpack("<h", data[:2])[0]
                data = data[2:]

        # Now again width and height follow for the gray scale picture, they should be the same as the thermal image
        (w2, h2) = struct.unpack("<HH", data[:4])
        data = data[4:]
        if w2 != w or h2 != h:
            raise ValueError("Gray scale image has different dimensions than thermal image")

        # Now w * h bytes follow, representing the gray scale data (1 byte per pixel)
        grayScale = ndarray((w, h), dtype=int)
        for y in range(h):
            for x in range(w):
                grayScale[x, y] = struct.unpack("<B", data[:1])[0]
                data = data[1:]

        # Now the metadata follows
        info = ThermoMetadata.from_bytes(data)

        return cls(mixed=mixed, visible=visible, thermal_resolution=(w, h), temperature=temperature, gray_scale=grayScale, info=info)

    @classmethod
    def from_path(cls, path: str) -> ThermoImage:
        # Open file
        with open(path, mode="rb") as f:
            data = f.read()
            return cls.from_bytes(data)
