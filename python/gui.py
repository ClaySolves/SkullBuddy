from PyQt5.QtGui import QKeyEvent
import DAD_Utils
import sys
import config
import time
import keyboard
import subprocess
import logging
from io import StringIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QKeySequence

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
class WorkerThread(QThread):
    outputSignal = pyqtSignal(str)  # var for output

    def run(self): # run function

        oldStdout = sys.stdout
        sys.stdout = GuiScriptStream(self.outputSignal)

        DAD_Utils.logGui("Starting Squirebot...")
        DAD_Utils.searchStash()
        DAD_Utils.logGui("Finished!")
    
        sys.stdout = oldStdout


#gui design
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # gui element setup
        self.setWindowTitle("SquireBot")
        self.setGeometry(100, 100, 800, 400)

        # button
        self.sellButton = QPushButton("Sell Items", self)
        self.sellButton.clicked.connect(self.handleSellItemButton)

        # log
        self.output_log = QTextEdit(self)
        self.output_log.setReadOnly(True)

        # labels
        self.helpLabel = QLabel("Ctrl + Q: Exit SquireBot")
        self.methodLabel = QLabel("Select Selling Method:")
        self.stashLabel = QLabel("Enter Stash Info:")

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
        logLayout.addWidget(self.output_log)

        # Settings Layout
        settingsLayout = QVBoxLayout()
        settingsLayout.addWidget(self.helpLabel)
        settingsLayout.addWidget(self.methodLabel)
        for value in self.radioMethodSelect.values():
            settingsLayout.addWidget(value)
        settingsLayout.addWidget(self.undercut)

        settingsLayout.addWidget(self.stashLabel)
        settingsLayout.addWidget(self.stashIndex)
        settingsLayout.addWidget(self.stashHeight)
        settingsLayout.addWidget(self.stashWidth)
        settingsLayout.addWidget(self.sellButton)

        # Main Layout
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(logLayout)
        mainLayout.addLayout(settingsLayout)

        # Finalize GUI
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    # Sell Items Button
    def handleSellItemButton(self):
        #handle config updates from settings
        updateMethod = next((key for key, value in self.radioMethodSelect.items() if value.isChecked()),None)
        if updateMethod: 
            DAD_Utils.logDebug(f"Updating sellMethod ... METHOD: {updateMethod}")
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
            self.thread = WorkerThread()
            self.thread.outputSignal.connect(self.appendLog)
            self.thread.start()
        except error:
            logger.debug("Error starting thread!")
            DAD_Utils.logGui("Error, Exiting!")

    # Log txt to GUI log
    def appendLog(self, txt): # append output to QTextEdit log
        self.output_log.append(txt)

      