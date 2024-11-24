from thermo import structures
from thermo.structures import ThermoImage

# Load the image

picture = ThermoImage.from_path("data/p1.jpg")

# Display the image
picture.mixed.show()
picture.visible.show()