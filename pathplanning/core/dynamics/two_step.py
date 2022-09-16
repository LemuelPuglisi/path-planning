import math

from typing import List

from pathplanning.core.base import SimPoint
from pathplanning.core.dynamics.base import RoboticSystem
from pathplanning.core.cinematics import Cart
from pathplanning.core.controllers import PIDSat, Polar2DController, StraightLine2DMotion
from pathplanning.core.geometry import normalizeAngle
from pathplanning.core.patterns.observer import Observable

class TwoStepCartRobot(RoboticSystem, Observable):
    
    FIXHEADING=0
    MOVE2POINT=1

    def __init__(self, cart: Cart, heading_threshold=5e-5, dist_threshold=1e-2, delta_t=.005):
        RoboticSystem.__init__(self, delta_t)
        Observable.__init__(self)
        self.cart = cart
        self.heading_controller         = PIDSat(8, 0, 0, 1)
        self.linear_speed_controller    = PIDSat(15, 8, 0, 5) 
        self.angular_speed_controller   = PIDSat(6, 10, 0, 8) 
        self.polar_controller           = Polar2DController(2.5, 2, 2.0 , 2)
        self.trajectory                 = StraightLine2DMotion(1.5, 2, 2)
        
        self.target = None
        self.heading_threshold      = heading_threshold
        self.distance_threshold     = dist_threshold
        self.state = self.FIXHEADING
        self.path = []
        self.observers = []
        
        
    def reset(self):
        super().reset()
        self.heading_controller.reset()
        self.linear_speed_controller.reset()
        self.angular_speed_controller.reset()
        self.polar_controller.reset()
        self.state = self.FIXHEADING
        self.target = None
                
        
    def run(self):
        if self.target is None: return True
        
        if self.state == self.FIXHEADING:
            error = self.headingError()
            T = self.heading_controller.evaluateError(self.delta_t, error)
            self.cart.evaluate(self.delta_t, 0, T)            
            
            if abs(error) < self.heading_threshold:   
                (x,y,_) = self.getPose()
                self.trajectory.startMotion((x,y), self.target())
                self.state = self.MOVE2POINT
                return True
            return True
        else:
            distance = self.distanceError()            
            (x_target, y_target) = self.trajectory.evaluate(self.delta_t)
            (v_target, w_target) = self.polar_controller.evaluate(self.delta_t, x_target, y_target, self.getPose())
            F = self.linear_speed_controller.evaluate(self.delta_t, v_target, self.cart.v)
            T = self.angular_speed_controller.evaluate(self.delta_t, w_target, self.cart.w)
            self.cart.evaluate(self.delta_t, F, T)

            if distance < self.distance_threshold:
                if len(self.path) == 0: 
                    # PHIDIAS task.
                    item = self.cart.releaseItem()
                    self.notifyObservers('released', { 'item': item })
                    
                    self.reset()
                    return True
                
                # PHIDIAS task.
                self.notifyObservers('picked', { 'item': self.target })
                self.cart.pickItem(self.target)
                
                new_target = self.path.pop()
                self.target = new_target
                self.linear_speed_controller.reset()
                self.angular_speed_controller.reset()
                self.state = self.FIXHEADING
                return True
            return True
    
    
    def setup(self, path: List[SimPoint]) -> None:
        self.path = path
        self.path.reverse()
        self.target = self.path.pop()
        (x, y, _) = self.getPose()
        self.trajectory.startMotion((x, y), self.target())


    def getPose(self):
        return self.cart.getPose()


    def getSpeed(self):
        return (self.cart.v, self.cart.w)


    def distanceError(self):
        x, y, _ = self.getPose()
        dx = self.target.x - x
        dy = self.target.y - y
        return math.sqrt(dx*dx + dy*dy)

    def targetHeading(self):
        x, y, _ = self.getPose()
        xt, yt = self.target()
        dx = xt - x
        dy = yt - y
        target_heading = math.atan2(dy , dx)
        return target_heading

    def headingError(self):
        heading = self.getPose()[2]
        target_heading = self.targetHeading()                
        heading_error = normalizeAngle(target_heading - heading)
        if (heading_error > math.pi/2)or(heading_error < -math.pi/2):
            heading_error = normalizeAngle(heading_error + math.pi)
        return heading_error