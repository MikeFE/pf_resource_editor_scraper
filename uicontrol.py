class UIControl:
    def __init__(self, left: int, top: int, right: int, bottom: int):
        assert left <= right, 'Invalid coords (left > right)'
        assert top <= bottom, 'Invalid coords (top > bottom)'
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    # Get pyautogui-friendly region tuple of the control: (left, top, width, height)
    def get_region(self):
        return (self.left, self.top, self.right - self.left, self.bottom - self.top)

class UIList(UIControl):
    def __init__(self, item_height: int, left: int, top: int, right: int, bottom: int):
        super().__init__(left, top, right, bottom)
        self.item_height = item_height

    # Get valid screen coordinates that will click a particular item in a list given the item#/row
    # Returns a tuple with the valid click coords
    def get_item(self, num: int):
        padding = 1  # Click 1 pixel down and right so we don't just click the border and do nothing
        return (padding + self.left, padding + self.top + (self.item_height * num))

    # Get pyautogui-friendly region tuple of the list item: (left, top, width, height)
    def get_item_region(self, num: int):
        item_left = self.left  # Same as list control
        item_top = self.top + (self.item_height * num)  # Calculate top of list item based on list top + item heights
        item_width = self.right - self.left  # Same as the list's width
        if item_top > self.bottom:
            raise ValueError('Item requested is out of view')

        return (item_left, item_top, item_width, self.item_height)