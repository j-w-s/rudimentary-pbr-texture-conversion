# imports
import os
import json
import numpy as  np
import tkinter as tk
from PIL import Image, ImageOps
from tkinter import filedialog
from noise import snoise2

# lists of string representations of in-game objects/their textures
LIGHT_SOURCES = ["beacon", "conduit", "end", "fire", "pickle", "glow", 
            "jack", "lantern", "lava", "campfire", "lamp", "anchor", "torch", 
            "rod", "furnace", "smoker", "portal", "crying", "candle", "lichen", 
            "sculk", "magma", "brewing", "brown_mushroom", "dragon", "enchant"]
RAW_ORES = ["raw"]
ORES = ["_ore"]
WATER = ["water"]
ORE_DERIV = ["iron", "chain", "gold", "diamond", "netherite", 
            "emerald", "amethyst", "lapis", "obsidian", "copper"]
NATURAL_ENTITIES = ["seagrass", "grass", "dirt", "podzol", "mycelium", 
            "gravel", "sand", "clay", "acacia", "birch", "dark_oak", "jungle", 
            "mangrove", "oak", "spruce", "stone", "andesite", "diorite", "granite", 
            "deep", "slate", "deepslate", "netherrack", "brick", "snow", "infested", 
            "basalt", "nylium", "mud", "soul", "rooted", "sapling", "allium", "azure", 
            "orchid", "cornflower", "dandelion", "lilac", "valley", "tulip", "oxeye", 
            "peony", "poppy", "rose", "sunflower", "hay", "melon", "moss", "roots", 
            "blossom", "dripleaf", "bush", "fern", "lily", "vine", "wool", "carpet",
            "terracotta", "banner", "honeycomb"]
MISC = ["glass", "slime", "honey", "ice"]

# conversion function
def convert_to_pbr(input_folder):

    # loop through every .png file in the texture folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
        
            # determine metalness, roughness, and emissiveness based on item type
            metalness = 0.50
            roughness = 0.45
            emissiveness = 0.1

            # check-based updating of these values
            if any(item in filename for item in LIGHT_SOURCES):
                emissiveness = 0.5
            elif any(item in filename for item in RAW_ORES):
                metalness = 0.20
                roughness = 0.85
                emissiveness = 0.05
            elif any(item in filename for item in ORES):
                metalness = 0.85
                roughness = 0.85
                emissiveness = 0.2
            elif any(item in filename for item in WATER):
                roughness = 0.15
                emissiveness = 0.35
            elif any(item in filename for item in ORE_DERIV):
                metalness = 1.0
                roughness = 0.85
            elif any(item in filename for item in NATURAL_ENTITIES):
                metalness = 0.20
                roughness = 0.85
                emissiveness = 0.05
            elif any(item in filename for item in MISC):
                metalness = 1.0
                roughness = 0.25
           
            # open the .png file for use with the PIL library
            image = Image.open(os.path.join(input_folder, filename))
            
            # create the metalness, emissive, and roughness maps by copying the red, green, and blue channels
            # of the image and multiplying them with the corresponding scalar values
            metalness_map = Image.new("RGB", image.size, (0, 0, 0))
            metalness_pixels = [(int(pixel[0]*metalness), 0, 0) for pixel in image.getdata()]
            metalness_map.putdata(metalness_pixels)
            # print("Sample pixels from metalness_map:", metalness_pixels[:10])

            emissive_map = Image.new("RGB", image.size, (0, 0, 0))
            emissive_pixels = [(0, int(pixel[1]*emissiveness), 0) for pixel in image.getdata()]
            emissive_map.putdata(emissive_pixels)
            # print("Sample pixels from emissive_map:", emissive_pixels[:10])

            roughness_map = Image.new("RGB", image.size, (0, 0, 0))
            roughness_pixels = [(0, 0, int(pixel[2]*roughness)) for pixel in image.getdata()]
            roughness_map.putdata(roughness_pixels)
            # print("Sample pixels from roughness_map:", roughness_pixels[:10])

            # combine the metalness, emissive, and roughness maps into a single image
            # with the _mer (m = metalness, e = emissive, r = roughness) suffix
            mer = Image.merge("RGB", (metalness_map.getchannel("R"), emissive_map.getchannel("G"), roughness_map.getchannel("B")))
            
            
            if any(item in filename for item in WATER):
                # create the normal map for water textures via perlin noise generation
                # define the size of the texture and the frequency of the noise
                size = 32 # assumes 32x32 textures as input
                freq = 16 # up to 16 * 9/(logb(2, texture size)) possible
                
                # generate 2d perlin noise function
                data = np.zeros((size, size)) # texture size x texture size zero matrix
                for y in range(size):
                    for x in range(size):
                        data[y][x] = snoise2((x / freq), (y / freq), octaves = 3, persistence = 0.5)
                
                # normalize data to range [0, 1]
                data = (data - np.min(data)) / (np.max(data) - np.min(data))

                # convert normalized data into a normal map
                normal_data = np.zeros((size, size, 3))
                for y in range(size):
                    for x in range(size):
                        # calculate the change in height between adjacent pixels in the x and y directions
                        dx = (data[y][(x+1)%size] - data[y][x-1]) / 2.0
                        dy = (data[(y+1)%size][x] - data[y-1][x]) / 2.0
                        # 2d texture; set z height change to a constant
                        dz = 1.0 / freq
                        # update normal vector
                        normal_data[y][x] = [dx, dy, dz]
                
                # re-adjust values such that they fall into range [0, 255] (RGB)
                normal_data = (normal_data + 1) / 2.0 * 255.0
                # convert normal vector into normal map
                normal = Image.fromarray(np.uint8(normal_data), mode = "RGB")
                
            else:
                # create the normal map for non-water textures by generating a
                # grayscale image from its blue channel
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
                json.dump(json_data, f, indent = 4)

# create tkinter root object
root = tk.Tk()
# prompt user to select input directory with texture to be converted
root.withdraw()
# define the folder where textures are located
input_folder = filedialog.askdirectory(title = "Select input folder")
# call function with input_folder as parameter
convert_to_pbr(input_folder)
# display status message post-conversion
print("Successful conversion.")
