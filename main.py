from thermo import structures
from thermo.structures import ThermoImage
import matplotlib.pyplot as plt

# Load the image

picture = ThermoImage.from_path("data/p1.jpg")

print(picture.thermalResolution)

# Plot the temperature data
plt.imshow(picture.temperature.transpose() / 10)
plt.colorbar()
plt.show()

# Plot the gray scale data
plt.imshow(picture.grayScale.transpose())
plt.colorbar()
plt.show()

# Display the image
#picture.mixed.show()
#picture.visible.show()