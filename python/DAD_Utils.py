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
from pynput import keyboard, mouse

#exception
class NoListingSlots(Exception):
    pass

#item class
class item():
    # constructor
    def __init__(self, name, rolls, rarity, coords):
        item.name = name # item name
        item.rolls = rolls # item rolls
        item.rarity = rarity # item rarity
        item.price = None # item price
        item.coords = coords # item location
        item.sold = False

    #Print item
    def printItem(self):
        print(f"{item.rarity} {item.name}")
        for roll in item.rolls:
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
            print(rollPrint)

            if item.price:
                print(f"Found Price: {item.price} Gold")

# search market gui for all item rolls
    def searchGoodRolls(self):
        numSearch = 0
        for i, roll in enumerate(item.rolls):

            if i == 0:
                pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=0.1) 
                pyautogui.click()                

                pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.05) 
                pyautogui.click()

            if roll[3]:
                pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=0.15) 
                pyautogui.click()
                pyautogui.typewrite(roll[1], interval=0.01)

                pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * numSearch), duration=0.15) 
                pyautogui.click()
                numSearch += 1


    # search market gui for all item rolls
    def searchAllRolls(self):
        for i, roll in enumerate(item.rolls):
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

    # search market gui for indexed item roll
    def searchRoll(self,i):
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=0.1) 
        pyautogui.click() 

        pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.05) 
        pyautogui.click()

        roll = item.rolls[i]
        pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=0.15) 
        pyautogui.click()
        pyautogui.typewrite(roll[1], interval=0.01)

        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect, duration=0.15) 
        pyautogui.click()

    #remove roll from market gui search 
    def removeSearchRoll(self,i):
        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + (25 * i), duration=0.15) 
        pyautogui.click()

    #Search market for item price # Assume that View Market tab is open
    def findPrice(self) -> bool: # True/False Price Find Success
        print("Searching for ...")
        item.printItem(self) 
        prices = []

        # reset filters, search rarity
        while not locateOnScreen('selectedViewMarket', region=config.regionMarketListings):
            pyautogui.moveTo(config.xViewMarket, config.yViewMarket, duration=0.1) 
            pyautogui.click()

        ss = pyautogui.screenshot(region=config.ssComp1)
        if confirmGameScreenChange(ss): pass 
        else: return False

        refreshMarketItem()
        pyautogui.moveTo(config.xRarity, config.yRarity, duration=0.1) 
        pyautogui.click()
        searchRarity(item.rarity)

        #search Item
        pyautogui.moveTo(config.xItemName, config.yItemName, duration=0.1) 
        pyautogui.click()  
        pyautogui.moveTo(config.xItemSearch, config.yItemSearch, duration=0.1) 
        pyautogui.click() 
        pyautogui.typewrite(item.name, interval=0.01)
        selectItemSearch() 

        #store base price
        foundPrice = recordDisplayedPrice()
        if foundPrice: prices.append(foundPrice)

        #store price of each roll
        for i, roll in enumerate(item.rolls):
            item.searchRoll(self,i)
            foundPrice = recordDisplayedPrice()
            if foundPrice: 
                prices.append(foundPrice)
                good = checkPriceRoll(prices[0],foundPrice)
                if not roll[3]: item.rolls[i][3] = good

        #store all roll price
        item.searchGoodRolls(self)
        foundPrice = recordDisplayedPrice()
        if foundPrice: item.price = foundPrice
        else: item.price = min(prices)
        
        item.printItem(self) 

        return prices

    #Lists item for found price
    def listItem(self) -> bool: # True/False Listing Success
        if item.price:
            slots = getAvailSlots(0)
            if(slots):
                pyautogui.moveTo(item.stashLocation[1], item.stashLocation[0], duration=0.1) 
                pyautogui.click()
                time.sleep(0.4)

                pyautogui.moveTo(config.xSellingPrice, config.ySellingPrice, duration=0.1) 
                pyautogui.click()
                pyautogui.typewrite(str(item.price), interval=0.01)

                pyautogui.moveTo(config.xCreateListing, config.yCreateListing, duration=0.1) 
                pyautogui.click()

                pyautogui.moveTo(config.xConfirmListing, config.yConfirmListing, duration=0.1) 
                pyautogui.click()
                return True
            else:
                return False
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
        return True
    else:
        return False

# searches market and finds price
def recordDisplayedPrice() -> int: # Price/None
    searched = refreshMarketSearch()
    if searched:
        price = getItemCost()
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

    while noInfiniteLOL < 65:
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
    ss = pyautogui.screenshot(region=config.ssMarketExpireTime)
    pyautogui.moveTo(config.xSearchPrice, config.ySearchPrice, duration=0.15)
    pyautogui.click()
    ret = confirmGameScreenChange(ss,region=config.ssMarketExpireTime)
    return ret


# Refresh market search query
def refreshMarketItem():
    pyautogui.moveTo(config.xResetFilters, config.yResetFilters, duration=0.10)
    pyautogui.click()


# Search market for item and find price
# return int>0 price, 0 if nothing, -1 if NICE LOOT
def searchAndFindPrice(weapon):

    #reset filters and search rarity
    while not locateOnScreen('selectedViewMarket', region=config.regionMarketListings):
        pyautogui.moveTo(config.xViewMarket, config.yViewMarket, duration=0.1) 
        pyautogui.click()  

    pyautogui.moveTo(config.xResetFilters, config.yResetFilters, duration=0.5) 
    pyautogui.click() 

    pyautogui.moveTo(config.xRarity, config.yRarity, duration=0.1) 
    pyautogui.click()

    # If no rarity, add one. search market
    if not searchRarity(weapon[-1]):
        logDebug("No rarity was found... Let's guess off the amount of rolls")
        length = len(weapon)
        if length == 1:
            weapon.append("Common")
        if length == 2:
            weapon.append("Uncommon")
        if length == 3:
            weapon.append("Rare")
        if length == 4:
            weapon.append("Epic")
        if length == 5:
            weapon.append("Legendary")
        if length == 6:
            weapon.append("Unique")
        searchRarity(weapon[-1])
    
    logDebug("Searching for : " + str(weapon[-1]) + ' ' + str(weapon[0]))

    #search Item
    pyautogui.moveTo(config.xItemName, config.yItemName, duration=0.1) 
    pyautogui.click()  

    pyautogui.moveTo(config.xItemSearch, config.yItemSearch, duration=0.1) 
    pyautogui.click() 
    pyautogui.typewrite(weapon[0], interval=0.01)

    selectItemSearch() 

    #Start reading price for each attribute starting with base item
    price = []
    pyautogui.moveTo(config.xSearchPrice, config.ySearchPrice, duration=0.1) 
    pyautogui.click()
    time.sleep(1)

    # Record base price, if no attr's than return
    basePrice = getItemCost()
    if len(weapon) == 2: return basePrice

    for weaponRolls in weapon[1:-1]:
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=0.1) 
        pyautogui.click()
        pyautogui.typewrite(weaponRolls, interval=0.01)

        logDebug("attr : " + str(weaponRolls))

        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(config.xSearchPrice, config.ySearchPrice, duration=0.1) 
        pyautogui.click()
        time.sleep(1)
        foundPrice = getItemCost(basePrice)
        if foundPrice < 0:
            return -1
        else:
            price.append(foundPrice)

    # If only one attr, skip more comps and return found price if signficant increase else basePrice
    if len(price) == 1:
        return basePrice if price[0] < basePrice + (basePrice * .10) else price[0]

    #If attr raises baseprice >25%, we're gonna comp it with other attr's
    #Get max index and search that
    maxPrice = max(price)
    maxIndex = price.index(maxPrice)
    bestAttr = weapon[maxIndex + 1]

    if maxPrice > basePrice + (basePrice * 0.25) or maxPrice > basePrice + 50:
        pyautogui.moveTo(config.xResetAttribute, config.yResetAttribute, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=.2) 
        pyautogui.click()
        pyautogui.typewrite(bestAttr, interval=0.01)

        pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect, duration=.2) 
        pyautogui.click()

        #add other attr to selected attr
        twoPrice = []
        for index, attr in enumerate(weapon[1:-1]):

            if index == maxIndex:
                logDebug('Skipping already selected attr')
                continue

            logDebug("attr : " + str(attr) + " " + str(bestAttr))

            pyautogui.moveTo(config.xAttrSearch, config.yAttrSearch, duration=.2) 
            pyautogui.click()
            pyautogui.typewrite(attr, interval=0.01)

            pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + 25, duration=.2) 
            pyautogui.click()

            pyautogui.moveTo(config.xSearchPrice, config.ySearchPrice, duration=.2) 
            pyautogui.click()
            time.sleep(1)
            found2Price = getItemCost(basePrice)
            if found2Price < 0:
                return -1
            else:
                twoPrice.append(found2Price)

            pyautogui.moveTo(config.xAttribute, config.yAttribute, duration=.2) 
            pyautogui.click()

            pyautogui.moveTo(config.xAttrSelect, config.yAttrSelect + 25, duration=.2) 
            pyautogui.click()

        return max(maxPrice,max(twoPrice))
    else:
        return maxPrice


# get average cost of displayed item in market lookup
def getItemCost(basePrice=None):
    prices = readPrices()
    if prices:
        price = calcItemPrice(prices,config.sellMethod)
    else:
        return None
    if price:
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

    print(prices)
    
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


#Returns coords of selected stash
def selectStash(market=False): 
    if market:
        stashNum = config.stashSell
    else:
        stashNum = config.stashDump
    txt = 'SharedMenu' if stashNum < 0 else str(stashNum)
    search = txt + "Market" if market else txt
    logDebug(f"selecting stash: {search}.png")
    res = locateOnScreen(f"stash{search}", region=config.getStashRegion)
    if res:
        pyautogui.moveTo(res[0]+15,res[1]+15)
        pyautogui.click()
    return res


#moves item in coords to/from inventor
def itemMoveInventory(x=config.xStashStart,y=config.yStashStart,attempt=1):
    pyautogui.moveTo(x,y)

    mouseKey = mouse.Controller()
    keyboardKey = keyboard.Controller()
    keyboardKey.press(keyboard.Key.shift)
    time.sleep(0.1)
    mouseKey.click(mouse.Button.right)
    keyboardKey.release(keyboard.Key.shift)
    if attempt > 4: 
        pass
    elif getItemTitle(): 
        attempt += 1
        itemMoveInventory(attempt)


#Nav to stash from market and dump into coords.dumpStash
# I probably need to update the region for the screenshot
def dumpInventory():
    pyautogui.moveTo(config.xExitMarket,config.yExitMarket) 
    pyautogui.click()

    pyautogui.moveTo(config.xExitMarketYes,config.yExitMarketYes,duration=0.1) 
    pyautogui.click()
    time.sleep(0.5)

    pyautogui.moveTo(config.xStashSelect,config.yStashSelect,duration=0.1) 
    pyautogui.click()

    if not locateOnScreen('selectedStash'): dumpInventory()

    selectStash()

    for y in range(5):
        for x in range(10):
            xInv = config.xInventory
            yInv = config.yInventory
            if not detectItem(41 * x, 41 * y,xInv,yInv):
                print(f'Continue{x}{y}')
                continue
            else:
                itemMoveInventory(xInv + (41 * x),yInv + (41 * y))


#two obv logging func
def logDebug(txt):
    logging.debug(txt) 

def logGui(txt):
    print(txt)


# Return location and santize ImageNotFound error
def locateOnScreen(img,region=config.getScreenRegion,grayscale=False,confidence=0.99):
    logDebug(f"Searching for Image {img}...")
    strKey = isinstance(img, str)
    try:
        if strKey:
            res = pyautogui.locateOnScreen(f'img/{img}.png', region = region, confidence = confidence, grayscale = grayscale)
        else:
            res = pyautogui.locateOnScreen(img, region = region, confidence = confidence, grayscale = grayscale)
        return res 
    except:
        logDebug("Failed!")
        return None
    
def locateAllOnScreen(img,region=config.getScreenRegion,grayscale=False,confidence=0.99):
    logDebug(f"Searching for Image {img}...")
    strKey = isinstance(img, str)
    try:
        if strKey:
            res = pyautogui.locateAllOnScreen(f'img/{img}.png', region = region, confidence = confidence, grayscale = grayscale)
        else:
            res = pyautogui.locateAllOnScreen(img, region = region, confidence = confidence, grayscale = grayscale)
        listRes = list(res)
        return listRes
    except:
        logDebug("Failed!")
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
        logDebug(f"Found {ret} item\n")  
    else:
        logDebug("ERROR!!! NO RARITY FOUND\n") 

    return ret   


# detects if item is in stash on given coord offset
def detectItem(xAdd,yAdd,xStart=config.xStashDetect,yStart=config.yStashDetect):
    ss = pyautogui.screenshot(region=[xStart + xAdd,yStart + yAdd,20,20])
    ss = ss.convert("RGB")
    # ss.save(f"debug/seeStash_x_{xAdd/41}_y_{yAdd/41}.png")
    w, h = ss.size
    data = ss.getdata()
    total = 0
    ret = 0

    for item in data:
        total += sum(item)

    div = w*h
    res = math.floor(total/div)
    logDebug(f"addX: {xAdd/41} addY: {yAdd/41} " + "avg pixel val on: " + str(res) + "\n")
    if res > 110:
        ret = 1

    if ret:
        logDebug("Item detected\n")
    else:
        logDebug("No item detected ; " + str(res) + " < 110\n")

    return ret


# Get the availible listing slots
def getAvailSlots():
    #Take screenshot and sanitize for read text
    ss = pyautogui.screenshot(region=[config.xGetListings,config.yGetListings,config.x2GetListings,config.y2GetListings])
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
    txt = txt.splitlines()

    #Read for listing slots and report if any avial, and #of slots
    slots = 0
    for lines in txt:
        if lines == 'List an Item':
            slots += 1
        else:
            continue

    logDebug(f"{str(slots)} listings availible\n")

    return slots


#Check listings for sold items and claim gold 
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
        gatherSoldListings()

    else: logDebug("All sold items cleared ...")
    

# Get the title of an item on top left corner
def getItemTitle():
    # Take screenshot of title and filter data for text read
    targetColor = 130    
    ss = pyautogui.screenshot(region=[config.xStashStart,config.yStashStart,config.xTitleAdd,config.yTitleAdd])
    ss = ss.convert("RGB")
    data = ss.getdata()
    newData = []

    for pixel in data:
        if pixel[0] >= targetColor or pixel[1] >= targetColor:
            newData.append(pixel)
        else:
            newData.append((0,0,0))

    ss.putdata(newData)
    ss.save('debug/testingTitle.png')
    txt = pytesseract.image_to_string("debug/testingTitle.png",config="--psm 6")
    logDebug("got title text: " + str(txt) + "\n")

    # Search for item from txt and return result
    with open("config/items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    txt = txt.splitlines()
    item = None
    for line in txt:
        item = findItem(line,allItems)
        if item:
            break
    
    return item


#Listen item at price
def listItem(price):
    slots = getAvailSlots()

    if(slots):
        pyautogui.moveTo(config.xStashStart, config.yStashStart, duration=0.1) 
        pyautogui.click()
        time.sleep(0.4)

        pyautogui.moveTo(config.xSellingPrice, config.ySellingPrice, duration=0.1) 
        pyautogui.click()
        pyautogui.typewrite(str(price), interval=0.01)

        pyautogui.moveTo(config.xCreateListing, config.yCreateListing, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(config.xConfirmListing, config.yConfirmListing, duration=0.1) 
        pyautogui.click()
        return 1
    else:
        return 0


# Lookup and return input_string from phrase_list
def findItem(input_string, phrase_list,n=1):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=n, cutoff=0.6)
    logDebug("Found: " + str(closest_match) + "\n")
    return closest_match[0] if closest_match else None


# Sanitize junk ascii from num
def sanitizeNumerRead(num):
    cleanNum = num.replace(',','')
    return cleanNum.isdigit()


# return to market
def returnMarketStash():
    while not locateOnScreen('selectedMyListings', region=config.regionMarketListings):
        pyautogui.moveTo(config.xMyListings, config.yMyListings, duration=0.1) 
        pyautogui.click()  

    time.sleep(0.25)


def seperateRollValues(s):
    # Use re.findall to extract both numbers and text in order
    parts = re.findall(r'\d+%?|\D+', s)
    
    # Clean up the parts by trimming extra whitespace from text
    parts = [part.strip() for part in parts if part.strip()]

    return parts


# return if dark and darker is running
def is_game_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == config.GAME_NAME:
            return True
    return False


# find .exe path
def findExecPath(appName):
    for path in config.execSearchPaths:
        for root, dirs, files in os.walk(path):
            if appName in files:
                return os.path.join(root, appName)
    return None


# Select Rarity from market gui
def searchRarity(rarity) -> bool: # True/False select
    if rarity.lower() == "poor":
        pyautogui.moveTo(config.xPoor, config.yPoor, duration=0.1) 
    elif rarity.lower() == "common":
        pyautogui.moveTo(config.xCommon, config.yCommon, duration=0.1) 
    elif rarity.lower() == "uncommon":
        pyautogui.moveTo(config.xUncommon, config.yUncommon, duration=0.1) 
    elif rarity.lower() == "rare":
        pyautogui.moveTo(config.xRare, config.yRare, duration=0.1) 
    elif rarity.lower() == "epic":
        pyautogui.moveTo(config.xEpic, config.yEpic, duration=0.1) 
    elif rarity.lower() == "legendary":
        pyautogui.moveTo(config.xLegend, config.yLegend, duration=0.1) 
    elif rarity.lower() == "unique":
        pyautogui.moveTo(config.xUnique, config.yUnique, duration=0.1) 
    
    ss = pyautogui.screenshot(region=config.ssRaritySearch)
    pyautogui.click()
    ret = confirmGameScreenChange(ss,region=config.ssRaritySearch)

    if ret:
        logging.debug(f"Searching... {rarity}")
    else:
        logging.debug("FAILED! Search Rarity... Retrying")
    return ret


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


def getItemDetails():
    targetFilter = 315
    targetColor = 150
    limitWhite = 200
    screenshot = pyautogui.screenshot(region=config.StashCoords)
    screenshot.save('debug/test.png')
    img = Image.open('debug/test.png')

    #Mask with blue to see attributes
    img = img.convert("RGB")
    data = img.getdata()
    newData = []

    for item in data:
        if item[0] >= targetColor or item[1] >= targetColor or item[2] >= targetColor:
            if item[0] >= limitWhite and item[1] >= limitWhite and item[2] >= limitWhite:
                newData.append((0,0,0))
            else:
                newData.append(item)
        else:
            newData.append((0,0,0))

    img.putdata(newData)
    rawItemData = pytesseract.image_to_string(img)
    logDebug(f"Raw Item Data:\n{rawItemData}")
    img.save('debug/final.png')
    return rawItemData


# remove junk text and get good item reading
def filterItemText(rawItem):
    weaponToSell = []
    rawItem = rawItem.splitlines()

    with open("config/items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    with open("config/rolls.txt", 'r') as file:
        lines = file.readlines()
    allRolls = [line.strip() for line in lines]

    itemName = getItemTitle()
    if itemName == None:
        print("RETURN NONE")
        return None
    weaponToSell.append(itemName)

    for textLines in rawItem:
        txt = ''.join(char for char in textLines if char.isalpha() or char == ' ')
        found = findItem(textLines,allRolls)
        if found:
            if found == 'Move Speed' or found == 'Weapon Damage':
                continue
            weaponToSell.append(found)
        else:
            continue
    
    itemRarity = getItemRarity()
    weaponToSell.append(itemRarity)
    print("selling: ...")
    print(weaponToSell)
    return(weaponToSell)
    

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
    try:
        for y in range(6):
            for x in range(12):

                xHome = config.xStashStart
                yHome = config.yStashStart
                undercut = config.undercutValue
                newYCoord = yHome + (40 *y)
                newXCoord = xHome +(40 *x)

                if not detectItem(41 * x,41 * y):
                    continue
                else:
                    for i in range (5):
                        if not x and not y: break
                        clickAndDrag(newXCoord,newYCoord, xHome - 15, yHome - 20,0.2)
                        if not detectItem(41 * x,41 * y):
                            break
                
                pyautogui.moveTo(xHome, yHome)
                rawWeapon = getItemDetails()
                weapon = filterItemText(rawWeapon)
                if weapon == None:
                    logDebug("No Weapon found ... going next cube")
                    continue
                price = searchAndFindPrice(weapon)
                print(price)
                sellPrice = price + undercut if undercut < 0 else int(price - (price * (0.01 * undercut)))
                returnMarketStash()

                # handle goot loot / inventory dump
                if sellPrice <= 15:
                    itemMoveInventory()
                    if getItemTitle():
                        dumpInventory()
                        navToMarket()
                else:
                    success = listItem(sellPrice)

                    if not success:
                        raise NoListingSlots
                    logDebug("SUCCESS!!! " + str(weapon[0]) + 
                                " Listed at " + str(price) + "\n")
                returnMarketStash()
                    
    except NoListingSlots:
        logDebug("No Weapon found ... its actually over bro ...")


# creates and returns item class from hovered item 
def getItemInfo() -> item:
    #vars
    global allItems
    global allRolls
    coords = []
    name = ""
    rolls = []
    foundName = False

    #check if item is on screen
    space = locateOnScreen('findItem',confidence=0.95)
    if not space: return None

    x, y = pyautogui.position()
    coords = [x,y]
    #screenshot for text & rarity
    ssRegion = (int(space[0]) - 110, int(space[1]) - 360, 335, 550)
    rarity = getItemRarity(ssRegion)
    ss = pyautogui.screenshot(region=ssRegion)
    ss.save("lestest.png")
    text = pytesseract.image_to_string(ss)
    name = ""
    rolls = []
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    lines = text.splitlines()

    #iterate read text
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


# Main Loop for selling items
def mainLoop():
    global running
    launchedGame = 0
    while True:
        if is_game_running():
            print(f"{config.GAME_NAME} is running.")
            
            with open('debug.txt', 'w') as file:
                file.write('reset\n')
            navToMarket()
            time.sleep(0.3)
            selectStash(True)
            time.sleep(0.3)
            searchStash()
            break  
        else:
            if not launchedGame:
                print(f"{config.GAME_NAME} is not running. Launching...\n")

                # Ironshield doesn't like this solution ... 
                # subprocess.Popen(DAD_Utils.findExecPath(coords.GAME_NAME))
                # launchedGame = 1

                sys.exit(f"{config.GAME_NAME} is NOT running. Launch Dark and Darker\n")
                return 0

        time.sleep(5)  # Wait 5 seconds before checking again

    return 1