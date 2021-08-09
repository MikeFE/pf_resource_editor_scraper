""" Scrape Age of Wonders: Planetfall data from the Resource Editor """

import time
import cv2
import numpy
import os

import pyautogui as ui
import pytesseract
from pywinauto.application import Application
from PIL import Image

from uiconfig import *

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def is_item_modded(region):
    if wait_on_image_located(image='images/modded.tiff', region=region):
        return True
    return False

def get_resource_list_item(row):

    print("Parsing resource #{}".format(row))

    r = resource_list.get_item_region(row)
    if not is_item_modded(r):
        make_resource_modded(row)
        if not is_item_modded(r):
            print('Info: cannot mod item #{} (blank resource?)'.format(row))
            return


    take_screenshots()

# Takes the requisite screenshots
def take_screenshots():
    get_resource_value_pages()
    cv2.waitKey()

# Get screenshots of the entire table of resource values. Each screenshot in the list returned corresponds to
# a "page down" action on the scrollbar here.
def get_resource_value_pages():
    n = 0
    while True:
        values = get_cv2_screenshot(resource_values.get_region())
        get_values_ocr(values)

        if not wait_on_image_located(image='images/fully_scrolled.tiff', region=resource_values_scrollbar_bottom_region, timeout=0.5):
            print('Finished scrolling page, returning')
            return

        print('Scrolling page {}'.format(n))
        ui.rightClick(*resource_values_scrollbar_coord)
        ui.moveRel(*scrollbar_page_down_rel_coord)
        ui.click()

        n += 1
        if n > 7:
            raise Exception("Couldn't find the end of the scrollbar")

# Take a screenshot within a region (default=fullscreen), return a usable cv2 image of it
def get_cv2_screenshot(region=None):
    pil_image = ui.screenshot(region=region)
    return cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)

# Do image processing to improve OCR accuracy. Convert to grayscale, scale image to
# get capital letters to ~30 pixels, invert the image (for dark text on bright bg), binarize the image
def process_values_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert to grayscale

    scale_percent = 220 # percent of original size,
                        # aim for ~30 pixels high capital letters for best results

    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)

    #image = range_to_color(image, [98, 98, 98], [98, 98, 98], [0, 0, 0])
    image = cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

    # invert image colors, tesseract likes dark text on white bg
    image = cv2.bitwise_not(image)
    _, image = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)
    return image

# Process cv2 image and pass it off to tesseract for OCR
def get_values_ocr(image):
    # How many pixels in the row until we hit the vertical line separating key/val
    # TODO: We'll want to dynamically determine what this is because the column width of the
    # table auto-sizes based on cell content when you click a new resource.
    key_value_divider_pos = 200
    _, w, _ = image.shape

    for n in range(0, items_per_page):
        top = n * resource_values.item_height
        row_img = image[top:top+resource_values.item_height, 0:w]
        row_name_img = row_img[:, 0:key_value_divider_pos]
        row_value_img = row_img[:, key_value_divider_pos:]

        row_name = pytesseract.image_to_string(Image.fromarray(process_values_image(row_name_img)), config=' --psm 7')
        row_value = pytesseract.image_to_string(Image.fromarray(process_values_image(row_value_img)), config=' --psm 7')

        row_name = os.linesep.join([s for s in row_name.splitlines() if s])
        row_value = os.linesep.join([s for s in row_value.splitlines() if s])

        if row_name:
            print('{}={}'.format(row_name, row_value))

        cv2.imwrite('images/debug/delme{}_name.tiff'.format(n), process_values_image(row_name_img))
        cv2.imwrite('images/debug/delme{}_val.tiff'.format(n), process_values_image(row_value_img))
        cv2.imwrite('images/debug/delme{}_row.tiff'.format(n), process_values_image(row_img))

        get_values_ocr.gn += 1

    processed_img = process_values_image(image)
    cv2.imwrite('images/debug/processed_img.tiff', processed_img)
get_values_ocr.gn = 0

# Right click resource on the list, click "create mod" in popup menu to enable properties table
# on the right hand panel. The property table text is grayed out / the scrollbar disabled otherwise.
def make_resource_modded(row):
    x, y = resource_list.get_item(row)
    print('Making resource {} modded ({}, {})'.format(row, x, y))

    ui.click(x, y)
    ui.rightClick()
    ui.moveRel(3, 3)
    ui.click()

# Wait a specified timeout amount of seconds and return if image specified is ever seen within
# screenshot (only in region if specified)
def wait_on_image_located(image, region=None, timeout=3):
    start_time = time.time()
    found = None

    while not found:
        if time.time() - start_time >= timeout:
            break
        try:
            found = ui.locateOnScreen(image, region=region)
        except ui.ImageNotFoundException as e:
            found = None
    return found


# Make game data name/values panel wider for better viewing
def resize_panels():
    ui.moveTo(*panel_resizer_rhs_coord)
    ui.dragTo(ui.size().width, 750, duration=0.2)

app = Application().connect(best_match='ResourceEd')
window = app.top_window()
window.minimize()
window.maximize()
window.set_focus()

#resize_panels()

get_resource_list_item(6)
cv2.imwrite('images/debug/values.tiff', get_cv2_screenshot(resource_values.get_region()))
print('**** Done')