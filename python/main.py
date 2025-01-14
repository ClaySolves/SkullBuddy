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

logging.basicConfig(
    filename = 'debug/debug.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

pytesseract.pytesseract.tesseract_cmd = shutil.which(config.pytessPath)

# Close GUI
def closeApp(app):
    DAD_Utils.logGui("Exiting...")
    app.quit()     


def closeHotkey(app):
    keyboard.add_hotkey("ctrl+q",lambda: closeApp(app))
    keyboard.wait()


def main():
    shutil.copyfile("python/config.py", "config/configBackup.py")
    logging.debug("Starting Program ...")
    app = gui.QApplication(sys.argv)  # Create the application
    app.setWindowIcon(QIcon("img/SkullBuddy.ico"))
    main_window = gui.MainWindow()     # Create an instance of MainWindow
    main_window.show()              # Show the window

    hotkey_thread = threading.Thread(target=closeHotkey, args=(app,), daemon=True)
    hotkey_thread.start()

    sys.exit(app.exec_())          # Start the event loop
    print("App Closed/n")

if __name__ == "__main__":
    main()