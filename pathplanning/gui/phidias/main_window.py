from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from pathplanning.core.base import DrawPoint
from pathplanning.gui.phidias.drawing_panel import PHIDIASDrawingPanelWidget
from pathplanning.gui.phidias.sidebar import PHIDIASSideBarWidget
from pathplanning.core.env import Environment
from pathplanning.core.dynamics.base import RoboticSystem


class PHIDIASMainWindow(QMainWindow):
    
    def __init__(self, env: Environment, 
                       system: RoboticSystem):
        super(PHIDIASMainWindow, self).__init__()
                  
        self.setWindowTitle("path-planning")
        self.setFixedSize(QSize(1350, 700))

        self.env = env
        self.system = system

        self.drawing_panel = PHIDIASDrawingPanelWidget(env, system)
        self.sidebar_widget = PHIDIASSideBarWidget()

        # we move the component "wiring" to the
        # upper component. This can be replaced to 
        # some design patterns later. 
        # [...]        

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.drawing_panel)    
        main_layout.setContentsMargins(25, 0, 25, 0)
        
        main_widget = QWidget()
        main_widget.setAutoFillBackground(True)
        main_widget_palette = main_widget.palette()
        main_widget_palette.setColor(QPalette.Window, QColor('#010409'))
        main_widget.setPalette(main_widget_palette)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
                
        