# imports
import os
import json
import tkinter as tk
from PIL import Image
from tkinter import filedialog

# conversion function
def convert_to_pbr(input_folder):
    # loop through every .png file in the texture folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            # open the .png file for use with the PIL library
            image = Image.open(os.path.join(input_folder, filename))
            
            # create the metalness, emissive, and roughness maps by copying the red, green, and blue channels
            # of the image
            metalness = Image.new("RGB", image.size, (0, 0, 0))
            metalness.putdata(list(image.getdata(0)))
            
            emissive = Image.new("RGB", image.size, (0, 0, 0))
            emissive.putdata(list(image.getdata(1)))
            
            roughness = Image.new("RGB", image.size, (0, 0, 0))
            roughness.putdata(list(image.getdata(2)))
            
            # combine the metalness, emissive, and roughness maps into a single image
            # with the _mer (m = metalness, e = emissive, r = roughness) suffix
            mer = Image.merge("RGB", (metalness.getchannel("R"), emissive.getchannel("G"), roughness.getchannel("B")))
            
            # create the normal map by generating a grayscale image from the blue channel
            # of the image
            if image.mode == "RGBA":
                normal = Image.new("RGB", image.size, (128, 128, 255))
                try:
                    normal.putdata(list(image.getdata(3)))
                except IndexError:
                    normal.putdata(list(image.getdata(2)))
            else:
                normal = Image.new("RGB", image.size, (128, 128, 255))
                normal.putdata(list(image.getdata(2)))
            
            # save the metalness, emissive, and roughness maps as .png files
            mer.save(os.path.join(input_folder, filename[:-4] + "_mer.png"))
            
            # save the normal map as both a .png and .tga file
            normal.save(os.path.join(input_folder, filename[:-4] + "_normal.png"))
            normal.save(os.path.join(input_folder, filename[:-4] + "_normal.tga"))
            
            # create a .json file with formatting -- use dictionary to represent contents
            json_data = {
                "format_version": "1.16.100",
                "minecraft:texture_set": {
                    "color": filename[:-4],
                    "metalness_emissive_roughness": filename[:-4] + "_mer.png",
                    "heightmap": filename[:-4] + "_normal.png"
                }
            }

            # write the .json data to a file
            json_filename = os.path.join(input_folder, filename[:-4] + ".texture_set.json")
            with open(json_filename, "w") as f:
                json.dump(json_data, f, indent=4)

# create tkinter root object
root = tk.Tk()
# prompt user to select input directory with texture to be converted
root.withdraw()
# define the folder where textures are located
input_folder = filedialog.askdirectory(title="Select input folder")
# call function with input_folder as parameter
convert_to_pbr(input_folder)
# display status message post-conversion
print("Successful conversion.")