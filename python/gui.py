import DAD_Utils
import sys
import config
import time
import re
import database
import config
import logging
from PyQt5.QtWidgets import QButtonGroup, QMessageBox, QDialog, QSpacerItem, QSizePolicy, QApplication, QMainWindow, QShortcut, QTableWidget, QTableWidgetItem, QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox, QGraphicsView, QTabWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize, QRegExp
from PyQt5.QtGui import QCursor, QIcon, QIntValidator, QDoubleValidator, QKeySequence, QPixmap, QPainter, QFont, QColor, QRegExpValidator

 # Get the root logger configured in main.py
logger = logging.getLogger() 



#basic exception
class error(Exception):
    pass



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
                return config.RARITY_ORDER.get(rarity1, -1) < config.RARITY_ORDER.get(rarity2, -1)  
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

    def __init__(self, selling):
        super().__init__()

        self.selling = selling
        self.oldStdout = sys.stdout


    def run(self): # run function
        sys.stdout = GuiScriptStream(self.outputSignal)

        if self.selling:
            DAD_Utils.searchStash()
        else:
            DAD_Utils.organizeStash()

        DAD_Utils.logGui("Finished!")

        sys.stdout = self.oldStdout

    def running(self):
        return self.isRunning()



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
    def __init__(self,darkMode):
        super().__init__()

        conn, cur = database.connectDatabase()
        self.darkMode = database.getConfig(cur,'darkMode') 
        database.closeDatabase(conn)

        # Create tabs
        self.tabs = QTabWidget()
        self.utilityTab(self.darkMode)
        self.historyTab(self.darkMode)
        self.helpTab(self.darkMode)

        self.tabs.currentChanged.connect(self.updateHistoryTable)

        self.setCentralWidget(self.tabs)
        self.setWindowTitle("SkullBuddy")
        self.setGeometry(100, 100, 670, 670)

        if self.darkMode:
            self.darkMode = False
            self.handleDarkModeButton()

        

    def minimizeWindow(self):
        self.showMinimized()



    # Switch to dark/light mode
    def handleDarkModeButton(self,updateConfig=True):
        #Switching to light mode
        if self.darkMode:
            DAD_Utils.logDebug("Switching to light mode")

            self.darkModeButton.setIcon(QIcon("img/darkModeIcon.png"))
            oldTxtColor = "color:#ffffff"
            newTxtColor = "color:#000000"
            mainAppBgrdColor = "background-color: #ffffff"
            buttonAppBgrd = "background-color: #e1e1e1"
            buttonColor = "border: 1px solid #7a7a7a"
            sellButtonPath = "img/DaDButton.png"
            organizeButtonPath = "img/organizeButtonEA.png"

            self.darkMode = False 

        #switching to Dark Mode
        else:
            DAD_Utils.logDebug("Switching to Dark mode")

            self.darkModeButton.setIcon(QIcon("img/darkModeIconDark.png")) 
            oldTxtColor = "color:#000000"
            newTxtColor = "color:#ffffff"
            mainAppBgrdColor = "background-color: #18181b"
            buttonAppBgrd = "background-color: #353535"
            buttonColor = "border: 1px solid #ffffff"
            sellButtonPath = "img/DaDButtonDark.png"
            organizeButtonPath = "img/organizeButtonDarkEA.png"

            self.darkMode = True

        for tab in range(self.tabs.count()):
            self.tabs.widget(tab).setStyleSheet(mainAppBgrdColor)
        
        #Swaping for Util tab
        currLine = self.sellLog.toHtml()
        newcurrLine = currLine.replace(oldTxtColor,newTxtColor)
        self.sellLog.clear()
        self.sellLog.insertHtml(newcurrLine)

        #Label txt Swap
        self.methodLabel.setStyleSheet(f"QLabel {{ {newTxtColor } }}")
        #self.stashLabel.setStyleSheet(f"QLabel {{ {newTxtColor } }}")
        self.organizeLabel.setStyleSheet(f"QLabel {{ {newTxtColor } }}")

        #Line txt Swap
        self.appSpeed.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.pixelValue.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.undercut.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.sellMin.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.sellMax.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.stashHeight.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.stashWidth.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        
       


        #Radio txt Swap
        for i in range (1,4):
            self.radioMethodSelect[i].setStyleSheet(f"QRadioButton {{ {newTxtColor } }}")

        for i in range (1,3):
            self.stashOrganizeMethod[i].setStyleSheet(f"QRadioButton {{ {newTxtColor } }}")

        for i in range(1,9):
             self.stashCheckboxSelect[i].setStyleSheet(f"QCheckBox {{ {newTxtColor } }}")

        #button txt swap
        self.sellButton.setIcon(QIcon(sellButtonPath))
        self.organizeButton.setIcon(QIcon(organizeButtonPath))

        self.paintSkully(self.darkMode)

        #Swaping for History Tab
        #Qlabel
        self.totalGoldLabel.setStyleSheet(f"QLabel {{ {newTxtColor } }}")

        #QTableWidget
        #background
        self.historyTable.setStyleSheet(f"""
            QHeaderView::section {{
               {mainAppBgrdColor}; {newTxtColor}; 
            }}
            QHeaderView::section:horizontal {{
                {mainAppBgrdColor}; 
            }}
            QHeaderView::section:vertical {{
                {mainAppBgrdColor}; 
            }}
            QTableCornerButton::section {{
                {mainAppBgrdColor};  
            }}
            """)
        
        # table data
        for row in range(self.historyTable.rowCount()):
            for col in range(self.historyTable.columnCount()):
                tableItem = self.historyTable.item(row, col)
                if tableItem:
                    QNewTxt = newTxtColor.replace("color:","")
                    QOldtxt = oldTxtColor.replace("color:","")
                    if QOldtxt == tableItem.foreground().color().name():
                        tableItem.setForeground(QColor(QNewTxt))
        
        #QLineEdit
        self.tableNameSearch.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")
        self.tableRollSearch.setStyleSheet(f"QLineEdit {{ {newTxtColor } }}")

        #Swaping txt Help Tab
        self.helpLog1.setStyleSheet(f"QTextEdit {{ {newTxtColor } }}")

        # super().setStyleSheet(f"""
        #     QMainWindow {{
        #         {mainAppBgrdColor};
        #     }}
        #     QMenuBar {{
        #         {mainAppBgrdColor};
        #     }}
        #     QMenuBar::item:selected {{
        #         {mainAppBgrdColor};
        #     }}
        # """)

        if self.darkMode:
            self.guiToDatabase("darkMode", 1)
        else:
            self.guiToDatabase("darkMode", 0)



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
        self.deathSkullLabel.setPixmap(self.deathSkullPixmapThinkSell)
        self.deathSkullLabel.repaint()

        self.organizeButton.setEnabled(False)

        #self.guiToConfig()
        if DAD_Utils.getDisplay(process_name=config.exeName) == DAD_Utils.getCurrentDisplay():
            self.showMinimized()
            time.sleep(0.5)

        # Run thread
        try:    
            DAD_Utils.logDebug("Starting SellButton thread...")
            self.logSellThread = logThread(True)
            self.logSellThreadRunning = True

            self.logSellThread.finished.connect(self.resetSkullyTxt)
            self.logSellThread.finished.connect(self.showNormal)
            self.logSellThread.finished.connect(self.stopSellLogThread)
            self.logSellThread.finished.connect(self.updatePixelVal)
            self.logSellThread.finished.connect(self.enableOrganizeButton)

            self.logSellThread.outputSignal.connect(self.appendSellLog)

            self.logSellThread.start()

        except error:
            DAD_Utils.logDebug("Error starting thread!")
            DAD_Utils.logGui("Error, Exiting!")


    
    # Organize Stash Button
    def handleOrganizeButton(self):
        # gui death skull update
        self.deathSkullLabel.setPixmap(self.deathSkullPixmapThinkOrganize)
        self.deathSkullLabel.repaint()

        self.sellButton.setEnabled(False)

        #self.guiToConfig()
        if DAD_Utils.getDisplay(process_name=config.exeName) == DAD_Utils.getCurrentDisplay():
            self.showMinimized()
            time.sleep(0.5)

        # Run thread
        try:    
            DAD_Utils.logDebug("Starting SellButton thread...")
            self.logOrganizeThread = logThread(False)
            self.logOrganizeThreadRunning = True

            self.logOrganizeThread.finished.connect(self.resetSkullyTxt)
            self.logOrganizeThread.finished.connect(self.showNormal)
            self.logOrganizeThread.finished.connect(self.stopOrganizeLogThread)
            self.logOrganizeThread.finished.connect(self.updatePixelVal)
            self.logOrganizeThread.finished.connect(self.enableSellButton)
            self.logOrganizeThread.outputSignal.connect(self.appendSellLog)

            self.logOrganizeThread.start()

        except error:
            DAD_Utils.logDebug("Error starting thread!")
            DAD_Utils.logGui("Error, Exiting!")



    # stop log thread
    def stopSellLogThread(self):
        DAD_Utils.logDebug("Stopping Log Thread")
        self.logSellThreadRunning = False


    def stopOrganizeLogThread(self):
        DAD_Utils.logDebug("Stopping Organize Log Thread")
        self.logOrganizeThreadRunning = False
    

    # enable sell buttons
    def enableSellButton(self):
        self.sellButton.setEnabled(True)

    def enableOrganizeButton(self):
        self.organizeButton.setEnabled(True)
    


    #update pixel val widget
    def updatePixelVal(self):
        conn, cur = database.connectDatabase()
        pxlVal = database.getConfig(cur,'pixelValue') 
        database.closeDatabase(conn)


        if self.pixelValue.text() != pxlVal:
            self.pixelValue.setText(str(pxlVal))



    # Log txt to GUI log
    def appendSellLog(self, txt): # append output to QTextEdit log
        
        if self.sellLogNewline:
            self.sellLog.append("")
            self.sellLogNewline = False

        if "^" in txt:
            self.sellLogNewline = True
            txt = txt.replace("^","")

        self.sellLog.insertHtml(txt)
        scroll = self.sellLog.verticalScrollBar()
        scroll.setValue(scroll.maximum())



    # log txt to GUI history log
    def appendHistoryLog(self,txt):
        pass
        # self.historyLog.append(txt)



    # Build utility tab
    def utilityTab(self,darkMode):
        conn, cursor = database.connectDatabase()
        tab = QWidget()

        # line edits
        intValidHeight = QIntValidator(0,20)
        intValidWidth = QIntValidator(0,12)
        doubleValidundercut = QDoubleValidator(0,100,2)
        intValidSellMin = QIntValidator(0,100000)
        intValidSellMax = QIntValidator(0,100000)
        intPixelValue = QIntValidator(0,220)
        doubleValidSpeed = QDoubleValidator(0.3,5.0,2)
        hotkeyRegex = QRegExp("[A-Za-z]")
        charValidQuitHotkey = QRegExpValidator(hotkeyRegex)
        charValidSellHotkey = QRegExpValidator(hotkeyRegex)

        # deathskull
        self.deathSkullPixmapTalk = QPixmap('img/DeathSkullTalking.png')
        self.deathSkullPixmapThink = QPixmap('img/DeathSkullThinking.png')
        self.deathSkullLabel = QLabel()

        self.paintSkully(darkMode)

        # sell Items button
        self.sellButton = QPushButton(self)
        self.sellButton.setIcon(QIcon("img/DaDButton.png"))
        self.sellButton.setIconSize(QSize(155,35))
        self.sellButton.clicked.connect(self.handleSellItemButton)
        self.sellButton.setFixedSize(QSize(155,35))

        # organize Stash button
        self.organizeButton = QPushButton(self)
        self.organizeButton.setIcon(QIcon("img/organizeButtonEA.png"))
        self.organizeButton.setIconSize(QSize(155,35))
        self.organizeButton.clicked.connect(self.handleOrganizeButton)
        self.organizeButton.setFixedSize(QSize(155,35))

        # dark mode button
        self.darkModeButton = QPushButton(self)
        self.darkModeButton.setIcon(QIcon("img/darkModeIcon.png"))
        self.darkModeButton.setIconSize(QSize(38,38))
        self.darkModeButton.setFixedSize(36,36)
        self.darkModeButton.clicked.connect(self.handleDarkModeButton)

        # logs
        self.logSellThreadRunning = False
        self.logOrganizeThreadRunning = False

        self.sellLogNewline = False
        self.sellLog = QTextEdit(self)
        self.sellLog.setReadOnly(True)
        self.sellLog.ensureCursorVisible()
        
        # exit hotkey layout
        closeHotkeyLayout = QHBoxLayout()

        closeHotkeyLabelFront = QLabel(f"Ctrl +")
        closeHotkeyLabelFront.setFont(QFont("Perpetua",15))
        closeHotkeyLabelFront.setStyleSheet("color: red")
        closeHotkeyLabelFront.setFixedSize(75,22)
        closeHotkeyLabelFront.setAlignment(Qt.AlignRight)

        self.exitHotkeyField = QLineEdit()
        self.exitHotkeyField.setFont(QFont("Perpetua",15))
        self.exitHotkeyField.setStyleSheet("color: red")
        self.exitHotkeyField.setFixedSize(25,25)
        self.exitHotkeyField.setText(database.getConfig(cursor,'closeHotkey'))
        self.exitHotkeyField.setAlignment(Qt.AlignCenter)
        self.exitHotkeyField.setValidator(charValidQuitHotkey)
        self.exitHotkeyField.textChanged.connect(lambda: self.guiToDatabase("closeHotkey",self.exitHotkeyField.text().upper()))
        self.exitHotkeyField.textChanged.connect(lambda: self.exitHotkeyField.setText(self.exitHotkeyField.text().upper())
                                                                                    if self.exitHotkeyField.text() else None)

        exitHotkeyLabelBack = QLabel(": Exit SkullBuddy")
        exitHotkeyLabelBack.setFont(QFont("Perpetua",15))
        exitHotkeyLabelBack.setFixedSize(175,22)
        exitHotkeyLabelBack.setStyleSheet("color: red")
        exitHotkeyLabelBack.setAlignment(Qt.AlignLeft)

        closeHotkeyLayout.addWidget(closeHotkeyLabelFront)
        closeHotkeyLayout.addWidget(self.exitHotkeyField)
        closeHotkeyLayout.addWidget(exitHotkeyLabelBack)

        # sell Hotkey Layout
        sellHotkeyLayout = QHBoxLayout()

        sellHotkeyLabelFront = QLabel(f"Ctrl +")
        sellHotkeyLabelFront.setFont(QFont("Perpetua",15))
        sellHotkeyLabelFront.setStyleSheet("color: red")
        sellHotkeyLabelFront.setFixedSize(75,22)
        sellHotkeyLabelFront.setAlignment(Qt.AlignRight)

        self.sellHotkeyField = QLineEdit()
        self.sellHotkeyField.setFont(QFont("Perpetua",15))
        self.sellHotkeyField.setStyleSheet("color: red")
        self.sellHotkeyField.setFixedSize(25,25)
        self.sellHotkeyField.setText(database.getConfig(cursor,"sellHotkey"))
        self.sellHotkeyField.setAlignment(Qt.AlignCenter)
        self.sellHotkeyField.setValidator(charValidSellHotkey)
        self.sellHotkeyField.textChanged.connect(lambda: self.guiToDatabase("sellHotkey",self.sellHotkeyField.text().upper()))
        self.sellHotkeyField.textChanged.connect(lambda: self.sellHotkeyField.setText(self.sellHotkeyField.text().upper())
                                                                                    if self.sellHotkeyField.text() else None)

        sellHotkeyLabelBack = QLabel(": Sell Items/Stop Script")
        sellHotkeyLabelBack.setFont(QFont("Perpetua",15))
        sellHotkeyLabelBack.setStyleSheet("color: red")
        sellHotkeyLabelBack.setFixedSize(225,22)
        sellHotkeyLabelBack.setAlignment(Qt.AlignLeft)

        sellHotkeyLayout.addWidget(sellHotkeyLabelFront)
        sellHotkeyLayout.addWidget(self.sellHotkeyField)
        sellHotkeyLayout.addWidget(sellHotkeyLabelBack)

        self.methodLabel = QLabel("Enter Selling Info:")
        self.methodLabel.setFixedWidth(85)

        self.stashLabel = QLabel("Enter Stash Info:")
        self.organizeLabel = QLabel("Enter Organize Info:")

        self.appSpeed = QLineEdit()
        self.appSpeed.setPlaceholderText("Enter App Speed")
        self.appSpeed.setText(str(database.getConfig(cursor,'sleepTime')))
        self.appSpeed.setFixedWidth(155)
        #self.appSpeed.setAlignment(Qt.AlignCenter)
        self.appSpeed.setValidator(doubleValidSpeed)
        self.appSpeed.textChanged.connect(lambda: self.guiToDatabase("sleepTime",self.appSpeed.text()
                                                                    if self.appSpeed.text() else None))

        self.pixelValue = QLineEdit()
        self.pixelValue.setPlaceholderText("Detected Pixel Value")
        self.pixelValue.setText(str(database.getConfig(cursor,'pixelValue')))
        self.pixelValue.setValidator(intPixelValue)
        self.pixelValue.setFixedWidth(155)
        self.pixelValue.textChanged.connect(lambda: self.guiToDatabase("pixelValue",self.pixelValue.text()
                                                                    if self.pixelValue.text() else None))

        self.undercut = QLineEdit()
        self.undercut.setPlaceholderText("Enter Undercut Value")
        self.undercut.setText(str(database.getConfig(cursor,'sellUndercut')))
        self.undercut.setValidator(doubleValidundercut)
        self.undercut.textChanged.connect(lambda: self.guiToDatabase("sellUndercut",self.undercut.text()
                                                                    if self.undercut.text() else None))

        self.sellMin = QLineEdit()
        self.sellMin.setPlaceholderText("Enter Sell Min")
        self.sellMin.setText(str(database.getConfig(cursor,'sellMin')))
        self.sellMin.setValidator(intValidSellMin)
        self.sellMin.textChanged.connect(lambda: self.guiToDatabase("sellMin",int(self.sellMin.text()) 
                                                                    if self.sellMin.text() else None))

        self.sellMax = QLineEdit()
        self.sellMax.setPlaceholderText("Enter Sell Max")
        self.sellMax.setText(str(database.getConfig(cursor,'sellMax')))
        self.sellMax.setValidator(intValidSellMax)
        self.sellMax.textChanged.connect(lambda: self.guiToDatabase("sellMax",int(self.sellMax.text())
                                                                    if self.sellMax.text() else None))

        self.stashHeight = QLineEdit()
        self.stashHeight.setPlaceholderText("Enter Sell Height")
        self.stashHeight.setText(str(database.getConfig(cursor,'sellHeight')))
        self.stashHeight.setValidator(intValidHeight)
        self.stashHeight.setFixedWidth(155)
        self.stashHeight.textChanged.connect(lambda: self.guiToDatabase("sellHeight",int(self.stashHeight.text())
                                                                    if self.stashHeight.text() else None)) 

        self.stashWidth = QLineEdit()
        self.stashWidth.setPlaceholderText("Enter Sell Width")
        self.stashWidth.setText(str(database.getConfig(cursor,'sellWidth')))
        self.stashWidth.setValidator(intValidWidth)
        self.stashWidth.setFixedWidth(155)
        self.stashWidth.textChanged.connect(lambda: self.guiToDatabase("sellWidth",int(self.stashWidth.text())
                                                                    if self.stashWidth.text() else None))

        # Radio Buttons
        sellMethodSelect = QButtonGroup(self)
        self.radioMethodSelect = {
            1 : QRadioButton("Lowest Price"),
            2 : QRadioButton("Lowest Price w/o Outliers"),
            3 : QRadioButton("Lowest 3 Price Avg")
        }
        self.radioMethodSelect[database.getConfig(cursor,'sellMethod')].setChecked(True)
        for i in range(1,4):
            sellMethodSelect.addButton(self.radioMethodSelect[i])
            self.radioMethodSelect[i].toggled.connect(lambda: self.guiToDatabase('sellMethod',
            next((key for key, value in self.radioMethodSelect.items() if value.isChecked()),None)))

        sellOrganizeSelect = QButtonGroup(self)
        self.stashOrganizeMethod = {
            1 : QRadioButton("Displayed Stash"),
            2 : QRadioButton("Multi-Select Stash")
        }
        
        setorganizeSelect = self.stashOrganizeMethod.get(database.getConfig(cursor,'organizeMethod'), None)
        if setorganizeSelect: setorganizeSelect.setChecked(True)

        for i in range(1,3):
            sellOrganizeSelect.addButton(self.stashOrganizeMethod[i])
            self.stashOrganizeMethod[i].toggled.connect(lambda: self.guiToDatabase('organizeMethod',
            next((key for key, value in self.stashOrganizeMethod.items() if value.isChecked()),None)))
            self.stashOrganizeMethod[i].toggled.connect(self.handleStashCheckBoxes)

        #checkBoxes
        self.stashCheckboxSelect = {
            1 : QCheckBox("Stash 1"),
            2 : QCheckBox("Stash 2"),
            3 : QCheckBox("Stash 3"),
            4 : QCheckBox("Stash 4"),
            5 : QCheckBox("Stash 5"),
            6 : QCheckBox("Stash 6"),
            7 : QCheckBox("Shared Stash"),
            8 : QCheckBox("DLC Stash")
        }
        
        flag = database.getConfig(cursor, "organizeStashes")
        for n, checkbox in enumerate(self.stashCheckboxSelect.values()):
            checkbox.stateChanged.connect(self.stashCheckBoxToDatabase)
            if database.getConfig(cursor, "organizeMethod") != 2:
                checkbox.setEnabled(False)
            if bool(flag & (1 << (n))):
                checkbox.setChecked(True)
                
        
        
        # Log Layout
        logLayout = QVBoxLayout()
        logHeader = QHBoxLayout()

        logHeader.addLayout(closeHotkeyLayout)
        logHeader.addLayout(sellHotkeyLayout)
        logHeader.addStretch()
        logHeader.addWidget(self.darkModeButton)
        logLayout.addWidget(self.sellLog)

        # Settings Layout
        settingsLayoutSelling = QVBoxLayout()
        settingsLayoutOrganize = QVBoxLayout()
        settingsMinMaxLayout = QHBoxLayout()
        settingsButtonLayout = QHBoxLayout()
        
        #Build settings for selling items
        settingsLayoutSelling.addWidget(self.methodLabel)

        for value in self.radioMethodSelect.values():
            settingsLayoutSelling.addWidget(value)

        settingsLayoutSelling.addSpacerItem(QSpacerItem(155, 22, QSizePolicy.Fixed, QSizePolicy.Fixed))
        settingsLayoutSelling.addWidget(self.stashHeight)
        settingsLayoutSelling.addWidget(self.stashWidth)
        settingsLayoutSelling.addWidget(self.undercut)

        settingsMinMaxLayout.addWidget(self.sellMin)
        settingsMinMaxLayout.addWidget(self.sellMax)
        settingsLayoutSelling.addLayout(settingsMinMaxLayout)

        settingsLayoutSelling.addSpacerItem(QSpacerItem(155, 25, QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        #build settings for organzing items
        settingsLayoutSelling.addSpacerItem(QSpacerItem(155, 4, QSizePolicy.Fixed, QSizePolicy.Fixed))
        settingsLayoutOrganize.addWidget(self.organizeLabel)

        for value in self.stashOrganizeMethod.values():
            settingsLayoutOrganize.addWidget(value)

        settingsLayoutOrganize.addSpacerItem(QSpacerItem(80, 35, QSizePolicy.Expanding, QSizePolicy.Fixed))

        checkCol1 = QVBoxLayout()
        checkCol2 = QVBoxLayout()
        checkWrapper = QHBoxLayout()

        for n, checkbox in enumerate(self.stashCheckboxSelect.values()):
            if n + 1 < 7:
                checkCol1.addWidget(checkbox)
            else:
                checkCol2.addWidget(checkbox)

        checkCol2.addSpacerItem(QSpacerItem(80, 98, QSizePolicy.Expanding, QSizePolicy.Fixed))

        #checkCol2.add

        checkWrapper.addLayout(checkCol1)
        checkWrapper.addLayout(checkCol2)

        settingsLayoutOrganize.addLayout(checkWrapper)


        settingsWrapper = QHBoxLayout()
        settingsWrapper.addLayout(settingsLayoutSelling)
        settingsWrapper.addLayout(settingsLayoutOrganize)
        settingsWrapper.addSpacerItem(QSpacerItem(1600, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        settingsFinalLayout = QVBoxLayout()
        
        speedWrapper = QHBoxLayout()
        speedWrapper.addWidget(self.appSpeed)
        speedWrapper.addWidget(self.pixelValue)
        speedWrapper.addSpacerItem(QSpacerItem(1600, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        settingsButtonLayout.addWidget(self.sellButton)
        settingsButtonLayout.addWidget(self.organizeButton)
        settingsButtonLayout.addSpacerItem(QSpacerItem(150, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        settingsFinalLayout.addLayout(speedWrapper)
        settingsFinalLayout.addLayout(settingsWrapper)
        settingsFinalLayout.addLayout(settingsButtonLayout)

        # Graphics Setup
        skullyLayout = QVBoxLayout()
        skullyLayout.addWidget(self.deathSkullLabel)

        #Bottom Layout
        BottomLayout = QHBoxLayout()
        BottomLayout.addLayout(skullyLayout)
        BottomLayout.addLayout(settingsFinalLayout)

        # Main Layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(logHeader)
        mainLayout.addLayout(logLayout)
        mainLayout.addLayout(BottomLayout)
        tab.setLayout(mainLayout)

        self.tabs.addTab(tab,"Utility")

        database.closeDatabase(conn)



    # Build history tab
    def historyTab(self,darkMode):
        tab = QWidget()

        # #skully setup
        # self.deathSkullHistory = QPixmap('img/DeathSkullTalking.png')
        # self.deathSkullFetchHistory = QPixmap('img/DeathSkullThinking.png')
        # self.skully = QLabel()

        # #skully txt
        # deathSkullText = QPainter(self.deathSkullHistory)
        # deathSkullText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        # deathSkullText.setPen(QColor("red"))      # Set the color of the text
        # deathSkullText.drawText(167, 183, "view your item listing history...")
        # deathSkullText.drawText(165, 200, "i can remember everything...")
        # deathSkullText.drawText(172, 217, "just ask...")
        # deathSkullText.end()
        # deathSkullThinkText = QPainter(self.deathSkullFetchHistory)
        # deathSkullThinkText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        # deathSkullThinkText.setPen(QColor("red"))      # Set the color of the text
        # deathSkullThinkText.drawText(167, 183, "...let me think...")
        # deathSkullThinkText.end()
        # self.skully.setPixmap(self.deathSkullHistory)

        #skully history button
        # self.historyButton = QPushButton("View Listing History", self)
        # self.historyButton.clicked.connect(self.handleViewHistoryButton)

        #Total gold label
        self.totalGoldLabel = QLabel()
        self.totalGoldLabel.setFont(QFont("Monotype Corsiva",18))
        self.totalGoldLabel.setText("Total Value Listed:")

        #Wipe Database Button
        self.wipeDatabasebutton = QPushButton()
        self.wipeDatabasebutton.setFixedSize(105,25)
        self.wipeDatabasebutton.setFont(QFont("Perpetua",11))
        self.wipeDatabasebutton.setText("Wipe Database")
        self.wipeDatabasebutton.setStyleSheet("color: red")
        self.wipeDatabasebutton.clicked.connect(self.handleWipeDatabaseButton)

        #Total gold Number
        self.totalGoldNumber = QLabel()
        self.totalGoldNumber.setFont(QFont("Monotype Corsiva",24))
        self.totalGoldNumber.setStyleSheet("color: #DAA520")
        # skullyGoldCount = f"{config.totalListedGold:,}"
        # self.totalGoldNumber.setText(skullyGoldCount)

        #add all for skully
        totalGoldLayout = QHBoxLayout()
        #skullyLayoutImg = QHBoxLayout()
        goldDisplayLayout = QHBoxLayout()
        #skullyLayoutImg.addWidget(self.skully)

        #goldDisplayLayout.addSpacerItem(QSpacerItem(1, 100, QSizePolicy.Fixed, QSizePolicy.Fixed))
        goldDisplayLayout.addWidget(self.totalGoldLabel,alignment=Qt.AlignLeft)
        goldDisplayLayout.addWidget(self.totalGoldNumber,alignment=Qt.AlignLeft)
        goldDisplayLayout.addSpacerItem(QSpacerItem(300, 15, QSizePolicy.Expanding, QSizePolicy.Fixed))
        #skullyLayoutGold.addSpacerItem(QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))
        # skullyLayoutButtons.addWidget(self.historyButton)
        #skullyLayoutTotal.addLayout(skullyLayoutImg)
        totalGoldLayout.addLayout(goldDisplayLayout)

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

        if darkMode:
            mainAppBgrdColor = "background-color: #18181b"
            newTxtColor = "color:#ffffff"
        else:
            mainAppBgrdColor = "background-color: #ffffff"
            newTxtColor = "color:#000000"

        self.historyTable.setStyleSheet(f"""
            QHeaderView::section {{
               {mainAppBgrdColor}; {newTxtColor}; 
            }}
            QHeaderView::section:horizontal {{
                {mainAppBgrdColor}; 
            }}
            QHeaderView::section:vertical {{
                {mainAppBgrdColor}; 
            }}
            QTableCornerButton::section {{
                {mainAppBgrdColor};  
            }}
            """)

        #Table search rarity & roll
        self.tableNameSearch = QLineEdit()
        self.tableNameSearch.setFixedSize(100, 25)  
        self.tableNameSearch.setPlaceholderText("Search Items...")
        self.tableNameSearch.textChanged.connect(self.filterName)

        self.tableRollSearch = QLineEdit()
        self.tableRollSearch.setFixedSize(100, 25)   
        self.tableRollSearch.setPlaceholderText("Search Rolls...")
        self.tableRollSearch.textChanged.connect(self.filterRolls)

        #History table header
        historyTableHeader.addWidget(self.tableNameSearch,alignment=Qt.AlignLeft)
        historyTableHeader.addSpacerItem(QSpacerItem(113, 12, QSizePolicy.Fixed, QSizePolicy.Fixed))
        historyTableHeader.addWidget(self.tableRollSearch,alignment=Qt.AlignLeft)
        historyTableHeader.addSpacerItem(QSpacerItem(800, 12, QSizePolicy.Expanding, QSizePolicy.Fixed))
        historyTableHeader.addWidget(self.wipeDatabasebutton,alignment=Qt.AlignRight)


        # Add all widgets
        historyLayout.addWidget(self.historyTable)

        # BUILD ALL GUI
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(historyTableHeader)
        mainLayout.addLayout(historyLayout)
        mainLayout.addLayout(totalGoldLayout)

        tab.setLayout(mainLayout)

        self.tabs.addTab(tab,"History")




    # Build help tab
    def helpTab(self,darkMode):
        tab = QWidget()

        #help widget
        self.helpLog1 = QTextEdit()
        self.helpLog1.setReadOnly(True)
        self.helpLog1.setFont(QFont("Ariel",8))
        self.helpLog1.setText(f"""
        How to use SkullBuddy:
                                    
        Launch Dark and Darker
        Navigate to Trade -> Marketplace -> My Listings
        Select stash to sell from
        Adjust settings
        Click Sell Items
                             
        Do not spam hotkeys                        

        App Speed:
        Controlls SkullBuddy's execution time
        Recommended value: 1.0 - 1.2
        Lower values increase speed  higher values decrease speed
                              

        Detected Pixel Value:
        SkullBuddy automatically sets this value while running
        If SkullBuddy is strugging to detect items lower the value to around 30-40
        If SkullBuddy is continously hovering empty stash squares increase the value 
                             
        Selling Settings:
               
        Sell Height and Width: 
        Creates a box from top left corner to include items being sold
                        
        Examples:
        Sell Hieght:  4 & Sell Width: 12         includes first 4 rows of stash boxes
        Sell Hieght: 20 & Sell Width: 12        includes all stash boxes
        Sell Hieght: 10 & Sell Width: 6          includes first quadrant of stash boxes  
                              
                                   
        Selling Method: 
        Determines calculated item price
        Lowest Price:                                    Lists with lowest recorded price
        Lowest Price w/o Outliers:                Lists with lowest recorded price, removing low/mislisted  prices
        Lowest 3 Price Avg:                          Lists with the average of the lowest 3 prices
                        
                        
        Undercut Value: 
        Decreases recorded price to sell faster
        Enter a number (1 - 100) to undercut the recorded price by a static value
        Enter a decimal value (0.01 - 0.99) to undercut the recorded price by percentage
                        
        Example: read 100 
        Undercut Value: 20                          100 - 20 = 80, list at 80 gold
        Undercut Value: .11                         100 - (100 * .11) = 89, list at 89 gold    

                             
        Sell Min and Max:
        Max and Min limits for listing price          

        Organizing Settings (EARLY ACCESS!!):

        Displayed Stash: 
        Organizes currently displayed stash

        Multi-select Stash: 
        Oraganizes selected stashes
                              
        Select checkboxes based on how many stashes you have unlocked
                                                            
        Example: 0 extra stashes
        Stash 1: mapped to Stash 1
        Shared Stash: mapped to Stash 2
        DLC Stash: mapped to Stash 3
                              
        Example: 2 extra stashes 
        Stash 1: mapped to Stash 1
        Stash 2: mapped to Stash 2
        Stash 3: mapped to Stash 3
        Shared Stash: mapped to Stash 4
        DLC Stash: mapped to Stash 5
        """)
        self.helpLog1.setAlignment(Qt.AlignLeft)

        devLabel = QLabel('<a href="https://github.com/ClaySolves">Dev</a>')
        devLabel.setOpenExternalLinks(True)
        devLabel.setAlignment(Qt.AlignCenter)

        donateLabel = QLabel('<a href="https://paypal.me/SolvingClay">Donate</a>')
        donateLabel.setOpenExternalLinks(True)
        donateLabel.setAlignment(Qt.AlignCenter)

        discordLabel = QLabel('<a href="https://discord.gg/Gd3Hr78H">Discord</a>')
        discordLabel.setOpenExternalLinks(True)
        discordLabel.setAlignment(Qt.AlignCenter)

        mainLayout = QVBoxLayout()
        linksLayout = QHBoxLayout()

        mainLayout.addWidget(self.helpLog1)

        linksLayout.addSpacerItem(QSpacerItem(300, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        linksLayout.addWidget(devLabel)
        linksLayout.addWidget(discordLabel)
        linksLayout.addWidget(donateLabel)
        linksLayout.addSpacerItem(QSpacerItem(300, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        mainLayout.addLayout(linksLayout)

        tab.setLayout(mainLayout)

        self.tabs.addTab(tab,"Help")



     # reset skully txt
    def resetSkullyTxt(self):
        time.sleep(0.1)

        self.deathSkullLabel.setPixmap(self.deathSkullPixmapTalk)
        self.deathSkullLabel.repaint()



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
        if str(config.sellUndercut) != txtRead:
            if "." in txtRead:
                DAD_Utils.updateConfig("undercutValue",float(txtRead))
            else:
                DAD_Utils.updateConfig("undercutValue",int(txtRead))

        txtRead = self.sellMin.text()
        if str(config.sellMin) != txtRead:
            DAD_Utils.updateConfig("sellMin",int(txtRead))

        txtRead = self.sellMax.text()
        if str(config.sellMax) != txtRead:
            DAD_Utils.updateConfig("sellMax",int(txtRead))



    # update database Config from gui selections
    def guiToDatabase(self,var,val):
        def floatSanitize(newVal):
            if newVal == '.':
                newVal = None
            elif '.' in newVal:
                newVal = float(newVal)
            else:
                newVal = int(newVal)
            return newVal
        
        conn, cursor = database.connectDatabase()

        if var == "sellUndercut" and val:
            val = floatSanitize(val)

        if var == "sleepTime" and val:
            val = floatSanitize(val)
                
        database.setConfig(cursor,var,val)
        database.closeDatabase(conn)



    def handleWipeDatabaseButton(self):
        class warnBeforeWipe(QDialog):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Do you really wanna do that bwo?")
                self.setFixedSize(350,100)

                warningLabel = QLabel("Listing history will be PERMANENTLY Deleted!!!")
                warningLabel.setStyleSheet("color: red")
                warningLabel.setFont(QFont("Perpetua",12))
                
                wipeButton = QPushButton("Wipe Data")
                wipeButton.setFixedSize(100,25)
                wipeButton.setStyleSheet("Color: red")
                wipeButton.clicked.connect(self.wipeDatabase)  # Closes the dialog

                nvmButton = QPushButton("Cancel")
                nvmButton.setFixedSize(100,25)
                nvmButton.clicked.connect(self.accept)  # Closes the dialog

                finalLayout = QVBoxLayout()
                layoutButtons = QHBoxLayout()
                layoutButtons.addWidget(wipeButton)
                layoutButtons.addWidget(nvmButton)

                finalLayout.addWidget(warningLabel)
                finalLayout.addLayout(layoutButtons)

                self.setLayout(finalLayout)

            def wipeDatabase(self):
                conn, cur = database.connectDatabase()
                database.wipeDatabase(cur)
                database.closeDatabase(conn)
                self.accept()


        warning = warnBeforeWipe()
        warning.exec_()



    # handle stash select checkboxes
    def handleStashCheckBoxes(self):
        setVal = False if self.stashOrganizeMethod[1].isChecked() else True
        for n, checkbox in enumerate(self.stashCheckboxSelect.values()):
                checkbox.setEnabled(setVal)



    #handle checkbox data to send to database
    def stashCheckBoxToDatabase(self):
        conn, cur = database.connectDatabase()
        flag = database.getConfig(cur, "organizeStashes")
        if flag == None: flag = 0

        for n, checkbox in enumerate(self.stashCheckboxSelect.values()):
            if checkbox.isChecked():
                flag |= 1 << (n)
            else:
                flag &= ~(1 << (n))

        database.setConfig(cur, "organizeStashes", flag)
        database.closeDatabase(conn)
            


    # Update history table
    def updateHistoryTable(self):
        conn, cur = database.connectDatabase()
        data = database.getStoredItems(cur)
        if not data:
            database.closeDatabase(conn)
            return

        #if data is displayed, wipe and reprint
        #todo: optimize
        if self.historyTable.rowCount() > 0:
            self.historyTable.setRowCount(0)

        numItems = 0
        totalGold = 0
        for i, item in enumerate(data):

            if not item[0] or not item[1] or not item[3]:
                continue

            self.historyTable.setRowCount(self.historyTable.rowCount() + 1)    
            self.historyTable.setRowHeight(numItems, 40)

            #Update name
            printColor = "white" if database.getConfig(cur,"darkMode") else "black"
            namePrint = item[0] if item[0] else 'NameReadError'
            tableName = QTableWidgetItem(namePrint)
            tableName.setFont(QFont("Arial",8))
            tableName.setForeground(QColor(printColor))
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
        self.filterHistoryTable(txt,0)



    # filter history table by name
    def filterRolls(self):
        txt = self.tableRollSearch.text().lower()
        self.filterHistoryTable(txt,3,8)
    

    # filter text in history table
    def filterHistoryTable(self,txt,column,column2=0):
        txt = re.sub(r'[^a-zA-Z0-9%]', '', txt)
        if txt == "":
            for row in range(self.historyTable.rowCount()):
                for col in range(self.historyTable.columnCount()):
                    item = self.historyTable.item(row, col)
                    if item:
                        if item.font().underline():
                                font = QFont("Arial",7)
                                font.setUnderline(False)
                                item.setFont(font)
            return

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

                            font = QFont("Arial",7)
                            font.setUnderline(True)
                            item.setFont(font)

                            # highlightItem = "<u>" + itemTxt + "</u>"
                            # highlightItemSet = QTableWidgetItem(highlightItem)
                            # DAD_Utils.logDebug(f" trying to underline txt: {highlightItem}")
                            # self.historyTable.setItem(row, col, highlightItemSet)
                            #break
                        else:
                            if item.font().underline():
                                font = QFont("Arial",7)
                                font.setUnderline(False)
                                item.setFont(font)

            else:
                item = self.historyTable.item(row, column)
                itemTxt = re.sub(r'[^a-zA-Z0-9%]', '', item.text().strip().lower())
                if item and txt in itemTxt:
                    hideRow = False

            self.historyTable.setRowHidden(row, hideRow)



    # paint skully for gui
    def paintSkully(self,darkMode):
        if darkMode:
            self.deathSkullPixmapTalk = QPixmap('img/DeathSkullTalkingDark.png')
            self.deathSkullPixmapThinkSell = QPixmap('img/DeathSkullThinkingDark.png')
            self.deathSkullPixmapThinkOrganize = QPixmap('img/DeathSkullThinkingDark.png')
            
        else:
            self.deathSkullPixmapTalk = QPixmap('img/DeathSkullTalking.png')
            self.deathSkullPixmapThinkSell = QPixmap('img/DeathSkullThinking.png')
            self.deathSkullPixmapThinkOrganize = QPixmap('img/DeathSkullThinking.png')

        self.deathSkullText = QPainter(self.deathSkullPixmapTalk)
        self.deathSkullText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        self.deathSkullText.setPen(QColor("red"))      # Set the color of the text
        self.deathSkullText.drawText(167, 183, "Greetings ... I list items ...")
        self.deathSkullText.drawText(145, 200, "Navigate to your market stash ...")
        self.deathSkullText.drawText(152, 217, "Adjust settings ... Click Sell Items ...")
        self.deathSkullText.end()

        
        self.deathSkullThinkText = QPainter(self.deathSkullPixmapThinkSell)
        self.deathSkullThinkText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        self.deathSkullThinkText.setPen(QColor("red"))      # Set the color of the text
        self.deathSkullThinkText.drawText(167, 183, "Selling your items...")
        self.deathSkullThinkText.drawText(145, 200, "Don't move your mouse...")
        self.deathSkullThinkText.end()
    
        self.deathSkullThinkText = QPainter(self.deathSkullPixmapThinkOrganize)
        self.deathSkullThinkText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        self.deathSkullThinkText.setPen(QColor("red"))      # Set the color of the text
        self.deathSkullThinkText.drawText(167, 183, "Organizing your items...")
        self.deathSkullThinkText.drawText(145, 200, "Don't move your mouse...")
        self.deathSkullThinkText.end()

        self.deathSkullLabel.setPixmap(self.deathSkullPixmapTalk)
        self.deathSkullLabel.repaint()