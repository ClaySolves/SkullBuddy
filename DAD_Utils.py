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

def getItemTitle():
    targetColor = 130    
    ss = pyautogui.screenshot(region=[coords.xStashStart,coords.yStashStart,coords.xTitleAdd,coords.yTitleAdd])
    ss = ss.convert("RGB")
    data = ss.getdata()
    newData = []

    for item in data:
        if item[0] >= targetColor or item[1] >= targetColor:
            newData.append(item)
        else:
            newData.append((0,0,0))

    ss.putdata(newData)
    ss.save('testingTitle.png')

    txt = pytesseract.image_to_string("testingTitle.png",config="--psm 6")

    with open('debug.txt', 'a') as file:
        file.write("got text: " + str(txt))

    # filteredText = filterGarbage(txt.split())
    # filteredText = ' '.join(filteredText)
    # print(filteredText)

    with open("items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    txt = txt.splitlines()
    for line in txt:
        print(line)
        item = findItem(line,allItems)
        print("found: " + str(item))
        if item:
            break
    print(txt)
    
    if item == None:
        sys.exit("ERROR, COULDN'T FIND ITEM")
    else:
        return item



def listItem(price):
    pyautogui.click()
    time.sleep(0.4)

    pyautogui.moveTo(coords.xSellingPrice, coords.ySellingPrice, duration=0.1) 
    pyautogui.click()
    pyautogui.typewrite(str(price), interval=0.01)

    pyautogui.moveTo(coords.xCreateListing, coords.yCreateListing, duration=0.1) 
    pyautogui.click()

    pyautogui.moveTo(coords.xConfirmListing, coords.yConfirmListing, duration=0.1) 
    pyautogui.click()



def findItem(input_string, phrase_list):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None



def sanitizeNumerRead(num):
    cleanNum = num.replace(',','')
    return cleanNum.isdigit()



def returnMarketStash():
    pyautogui.moveTo(coords.xMyListings, coords.yMyListings, duration=0.1) 
    pyautogui.click()  

    time.sleep(0.25)



def is_game_running():
    # Iterate through all running processes
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == coords.GAME_NAME:
            return True
    return False



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



def searchAndFindPrice(weapon):
    #reset filters and search rarity
    with open('debug.txt', 'a') as file:
            file.write("Searching for : " + str(weapon[-1]) + ' ' + str(weapon[0])  + '\n')

    pyautogui.moveTo(coords.xViewMarket, coords.yViewMarket, duration=0.1) 
    pyautogui.click()  

    pyautogui.moveTo(coords.xResetFilters, coords.yResetFilters, duration=0.5) 
    pyautogui.click() 

    pyautogui.moveTo(coords.xRarity, coords.yRarity, duration=0.1) 
    pyautogui.click()

    if not searchRarity(weapon[-1]):
        with open('debug.txt', 'a') as file:
            file.write("No rarity was found... Let's guess off the amount of rolls\n")
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
        if length == 5:
            weapon.append("Unique")
        searchRarity(weapon[-1])
        
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
    price.append(getItemCost())

    for weaponRolls in weapon[1:-1]:
        pyautogui.moveTo(coords.xResetAttribute, coords.yResetAttribute, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xAttribute, coords.yAttribute, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xAttrSearch, coords.yAttrSearch, duration=0.1) 
        pyautogui.click()
        pyautogui.typewrite(weaponRolls, interval=0.01)

        with open('debug.txt', 'a') as file:
            file.write("attr : " + str(weaponRolls) + '\n')

        pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect, duration=0.1) 
        pyautogui.click()

        pyautogui.moveTo(coords.xSearchPrice, coords.ySearchPrice, duration=0.1) 
        pyautogui.click()
        time.sleep(1)
        price.append(getItemCost())
        
    #If attr raises price >25%, we're gonna comp it with other attr's
    #Get max index and search that
    maxPrice = max(price)
    maxIndex = price.index(maxPrice)
    bestAttr = weapon[maxIndex]

    if maxIndex != 0 and ((maxPrice > price[0] + (price[0] * 0.25)) or (maxPrice > price[0] + 50)):
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
                with open('debug.txt', 'a') as file:
                    file.write('Skipping already selected attr\n')
                continue

            with open('debug.txt', 'a') as file:
                file.write("attr : " + str(attr) + " " + str(bestAttr) + '\n')

            pyautogui.moveTo(coords.xAttrSearch, coords.yAttrSearch, duration=.2) 
            pyautogui.click()
            pyautogui.typewrite(attr, interval=0.01)

            pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect + 25, duration=.2) 
            pyautogui.click()

            pyautogui.moveTo(coords.xSearchPrice, coords.ySearchPrice, duration=.2) 
            pyautogui.click()
            time.sleep(1)
            twoPrice.append(getItemCost())

            pyautogui.moveTo(coords.xAttribute, coords.yAttribute, duration=.2) 
            pyautogui.click()

            pyautogui.moveTo(coords.xAttrSelect, coords.yAttrSelect + 25, duration=.2) 
            pyautogui.click()

        if twoPrice:    
            maxTwoPrice = max(twoPrice)
            realMax = max(maxTwoPrice,maxPrice)
        else:
            realMax = maxPrice
        ret = math.floor(realMax - (realMax * (0.01 * coords.undercutPercent)))
        return(ret)
    else:
        return maxPrice



def getItemCost():
    targetColor = 120
    getRidCoin = 50
    numCompares = coords.numComps
    attempts = 10
    count = 1
    avgPrice = 0
    
    # Take screenshot of price area and record attempts. If issues getting price, increase the amount recorded.
    # If can't find good price, return negative highest value found
    while(count < attempts):
        coords.xPriceCoords
        xCoordadd = 140 + random.randint(1,50)
        yCoordadd = (65 * numCompares) + random.randint(1,30) 

        # with open('debug.txt', 'a') as file:
        #     file.write("x : " + str(coords.xPriceCoords)  + '\n')
        #     file.write("y : " + str(coords.yPriceCoords)  + '\n')
        #     file.write("xadd : " + str(xCoordadd)  + '\n')
        #     file.write("yadd : " + str(yCoordadd)  + '\n')

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

        txt = pytesseract.image_to_string("testing.png",config="--psm 6")

        numList = txt.split()
        
        newNums = [int(num.replace(',','')) for num in numList if sanitizeNumerRead(num)]
        
        with open('debug.txt', 'a') as file:
            file.write("Price : " + str((newNums)) + '\n')

        #if we are missing value or read 0 reread with more comps
        divCheck = len(newNums)
        if divCheck == 0 or divCheck != coords.numComps:
            count += 1
            numCompares += 1
            continue

        avgPrice = math.floor(sum(newNums) / divCheck)

        #this block filters out higher listing prices for faster selling
        for count, nums in enumerate(newNums):
            if nums != newNums[-1]:
                if newNums[count] + 50 > newNums[count + 1] or newNums[count] + (newNums[count] * 0.65) > newNums[count + 1]:
                    if abs(newNums[count] - avgPrice) > abs(newNums[count + 1] - avgPrice):
                        newNums.remove(nums)
                    else:
                        newNums.remove(newNums[count + 1])

        avgPrice = math.floor(sum(newNums) / len(newNums))

        return avgPrice
    
    with open('debug.txt', 'a') as file:
            file.write("Not Enough Legit Comps for this roll:" + str(newNums) + '\n')
    
    return 0



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
    with open('debug.txt', 'a') as file:
        file.write(rawItemData)

    img.save('final.png')

    return rawItemData




def filterItemText(rawItem):
    weaponToSell = []

    # with open("debug.txt", 'a') as file:
    #     file.write(rawItem)

    rawItem = rawItem.splitlines()

    with open("items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    with open("rolls.txt", 'r') as file:
        lines = file.readlines()
    allRolls = [line.strip() for line in lines]

    itemName = getItemTitle()
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
            #print("ERROR: ROLL NOT FOUND")
    
    print("selling: ...")
    print(weaponToSell)
    return(weaponToSell)
    
    

def changeClass():
    pyautogui.moveTo(coords.xPlay, coords.yPlay, duration=0.1)  
    pyautogui.click()  # Perform a mouse click

    pyautogui.moveTo(coords.xChangeClass,coords.yChangeClass,duration=0.1)
    pyautogui.click()

    time.sleep(3)

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

def clickAndDrag(xStart, yStart, xEnd, yEnd, duration=0.2):
    """
    Click and drag from startPos to endPos over a specified duration.
    
    Parameters:
        startPos (tuple): The (x, y) coordinates to start dragging from.
        endPos (tuple): The (x, y) coordinates to drag to.
        duration (float): The duration to complete the drag operation.
    """
    pyautogui.moveTo(xStart, yStart)  # Move to the starting position
    pyautogui.mouseDown()        # Press and hold the mouse button
    time.sleep(0.1)              # Optional: Wait a moment for the cursor to settle
    pyautogui.moveTo(xEnd, yEnd, duration=duration)  # Drag to the destination position
    pyautogui.mouseUp()          # Release the mouse button



def searchStash():
    for i in range(1):
        for j in range(2):
            xHome = coords.xStashStart
            yHome = coords.yStashStart
            newXCoord = xHome + (40 *j)
            newYCoord = yHome +(40 *i)
            clickAndDrag(newXCoord,newYCoord, xHome, yHome,0.5)
                
            rawWeapon = getItemDetails()
            weapon = filterItemText(rawWeapon)
            price = searchAndFindPrice(weapon)
            returnMarketStash()
            listItem(price)
            returnMarketStash() 