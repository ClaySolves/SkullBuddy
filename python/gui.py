from PyQt5.QtGui import QKeyEvent
import DAD_Utils
import sys
import config
import time
import database
import keyboard
import subprocess
import logging
from io import StringIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox, QGraphicsView, QTabWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QKeySequence, QPixmap, QPainter, QFont, QColor

logger = logging.getLogger()  # Get the root logger configured in main.py



#basic exception
class error(Exception):
    pass


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

class listHistoryThread(QThread):
    outputSignal = pyqtSignal(str)  # var for output

    def run(self):
        oldStdout = sys.stdout
        sys.stdout = GuiScriptStream(self.outputSignal)

        conn, cur = database.connectDatabase()
        database.printDatabase(cur)

        sys.stdout = oldStdout

#gui design
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create tabs
        self.tabs = QTabWidget()
        self.utilityTab()
        self.historyTab()

        self.setCentralWidget(self.tabs)
        self.setWindowTitle("SkullBuddy")
        self.setGeometry(100, 100, 400, 800)


    # Update History Button
    def handleViewHistoryButton(self):
        self.skully.setPixmap(self.deathSkullFetchHistory)
        self.skully.repaint()

        try:    
            logger.debug("Starting thread...")
            self.historyThread = listHistoryThread()
            self.historyThread.outputSignal.connect(self.appendHistoryLog)
            self.historyThread.start()
        except error:
            logger.debug("Error starting thread!")
            DAD_Utils.logGui("Error, Exiting!")

    # Sell Items Button
    def handleSellItemButton(self):
        # gui death skull update
        self.deathSkullLabel.setPixmap(self.deathSkullPixmapThink)
        self.deathSkullLabel.repaint()
        

        #handle config updates from settings
        updateMethod = next((key for key, value in self.radioMethodSelect.items() if value.isChecked()),None)
        if updateMethod: 
            DAD_Utils.updateConfig("sellMethod",updateMethod)

        txtRead = self.stashIndex.text()
        if txtRead:
            DAD_Utils.updateConfig("stashSell",int(txtRead))

        txtRead = self.stashWidth.text()
        if txtRead:
            DAD_Utils.updateConfig("sellWidth",int(txtRead))

        txtRead = self.stashHeight.text()
        if txtRead:
            DAD_Utils.updateConfig("sellHeight",int(txtRead))

        txtRead = self.undercut.text()
        if txtRead:
            if "." in txtRead:
                DAD_Utils.updateConfig("undercutValue",float(txtRead))
            else:
                DAD_Utils.updateConfig("undercutValue",int(txtRead))

        # Run thread
        try:    
            logger.debug("Starting thread...")
            self.thread = logThread()
            self.thread.outputSignal.connect(self.appendSellLog)
            self.thread.start()
        except error:
            logger.debug("Error starting thread!")
            DAD_Utils.logGui("Error, Exiting!")

    # Log txt to GUI log
    def appendSellLog(self, txt): # append output to QTextEdit log
        self.sellLog.append(txt)
        if self.thread.isFinished():
            self.deathSkullLabel.setPixmap(self.deathSkullPixmapTalk)
            self.deathSkullLabel.repaint()

    # log txt to GUI history log
    def appendHistoryLog(self,txt):
        self.historyLog.append(txt)

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
        helpLabel = QLabel("Ctrl + Q: Exit SquireBot")
        methodLabel = QLabel("Select Selling Method:")
        stashLabel = QLabel("Enter Stash Info:")

        # line edits
        intValidIndex = QIntValidator(-1,10)
        intValidHeight = QIntValidator(0,20)
        intValidWidth = QIntValidator(0,12)
        doubleValid = QDoubleValidator(-1.0,100.0,2)

        self.undercut = QLineEdit()
        self.undercut.setPlaceholderText("Enter Undercut Value")
        self.undercut.setText(str(config.undercutValue))
        self.undercut.setValidator(doubleValid)

        self.stashIndex = QLineEdit()
        self.stashIndex.setPlaceholderText("Enter Sell Stash")
        self.stashIndex.setText(str(config.stashSell))
        self.stashIndex.setValidator(intValidIndex) 

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
        logLayout.addWidget(self.sellLog)

        # Settings Layout
        settingsLayout = QVBoxLayout()
        settingsLayout.addWidget(helpLabel)
        settingsLayout.addWidget(methodLabel)
        for value in self.radioMethodSelect.values():
            settingsLayout.addWidget(value)
        settingsLayout.addWidget(self.undercut)

        settingsLayout.addWidget(stashLabel)
        settingsLayout.addWidget(self.stashIndex)
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

    def historyTab(self):
        tab = QWidget()

        #skully setup
        skullyLayout = QHBoxLayout()
        self.deathSkullHistory = QPixmap('img/DeathSkullTalking.png')
        self.deathSkullFetchHistory = QPixmap('img/DeathSkullThinking.png')
        self.skully = QLabel()

        #skully txt
        deathSkullText = QPainter(self.deathSkullHistory)
        deathSkullText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        deathSkullText.setPen(QColor("red"))      # Set the color of the text
        deathSkullText.drawText(167, 183, "view your item listing history...")
        deathSkullText.drawText(145, 200, "i can remember everything...")
        deathSkullText.drawText(152, 217, "just ask...")
        deathSkullText.end()
        deathSkullThinkText = QPainter(self.deathSkullFetchHistory)
        deathSkullThinkText.setFont(QFont("Tahoma", 10))  # Set the font and font size
        deathSkullThinkText.setPen(QColor("red"))      # Set the color of the text
        deathSkullThinkText.drawText(167, 183, "...let me think...")
        deathSkullThinkText.end()

        #skully history button
        self.historyButton = QPushButton("View Listing History", self)
        self.historyButton.clicked.connect(self.handleViewHistoryButton)
        
        self.skully.setPixmap(self.deathSkullHistory)
        skullyLayout.addWidget(self.skully)
        skullyLayout.addWidget(self.historyButton)

        historyLayout = QVBoxLayout()

        #history log
        self.historyLog = QTextEdit(self)
        self.historyLog.setReadOnly(True)

        historyLayout.addWidget(self.historyLog)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(historyLayout)
        mainLayout.addLayout(skullyLayout)

        tab.setLayout(mainLayout)

        self.tabs.addTab(tab,"History")
      