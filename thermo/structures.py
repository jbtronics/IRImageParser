from __future__ import annotations

import io

from PIL import Image
from numpy import ndarray
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

"""
Represents a spot in an image, containing temperature data
"""
@dataclass
class ThermoSpot:

    # X position
    x: int

    # Y position
    y: int

    # The temperature value in decidegree celsius
    value: int

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

    # The camera model (e.g. "HT-04D") (called devType internally)
    model: str

    # The camera firmware version (called devVersion internally)
    firmware: str

    # The time the image was taken (called captureTime internally)
    captureTime: datetime

    # The spot representing the center spot
    spotCenter: ThermoSpot

    # The spot representing the minimum temperature spot
    spotMin: ThermoSpot

    # The spot representing the maximum temperature spot
    spotMax: ThermoSpot

    # The emissivity that was configured in the camera
    emissivity: int

    # The color palette that was chosen in the camera for the picture
    selectedPalette: ThermoPalette

    # The mix grade between the ir and vis picture in percentage
    mixFactor: int

    # Image margins of the visible picture [top, right, bottom, left] in pixels
    imageMargin: tuple[int, int, int, int]



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
    thermalResolution: tuple[int, int]

    # The temperature data for each pixel in the image (two-dimensional array, w x h), in decidegree Celsius (°C * 10) ?
    temperature: ndarray[int, int]

    # A gray scale representation of the temperature data (two-dimensional array, w x h), between 0 and 2^16 ?
    grayScale: ndarray[int, int]

    # The metadata / info of the image,
    info: ThermoMetadata

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

        return cls(mixed, visible, (0, 0), None, None, None)




    @classmethod
    def from_path(cls, path: str) -> ThermoImage:
        # Open file
        with open(path, mode="rb") as f:
            data = f.read()
            return cls.from_bytes(data)
