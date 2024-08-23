xTrade, yTrade = 1109, 37
xCloseWindow, yCloseWindow = 310, 37
xAttribute, yAttribute = 1565, 201
xResetAttribute, yResetAttribute = 1673, 200
xAttrSearch, yAttrSearch = 1575, 245
xAttrSelect, yAttrSelect = 1575, 276
xMarket, yMarket = 1176, 244
xViewMarket, yViewMarket = 847, 118
xMyListings, yMyListings = 1056, 119
xSellingPrice, ySellingPrice = 1074, 624
xItemName, yItemName = 211, 198
xItemSearch, yItemSearch = 150, 243
xItemSelect, yItemSelect = 127, 278
xPoor, yPoor = 300, 275
xCommon, yCommon = 300, 300
xUncommon, yUncommon = 300, 325
xRare, yRare = 300, 350
xRarity, yRarity = 375, 200
xEpic, yEpic = 300, 375
xLegend, yLegend = 300, 400 
xUnique, yUnique = 300, 425
xCreateListing, yCreateListing = 944, 963
xConfirmListing, yConfirmListing = 859, 617
xCanListing, yCanListing = 1049, 617
xLeaveTrading, yLeaveTrading = 145, 139
xPlay, yPlay = 315, 37
xChangeClass, yChangeClass = 1852, 1010
StashCoords = (1289, 0, 620, 1059)
xStashStart, yStashStart = 1390, 213
priceCoords = (1452, 324, 180, 180) # for add its x + 60 y + 150
xResetFilters, yResetFilters = 1790, 201
xSearchPrice, ySearchPrice = 1788, 273

import math
import psutil
import pyautogui
import time
import pytesseract
from PIL import Image, ImageOps
import difflib

# Replace 'game.exe' with the actual name of the game's process
GAME_NAME = "DungeonCrawler.exe"

def findItem(input_string, phrase_list):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None

def is_game_running():
    # Iterate through all running processes
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == GAME_NAME:
            return True
    return False

def searchAndFindPrice(weapon):
    #reset filters and search item name
    pyautogui.moveTo(xViewMarket, yViewMarket, duration=.5) 
    pyautogui.click()  

    pyautogui.moveTo(xResetFilters, yResetFilters, duration=.5) 
    pyautogui.click()  

    pyautogui.moveTo(xItemName, yItemName, duration=.5) 
    pyautogui.click()  

    pyautogui.moveTo(xItemSearch, yItemSearch, duration=.5) 
    pyautogui.click() 
    pyautogui.typewrite(weapon[0], interval=0.05)

    pyautogui.moveTo(xItemSelect, yItemSelect, duration=.5) 
    pyautogui.click() 

    #select rarity
    pyautogui.moveTo(xRarity, yRarity, duration=.2) 
    pyautogui.click()

    if weapon[-1] == "Poor":
        pyautogui.moveTo(xPoor, yPoor, duration=.2) 
        pyautogui.click()
    elif weapon[-1] == "Common":
        pyautogui.moveTo(xCommon, yCommon, duration=.2) 
        pyautogui.click()
    elif weapon[-1] == "Uncommon":
        pyautogui.moveTo(xUncommon, yUncommon, duration=.2) 
        pyautogui.click()
    elif weapon[-1] == "Rare":
        pyautogui.moveTo(xRare, yRare, duration=.2) 
        pyautogui.click()
    elif weapon[-1] == "Epic":
        pyautogui.moveTo(xEpic, yEpic, duration=.2) 
        pyautogui.click()
    elif weapon[-1] == "Legendary":
        pyautogui.moveTo(xLegend, yLegend, duration=.2) 
        pyautogui.click()
    elif weapon[-1] == "Unique":
        pyautogui.moveTo(xUnique, yUnique, duration=.2) 
        pyautogui.click() 
    else:
        print("ERROR, WRONG RARITY!!! TS SHOULD NOT SHOW IN TERMINAL")

    price = []

    for weaponRolls in weapon[1:-1]:
        pyautogui.moveTo(xResetAttribute, yResetAttribute, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(xAttribute, yAttribute, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(xAttrSearch, yAttrSearch, duration=.2) 
        pyautogui.click()
        pyautogui.typewrite(weaponRolls, interval=0.05)

        pyautogui.moveTo(xAttrSelect, yAttrSelect, duration=.2) 
        pyautogui.click()

        pyautogui.moveTo(xSearchPrice, ySearchPrice, duration=.02) 
        pyautogui.click()
        time.sleep(3)
        price.append(getItemCost())
        
    print(price)



def searchStash():
    for i in range(1):
        for j in range(1):
            pyautogui.moveTo(xStashStart + (40 *j), yStashStart +(40 *i),duration=0.15) # moves to each stash square
            getItemDetails()



def getItemCost():
    targetColor = 120
    getRidCoin = 50

    ss = pyautogui.screenshot(region=priceCoords)
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
    numbers = [int(num) for num in numList]
    avgPrice = math.floor(sum(numbers) / 3)

    return avgPrice



def navCharLogin():

    xChar, yChar = 1750, 200 # coords for char location
    pyautogui.moveTo(xChar, yChar, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click

    xLobby, yLobby = 960, 1000  # coords for enter lobby location
    pyautogui.moveTo(xLobby, yLobby, duration=0.1)  # Move the mouse to (x, y) over 1 second
    pyautogui.click()  # Perform a mouse click
    time.sleep(7)



def getItemDetails():

    targetColor = 130
    screenshot = pyautogui.screenshot(region=StashCoords)
    screenshot.save('test.png')

    
    img = Image.open('test.png')

    #Mask with blue to see attributes
    img = img.convert("RGB")

    data = img.getdata()
    newData = []

    for item in data:
        if item[0] >= targetColor or item[1] >= targetColor or item[2] >= targetColor:
            newData.append(item)
        else:
            newData.append((0,0,0))

    img.putdata(newData)

    txt = pytesseract.image_to_string(img)
    with open('debug.txt', 'w') as file:
        file.write(txt)

    img.save('final.png')

    filterItemText()



def filterItemText():

    weaponToSell = []

    keywords = [
        "Strength", "Agility", "Dexterity", "Will", "Knowledge", "Vigor", "Resourcefulness",
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

    with open('debug.txt', 'r') as infile:
        lines = infile.readlines()

    filteredText = []
    for line in lines:
        if any(keyword in line for keyword in keywords):
            filteredText.append(line)

    with open('loot.txt', 'w') as outfile:
        outfile.writelines(filteredText)

    with open("items.txt", 'r') as file:
        lines = file.readlines()
    allItems = [line.strip() for line in lines]

    with open("rolls.txt", 'r') as file:
        lines = file.readlines()
    allRolls = [line.strip() for line in lines]

    itemName = findItem(filteredText[0],allItems)
    if itemName:
        weaponToSell.append(itemName)
        filteredText.pop(0)
    else:
        print("ERROR: ITEM NOT FOUND")

    for textLines in filteredText:
        found = findItem(textLines,allRolls)
        if found:
            if found == 'Move Speed' or found == 'Weapon Damage':
                continue
            weaponToSell.append(found)
        else:
            print("ERROR: ROLL NOT FOUND")
            
    print("selling: ...")

    print(weaponToSell)
    print("done")

    searchAndFindPrice(weaponToSell)

    
    
    

def changeClass():
    pyautogui.moveTo(xPlay, yPlay, duration=0.1)  
    pyautogui.click()  # Perform a mouse click

    pyautogui.moveTo(xChangeClass,yChangeClass,duration=0.1)
    pyautogui.click()

    time.sleep(3)



def main():
    while True:
        if is_game_running():
            print(f"{GAME_NAME} is running.")
            #navCharLogin()  # Call your automation function
            #getItemDetails()
            #changeClass()
            searchStash()
            #getItemCost()
            break  # Stop after performing the action, or remove this if you want continuous automation
        else:
            print(f"{GAME_NAME} is not running.")
        
        time.sleep(5)  # Wait 5 seconds before checking again

if __name__ == "__main__":
    main()
    print("Finished/n")
