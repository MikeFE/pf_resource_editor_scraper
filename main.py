""" Scrape Age of Wonders: Planetfall data from the Resource Editor """

import time
import cv2
import numpy
import os

import pyautogui as ui
import pytesseract
from pywinauto.application import Application
from PIL import Image

from config import *

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def is_item_modded(region):
    if wait_on_image_located(image='images/modded.tiff', region=region):
        return True
    return False

def click_item(r, f=ui.click):
    """ Bit of a kludge, just click the item's top left corner +2 pixels inside """
    f(r[0] + 2, r[1] + 2)

def get_resource_name():
    """ Get current resource name """
    name_img = process_values_image(get_cv2_screenshot(resource_name.get_region()))
    return clean_ocr_text(pytesseract.image_to_string(Image.fromarray(name_img), config=' --psm 7'))

def clean_ocr_text(text):
    """ Clear extraneous newlines from OCR text reads """
    return os.linesep.join([s for s in text.splitlines() if s])

def get_resource_list_item(row):
    print("Parsing resource list row #{}".format(row))

    # Kludge: use down arrow to scroll the list if we reach the bottom
    """
    tried_keydown = False
    while True:
        try:
            r = resource_list.get_item_region(row)
            break
        except ValueError as e:
            if tried_keydown:
                return
            ui.press('down')
            tried_keydown = True
    """
    r = resource_list.get_item_region(row)
    click_item(r)

    if not is_item_modded(r):
        make_resource_modded(row)
        if not is_item_modded(r):
            print('Info: cannot mod item #{} (blank resource?)'.format(row))
            return

    take_values_table_screenshots()

# Takes the requisite screenshots
def take_values_table_screenshots():
    get_resource_value_pages()
    cv2.waitKey()

def output_resource(name, values, stdout=True):
    with open('debug/output.csv', 'a') as f:
        output = '{}\t{}'.format(name, '\t'.join([v[1] for v in values]))
        if stdout:
            print(output)
        print(output, file=f)

# Get screenshots of the entire table of resource values. Each screenshot in the list returned corresponds to
# a "page down" action on the scrollbar here.
def get_resource_value_pages():
    n = 0
    while True:
        res_name = get_resource_name()
        assert res_name

        res_values = get_values_ocr(get_cv2_screenshot(resource_values.get_region()))
        assert res_values

        output_resource(res_name, res_values, True)

        if not wait_on_image_located(image='images/fully_scrolled.tiff', region=resource_values_scrollbar_bottom_region, timeout=0.5):
            print('Finished scrolling values, returning')
            return

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
# This will grab / process the actual key/value image pairs in the values table
def get_values_ocr(image):
    # How many pixels in the row until we hit the vertical line separating key/val
    # TODO: We'll want to dynamically determine what this is because the column width of the
    # table auto-sizes based on cell content when you click a new resource.
    key_value_divider_pos = 200
    _, w, _ = image.shape

    ret = []

    for n in range(0, items_per_values_page):
        top = n * resource_values.item_height
        row_img = image[top:top+resource_values.item_height, 0:w]
        row_name_img = row_img[:, 0:key_value_divider_pos]
        row_value_img = row_img[:, key_value_divider_pos:]

        row_name = pytesseract.image_to_string(Image.fromarray(process_values_image(row_name_img)), config=' --psm 7')
        row_value = pytesseract.image_to_string(Image.fromarray(process_values_image(row_value_img)), config=' --psm 7')

        row_name = clean_ocr_text(row_name)
        row_value = clean_ocr_text(row_value)

        if row_name:
            ret.append((row_name, row_value))

        #cv2.imwrite('images/debug/delme{}_name.tiff'.format(n), process_values_image(row_name_img))
        #cv2.imwrite('images/debug/delme{}_val.tiff'.format(n), process_values_image(row_value_img))
        #cv2.imwrite('images/debug/delme{}_row.tiff'.format(n), process_values_image(row_img))

        get_values_ocr.gn += 1

    processed_img = process_values_image(image)
    cv2.imwrite('images/debug/processed_img.tiff', processed_img)
    return ret
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

def iterate_resources():
    """ Go through the resource list and try to output the values """
    effective_row = 0
    end = 184
    skip = 0
    for n in range(0, end):
        if n < skip:
            continue
        # Click page down if we reach end of list
        if n % items_per_resource_list_page == 0 and n >= items_per_resource_list_page:
            ui.rightClick(*resource_list_scrollbar_coord)
            ui.moveRel(*scrollbar_page_down_rel_coord)
            ui.click(duration=1)
        get_resource_list_item(n % items_per_resource_list_page)

def scrape_cur_type():
    img = get_cv2_screenshot(resource_type.get_region())
    type_name = pytesseract.image_to_string(Image.fromarray(process_values_image(img)), config=' --psm 7')

    return clean_ocr_text(type_name)
    #cv2.imwrite('images/debug/type.tiff', get_cv2_screenshot(resource_type.get_region()))

def scrape_types():
    click_item(resource_type.get_region(), f=ui.doubleClick)
    ui.moveRel(0, 100)
    time.sleep(2)

    for n in range(0, 1000):
        ui.press('down')
        time.sleep(1)
        #ui.hotkey('ctrl', 's')

        t = scrape_cur_type()
        f = open('debug/restypes.txt', 'a')
        print(t, file=f)
        f.close()
        print('Type:', t)
        if t.find('Sector Effect Settings') != -1:
            print('Got end of types')
            break

app = Application().connect(best_match='ResourceEd')
window = app.top_window()
window.minimize()
window.maximize()

window.set_focus()

scrape_types()

print('**** Done')