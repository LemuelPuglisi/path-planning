from pathplanning.core.base import SimPoint
from pathplanning.core.cinematics import Cart
from pathplanning.core.const import OBS_H, OBS_W, SCALE


class Obstacle:
    
    def __init__(self, center: SimPoint):
        self.x = center.x
        self.y = center.y
        self.w = OBS_W / SCALE
        self.h = OBS_H / SCALE        


class Environment:
    """ This class is responsible for letting the GUI know
        where objects of the environment are. Also, the
        coordinates here are not transformed in the drawing
        panel coordinate system, so the transformation must 
        be done inside the DrawingPanelWidget. 
    """
    
    def __init__(self, cart: Cart, target: SimPoint):
        self.cart = cart
        self.target = target
        self.obstacles = []

    def moveCartStationary(self, point: SimPoint):
        self.cart.reset(point)
        
    def moveTarget(self, point: SimPoint):
        self.target = point
        
    def addObstacle(self, obstacle: SimPoint):
        self.obstacles.append(obstacle)
        
    def reset(self):
        self.cart.reset(SimPoint(0, 0))
        self.target = SimPoint(0, 0)
        self.obstacles = []