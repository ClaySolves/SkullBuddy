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
import database
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
def closeHotkey(app,closeKey):
    keyboard.add_hotkey(f"ctrl+{closeKey.lower()}",lambda: closeApp(app))
    keyboard.wait()



# Close Hotkey
def sellHotkey(mainWindow,sellKey):
    keyboard.add_hotkey(f"ctrl+{sellKey.lower()}",lambda: sellHotkeyExec(mainWindow))
    keyboard.wait()



# sell hotkey function
def sellHotkeyExec(mainWindow):
    DAD_Utils.logDebug("Selling via sell hotkey")
    if mainWindow.logSellThreadRunning:
        DAD_Utils.logGui("Terminating Sell Script...",color='red')
        DAD_Utils.stopScript()

    elif mainWindow.logOrganizeThreadRunning:
        DAD_Utils.logGui("Terminating Organize Script...",color='red')
        DAD_Utils.stopScript()
    else:
        mainWindow.handleSellItemButton() 



# Close GUIq
def closeApp(app):
    DAD_Utils.logDebug("Exiting via hotkey... Goodbye!")
    app.quit()     



def main():
    logging.debug("Starting Program ...") 

    conn, cursor = database.connectDatabase()
    closeKey = database.getConfig(cursor,'closeHotkey')
    sellKey = database.getConfig(cursor,'sellHotkey')
    darkMode = database.getConfig(cursor,'darkMode')

    currNumData = database.printConfig(cursor)

    if currNumData == None:
         database.updateConfig(cursor, 0)
    elif len(currNumData[0]) != config.numDatabase:
        if currNumData[0] != None:
            database.updateConfig(cursor,len(currNumData[0]) if currNumData[0] else 0)

    database.closeDatabase(conn)

    #Create app
    app = gui.QApplication(sys.argv)    
    app.setWindowIcon(QIcon("img/SkullBuddy.ico"))

    #Dispaly main window
    mainWindow = gui.MainWindow(darkMode) 
    mainWindow.show()             
    

    #Close app hotkey setup
    closeAppHotkey = threading.Thread(target=closeHotkey, args=(app,closeKey,), daemon=True)
    closeAppHotkey.start()

    #Sell Button hotkey setup
    sellButtonHotkey = threading.Thread(target=sellHotkey, args=(mainWindow,sellKey,), daemon=True)
    sellButtonHotkey.start()

    #End 
    sys.exit(app.exec_())         
    logging.debug("Program Shutting Down")

if __name__ == "__main__":
    main()