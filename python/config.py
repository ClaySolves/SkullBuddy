#storage for GUI navigation
exeName = "DungeonCrawler.exe"
pytessPath = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytessConfig = "--psm 6"
# -1 for -1 under price, float val for percent undercut, int for static undercut
sellUndercut = None
sellMin = None
sellMax = None
sleepTime = None
sigRollIncreaseStatic = 50
sigRollIncreasePercent = 0.2
darkMode = False
# values for sellMethod:
# 1 -> Lowest Price
# 2 -> Lowest w/o outliers
# 3 -> Lowest 3 avg
sellMethod = 1
rollMethod = ""
sellHotkey = "S"
closeHotkey = "Q"
# stashDump: -1 for shared stash, 0-10 are numbered with 0 default
stashDump = 2 
# stashSell: -1 for shared stash, 0-10 are numbered with 0 default
stashSell = 0
sellWidth = None
sellHeight = None
stashPixelVal = None
organizeMethod = None
organizeStashes = 0
numDatabase = 13

ssQuantity = [910,400,80,15]
ssComp1 = [700, 400, 500, 400]
ssComp2 = [650, 350, 600, 500]
ssGold = [1488, 340, 72, 620]
ssGoldQuantity = [1600, 340, 110, 620]
ssMarketItem = [200,200,100,100]
ssMarketRoll = [1450, 175, 250, 245]
ssMarketExpireTime = [1262, 322, 200, 630]
ssMarketSearch = [1262, 322, 350, 630]
ssMarketRollSearch = [1470, 231, 130, 20]
ssRaritySearch = [286, 193, 130, 22]
ssPriceColumnRead = [1461,258,56,31]
ssBuyRead = [1761,342,60,28]
ssItemNameSearch = [49, 192, 130, 22]
ssConfirmStash = [1585,131,65,26]
ssEntireStash = [1376, 199, 493, 814]
ssGetListings = [142, 500, 150, 485]
ssGetListingPageNum = [174, 1004, 230, 40]
ssGetStashInv = [686, 624, 415, 208]

xListingLeft, yListingLeft = 217,1021
xListingRight, yListingRight = 368,1021
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

ITEM_MOVES_BOTTOM_RIGHT_CORNER = {
    "Lyre",
    "Surgical Kit"
}

# slot type sorting order
SLOTTYPE_ORDER = {
    "Ring": 1,
    "Necklace": 2,
    "Head": 3,
    "Chest": 4,
    "Back": 5,
    "Hands": 6,
    "Legs": 7,
    "Feet": 8,
    "Primary Weapon": 9,
    "Secondary Weapon": 10,
    "Utility": 11,
    "Decoration": 12,
    "Invalid": 13
}

# rarity sorting order
RARITY_ORDER = {
    "poor": 0,
    "common": 1,
    "uncommon": 2,
    "rare": 3,
    "epic": 4,
    "legendary": 5,
    "unique": 6
}

# rarity sorting order
ROLL_SEARCH = {
    "%Action Speed": "act",
    "Weapon Damage": "",
    "Move Speed": "",
    "Additional Magical Damage": "l ma",
    "Additional Memory Capacity": "l me",
    "Additional Armor Rating": "l a",
    "Additional Move Speed": "l mo",
    "Additional Physical Damage": "l ph",
    "Additional Weapon Damage": "l w",
    "Agility": "ili",
    "%Armor Penetration": "r p",
    "Armor Rating": "",
    "%Buff Duration Bonus": "bu",
    "%Debuff Duration Bonus": "deb",
    "Dexterity": "ex",
    "Knowledge": "kn",
    "Luck": "lu",
    "%Magic Penetration": "c p",
    "Magic Resistance": "c r",
    "%Magical Damage Bonus": "gical damage b",
    "%Magical Damage Reduction": "gical damage r",
    "Magical Healing": "gical h",
    "%Magical Interaction Speed": "gical i",
    "Magical Power": "gical p",
    "Max Health": "x h",
    "%Max Health Bonus": "h b",
    "%Memory Capacity Bonus": "y b",
    "%Move Speed Bonus": "d b",
    "%Physical Damage Bonus": "sical damage b",
    "%Physical Damage Reduction": "sical damage r",
    "Physical Healing": "sical h",
    "Physical Power": "sical p",
    "%Projectile Damage Reduction": "e d",
    "%Regular Interaction Speed": "r i",
    "Resourcefulness": "ef",
    "%Spell Casting Speed": "l c",
    "Strength": "gt",
    "True Magical Damage": "e m",
    "True Physical Damage": "e p",
    "Vigor": "vi",
    "Will": "wi",
    "All Attributes": "all",
    "%Cooldown Reduction Bonus": "n r"
}

ITEM_SIZE = {
    "Adventurer Boots" : (2,2),
    "Adventurer Cloak" : (2,3),
    "Adventurer Tunic" : (2,3),
    "Ale" : (1,1),
    "Ancient Scroll" : (2,3),
    "Arcane Garb" : (2,2),
    "Arcane Gloves" : (2,2),
    "Arcane Hood" : (2,2),
    "Armet" : (2,2),
    "Arming Sword" : (1,3),
    "Armor Scrap" : (2,2),
    "Arrow" : (1,3),
    "Axe of Righteousness" : (2,4),
    "Badger Pendant" : (1,1),
    "Bandage" : (1,1),
    "Bandshee sonnet" : (1,2), 
    "Barbuta Helm" : (2,2),
    "Bardic Pants" : (2,3),
    "Bardiche" : (2,5),
    "Bat Claw" : (1,1),
    "Bat Wing" : (2,2),
    "Battle Axe" : (2,4),
    "Bear Pendant" : (1,1),
    "Beetle Wings" : (1,3),
    "Blade of Righteousness" : (1,4),
    "Bloodsap Blade" : (1,3),
    "Bloodwoven Gloves" : (2,2),
    "Bloodwoven Robe" : (2,3),
    "Blue Eyeballs" : (1,1),
    "Blue Sapphire" : (1,1),
    "Bolt" : (1,3),
    "Bone" : (1,3),
    "Boneshaper" : (1,3),
    "Bow of Righteousness" : (1,3),
    "Bowstring" : (1,1),
    "Brave Hunter's Pants" : (2,3),
    "Broken Skull" : (2,2),
    "Buckled Boots" : (2,2),
    "Buckler" : (2,2),
    "Bug Shell" : (2,2),
    "Buttoned Boots" : (2,2),
    "Buttoned Leggings" : (2,3),
    "Campfire Kit" : (2,2),
    "Candy Cane" : (1,1),
    "Candy Corn" : (1,1),
    "Captured Mana Flakes" : (1,1),
    "Castillion Dagger" : (1,2),
    "Centaur Hoof" : (2,2),
    "Centaur Horn" : (2,2),
    "Centaur Tail" : (1,3),
    "Centaur's Madness" : (1,3),
    "Ceremonial Dagger" : (1,2),
    "Ceremonial Headdress" : (2,2),
    "Ceremonial Staff" : (1,4),
    "Champion Armor" : (2,3),
    "Chapel De Fer" : (2,2),
    "Chaperon" : (2,2),
    "Chocolate Chip Muffin" : (1,1),
    "Chronicles of the Cursed Crow" : (2,2),
    "Cloak of Darkness" : (2,3),
    "Cloth Pants" : (2,3),
    "Club" : (1,3),
    "Cobalt Chapel De Fer" : (2,2),
    "Cobalt Frock" : (2,3),
    "Cobalt Hat" : (2,2),
    "Cobalt Heavy Gauntlet" : (2,2),
    "Cobalt Hood" : (2,2),
    "Cobalt Ingot" : (2,2),
    "Cobalt Leather Gloves" : (2,2),
    "Cobalt Lightfoot Boots" : (2,2),
    "Cobalt Ore" : (2,2),
    "Cobalt Plate Boots" : (2,2),
    "Cobalt Plate Pants" : (2,3),
    "Cobalt Powder" : (1,1),
    "Cobalt Regal Gambeson" : (2,3),
    "Cobalt Templar Armor" : (2,3),
    "Cobalt Trousers" : (2,3),
    "Cobalt Viking Helm" : (2,2),
    "Cockatrice's Lucky Feather" : (1,1),
    "Coif" : (2,2),
    "Copper Ingot" : (2,2),
    "Copper Ore" : (2,2),
    "Copper Powder" : (1,1),
    "Copperlight Attire" : (2,3),
    "Copperlight Gauntlets" : (2,2),
    "Copperlight Kettle Hat" : (2,2),
    "Copperlight Leggings" : (2,3),
    "Copperlight Lightooft Boots" : (2,2),
    "Copperlight Outfit" : (2,3),
    "Copperlight Pants" : (2,3),
    "Copperlight Plate Boots" : (2,2),
    "Copperlight Plate Pants" : (2,3),
    "Copperlight Riveted Gloves" : (2,2),
    "Copperlight Sanctum Plate Armor" : (2,3),
    "Copperlight Shadow Hood" : (2,2),
    "Copperlight Straw Hat" : (2,2),
    "Copperlight Tunic" : (2,3),
    "Cowl of Darkness" : (2,2),
    "Crossbow" : (2,3),
    "Crusader Armor" : (2,3),
    "Crusader Helm" : (2,2),
    "Crystal Ball" : (2,2),
    "Crystal Sword" : (1,4),
    "Crystal Boots" : (2,2),
    "Cursed Crown" : (2,2),
    "Cyclops Eye" : (2,2),
    "Cyclops Rags" : (2,2),
    "Cyclops Vision Crystal" : (2,2),
    "Cyclop's Club" : (2,4),
    "Dagger of Righteousness" : (1,2),
    "Dark Cuirass" : (2,3),
    "Dark Leather Leggings" : (2,3),
    "Dark Matter" : (1,1),
    "Dark Matter Tunic" : (2,3),
    "Dark Plate Armor" : (2,3),
    "Darkgrove Hood" : (2,2),
    "Darkgrove Robe" : (2,3),
    "Darkleaf Boots" : (2,2),
    "Dashing Boots" : (2,2),
    "Demon Blood" : (1,1),
    "Demon Dog Thorn" : (1,3),
    "Demon Grip Gloves" : (2,2),
    "Demon's Glee" : (1,3),
    "Demonclad Leggings" : (2,3),
    "Diamond" : (1,1),
    "Diary of the Toz" : (2,2),
    "Divine Axe" : (2,4),
    "Divine Blade" : (1,4),
    "Divine Bow" : (1,3),
    "Divine Dagger" : (1,2),
    "Divine Rod" : (1,3),
    "Divine Short Sword" : (1,3),
    "Divine Staff" : (1,5),
    "Dog Collar" : (2,2),
    "Dotted Gold Bangle" : (1,1),
    "Double Axe" : (2,4),
    "Doublet" : (2,3),
    "Dread Hood" : (2,2),
    "Drum" : (2,2),
    "Ectoplasm" : (1,1),
    "Elkwood Crown" : (2,2),
    "Elkwood Gloves" : (2,2),
    "Emerald" : (1,1),
    "Enchanted Dark Fabric" : (2,2),
    "Explosive Bottle" : (1,2),
    "Extra Thick Pelt" : (2,2),
    "Falchion" : (1,3),
    "Falchion of Honor" : (1,3),
    "Fangs of Death Necklace" : (1,1),
    "Feathered Hat" : (2,2),
    "Felling Axe" : (2,4),
    "Fine Cuirass" : (2,3),
    "Firefly's Abdomen" : (1,1),
    "Flanged Mace" : (1,3),
    "Flute" : (1,3),
    "Forest Boots" : (2,2),
    "Forest Hood" : (2,2),
    "Foul Boots" : (2,2),
    "Fox Pendant" : (1,1),
    "Francisca Axe" : (1,2),
    "Frock" : (2,3),
    "Frost Amulet" : (1,1),
    "Frost Wyvern Egg" : (3,3),
    "Frost Wyvern's Claws" : (2,2),
    "Frost Wyvern's Hide" : (2,2),
    "Frosted Feather" : (1,1),
    "Frostlight Abyss Plate Armor" : (2,3),
    "Frostlight Aketon" : (2,3),
    "Frostlight Cloak" : (2,3),
    "Frostlight Crusader Helm" : (2,2),
    "Frostlight Crystal Sword" : (1,4),
    "Frostlight Feathered Hat" : (2,2),
    "Frostlight Gauntlets" : (2,2),
    "Frostlight Hood" : (2,2),
    "Frostlight Lantern Shield" : (2,3),
    "Frostlight Leather leggings" : (2,3),
    "Frostlight Lightfoot Boots" : (2,2),
    "Frostlight Mystic Gloves" : (2,2),
    "Frostlight Norman Nasal Helm" : (2,2),
    "Frostlight Oracle Robe" : (2,3),
    "Frostlight Plate Boots" : (2,2),
    "Frostlight Plate Pants" : (2,3),
    "Frostlight Riveted Gloves" : (2,2),
    "Frostlight Rugged Boots" : (2,2),
    "Frostlight Runestone Gloves" : (2,2),
    "Frostlight Spear" : (1,5),
    "Frostlight Trousers" : (2,3),
    "Frostlight Warden Outfit" : (2,3),
    "Frostlight Wizard Hat" : (2,2),
    "Frostlight Ingot" : (2,2),
    "Frostlight Ore" : (2,2),
    "Frostlight Powder" : (1,1),
    "Frozen Heart" : (2,2),
    "Frozen Iron Key" : (1,2),
    "Gem Necklace" : (1,1),
    "Gem Ring" : (1,1),
    "Ghostdust Pouch" : (1,1),
    "Ghostly Essence" : (1,1),
    "Giant Bat Ear" : (1,1),
    "Giant Bat Hide" : (2,2),
    "Giant Toe" : (1,2),
    "Gingerbread Cookie" : (1,1),
    "Gjermundbu" : (2,2),
    "Glimmer Bangle" : (1,1),
    "Gloves of Utility" : (2,2),
    "Glowing Blue Ice Eyes" : (1,1),
    "Goblet" : (1,2),
    "Goblin Ear" : (1,1),
    "Gold Band" : (1,1),
    "Gold Bowl" : (2,2),
    "Gold Candelabra" : (2,2),
    "Gold Candle Holder" : (2,2),
    "Gold Candle Platter" : (2,2),
    "Gold Chalice" : (1,2),
    "Gold Coin" : (1,1),
    "Gold Coin Bag" : (2,2),
    "Gold Coin Chest" : (2,3),
    "Gold Coin Pouch" : (1,2),
    "Gold Coin Purse" : (1,1),
    "Gold Crown" : (2,2),
    "Gold Goblet" : (1,2),
    "Gold Ingot" : (2,2),
    "Gold Ore" : (2,2),
    "Gold Powder" : (1,1),
    "Gold Waterpot" : (2,2),
    "Golden Armet" : (2,2),
    "Golden Boots" : (2,2),
    "Golden Chausses" : (2,3),
    "Golden Cloack" : (2,3),
    "Golden Felling Axe" : (2,4),
    "Golden Gauntlets" : (2,2),
    "Golden Gjermundbu" : (2,2),
    "Golden Gloves" : (2,2),
    "Golden Hounskull" : (2,2),
    "Golden Key" : (1,2),
    "Golden Leaf Hood" : (2,2),
    "Golden Leggings" : (2,3),
    "Golden Padded Tunic" : (2,3),
    "Golden Plate" : (2,3),
    "Golden Plate Boots" : (2,2),
    "Golden Plate Pants" : (2,3),
    "Golden Robe" : (2,3),
    "Golden Scarf" : (2,2),
    "Golden Skull Token" : (1,1),
    "Golden Teeth" : (1,1),
    "Golden Viking Sword" : (1,3),
    "Golden Bridgandine" : (2,3),
    "Grave Essence" : (1,1),
    "Gravewolf Gloves" : (2,2),
    "Great Helm" : (2,2),
    "Great Potion of Luck" : (1,1),
    "Grimslayer" : (1,4),
    "Grimsmile Ring" : (1,1),
    "Halberd" : (2,5),
    "Hand Crossbow" : (2,2),
    "Hatchet" : (1,3),
    "Haze Blade" : (1,2),
    "Heart Candy" : (1,1),
    "Heater Shield" : (2,3),
    "Heavy Boots" : (2,2),
    "Heavy Gambeson" : (2,3),
    "Heavy Gauntlets" : (2,2),
    "Heavy Leather Leggings" : (2,3),
    "Honeybliss Pear" : (1,1),
    "Horseman's Axe" : (1,3),
    "Hounskull" : (2,2),
    "Hunting trap" : (2,2),
    "Icefang" : (1,2),
    "Infected Flesh" : (1,2),
    "Intact Skull" : (2,2),
    "Iron Ore" : (2,2),
    "Iron Ingot" : (2,2),
    "Iron Powder" : (1,1),
    "Kettle Hat" : (2,2),
    "Kobold's Ear" : (1,1),
    "Kris Dagger" : (1,2),
    "Laced Turnshoe" : (2,2),
    "Lantern" : (2,2),
    "Lantern Shield" : (2,3),
    "Leaf Gold Bangle" : (1,1),
    "Leather Bonnet" : (2,2),
    "Leather Cap" : (2,2),
    "Leather Chausses" : (2,3),
    "Leather Gloves" : (2,2),
    "Leather Leggings" : (2,3),
    "Lifeleaf" : (1,2),
    "Light Aketon" : (2,3),
    "Light Bringer" : (1,3),
    "Light Gauntlets" : (2,2),
    "Light Gold Bangle" : (1,1),
    "Lightfoot Boots" : (2,2),
    "Lockpick" : (1,1),
    "Longbow" : (1,4),
    "Longsword" : (1,4),
    "Loose Trousers" : (2,3),
    "Low Boots" : (2,2),
    "Lute" : (2,3),
    "Lyre" : (2,2),
    "Maggot" : (1,1),
    "Magic Protection Potion" : (1,1),
    "Magic Staff" : (1,4),
    "Mana Sphere" : (2,2),
    "Manuscripts of the Warlord" : (2,2),
    "Marauder Outfit" : (2,3),
    "Mercurial Cloak" : (2,3),
    "Mimic Tongue" : (2,2),
    "Mimic Tooth" : (1,2),
    "Moldy Bread" : (1,2),
    "Monkey Pendant" : (1,1),
    "Morning Star" : (1,3),
    "Mystic Gloves" : (2,2),
    "Mystic Vestments" : (2,3),
    "Mystical Gem" : (1,1),
    "Necklace of Peace" : (1,1),
    "Norman Nasal Helm" : (2,2),
    "Northern Full Tunic" : (2,3),
    "Occultist Boots" : (2,2),
    "Occultist Hood" : (2,2),
    "Occultist Pants" : (2,3),
    "Occultist Robe" : (2,3),
    "Occultist Tunic" : (2,3),
    "Oil Lantern" : (1,2),
    "Old Bloody Bandage" : (1,1),
    "Old Cloth" : (2,2),
    "Old Rusty Key" : (1,2),
    "Old Shoes" : (2,2),
    "Open Sallet" : (2,2),
    "Oracle Robe" : (2,3),
    "Ornate Jazerant" : (2,3),
    "Owl Pendant" : (1,1),
    "Ox Pendant" : (1,1),
    "Padded Leggings" : (2,3),
    "Padded Tunic" : (2,3),
    "Patterned Gold Bangle" : (1,1),
    "Pavise" : (3,4),
    "Pearl Necklace" : (1,1),
    "Phantom Flower" : (1,2),
    "Phoenix Choker" : (1,1),
    "Pickaxe" : (2,3),
    "Plate Boots" : (2,2),
    "Plate Pants" : (2,3),
    "Poison Vial" : (1,1), ################################## 
    "Potion of Clarity" : (1,1),
    "Potion of Healing" : (1,1),
    "Potion of Invisibility" : (1,1),
    "Potion of Luck" : (1,1),
    "Potion of Protection" : (1,1),
    "Pourpoint" : (2,3),
    "Primitive Bracelet" : (1,1),
    "Quarterstaff" : (1,5),
    "Radiant Cloak" : (2,3),
    "Ranger Hood" : (2,2),
    "Rapier" : (1,3),
    "Rat Pendant" : (1,1),
    "Rawhide Gloves" : (2,2),
    "Recurve Bow" : (1,3),
    "Regal Gambeson" : (2,3),
    "Reinforced Gloves" : (2,2),
    "Ring of Courage" : (1,1),
    "Ring of Finesse" : (1,1),
    "Ring of Quickness" : (1,1),
    "Ring of Resolve" : (1,1),
    "Ring of Survival" : (1,1),
    "Ring of Vitality" : (1,1),
    "Ring of Wisdom" : (1,1),
    "Ritual Robe" : (2,3),
    "Riveted Gloves" : (2,2),
    "Robe of Darkness" : (2,3),
    "Rod of Righteousness" : (1,3),
    "Rogue Cowl" : (2,2),
    "Rondel Dagger" : (1,2),
    "Rotten Fluids" : (1,1),
    "Round Shield" : (2,3),
    "Ruby" : (1,1),
    "Rubysilver Adventurer Boots" : (2,2),
    "Rubysilver Barbute Helm" : (2,2),
    "Rubysilver Cap" : (2,2),
    "Rubysilver Cuirass" : (2,3),
    "Rubysilver Doublet" : (2,3),
    "Rubysilver Gauntlets" : (2,2),
    "Rubysilver Hood" : (2,2),
    "Rubysilver Ingot" : (2,2),
    "Rubysilver Leggings" : (2,3),
    "Rubysilver Ore" : (2,2),
    "Rubysilver Plate Boots" : (2,2),
    "Rubysilver Plate Pants" : (2,3),
    "Rubysilver Powder" : (1,1),
    "Rubysilver Rawhide Gloves" : (2,2),
    "Rubysilver Vestments" : (2,3),
    "Rugged Boots" : (2,2),
    "Runestone Gloves" : (2,2),
    "Rusty Broken Sword" : (1,2),
    "Sallet" : (2,2),
    "Shadow Hood" : (2,2),
    "Shadow Mask" : (2,2),
    "Shine Bangle" : (1,1),
    "Shoes of Darkness" : (2,2),
    "Short Sword" : (1,3),
    "Short Sword of Righteousness" : (1,3),
    "Silver Chalice" : (1,2),
    "Silver Coin" : (1,1),
    "Silver Ingot" : (2,2),
    "Silver Ore" : (2,2),
    "Silver Powder" : (1,1),
    "Silver Skull Token" : (1,1),
    "Simple Gold Bangle" : (1,1),
    "Skull Key" : (1,2),
    "Sleek Hide Pants" : (2,3),
    "SLim Bandle" : (1,1),
    "Sovereign's Ghostblade" : (1,4),
    "Spangenhlem" : (2,2),
    "Spear" : (1,5),
    "Spear of Rot" : (1,5),
    "Spectral Coinbag" : (2,2),
    "Spectral Fabric" : (2,2),
    "Spectral Hilt" : (1,2),
    "Spellbook" : (2,2),
    "Spellplunder Rod" : (1,4),
    "Spider Silk" : (1,1),
    "Splendid Cloak" : (2,3),
    "Staff of Righteousness" : (1,5),
    "Sterling Axe" : (2,4),
    "Sterling Blade" : (1,4),
    "Sterling Bow" : (1,3),
    "Sterling Dagger" : (1,2),
    "Sterling Rod" : (1,3),
    "Sterling Short Sword" : (1,3),
    "Sterling Staff" : (1,5),
    "Stiletto Dagger" : (1,2),
    "Stilmend Boots" : (2,2),
    "Stitched Turnshoes" : (2,2),
    "Straw Hat" : (2,2),
    "Studded Leather" : (2,3),
    "Sunburt Orb" : (1,1), ########################
    "Surgical Kit" : (2,2),
    "Suvival Bow" : (1,3),
    "Tanglethread Trousers" : (2,3),
    "Tattered Cloak" : (2,3),
    "Templar Armor" : (2,3),
    "Thorn Shield"  : (2,2), 
    "Throwing Knife" : (1,2),
    "Token of Honor" : (1,1),
    "Topfhelm" : (2,2),
    "Torch" : (1,3),
    "Torn Bat Wing" : (2,2),
    "Torq of Soul" : (1,1),
    "Trap Disarming Kit" : (1,2),
    "Tri-Pelt Doublet" : (2,3),
    "Tri-Pelt Northern Full Tunic" : (2,3),
    "Triple Gem Bangle" : (1,1),
    "Troll Pelt" : (2,2),
    "Troll's Blood" : (1,2),
    "Troll's Club" : (1,3),
    "Troll's Bane" : (1,5),
    "Troubadour Outfit" : (2,3),
    "Turnshoe" : (2,2),
    "Turquoise Gem Bangle" : (1,1),
    "Vigilant Cloak" : (2,3),
    "Viking Helm" : (2,2),
    "Viking Sword" : (1,3),
    "Visored Barbuta Helm" : (2,2),
    "Visored Sallet" : (2,2),
    "Void Blade" : (1,4),
    "Volcanic Ash" : (1,1),
    "Wanderer Attire" : (2,3),
    "Wanderlight Lantern" : (2,2),
    "War Hammer" : (1,3),
    "War Maul" : (2,4),
    "Warden Outfit" : (2,3),
    "Wardweed" : (1,2),
    "Warlord's Armor Shard" : (2,2),
    "Warlord's Broken Swrod Blade" : (2,3),
    "Watchman Cloak" : (2,3),
    "Wendigo's Antler Fragment" : (2,2),
    "Wendigo's Entrails" : (2,2),
    "Wendigo's Hoof" : (2,2),
    "Wendigo's Sharp Claws" : (1,2), 
    "Wind Locket" : (1,1),
    "Windlass Crossbow" : (2,4),
    "Wizard Hat" : (2,2),
    "Wizard Shoes" : (2,2),
    "Wolf Claw" : (1,1),
    "Wolf Fang" : (1,2),
    "Wolf Hunter Leggings" : (2,3),
    "Wolf Pelt" : (2,2),
    "Yeti's Teeth" : (1,1),
    "Zweihander" : (1,4)
}