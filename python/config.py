#storage for GUI navigation
GAME_NAME = "DungeonCrawler.exe"
pytessPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
pytessConfig = "--psm 6"
# -1 for -1 under price, float val for percent undercut, int for static undercut
undercutValue = -1
sleepTime = 1.5
sigRollIncrease = [100, 0.4]

# values for sellMethod:
# 1 -> Lowest Price
# 2 -> Lowest w/o outliers
# 3 -> Lowest 3 avg
sellMethod = 1
rollMethod = 1
# stashDump: -1 for shared stash, 0-10 are numbered with 0 default
stashDump = 2 
# stashSell: -1 for shared stash, 0-10 are numbered with 0 default
stashSell = 0
sellWidth = 12
sellHeight = 8
ssComp1 = [700, 400, 500, 400]
ssComp2 = [650, 350, 600, 500]
ssGold = [1488, 340, 72, 620]
ssMarketItem = [200,200,100,100]
ssMarketRoll = [1450, 175, 250, 245]
ssMarketExpireTime = [1262, 322, 200, 630]
ssMarketRollSearch = [1470, 231, 130, 20]
ssRaritySearch = [286, 193, 130, 22]
ssItemNameSearch = [49, 192, 130, 22]
xMarketSearchNameRairty, yMarketSearchNameRairty = 945,469
xTrade, yTrade = 1109, 37
xStashSelect,yStashSelect = 800,40
xGatherGold, yGatherGold = 300, 988
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
xStashStart, yStashStart = 1386, 209
xTitleAdd, yTitleAdd = 352, 75
xPriceCoords, yPriceCoords = 1452, 324 
xResetFilters, yResetFilters = 1790, 201
xSearchPrice, ySearchPrice = 1788, 273
numComps = 3
totalListings = 10
valueThreshold = 1250
xGetListings, yGetListings = 242, 509
x2GetListings, y2GetListings = 110, 500
xCanOrTransfer, yCanOrTransfer = 960, 660
xConfirmNo, yConfirmNo = 1111, 615
xSelectTrade, ySelectTrade = 1111, 40
xSelectMarket, ySelectMarket = 1250, 250
xStashDetect, yStashDetect = 1380, 195
firstSlotItemDisplayRegion = (1358, 170, 442, 630)
listingSoldRegion = (20,500,45,515)
xInventory,yInventory = 705, 644
xExitMarket,yExitMarket = 150,40
xExitMarketYes,yExitMarketYes = 855,615
getDungeonInvRegion = (656, 509, 400, 200)
getExpressmanRegion = (1169, 335, 400, 200)
xStartExpressmanInv, yStartExpressmanInv = 1184, 350
xStartPlayerInv, yStartPlayerInv = 671, 524
getStashRegion = (1284, 172, 80, 371)
getMarketRegion = (800,0,400,80)
getScreenRegion = (0, 0, 1920, 1080)
itemSearchRegion = (73, 262, 192, 250)
regionMarketListings = (700, 60, 440, 100)
xCollectExpressman, yCollectExpressman = 69, 256
xPayGetExpressman, yPayGetExpressman = 953,926
