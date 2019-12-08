import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime


image = Image.open("/Users/<username>/Desktop/IMG_2368.jpg")
info = image._getexif()

for tag, value in info.items():
    decoded = TAGS.get(tag, tag)
    print(decoded)