"""from PIL import ImageDraw, Image, ImageFont

font = ImageFont.truetype("arial.ttf")

img = Image.new("RGB",(1920,1080))
d = ImageDraw.Draw(img)
d.textsize(int(1920/16))
d.text((0,0),"2013",font=font)

img.show()"""

import sys

print(len(sys.argv))