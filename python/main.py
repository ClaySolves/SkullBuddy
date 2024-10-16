import math
import sys
import numbers
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

def main():
    app = gui.QApplication(sys.argv)  # Create the application
    main_window = gui.MainWindow()     # Create an instance of MainWindow
    main_window.show()              # Show the window
    keyboard.add_hotkey('ctrl+q', main_window.stopScript)
    sys.exit(app.exec_())          # Start the event loop

if __name__ == "__main__":
    main()
    print("Finished/n")