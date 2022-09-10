import sys

from PyQt5.QtWidgets import QApplication
from pathplanning.gui.main_window import MainWindow
from pathplanning.gui.darktheme import set_dark_theme

def run_application():
    app = QApplication(sys.argv)
    set_dark_theme(app)
    window = MainWindow()
    window.show()
    app.exec()
    