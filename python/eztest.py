import difflib
import DAD_Utils
import config
import time
import pyautogui

DAD_Utils.loadTextFiles()
# pyautogui.mouseInfo()

time.sleep(2)
item = DAD_Utils.getItemInfo()
item.findPrice()

