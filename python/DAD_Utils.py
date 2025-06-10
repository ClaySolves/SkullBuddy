import math
import re
import random
import database
import pyautogui
import pydirectinput
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
from PIL import Image
import numpy as np
from screeninfo import get_monitors
from collections import deque

logger = logging.getLogger()  # Get the root logger configured in main.py

#item class
class item():
    # constructor
    def __init__(self, name, rolls, rarity, coords, size, quantity, slotType=None, price=None, numStash=None):
        self.name = name # item name
        self.rolls = rolls # item rolls
        self.rarity = rarity # item rarity
        self.price = price # item market price
        self.listPrice = None # price item is listed at
        self.coords = coords # item location
        self.size = size # item size
        self.sold = False
        self.goodRoll = None
        self.quantity = quantity
        self.slotType = slotType
        self.destination = None
        self.numStash = numStash

        logger.debug(f"created {self.rarity} {self.name} sz {self.size} @ {self.coords}")

    
    # get item from database storing string
    def getItemStoreDatabaseInfo(self):

        rollStr = ""
        if self.quantity > 1:
            nameStr = self.name + f" x {self.quantity}"
        else:
            nameStr = self.name

        for roll in self.rolls:    
            dataStr = ",".join(str(data) for data in roll)
            rollStr += "|" + dataStr
        good = 1 if self.goodRoll else 0

        return [nameStr, self.rarity, rollStr, self.price, good]



    #get slottype
    def getSlotType(self): return self.slotType
    
    #get name
    def getName(self): return self.name
    
    #get rarity
    def getRarity(self): 
        if self.rarity:
            return self.rarity
        else:
            return "None"
    
    #get quantity
    def getQuantity(self): return self.quantity

    #get Price
    def getPrice(self): return self.price

    #get Good roll status
    def getGetRoll(self): return self.goodRoll

    #get size
    def getSize(self): return self.size

    #get coords
    def getCoords(self): return self.coords

    #get coords relative to stash
    def getStashCoords(self):
        xInt = int((self.coords[0] - 10 - config.xStashStart) / 40)
        yInt = int((self.coords[1] - 10 - config.yStashStart) / 40)
        return xInt, yInt


    def setCoords(self, x, y): self.coords = (x,y)

    def getDestination(self): return self.destination

    def setDestination(self ,xDest, yDest): self.destination = (xDest, yDest)

    def getNumStash(self): return self.numStash

    #get list of rolls
    def getRolls(self):
        retRolls = []
        for roll in self.rolls:
            retRolls.append(roll)
        return retRolls


    #Print item
    def printItem(self,newline=False):
        if self.rarity:
            self.printRarityName()

        for i , _ in enumerate(self.rolls):
            self.printRoll(i)
                
        if self.price:
            logGui(f"Price: {self.price} Gold","Gold", printEnd=" ")

        if newline: logGui("\n")


    # print item rarity and name
    def printRarityName(self,printEnd="\n"):
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
        logGui(f"{rarityPrint} {self.name}",printColor,printEnd=printEnd)


    #print item roll
    def printRoll(self,i,printEnd='\n'):
        roll = self.rolls[i]
        rollPrint = ""
        #check for % for print format
        if roll[2]:
            if int(roll[0]) == 1: rollPrint = f"+ {roll[0]}.0% {roll[1]}"
            else: rollPrint = f"+ {int(roll[0])/10:.1f}% {roll[1]}"
        else:
            rollPrint = f"+ {roll[0]} {roll[1]}"
        #check for good roll (added after price check)

        logGui(rollPrint,"DeepSkyBlue",printEnd=" ")
        if roll[3]:
            logGui(" <- Good Roll","DarkGoldenRod",printEnd=" ")
        else:
            logGui(" ",printEnd=" ")
        


    # search market gui for all item rolls
    def searchGoodRolls(self) -> bool: #True/False searched anything
        numSearch = 0
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
        time.sleep(sleepTime / 15)
        pyautogui.click()                

        pyautogui.moveTo(config.xAttribute, config.yAttribute)
        time.sleep(sleepTime / 15) 
        pyautogui.click()

        printResearch = True
        for i, roll in enumerate(self.rolls):
            if roll[3]:
                if printResearch:
                    logGui(f"Researching",printEnd=" ")
                    printResearch = False
                self.printRoll(i,printEnd=" ")
                logGui("...",printEnd=" ")

                rollSearchStr = findItem(roll[1],allRolls)
                clearAttrSearch()
                if rollSearchStr:
                    search = config.ROLL_SEARCH.get(rollSearchStr)
                    pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
                    time.sleep(sleepTime / 15) 
                    pyautogui.click()
                    pyautogui.typewrite(search, interval=0.005)

                    pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * numSearch))
                    time.sleep(sleepTime / 15)
                    pyautogui.click()
                    numSearch += 1
        logger.debug(f"Searched for {numSearch} good rolls")
        return numSearch > 0



    # search market gui for all item rolls
    def searchAllRolls(self):
        for i, roll in enumerate(self.rolls):
            if i == 0:
                pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
                time.sleep(sleepTime / 15)
                pyautogui.click()                

                pyautogui.moveTo(config.xAttribute, config.yAttribute)
                time.sleep(sleepTime / 15)
                pyautogui.click()

            rollSearchStr = findItem(roll[1],allRolls)
            clearAttrSearch()
            if rollSearchStr:
                search = config.ROLL_SEARCH.get(rollSearchStr)
                pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
                time.sleep(sleepTime / 15)
                pyautogui.click()
                pyautogui.typewrite(search, interval=0.005)

                pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i))
                time.sleep(sleepTime / 15)
                pyautogui.click()
        logger.debug(f"Searched for all rolls")



    # search market gui for indexed item roll
    def searchRoll(self,i):
        logGui(f"Researching",printEnd=" ")
        self.printRoll(i,printEnd=" ")
        logGui("...",printEnd=" ")

        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
        time.sleep(sleepTime / 15)
        pyautogui.click() 

        pyautogui.moveTo(config.xAttribute, config.yAttribute)
        time.sleep(sleepTime / 15)
        pyautogui.click()

        clearAttrSearch()
        roll = self.rolls[i]
        rollSearchStr = findItem(roll[1],allRolls)
        if rollSearchStr:
            search = config.ROLL_SEARCH.get(rollSearchStr)
            pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
            time.sleep(sleepTime / 15)
            pyautogui.click()
            pyautogui.typewrite(search, interval=0.005)

            pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect)
            time.sleep(sleepTime / 15)
            pyautogui.click()
            logger.debug(f"Searched for {search}")



    # search item name and rairty from market stash GUI
    def searchFromMarketStash(self):
        pyautogui.moveTo(self.coords[0], self.coords[1]) 
        pyautogui.click() 
        time.sleep(sleepTime / 9)

        pyautogui.moveTo(config.xMarketSearchNameRairty, config.yMarketSearchNameRairty, duration=0.1) 
        pyautogui.click()
        logger.debug(f"Searching for {self.rarity} {self.name} form market stash")
    


    #remove roll from market gui search 
    def removeSearchRoll(self,i):
        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i))
        time.sleep(sleepTime / 10)
        pyautogui.click()
        logger.debug("removed searched roll")



    #Search market for item price # Assume that View Market tab is open
    # Written for hotfix #79+
    def findPrice3(self) -> bool: #True/Flase Price Find Success
        logger.debug(f"Searching for {self.name} price")
        undercutValue = database.getConfig(cursor,'sellUndercut')
        quantity = self.quantity

        if isinstance(undercutValue,float):
            quickCheckMax = database.getConfig(cursor,'sellMax') + (database.getConfig(cursor,'sellMax') * undercutValue)
        else:
            quickCheckMax = database.getConfig(cursor,'sellMax') + undercutValue

        if isinstance(undercutValue,float):
            quickCheckMin = database.getConfig(cursor,'sellMin') + (database.getConfig(cursor,'sellMin') * undercutValue)
        else:
            quickCheckMin = database.getConfig(cursor,'sellMin') + undercutValue

        logDebug(f"Number of rolls for this lookup: {len(self.rolls)}")

        self.printRarityName()

        # algo for item with many rolls
        if (len(self.rolls) > 1):
            logger.debug(f"many roll item found")

            # record price of all rolls
            logGui("Researching all rolls ...", printEnd=" ")
            allAttrPrice = recordDisplayedPrice(False)
            if allAttrPrice:
                if allAttrPrice < quickCheckMin or allAttrPrice > quickCheckMax: return False
            
            # reset attr and get baseprice
            pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
            time.sleep(sleepTime / 15)
            pyautogui.click()

            prices = []

            logGui("Researching base price ...", printEnd=" ")
            foundPrice = recordDisplayedPrice()
            if foundPrice: prices.append(foundPrice)
            
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
            # quantity not added to roll searches to avoid bugs
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
        elif(len(self.rolls) == 1):
            logDebug(f"few roll item found")

            # record price of all rolls
            logGui("Researching roll ...", printEnd=" ")
            foundPrice = recordDisplayedPrice(False)

            # found price on all attr search, return and log
            if foundPrice:
                if foundPrice > quickCheckMax or foundPrice < quickCheckMin: return False

                logGui(f"Found ",printEnd=" ")
                if isinstance(foundPrice,int):
                    logGui(f"{foundPrice}",color="Gold",printEnd=" ")
                else:
                    logGui(f"{foundPrice}",color="Gray",printEnd=" ")
                logGui(f"for ",printEnd=" ")
                self.printRarityName()
                self.price = foundPrice * quantity
                return True

            # reset attr and get baseprice
            pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute)
            time.sleep(sleepTime / 15)
            pyautogui.click() 

            logGui("Researching base price ...", printEnd=" ")
            foundPrice = recordDisplayedPrice()

            if foundPrice:
                if foundPrice > quickCheckMax or foundPrice < quickCheckMin: return False 

                logGui(f"Found ",printEnd=" ")
                if isinstance(foundPrice,int):
                    logGui(f"{foundPrice}",color="Gold",printEnd=" ")
                else:
                    logGui(f"{foundPrice}",color="Gray",printEnd=" ")
                logGui(f"for ",printEnd=" ")
                self.printRarityName()
                self.price = foundPrice * quantity
                return True
        
            return False

        elif(len(self.rolls) == 0):
            logDebug(f"zero item found")

            # record displayed price
            logGui("Researching base price ...", printEnd=" ")
            foundPrice = recordDisplayedPrice(False)

            # found price on all attr search, return and log
            if foundPrice:
                if foundPrice > quickCheckMax or foundPrice < quickCheckMin: return False

                logGui(f"Found ",printEnd=" ")
                if isinstance(foundPrice,int):
                    logGui(f"{foundPrice}",color="Gold",printEnd=" ")
                else:
                    logGui(f"{foundPrice}",color="Gray",printEnd=" ")
                logGui(f"for ",printEnd=" ")
                self.printRarityName()
                self.price = foundPrice * quantity
                return True
        
            return False

        # this should never trigger
        else:
            logDebug('BAD ITEM READ !!!')

        logDebug('Price Read Error')
        return False



    #Moves item from starting coords to destination coords in stash. Returns status of move and end coordinates
    def moveToStash(self, xDest, yDest, stashStorageCoordDict, destStash, invStorage):
        global runOrganize
        if not runOrganize: return False

        name = self.name
        xSz, ySz = self.size
        xStart, yStart = self.coords
        xStartInt, yStartInt = self.getStashCoords()

        global currentStashSelect

        def validateCoords(i):
            return 0 <= i and i <= 19
    
        if not (validateCoords(xStartInt) and validateCoords(yStartInt) and validateCoords(xDest) and validateCoords(yDest)):
            logDebug(f"Coordinate Error on {(xStartInt, yStartInt)} , {(xDest, yDest)} for {self.getName()}")
            return False

        logDebug(f"Trying to move from {xStartInt, yStartInt} to {xDest, yDest}")

        if(xStartInt, yStartInt) == (xDest,yDest) and destStash == self.numStash: return True

        for y in range(ySz):
            for x in range(xSz):
                stashStorageCoordDict[(x + xDest, y + yDest, destStash)] = stashStorageCoordDict.pop((x + xStartInt,y + yStartInt, self.numStash))

        xDestGui = ((xDest * 40) + 10 + config.xStashStart)
        yDestGui = ((yDest * 40) + 10 + config.yStashStart)

        self.setCoords(xDestGui, yDestGui)

        if name in config.ITEM_MOVES_BOTTOM_RIGHT_CORNER:
            xDestGui += 40 * (xSz - 1)
            yDestGui += 40 * (ySz - 1)

        if currentStashSelect != self.numStash:
            selectStash(self.numStash)
        
        logGui(f"Moving ", printEnd=" ")
        self.printRarityName(printEnd=" ")
        logGui(f"Moving {name} from {xStartInt, yStartInt} to {xDest, yDest}")

        if self.numStash != destStash:
            xSz, ySz = self.size

            clickAndShift(xStart, yStart)
            newStartCoords = invStorage.get((xSz,ySz),None)
            if not newStartCoords: 
                logDebug(f"Error getting inv Stash coords for {x,y} with {self.size}")
                return False
            
            selectStash(destStash)
            clickAndDrag(newStartCoords[0], newStartCoords[1], xDestGui, yDestGui, duration=sleepTime/7)
        else:
            clickAndDrag(xStart, yStart, xDestGui, yDestGui, duration=sleepTime/7)

        currentStashSelect = destStash
        self.numStash = destStash
        
        return True
    


    #confirms item should be listed for found price:
    def confirmPrice(self) -> bool: #True/False is good to list
        rarity = self.rarity
        size = self.size[0] * self.size[1]
        if rarity: rarity = rarity.lower()
        priceCalc = None
        useRolls = False
        numRolls = len(self.rolls)
        compPrice = self.listPrice

        if compPrice < database.getConfig(cursor,'sellMin') or compPrice > database.getConfig(cursor,'sellMax'):
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

        if compPrice - 15 > size * priceCalc: return True
        
        logger.debug(f"{rarity} {self.name} not listed at {compPrice}, vendor instead")
        logGui("Vendor Item for Better Price!",color="Gold")
        return False
        


    #Lists item for found price
    def listItem(self) -> bool: # True/False Listing Success
        price = self.price
        if not price: 
            logGui("No Price Found, Can't List")
            return False

        undercut = database.getConfig(cursor,'sellUndercut')

        logger.debug(f"using {undercut} undercut value and {self.quantity} quantity")

        if undercut < 0:
            finalPrice = price - 1
        else:
            if isinstance(undercut,float):
                finalPrice = int(price - (price * undercut))
                finalPrice = int(finalPrice)
            else:
                finalPrice = price - int(undercut)

        logger.debug(f"{finalPrice} found to list")

        self.listPrice = finalPrice

        if self.confirmPrice():
            pyautogui.moveTo(self.coords[0], self.coords[1], duration=0.1) 
            pyautogui.click()
            time.sleep(sleepTime / 3)

            pyautogui.moveTo(config.xSellingPrice, config.ySellingPrice, duration=0.1) 
            pyautogui.click()
            logGui(f"Listing item for {finalPrice}","Gold")
            pyautogui.typewrite(str(finalPrice), interval=0.03)

            pyautogui.moveTo(config.xCreateListing, config.yCreateListing, duration=0.1) 
            pyautogui.click()

            pyautogui.moveTo(config.xConfirmListing, config.yConfirmListing, duration=0.1) 
            pyautogui.click()
            logger.debug(f"Listed for {finalPrice}")
            return True

        logger.debug(f"CANNOT LIST AN ITEM WITH NO/INVALID PRICE!")
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
        time.sleep(sleepTime / 150)
        ss = pyautogui.screenshot(region=config.ssMarketSearch)
        #ss.save(f"debug/preSearchSave.png")
        changed = confirmGameScreenChange(ss,config.ssMarketSearch)

        if not changed: 
            logger.debug(f"No Gold Load Detected...")

    priceListed = readPrices()
    priceQuant = readPrices(region=config.ssGoldQuantity)

    foundPrices = None
    if priceListed and priceQuant:
        foundPrices = priceListed + priceQuant
        foundPrices.sort()
    elif priceListed:
        foundPrices = priceListed
    elif priceQuant:
        foundPrices = priceQuant

    if foundPrices:
        logDebug(f"Calcing item price with {foundPrices}")
        retPrice = calcItemPrice(foundPrices,database.getConfig(cursor,'sellMethod'))
        logGui(f"Found ",printEnd=" ")
        if isinstance(retPrice,int):
            logGui(f"{retPrice}",color="Gold",printEnd=" ")
        else:
            logGui(f"{retPrice}",color="Gray",printEnd=" ")
        logGui(f"...")
    else:
        logDebug(f"no price found ...")
        return None
    
    logDebug(f"Found price {retPrice}")
    return retPrice



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
        time.sleep(sleepTime / 30)
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
    time.sleep(sleepTime / 7.5)



# read displayed prices from market
def readPrices(region=config.ssGold) -> list: # return list of prices
    ss = pyautogui.screenshot(region=region)
    data = ss.getdata()
    newData = []
    retPrices = []

    for item in data:
        if (item[0] >= 110 or item[1] >= 110):
            newData.append(item)
        else:
            newData.append((0,0,0))

    ss.putdata(newData)
    #ss.save("debug/finalPrice.png")
    numConfig = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789x.'
    txt = pytesseract.image_to_string(ss,config=numConfig)

    #Filter read text for ',' reads and quantitiy reads
    if 'x' in txt:
        prices = []
        pricesX = txt.split()
        for price in pricesX:
            prices.append(price.split('x')[0])
    else:
        prices = txt.split()

    if prices:
        for i, price in enumerate(prices):

            #for reads like 1,249.3, pytess reads as 1.249.3. Remove first n-1 . char
            dotCount = price.count('.')
            if dotCount > 1:
                dotCount = dotCount - 1
            price = price.replace(".","",dotCount)

            #clean price to float or int for undercut val
            try:
                priceAdd = int(float(price))
                retPrices.append(priceAdd)
            except:
                logger.debug("Value error reading price")

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
# Depricated
def getItemSize(ss) -> list:
    res = locateOnImage('topLeftCorner', ss, grayscale=False,confidence=0.82)
    res4 = locateOnImage('bottomRightCorner', ss, grayscale=False,confidence=0.82)
    res2 = None
    res3 = None

    if not (res4 and res):
        res2 = locateOnImage('topRightCorner', ss, grayscale=False,confidence=0.82)
        res3 = locateOnImage('bottomLeftCorner', ss, grayscale=False,confidence=0.82)

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
    
    res = locateOnImage('topLeftCornerRed', ss, grayscale=False,confidence=0.82)
    res4 = locateOnImage('bottomRightCornerRed', ss, grayscale=False,confidence=0.82)
    res2 = None
    res3 = None
    
    if not (res4 and res):
        res2 = locateOnImage('topRightCornerRed', ss, grayscale=False,confidence=0.82)
        res3 = locateOnImage('bottomLeftCornerRed', ss, grayscale=False,confidence=0.82)

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
    global slotTypes
    global cursor
    global conn
    global sleepTime
    global darkMode

    global runOrganize
    global currentStashSelect

    conn, cursor = database.connectDatabase()
    logDebug(database.printConfig(cursor)[0])
   
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

    sleepTime = database.getConfig(cursor,'sleepTime')
    darkMode = database.getConfig(cursor,'darkMode')
    slotTypes = list(config.SLOTTYPE_ORDER.keys())

    currentStashSelect = None
    runOrganize = True



#Find stash pixel val for detect item 
def getStashPixelVal():
    listPxVal = []
    ss = pyautogui.screenshot()

    for y in range(20):
        for x in range(12):
            newX = config.xStashStart + (40 * x)
            newY = config.yStashStart + (40 * y)

            cropRegion = [newX,newY,newX+20,newY+20]
            ssFiltered = ss.crop(cropRegion)
            ssFiltered = ssFiltered.convert("RGB")

            w, h = ssFiltered.size
            data = ssFiltered.getdata()
            total = 0

            for item in data:
                total += sum(item)
            div = w*h
            res = math.floor(total/div)

            listPxVal.append(res)

    listPxVal.sort()
    avgList = listPxVal[:3]
    val = int(sum(avgList) / len(avgList))

    return val + 30


#Minimize Window
def minimizeSelf():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)



#restore window
def restoreSelf():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)



def getCurrentDisplay():
    # Get current process ID
    currentPid = os.getpid()
    
    # Get current window position
    def callback(hwnd, position):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid == currentPid:
                rect = win32gui.GetWindowRect(hwnd)
                position.extend([rect[0], rect[1]])
    
    position = []
    win32gui.EnumWindows(callback, position)
    
    if not position:
        return None
        
    windowX, windowY = position[0], position[1]
    
    # Find which monitor contains the window
    for i, monitor in enumerate(get_monitors()):
        if (monitor.x <= windowX < monitor.x + monitor.width and
            monitor.y <= windowY < monitor.y + monitor.height):
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
                procName = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                procName = "Unknown"
                
            # Check if window matches criteria
            if (process_name and process_name.lower() == procName.lower()):
                rect = win32gui.GetWindowRect(hwnd)
                windows.append({
                    'handle': hwnd,
                    'title': title,
                    'process': procName,
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
def enforceConfig() -> bool: # ret True/False correct config
    #relaod config
    importlib.reload(config)

    #bounds check function
    def boundsCheck(val,int1,int2):
        if val:
            if val < int1 or val > int2:
                return False
            else:
                return True
        else:
            return False
        
    #bool for set pixelval
    setPixelVal = True

    #check each instance and bounds
    check = database.getConfig(cursor,'sleepTime')
    if not boundsCheck(check,0.3,5.0): return False, 'App Speed'
    if not isinstance(check,float): return False, 'App Speed'

    check = database.getConfig(cursor,'sellMethod')
    if not boundsCheck(check,1,3): return False, 'Sell Method Selection'
    if not isinstance(check,int): return False, 'Sell Method Selection'
    
    check = database.getConfig(cursor,'sellWidth')
    if not boundsCheck(check,1,12): return False, 'Sell Width'
    if not isinstance(check,int): return False, 'Sell Width'
        
    check = database.getConfig(cursor,'sellHeight')
    if not boundsCheck(check,1,20): return False, 'Sell Height'
    if not isinstance(check,int): return False, 'Sell Height'
        
    check = database.getConfig(cursor,'sellUndercut')
    if check == int(check): check = int(check)
    if isinstance(check,int): 
        if not boundsCheck(check,0,99): return False, 'Undercut Value'
    if isinstance(check,float):
        if not boundsCheck(check,.01,.99): return False, 'Undercut Value'

    #check && assign for stashPixelVal
    pixelVal = getStashPixelVal()
    logDebug(f"pixelVal: {pixelVal}")
    if setPixelVal or database.getConfig(cursor,'pixelValue') == None:
        database.setConfig(cursor,'pixelValue',pixelVal)


    #all checks pass
    return True, " "



#Sends all treasure to expressman
#broken as of 4/26/25 | adjust for getItemSlotType() rework
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
def getItemSlotType(ssStash,location):
    xRegion = int(location[0])
    yRegion = int(location[1])
    ssRegion = (xRegion, yRegion, xRegion + 250, yRegion + 25)

    ssSlotType = ssStash.crop(ssRegion)

    txt = pytesseract.image_to_string(ssSlotType,config="--psm 6")

    txtRemove = "Slot Type"
    try:
        keywordIndex = txt.index(txtRemove) + len(txtRemove)
        ret = txt[keywordIndex:].lstrip()
        finalRet = ''.join(char for char in ret if char.isalpha())
        finalFinalRet = findItem(finalRet, slotTypes, cutoff=0.8)
        return finalFinalRet
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
    if darkMode and color == 'black':
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
        logger.debug(f"Failed to find image {img}")
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
        logger.debug(f"Failed to find any image {img}")
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
        logger.debug(f"Failed to find any image {imgNeedle} in image {imgHaystack}")
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
def getItemRarity(ss,txt):
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
        return ret

    txt = txt.lower()

    if 'poor' in txt:
        ret = 'Poor'

    if 'uncommon' in txt:
        ret = 'Uncommon'

    if 'common' in txt:
        ret = 'Common'

    if 'rare' in txt:
        ret = 'Rare'

    if 'epic' in txt:
        ret = 'Epic'

    if 'legendary' in txt:
        ret = 'Legendary'

    if 'unique' in txt:
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
    pixelVal = database.getConfig(cursor,'pixelValue')

    w, h = ss.size
    data = ss.getdata()
    total = 0
    ret = False
    for item in data:
        total += sum(item)
    div = w*h
    res = math.floor(total/div)

    logger.debug(f"Pixel val for x:{x} y:{y} {res}")
    if res > pixelVal:
        ret = True

    if ret:
        logger.debug("Item detected")
    else:
        logger.debug(f"No item detected: {str(res)} < {pixelVal}")
    return ret



# Get the availible listing slots
def getAvailSlots():
    #get current listing page
    ss = pyautogui.screenshot(region=config.ssGetListingPageNum)
    listConfig = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789/'
    txtList = pytesseract.image_to_string(ss,config=listConfig)
    if txtList == None or txtList == '': return 0
    currListPage = int(txtList.split('/')[0]) - 1

    #Take screenshot and sanitize for read text for all listing pages
    for i in range(currListPage, 3):
        #logic for checking locked listings on 3rd page
        ssRegion = config.ssGetListings
        if i == 2:
            ssRegion[2] += 250

        ss = pyautogui.screenshot(region=ssRegion)
        txt = pytesseract.image_to_string(ss,config="--psm 6")

        if "locked" in txt.lower():
            break

        txt = txt.splitlines()

        #Read for listing slots and report if any avial, and #of slots. Else go next page
        slots = 0
        for lines in txt:
            if 'list an item' in lines.lower():
                slots += 1
            else:
                continue

        if slots > 0:
            logger.debug(f"{slots} listings available on listing page {i}")
            return slots
        
        else:
            ssChange = pyautogui.screenshot(region=config.ssGetListingPageNum)
            logger.debug(f"no listings slots on listing page {i}")
            pyautogui.moveTo(config.xListingRight,config.yListingRight)
            pyautogui.click()
            confirmGameScreenChange(ssChange,config.ssGetListingPageNum)
                

    return 0



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
    if closest_match: logger.debug(f"Found: {closest_match}")
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
        time.sleep(sleepTime / 15)
        return True
    


# Search for item from market stash
def searchFromMarketStash() -> bool:
    logger.debug(f"Searching form market stash")
    logGui("Searching...",printEnd=" ")
    ss = pyautogui.screenshot(region=config.ssMarketItem)

    pyautogui.moveTo(config.xMarketSearchNameRairty, config.yMarketSearchNameRairty, duration=0.1) 
    pyautogui.click()

    res = confirmGameScreenChange(ss,region=config.ssMarketItem)

    #remove search overlay by looking for price column to gather price
    ss = pyautogui.screenshot(region=config.ssPriceColumnRead)
    priceRead = pytesseract.image_to_string(ss,config="--psm 6").lower()    
    for x in range(5):
        pyautogui.click()
        ss = pyautogui.screenshot(region=config.ssPriceColumnRead)
        priceRead = pytesseract.image_to_string(ss,config="--psm 6").lower()  
        if "price" in priceRead: 
            break

    for x in range(10):
        ssBuy = pyautogui.screenshot(region=config.ssBuyRead)
        buyRead = pytesseract.image_to_string(ssBuy,config="--psm 6").lower() 
        if 'yours' in buyRead or 'buy' in buyRead:
            break

    logGui("Search completed.",printEnd=" ")
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
    pyautogui.moveTo(xChar, yChar, duration=0.1)  
    pyautogui.click()  

    xLobby, yLobby = 960, 1000  
    pyautogui.moveTo(xLobby, yLobby, duration=0.1) 
    pyautogui.click()  
    
    while not locateOnScreen('verifyMainScreen', region=(0,0,300,300)):
        time.sleep(sleepTime / 7.5)



# Change class 
def changeClass():
    pyautogui.moveTo(config.xPlay, config.yPlay, duration=0.1)  
    pyautogui.click()  # Perform a mouse click

    pyautogui.moveTo(config.xChangeClass,config.yChangeClass,duration=0.1)
    pyautogui.click()

    time.sleep(sleepTime * 3)



# moves mouse from start to end
def clickAndDrag(xStart, yStart, xEnd, yEnd, duration=0.1):
    pyautogui.moveTo(xStart, yStart)  
    pyautogui.mouseDown() 
    time.sleep(duration/25)      
    pyautogui.moveTo(xEnd, yEnd, duration=duration/1) 
    time.sleep(duration/25)   
    pyautogui.mouseUp()          



# shift + right click. For whatever reason pyautogui shift click combo doesn't work, so pydirectinput is used
def clickAndShift(x,y):
    pyautogui.moveTo(x,y)
    pydirectinput.keyDown('shift')   
    pydirectinput.rightClick()
    pydirectinput.keyUp('shift')



def stopScript():
    global runSearch
    logDebug("Turning runSearch FALSE")
    runSearch = False

    global runOrganize
    logDebug("Turning runOrganize FALSE")
    runOrganize = False


# Main script call. Search through all stash cubes, drag item to first, and sell
def searchStash() -> bool:
    global runSearch
    runSearch = True

    loadTextFiles()
    check, err = enforceConfig()
    if not check:
        logGui("Invalid Settings!!!","red")
        logGui(f"Check {err} value")
        database.closeDatabase(conn) 
        return False
        
    logGui("Listing Items...")

    if getAvailSlots():

        searchBlacklist = []
        for y in range(database.getConfig(cursor,'sellHeight')):
            if not runSearch: break
            for x in range(database.getConfig(cursor,'sellWidth')):
                if runSearch:
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
                            database.insertItem(cursor,foundItem.getItemStoreDatabaseInfo())     

                    # if failure blacklist item slots to avoid re searching + unhover item
                    else:
                        logGui(f"Item not listed",color="Gray",printEnd=" ")
                        logGui("... Skipping")
                        logDebug(f"Blacklisting stash squares ...")
                        if foundItem:
                            logDebug(f"item size save:{foundItem.size[0]}{foundItem.size[1]}")
                        
                            # pyautogui.moveTo(newX,newY)
                            # pyautogui.click(button='right') 
                            time.sleep(sleepTime/20)
                            # pyautogui.moveTo(config.xStashStart,config.xStashStart - 100)  

                            for xBL in range(foundItem.size[0]):
                                for yBL in range(foundItem.size[1]):
                                    if xBL == 0 and yBL == 0: continue
                                    searchBlacklist.append([x+xBL,y+yBL])
                                    logDebug(f"blacklisted {x}+{xBL},{y}+{yBL}")
                

                    if not getAvailSlots(): 
                        database.closeDatabase(conn)
                        return False
                    

                else:
                    logGui("Script Terminated!",color = 'red')
                    break

        database.closeDatabase(conn)        
    else:
        database.closeDatabase(conn)  
        logGui(f"No listing slots available","red")
        logGui(f"Clear sold listings or change characters")



# creates and returns item class from hovered item 
def getItemInfo() -> item:
    #vars
    global allItems
    global allRolls
    coords = []
    rolls = []
    foundName = False

    logGui("Reading item...", printEnd=" ")
 
    x, y = pyautogui.position()
    coords = [x,y]

    pyautogui.moveTo(x, y) 
    pyautogui.click() 
    time.sleep(sleepTime / 9)

    #check if item is on screen
    space = locateOnScreen('slotType2',grayscale=False,confidence=0.90)
    if not space: return None

    #screenshot for quantity
    ss = pyautogui.screenshot(region=config.ssQuantity)
    numConfig = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    quanRead = pytesseract.image_to_string(ss,config=numConfig)
    if quanRead:
        quantity = int(quanRead)
    else:
        quantity = 1
        logDebug("Error finding quanittiy ,setting to 1")

    #screenshot for text & rarity
    ssRegion = (int(space[0]) - 150, int(space[1]) - 410, 535, 800)
    logGui("Getting item info...", printEnd=" ")
    ss = pyautogui.screenshot(region=ssRegion)

    #start movement thread while reading data
    searchFromStashThread = threading.Thread(target=searchFromMarketStash)
    searchFromStashThread.start()

    textCropBox = [60,0,400,600]
    ssTextCrop = ss.crop(textCropBox)
    text = pytesseract.image_to_string(ssTextCrop,config="--psm 6")

    rarity = getItemRarity(ss,text)

    #ssTextCrop.save(f"debug/itemSStext_{x}_{y}.png")

    # Read item data
    name = ""
    rolls = []
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    lines = text.splitlines()

    #iterate read text
    logGui("Storing item rolls...", printEnd=" ")
    for line in lines:
        logDebug(f"line: {line}")
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

    # lookup size
    size = config.ITEM_SIZE.get(name)
    if size == None: 
        logDebug(f"NoneSizeFound")
        size = (1,1)

    #make item and return
    foundItem = item(name,rolls,rarity,coords,size,quantity)
    logGui("Item read completed.",printEnd=" ")
    searchFromStashThread.join()
    logGui(" ")
    return foundItem



#Get item name and size quickly
def getItemNameSizeSpace(ssStash) -> item:
    #vars
    global allItems 
    name = None
    size = None

    #check if item is on screen for bounds
    space = locateOnImage('slotType2',ssStash,grayscale=False,confidence=0.90)
    if space == None: space = (config.xStashStart, config.yStashStart)

    #screenshot for text & rarity
    xRegion = int(space[0]) - 150
    yRegion = int(space[1]) - 410
    ssRegion = (xRegion, yRegion, xRegion + 535, yRegion + 800)
    ss = ssStash.crop(ssRegion)

    def filterText(ss):
        textCropBox = [60,0,400,600]
        ssTextCrop = ss.crop(textCropBox)
        ssTextCrop = ssTextCrop.convert('L') 
        text = pytesseract.image_to_string(ssTextCrop,config="--psm 6")

        # Read item data
        text = ''.join(char for char in text if char.isalnum() or char.isspace() or char == '(' or char == ')')
        lines = text.splitlines()

        #Search for name
        for line in lines:
            if '(' in line and ')' in line:
                line = line.split('(')[0]
            found = findItem(line, allItems, cutoff=0.7)
            if found: 
                return found, lines
            
        return None, lines

    name, lines = filterText(ss)
    
    retryCount = 0
    while name is None and retryCount < 4:
        w,l = ss.size
        newCrop = [0, 50 * retryCount, w, l-(50 * retryCount)]
        ss = ss.crop(newCrop)
        name, lines = filterText(ss)
        retryCount += 1


    if name:
        # lookup size
        size = config.ITEM_SIZE.get(name)
        if size == None: 
            logDebug(f"NoneSizeFound for {name}")
            size = (1,1)
    else:
        logDebug(f"Could not f1nd name in\n{lines}" )

    return name, size, space



#Get additional information needed for item sort
def finalizeStashItem(ssStash, name, size, space, x, y, numStash) -> item:
    #vars
    global allItems 
    coords = [x,y]

    slotType = getItemSlotType(ssStash,space)

    #screenshot for text & rarity
    xRegion = int(space[0]) - 150
    yRegion = int(space[1]) - 410
    ssRegion = (xRegion, yRegion, xRegion + 535, yRegion + 800)
    ss = ssStash.crop(ssRegion)

    textCropBox = [60,0,400,600]
    ssTextCrop = ss.crop(textCropBox)
    text = pytesseract.image_to_string(ssTextCrop,config="--psm 6")

    rarity = getItemRarity(ss,text)

    #make item and return
    foundItem = item(name, [], rarity, coords, size, 1, slotType=slotType, numStash=numStash)

    return foundItem



# main function 
# reads hovered item info, lists on market
def handleItem() -> tuple[item, bool]: # Returns listed item / listing success

    time.sleep(sleepTime / 5)
    mytime = time.time()
    myItem = getItemInfo()                                               
    
    #if we successfully read an item, find a price and list it on the market
    if myItem:
        logGui("Searching Market For",printEnd=" ")
        myItem.printItem()                                                 
        foundPrice = myItem.findPrice3()                                
        returnMarketStash()                                              

        if foundPrice:
            listedSuccess = myItem.listItem()
            if listedSuccess:                                             
                mytime2 = time.time()
                logGui(f"Listed item in {mytime2-mytime:0.1f} seconds")        
                time.sleep(sleepTime / 1.2)
                return myItem, True
    
        return myItem, False      
    return None, False                                                 

#Search current displayed stash
def organizeStash() -> bool: # True/False successful sort
    
    loadTextFiles()
    global runOrganize

    runOrganize = True


    check, err = enforceConfig()
    if not check:
        logGui("Invalid Settings!!!","red")
        logGui(f"Check {err} value")
        database.closeDatabase(conn) 
        return False

    global currentStashSelect
    time1=time.time()

    def getStash(val):
        if val == 6:
            return "Shared Stash"

        if val == 7:
            return "DLC Stash"
        
        return f"{val + 1}"

    # get config vars for single or multi stash sort
    organizeMethod = database.getConfig(cursor, "organizeMethod")
    flag = database.getConfig(cursor, "organizeStashes")
    stashFlags = []
    if organizeMethod == 2:
        for i in range(8):
            if bool(flag & (1 << i)):
                stashFlags.append(i)
    else:
        stashFlags.append(1)

    if organizeMethod == 1:
        logGui("Organizing Selected Stash...")
    else:
        logGui(f"Organizing Stash",printEnd=" ")
        numFlags = len(stashFlags)
        if numFlags == 1:
            logGui(f"{getStash(stashFlags[0])}")

        elif numFlags == 2:
            logGui(f"{getStash(stashFlags[0])} and {getStash(stashFlags[1])}")

        else:
            for i, val in enumerate(stashFlags):
                if i == len(stashFlags) - 1:
                    logGui(f"and {getStash(val)}")
                    break

                logGui(f"{getStash(val)}", printEnd=", ")

    logDebug(f"Organizing Stash with organize method {organizeMethod} and {stashFlags}")

    #check to make sure we're on stash page
    ssCheckStashPage = pyautogui.screenshot(region=config.ssConfirmStash)
    txt = pytesseract.image_to_string(ssCheckStashPage,config="--psm 6")
    if 'stash' not in txt.lower():
        logGui("Stash Not Detected","red")
        logGui("Navigate to the stash you want to organize and try again")
        logger.error("Organize stash called but no stash page detected")
        database.closeDatabase(conn)
        return False

    #var setup
    numReadStashes = len(stashFlags) if organizeMethod == 2 else 1

    itemDetectedStashSquares = []
    stashFrequency = {}
    ssQueue = deque()
    itemQueue = deque()
    stashStorage = [[None for _ in range(12)] for _ in range(20 * numReadStashes)]
    stashQuickEmptyCoordSet = set()
    itemsToSort = []


    #look for items to sort in stash ss
    for i in range(numReadStashes-1,-1,-1):

        if organizeMethod == 2:
            selectStash(stashFlags[i])

        ssGetStash = pyautogui.screenshot(region=config.ssEntireStash)
        for y in range(20):
            for x in range(12):
                newX = 10 + (40 * x)
                newY = 10 + (40 * y)
                itemDetected = detectItem2(ssGetStash,newX,newY)

                if itemDetected:
                    # if organizeMethod == 2:
                    foundItem = [config.xStashStart + newX, config.yStashStart + newY,stashFlags[i]]

                    # else:
                    #     foundItem = [config.xStashStart + newX, config.yStashStart + newY,stashFlags[i]]
                    itemDetectedStashSquares.append(foundItem)
                else:
                    stashQuickEmptyCoordSet.add((x,y))

    #if no items return None
    if not itemDetectedStashSquares:
        logGui("Yeah let me just organize this empty stash... Bro are you dumb or something?")
        database.closeDatabase(conn)
        return None

    #create workers to scrape screenshots
    def ssWorker():
        firstTime = True
        if not runOrganize: return False

        while(ssQueue or itemQueue or firstTime):
            if not runOrganize: return False
            firstTime = False
            logDebug("Thread working ssQueue")
            for _ in range(50):
                #If a screenshot is added to the queue, a worker will take it and harvest info
                
                while ssQueue:
                    queueData = ssQueue.popleft()
                    x = int ((queueData[1] - (10 + config.xStashStart) ) / 40)
                    y = int ((queueData[2] - (10 + config.yStashStart) ) / 40) + (20 * stashFlags.index(queueData[3]))

                    #read necessary info for size and name
                    foundSortName, foundSortSize, foundSortSpace = getItemNameSizeSpace(queueData[0])

                    # record frequency of items, if we have same frequency as size send item to be completed
                    if foundSortName is not None:
                        stashStorage[y][x] = foundSortName

                        if foundSortName not in stashFrequency:
                            stashFrequency[foundSortName] = 1
                        else:
                            stashFrequency[foundSortName] += 1

                        itemReady = True
                        if stashFrequency[foundSortName] >= (foundSortSize[0] * foundSortSize[1]):
                            
                            for y2 in range(foundSortSize[1]):
                                if y-y2 < 0: 
                                    itemReady = False
                                    break
                                for x2 in range(foundSortSize[0]):
                                    if x-x2 < 0: 
                                        itemReady = False
                                        break
                                    if stashStorage[y-y2][x-x2] != foundSortName:
                                        itemReady = False
                                
                        else:
                            itemReady = False

                        #if item is sent to queue, adjust stashStorage and frequency
                        if itemReady:
                            for y2 in range(foundSortSize[1]):
                                    for x2 in range(foundSortSize[0]):
                                        stashStorage[y-y2][x-x2] = foundSortName + "_Done"
                                        stashFrequency[foundSortName] -= 1

                            logDebug(f"sending {foundSortName} to item queue")
                            xCoord = queueData[1] - (40 * (foundSortSize[0] - 1))
                            yCoord = queueData[2] - (40 * (foundSortSize[1] - 1))

                            itemQueue.append((queueData[0], foundSortName, foundSortSize, foundSortSpace, xCoord, yCoord, queueData[3]))

                time.sleep(0.05)

            logDebug("Thread working itemQueue")
            # Once the screenshot queue is empty, work on items to be complted
            for _ in range(50):
                while(itemQueue):
                    if not runOrganize: return False

                    item = itemQueue.popleft()
                    finalItem = finalizeStashItem(item[0],item[1],item[2],item[3],item[4],item[5], item[6])
                    logGui("Found ", printEnd=" ")
                    finalItem.printRarityName(printEnd=" ")
                    logGui(f"at coords {finalItem.getStashCoords()} & stash {finalItem.getNumStash()}")

                    itemsToSort.append(finalItem)

                time.sleep(0.05)

    #start worker threads
    numWorkers = 4 if sleepTime >= 1.3 else 6
    logDebug(f"Using numworkers: {numWorkers}")

    threads = []
    for _ in range(numWorkers):
        t = threading.Thread(target=ssWorker)
        t.start()
        threads.append(t)



    #store screenshots of each item square
    if organizeMethod == 2: prevStash = None
    for n, item in enumerate(itemDetectedStashSquares):
        if not runOrganize: 
            database.closeDatabase(conn)
            return False

        currStash = item[2]
        if organizeMethod == 2 and prevStash != currStash:
            selectStash(currStash)
            time.sleep(sleepTime/10)  

        pyautogui.moveTo(item[0],item[1])
        ss = pyautogui.screenshot()
        ssStore = (ss,item[0],item[1],currStash)
        ssQueue.append(ssStore)
        prevStash = currStash

    #Wait for workers
    for thread in threads:
        thread.join()

    logDebug(f"Length of StashFrequency {len(stashFrequency.items())}")
    for misfets in stashFrequency.items():
        logDebug(misfets)
        print(misfets)

    for row in stashStorage:
        logDebug(row)

    print(runOrganize)

    # Sort items into order for new stash
    itemSortPlaceOrder = sorted(itemsToSort, key=lambda item: (config.SLOTTYPE_ORDER.get(item.getSlotType() , -1), -item.getSize()[1], 
                                                                config.RARITY_ORDER.get(item.getRarity().lower(), -1), item.getName()))

    logGui(f"Found {len(itemSortPlaceOrder)} to organize")

    #new stash creation vars
    slotTypeSize = {}
    slotTypeMax = {}
    newStashBlocks = {}
    stashStorageCoordDict = {}
    newStash = [[None for _ in range(12)] for _ in range(20)]

    #break sorted items by slotType for placement
    for item in itemSortPlaceOrder:        
        xStorage,yStorage = item.getCoords()
        xSize, ySize = item.getSize()
        xStashCoord = int((xStorage - 10 - config.xStashStart) / 40)
        yStashCoord = int((yStorage - 10 - config.yStashStart) / 40)
        for x in range(xStashCoord, xStashCoord + xSize):
            for y in range(yStashCoord, yStashCoord + ySize):
                stashStorageCoordDict[(x,y,item.numStash)] = (item)

        if item.getSlotType() in slotTypeSize:
            slotTypeSize[item.getSlotType()].append(item)
        else:
            slotTypeSize[item.getSlotType()] = [item]

    logDebug(f"Testing stashStorageCoordDict:")
    for itemCoordDict in stashStorageCoordDict.items():
        logDebug((itemCoordDict[0],itemCoordDict[1].getName()))

    #get size allocation for new stash region for each slot type
    for items in slotTypeSize.items():
        slotTypeMax[items[0]] = max(items[1], key = lambda x: x.getSize()[1])

    #reserve space and construct each stash block
    newItemCoords = {}
    coordsAddYSave = 0
    blockCache = {}
    for n, regions in enumerate(slotTypeMax.items()):
        newStashBlockHeight = regions[1].getSize()[1]
        regionSlotTypeName = regions[0]
        newStashBlocks[regionSlotTypeName] = [[None for _ in range(12)] for _ in range(newStashBlockHeight)]

        coordsAddY = coordsAddYSave

        travelWidth = 0
        #get items to add for each slot type
        for itemsToAdd in slotTypeSize[regionSlotTypeName]:
            logDebug(f'Item to add: {itemsToAdd.getName()}')
            sz = itemsToAdd.getSize()
            addX,addY = sz[0], sz[1]

            travelWidth += addX
            if travelWidth > 11:
                newStashBlockHeight += addY
                for stashAddY in range(addY):
                        newStashBlocks[regionSlotTypeName].append([None for _ in range(12)])
                        
                travelWidth = 0
            
            for x in range(12):
                breakX = False
                for y in range(newStashBlockHeight):
                    #lookup coords from cache or region map
                    if (y+coordsAddY,x) in blockCache:
                        blockCheck = blockCache[y+coordsAddY,x]
                        logDebug(f"retrieve {blockCheck} from blockCache @ {x,y+coordsAddY}")
                    else:
                        blockCheck = newStashBlocks[regionSlotTypeName][y][x]
                        logDebug(f"retrieve {blockCheck} from newStashBlocks @ {x,y}")

                    if blockCheck == None:
                        #If we have an empty slot, check to see if there is enough room to add
                        #by iterating to all size squares. If we see another item stop.
                        addAtCurrentLeftCorner = True
                        while addAtCurrentLeftCorner:
                            for y2 in range(y,y+addY):
                                if y2 > newStashBlockHeight - 1: 
                                    addAtCurrentLeftCorner = False
                                    break
                                for x2 in range(x,x+addX):
                                    if x2 > 11: 
                                        addAtCurrentLeftCorner = False
                                        break
                                    comp2 = newStashBlocks[regionSlotTypeName][y2][x2]
                                    blockCache[(y2+coordsAddY,x2)] = comp2
                                    if comp2 != None: 
                                        addAtCurrentLeftCorner = False
                                        break
                            break

                        # if we have space, reserve it and update cache
                        if addAtCurrentLeftCorner:
                            nameRegion = itemsToAdd.getName()
                            for y2 in range(y,y+addY):
                                for x2 in range(x,x+addX):
                                    blockCache[(y2+coordsAddY,x2)] = nameRegion
                                    newStashBlocks[regionSlotTypeName][y2][x2] = nameRegion

                            logDebug(f"added {nameRegion} to new stash @ {x, y}")
                            logDebug(f"dict store {nameRegion} to new stash @ {x, y+coordsAddY}")
                            newItemCoords[(x,y+coordsAddY)] = itemsToAdd
                            x,y = 13, newStashBlockHeight + 1
                            breakX = True
                            break

                if breakX: break

        coordsAddYSave += newStashBlockHeight

    for coords in newItemCoords.items():
        logDebug(f"coord: {coords[0]} stash: {coords[1].numStash} item:{coords[1].getName()}")


    #stack newly created item blocks and form new stash
    lastBlock = None
    blockLen = len(newStashBlocks.items()) - 1

    for n, block in enumerate(newStashBlocks.items()):
        for row in block[1]:
            logDebug(row)

    #Move through blocks in pair of 2 and try to combine to retain order
    coordsAddYSave = 0
    ComboDelY = 0
    ComboCurrent = 0
    stackingCombo = False
    for n, block in enumerate(newStashBlocks.items()):
        if lastBlock != None:
            logDebug(f"block name: {block[0]}")
        if lastBlock == None: 
            lastBlock = block[1]
            coordsAddYSave += len(lastBlock)
            logDebug("Just Continued!!!")
            continue

        for brick in lastBlock:
            logDebug(brick)

        for brick in block[1]:
            logDebug(brick)
        
        #attempt to combine blocks
        itemCoordYAdd = 0
        for i , row in enumerate(newStash):
            logDebug(f"new stash row: {row}")
            if row[0] == None:
                itemCoordYAdd = i
                break
        comboBlock, newItemCoords = combineStashBlocks(lastBlock,block[1], newItemCoords, coordsAddYSave, ComboDelY)

        #if success, set last block. If not, push block to final
        if comboBlock:
            stackingCombo = True
            lastBlock = comboBlock   
            ComboDelY += len(block[1])
        else:
            if lastBlock != None:
                for y in range(len(lastBlock)):
                    for x in range(len(lastBlock[0])):
                        yDict = y + ComboCurrent + itemCoordYAdd
                        yNewStash = y + itemCoordYAdd
                        logDebug(f"""coordsAddYSave: {coordsAddYSave} minus length of last block{len(lastBlock)} itemCoordYAdd: {itemCoordYAdd} comboDelY: {ComboDelY} comboCurrent: {ComboCurrent} x iter 0 to {len(lastBlock[0])} y iter 0 to {len(lastBlock)}
                                    ||||| Searching @ dict for block no combo {x, yDict} to assign newStash @ {x,yNewStash} """)
                        
                        newStash[y+itemCoordYAdd][x] = lastBlock[y][x]
                        if (x, yDict) in newItemCoords:
                            logDebug(f"Moving {newItemCoords[(x, yDict)].getName()} aka {lastBlock[y][x]} by block no combo @ {x, yDict} to {x, yNewStash}")
                            newItemCoords[x,yNewStash] = newItemCoords.pop((x, yDict))
                            
            if n == blockLen: 
                itemCoordYAdd += len(lastBlock)

            if stackingCombo:
                ComboCurrent = ComboDelY
                stackingCombo = False

            lastBlock = block[1]

        if n == blockLen:
            for y in range(len(lastBlock)):
                    for x in range(len(lastBlock[0])):
                        yDict = y + ComboCurrent + itemCoordYAdd
                        yNewStash = y + itemCoordYAdd

                        logDebug(f"""coordsAddYSave: {coordsAddYSave} itemCoordYAdd: {itemCoordYAdd} comboDelY: {ComboDelY} comboCurrent: {ComboCurrent} x iter 0 to {len(lastBlock[0])} y iter 0 to {len(lastBlock)} 
                                    ||||| Searching @ dict for block final{x, yDict} to assign newStash @ {x,yNewStash} """)
                        newStash[y+itemCoordYAdd][x] = lastBlock[y][x]
                        if (x,yDict) in newItemCoords:
                            logDebug(f"Moving {newItemCoords[(x,yDict)].getName()} by block final @ {x,yDict} to {x,yNewStash}")
                            newItemCoords[x,yNewStash] = newItemCoords.pop((x, yDict))

        if comboBlock:
            coordsAddYSave += len(block[1])
        else:
            coordsAddYSave += len(lastBlock)

    for coord, item in newItemCoords.items():
        item.setDestination(coord[0],coord[1])

    logDebug(f"{len(itemsToSort)} items to sort")

    # find closest empty stash block XxY stash block
    def findClosestEmptyBlock(xStart, yStart, xFindSize, yFindSize, destSet, destStash, xStash=20, yStash=20):

        stashQuickEmptyCoordSet = set()
        for itemGetNones in stashStorageCoordDict.items():
            if itemGetNones[1].numStash == destStash:
                x,y = (itemGetNones[0][0],itemGetNones[0][1])
                stashQuickEmptyCoordSet.add((x,y))

        bestCoord = None
        bestDist = float('inf')

        for x in range(xStash - xFindSize + 1):
            for y in range(yStash - yFindSize + 1):
                blockCoords = [(x + dx, y + dy) for dx in range(xFindSize) for dy in range(yFindSize)]
                if all(coord not in stashQuickEmptyCoordSet for coord in blockCoords) and all(coord not in destSet for coord in blockCoords):
                    dist = abs(x - xStart) + abs(y - yStart)
                    if dist < bestDist:
                        bestDist = dist
                        bestCoord = (x, y)
                        
        return bestCoord



    #Handle all of an item's blockers
    def handleBlocking(currentBlocker, stashStorageCoordDict, destStash, invStorage, visited=[], destSet = set()):
        if not runOrganize: return False

        xStart, yStart = currentBlocker.getStashCoords()
        xSz, ySz = currentBlocker.getSize()
        name = currentBlocker.getName()
        xDest, yDest = currentBlocker.getDestination()

        logDebug(f"HandlingBlocking for {name}")
        
        #if we have seen this blocker before, find temp space and move seen item to it- if no temp space then we need to create it or else we have truly failed.
        if currentBlocker in visited:
            tempPlacement = findClosestEmptyBlock(xStart, yStart, xSz, ySz, destSet, destStash)
            if tempPlacement:
                moved = currentBlocker.moveToStash(tempPlacement[0], tempPlacement[1], stashStorageCoordDict, destStash, invStorage)
                if moved:
                    logDebug(f"Moving {name} to temp space @ {tempPlacement[0], tempPlacement[1]}")
                else:
                    logDebug(f"FAILED1 Moving {name} to temp space @ {tempPlacement[0], tempPlacement[1]}")
                    return False
            else:
                logDebug(f"No avail temp space, FAIL!!!!")
                return False
            
        #if we haven't seen the blocker, attempt to move it to it's final destination
        else:
            visited.append(currentBlocker)
            for y in range(ySz):
                for x in range(xSz):
                    xCheck = x + xDest
                    yCheck = y + yDest
                    blockCheck = stashStorageCoordDict.get((xCheck, yCheck, destStash), None)
                    if blockCheck != None and blockCheck != currentBlocker:
                        logDebug(f"{name} blocked by {blockCheck.getRarity()} {blockCheck.getName()} @ {(xCheck,yCheck)}")
                        
                        success = handleBlocking(blockCheck, stashStorageCoordDict, destStash, invStorage)
                        if success:
                            logDebug(f"Moved3 {blockCheck.getName()} successfully via handleBlocking")
                
                        else:
                            logDebug(f"FAILED2 Moving {blockCheck.getName()} via handleBlocking. Cannot move {name}")
                            return False

            moved = currentBlocker.moveToStash(xDest, yDest, stashStorageCoordDict, destStash, invStorage)

            if not moved:
                logDebug(f"FAILED3!! to move {name} via handleBlocking")
                return False
        
            else:
                logDebug(f"Moved2 {name} successfully via handleBlocking")
                
                for y in range(yDest, yDest + ySz):
                    for x in range(xDest, xDest + xSz):
                            destSet.discard((x,y))
        
        # If we visited other blockers, move them to final positions now that we have a clear path
        while visited:
            if not runOrganize: return False

            lastVisited = visited.pop()
            xStart, yStart = lastVisited.getStashCoords()
            xSz, ySz = lastVisited.getSize()
            name = lastVisited.getName()
            xDest, yDest = lastVisited.getDestination()

            logDebug((name, lastVisited.getRarity()))


            for y in range(ySz):
                for x in range(xSz):
                    xCheck = x + xDest
                    yCheck = y + yDest
                    blockCheck = stashStorageCoordDict.get((xCheck, yCheck, destStash), None)
                    if blockCheck != None and blockCheck != lastVisited:
                        logDebug(f"{name} blocked by {blockCheck.getRarity()} {blockCheck.getName()} @ {(xCheck,yCheck)}")
                        
                        success = handleBlocking(blockCheck, stashStorageCoordDict, destStash, invStorage)
                        if success:
                            logDebug(f"Moved3 {blockCheck.getName()} successfully via handleBlocking")
        
                        else:
                            logDebug(f"FAILED2 Moving {blockCheck.getName()} via handleBlocking. Cannot move {name}")
                            return False

            moved = lastVisited.moveToStash(xDest, yDest, stashStorageCoordDict, destStash, invStorage)

            if not moved:
                logDebug(f"FAILED3!! to move {lastVisited.getName()} via handleBlocking")
                return False
        
            else: 
                logDebug(f"Moved2 {lastVisited.getName()} successfully via handleBlocking")
                for y in range(yDest, yDest + ySz):
                        for x in range(xDest, xDest + xSz):
                            destSet.discard((x,y))
        
        return True

    #if multi-stash select, find 

    destStash = min(stashFlags)
    invStorage = getInvQuickStashLocations()
    currentStashSelect = destStash

    for item in itemSortPlaceOrder:
        #get new destination coords and attempt move
        xDestination, yDestination = item.getDestination()
        xSz, ySz = item.getSize()

        
        for y in range(ySz):
            for x in range(xSz):
                xCheck = x + xDestination
                yCheck = y + yDestination
                blockCheck = stashStorageCoordDict.get((xCheck, yCheck, destStash), None)
                if blockCheck != None and blockCheck != item:
                    logDebug(f"{item.getName()} blocked by {blockCheck.getRarity()} {blockCheck.getName()} @ {(xCheck,yCheck)}")
                    
                    success = handleBlocking(blockCheck, stashStorageCoordDict, destStash, invStorage)
                    if success:
                        logDebug(f"Moved3 {blockCheck.getName()} successfully via handleBlocking")
            
                    else:
                        logDebug(f"FAILED2 Moving {blockCheck.getName()} via handleBlocking. Cannot move {item.getName()}")
                        database.closeDatabase(conn)
                        return False

        success = item.moveToStash(xDestination, yDestination, stashStorageCoordDict, destStash, invStorage)

        if success:
            logDebug(f"Moved3 {item.getName()} successfully via order move")
        
        else:
            logDebug(f"FAILED2 Moving {item.getName()} via order move after handling blocking. Cannot move {item.getName()}")
            database.closeDatabase(conn)
            return False
        
    logGui(f'done in {time.time() - time1:.2f} seconds')

    #This block is used to compare stash read square vals for debugging 
    numGoodGood = 0
    for i, item in enumerate(newItemCoords.items()):
        logDebug(f"Comping {item[1].getName()} and {itemSortPlaceOrder[i].name}")
        xNew1,yNew1 = item[0]
        xNew2 = ((xNew1 * 40) + 10 + config.xStashStart)
        yNew2 = ((yNew1 * 40) + 10 + config.yStashStart)

        x,y = itemSortPlaceOrder[i].getCoords()
        xReal = int((x - 10 - config.xStashStart) / 40)
        yReal = int((y - 10 - config.yStashStart) / 40)
        logDebug(f"Moving {itemSortPlaceOrder[i].getName()} from {x,y} aka {xReal, yReal} to {xNew2,yNew2 } aka {xNew1,yNew1}")
        if newStash[yNew1][xNew1] == item[1].getName(): numGoodGood+=1
        try:
            logDebug(f"{newStash[yNew1][xNew1] == item[1].getName()} newStashComp: {newStash[yNew1][xNew1]} accepting {item[1].getName()} @ {xNew1,yNew1}")
        except Exception as e:   
            logDebug(f"fail @ {x,y} {item[1].getName()}")
            pass

    if numGoodGood == len(itemsToSort):
        logDebug(f"Ultimate success! {numGoodGood} == {len(itemsToSort)} Items to sort matches itemToSort")
    else:
        logDebug(f"{numGoodGood} != {len(itemsToSort)}")

    y = len(stashStorage) -1
    x = len(stashStorage[0]) -1
    numStashFreq = 0
    for i in range(y):
        logDebug(stashStorage[i])
        for j in range(x):
            if stashStorage[i][j] != None: numStashFreq += 1

    numNotNone = 0
    for row in newStash:
        logDebug(row)
        for ele in row:
            if ele != None:
                numNotNone += 1

    logDebug(f"{numStashFreq} should ==  {len(itemDetectedStashSquares)} should ==  {(numNotNone)}")

    database.closeDatabase(conn)
    return True



# better detect if item is in stash on given coords
def detectItem2(ss,x,y):
    cropRegion = [x,y,x+20,y+20]
    ssStashSquare = ss.crop(cropRegion)

    w, h = ssStashSquare.size

    pixelData = ssStashSquare.getdata()
    total = 0
    for data in pixelData:
        total += sum(data)
    
    avgPxlVal = int(total / (w * h))

    if avgPxlVal > database.getConfig(cursor,"pixelValue"):
        return True
    else:
        return False



# Merge block2 into block1 for one item block if possible
def combineStashBlocks(block1, block2, newItemCoords, coordsAddY, ComboDelY):
    #find max rect of avail space for target
    def largestRect(grid, matchNone=True):
        if not grid or not grid[0]:
            return 0, 0, -1, -1  # width, height, x, y

        height = len(grid)
        width = len(grid[0])
        hist = [0] * width
        max_area = 0
        max_dims = (0, 0, -1, -1)  # width, height, x, y (top-left corner)

        for y in range(height):
            for x in range(width):
                cell_matches = (grid[y][x] is None) if matchNone else (grid[y][x] is not None)
                hist[x] = hist[x] + 1 if cell_matches else 0

            # Stack-based histogram max-rectangle
            stack = []
            x = 0
            while x <= width:
                curr_height = hist[x] if x < width else 0
                if not stack or curr_height >= hist[stack[-1]]:
                    stack.append(x)
                    x += 1
                else:
                    top = stack.pop()
                    h = hist[top]
                    w = x if not stack else x - stack[-1] - 1
                    area = h * w

                    if area > max_area:
                        max_area = area
                        x_left = 0 if not stack else stack[-1] + 1
                        top_left_x = x_left
                        top_left_y = y - h + 1  # y of top-left is current row minus height + 1
                        max_dims = (w, h, top_left_x, top_left_y)

        return max_dims  # width, height, x, y
    
    def largest_connected_non_none(grid):
        if not grid or not grid[0]:
            return 0, 0, -1, -1  # width, height, x, y

        height = len(grid)
        width = len(grid[0])
        visited = [[False] * width for _ in range(height)]
        max_area = 0
        max_dims = (0, 0, -1, -1)  # width, height, x, y

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

        for y in range(height):
            for x in range(width):
                if grid[y][x] is not None and not visited[y][x]:
                    # Start BFS
                    queue = deque()
                    queue.append((x, y))
                    visited[y][x] = True

                    min_x = max_x = x
                    min_y = max_y = y

                    while queue:
                        cx, cy = queue.popleft()
                        for dx, dy in directions:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                if grid[ny][nx] is not None and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                                    min_x = min(min_x, nx)
                                    max_x = max(max_x, nx)
                                    min_y = min(min_y, ny)
                                    max_y = max(max_y, ny)

                    comp_width = max_x - min_x + 1
                    comp_height = max_y - min_y + 1
                    comp_area = comp_width * comp_height

                    if comp_area > max_area:
                        max_area = comp_area
                        max_dims = (comp_width, comp_height, min_x, min_y)

        return max_dims  # width, height, x, y
    
    largestRec1 = largestRect(block1)
    largestRec2 = largest_connected_non_none(block2)

    #if we have enough "None" space in block1 for block2 items, combine.
    if largestRec1[0] >= largestRec2[0] and largestRec1[1] >= largestRec2[1]:
        for y in range(largestRec2[1]):
            for x in range(largestRec2[0]):
                #update first block with both to return in & update newItemCoords Y value for affected items
                block1[y+largestRec1[3]][x+largestRec1[2]] = block2[y+largestRec2[3]][x+largestRec2[2]]
                logDebug(f"Searching for index in dict: for combo block {(x,y + coordsAddY)} mapped to replacement {x+largestRec1[2],y+coordsAddY-len(block1)-ComboDelY}")
                if (x,y + coordsAddY) in newItemCoords:
                    logDebug(f"Moving {newItemCoords[(x,y + coordsAddY)].getName()} by stash combo @ {x,y + coordsAddY} to {x+largestRec1[2],y+coordsAddY-len(block1)-ComboDelY}")
                    newItemCoords[x+largestRec1[2],y+coordsAddY-len(block1)-ComboDelY] = newItemCoords.pop((x,y + coordsAddY))

        logDebug("combo rows:")
        for row in block1:
            logDebug(row) 

        return block1, newItemCoords
    
    else:
        return None, newItemCoords



# Best detect item, take ss of entire stash, filter background colors, record coords of pixel clusters
def detectItem3():
    #Get list of each item and x,y coord for an easy read. One iteration, no multiple queue
    pass



# select stash
def selectStash(numStash):
    xStashSwitch, yStashSwitch = 1380, 195
    pyautogui.moveTo(xStashSwitch - 60, yStashSwitch + 10 + (numStash * 46))
    pyautogui.click()



# get locations of empty inventory space
def getInvQuickStashLocations():
    mySS = pyautogui.screenshot(region=config.ssGetStashInv)
    myGrid = [[None for _ in range (10)] for _ in range(5)]

    for y in range(5):
        for x in range(10):
            newX = 10 + (40 * x)
            newY = 10 + (40 * y)
            if detectItem2(mySS,newX, newY):
                myGrid[y][x] = 1

    def findFirstEmptyRect(grid, width, height):
        rows, cols = len(grid), len(grid[0])

        for y in range(rows - height + 1):
            for x in range(cols - width + 1):
                all_none = True
                for dy in range(height):
                    if any(grid[y + dy][x : x + width]):
                        all_none = False
                        break
                if all_none:
                    xMv = x * 40 + config.ssGetStashInv[0] + 17
                    yMv = y * 40 + config.ssGetStashInv[1] + 17
                    return (xMv, yMv)

        return None

    findFirstAcceptGrid = dict()
    for y in range(1,6):
        for x in range(1,4):
            if(x,y) == (3,5): break

            res = findFirstEmptyRect(myGrid,x,y)
            if res: findFirstAcceptGrid[(x,y)] = res
        if(x,y) == (3,5): break

    return findFirstAcceptGrid