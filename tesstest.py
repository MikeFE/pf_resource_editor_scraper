# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import numpy

def imshow_scaled(img, title=''):
	target_size = (960, 540)
	imgs = img#cv2.resize(img, target_size)
	cv2.imshow(title, imgs)

# Converts pixels in color range to specified destination color
def range_to_color(img, lo, hi, output_color):
	# BGR not RGB
	lo = numpy.array(lo)
	hi = numpy.array(hi)

	# Mask image to only select range
	mask = cv2.inRange(img, lo, hi)

	# Change image to red where we found range
	img[mask>0] = output_color
	return img

def translate_colors(img):
	ignore_color = [0,0,255]
	text_color = [0,0,255]

	# Convert white text to text color
	#img = range_to_color(img, ignore_color, ignore_color, text_color)
	# Black borders and stuff to white
	img = range_to_color(img, [0, 0, 0], [40, 40, 40], ignore_color)

	return img

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
	help="type of preprocessing to be done")
args = vars(ap.parse_args())

orig = cv2.imread(args['image'])
image = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)  # convert to grayscale

filename = "images/tmp.tiff"

scale_percent = 250 # percent of original size,
					# aim for ~30 pixels high capital letters for best results

width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)

#image = range_to_color(image, [98, 98, 98], [98, 98, 98], [0, 0, 0])
image = cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

# invert image colors, tesseract likes dark text on white bg
image = cv2.bitwise_not(image)
_, image = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)
cv2.imwrite(filename, image)

i = Image.open(filename)
print(repr(i))
text = pytesseract.image_to_string(i, config=' --psm 6')
#os.remove(filename)
text = os.linesep.join([s for s in text.splitlines() if s])
print(text)

imshow_scaled(orig, "Input")
imshow_scaled(image, "Output")
cv2.waitKey(0)