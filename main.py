# TO DO:

#the fix for item search not in right spot is to return more than 1 result first time,
#search for string withing string, and if its YES, make plot map for dupes and refer to it



# More bounds check for getting price. Need better algorithm than double search, get max, and list - undercut %
# I should account for low listings as well (less than 3 for item check)

# ideally the flow is->
# base price with rareity
# check all Attr 
# if one attr +25% value or 100g, check best val with other attr selected
# if condition happens again & >=epic, set aside for Manual Pricing 
# else else get price and apply undercutPercent
# dev CheckListings and < 5 throw value out

# FIX item name detection, some itms not working
# you could take screenshot to ONLY capture name for better reading

# add statemachine that detects what part of game at, where need to go so you can start script whenever
# statemachine accounts for what stash to sell from
# statemachine accounts for how many selling slots left

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

def main():
    launchedGame = 0
    while True:
        if DAD_Utils.is_game_running():
            print(f"{coords.GAME_NAME} is running.")
            
            with open('debug.txt', 'w') as file:
                file.write('reset\n')

            #DAD_Utils.navCharLogin()
            #DAD_Utils.getItemDetails()
            #DAD_Utils.changeClass()
            DAD_Utils.searchStash()
            #DAD_Utils.getItemCost()
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