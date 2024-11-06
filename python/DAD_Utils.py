import math
import re
import sys
import numbers
import psutil
import database
import pyautogui
import time
import pytesseract
from PIL import Image, ImageOps, ImageChops
import difflib
import config
import random
import os
import logging
from pynput import keyboard, mouse

logger = logging.getLogger()  # Get the root logger configured in main.py

#item class
class item():
    # constructor
    def __init__(self, name, rolls, rarity, coords):
        self.name = name # item name
        self.rolls = rolls # item rolls
        self.rarity = rarity # item rarity
        self.price = None # item price
        self.coords = coords # item location
        self.sold = False
        self.goodRoll = None

        logger.debug("New item created")

    #Print item
    def printItem(self):
        printColor = "Black"
        if self.rarity:
            if self.rarity.lower() == 'poor' or self.rarity.lower() == 'common':
                printColor = 'gray'
            elif self.rarity.lower() == 'uncommon':
                printColor = 'green'
            elif self.rarity.lower() == 'rare':
                printColor = 'MediumBlue'
            elif self.rarity.lower() == 'epic':
                printColor = 'Orchid'
            elif self.rarity.lower() == 'legendary':
                printColor = 'Gold'
            elif self.rarity.lower() == 'unique':
                printColor = 'Yellow'

        logGui(f"{self.rarity} {self.name}",printColor)
        for roll in self.rolls:
            rollPrint = ""
            #check for % for print format
            if roll[2]:
                if int(roll[0]) == 1: rollPrint = f"+ {roll[0]}.0% {roll[1]}"
                else: rollPrint = f"+ {int(roll[0])/10:.1f}% {roll[1]}"
            else:
                 rollPrint = f"+ {roll[0]} {roll[1]}"
            #check for good roll (added after price check)
            if roll[3]:
                rollPrint += " <-- GOOD ROLL FOUND!"
            logGui(rollPrint,"DeepSkyBlue")
            
        if self.price:
            logGui(f"Price: {self.price} Gold","Goldenrod")

    def getItemStoreDetails(self):
        rollStr = ""
        for roll in self.rolls:    
            dataStr = ",".join(str(data) for data in roll)
            rollStr += "|" + dataStr
        good = 1 if self.goodRoll else 0
        return [self.name, self.rarity, rollStr, self.price, good]
        

# search market gui for all item rolls
    def searchGoodRolls(self) -> bool: #True/False searched anything
        numSearch = 0
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=0.1) 
        pyautogui.click()                

        pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.05) 
        pyautogui.click()

        for roll in self.rolls:
            if roll[3]:
                pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=0.15) 
                pyautogui.click()
                pyautogui.typewrite(roll[1], interval=0.01)

                pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * numSearch), duration=0.15) 
                pyautogui.click()
                numSearch += 1
        logger.debug(f"Searched for {numSearch} good rolls")
        return numSearch > 0

    # search market gui for all item rolls
    def searchAllRolls(self):
        for i, roll in enumerate(self.rolls):
            if i == 0:
                pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=0.1) 
                pyautogui.click()                

                pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.05) 
                pyautogui.click()

            pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=0.15) 
            pyautogui.click()
            pyautogui.typewrite(roll[1], interval=0.01)

            pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i), duration=0.15) 
            pyautogui.click()
        logger.debug(f"Searched for all rolls")

    # search market gui for indexed item roll
    def searchRoll(self,i):
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=0.1) 
        pyautogui.click() 

        pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.05) 
        pyautogui.click()

        roll = self.rolls[i]
        pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=0.15) 
        pyautogui.click()
        pyautogui.typewrite(roll[1], interval=0.01)

        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect, duration=0.15) 
        pyautogui.click()
        logger.debug("Searched for a roll")

    # search item name and rairty from market stash GUI
    def searchFromMarketStash(self):
        pyautogui.moveTo(self.coords[0], self.coords[1]) 
        pyautogui.click() 
        time.sleep(0.1)

        pyautogui.moveTo(config.xMarketSearchNameRairty, config.yMarketSearchNameRairty, duration=0.1) 
        pyautogui.click()
        logger.debug("Searching item name, rarity form market stash")  
    
    #remove roll from market gui search 
    def removeSearchRoll(self,i):
        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i), duration=0.15) 
        pyautogui.click()
        logger.debug("removed searched roll")
        
    #Search market for item price # Assume that View Market tab is open
    def findPrice(self) -> bool: # True/False Price Find Success
        logger.debug(f"Searching for {self.name} price")
        logGui(f"Searching market for {self.rarity} {self.name}")

        prices = []
        foundPrice = None
        # reset filters, search rarity
        self.searchFromMarketStash()

        #store base price
        while foundPrice is None:
            foundPrice = recordDisplayedPrice()
        prices.append(foundPrice)
        logger.debug(f"Found price {foundPrice} base price")

        #store price of each roll
        for i, roll in enumerate(self.rolls):
            self.searchRoll(i)
            foundPrice = recordDisplayedPrice()
            if foundPrice: 
                prices.append(foundPrice)
                good = checkPriceRoll(prices[0],foundPrice)
                if good and self.goodRoll is None: self.goodRoll = good
                if not roll[3]: self.rolls[i][3] = good
            logger.debug(f"Found price {foundPrice} for roll {i+1}")

        #store all roll price
        if self.goodRoll and len(self.rolls) > 1: 
            self.searchGoodRolls()
            foundPrice = recordDisplayedPrice()
            if foundPrice: self.price = foundPrice
            logger.debug(f"Found price {foundPrice} for good rolls")
        else: self.price = min(prices)
        logger.debug(f"Found price {self.price} for {self.rarity} {self.name}")

    #Lists item for found price
    def listItem(self) -> bool: # True/False Listing Success
        price = self.price
        if price:
            undercut = config.undercutValue
            logger.debug(f"{undercut} undercut value")
            if undercut < 0:
                finalPrice = price - 1
            else:
                if isinstance(undercut,float):
                    finalPrice = int(price - (price * undercut))
                    finalPrice = int(finalPrice)
                else:
                    finalPrice = price - undercut
            logger.debug(f"{finalPrice} found")
    
            pyautogui.moveTo(self.coords[0], self.coords[1], duration=0.1) 
            pyautogui.click()
            time.sleep(0.4)

            pyautogui.moveTo(config.xSellingPrice, config.ySellingPrice, duration=0.1) 
            pyautogui.click()
            logGui(f"Listing item for {finalPrice}","Goldenrod")
            pyautogui.typewrite(str(finalPrice), interval=0.06)

            pyautogui.moveTo(config.xCreateListing, config.yCreateListing, duration=0.1) 
            pyautogui.click()

            pyautogui.moveTo(config.xConfirmListing, config.yConfirmListing, duration=0.1) 
            pyautogui.click()
            logger.debug(f"Listed for {finalPrice}")
            return True

        logger.debug(f"CANNOT LIST AN ITEM WITH NO PRICE!")
        return False


# clears searched item rolls
def clearSearchRoll():
    ss = pyautogui.screenshot(region=config.ssMarketRollSearch)
    txt = pytesseract.image_to_string(ss,config="--psm 6")
    if not txt:
        pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.05) 
        pyautogui.click()
    checks = locateAllOnScreen('marketChecked',region=config.ssMarketRoll)
    myChecks = list(checks)
    for i in range(len(checks)):
        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect, duration=0.2) 
        pyautogui.click()
    checks = locateAllOnScreen('marketChecked',region=config.ssMarketRoll)
    if not checks:
        return True
    clearSearchRoll()


# check price for significant increase
def checkPriceRoll(basePrice, rollPrice) -> bool: # True/False good item roll
    if basePrice + config.sigRollIncrease[0] < rollPrice or basePrice + int(config.sigRollIncrease[1] * basePrice) < rollPrice:
        logger.debug("Good Price Found!")
        return True
    else:
        return False


# searches market and finds price
def recordDisplayedPrice() -> int: # Price/None
    searched = refreshMarketSearch()
    if searched:
        price = getItemCost()
        logger.debug(f"found price {price}!")
        logGui(f"Researching prices... Found {price}...")
        return price
    else: return None


# compare ss and confirm change in game state
def confirmGameScreenChange(ss1, region=config.ssComp2) -> bool: #True/False Success
    noInfiniteLOL = 0
    newRegion = [0,0,0,0]
    for i, val in enumerate(region):
        if i < 2:
            newRegion[i] = val - 50
        else:
            newRegion[i] = val + 100

    while noInfiniteLOL < 31:
        check = locateOnScreen(ss1,region=newRegion)
        if not check: return True
        time.sleep(0.05)
        noInfiniteLOL += 1

    return False


# take ss and read txt
def readSSTxt(region,config=config.pytessConfig):
    ss = pyautogui.screenshot(region=region)
    ss.save('LOLtest.png')
    txt = pytesseract.image_to_string(ss,config=config)
    if txt: return txt
    else: return None


# send market request and confirm response
def refreshMarketSearch() -> bool: # True/False Success
    logger.debug("refreshing market Search...")
    ss = pyautogui.screenshot(region=config.ssMarketExpireTime)
    pyautogui.moveTo(config.xSearchPrice, config.ySearchPrice, duration=0.15)
    pyautogui.click()
    ret = confirmGameScreenChange(ss,region=config.ssMarketExpireTime)
    logger.debug(f"{ret}! Gui change")
    return ret


# Refresh market search query
def refreshMarketItem():
    logger.debug("refreshing market filters...")
    pyautogui.moveTo(config.xResetFilters, config.yResetFilters, duration=0.05)
    pyautogui.click()
    time.sleep(0.2)


# get average cost of displayed item in market lookup
def getItemCost():
    prices = readPrices()
    if prices:
        price = calcItemPrice(prices,config.sellMethod)
        return price
    else: return None


# read displayed prices from market
def readPrices() -> list: # return list of prices
    ss = pyautogui.screenshot(region=config.ssGold)
    data = ss.getdata()
    newData = []

    for item in data:
        if (item[0] >= 120 or item[1] >= 120):
            newData.append(item)
        else:
            newData.append((0,0,0))

    ss.putdata(newData)
    numConfig = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    txt = pytesseract.image_to_string(ss,config=numConfig)
    prices = txt.split()
    for i, price in enumerate(prices):
        prices[i] = int(price)
    logger.debug(f"Found prices: {prices}")
    return prices
                                

# compute price from list of item prices
def calcItemPrice(prices, method, ascending=True):
    priceLen = len(prices)
    if priceLen == 0:
        return None

    #make sure list is ascending order
    if ascending:
        prev = prices[0]
        for price in prices[1:-1]:
            if prev > price:
                prices.remove(price)
            else:
                prev = price

    logger.debug(f"Calcing price ... Method {method}...")
    
    #Lowest
    if method == 1:
        lowest = int(prices[0])
        if priceLen > 1:
            for price in prices[1:]:
                price = int(price)
                if price < lowest: lowest = price
        return lowest

    #Lowest, but remove outliers
    elif method == 2:
        avg = 0
        useLen = priceLen if priceLen < 4 else 4
        for price in prices[:useLen]:
            avg += int(price)
        avg = int(avg/useLen)
        
        for price in prices: 
            ret = int(price)
            if abs(ret - avg) < avg * 0.37:
                return ret
            
    #Avg first 3
    elif method == 3:
        useLen = priceLen if priceLen < 3 else 3

        avg = 0
        for price in prices[:useLen]:
            avg += int(price)
        return int(avg / useLen)


#Load global variables and clear debug file. MUST BE RAN!
def loadTextFiles():
    logger.debug(f"Loading config files")
    global allItems
    global allRolls

    with open("debug.log", 'w') as file:
        pass

    with open("config/items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    with open("config/rolls.txt", 'r') as file:
        lines = file.readlines()
    allRolls = [line.strip() for line in lines]


#update config.py
def updateConfig(var,newVal) -> bool: # ret True/False updated
    logger.debug(f"Updating config {var} -> {newVal}")
    with open("python/config.py","r") as file:
        lines = file.readlines()

    with open("python/config.py","w") as file:
        for line in lines:
            if line.startswith(var):
                if isinstance(newVal,str):
                    file.write(f'{var} = "{newVal}"\n')
                else:
                    file.write(f'{var} = {newVal}\n')
            else:
                file.write(line)


#Sends all treasure to expressman
def stashExpressman():
    xStart = config.xInventory
    yStart = config.yInventory
    for y in range(5):
        for x in range(10):
            newX = (x * 41) + xStart
            newY = (y * 41) + yStart
            if detectItem(x * 41,y * 41,xStart,yStart):
                pyautogui.moveTo(newX,newY) 
                if getItemSlotType() == "Invalid":
                    clickAndDrag(newX, newY, config.xStartExpressmanInv + (x * 41), config.yStartExpressmanInv + (y * 41),duration=0.05)

    return True


#Gathers all items from expressman
def gatherExpressman():
    while detectItem(0,0,config.xCollectExpressman,config.yCollectExpressman):
        pyautogui.moveTo(config.xCollectExpressman,config.yCollectExpressman,duration=0.2) 
        pyautogui.click()

        if locateOnScreen("fillInAllStash",grayscale=False,confidence=0.998):
            pyautogui.moveTo(config.xPayGetExpressman,config.yPayGetExpressman,duration=0.2) 
            pyautogui.click()

        pyautogui.moveTo(config.xPayGetExpressman,config.yPayGetExpressman+70,duration=0.2) 
        pyautogui.click()

    return True
        

# Returns slot type of highlighted item
def getItemSlotType():
    location = locateOnScreen("slotType",confidence=0.9)
    if not location:
        return None
    
    ssRegion = (int(location[0]), int(location[1]), 250, 25)

    ss = pyautogui.screenshot(region=ssRegion)
    ss = ss.convert("RGB")
    ss.save('debug/itemSlot.png')
    txt = pytesseract.image_to_string('debug/itemSlot.png',config="--psm 6")
    print(txt)
    txtRemove = "Slot Type"
    try:
        keyword_index = txt.index(txtRemove) + len(txtRemove)
        ret = txt[keyword_index:].lstrip()
        finalRet = ''.join(char for char in ret if char.isalpha())
        return finalRet
    except ValueError:
        return None  


# Selects item with shortest name from market gui 
def selectItemSearch() -> bool: # True/False selected
    #read img
    ss = pyautogui.screenshot(region=config.itemSearchRegion)
    ss = ss.convert("RGB")
    data = ss.getdata()
    newData = []
    for item in data:
        avg = math.floor((item[0] + item[1] + item[2]) / 3)
        bounds = avg * 0.05
        if bounds > abs(avg - item[0]) and bounds > abs(avg - item[1]) and bounds > abs(avg - item[2]):
            newData.append(item)
        else:
            newData.append((0,0,0))
    ss.putdata(newData)
    txt = pytesseract.image_to_string(ss,config="--psm 6")
    txt = ''.join(char for char in txt if char.isalpha() or char.isspace())
    txt = txt.splitlines()
    for txtLines in reversed(txt):
        if len(txtLines) < 3:
            txt.remove(txtLines)

    #click button with lowest char count (this works since we looked up item name)
    if len(txt) == 0:
        logDebug("Item not found in search ... we have a problem")
        return False
    elif len(txt) == 1:
        pyautogui.moveTo(config.xItemSelect,config.yItemSelect) 
        pyautogui.click()
        return True
    lengths = []
    for lines in txt:
        lengths.append(len(lines))
    minLength = min(lengths)
    minIndex = lengths.index(minLength)

    ss = pyautogui.screenshot(region=config.ssItemNameSearch)
    pyautogui.moveTo(config.xItemSelect,config.yItemSelect + (minIndex * 25)) 
    pyautogui.click()
    ret = confirmGameScreenChange(ss,region=config.ssItemNameSearch)
    return ret


#Navigate to the market place
def navToMarket():
    #Add some automation, if not on main screen FIX
    if locateOnScreen('verifyMarket',region=config.getMarketRegion): 
        pyautogui.moveTo(config.xMyListings,config.yMyListings) 
        pyautogui.click()

    if locateOnScreen('verifyTitleScreen',region=(0,0,500,333)): 
        navCharLogin()

    if locateOnScreen('verifyMainScreen',region=(0,0,300,300)): 
        pyautogui.moveTo(config.xSelectTrade,config.ySelectTrade) 
        pyautogui.click()

        while not locateOnScreen('verifyMarket',region=config.getMarketRegion):
            pyautogui.moveTo(config.xSelectMarket,config.ySelectMarket) 
            pyautogui.click()

        while not locateOnScreen('selectedMyListings', region=config.regionMarketListings):
            pyautogui.moveTo(config.xMyListings,config.yMyListings) 
            pyautogui.click()      


#two obv logging func
def logDebug(txt):
    logger.debug(txt) 


def logGui(txt,color='black'):
    print(f"<span style='color: {color};'>{txt}</span>")


# Return location and santize ImageNotFound error
def locateOnScreen(img,region=config.getScreenRegion,grayscale=False,confidence=0.99):
    logger.debug(f"Searching for Image...")
    strKey = isinstance(img, str)
    try:
        if strKey:
            res = pyautogui.locateOnScreen(f'img/{img}.png', region = region, confidence = confidence, grayscale = grayscale)
        else:
            res = pyautogui.locateOnScreen(img, region = region, confidence = confidence, grayscale = grayscale)
        return res 
    except:
        logger.debug("Failed to find image")
        return None
    

def locateAllOnScreen(img,region=config.getScreenRegion,grayscale=False,confidence=0.99):
    logger.debug(f"Searching for Image {img}...")
    strKey = isinstance(img, str)
    try:
        if strKey:
            res = pyautogui.locateAllOnScreen(f'img/{img}.png', region = region, confidence = confidence, grayscale = grayscale)
        else:
            res = pyautogui.locateAllOnScreen(img, region = region, confidence = confidence, grayscale = grayscale)
        listRes = list(res)
        return listRes
    except:
        logger.debug("Failed!")
        return None
        

# Read image text and confirm the rarity
def confirmRarity(img,rarity):
    left = int(img.left)
    top = int(img.top)
    width = int(img.width)
    height = int(img.height)
    ssRegion=(left, top, width, height)
    ss = pyautogui.screenshot(region=ssRegion)
    txt = pytesseract.image_to_string(ss, config="--psm 6")
    if rarity.lower() in txt.lower():
        return 1
    else:
        return 0


# Returns the rarity of the item in top left 
def getItemRarity(region=config.firstSlotItemDisplayRegion):
    ret = None

    poorDetect = locateOnScreen('poor', region=region)
    if poorDetect:
        if confirmRarity(poorDetect,'poor'):
            ret = 'Poor'

    commonDetect = locateOnScreen('common', region=region)
    if commonDetect:
        if confirmRarity(commonDetect,'common'):
            ret = 'Common'

    uncommonDetect = locateOnScreen('uncommon', region=region)
    if uncommonDetect:
        if confirmRarity(uncommonDetect,'uncommon'):
            ret = 'Uncommon'

    rareDetect = locateOnScreen('rare', region=region)
    if rareDetect:
        if confirmRarity(rareDetect,'rare'):
            ret = 'Rare'

    epicDetect = locateOnScreen('epic', region=region)
    if epicDetect:
        if confirmRarity(epicDetect,'epic'):
            ret = 'Epic'

    legendaryDetect = locateOnScreen('legendary', region=region)
    if legendaryDetect:
        if confirmRarity(legendaryDetect,'legendary'):
            ret = 'Legendary'

    uniqueDetect = locateOnScreen('unique', region=region)
    if uniqueDetect:
        if confirmRarity(uniqueDetect,'unique'):
            ret = 'Unique'

    if ret:
        logger.debug(f"Found {ret} item")  
    else:
        logger.debug("ERROR!!! NO RARITY FOUND") 

    return ret   


# detects if item is in stash on given coords
def detectItem(x,y):
    ss = pyautogui.screenshot(region=[x,y,20,20])
    ss = ss.convert("RGB")
    # ss.save(f"debug/seeStash_{x}_{y}.png")
    w, h = ss.size
    data = ss.getdata()
    total = 0
    ret = False
    for item in data:
        total += sum(item)
    div = w*h
    res = math.floor(total/div)
    logger.debug(f"Pixel val for x:{x} y:{y} {res}")
    if res > 110:
        ret = True

    if ret:
        logger.debug("Item detected")
    else:
        logger.debug(f"No item detected: {str(res)} < 110")
    return ret


# Get the availible listing slots
def getAvailSlots():
    #Take screenshot and sanitize for read text
    ss = pyautogui.screenshot(region=[config.xGetListings,config.yGetListings,config.x2GetListings,config.y2GetListings])
    ss = ss.convert("RGB")
    txt = pytesseract.image_to_string(ss,config="--psm 6")
    txt = txt.splitlines()

    #Read for listing slots and report if any avial, and #of slots
    slots = 0
    for lines in txt:
        if lines == 'List an Item':
            slots += 1
        else:
            continue

    logger.debug(f"{slots} listings availible")

    return slots


#Check listings for sold items and claim gold 
#I NEED TO OPTIMIZE THIS WITH checkScreenChange
def gatherSoldListings():
    sold = locateAllOnScreen("soldItem", confidence=0.95)
    soldList = list(sold)
    if soldList:
        numClear = len(soldList) if len(soldList) < 3 else 3
        for first3 in soldList[:numClear]:
            pyautogui.moveTo(int(first3[0] + 30), int(first3[1]), duration=0.2) 
            pyautogui.click()

            pyautogui.moveTo(config.xCanOrTransfer, config.yCanOrTransfer, duration=0.2) 
            pyautogui.click()
            logger.debug("Gathering Gold ...")
        gatherSoldListings()
    else: logger.debug("All sold items cleared")
    

# Lookup and return input_string from phrase_list
def findItem(input_string, phrase_list,n=1):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=n, cutoff=0.6)
    logger.debug(f"Found: {closest_match}")
    return closest_match[0] if closest_match else None


# return to market
def returnMarketStash():
    ss = pyautogui.screenshot(region=config.ssComp1)
    def work():
        pyautogui.moveTo(config.xMyListings, config.yMyListings, duration=0.1) 
        pyautogui.click()  
        if not confirmGameScreenChange(ss):
            logger.debug("attempting to switch to market listings...")
            work()
        else: 
            return True
    if work():
        time.sleep(0.1)
        return True


# return value, roll name
def seperateRollValues(s) -> list: #[val, rollName]
    # Use re.findall to extract both numbers and text in order
    parts = re.findall(r'\d+%?|\D+', s)
    
    # Clean up the parts by trimming extra whitespace from text
    parts = [part.strip() for part in parts if part.strip()]

    return parts


# Navigate char login screen
def navCharLogin():
    xChar, yChar = 1750, 200 # coords for char location
    pyautogui.moveTo(xChar, yChar, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click

    xLobby, yLobby = 960, 1000  # coords for enter lobby location
    pyautogui.moveTo(xLobby, yLobby, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click
    
    while not locateOnScreen('verifyMainScreen', region=(0,0,300,300)):
        time.sleep(0.3)


# Change class 
def changeClass():
    pyautogui.moveTo(config.xPlay, config.yPlay, duration=0.1)  
    pyautogui.click()  # Perform a mouse click

    pyautogui.moveTo(config.xChangeClass,config.yChangeClass,duration=0.1)
    pyautogui.click()

    time.sleep(3)


# moves mouse from start to end
def clickAndDrag(xStart, yStart, xEnd, yEnd, duration=0.1):
    pyautogui.moveTo(xStart, yStart)  # Move to the starting position
    pyautogui.mouseDown()        # Press and hold the mouse button
    time.sleep(0.05)              # Optional: Wait a moment for the cursor to settle
    pyautogui.moveTo(xEnd, yEnd, duration=duration)  # Drag to the destination position
    time.sleep(0.05)   
    pyautogui.mouseUp()          # Release the mouse button
    pyautogui.moveTo(config.xStashStart, config.yStashStart)


# Main script call. Search through all stash cubes, drag item to first, and sell
def searchStash():
    loadTextFiles()
    if getAvailSlots():

        conn, cursor = database.connectDatabase()

        for y in range(config.sellHeight):
            for x in range(config.sellWidth):
                
                xHome = config.xStashStart
                yHome = config.yStashStart
                newY = yHome + (40 *y)
                newX = xHome +(40 *x)
                logger.debug(f"Searching stash at x:{newX} y:{newY}")
                if not detectItem(newX,newY):
                    continue
                #Item found, hover and check listing slot
                pyautogui.moveTo(newX, newY)
                sucess = mainLoop(cursor)
                if not sucess:
                    logGui(f"Item listing failure ... go next")
                if not getAvailSlots(): 
                    database.closeDatabase(conn)
                    return False
        database.closeDatabase(conn)        
    else:
        logGui(f"No Listing slots avialible...")


# creates and returns item class from hovered item 
def getItemInfo() -> item:
    #vars
    global allItems
    global allRolls
    coords = []
    name = ""
    rolls = []
    foundName = False
    logGui("Reading item...")

    #check if item is on screen
    space = locateOnScreen('findItem',confidence=0.95)
    if not space: return None
    
    x, y = pyautogui.position()
    coords = [x,y]
    
    #screenshot for text & rarity
    ssRegion = (int(space[0]) - 110, int(space[1]) - 360, 335, 550)
    logGui("Getting item info...")
    rarity = getItemRarity(ssRegion)
    ss = pyautogui.screenshot(region=ssRegion)
    text = pytesseract.image_to_string(ss)
    name = ""
    rolls = []
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    lines = text.splitlines()

    #iterate read text
    logGui("Getting item rolls...")
    for line in lines:
        logDebug(f"lines: {lines}")
        if not foundName:
            found = findItem(line, allItems)
            if found: 
                name = found
                foundName = True

        if foundName:
            found = findItem(line, allRolls)
            if(found):
                roll = seperateRollValues(line)
                if "%" in found:
                    roll.append(1)
                else:
                    roll.append(0)
                if roll[0].isdigit():
                    roll.append(None)
                    rolls.append(roll)

    #make item and return
    foundItem = item(name,rolls,rarity,coords)
    return foundItem

# main function
# reads hovered item info, lists on market
def mainLoop(cursor) -> bool: # True/False listing success
    time.sleep(config.sleepTime / 5)
    mytime = time.time()
    myItem = getItemInfo()                                              # read item info
    if myItem:
        myItem.printItem()                                              # print item to gui
        myItem.findPrice()
        database.insertItem(cursor,myItem.getItemStoreDetails())        # insert into database
        returnMarketStash()                                             # return market stash
        myItem.listItem()                                               # list item
        mytime2 = time.time()
        logGui(f"Listed item in {mytime2-mytime:0.1f} seconds")         # log time to gui
        time.sleep(config.sleepTime)
        return True
    else:
        return False