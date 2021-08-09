import pyautogui
from pywinauto.application import Application

app = Application().connect(best_match='ResourceEd')
top = app.top_window()
top.minimize()
top.maximize()
top.set_focus()

pyautogui.click(134, 374)