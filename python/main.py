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
import coords
import subprocess
import keyboard

def main():
    global running
    launchedGame = 0
    while True:
        if DAD_Utils.is_game_running():
            print(f"{coords.GAME_NAME} is running.")
            
            with open('debug.txt', 'w') as file:
                file.write('reset\n')
            DAD_Utils.navToMarket()
            time.sleep(0.3)
            DAD_Utils.selectStash(True)
            time.sleep(0.3)
            DAD_Utils.searchStash()
            break  
        else:
            if not launchedGame:
                print(f"{coords.GAME_NAME} is not running. Launching...\n")

                # Ironshield doesn't like this solution ... 
                # subprocess.Popen(DAD_Utils.findExecPath(coords.GAME_NAME))
                # launchedGame = 1

                sys.exit(f"{coords.GAME_NAME} is NOT running. Launch Dark and Darker\n")

        time.sleep(5)  # Wait 5 seconds before checking again

if __name__ == "__main__":
    main()
    print("Finished/n")