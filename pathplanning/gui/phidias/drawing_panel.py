import math
import pathlib

from PyQt5.QtCore import QSize, QTimer, QPoint
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPalette, QPainter, QTransform, QPixmap

from pathplanning.core.algorithms.base import PathPlanningBase
from pathplanning.core.const import DP_ITEM_PIC_PATH, DP_ROBOT_PIC_PATH, OBS_H, OBS_W, PANEL_H, PANEL_W
from pathplanning.core.dynamics.base import RoboticSystem
from pathplanning.core.env import Environment


class PHIDIASDrawingPanelWidget(QWidget):
        
    def __init__(self, env: Environment, system: RoboticSystem):
        super().__init__()
        self.env = env
        self.system = system
        self.setFixedSize(QSize(PANEL_W, PANEL_H))
        self.initUI()


    def initUI(self):
        self.setAutoFillBackground(True)
        drawing_panel_palette = self.palette()
        drawing_panel_palette.setColor(QPalette.Window, QColor('#010409'))
        self.setPalette(drawing_panel_palette)
        
        current_path = pathlib.Path(__file__).parent.resolve()
        robot_image = str(current_path) + '/../' + DP_ROBOT_PIC_PATH
        item_image = str(current_path) + '/../' + DP_ITEM_PIC_PATH
        self.robot_pic = QPixmap(robot_image)        
        self.item_pic = QPixmap(item_image)        

        self.delta_t = 1e-4
        self._timer_painter = QTimer(self)
        self._timer_painter.timeout.connect(self.go)
        self._timer_painter.setInterval(self.delta_t)
        

    def start(self):
        self._timer_painter.start()
        
        
    def reset(self):
        self._timer_painter.stop()
        self.update()

    def go(self):
        if not(self.system.step()):
            self._timer_painter.stop()
        self.update() # repaint window
        
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor('#0d1117'))
        qp.setBrush(QColor('#0d1117'))
        qp.drawRect(event.rect())

        #---------------------
        # Paint the arena    
        #---------------------   
        qp.setPen(QColor('white'))
        self.draw_rect(qp)
        
        #---------------------
        # Paint the measurements   
        #---------------------   
        qp.setPen(QColor('white'))
        self.draw_measures(qp)

        #---------------------
        # Paint the items    
        #---------------------    
        for o in self.env.items:
            drawable = o.toDrawPoint().toTopLeft(OBS_W, OBS_H).toQPoint()
            qp.drawPixmap(drawable, self.item_pic)        

        # ---------------------
        # Paint the robot    
        # ---------------------
        cart = self.env.cart
        center = cart.pos.toDrawPoint()
        heading = cart.getHeading()
        shape = self.robot_pic.size()
        top_left = center.toTopLeft(shape.width(), shape.height())
         
        qp.setPen(QColor('white'))
        qp.setBrush(QColor('red'))    
        # painting rotation according to theta. 
        # this will be a problem when we put in obstacles.
        t = QTransform()
        t.translate(top_left.x + shape.width()/2, top_left.y + shape.height()/2)
        t.rotate(-math.degrees(heading))
        t.translate(-(top_left.x + shape.width()/2), - (top_left.y + shape.height()/2))
        qp.setTransform(t)
        # BECAUSE: everything we put here will rotate
        # according to theta, so put the obstacles ABOVE
        # this block. 
        qp.drawPixmap(top_left.x, top_left.y, self.robot_pic)
        qp.end()
        
        
    def draw_rect(self, qp):
        qp.drawLine(0, 0, PANEL_W, 0)                        # upper line
        qp.drawLine(PANEL_W - 2, 0, PANEL_W - 2, PANEL_H)    # right line 
        qp.drawLine(PANEL_W, PANEL_H-2, 0, PANEL_H-2)        # lower line
        qp.drawLine(0, PANEL_H, 0, 0)                        # left  line 
        

    def draw_measures(self, qp):
        (x, y, theta) = self.env.cart.getPose()
        qp.drawText(50,  530, "X  = %6.3f m" % (x))
        qp.drawText(200, 530, "Y  = %6.3f m" % (y))
        qp.drawText(350, 530, "Th = %6.3f deg" % (math.degrees(theta)))
        qp.drawText(500, 530, "T  = %6.3f s" % (self.system.t))