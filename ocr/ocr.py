try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import re

import sys

def getBarcode(image):
    res = pytesseract.image_to_string(Image.open(image))
    r1 = re.findall(r"\w\w\w\w\w-\w\w\w\w\w-\w\w\w\w\w-\w\w\w\w\w-\w\w\w\w\w",res)
    if len(r1) != 1:
        raise ValueError("Could not find barcode from " + image)
    return r1[0]

if len(sys.argv[1:]) == 0:
    raise ValueError("Please supply the desired image as a command line argument")

for pic in sys.argv[1:]:
    print(getBarcode(pic))
