from uicontrol import UIControl, UIList

# 2560x1440 maximized Resource Editor window's control positions
resource_list = UIList(30, 20, 240, 795, 1380)  # Resource list on the left side of the editor

# The rectangle here is smaller/padded from the full width to prevent the region from including
# the little icons that can be on the far left/right sides of the values. OCR can't read the icons.
resource_values = UIList(30, 880, 615, 2040, 1250)
items_per_page = 21  # Num rows of values that fit per scrollbar page in the values table

panel_resizer_rhs_coord = (1215, 750)  # Valid coord for the panel-resizer control to the right, we'll drag/resize this later

# Valid coord for the values table scrollbar, we'll just right click this -> left click page down/up from the popup menu
resource_values_scrollbar_coord = (2095, 645)

# Where the "page down" button is relative to the popup menu when you right click a scrollbar
scrollbar_page_down_rel_coord = (90, 215)

resource_values_scrollbar_bottom_region = (2070, 1215, 50, 64)  # Area near the bottom of the values list scrollbar test if we've scrolled all values