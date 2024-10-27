from PyQt5.QtGui import QKeyEvent
import DAD_Utils
import sys
import time
import keyboard
import subprocess
import logging
import eztest
from io import StringIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon

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

        print("calling main loop")
        DAD_Utils.searchStash()
        print("Done")
    
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

        # Radio Buttons
        self.radioMethodSelect = {
            1 : QRadioButton("Lowest Price"),
            2 : QRadioButton("Lowest Price w/o Outliers"),
            3 : QRadioButton("Lowest 3 Price Avg")
        }
        self.radioMethodSelect[1].setChecked(True)
        
        # Log Layout
        logLayout = QVBoxLayout()
        logLayout.addWidget(self.helpLabel)
        logLayout.addWidget(self.output_log)

        # Settings Layout
        settingsLayout = QVBoxLayout()
        for value in self.radioMethodSelect.values():
            settingsLayout.addWidget(value)
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
        updateMethod = next((key for key, value in self.radioMethodSelect.items() if value.isChecked()),None)
        
        if updateMethod: 
            DAD_Utils.logDebug(f"Updating sellMethod ... METHOD: {updateMethod}")
            DAD_Utils.updateConfig("sellMethod",updateMethod)
 
        try:
            self.thread = WorkerThread()
            self.thread.outputSignal.connect(self.appendLog)
            self.thread.start()
            print("Thread started!")  
        except error:
            print("Error, Exiting!")  

    # Log txt to GUI log
    def appendLog(self, txt): # append output to QTextEdit log
        self.output_log.append(txt)

    # Close GUI
    def closeApp(self):
        print("Exiting...")
        QApplication.quit()
            