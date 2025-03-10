import math
import re
import database
import pyautogui
import importlib
import time
import pytesseract
import difflib
import config
import logging
import win32gui
import win32process
import win32con
import ctypes
import threading
import os
import psutil
from screeninfo import get_monitors

logger = logging.getLogger()  # Get the root logger configured in main.py

#item class
class item():
    # constructor
    def __init__(self, name, rolls, rarity, coords, size, price=None):
        self.name = name # item name
        self.rolls = rolls # item rolls
        self.rarity = rarity # item rarity
        self.price = price # item price
        self.coords = coords # item location
        self.size = size # item size
        self.sold = False
        self.goodRoll = None

        logger.debug("New item created")



    #Print item
    def printItem(self,newline=False):
        if self.price and self.rarity:
            self.printRarityName()

            for roll in self.rolls:
                self.printRoll(roll)
                
            logGui(f"Price: {self.price} Gold","Gold")
            if newline: logGui("\n")


    # print item rarity and name
    def printRarityName(self):
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
                printColor = 'Goldenrod'
            elif self.rarity.lower() == 'unique':
                printColor = 'PaleGoldenRod'

        rarityPrint = self.rarity[0].upper() + self.rarity[1:]
        logGui(f"{rarityPrint} {self.name}",printColor)


    #print item roll
    def printRoll(self,i):
        roll = self.rolls[i]
        rollPrint = ""
        #check for % for print format
        if roll[2]:
            if int(roll[0]) == 1: rollPrint = f"+ {roll[0]}.0% {roll[1]}"
            else: rollPrint = f"+ {int(roll[0])/10:.1f}% {roll[1]}"
        else:
            rollPrint = f"+ {roll[0]} {roll[1]}"
        #check for good roll (added after price check)

        logGui(rollPrint,"DeepSkyBlue"," ")
        if roll[3]:
            logGui(" <- Good Roll","DarkGoldenRod")
        else:
            logGui(" ")


    # get item from database storing string
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
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
        time.sleep(config.sleepTime / 15)
        pyautogui.click()                

        pyautogui.moveTo(config.xAttribute, config.yAttribute)
        time.sleep(config.sleepTime / 15) 
        pyautogui.click()

        for roll in self.rolls:
            if roll[3]:
                clearAttrSearch()
                pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
                time.sleep(config.sleepTime / 15) 
                pyautogui.click()
                pyautogui.typewrite(roll[1], interval=0.004)

                pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * numSearch))
                time.sleep(config.sleepTime / 15)
                pyautogui.click()
                numSearch += 1
        logger.debug(f"Searched for {numSearch} good rolls")
        return numSearch > 0



    # search market gui for all item rolls
    def searchAllRolls(self):
        for i, roll in enumerate(self.rolls):
            if i == 0:
                pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
                time.sleep(config.sleepTime / 15)
                pyautogui.click()                

                pyautogui.moveTo(config.xAttribute, config.yAttribute)
                time.sleep(config.sleepTime / 15)
                pyautogui.click()

            clearAttrSearch()
            pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
            time.sleep(config.sleepTime / 15)
            pyautogui.click()
            pyautogui.typewrite(roll[1], interval=0.004)

            pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i))
            time.sleep(config.sleepTime / 15)
            pyautogui.click()
        logger.debug(f"Searched for all rolls")



    # search market gui for indexed item roll
    def searchRoll(self,i):
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
        time.sleep(config.sleepTime / 15)
        pyautogui.click() 

        pyautogui.moveTo(config.xAttribute, config.yAttribute)
        time.sleep(config.sleepTime / 15)
        pyautogui.click()

        clearAttrSearch()
        roll = self.rolls[i]
        pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
        time.sleep(config.sleepTime / 15)
        pyautogui.click()
        pyautogui.typewrite(roll[1], interval=0.004)

        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect)
        time.sleep(config.sleepTime / 15)
        pyautogui.click()
        logger.debug("Searched for a roll")



    # search item name and rairty from market stash GUI
    def searchFromMarketStash(self):
        pyautogui.moveTo(self.coords[0], self.coords[1]) 
        pyautogui.click() 
        time.sleep(config.sleepTime / 9)

        pyautogui.moveTo(config.xMarketSearchNameRairty, config.yMarketSearchNameRairty, duration=0.1) 
        pyautogui.click()
        logger.debug(f"Searching for {self.rarity} {self.name} form market stash")
    


    #remove roll from market gui search 
    def removeSearchRoll(self,i):
        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i))
        time.sleep(config.sleepTime / 10)
        pyautogui.click()
        logger.debug("removed searched roll")



    #Search market for item price # Assume that View Market tab is open
    # Written for hotfix #79+
    def findPrice3(self) -> bool: #True/Flase Price Find Success
        logger.debug(f"Searching for {self.name} price")

        if isinstance(config.undercutValue,float):
            quickCheckMax = config.sellMax - (config.sellMax * config.undercutValue)
        else:
            quickCheckMax = config.sellMax - config.undercutValue
        quickCheckMin = config.sellMin

        self.printRarityName()
        # algo for item with many rolls
        if (self.rarity.lower() == 'epic' or self.rarity.lower() == 'legendary' or self.rarity.lower() == 'unique' or self.rarity.lower() == 'rare'):
            logger.debug(f"many roll item found")

            # record price of all rolls
            allAttrPrice = recordDisplayedPrice(False)
            if allAttrPrice:
                if allAttrPrice < quickCheckMin or allAttrPrice > quickCheckMax: return False
            
            # reset attr and get baseprice
            pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
            time.sleep(config.sleepTime / 15)
            pyautogui.click()

            prices = []

            foundPrice = recordDisplayedPrice()
            prices.append(foundPrice)
            
            if foundPrice:
                if foundPrice > quickCheckMax: return False
            
                if allAttrPrice:
                    worthLookup = foundPrice + config.sigRollIncreaseStatic < allAttrPrice
                    if not worthLookup:
                        logGui(f"Found ",printEnd=" ")
                        if isinstance(allAttrPrice,int):
                            logGui(f"{allAttrPrice}",color="Gold",printEnd=" ")
                        else:
                            logGui(f"{allAttrPrice}",color="Gray",printEnd=" ")
                        logGui(f"for ",printEnd=" ")
                        self.printRarityName()

                        self.price = foundPrice
                        return True

            # search and store each roll
            goodRolls = 0
            for i, _ in enumerate(self.rolls):
                self.searchRoll(i)
                foundPrice = recordDisplayedPrice()
                if foundPrice: 
                    if foundPrice > quickCheckMax: return False
                    prices.append(foundPrice)
                    good = checkPriceRoll(prices[0],foundPrice)
                    self.rolls[i][3] = good
                    if good:
                        self.goodRoll = good
                        goodRolls = goodRolls + 1
                
            #store many good roll price if there are many good rolls
            if goodRolls >= 2 and goodRolls != len(self.rolls): 
                self.searchGoodRolls()
                foundPrice = recordDisplayedPrice()
                if foundPrice: 
                    if foundPrice > quickCheckMax: return False
                    prices.append(foundPrice)


            # assign best price 
            if prices: 
                finalPrice = max(prices)
                #Check if profitable or too expensive
                # to do, add each rarity sell off but for now just check to make the listing fee
                self.price = finalPrice
                logGui(f"Found ",printEnd=" ")
                if isinstance(finalPrice,int):
                    logGui(f"{finalPrice}",color="Gold",printEnd=" ")
                else:
                    logGui(f"{finalPrice}",color="Gray",printEnd=" ")
                logGui(f"for ",printEnd=" ")
                self.printRarityName()
                return True
            
            return False

        #algo for item with few rolls
        elif(self.rarity.lower() == 'poor' or self.rarity.lower() == 'common' or self.rarity.lower() == 'uncommon'):
            logDebug(f"few roll item found")

            # record price of all rolls
            foundPrice = recordDisplayedPrice(False)
            if foundPrice:
                if foundPrice > quickCheckMax or foundPrice < quickCheckMin: return False

            # found price on all attr search, return and log
            if foundPrice:
                logGui(f"Found ",printEnd=" ")
                if isinstance(foundPrice,int):
                    logGui(f"{foundPrice}",color="Gold",printEnd=" ")
                else:
                    logGui(f"{foundPrice}",color="Gray",printEnd=" ")
                logGui(f"for ",printEnd=" ")
                self.printRarityName()
                self.price = foundPrice
                return True
            
            # no matching listing for all attr, search all attr individually
            price = None

            # reset attr and get baseprice
            pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
            time.sleep(config.sleepTime / 15)
            pyautogui.click() 

            foundPrice = recordDisplayedPrice()

            if foundPrice: 
                self.price = foundPrice
                logGui(f"Found ",printEnd=" ")
                if isinstance(foundPrice,int):
                    logGui(f"{foundPrice}",color="Gold",printEnd=" ")
                else:
                    logGui(f"{foundPrice}",color="Gray",printEnd=" ")
                logGui(f"for ",printEnd=" ")
                self.printRarityName()
                return True
        
            return False

        # this should never trigger
        else:
            logDebug('BAD ITEM READ !!!')

        logDebug('Price Read Error')
        return False


    #Search market for item price # Assume that View Market tab is open
    #Rewrite for optimization
    #Depricated
    def findPrice2(self) -> bool: #True/Flase Price Find Success
        logger.debug(f"Searching for {self.name} price")
        logGui(f"Searching market for {self.rarity} {self.name}")

        # Search for item from Listings Stash
        ss = pyautogui.screenshot(region=config.ssMarketItem)
        self.searchFromMarketStash()
        confirmGameScreenChange(ss,region=config.ssMarketItem)

        # record price of all rolls
        self.searchAllRolls()
        foundPrice = recordDisplayedPrice()

        # found price on all attr search, return and log
        if foundPrice:
            logGui(f"Found {foundPrice} for {self.name}")
            logDebug(f"Found {foundPrice} for {self.name}")
            self.price = foundPrice
            return True
        
        # no matching listing for all attr, search all attr 1 @ at a time
        prices = []

        # reset attr and get baseprice
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
        time.sleep(config.sleepTime / 15)
        pyautogui.click() 

        foundPrice = recordDisplayedPrice()
        prices.append(foundPrice)

        # search and store each roll
        manyGoodRolls = False
        goodRolls = 0
        for i, _ in enumerate(self.rolls):
            self.searchRoll(i)
            foundPrice = recordDisplayedPrice()
            if foundPrice: 
                prices.append(foundPrice)
                good = checkPriceRoll(prices[0],foundPrice)
                if good and self.goodRoll is None:
                    self.goodRoll = good
                    goodRolls += 1
                    manyGoodRolls = goodRolls >= 2
            logger.debug(f"Found price {foundPrice} for roll {self.rolls[i]}")

        #store many good roll price if there are many good rolls
        if manyGoodRolls: 
            self.searchGoodRolls()
            foundPrice = recordDisplayedPrice()
            if foundPrice: prices.append(foundPrice)
            logger.debug(f"Found price {foundPrice} for good rolls")

        # assign best price 
        if prices: 
            finalPrice = max(prices)
            #Check if profitable or too expensive
            # to do, add each rarity sell off but for now just check to make the listing fee
            self.price = finalPrice
            logGui(f"Found price {self.price} for {self.rarity} {self.name}")
            logger.debug(f"Found price {self.price} for {self.rarity} {self.name}")
            return True
        
        return False

        
        
    #Search market for item price # Assume that View Market tab is open
    #Depricated
    def findPrice(self) -> bool: # True/False Price Find Success
        logger.debug(f"Searching for {self.name} price")
        logGui(f"Searching market for {self.rarity} {self.name}")

        prices = []
        foundPrice = None
        # reset filters, search rarity
        self.searchFromMarketStash()

        #store base price, 5 attempts
        attempts = 3
        for attempt in range(attempts):
            foundPrice = recordDisplayedPrice(True)
            if foundPrice:
                prices.append(foundPrice)
                break
            else:
                foundPrice = 0

        #If none found or <15, something is wrong. Go next
        goodBaseRead = True
        if foundPrice < 15:
            logger.debug(f"!!!!!!!!!WEIRD LOW PRICE FOUND!!!!!!!!!!")
            goodBaseRead = False
            if self.rarity == 'poor' or self.rarity == 'common':
                return False
        logger.debug(f"Found price {foundPrice} base price")

        #store price of each roll
        manyGoodRolls = False
        goodRolls = 0
        for i, roll in enumerate(self.rolls):
            self.searchRoll(i)
            foundPrice = recordDisplayedPrice()
            if foundPrice: 
                prices.append(foundPrice)
                good = checkPriceRoll(prices[0],foundPrice)
                if good and self.goodRoll is None and goodBaseRead:
                    self.goodRoll = good
                    goodRolls += 1
                    manyGoodRolls = goodRolls >= 2
                if not roll[3]: self.rolls[i][3] = good
            logger.debug(f"Found price {foundPrice} for roll {i+1}")
        
        #store all roll price if there are many good rolls
        if manyGoodRolls: 
            self.searchGoodRolls()
            foundPrice = recordDisplayedPrice()
            if foundPrice: self.price = foundPrice
            logger.debug(f"Found price {foundPrice} for good rolls")
        else:
            if prices: 
                finalPrice = max(prices)
                #Check if profitable or too expensive
                # to do, add each rarity sell off but for now just check to make the listing fee
                if finalPrice < 15 or finalPrice > config.sellMin:
                    return False
                else:
                    self.price = finalPrice
                    logger.debug(f"Found price {self.price} for {self.rarity} {self.name}")
                    return True
            else:
                return False



    #confirms item should be listed for found price:
    def confirmPrice(self) -> bool: #True/False is good to list
        rarity = self.rarity
        size = self.size[0] * self.size[1]
        if rarity: rarity = rarity.lower()
        priceCalc = None
        useRolls = False
        numRolls = len(self.rolls)

        if self.price < config.sellMin or self.price > config.sellMax:
            return False
        if rarity == None:
            useRolls = True
        elif (rarity == "uncommon" or rarity == "common" or rarity == 'poor'):
            if size == 1: priceCalc = 7
            else: priceCalc = 3
        elif rarity == "rare":
            if size == 1: priceCalc = 12
            else: priceCalc = 6
        elif rarity == "epic":
            if size == 1: priceCalc = 20
            else: priceCalc = 10
        elif rarity == "legendary":
            if size == 1: priceCalc = 32
            else: priceCalc = 20
        elif rarity == "unique":
            if size == 1: priceCalc = 53
            else: priceCalc = 30

        if self.price - 15 > size * priceCalc: return True
        
        logger.debug(f"{rarity} {self.name} not listed at {self.price}, vendor instead")
        return False
        


    #Lists item for found price
    def listItem(self) -> bool: # True/False Listing Success
        price = self.price
        if price and self.confirmPrice():
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
            time.sleep(config.sleepTime / 3)

            pyautogui.moveTo(config.xSellingPrice, config.ySellingPrice, duration=0.1) 
            pyautogui.click()
            logGui(f"Listing item for {finalPrice}","Gold")
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
def checkPriceRoll(basePrice, rollPrice, staticCheck=config.sigRollIncreaseStatic) -> bool: # True/False good item roll
    if basePrice + staticCheck < rollPrice or basePrice + int(config.sigRollIncreasePercent * basePrice) < rollPrice:
        logger.debug("Good Price Found!")
        return True
    else:
        return False



# searches market and finds price
def recordDisplayedPrice(search=True) -> int: # Price/None
    logGui(f"Finding prices... ",printEnd=" ")

    if search:
        pyautogui.moveTo(config.xSearchPrice, config.ySearchPrice)
        pyautogui.click()

        ss = pyautogui.screenshot(region=config.ssMarketSearch)
        changed = confirmGameScreenChange(ss,config.ssMarketSearch)

        if not changed: 
            logger.debug(f"no price found ...")
            return None

    price = readPrices()

    if price:
        price = calcItemPrice(price,config.sellMethod)
        logGui(f"Found ",printEnd=" ")
        if isinstance(price,int):
            logGui(f"{price}",color="Gold",printEnd=" ")
        else:
            logGui(f"{price}",color="Gray",printEnd=" ")
        logGui(f"...",printEnd=" ")
    else:
        logger.debug(f"no price found ...")
        return None
    
    logger.debug(f"Found price {price}")
    return price



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
        time.sleep(config.sleepTime / 30)
        noInfiniteLOL += 1

    return False



# take ss and read txt
def readSSTxt(region,config=config.pytessConfig):
    ss = pyautogui.screenshot(region=region)
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
    time.sleep(config.sleepTime / 7.5)



# read displayed prices from market
def readPrices() -> list: # return list of prices
    ss = pyautogui.screenshot(region=config.ssGold)
    data = ss.getdata()
    newData = []
    retPrices = []

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
        priceAdd = int(price)
        if priceAdd > 15:
            retPrices.append(priceAdd)

    logger.debug(f"Found prices: {retPrices}")
    return retPrices



# compute price from list of item prices
def calcItemPrice(prices, method, ascending=True):
    priceLen = len(prices)
    if priceLen == 0:
        return 0

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



# get size of selected item, return size of 1 if error read
def getItemSize(ss) -> list:
    res = locateOnImage('topLeftCorner', ss, grayscale=False,confidence=0.82)
    res4 = locateOnImage('bottomRightCorner', ss, grayscale=False,confidence=0.82)
    res2 = None
    res3 = None
    if not (res4 and res):
        res2 = locateOnImage('topRightCorner',  ss, grayscale=False,confidence=0.82)
        res3 = locateOnImage('bottomLeftCorner',  ss, grayscale=False,confidence=0.82)

    if res and res4:
        xSize = round((int(res4[0])-int(res[0])) / 39)
        ySize = round((int(res4[1])-int(res[1])) / 39)
        logDebug(f"item area: {xSize} x {ySize}")
        return (xSize,ySize)
        
    elif res2 and res3:
        xSize = round((int(res2[0])-int(res3[0])) / 39)
        ySize = round((int(res3[1])-int(res2[1])) / 39)
        logDebug(f"item area: {xSize} x {ySize}")
        return (xSize,ySize)

    return (1,1)



#Load global variables and clear debug file. MUST BE RAN!
def loadTextFiles():
    logger.debug(f"Loading config files")
    global allItems
    global allRolls

    with open("debug/debug.log", 'r+') as file:
        #Clear debug file if over 2MB
        file.seek(0,2)
        size = file.tell()
        if size > 2000000:
            file.seek(0)  
            file.truncate(0) 
            file.write("Debug.log cleared")
    

    with open("config/items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    with open("config/rolls.txt", 'r') as file:
        lines = file.readlines()
    allRolls = [line.strip() for line in lines]



#Minimize Window
def minimizeSelf():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)



#restore window
def restoreSelf():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def getCurrentDisplay():
    """
    Returns which display number the current program is running on.
    Returns: int or None (1 for first display, 2 for second, etc.)
    """
    # Get current process ID
    current_pid = os.getpid()
    
    # Get current window position
    def callback(hwnd, position):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid == current_pid:
                rect = win32gui.GetWindowRect(hwnd)
                position.extend([rect[0], rect[1]])
    
    position = []
    win32gui.EnumWindows(callback, position)
    
    if not position:
        return None
        
    window_x, window_y = position[0], position[1]
    
    # Find which monitor contains the window
    for i, monitor in enumerate(get_monitors()):
        if (monitor.x <= window_x < monitor.x + monitor.width and
            monitor.y <= window_y < monitor.y + monitor.height):
            return i + 1
            
    return 1  # Default to first display if not found



# get screen running .exe
def getDisplay(process_name=None):

    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            
            # Get process ID and name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                proc_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_name = "Unknown"
                
            # Check if window matches criteria
            if (process_name and process_name.lower() == proc_name.lower()):
                rect = win32gui.GetWindowRect(hwnd)
                windows.append({
                    'handle': hwnd,
                    'title': title,
                    'process': proc_name,
                    'rect': rect,
                    'position': (rect[0], rect[1])
                })
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    if not windows:
        return None
        
    # Get monitor information
    monitors = get_monitors()
    
    # Find which monitor contains the window
    for window in windows:
        window_x, window_y = window['position']
        
        for i, monitor in enumerate(monitors):
            if (monitor.x <= window_x < monitor.x + monitor.width and
                monitor.y <= window_y < monitor.y + monitor.height):
                ret = i + 1
                window['display'] = {
                    'number': i + 1,
                    'resolution': f"{monitor.width}x{monitor.height}",
                    'position': (monitor.x, monitor.y),
                    'is_primary': monitor.is_primary
                }
                return ret
                
    return ret



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



# make sure updated config variables are correct
def enforceSellConfig() -> bool: # ret True/False correct config
    #relaod config
    importlib.reload(config)
    def boundsCheck(val,int1,int2):
        if val < int1 or val > int2:
            return False
        else:
            return True

    #check each instance and bounds
    check = config.sellMethod
    if not boundsCheck(check,1,3): return False
    if not isinstance(check,int): return False
    
    check = config.sellWidth
    if not boundsCheck(check,1,12): return False
    if not isinstance(check,int): return False
        
    check = config.sellHeight
    if not boundsCheck(check,1,20): return False
    if not isinstance(check,int): return False
        
    check = config.undercutValue
    if isinstance(check,int): 
        if not boundsCheck(check,0,99): return False
    if isinstance(check,float):
        if not boundsCheck(check,.01,.99): return False

    #all checks pass
    return True 



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
    txt = pytesseract.image_to_string('debug/itemSlot.png',config="--psm 6")
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



def logGui(txt,color='black',printEnd="\n"):
    #Append ^ for gui newline
    if printEnd == "\n":
        txt = txt + "^"
    elif printEnd == " ":
        txt = txt + " "
    if color == 'black' and config.darkMode:
        color = 'white'
    print(f"<span style='color: {color};'>{txt}</span>", end=printEnd)
 



#find if text is clear in item attr search on market
def clearAttrSearch():
    ss = pyautogui.screenshot(region=[config.xAttribute-103,config.yAttribute+22,64,32])
    data = ss.getdata()

    for item in data:
        if (item[2] >= 230):
            pyautogui.press('backspace')
            return



# Return location and santize ImageNotFound error
def locateOnScreen(img,region=config.getScreenRegion,grayscale=False,confidence=0.99):
    logger.debug(f"Searching for Image... @ coords {region[0]}  {region[1]}  {region[2]}  {region[3]}")
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
    


# Return location of all and santize ImageNotFound error
def locateAllOnScreen(img,region=config.getScreenRegion,grayscale=False,confidence=0.99):
    logger.debug(f"Searching for Image {img}... @ coords {region[0]}  {region[1]}  {region[2]}  {region[3]}")
    strKey = isinstance(img, str)
    try:
        if strKey:
            res = pyautogui.locateAllOnScreen(f'img/{img}.png', region = region, confidence = confidence, grayscale = grayscale)
        else:
            res = pyautogui.locateAllOnScreen(img, region = region, confidence = confidence, grayscale = grayscale)
        listRes = list(res)
        return listRes
    except:
        logger.debug("Failed to find any image")
        return None
    
def locateOnImage(imgNeedle, imgHaystack, grayscale=False,confidence=0.99):
    logger.debug(f"Searching for Image {imgNeedle} in {imgHaystack}...")
    strKey = isinstance(imgNeedle, str)
    try:
        if strKey:
            res = pyautogui.locate(f'img/{imgNeedle}.png', imgHaystack, confidence = confidence, grayscale = grayscale)
        else:
            res = pyautogui.locate(imgNeedle, imgHaystack, confidence = confidence, grayscale = grayscale)
        return res
    except:
        logger.debug("Failed to find any image")
        return None
    


# Read image text and confirm the rarity
def confirmRarity(ss, img, rarity):
    left = int(img.left) 
    top = int(img.top)
    width = int(img.width)
    height = int(img.height)
    ssRegion=(left, top, width, height)

    txt = pytesseract.image_to_string(ss, config="--psm 6")
    if rarity.lower() in txt.lower():
        return 1
    else:
        return 0
    


# validate item screenshot can read size
def confirmScreenShot(ss,ssRegion):
    #confirm corners are in ss
    res = locateOnImage('topLeftCorner', ss, grayscale=False,confidence=0.82)
    res2 = locateOnImage('topRightCorner',  ss, grayscale=False,confidence=0.82)
    res3 = locateOnImage('bottomLeftCorner',  ss, grayscale=False,confidence=0.82)
    res4 = locateOnImage('bottomRightCorner', ss, grayscale=False,confidence=0.82)

    # scroll down on item to find full size while unrevealed 
    x,y = pyautogui.position()
    i = 0
    while (res == None or res4 == None) and (res2 == None or res3 == None):
        i = i + 40
        if i > 180: return False, None
        pyautogui.moveTo(x,y+i)
        ss = pyautogui.screenshot(region=ssRegion)

        if not res: res = locateOnImage('topLeftCorner', ss, grayscale=False,confidence=0.82)
        if not res2: res2 = locateOnImage('topRightCorner',  ss, grayscale=False,confidence=0.82)
        if not res3: res3 = locateOnImage('bottomLeftCorner',  ss, grayscale=False,confidence=0.82)
        if not res4: res4 = locateOnImage('bottomRightCorner', ss, grayscale=False,confidence=0.82)

    return True, ss



# Returns the rarity of the item in top left 
def getItemRarity(ss):
    ret = None

    poorDetect = locateOnImage('poor', ss)
    if poorDetect:
        if confirmRarity(ss, poorDetect,'poor'):
            ret = 'Poor'

    commonDetect = locateOnImage('common', ss)
    if commonDetect:
        if confirmRarity(ss, commonDetect,'common'):
            ret = 'Common'

    uncommonDetect = locateOnImage('uncommon',ss)
    if uncommonDetect:
        if confirmRarity(ss, uncommonDetect,'uncommon'):
            ret = 'Uncommon'

    rareDetect = locateOnImage('rare', ss)
    if rareDetect:
        if confirmRarity(ss, rareDetect,'rare'):
            ret = 'Rare'

    epicDetect = locateOnImage('epic', ss)
    if epicDetect:
        if confirmRarity(ss, epicDetect,'epic'):
            ret = 'Epic'

    legendaryDetect = locateOnImage('legendary', ss)
    if legendaryDetect:
        if confirmRarity(ss, legendaryDetect,'legendary'):
            ret = 'Legendary'

    uniqueDetect = locateOnImage('unique', ss)
    if uniqueDetect:
        if confirmRarity(ss, uniqueDetect,'unique'):
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
    txt = pytesseract.image_to_string(ss,config="--psm 6")
    txt = txt.splitlines()

    #Read for listing slots and report if any avial, and #of slots
    slots = 0
    for lines in txt:
        if lines == 'List an Item':
            slots += 1
        else:
            continue

    logger.debug(f"{slots} listings available")

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
def findItem(input_string, phrase_list, n = 1 , cutoff = 0.6):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n = n, cutoff = cutoff)
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
        time.sleep(config.sleepTime / 15)
        return True
    


# Search for item from market stash
def searchFromMarketStash() -> bool:
    logger.debug(f"Searching form market stash")
    logGui("Searching...",printEnd=" ")
    ss = pyautogui.screenshot(region=config.ssMarketItem)

    pyautogui.moveTo(config.xMarketSearchNameRairty, config.yMarketSearchNameRairty, duration=0.1) 
    pyautogui.click()

    res = confirmGameScreenChange(ss,region=config.ssMarketItem)
    if not res: return res

    pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
    time.sleep(config.sleepTime / 15)
    ss = pyautogui.screenshot(region=[config.ssMarketRollSearch[0] + 10,config.ssMarketRollSearch[1],config.ssMarketRollSearch[2],config.ssMarketRollSearch[3] + 50])
    pyautogui.click()

    pyautogui.moveTo(config.xAttrSearch + 250, config.yAttrSearch)
    time.sleep(config.sleepTime / 15)
    pyautogui.click()
    res = confirmGameScreenChange(ss,region=config.ssMarketRollSearch)
    if not res:
        pyautogui.moveTo(config.xAttrSearch + 250, config.yAttrSearch)
        time.sleep(config.sleepTime / 15)
        pyautogui.click()
        res = confirmGameScreenChange(ss,region=config.ssMarketRollSearch)

    return res




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
        time.sleep(config.sleepTime / 7.5)



# Change class 
def changeClass():
    pyautogui.moveTo(config.xPlay, config.yPlay, duration=0.1)  
    pyautogui.click()  # Perform a mouse click

    pyautogui.moveTo(config.xChangeClass,config.yChangeClass,duration=0.1)
    pyautogui.click()

    time.sleep(config.sleepTime * 3)



# moves mouse from start to end
def clickAndDrag(xStart, yStart, xEnd, yEnd, duration=0.1):
    pyautogui.moveTo(xStart, yStart)  # Move to the starting position
    pyautogui.mouseDown()        # Press and hold the mouse button
    time.sleep(0.05)              # Optional: Wait a moment for the cursor to settle
    pyautogui.moveTo(xEnd, yEnd, duration=duration)  # Drag to the destination position
    time.sleep(0.05)   
    pyautogui.mouseUp()          # Release the mouse button
    pyautogui.moveTo(config.xStashStart, config.yStashStart)



# shift + right click
def clickAndShift(x,y):
    pyautogui.keyDown('shift')   
    pyautogui.keyDown('shift')   
    pyautogui.keyDown('shift')   
    pyautogui.keyDown('shift')   
    pyautogui.keyDown('shift')   
    pyautogui.keyDown('shift')   

    pyautogui.moveTo(x,y)
    time.sleep(config.sleepTime/10)
    pyautogui.keyDown('shift')   
    time.sleep(config.sleepTime/10)
    pyautogui.click(button="right")
    time.sleep(config.sleepTime/10)
    pyautogui.keyUp('shift')        



# Main script call. Search through all stash cubes, drag item to first, and sell
def searchStash() -> bool:
    loadTextFiles()
    if not enforceSellConfig():
        logGui("Invalid Settings!!!","red")
        return False
    
    logGui("Listing Items...")

    if getAvailSlots():

        conn, cursor = database.connectDatabase()
        searchBlacklist = []

        for y in range(config.sellHeight):
            for x in range(config.sellWidth):
                
                newX = config.xStashStart + (40 * x)
                newY = config.yStashStart + (40 * y)

                skip = False
                if len(searchBlacklist):
                    for blackList in searchBlacklist:
                        if [x,y] == blackList:
                            logDebug("Skipping blacklisted item")
                            skip = True 
                    if skip: continue 
                
                logger.debug(f"Searching stash at x:{newX} y:{newY}")
                if not detectItem(newX,newY):
                    continue
                #Item found, hover and check listing slot
                pyautogui.moveTo(newX, newY)

                foundItem, success = handleItem()

                # insert into database if successful read
                if success:
                    if foundItem.rarity and foundItem.name:
                        database.insertItem(cursor,foundItem.getItemStoreDetails())     

                # if failure blacklist item slots to avoid re searching + unhover item
                else:
                    logGui(f"Item not listed",color="Red",printEnd=" ")
                    logGui("... Skipping")
                    logDebug(f"Blacklisting stash squares ...")
                    if foundItem:
                        logDebug(f"item size save:{foundItem.size[0]}{foundItem.size[1]}")
                    
                        # pyautogui.moveTo(newX,newY)
                        # pyautogui.click(button='right') 
                        time.sleep(config.sleepTime/20)
                        # pyautogui.moveTo(config.xStashStart,config.xStashStart - 100)  

                        for xBL in range(foundItem.size[0]):
                            for yBL in range(foundItem.size[1]):
                                if xBL == 0 and yBL == 0: continue
                                searchBlacklist.append([x+xBL,y+yBL])
                                logDebug(f"blacklisted {x}+{xBL},{y}+{yBL}")
            

                if not getAvailSlots(): 
                    database.closeDatabase(conn)
                    return False
                
        database.closeDatabase(conn)        
    else:
        logGui(f"No listing slots available")
        logGui(f"Clear sold listings or change characters")



# creates and returns item class from hovered item 
def getItemInfo() -> item:
    #vars
    global allItems
    global allRolls
    coords = []
    name = ""
    rolls = []
    foundName = False

    logGui("Reading item...", printEnd=" ")
 
    x, y = pyautogui.position()
    coords = [x,y]

    pyautogui.moveTo(x, y) 
    pyautogui.click() 
    time.sleep(config.sleepTime / 9)

    #check if item is on screen
    space = locateOnScreen('findItem',confidence=0.95)
    if not space: return None

    #screenshot for text & rarity
    ssRegion = (int(space[0]) - 210, int(space[1]) - 460, 535, 750)
    logGui("Getting item info...", printEnd=" ")

    ss = pyautogui.screenshot(region=ssRegion)
    sizeSS = ss

    goodSS, newSS = confirmScreenShot(ss,ssRegion)
    if goodSS: sizeSS = newSS

    #start movement thread while reading data
    searchFromStashThread = threading.Thread(target=searchFromMarketStash)
    searchFromStashThread.start()

    size = getItemSize(sizeSS)
    rarity = getItemRarity(ss)

    textCropBox = [60,150,400,520]
    ssTextCrop = ss.crop(textCropBox)
    text = pytesseract.image_to_string(ssTextCrop)

    # Read item data
    name = ""
    rolls = []
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    lines = text.splitlines()

    #iterate read text
    logGui("Storing item rolls...")
    for line in lines:
        logDebug(f"lines: {lines}")
        if not foundName:
            found = findItem(line, allItems)
            if found: 
                name = found
                foundName = True
                continue
            found = findItem(line, allRolls, cutoff = 0.9)
            if found:
                name = "NameReadError"
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

    if not rarity:
        numRolls = len(rolls)
        if numRolls < 1:
            rarity = 'common'
        elif numRolls == 1:
            rarity = 'uncommon'
        elif numRolls == 2:
            rarity = 'rare'
        elif numRolls == 3:
            rarity = 'epic'
        elif numRolls == 4:
            rarity = 'legendary'
        else:
            rarity = 'unique'

    #make item and return
    foundItem = item(name,rolls,rarity,coords,size)
    searchFromStashThread.join()
    return foundItem



# main function 
# reads hovered item info, lists on market
def handleItem() -> tuple[item, bool]: # Returns listed item / listing success

    time.sleep(config.sleepTime / 5)
    mytime = time.time()
    myItem = getItemInfo()                                                  # read item info
    
    if myItem:
        myItem.printItem()                                                  # print item to gui
        foundPrice = myItem.findPrice3()                                    # if price found, continue loop || return false
        returnMarketStash()                                                 # return market stash

        if foundPrice:
            listedSuccess = myItem.listItem()
            if listedSuccess:                                               # list item
                mytime2 = time.time()
                logGui(f"Listed item in {mytime2-mytime:0.1f} seconds")         # log time to gui
                time.sleep(config.sleepTime / 1.2)
                return myItem, True
    
        # time.sleep(config.sleepTime / 3)
        # pyautogui.moveTo(myItem.coords[0],myItem.coords[1])
        # pyautogui.click(button='right')

        return myItem, False      
    return None, False                                                      # if we fail any part of loop, return false