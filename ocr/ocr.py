from PIL import Image

Image.MAX_IMAGE_PIXELS = 9331200000

import pytesseract
import re

import sys

def getText(image):
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(image, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    #print('Texts:')

    res = ""
    for text in texts:
        res += " " + text.description
        #print('\n"{}"'.format(text.description))

        #vertices = (['({},{})'.format(vertex.x, vertex.y)
        #            for vertex in text.bounding_poly.vertices])

        #print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return res

def localText(image):
    return pytesseract.image_to_string(Image.open(image))

def fix(z):
    st = z#""
    #for a in z:
    #    for b in a:
    #        st += b
    return st.replace(" ", "")

def getBarcode(image):
    res = getText(image)
    #print(res)
    r1 = re.findall(r"[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] *\- *[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] *\- *[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] *\- *[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] *\- *[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?[A-Z0-9] ?",res)
    #print(r1)
    res = [ fix(z) for z in r1]
    #if len(r1) != 1:
    #    raise ValueError("Could not find barcode from " + image)
    return set(res) #[0]

if len(sys.argv[1:]) == 0:
    raise ValueError("Please supply the desired image as a command line argument")

import os
for pic in sys.argv[1:]:
    os.system("convert -density 600 -rotate 270 " + pic + " tmp.png")
    bcs = getBarcode("tmp.png")
    print(len(bcs), pic)
    for bc in bcs:
        print(bc)
