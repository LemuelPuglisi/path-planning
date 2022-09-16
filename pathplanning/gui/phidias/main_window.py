from typing import Optional
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from pathplanning.core.base import DrawPoint
from pathplanning.core.patterns.observer import Observer
from pathplanning.core.phidias.handler import PHIDIASHandler
from pathplanning.gui.phidias.drawing_panel import PHIDIASDrawingPanelWidget
from pathplanning.gui.phidias.sidebar import PHIDIASSideBarWidget
from pathplanning.core.env import PHIDIASEnvironment
from pathplanning.core.dynamics.base import RoboticSystem


class PHIDIASMainWindow(QMainWindow):
    
    def __init__(self, env: PHIDIASEnvironment, 
                       system: RoboticSystem, 
                       handler: PHIDIASHandler):
        super(PHIDIASMainWindow, self).__init__()
        
        self.setWindowTitle("path-planning")
        self.setFixedSize(QSize(1350, 700))

        self.env = env
        self.system = system
        self.handler = handler
        self.handler.setConnectionCb(self.connectionCallback)

        self.drawing_panel = PHIDIASDrawingPanelWidget(env, system)
        self.sidebar_widget = PHIDIASSideBarWidget()
        self.sidebar_widget.blockButtons()

        # we move the component "wiring" to the
        # upper component. This can be replaced to 
        # some design patterns later. 
        self.sidebar_widget.starting_point_button.clicked.connect(self.awaitStartingPoint)
        self.sidebar_widget.set_container_button.clicked.connect(self.awaitContainerSetup)
        self.sidebar_widget.add_item_button.clicked.connect(self.awaitItemAddition)

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
                
    def startSimulation(self):
        self.system.reset()
        self.drawing_panel.reset() 
        self.drawing_panel.start()

    def awaitStartingPoint(self):
        self.drawing_panel.mousePressEvent = self.handleStartingPoint        
        
    def handleStartingPoint(self, event):
        self.drawing_panel.mousePressEvent = lambda e: None
        position = event.pos()
        point = DrawPoint(position.x(), position.y())       
        self.env.moveCartStationary(point.toSimPoint())
        self.sidebar_widget.releaseButtons()
        self.drawing_panel.update()

    def awaitContainerSetup(self):
        self.drawing_panel.mousePressEvent = self.handleContainerSetup        

    def handleContainerSetup(self, event):
        self.drawing_panel.mousePressEvent = lambda e: None
        position = event.pos()
        point = DrawPoint(position.x(), position.y())       
        self.env.moveContainer(point.toSimPoint())
        self.sidebar_widget.releaseButtons()
        self.drawing_panel.update()
        
    def awaitItemAddition(self):
        self.drawing_panel.mousePressEvent = self.handleItemAddition        

    def handleItemAddition(self, event):
        self.drawing_panel.mousePressEvent = lambda e: None
        position = event.pos()
        item = DrawPoint(position.x(), position.y()).toSimPoint()

        try:
            self.handler.notifyItem(item)
        except:
            self.sidebar_widget.instruct('PHIDIAS handler not initialized.')
            
        self.env.addItem(item)
        self.sidebar_widget.releaseButtons()
        self.drawing_panel.update()
        
    def connectionCallback(self):
        self.sidebar_widget.releaseButtons()
        self.sidebar_widget.instruct('PHIDIAS client connected.')
