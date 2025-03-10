import math
import re
import sys
import numbers
import psutil
import pyautogui
import time
import pytesseract
from PIL import Image, ImageOps, ImageChops
import difflib
import config
import random
import os
import logging
import keyboard
import subprocess
from io import StringIO
from PyQt5.QtGui import QKeyEvent, QIcon, QIntValidator, QDoubleValidator, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import gui
import shutil
import threading
import DAD_Utils

# Logging setup
logging.basicConfig(
    filename = 'debug/debug.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Pytess setup
pytesseract.pytesseract.tesseract_cmd = shutil.which(config.pytessPath)



# Close Hotkey
def closeHotkey(app):
    keyboard.add_hotkey(f"ctrl+{config.closeHotkey.lower()}",lambda: closeApp(app))
    keyboard.wait()



# Close Hotkey
def sellHotkey(mainWindow):
    keyboard.add_hotkey(f"ctrl+{config.sellHotkey.lower()}",lambda: sellHotkeyExec(mainWindow))
    keyboard.wait()


# sell hotkey function
def sellHotkeyExec(mainWindow):
    DAD_Utils.logDebug("Selling via sell hotkey")
    mainWindow.handleSellItemButton() 



# Close GUI
def closeApp(app):
    DAD_Utils.logDebug("Exiting via hotkey... Goodbye!")
    app.quit()     



def main():
    logging.debug("Starting Program ...")

    #Create app
    app = gui.QApplication(sys.argv)    
    app.setWindowIcon(QIcon("img/SkullBuddy.ico"))

    #Dispaly main window
    mainWindow = gui.MainWindow() 
    mainWindow.show()             
    

    #Close app hotkey setup
    closeAppHotkey = threading.Thread(target=closeHotkey, args=(app,), daemon=True)
    closeAppHotkey.start()

    #Sell Button hotkey setup
    sellButtonHotkey = threading.Thread(target=sellHotkey, args=(mainWindow,), daemon=True)
    sellButtonHotkey.start()

    #End 
    sys.exit(app.exec_())         
    logging.debug("Program Shutting Down")

if __name__ == "__main__":
    main()