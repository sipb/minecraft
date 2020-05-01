#This Python script was created by tjmurphy@mit.edu in order to convert a 128x128 image
#into a list of blocks to place in a Minecraft world to show up on a map, to create
#things like wall posters. Provide it as input the image you want, and a file which
#outlines the available colors for use in a Minecraft map. I pulled this file from
#the Minecraft wiki, where a table with colors can be found for reference.

#Created 4/30/2020

input_filename = 'rsz_wednesdayfrog.jpg'
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
srgb_p = ImageCms.createProfile("sRGB")
lab_p = ImageCms.createProfile("LAB")
rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")

#Take the colors we've gathered and make an image out of them.
color_palette = Image.new("RGB",(1,len(colors)))
for y in range(len(colors)):
    color_palette.putpixel((0,y),(colors[y].r,colors[y].g,colors[y].b))
#convert that image to LAB
lab_palette = ImageCms.applyTransform(color_palette,rgb2lab)
                           
im = Image.open(input_filename)

Lab = ImageCms.applyTransform(im,rgb2lab)
lab_pix = Lab.load()
width,height = im.size
print(im.size)

#Output_image stores a pixel representation of your palettized image.
output_image = Image.new("RGB",(width,height))
for y in range(height):
    for x in range(width):
        #palette color that most closely matches this pixel
        p_c = get_closest_from_palette(lab_pix[x,y],lab_palette)
        #Now that we know the index of the palette which matches, pull the rgb values back
        #out of our original "colors" list from the very beginning.
        output_image.putpixel((x,y), (colors[p_c].r,colors[p_c].g,colors[p_c].b))
        
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
output_image.show()
output_image.save("Out_image.png")
with open("out_list.txt","w") as f:
    f.write(instruction_string)            
