import os

IMAGE_PATH = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(IMAGE_PATH, "pixel.gif"), "rb") as pixel_file:
    PIXEL = bytearray(pixel_file.read())

with open(os.path.join(IMAGE_PATH, "favicon.ico"), "rb") as favicon_file:
    FAVICON = bytearray(favicon_file.read())
