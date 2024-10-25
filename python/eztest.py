import difflib
import DAD_Utils
import config
import time
import pyautogui


# pyautogui.mouseInfo()
DAD_Utils.loadTextFiles()

# time.sleep(2)
# item = DAD_Utils.getItemInfo()
# item.findPrice()

# _________________________________________________________________________________________

# while(True):
#     ss = pyautogui.screenshot(region=config.ssMarketRoll)
#     ss.save("hahaha.png")
#     print(DAD_Utils.confirmGameScreenChange(ss,config.ssMarketRoll))
#     time.sleep(1)

# _________________________________________________________________________________________
def mainLoop():
    DAD_Utils.loadTextFiles()
    time.sleep(2)
    mytime =time.time()
    myItem = DAD_Utils.getItemInfo()
    myItem.findPrice()
    DAD_Utils.returnMarketStash()
    print(myItem.listItem())


    mytime2 = time.time()

    print(f"price found in {mytime2-mytime} seconds")

    # print(DAD_Utils.selectStash(True))