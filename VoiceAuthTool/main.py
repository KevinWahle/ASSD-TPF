import sys
from PyQt5.QtWidgets import QApplication
from src.VoiceAuthToolApp import VoiceAuthToolApp

app = QApplication(sys.argv)
win = VoiceAuthToolApp()
win.show()
sys.exit(app.exec())