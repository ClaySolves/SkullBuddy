import math
import re
import random
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
from PIL import Image
import numpy as np
from screeninfo import get_monitors
from collections import deque

logger = logging.getLogger()  # Get the root logger configured in main.py

#item class
class item():
    # constructor
    def __init__(self, name, rolls, rarity, coords, size, quantity, slotType=None,price=None):
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

        logger.debug("New item created")



    #Print item
    def printItem(self,newline=False):
        if self.rarity:
            self.printRarityName()

            for roll in self.rolls:
                self.printRoll(roll)
                
        if self.price:
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


    # get item from database storing string
    def getItemStoreDetails(self):

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
        time.sleep(sleepTime / 15)
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
            foundPrice = recordDisplayedPrice()
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
                if finalPrice < 15 or finalPrice > database.getConfig(cursor,'sellMin'):
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

    conn, cursor = database.connectDatabase()

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
    slotTypes = config.SLOT_TYPE



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
    #print(f'slot txt {txt}')
    txtRemove = "Slot Type"
    try:
        keywordIndex = txt.index(txtRemove) + len(txtRemove)
        ret = txt[keywordIndex:].lstrip()
        finalRet = ''.join(char for char in ret if char.isalpha())
        finalFinalRet = findItem(finalRet, slotTypes, cutoff=0.8)
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

    # ss = pyautogui.screenshot(region=[config.ssMarketRollSearch[0] + 10,config.ssMarketRollSearch[1],config.ssMarketRollSearch[2],config.ssMarketRollSearch[3] + 50])
    # ss.save("debug/marketstall.png")

    # pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch)
    # time.sleep(sleepTime / 15)
    # pyautogui.click()

    # pyautogui.moveTo(config.xAttrSearch + 250, config.yAttrSearch)
    # time.sleep(sleepTime / 15)
    # pyautogui.click()

    # res = confirmGameScreenChange(ss,region=config.ssMarketRollSearch)
    # if not res:
    #     pyautogui.moveTo(config.xAttrSearch + 250, config.yAttrSearch)
    #     time.sleep(sleepTime / 15)
    #     pyautogui.click()
    #     res = confirmGameScreenChange(ss,region=config.ssMarketRollSearch)

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
    pyautogui.moveTo(xChar, yChar, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click

    xLobby, yLobby = 960, 1000  # coords for enter lobby location
    pyautogui.moveTo(xLobby, yLobby, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click
    
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
    pyautogui.moveTo(x,y)
    time.sleep(sleepTime/10)
    pyautogui.keyDown('shift')   
    time.sleep(sleepTime/10)
    pyautogui.click(button="right")
    time.sleep(sleepTime/10)
    pyautogui.keyUp('shift')



def stopScript():
    global runSearch
    logDebug("Turning runSearch FALSE")
    runSearch = False


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
                            database.insertItem(cursor,foundItem.getItemStoreDetails())     

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
        logGui(f"No listing slots available")
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
        logDebug(f"Could not find name in\n{lines}" )

    return name, size, space



#Get additional information needed for item sort
def finalizeStashItem(ssStash, name, size, space, x, y) -> item:
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
    foundItem = item(name,[],rarity,coords,size,1,slotType=slotType)
    print(f"{foundItem.rarity} {foundItem.name} {foundItem.size} {foundItem.slotType}")
    return foundItem



# main function 
# reads hovered item info, lists on market
def handleItem() -> tuple[item, bool]: # Returns listed item / listing success

    time.sleep(sleepTime / 5)
    mytime = time.time()
    myItem = getItemInfo()                                                  # read item info
    
    if myItem:
        logGui("Searching Market For",printEnd=" ")
        myItem.printItem()                                                  # print item to gui
        foundPrice = myItem.findPrice3()                                    # if price found, continue loop || return false
        returnMarketStash()                                                 # return market stash

        if foundPrice:
            listedSuccess = myItem.listItem()
            if listedSuccess:                                               # list item
                mytime2 = time.time()
                logGui(f"Listed item in {mytime2-mytime:0.1f} seconds")         # log time to gui
                time.sleep(sleepTime / 1.2)
                return myItem, True
    
        # time.sleep(sleepTime / 3)
        # pyautogui.moveTo(myItem.coords[0],myItem.coords[1])
        # pyautogui.click(button='right')

        return myItem, False      
    return None, False                                                      # if we fail any part of loop, return false



#Search current displayed stash
def organizeStash() -> bool: # True/False successful sort
    logger.debug("Organizing Stash")
    time1=time.time()

    ssCheckStashPage = pyautogui.screenshot(region=config.ssConfirmStash)
    txt = pytesseract.image_to_string(ssCheckStashPage,config="--psm 6")
    if 'stash' not in txt.lower():
        logGui("Stash Not Detected","red")
        logGui("Navigate to the stash you want to organize and try again")
        logger.error("Organize stash called but no stash page detected")
        return False

    ssGetStash = pyautogui.screenshot(region=config.ssEntireStash)

    itemDetectedStashSquares = []
    stashFrequency = {}
    ssQueue = deque()
    itemQueue = deque()
    stashStorage = [[None for _ in range(12)] for _ in range(20)]
    stashItemPresent = [[False for _ in range(12)] for _ in range(20)]
    itemsToSort = []

    #look for items to sort
    for y in range(database.getConfig(cursor,'sellHeight')):
        for x in range(database.getConfig(cursor,'sellWidth')):
            newX = 10 + (40 * x)
            newY = 10 + (40 * y)
            itemDetected = detectItem2(ssGetStash,newX,newY)

            if itemDetected:
                foundItem = [config.xStashStart + newX, config.yStashStart + newY]
                itemDetectedStashSquares.append(foundItem)
                stashItemPresent[y][x] = True

    #this doesn't do anything but the random movement looks cool lol
    #random.shuffle(itemDetectedStashSquares)

    if not itemDetectedStashSquares:
        logGui("Yeah let me just organize this empty stash... Bro are you dumb or something?")
        return None

    #create workers to scrape screenshots
    def ssWorker():
        for _ in range(20):
            while ssQueue:
                queueData = ssQueue.popleft()
                x = (queueData[1] - (10 + config.xStashStart) ) // 40
                y = (queueData[2] - (10 + config.yStashStart) ) // 40

                foundSortName, foundSortSize, foundSortSpace = getItemNameSizeSpace(queueData[0])

                #If we found an item record. If we have full item, send to 
                if foundSortName is not None:
                    stashStorage[y][x] = foundSortName

                    if foundSortName not in stashFrequency:
                        stashFrequency[foundSortName] = 1
                    else:
                        stashFrequency[foundSortName] += 1

                    itemReady = True
                    if stashFrequency[foundSortName] >= (foundSortSize[0] * foundSortSize[1]):
                        while itemReady:
                            for y2 in range(foundSortSize[1]):
                                if y-y2 < 0: break
                                for x2 in range(foundSortSize[0]):
                                    if x-x2 < 0: break
                                    #print(f"looking for stashStorage[{y-y2}][{x-x2}]")
                                    if stashStorage[y-y2][x-x2] != foundSortName:
                                        itemReady = False
                            break
                    else:
                        itemReady = False

                    if itemReady:
                        for y2 in range(foundSortSize[1]):
                                for x2 in range(foundSortSize[0]):
                                    stashStorage[y-y2][x-x2] = None

                        print(f"sending {foundSortName} to item queue")
                        itemQueue.append((queueData[0], foundSortName, foundSortSize, foundSortSpace, queueData[1], queueData[2]))
                else:
                    pass
            else:
                time.sleep(0.1)

        for _ in range(20):
            while(itemQueue):
                item = itemQueue.popleft()
                finalItem = finalizeStashItem(item[0],item[1],item[2],item[3],item[4],item[5])
                itemsToSort.append(finalItem)

            else:
                time.sleep(0.1)

    numWorkers = 6 #4 if sleepTime >= 1.3 else 6
    print(numWorkers)
    threads = []

    for _ in range(numWorkers):
        t = threading.Thread(target=ssWorker)
        t.start()
        threads.append(t)

    #store screenshots of each item square
    for item in itemDetectedStashSquares:
        pyautogui.moveTo(item[0],item[1])
        ss = pyautogui.screenshot()
        ssStore = (ss,item[0],item[1])
        ssQueue.append(ssStore)

    #Wait for workers
    for thread in threads:
        thread.join()

    # Group found items by slotType, generate ideal stash, move items to new positions
    slotTypeFreq = {}

    for item in itemsToSort:
        if item.slotType not in slotTypeFreq:
            slotTypeFreq[item.slotType] = [item.size[0] * item.size[1], (item.size[0], item.size[1])]
        else:
            slotTypeFreq[item.slotType][0] += item.size[0] * item.size[1]
            slotTypeFreq[item.slotType].append((item.size[0], item.size[1]))

    print(slotTypeFreq.items())
    print(f'done in {time.time() - time1} seconds')

    sumFreq = 0
    for freq in slotTypeFreq.values():
        sumFreq += freq[0]
    sortedStashItems = dict(sorted(stashFrequency.items()))
    totalSort = 0
    for val in sortedStashItems:
        totalSort += sortedStashItems[val]
    print(totalSort, len(itemDetectedStashSquares), sumFreq)




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
    


# Best detect item, take ss of entire stash, filter background colors, record coords of pixel clusters
def detectItem3():
    #Get list of each item and x,y coord for an easy read. One iteration, no multiple queue
    pass