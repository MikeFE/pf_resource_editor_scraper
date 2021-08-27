""" Configuration for the Resource Editor Scraper

Basically, we need to tell the scraper the coordinates to the bounding boxes of each relevant
UI control in the Resource Editor [left, top, right, bottom], so that we may simulate user
clicks / typing properly and where to take screenshots for Tesseract to interpret.

For my environment I'm using 1440p (2560x1440), if you're using another resolution *unfortunately*
you'll have to take a screenshot of the Resource Editor maximized in that resolution then figure
out the coordinates for the pertinent UI controls that way. The [x, y] coordinates for the top left corner
of the UI control will be the left & top, and the [x, y] coordinates to the bottom right corner
will be the right & bottom values.

A 1080p config file would be great but I don't have the time for it atm.

Also some of these coordinates may be off since I've been mucking around with resize_panels() a lot recently. Will
double check the numbers soon.
"""
from uicontrol import UIControl, UIList

# You can go to https://github.com/UB-Mannheim/tesseract/wiki if you plan on installing Tesseract for Windows.
# Tested version: tesseract v5.0.0-alpha.20201127
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#
# 2560x1440 maximized Resource Editor window's control positions
#

resource_name = UIControl(975, 465, 2100, 485)  # Resource's name
resource_list = UIList(30, 20, 240, 795, 1380)  # Resource list on the left side of the editor
resource_type = UIControl(555, 385, 1065, 425)  # Resource "type" indicated above resource properties table

# The rectangle here is smaller/padded from the full width to prevent the region from including
# the little icons like "down arrows" for collapsing that can be on the far left/right sides of the values.
# OCR can't read the icons.
resource_values = UIList(30, 880, 615, 2040, 1250)

items_per_values_page = 21  # Number of rows of values that fit per scrollbar page in the resource properties table
items_per_resource_list_page = 37

panel_resizer_rhs_coord = (1215, 750)  # Any valid x,y coord for the panel-resizer control to the right, used in resize_panels()

# Any valid x,y coord for the properties table scrollbar, we'll just right click this -> left click page down/up from the popup menu
resource_values_scrollbar_coord = (2095, 645)
resource_list_scrollbar_coord = (800, 350)

# Relative x,y pixel values to a valid "page down" button coordinate in the popup menu when you first right click a scrollbar
scrollbar_page_down_rel_coord = (90, 215)

# Area near the bottom of the properties table scrollbar to test if we've scrolled all values
resource_values_scrollbar_bottom_region = (2070, 1215, 50, 64)