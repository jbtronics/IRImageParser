import os
import sys
from tkinter import Tk, filedialog, Label, Entry, Button
import matplotlib.pyplot as plt
import numpy as np
import math
from thermo.structures import ThermoImage, ThermoMetadata

#usage python alignTemp.py [your/directory/path] [yourCMAP] 
#yourCMAP from https://matplotlib.org/stable/gallery/color/colormap_reference.html


#open the images in the path and extract the temperature data section
def load_images(path):
    results = []
    thermal_resolution = None
    for filename in os.listdir(path):
        if filename.endswith(".jpg") and not filename.startswith("_"):
            img_path = os.path.join(path, filename)
            img = ThermoImage.from_path(img_path)
            
            if thermal_resolution is None:
                thermal_resolution = img.thermal_resolution
            elif thermal_resolution != img.thermal_resolution:
                print(f"Different resolutions found: {thermal_resolution} and {img.thermal_resolution}")
                sys.exit(1)
            
            results.append((filename, img.temperature_celsius.transpose()))
    return results

#plot the image with the current settings
def plot_images(result, cmap, vmin=None, vmax=None):
    num_images = len(result)
    grid_sizeX = math.ceil(math.sqrt(num_images))
    grid_sizeY = math.ceil(num_images/grid_sizeX)
    
    # Calculate aspect ratio based on the first image
    #aspect_ratio = result[0][1].shape[1] / result[0][1].shape[0]
    fig_width = 10
    fig_height = 10 #fig_width / aspect_ratio * grid_sizeY
    
    fig, axes = plt.subplots(grid_sizeX, grid_sizeY, figsize=(fig_width, fig_height))
    
    for i in range(grid_sizeX):
        for j in range(grid_sizeY):
            index = i * grid_sizeY + j
            if index < num_images:
                im = axes[i, j].imshow(result[index][1], cmap=cmap, interpolation='nearest', vmin=vmin, vmax=vmax)
                axes[i, j].set_title(os.path.splitext(result[index][0])[0])
                axes[i, j].axis('off')
            else:
                axes[i, j].axis('off')
    
    plt.suptitle(f"Temp from {vmin} to {vmax}")
    plt.colorbar(im, ax=axes, orientation='vertical', fraction=.1)
    plt.show()

#export the temperature data as images witht the current temperature range settings and cmap
def export_images(out_path, result, cmap, vmin=None, vmax=None):
    plt.close()
    for filename, data in result:
        print(filename)
        plt.imshow(data, cmap=cmap, interpolation='nearest', vmin=vmin, vmax=vmax)
        plt.axis('off')
        export_filename = f"_T[{vmin}]-[{vmax}]_{os.path.splitext(filename)[0]}.jpg"
        full_path = os.path.join(out_path, export_filename)
        plt.savefig(full_path, bbox_inches='tight', pad_inches=0)
        plt.close()

def main():
    if len(sys.argv) < 1 or len(sys.argv) > 3:
        print("Usage: python script.py <path> [cmap]")
        sys.exit(1)
    elif len(sys.argv) == 1:
        path = filedialog.askdirectory(initialdir=".", title="Select IR Image Directory")
    else:
        path = sys.argv[1]
    
    if not os.path.isdir(path):
        print("Usage: python script.py <path> [cmap]")
        print("Not a directory: {path}")
        sys.exit(1)
        
    
    cmap = sys.argv[2] if len(sys.argv) == 3 else 'hot'
    
    result = load_images(path)
    
    # Calculate min and max temperature
    all_temperatures = np.concatenate([np.array(img[1]) for img in result])
    vmin = all_temperatures.min()
    vmax = all_temperatures.max()
    
    # GUI to control image range and color
    def show_plot():
        new_vmin = float(entry_vmin.get())
        new_vmax = float(entry_vmax.get())
        new_cmap = str(entry_CMAP.get())
        plot_images(result, cmap=new_cmap, vmin=new_vmin, vmax=new_vmax)
    
    def export_plot():
        new_vmin = float(entry_vmin.get())
        new_vmax = float(entry_vmax.get())
        new_cmap = str(entry_CMAP.get())
        export_images(path, result, cmap=new_cmap, vmin=new_vmin, vmax=new_vmax)
    
    gui_root = Tk()
    gui_root.title("Temp Settings")
    
    Label(gui_root, text="Min Temperature:").grid(row=0, column=0)
    entry_vmin = Entry(gui_root)
    entry_vmin.grid(row=0, column=1)
    entry_vmin.insert(0, str(vmin))
    
    Label(gui_root, text="Max Temperature:").grid(row=1, column=0)
    entry_vmax = Entry(gui_root)
    entry_vmax.grid(row=1, column=1)
    entry_vmax.insert(0, str(vmax))
    
    Label(gui_root, text="CMAP:").grid(row=2, column=0)
    entry_CMAP = Entry(gui_root)
    entry_CMAP.grid(row=2, column=1)
    entry_CMAP.insert(0, str(cmap))
    
    Button(gui_root, text="Show", command=show_plot).grid(row=3, columnspan=2)
    Button(gui_root, text="Export", command=export_plot).grid(row=4, columnspan=2)
    
    show_plot()
    gui_root.mainloop()

if __name__ == "__main__":
    main()