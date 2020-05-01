#This Python script was created by tjmurphy@mit.edu in order to convert a 128x128 image
#into a list of blocks to place in a Minecraft world to show up on a map, to create
#things like wall posters. Provide it as input the image you want, and a file which
#outlines the available colors for use in a Minecraft map. I pulled this file from
#the Minecraft wiki, where a table with colors can be found for reference.

#Created 4/30/2020

input_filename = 'rsz_wednesdayfrog.jpg'
#There are three possible outputs:
#1. Render an image of what your map will look like after converting to blocks, showing and saving it
#2. Output a list of blocks to build by hand
#3. Output a Minecraft Schematic file of your image for easy pasting
show_image = False
write_list = False
make_schematic = True

palette_file = 'colortable.txt'
#Class which represents a given color, for keeping track of palette
class Mapcolor:
    def __init__(self,name,r,g,b):
        self.name = name
        self.r = r
        self.g = g
        self.b = b
    def __repr__(self):
        return ",".join([self.name,str(self.r),str(self.g),str(self.b)])
#Given that we have a particular pixel's L, A, B values (by the CIELAB color standard),
#And and image which is just a single vertical column of pixels representing the color
#options available, this will tell you the index of the pixel of the palette which most
#closely matches the given pixel.
def get_closest_from_palette(l_a_b, palette):
    #l_a_b is a list of values, palette is a vertical column-image.
    palette_pixels = palette.load()
    lowest_dist = 99999
    closest_match = -1
    for y in range(palette.size[1]):
        palette_color = palette_pixels[0,y]
        #This is the equation for how close colors are in the LAB color space.
        #Technically you're supposed to sqrt this for a proper pythagorean comparison
        #but since we're just comparing magnitudes it doesn't matter.
        distance = sum((l_a_b[i] - palette_color[i])**2 for i in range(3))
        if distance < lowest_dist:
            lowest_dist = distance
            closest_match = y
    return closest_match

#Take a list of colors (the palette) and, given a color, return the name of that color. Needs perfect match!
def get_palette_id(palette, color):
    for i in range(len(palette)):
        if palette[i].r == color[0] and palette[i].g == color[1] and palette[i].b == color[2]:
            return i
    return "ERROR"

#-----------------------End of class and function definitions, main code below!--------------------

#Open the text file for the color table and use that to get a list of available RGB's
colors = []
with open(palette_file,'r') as f:
    lines = f.readlines()
    #Is this the best way to do this? Once I hit the line with 'id = ' in it I also need
    #info from the next line so I use enumerate and then idx+1 to grab the secondary line.
    for idx,line in enumerate(lines):
        if "id = " in line:
            colorname = line.split()[-1]
            colorline = lines[idx+1].replace(",", " ").split()
            r,g,b = [int(i) for i in colorline[-3:]]
            colors += [Mapcolor(colorname, r, g, b)]

from PIL import Image, ImageCms
#Build a transformation from RGB to CIELAB (which is good for color closeness checking)
#Not gonna use this transformation just yet, but setting it up.
srgb_p = ImageCms.createProfile("sRGB")
lab_p = ImageCms.createProfile("LAB")
rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")

#Take the colors we've gathered and make an image out of them.
color_palette = Image.new("RGB",(1,len(colors)))
for y in range(len(colors)):
    color_palette.putpixel((0,y),(colors[y].r,colors[y].g,colors[y].b))
#convert that image to LAB
lab_palette = ImageCms.applyTransform(color_palette,rgb2lab)
                           
im = Image.open(input_filename).convert('RGB')

Lab = ImageCms.applyTransform(im,rgb2lab)
lab_pix = Lab.load()
width,height = im.size
print("Image size is: " + str(im.size))
print("If it's not 128x128, all bets are off! This script is made for 128x128.")

#Output_image stores a pixel representation of your palettized image.
output_image = Image.new("RGB",(width,height))
for y in range(height):
    for x in range(width):
        #palette color that most closely matches this pixel
        p_c = get_closest_from_palette(lab_pix[x,y],lab_palette)
        #Now that we know the index of the palette which matches, pull the rgb values back
        #out of our original "colors" list from the very beginning.
        output_image.putpixel((x,y), (colors[p_c].r,colors[p_c].g,colors[p_c].b))
if(show_image):
    output_image.show()
    output_image.save("Out_image.png")
if(write_list):
    #We've converted our image into our limited color palette. Now we need to take that palette
    #and identify the block-types which will yield those colors in-game.
    instruction_string = ""
    current_block = ""

    for row in range(height):
        instruction_string += ("\nROW " + str(row) + ": ")
        #At start of row, set the first block.
        current_block = colors[get_palette_id(colors,output_image.getpixel((0,row)))].name
        block_count = 0
        for pixel in range(width):
            best_block = colors[get_palette_id(colors,output_image.getpixel((pixel,row)))].name
            #Keep track of block_count, which is the length of the run we've had with the current block.
            #Also, always do the "end of block run" at the end of each row.
            if (best_block == current_block):
                #We're still on the same block run.
                block_count +=1
            else:
                #We have a new block. Print out how many of the previous block we had.
                instruction_string += (str(block_count) + " " + current_block + " || ")
                current_block = best_block
                block_count = 1
            #At the end of the row, print off the current block run that is truncated by the edge.
            if(pixel == width -1):
                instruction_string += (str(block_count) + " " + current_block)
                
    with open("out_list.txt","w") as f:
        f.write(instruction_string)
if(make_schematic):
    #Parse the image into a Minecraft Schematic file for easy pasting into world
    from nbtschematic import SchematicFile
    sf = SchematicFile(shape=(1, width, height))
    assert sf.blocks.shape == (1, width, height)
    #This dictionary takes a name for a block in the palette, and converts to an in-game block which
    #has that color on the map. Schematics use minecraft block ID's so these are the numbers.
    #First number is block ID, second is data value for things like color.
    name_to_id = {"GRASS":(2,0),"SAND":(5,2),"WOOL":(99,15),"FIRE":(152,0),"ICE":(174,0),"METAL":(42,0),
                  "PLANT":(18,0),"SNOW":(80,0),"CLAY":(82,0),"DIRT":(3,1),"STONE":(1,0),"WATER":(9,0),
                  "WOOD":(5,0),"GOLD":(41,0),"DIAMOND":(57,0),"LAPIS":(22,0),"EMERALD":(133,0),"PODZOL":(3,2),"NETHER":(87,0),
                  "COLOR_WHITE":(35,0),"COLOR_ORANGE":(35,1),"COLOR_MAGENTA":(35,2),"COLOR_LIGHT_BLUE":(35,3),
                  "COLOR_YELLOW":(35,4),"COLOR_LIGHT_GREEN":(35,5),"COLOR_PINK":(35,6),"COLOR_GRAY":(35,7),
                  "COLOR_LIGHT_GRAY":(35,8),"COLOR_CYAN":(35,9),"COLOR_PURPLE":(35,10),"COLOR_BLUE":(35,11),
                  "COLOR_BROWN":(35,12),"COLOR_GREEN":(35,13),"COLOR_RED":(35,14),"COLOR_BLACK":(35,15),
                  "TERRACOTTA_WHITE":(159,0),"TERRACOTTA_ORANGE":(159,1),"TERRACOTTA_MAGENTA":(159,2),"TERRACOTTA_LIGHT_BLUE":(159,3),
                  "TERRACOTTA_YELLOW":(159,4),"TERRACOTTA_LIGHT_GREEN":(159,5),"TERRACOTTA_PINK":(159,6),"TERRACOTTA_GRAY":(159,7),
                  "TERRACOTTA_LIGHT_GRAY":(159,8),"TERRACOTTA_CYAN":(159,9),"TERRACOTTA_PURPLE":(159,10),"TERRACOTTA_BLUE":(159,11),
                  "TERRACOTTA_BROWN":(159,12),"TERRACOTTA_GREEN":(159,13),"TERRACOTTA_RED":(159,14),"TERRACOTTA_BLACK":(159,15),
                  }
    for y in range(height):
        for x in range(width):
            block_name = colors[get_palette_id(colors,output_image.getpixel((x,y)))].name
            sf.blocks[0,y,x] = name_to_id[block_name][0]
            sf.data[0,y,x] = name_to_id[block_name][1]
    sf.save('output.schematic')
print("Map maker complete!")
