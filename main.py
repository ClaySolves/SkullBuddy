xTrade, yTrade = 1109, 37
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

import math
import psutil
import pyautogui
import time
import pytesseract
from PIL import Image, ImageOps

# Replace 'game.exe' with the actual name of the game's process
GAME_NAME = "DungeonCrawler.exe"



def is_game_running():
    # Iterate through all running processes
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == GAME_NAME:
            return True
    return False



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

    print(avgPrice)



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

    print(lines)

    filteredText = []
    for line in lines:
        if any(keyword in line for keyword in keywords):
            print(line)
            filteredText.append(line)

    with open('loot.txt', 'w') as outfile:
        outfile.writelines(filteredText)
    
    

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
