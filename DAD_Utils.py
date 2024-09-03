import math
import sys
import numbers
import psutil
import pyautogui
import time
import pytesseract
from PIL import Image, ImageOps
import difflib
import coords
import random
import os

class NoListingSlots(Exception):
    pass



#moves item in coords to/from inventor
def itemMoveInventory(x=coords.xStashStart,y=coords.yStashStart,attempt=1):
    pyautogui.moveTo(x,y)
    pyautogui.keyDown('shift')
    time.sleep(0.1)
    pyautogui.click(button='right')
    pyautogui.keyUp('shift')
    if attempt > 4: 
        pass
    elif getItemTitle(): 
        attempt += 1
        itemMoveInventory(attempt)


#Nav to stash from market and dump into coords.dumpStash
def dumpInventory():
    pyautogui.moveTo(coords.xExitMarket,coords.yExitMarket) 
    pyautogui.click()

    pyautogui.moveTo(coords.xExitMarketYes,coords.yExitMarketYes,duration=0.1) 
    pyautogui.click()
    time.sleep(0.5)

    pyautogui.moveTo(coords.xStashSelect,coords.yStashSelect,duration=0.1) 
    pyautogui.click()

    if not getCurrentScreen('selectedStash'): dumpInventory()

    for y in range(5):
        for x in range(10):
            xInv = coords.xInventory
            yInv = coords.yInvetory
            if not detectItem(41 * x, 41 * y,xInv,yInv):
                print(f'Continue{x}{y}')
                continue
            else:
                itemMoveInventory(xInv + (41 * x),yInv + (41 * y))





def logDebug(txt):
    with open('debug.txt', 'a') as file:
        file.write(f"{txt}\n")    



def checkForSold():
    ss = pyautogui.screenshot(region=coords.listingSoldRegion)
    ss.save("TestingGatherGold.png")
    soldLocation = locateOnScreen("betterSoldItem",coords.listingSoldRegion,True,0.95)
    if soldLocation:
        pyautogui.moveTo(int(soldLocation[0] + 30), int(soldLocation[1]), duration=0.05) 
        pyautogui.click()

        pyautogui.moveTo(coords.xCanOrTransfer, coords.yCanOrTransfer, duration=0.05) 
        pyautogui.click()

        logDebug("gathered gold")
        time.sleep(3)
        checkForSold()

    else: logDebug("Nothing found")



#return 1 if img on screen else return location
def getCurrentScreen(img):
    logDebug(f'Checking screen for: img/{img}.png')

    try:
        pyautogui.locateOnScreen(f'img/{img}.png', confidence=0.98)
        logDebug("SCREEN DETECTED!")
        return 1
    except pyautogui.ImageNotFoundException as e:
        logDebug("NOT FOUND: " + str(e))
        return 0



# Read image text and confirm the rarity
def confirmRarity(img,rarity):

    left = int(img.left)
    top = int(img.top)
    width = int(img.width)
    height = int(img.height)
    ssRegion=(left, top, width, height)
    ss = pyautogui.screenshot(region=ssRegion)
    ss.save('readText.png')
    txt = pytesseract.image_to_string('readText.png', config="--psm 6")
    if rarity.lower() in txt.lower():
        return 1
    else:
        return 0



# Return location and santize ImageNotFound error
def locateOnScreen(img,region,grayscale=False,confidence=0.99):
    try:
        res = pyautogui.locateOnScreen(f'img/{img}.png', region = region, 
                                       confidence = confidence, grayscale = grayscale)
        logDebug(f"Found: {img}\n") 
        return res 
    except pyautogui.ImageNotFoundException as e:
        logDebug(f"{img} was not found\n") 
        return None
        

# Returns the rarity of the item in top left 
def getItemRarity():
    pyautogui.moveTo(coords.xStashStart,coords.yStashStart,duration=0.1)
    ret = None

    poorDetect = locateOnScreen('poor', region=coords.firstSlotItemDisplayRegion)
    if poorDetect:
        if confirmRarity(poorDetect,'poor'):
            print('its poor\n')
            ret = 'poor'
    time.sleep(0.002)

    commonDetect = locateOnScreen('common', region=coords.firstSlotItemDisplayRegion)
    if commonDetect:
        if confirmRarity(commonDetect,'common'):
            print('its common\n')
            ret = 'common'
    time.sleep(0.002)

    uncommonDetect = locateOnScreen('uncommon', region=coords.firstSlotItemDisplayRegion)
    if uncommonDetect:
        if confirmRarity(uncommonDetect,'uncommon'):
            print('its uncommon\n')
            ret = 'uncommon'
    time.sleep(0.002)

    rareDetect = locateOnScreen('rare', region=coords.firstSlotItemDisplayRegion)
    if rareDetect:
        if confirmRarity(rareDetect,'rare'):
            print('its rare\n')
            ret = 'rare'
    time.sleep(0.002)

    epicDetect = locateOnScreen('epic', region=coords.firstSlotItemDisplayRegion)
    if epicDetect:
        if confirmRarity(epicDetect,'epic'):
            print('its epic\n')
            ret = 'epic'
    time.sleep(0.002)

    legendaryDetect = locateOnScreen('legendary', region=coords.firstSlotItemDisplayRegion)
    if legendaryDetect:
        if confirmRarity(legendaryDetect,'legendary'):
            print('its legendary\n')
            ret = 'legendary'
    time.sleep(0.002)

    uniqueDetect = locateOnScreen('unique', region=coords.firstSlotItemDisplayRegion)
    if uniqueDetect:
        if confirmRarity(uniqueDetect,'unique'):
            print('its unique\n')
            ret = 'unique'
    time.sleep(0.002)

    if ret:
        logDebug(f"Found {ret} item\n")  
    else:
        logDebug("ERROR!!! NO RARITY FOUND\n") 

    return ret   



# detects if item is in stash on given coord offset
def detectItem(xAdd,yAdd,xStart=coords.xStashDetect,yStart=coords.yStashDetect):
    ss = pyautogui.screenshot(region=[xStart + xAdd,yStart + yAdd,20,20])
    ss = ss.convert("RGB")
    # ss.save(f"ssDebug/seeStash_x_{xAdd/41}_y_{yAdd/41}.png")
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



# Gathers gold from sold listings
def gatherGold():
    for i in range(10):
        time.sleep(0.1)
        pyautogui.moveTo(coords.xGatherGold, coords.yGatherGold - (i * 51), duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xCanOrTransfer, coords.yCanOrTransfer, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xConfirmNo, coords.yConfirmNo, duration=0.1) 
        pyautogui.click()



# Get the availible listing slots
def getAvailListings(secondRun):
    #Take screenshot and sanitize for read text
    ss = pyautogui.screenshot(region=[coords.xGetListings,coords.yGetListings,coords.x2GetListings,coords.y2GetListings])
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
    ss.save('testingTitle.png')
    ss.save('testingListItem.png')
    txt = pytesseract.image_to_string('testingListItem.png',config="--psm 6")
    txt = txt.splitlines()

    #Read for listing slots and report if any avial, and #of slots
    avail = 0
    slots = 0
    for lines in txt:
        if lines == 'List an Item':
            avail = 1
            slots += 1
        else:
            continue

    if avail:
        logDebug("YES! " + str(slots) + " listings availible\n")
    else:
        logDebug("NO LISTING SLOTS!, CLEAR GOLD ")

    if not avail and not secondRun:
        checkForSold()
        if not secondRun:
            avail, _ = getAvailListings(1)

    return avail, slots
    


# Get the title of an item on top left corner
def getItemTitle():
    # Take screenshot of title and filter data for text read
    targetColor = 130    
    ss = pyautogui.screenshot(region=[coords.xStashStart,coords.yStashStart,coords.xTitleAdd,coords.yTitleAdd])
    ss = ss.convert("RGB")
    data = ss.getdata()
    newData = []

    for pixel in data:
        if pixel[0] >= targetColor or pixel[1] >= targetColor:
            newData.append(pixel)
        else:
            newData.append((0,0,0))

    ss.putdata(newData)
    ss.save('testingTitle.png')
    txt = pytesseract.image_to_string("testingTitle.png",config="--psm 6")
    logDebug("got title text: " + str(txt) + "\n")

    # Search for item from txt and return result
    with open("items.txt", 'r') as file:
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
    avail, slots = getAvailListings(0)

    if(avail):
        pyautogui.moveTo(coords.xStashStart, coords.yStashStart, duration=0.1) 
        pyautogui.click()
        time.sleep(0.4)

        pyautogui.moveTo(coords.xSellingPrice, coords.ySellingPrice, duration=0.1) 
        pyautogui.click()
        pyautogui.typewrite(str(price), interval=0.01)

        pyautogui.moveTo(coords.xCreateListing, coords.yCreateListing, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xConfirmListing, coords.yConfirmListing, duration=0.1) 
        pyautogui.click()
        return 1
    else:
        return 0



# Lookup and return input_string from phrase_list
def findItem(input_string, phrase_list):
    logDebug("Searching for: " + str(input_string) + 
                   "from " + str(phrase_list[:3]) + "\n")

    closest_match = difflib.get_close_matches(input_string, phrase_list, n=1, cutoff=0.6)

    logDebug("Found: " + str(closest_match) + "\n")
    return closest_match[0] if closest_match else None



# Sanitize junk ascii from num
def sanitizeNumerRead(num):
    cleanNum = num.replace(',','')
    return cleanNum.isdigit()



# return to market
def returnMarketStash():
    pyautogui.moveTo(coords.xMyListings, coords.yMyListings, duration=0.1) 
    pyautogui.click()  

    time.sleep(0.25)



# return if dark and darker is running
def is_game_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == coords.GAME_NAME:
            return True
    return False



# find .exe path
def findExecPath(appName):
    for path in coords.execSearchPaths:
        for root, dirs, files in os.walk(path):
            if appName in files:
                return os.path.join(root, appName)
    return None



# Search market GUI for rarity
def searchRarity(rarity):
    if rarity == "Poor":
        pyautogui.moveTo(coords.xPoor, coords.yPoor, duration=0.1) 
        pyautogui.click()
    elif rarity == "Common":
        pyautogui.moveTo(coords.xCommon, coords.yCommon, duration=0.1) 
        pyautogui.click()
    elif rarity == "Uncommon":
        pyautogui.moveTo(coords.xUncommon, coords.yUncommon, duration=0.1) 
        pyautogui.click()
    elif rarity == "Rare":
        pyautogui.moveTo(coords.xRare, coords.yRare, duration=0.1) 
        pyautogui.click()
    elif rarity == "Epic":
        pyautogui.moveTo(coords.xEpic, coords.yEpic, duration=0.1) 
        pyautogui.click()
    elif rarity == "Legendary":
        pyautogui.moveTo(coords.xLegend, coords.yLegend, duration=0.1) 
        pyautogui.click()
    elif rarity == "Unique":
        pyautogui.moveTo(coords.xUnique, coords.yUnique, duration=0.1) 
        pyautogui.click() 
    else:
        return 0
    return 1



# Search market for item and find price
# return int>0 price, 0 if nothing, -1 if NICE LOOT
def searchAndFindPrice(weapon):
    #reset filters and search rarity
    pyautogui.moveTo(coords.xViewMarket, coords.yViewMarket, duration=0.1) 
    pyautogui.click()  

    pyautogui.moveTo(coords.xResetFilters, coords.yResetFilters, duration=0.5) 
    pyautogui.click() 

    pyautogui.moveTo(coords.xRarity, coords.yRarity, duration=0.1) 
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
    pyautogui.moveTo(coords.xItemName, coords.yItemName, duration=0.1) 
    pyautogui.click()  

    pyautogui.moveTo(coords.xItemSearch, coords.yItemSearch, duration=0.1) 
    pyautogui.click() 
    pyautogui.typewrite(weapon[0], interval=0.01)

    pyautogui.moveTo(coords.xItemSelect, coords.yItemSelect, duration=0.1) 
    pyautogui.click() 

    #Start reading price for each attribute starting with base item
    price = []
    pyautogui.moveTo(coords.xSearchPrice, coords.ySearchPrice, duration=0.1) 
    pyautogui.click()
    time.sleep(1)

    # Record base price, if no attr's than return
    basePrice = getItemCost()
    if len(weapon) == 2: return basePrice

    for weaponRolls in weapon[1:-1]:
        pyautogui.moveTo(coords.xResetAttribute, coords.yResetAttribute, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xAttribute, coords.yAttribute, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xAttrSearch, coords.yAttrSearch, duration=0.1) 
        pyautogui.click()
        pyautogui.typewrite(weaponRolls, interval=0.01)

        logDebug("attr : " + str(weaponRolls))

        pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xSearchPrice, coords.ySearchPrice, duration=0.1) 
        pyautogui.click()
        time.sleep(1)
        price.append(getItemCost(basePrice))
    
    #Check for NICE LOOT
    for prices in price:
        if prices == -1:
            return -1

    # If only one attr, skip more comps and return found price if signficant increase else basePrice
    if len(price) == 1:
        return basePrice if price[0] < basePrice + (basePrice * .10) else price[0]

    #If attr raises baseprice >25%, we're gonna comp it with other attr's
    #Get max index and search that
    maxPrice = max(price)
    maxIndex = price.index(maxPrice)
    bestAttr = weapon[maxIndex + 1]
    if maxIndex != 0 and ((maxPrice > basePrice + (basePrice * 0.25)) or (maxPrice > basePrice + 50)):
        pyautogui.moveTo(coords.xResetAttribute, coords.yResetAttribute, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(coords.xAttribute, coords.yAttribute, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(coords.xAttrSearch, coords.yAttrSearch, duration=.2) 
        pyautogui.click()
        pyautogui.typewrite(bestAttr, interval=0.01)

        pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect, duration=.2) 
        pyautogui.click()

        #add other attr to selected attr
        twoPrice = []
        for index, attr in enumerate(weapon[1:-1]):

            if index + 1 == maxIndex:
                logDebug('Skipping already selected attr')
                continue

            logDebug("attr : " + str(attr) + " " + str(bestAttr))

            pyautogui.moveTo(coords.xAttrSearch, coords.yAttrSearch, duration=.2) 
            pyautogui.click()
            pyautogui.typewrite(attr, interval=0.01)

            pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect + 25, duration=.2) 
            pyautogui.click()

            pyautogui.moveTo(coords.xSearchPrice, coords.ySearchPrice, duration=.2) 
            pyautogui.click()
            time.sleep(1)
            twoPrice.append(getItemCost(basePrice))

            pyautogui.moveTo(coords.xAttribute, coords.yAttribute, duration=.2) 
            pyautogui.click()

            pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect + 25, duration=.2) 
            pyautogui.click()

        #Check for NICE LOOT
        for twoPrices in twoPrice:
            if twoPrices == -1:
                return -1
            
        return max(maxPrice,max(twoPrice))
    else:
        return maxPrice



# get average cost of displayed item in market lookup
def getItemCost(basePrice=None):
    targetColor = 120
    getRidCoin = 50
    numCompares = coords.numComps
    totalListings = coords.totalListings
    attempts = 10
    count = 1
    avgPrice = 0
    
    # Take screenshot of price area and record attempts. If issues getting price, increase the amount recorded.
    # If can't find good price, return negative highest value found
    # Goal is return the lowest reasonable price
    while(count < attempts):
        # get coords for price read and filter ss
        coords.xPriceCoords
        xCoordadd = 140 + random.randint(1,50)
        yCoordadd = (65 * numCompares) + random.randint(1,30) 
        ss = pyautogui.screenshot(region=[coords.xPriceCoords,coords.yPriceCoords,xCoordadd,yCoordadd])
        ss = ss.convert("RGB")
        data = ss.getdata()
        newData = []

        for item in data:
            if (item[0] >= targetColor or item[1] >= targetColor) and item[2] < getRidCoin:
                newData.append(item)
            else:
                newData.append((0,0,0))

        ss.putdata(newData)
        ss.save('testing.png')

        # Read and sanitize text
        txt = pytesseract.image_to_string("testing.png",config="--psm 6")
        numList = txt.split()
        newNums = [int(num.replace(',','')) for num in numList if sanitizeNumerRead(num)]  

        # Value correction, check for improper reads and remove
        for i in range(len(newNums)-1,-1,-1):
            if newNums[i] == newNums[0]:
                break
            if newNums[i] < newNums[i-1]:
                newNums[i].pop(i)

        #if we are missing value or read 0 reread with more comps
        divCheck = len(newNums)
        if divCheck < coords.numComps:
            if count + 1 == attempts:
                if sum(newNums):
                    logDebug(f"Didn't get to {coords.numComps} but we got a price, so use it")
                else: 
                    break
            else:    
                count += 1
                numCompares += 1
                continue

        logDebug("Recorded Price : " + str((newNums)) + '\n')
        avgPrice = math.floor(sum(newNums) / divCheck)

        # get rid of outliers
        for i, nums in enumerate(newNums):
            if nums == newNums[-1]:
                break
            else:
                if abs(nums - newNums[i+1]) > avgPrice * 0.4:
                    logDebug("Removing undercut value")
                    newNums[i] = 0

        logDebug("Recorded Price : " + str((newNums)) + '\n')

        if basePrice:
            for nums in newNums:
                if nums > basePrice * 1.6 and nums > coords.valueThreshold:
                    return -1

        for nums in newNums:
            if nums != 0:
                return nums
    
    logDebug("Not Enough Legit Comps for this roll:" + str(newNums) + '\n')
    
    return 0



# Navigate char login screen
def navCharLogin():
    xChar, yChar = 1750, 200 # coords for char location
    pyautogui.moveTo(xChar, yChar, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click

    xLobby, yLobby = 960, 1000  # coords for enter lobby location
    pyautogui.moveTo(xLobby, yLobby, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click
    time.sleep(7)



def getItemDetails():
    targetFilter = 315
    targetColor = 150
    limitWhite = 200
    screenshot = pyautogui.screenshot(region=coords.StashCoords)
    screenshot.save('test.png')
    img = Image.open('test.png')

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
    logDebug(rawItemData)

    img.save('final.png')
    return rawItemData



#
def filterItemText(rawItem):
    weaponToSell = []
    rawItem = rawItem.splitlines()

    with open("items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    with open("rolls.txt", 'r') as file:
        lines = file.readlines()
    allRolls = [line.strip() for line in lines]

    itemName = getItemTitle()
    if itemName == None:
        print("RETURN NONE")
        return None
    weaponToSell.append(itemName)

    for textLines in rawItem:
        #print(textLines)
        found = findItem(textLines,allRolls)

        if found:
            if found == 'Move Speed' or found == 'Weapon Damage':
                continue
            weaponToSell.append(found)
        else:
            continue
    
    print("selling: ...")
    print(weaponToSell)
    return(weaponToSell)
    
    

# Change class 
def changeClass():
    pyautogui.moveTo(coords.xPlay, coords.yPlay, duration=0.1)  
    pyautogui.click()  # Perform a mouse click

    pyautogui.moveTo(coords.xChangeClass,coords.yChangeClass,duration=0.1)
    pyautogui.click()

    time.sleep(3)



# Get rid of this garbage unused function
def filterGarbage(text):
    keywords = [
        "Bane", "Strength", "Agility", "Dexterity", "Will", "Knowledge", "Vigor", "Resourcefulness",
        "Armor", "Penetration", "Additional", "Physical", "Damage", "Bonus", "Weapon", "Add",
        "Power", "Magic", "True", "Rating", "Resistance", "Reduction", "Projectile", "Mod", "Action",
        "Speed", "Move", "Regular", "Interaction", "Magical", "Spell", "Casting", "Buff", "Duration",
        "Max", "Health", "Luck", "Healing", "Debuff", "Memory", "Capacity", "Arming", "Sword", "Crystal",
        "Falchion", "Heater", "Shield", "Longsword", "Rapier", "Lantern", "Short", "Zweihander",
        "Viking", "Buckler", "Round", "Club", "Flanged", "Mace", "Lute", "Pavise", "Morning", "Star",
        "Quarterstaff", "Torch", "War", "Hammer", "Maul", "Castillon", "Dagger", "Kris", "Rondel",
        "Stiletto", "Bardiche", "Halberd", "Spear", "Ball", "Battle", "Axe", "Double", "Recurve",
        "Bow", "Spellbook", "Felling", "Hatchet", "Staff", "Horseman's", "Ceremonial", "Longbow",
         "Crossbow", "Windlass", "Fighter", "Survival", "Armet", "Barbuta", "Helm", "Chapel",
        "De", "Fer", "Chaperon", "Crusader", "Darkgrove", "Hood", "Elkwood", "Crown", "Feathered",
        "Forest", "Gjermundbu", "Great", "Hounskull", "Kettle", "Leather", "Bonnet", "Cap", "Norman",
        "Nasal", "Occultist", "Open", "Sallet", "Ranger", "Rogue", "Cowl", "Shadow", "Mask",
        "Spangenhelm", "Straw", "Topfhelm", "Visored", "Wizard", "Adventurer", "Tunic",
        "Champion", "Dark", "Cuirass", "Plate", "Robe", "Doublet", "Fine", "Frock", "Grand",
        "Brigandine", "Heavy", "Gambeson", "Light", "Aketon", "Marauder", "Outfit", "Mystic", "Vestments",
        "Northern", "Full", "Oracle", "Ornate", "Jazerant", "Padded", "Pourpoint", "Regal", "Ritual",
        "Studded", "Chausses", "Loose", "Trousers", "Leggings", "Bardic", "Cloth", "Copperlight",
        "Pants", "Gloves", "Utility", "Gauntlets", "Rawhide", "Reinforced", "Riveted", "Runestone",
        "Boots", "Buckled", "Darkleaf", "Dashing", "Laced", "Lightfoot", "Low", "Old",
        "Rugged", "Stitched", "Turnshoe", "Shoes", "Mercurial", "Radiant", "Splendid",
        "Tattered", "Vigilant", "Watchman", "Badger", "Pendant", "Bear", "Fangs", "Death", "Necklace",
        "Fox", "Frost", "Amulet", "Monkey", "Peace", "Owl", "Ox", "Phoenix", "Choker", "Wisdom",
        "Vitality", "Resolve", "Quickness", "Finesse", "Courage", "Grimsmile", "Legendary", "Epic", "Rare", "Uncommon", "Common", "Poor"
    ]
    
    filteredText = []

    if len(text) != 1:
        for line in text:
            if any(keyword in line for keyword in keywords):
                filteredText.append(line)
    else:
        if any(keyword in line for keyword in keywords):
                filteredText.append(line)

    return filteredText



# moves mouse from start to end
def clickAndDrag(xStart, yStart, xEnd, yEnd, duration=0.1):
    pyautogui.moveTo(xStart, yStart)  # Move to the starting position
    pyautogui.mouseDown()        # Press and hold the mouse button
    time.sleep(0.1)              # Optional: Wait a moment for the cursor to settle
    pyautogui.moveTo(xEnd, yEnd, duration=duration)  # Drag to the destination position
    time.sleep(0.05)   
    pyautogui.mouseUp()          # Release the mouse button



# Main script call. Search through all stash cubes, drag item to first, and sell
def searchStash():
    try:
        for y in range(20):
            for x in range(12):

                xHome = coords.xStashStart
                yHome = coords.yStashStart
                newYCoord = yHome + (40 *y)
                newXCoord = xHome +(40 *x)
                if not detectItem(41 * x,41 * y):
                    continue
                clickAndDrag(newXCoord,newYCoord, xHome - 20, yHome - 20,0.2)
                    
                rawWeapon = getItemDetails()
                weapon = filterItemText(rawWeapon)
                if weapon == None:
                    logDebug("No Weapon found ... going next cube")
                    continue
                price = searchAndFindPrice(weapon)
                returnMarketStash()

                success = listItem(price)
                returnMarketStash()
                if not success:
                    raise NoListingSlots
                logDebug("SUCCESS!!! " + str(weapon[0]) + 
                         " Listed at " + str(price) + "\n")
                    
    except NoListingSlots:
        logDebug("No Weapon found ... its actually over bro ...")