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

The maximum and minimum points in the temperature arrays are different from the ones calculated by the camera. This
is because the camera (and IRImageTools) performs averaging over a 3x3 grid to get the temperature of the pixed.

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

### Convert JPG files to IRG files
This library includes a small script to convert the JPG files of the HTI cameras to the IRG format used by the Infiray,
Topdon and Vevor Thermal cameras. This allows you to analyze the data with the Infiray IR Discovery software or the [Topdon
TDView for TC005](https://www.topdon.com/pages/pro-down?fuzzy=TC005) software, which is better than the HTI IRImageTools.

You can pass  files or whole folders containing JPG files from the HTI camera to the script. The script will create a IRG
file alongside the JPG files. Both JPG and IRG files are required to be in the same folder, so the IR Discovery software
can open it.

```bash
# Convert a single JPG file to IRG
python to_irg.py file.jpg

# Convert all JPG files in the folder to IRG files
python to_irg.py folder_with_jpg_files/
```

This script does not touch the JPG file, so it remains usable with the HTI software. However, the IR Discovery software
might overwrite the JPG file with its own version, so you probably want to keep a backup of the original JPG files.

This script was only possible with the reverse engineering work done by [@jelle737](https://github.com/jelle737/Vevor-Thermal-Utilities/tree/main)
and [@jaseg](https://github.com/jaseg/infiray_irg). They wrote parser software for the IRG files, which allowed me to
write a file writer for it.

## License
This library is licensed under the MIT license. That means you can use this library for any purpose free of charge,
as long as you retain the license information in the source code.

See the LICENSE file for more information.