import difflib
import DAD_Utils
import config
import time
import pyautogui

# DAD_Utils.loadTextFiles()
# pyautogui.mouseInfo()

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
mytime =time.time()
s = DAD_Utils.locateAllOnScreen('marketChecked',region=config.ssMarketRoll)
if s:
    print(len(s))
else:
    print("NO")

mytime2 = time.time()


print(mytime2-mytime)