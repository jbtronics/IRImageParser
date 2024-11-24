# IRImageParser

This library (and tool) allows to parse the data contained in the JPG files created by the thermalcameras of HTI (HTI-Xintai)
They are a OEM whose cameras get sold often under different branch. The library is written in Python and can be used to process the data in the JPG file for
further analysis. Some little demo program is included, to show what data can be extracted.

## Supported cameras
 
The library has been tested with the following cameras:
* HT-04D (also sold as Tooltop ET692B)
* HT-19

Probably it will work with other thermal cameras from HTI as well. If your camera pictures can be opened by the `IRImageTools`
software, its possible that the library will work with your camera as well.

## Data format
The cameras store a JPG file which contains the screenshot shown on the camera in any normal image viewer.

After the image data, the JPG files contains another JPEG image, which contains the visible picture without any overlays.
Afterwards an raw byte array containing the temperature data and a grayscale representation of the temperature between
min and max temperature.
In the end of the file various metadata is stored like model number, firmware version, min, max and center temperature,
emissivity, the used color palette, mixing factor and the temperature unit.

All of this data can be extracted by the library and used for further analysis, to exceed the capabilities of the normal
analysis software.

The file format was reversed engineered from the firmware of a HT-04D thermal camera using ghidra.

## Installation

The library itself requires `pillow` and `numpy` to be installed. The main program requires `matplotlib` to be installed as well.
You can install the library via pip:

```bash
pip install -r requirements.txt
```

## Usage

The library can be used to extract the data from the JPG file. The data is stored in the `ThermoImage` object in the thermo
package. The `ThermoImage` object contains the raw data, the temperature data and the image data.

The `main.py` script in the root folder allows to open a JPG file and display the data in a very simple way. The script
can be used as follows:

```bash
python main.py <path_to_jpg_file>
```

It will show metadata, the mixed and visible image and temperature plots.

A demo picture is included in the `demo` folder.

You will get some output like this (and the pictures shown):

```
====== Picture info =======
Camera: HT-04D (Firmware 2.5.1)
Thermal resolution: 120x160
Visible resolution: 240x320
Capture time: 2024-11-21 01:06:39

Center: 25.4 °C (x=120, y=160)
Min temperature: 13.8 °C (x=234, y=236)
Max temperature: 26.1 °C (x=118, y=198)

Palette: SPECTRA
Emissivity: 0.95
Unit: CELSIUS
Mixing factor: 0
Image margins: (0, 0, 0, 0)
===========================
```