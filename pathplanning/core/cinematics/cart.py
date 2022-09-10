import math

from pathplanning.core.base import SimPoint
from pathplanning.core.const import TWOPI

class Cart:

    def __init__(self, starting_point: SimPoint):
        self._setModelProperties()
        self.reset(starting_point)
                
    def _setModelProperties(self):
        self.M = 1.
        self.radius = .15
        self.b = .8
        self.beta = .8
        self.Iz = 0.5 * self.M * (self.radius ** 2)
                
                
    def reset(self, point: SimPoint):
        self.v = 0
        self.w = 0
        self.theta = 0
        self.pos = point
        

    @property
    def x(self):
        return self.pos.x
    

    @property
    def y(self):
        return self.pos.y


    @x.setter
    def x(self, x):
        self.pos.x = x


    @y.setter
    def y(self, y):
        self.pos.y = y


    def evaluate(self, delta_t, _force, _torque):
        new_v = self.v * (1 - self.b * delta_t / self.M) + delta_t * _force / self.M
        new_w = self.w * (1 - self.beta * delta_t / self.Iz) + delta_t * _torque / self.Iz
        self.x = self.x + self.v * delta_t * math.cos(self.theta)
        self.y = self.y + self.v * delta_t * math.sin(self.theta)
        self.theta = (self.theta + delta_t * self.w) % TWOPI 
        self.v = new_v
        self.w = new_w


    def getPose(self):
        return (self.x, self.y, self.theta)
    
    
    def getCoordinates(self):
        return (self.x, self.y)
    
    
    def getHeading(self):
        return self.theta