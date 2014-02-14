with open("images/pixel.gif", "rb") as pixel_file:
    PIXEL = bytearray(pixel_file.read())

with open("images/favicon.ico", "rb") as favicon_file:
    FAVICON = bytearray(favicon_file.read())
