from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication

def set_dark_theme(app: QApplication) -> None:
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")
    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor('white'))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor('black'))
    palette.setColor(QPalette.ToolTipText, QColor('white'))
    palette.setColor(QPalette.Text, QColor('white'))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor('white'))
    palette.setColor(QPalette.BrightText, QColor('red'))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor('black'))
    app.setPalette(palette)