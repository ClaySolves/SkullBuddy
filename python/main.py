import math
import sys
import numbers
import config
import psutil
import pyautogui
import time
import pytesseract
from PIL import Image, ImageOps
import difflib
import DAD_Utils
import subprocess
import keyboard
import gui
import shutil
import logging
import threading

logging.basicConfig(
    filename = 'debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
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
    shutil.copyfile("python/config.py", "python/configBackup,py")
    logging.debug("Starting Program ...")
    app = gui.QApplication(sys.argv)  # Create the application
    main_window = gui.MainWindow()     # Create an instance of MainWindow
    main_window.show()              # Show the window

    hotkey_thread = threading.Thread(target=closeHotkey, args=(app,), daemon=True)
    hotkey_thread.start()


    sys.exit(app.exec_())          # Start the event loop
    print("App Closed/n")

if __name__ == "__main__":
    main()