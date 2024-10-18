import difflib
import DAD_Utils
import config
import time
import pyautogui

def findItem(input_string, phrase_list):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None

# str = '+ - +18 Luck -'
# str = ''.join([char for char in str if char.isalpha()])
# print(str)

# with open("rolls.txt", 'r') as file:
#         lines = file.readlines()
# allItems = [line.strip() for line in lines]

# res = findItem(str,allItems)


# print(DAD_Utils.findExecPath(coords.GAME_NAME))
# print(DAD_Utils.getCurrentScreen('selectedPlay'))
# time.sleep(0.2)
# print(DAD_Utils.getCurrentScreen('selectedTrade'))
# time.sleep(0.2)
# print(DAD_Utils.getCurrentScreen('selectedStash'))
# time.sleep(0.2)
# print(DAD_Utils.getCurrentScreen('showListingComplete'))
# time.sleep(0.2)
# print(DAD_Utils.getCurrentScreen('selectedTitleScreen'))
# time.sleep(0.2)
# print(DAD_Utils.getCurrentScreen('sharedStash'))
# time.sleep(0.2)
#weapon = ["Loose Trousers","Strength","Max Health","Max Health Bonus", "Epic"]
#print(DAD_Utils.searchAndFindPrice(weapon))
#print(          )
# print(DAD_Utils.locateOnScreen('selected iewMarket',region=coords.regionMarketListings))

# ss = pyautogui.screenshot(region=coords.regionMarketListings)
# ss.save('LOL.png')
# print(DAD_Utils.getItemSlotType())
# ss = pyautogui.screenshot(region=coords.getExpressmanRegion)
# ss.save('LOL.png')

# ss = pyautogui.screenshot(region=coords.getDungeonInvRegion)
# ss.save('LOL2.png')
# DAD_Utils.gatherExpressman()

time.sleep(1)
DAD_Utils.loadTextFiles()
item = DAD_Utils.getItemInfo()
item.findPrice()

# ret = DAD_Utils.seperateRollValues("Agility 66 Armor Rating")
# print(ret)

# time1 = time.time()
# slots = DAD_Utils.getAvailListings()
# DAD_Utils.checkForSold(slots)
# time2 = time.time()
# print(time2-time1)


# DAD_Utils.gatherSoldListings()
DAD_Utils.gatherSoldListings()


# var1 = "str"
# var2 = pyautogui.screenshot()

# print(f"{type(var1)} {type(var2)}")