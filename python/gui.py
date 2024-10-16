from PyQt5.QtGui import QKeyEvent
import DAD_Utils
import sys
import time
import keyboard
import subprocess
from io import StringIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt

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
        DAD_Utils.mainLoop()
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
        self.button = QPushButton("Sell Items", self)
        self.button.clicked.connect(self.on_button_click)

        # log
        self.output_log = QTextEdit(self)
        self.output_log.setReadOnly(True)

        #label
        self.helpLabel = QLabel("Ctrl + Q: Exit SquireBot")

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.output_log)
        layout.addWidget(self.button)
        layout.addWidget(self.helpLabel)
 
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_click(self):
        print("Button Press!") 
        try:
            self.thread = WorkerThread()
            self.thread.outputSignal.connect(self.appendLog)
            self.thread.start()
            print("Thread started!")  
        except error:
            print("Error, Exiting!")  

    def appendLog(self, txt): # append output to QTextEdit log
        self.output_log.append(txt)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.stopScript()

    def stopScript(self):
        print("Exiting...")
        QApplication.quit()
            