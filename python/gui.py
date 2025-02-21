from PyQt5.QtGui import QKeyEvent
import DAD_Utils
import sys
import config
import time
import re
import database
import config
import keyboard
import subprocess
import logging
from io import StringIO
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QApplication, QMainWindow, QShortcut, QTableWidget, QTableWidgetItem, QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox, QGraphicsView, QTabWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QKeySequence, QPixmap, QPainter, QFont, QColor




 # Get the root logger configured in main.py
logger = logging.getLogger() 



#basic exception
class error(Exception):
    pass



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



# Custom QTableWidgetItem that sorts numbers 
class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            try:
                return float(self.text()) < float(other.text())  
            except ValueError:
                pass 
        return super().__lt__(other)



# Custom QTableWidgetItem that sorts rarities 
class RarityTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            rarity1 = self.text().lower()
            rarity2 = other.text().lower()
            try:
                return RARITY_ORDER.get(rarity1, -1) < RARITY_ORDER.get(rarity2, -1)  
            except ValueError:
                pass 
        return super().__lt__(other)



#gui stream
class GuiScriptStream():
    def __init__(self, outputSignal, color="black"):
        self.outputSignal = outputSignal
        self.color = color

    def write(self,txt):
        if txt.strip():
            message = f'<span style="color:{self.color};">{txt}</span>'
            self.outputSignal.emit(message)

    def flush(self):
        pass



# worker for gui stream
class logThread(QThread):
    outputSignal = pyqtSignal(str)  # var for output

    def run(self): # run function

        oldStdout = sys.stdout
        sys.stdout = GuiScriptStream(self.outputSignal)

        DAD_Utils.logGui("Listing Items...")
        DAD_Utils.searchStash()
        DAD_Utils.logGui("Finished!")
        sys.stdout = oldStdout



# worker for history stream
class listHistoryThread(QThread):
    outputSignal = pyqtSignal(str)  # var for output
    listedGoldTotal = pyqtSignal(int)

    def run(self):
        oldStdout = sys.stdout
        sys.stdout = GuiScriptStream(self.outputSignal)
        
        conn, cur = database.connectDatabase()
        totalGold = database.printDatabase(cur)
        self.listedGoldTotal.emit(totalGold)
        database.closeDatabase(conn)

        sys.stdout = oldStdout



#gui design
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create tabs
        self.tabs = QTabWidget()
        self.utilityTab()
        self.historyTab()
        self.helpTab()

        self.setCentralWidget(self.tabs)
        self.setWindowTitle("SkullBuddy")
        self.setGeometry(100, 100, 670, 670)



    # Update History Button
    def handleViewHistoryButton(self):
        self.skully.setPixmap(self.deathSkullFetchHistory)
        self.skully.repaint()

        # try:    
        #     logger.debug("Starting thread...")
        #     self.historyThread = listHistoryThread()
        #     self.historyThread.finished.connect(self.resetSkullyTxt)
        #     self.historyThread.outputSignal.connect(self.appendHistoryLog)
        #     self.historyThread.listedGoldTotal.connect(self.updateGoldText)
        #     self.historyThread.start()
        # except error:
        #     logger.debug("Error starting thread!")
        #     DAD_Utils.logGui("Error, Exiting!")

        # update history table
        self.updateHistoryTable()
        self.resetSkullyTxt()



    # Sell Items Button
    def handleSellItemButton(self):
        # gui death skull update
        self.deathSkullLabel.setPixmap(self.deathSkullPixmapThink)
        self.deathSkullLabel.repaint()
        
        self.guiToConfig()

        # Run thread
        try:    
            logger.debug("Starting thread...")
            self.thread = logThread()
            self.thread.finished.connect(self.resetSkullyTxt)
            self.thread.outputSignal.connect(self.appendSellLog)
            self.thread.start()
        except error:
            logger.debug("Error starting thread!")
            DAD_Utils.logGui("Error, Exiting!")



    # Log txt to GUI log
    def appendSellLog(self, txt): # append output to QTextEdit log
        self.sellLog.append(txt)



    # log txt to GUI history log
    def appendHistoryLog(self,txt):
        pass
        # self.historyLog.append(txt)



    # Build utility tab
    def utilityTab(self):
        #tab creation
        tab = QWidget()


        # deathskull
        self.deathSkullPixmapTalk = QPixmap('img/DeathSkullTalking.png')
        self.deathSkullPixmapThink = QPixmap('img/DeathSkullThinking.png')
        self.deathSkullLabel = QLabel()

        deathSkullText = QPainter(self.deathSkullPixmapTalk)
        deathSkullText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        deathSkullText.setPen(QColor("red"))      # Set the color of the text
        deathSkullText.drawText(167, 183, "greetings ... i list items...")
        deathSkullText.drawText(145, 200, "navigate to your market stash...")
        deathSkullText.drawText(152, 217, "adjust settings on right... and go...")
        deathSkullText.end()

        deathSkullThinkText = QPainter(self.deathSkullPixmapThink)
        deathSkullThinkText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        deathSkullThinkText.setPen(QColor("red"))      # Set the color of the text
        deathSkullThinkText.drawText(167, 183, "Selling your items...")
        deathSkullThinkText.drawText(145, 200, "Don't move your mouse...")
        deathSkullThinkText.end()
        
        self.deathSkullLabel.setPixmap(self.deathSkullPixmapTalk)

        # button
        self.sellButton = QPushButton("Sell Items", self)
        self.sellButton.clicked.connect(self.handleSellItemButton)

        # logs
        self.sellLog = QTextEdit(self)
        self.sellLog.setReadOnly(True)

        # labels
        
        #Close layout
        helpLabel = QLabel("Ctrl + Q: Exit SkullBuddy")
        helpLabel.setFont(QFont("Perpetua",18))
        helpLabel.setStyleSheet("color: red")
        helpLabel.setAlignment(Qt.AlignCenter)

        methodLabel = QLabel("Select Selling Method:")
        stashLabel = QLabel("Enter Stash Info:")

        # line edits
        intValidHeight = QIntValidator(0,20)
        intValidWidth = QIntValidator(0,12)
        doubleValidundercut = QDoubleValidator(0,100,2)
        intValidSellLimit = QIntValidator(0,100000)
        doubleValidSpeed = QDoubleValidator(0.3,5.0,2)

        self.appSpeed = QLineEdit()
        self.appSpeed.setPlaceholderText("Enter Sell Speed")
        self.appSpeed.setText(str(config.sleepTime))
        self.appSpeed.setValidator(doubleValidSpeed)

        self.undercut = QLineEdit()
        self.undercut.setPlaceholderText("Enter Undercut Value")
        self.undercut.setText(str(config.undercutValue))
        self.undercut.setValidator(doubleValidundercut)

        self.sellLimit = QLineEdit()
        self.sellLimit.setPlaceholderText("Enter Price Limit")
        self.sellLimit.setText(str(config.sellLimit))
        self.sellLimit.setValidator(intValidSellLimit)

        self.stashHeight = QLineEdit()
        self.stashHeight.setPlaceholderText("Enter Sell Height")
        self.stashHeight.setText(str(config.sellHeight))
        self.stashHeight.setValidator(intValidHeight)  

        self.stashWidth = QLineEdit()
        self.stashWidth.setPlaceholderText("Enter Sell Width")
        self.stashWidth.setText(str(config.sellWidth))
        self.stashWidth.setValidator(intValidWidth)

        # Radio Buttons
        self.radioMethodSelect = {
            1 : QRadioButton("Lowest Price"),
            2 : QRadioButton("Lowest Price w/o Outliers"),
            3 : QRadioButton("Lowest 3 Price Avg")
        }
        self.radioMethodSelect[1].setChecked(True)
        
        # Log Layout
        logLayout = QVBoxLayout()
        logLayout.addWidget(helpLabel)
        logLayout.addWidget(self.sellLog)

        # Settings Layout
        settingsLayout = QVBoxLayout()
        settingsLayout.addWidget(methodLabel)
        for value in self.radioMethodSelect.values():
            settingsLayout.addWidget(value)

        settingsLayout.addWidget(self.appSpeed)
        settingsLayout.addWidget(self.undercut)
        settingsLayout.addWidget(self.sellLimit)

        settingsLayout.addWidget(stashLabel)
        settingsLayout.addWidget(self.stashHeight)
        settingsLayout.addWidget(self.stashWidth)
        settingsLayout.addWidget(self.sellButton)

        # Graphics Setup
        logLayout.addWidget(self.deathSkullLabel)

        # Main Layout
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(logLayout)
        mainLayout.addLayout(settingsLayout)
        tab.setLayout(mainLayout)

        self.tabs.addTab(tab,"Utility")



    # Build history tab
    def historyTab(self):
        tab = QWidget()

        #skully setup
        self.deathSkullHistory = QPixmap('img/DeathSkullTalking.png')
        self.deathSkullFetchHistory = QPixmap('img/DeathSkullThinking.png')
        self.skully = QLabel()

        #skully txt
        deathSkullText = QPainter(self.deathSkullHistory)
        deathSkullText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        deathSkullText.setPen(QColor("red"))      # Set the color of the text
        deathSkullText.drawText(167, 183, "view your item listing history...")
        deathSkullText.drawText(165, 200, "i can remember everything...")
        deathSkullText.drawText(172, 217, "just ask...")
        deathSkullText.end()
        deathSkullThinkText = QPainter(self.deathSkullFetchHistory)
        deathSkullThinkText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        deathSkullThinkText.setPen(QColor("red"))      # Set the color of the text
        deathSkullThinkText.drawText(167, 183, "...let me think...")
        deathSkullThinkText.end()
        self.skully.setPixmap(self.deathSkullHistory)

        #skully history button
        # self.historyButton = QPushButton("View Listing History", self)
        # self.historyButton.clicked.connect(self.handleViewHistoryButton)

        #Total gold label
        self.totalGoldLabel = QLabel()
        self.totalGoldLabel.setFont(QFont("Monotype Corsiva",18))
        self.totalGoldLabel.setText("Total Value Listed:")

        #Total gold Number
        self.totalGoldNumber = QLabel()
        self.totalGoldNumber.setFont(QFont("Monotype Corsiva",36))
        self.totalGoldNumber.setStyleSheet("color: #DAA520")
        skullyGoldCount = f"{config.totalListedGold:,}"
        self.totalGoldNumber.setText(skullyGoldCount)

        #add all for skully
        skullyLayoutTotal = QHBoxLayout()
        skullyLayoutImg = QHBoxLayout()
        skullyLayoutButtons = QVBoxLayout()
        skullyLayoutImg.addWidget(self.skully)

        skullyLayoutButtons.addSpacerItem(QSpacerItem(113, 150, QSizePolicy.Fixed, QSizePolicy.Fixed))
        skullyLayoutButtons.addWidget(self.totalGoldLabel)
        skullyLayoutButtons.addWidget(self.totalGoldNumber)
        # skullyLayoutButtons.addWidget(self.historyButton)
        skullyLayoutTotal.addLayout(skullyLayoutImg)
        skullyLayoutTotal.addLayout(skullyLayoutButtons)

        #history layout
        historyLayout = QVBoxLayout()
        historyTableHeader = QHBoxLayout()

        #history log
        # self.historyLog = QTextEdit()
        # self.historyLog.setReadOnly(True)
        # historyLayout.addWidget(self.historyLog)

        #history table
        self.historyTable = QTableWidget()
        self.historyTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.historyTable.setColumnCount(8)
        self.historyTable.setRowCount(0)
        self.historyTable.setSortingEnabled(True)
        self.historyTable.setHorizontalHeaderLabels(['Name', 'Rarity', 'Price', 'Roll 1', 'Roll 2', 'Roll 3', 'Roll 4', 'Roll 5'])

        self.historyTable.setColumnWidth(0, 85)
        self.historyTable.setColumnWidth(1, 60)
        self.historyTable.setColumnWidth(2, 45)
        self.historyTable.setColumnWidth(3, 81)
        self.historyTable.setColumnWidth(4, 81)
        self.historyTable.setColumnWidth(5, 81)
        self.historyTable.setColumnWidth(6, 81)
        self.historyTable.setColumnWidth(7, 81)

        #Table search rarity & roll
        self.tableNameSearch = QLineEdit()
        self.tableNameSearch.setFixedSize(100, 20)  
        self.tableNameSearch.setPlaceholderText("Search Items...")
        self.tableNameSearch.textChanged.connect(self.filterName)

        self.tableRollSearch = QLineEdit()
        self.tableRollSearch.setFixedSize(100, 20)   
        self.tableRollSearch.setPlaceholderText("Search Rolls...")
        self.tableRollSearch.textChanged.connect(self.filterRolls)

        #History table header
        historyTableHeader.addWidget(self.tableNameSearch,alignment=Qt.AlignLeft)
        historyTableHeader.addSpacerItem(QSpacerItem(113, 12, QSizePolicy.Fixed, QSizePolicy.Fixed))
        historyTableHeader.addWidget(self.tableRollSearch,alignment=Qt.AlignLeft)
        historyTableHeader.addSpacerItem(QSpacerItem(800, 12, QSizePolicy.Expanding, QSizePolicy.Fixed))


        # Add all widgets
        historyLayout.addWidget(self.historyTable)

        # BUILD ALL GUI
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(historyTableHeader)
        mainLayout.addLayout(historyLayout)
        mainLayout.addLayout(skullyLayoutTotal)
        tab.setLayout(mainLayout)
        self.tabs.addTab(tab,"History")

        self.updateHistoryTable()



    # Build help tab
    def helpTab(self):
        tab = QWidget()

        #help widget
        helpLog = QTextEdit()
        helpLog.setReadOnly(True)
        helpLog.setText(f"""
        How to use SkullBuddy:
        
        Launch Dark and Darker
        Navigate to Trade -> Marketplace -> My Listings
        Select stash to sell from
        Adjust Settings
        Click Sell Items
                        

                        
        App Speed:
        Controlls SkullBuddy's execution time
        Recommended Value: 1.0
        Lower values increase speed and higher values decrease speed
        test and adjust accordingly for ideal performance 

                                   

        Selling Method: 
        Determines calculated item price
        Lowest Price:                          Lists with lowest recorded price
        Lowest Price w/o Outliers:      Lists with lowest recorded price, removing low/mislisted recorded prices
        Lowest 3 Price Avg:                Lists with the average of the lowest 3 prices
                        
                        

        Undercut Value: 
        Decreases recorded price to sell faster
        Enter a number (1 - 100) to undercut the recorded price by a static value
        Enter a decimal value (0.01 - 0.99) to undercut the recorded price by a percentage
                        
        Example: Listing at 100
        Undercut Value: 20          100 - 20 = 80, list at 80 gold
        Undercut Value: .11         100 - (100 * .11) = 89, list at 89 gold    
            
                        
                        
        Sell Height and Width: 
        Creates a box from top left corner to include items being sold
                        
        Examples:
        Sell Hieght:  4 & Sell Width: 12        includes first 4 rows of stash boxes
        Sell Hieght: 20 & Sell Width: 12        includes all stash boxes
        Sell Hieght: 10 & Sell Width: 6         includes first quadrant of stash boxes              
                        """)
        helpLog.setAlignment(Qt.AlignLeft)

        devLabel = QLabel('<a href="https://github.com/ClaySolves">Dev</a>')
        devLabel.setOpenExternalLinks(True)
        devLabel.setAlignment(Qt.AlignCenter)

        donateLabel = QLabel('<a href="https://paypal.me/SolvingClay">Donate</a>')
        donateLabel.setOpenExternalLinks(True)
        donateLabel.setAlignment(Qt.AlignCenter)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(helpLog)
        mainLayout.addWidget(devLabel)
        mainLayout.addWidget(donateLabel)
        tab.setLayout(mainLayout)

        self.tabs.addTab(tab,"Help")



     # reset skully txt
    def resetSkullyTxt(self):
        time.sleep(0.1)

        self.deathSkullLabel.setPixmap(self.deathSkullPixmapTalk)
        self.deathSkullLabel.repaint()

        self.skully.setPixmap(self.deathSkullHistory)
        self.skully.repaint()



    # update total gold
    def updateGoldText(self,totalGold):
        self.totalGoldNumber.setText(f"{totalGold:,}")
        DAD_Utils.updateConfig("totalListedGold",totalGold)

    
    
    # update config from gui selections
    def guiToConfig(self):
        #handle config updates from settings
        txtRead = next((key for key, value in self.radioMethodSelect.items() if value.isChecked()),None)
        if str(config.sellMethod) != str(txtRead):
            DAD_Utils.updateConfig("sellMethod",txtRead)

        txtRead = self.appSpeed.text()
        if str(config.sleepTime) != txtRead:
            DAD_Utils.updateConfig("sleepTime",float(txtRead))

        txtRead = self.stashWidth.text()
        if str(config.sellWidth) != txtRead: 
            DAD_Utils.updateConfig("sellWidth",int(txtRead))

        txtRead = self.stashHeight.text()
        if str(config.sellHeight) != txtRead:
            DAD_Utils.updateConfig("sellHeight",int(txtRead))

        txtRead = self.undercut.text()
        if str(config.undercutValue) != txtRead:
            if "." in txtRead:
                DAD_Utils.updateConfig("undercutValue",float(txtRead))
            else:
                DAD_Utils.updateConfig("undercutValue",int(txtRead))

        txtRead = self.sellLimit.text()
        if str(config.sellLimit) != txtRead:
            DAD_Utils.updateConfig("sellLimit",int(txtRead))



    # Update history table
    def updateHistoryTable(self):
        conn, cur = database.connectDatabase()
        data = database.getStoredItems(cur) 

        numItems = 0
        totalGold = 0
        for i, item in enumerate(data):

            if not item[0] or not item[1] or not item[3]:
                continue

            self.historyTable.setRowCount(self.historyTable.rowCount() + 1)    
            self.historyTable.setRowHeight(numItems, 40)

            #Update name
            namePrint = item[0] if item[0] else 'NameReadError'
            tableName = QTableWidgetItem(namePrint)
            tableName.setFont(QFont("Arial",8))
            self.historyTable.setItem(numItems, 0, tableName)

            #update rarity
            printColor = 'gray'
            if item[1]:
                item[1][0].upper()
                if item[1].lower() == 'poor' or item[1].lower() == 'common':
                    printColor = 'gray'
                elif item[1].lower() == 'uncommon':
                    printColor = 'green'
                elif item[1].lower() == 'rare':
                    printColor = 'MediumBlue'
                elif item[1].lower() == 'epic':
                    printColor = 'Orchid'
                elif item[1].lower() == 'legendary':
                    printColor = 'Goldenrod'
                elif item[1].lower() == 'unique':
                    printColor = 'PaleGoldenRod'

            rarityPrint = 'None' if not item[1] else item[1][0].upper() + item[1][1:]
            tableRarity = RarityTableWidgetItem(rarityPrint)
            tableRarity.setForeground(QColor(printColor))
            tableRarity.setFont(QFont("Arial",8))
            self.historyTable.setItem(numItems, 1, tableRarity)

            #update price
            totalGold = totalGold + item[3]
            printPrice = str(item[3]) if item[3] else 'None'
            tablePrice = NumericTableWidgetItem(printPrice)
            fontColor = QColor('Gold') if printPrice != 'None' else QColor('Black')
            tablePrice.setForeground(fontColor)
            tablePrice.setFont(QFont("Arial",8))
            self.historyTable.setItem(numItems, 2, tablePrice)

            #Update rolls
            newString = item[2].strip('|')
            newList = newString.split('|')
            newNewList = [ele.split(",") for ele in newList]
            for j, attr in enumerate(newNewList):
                rollPrint = ""
                if len(attr) > 2:
                    if not (attr[2] == '0' or attr[2] == '1'): continue
                    if int(attr[2]):
                        if int(attr[0]) == 1: rollPrint = f"+ {attr[0]}.0%\n{attr[1]}"
                        else: rollPrint = f"+ {int(attr[0])/10:.1f}%\n{attr[1]}"
                    else:
                        rollPrint = f"+ {attr[0]}\n{attr[1]}"

                tableItem = QTableWidgetItem(rollPrint)
                tableItem.setForeground(QColor('DeepSkyBlue'))
                tableItem.setFont(QFont("Arial",7))
                self.historyTable.setItem(numItems, j + 3, tableItem)

            numItems = numItems + 1

        self.updateGoldText(totalGold)
        database.closeDatabase(conn)



    # filter history table by name
    def filterName(self):
        txt = self.tableNameSearch.text().lower()
        logger.debug(f"filtering names with: {txt}")
        self.filterTable(txt,0)



    # filter history table by name
    def filterRolls(self):
        txt = self.tableRollSearch.text().lower()
        logger.debug(f"filtering roll with: {txt}")
        self.filterTable(txt,3,8)
    

    # filter text in history table
    def filterTable(self,txt,column,column2=0):

        txt = re.sub(r'[^a-zA-Z0-9%]', '', txt)
        # hide column rows that do not match query
        for row in range(self.historyTable.rowCount()):
            hideRow = True 
            if column2:
                for col in range(column,column2):
                    item = self.historyTable.item(row, col)
                    if item:
                        itemTxt = re.sub(r'[^a-zA-Z0-9%]', '', item.text().strip().lower())
                        if txt in itemTxt:
                            hideRow = False
                            break
            else:
                item = self.historyTable.item(row, column)
                itemTxt = re.sub(r'[^a-zA-Z0-9%]', '', item.text().strip().lower())
                if item and txt in itemTxt:
                    hideRow = False

            self.historyTable.setRowHidden(row, hideRow)
