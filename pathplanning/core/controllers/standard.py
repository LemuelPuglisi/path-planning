import math

from pathplanning.core.geometry import normalizeAngle
from pathplanning.core.controllers.virtual_robot import VirtualRobot

#-------------------------------
#-------------------------------
#-------------------------------

class Proportional:

    def __init__(self, kp):
        self.kp = kp

    def evaluate(self, target, current):
        error = target - current
        return self.kp * error

    def evaluate_error(self, error):
        return self.kp * error

#-------------------------------
#-------------------------------
#-------------------------------

class Integral:

    def __init__(self, ki):
        self.ki = ki
        self.output = 0

    def evaluate(self, delta_t, target, current):
        error = target - current
        self.output = self.output + self.ki * error * delta_t
        return self.output

    def evaluate_error(self, delta_t, error):
        self.output = self.output + self.ki * error * delta_t
        return self.output

#-------------------------------
#-------------------------------
#-------------------------------

class PIDSat:

    def __init__(self, kp, ki, kd, saturation, antiwindup = True):
        self.p = Proportional(kp)
        self.i = Integral(ki)
        self.kd = kd
        self.prev_error = 0
        self.saturation = saturation
        self.antiwindup = antiwindup
        self.in_saturation = False

    def evaluate(self, delta_t, target, current):
        error = target - current
        derivative  = (error - self.prev_error) / delta_t
        self.prev_error = error
        if not(self.antiwindup):
            self.i.evaluate(delta_t, target, current)
        elif not(self.in_saturation):
            self.i.evaluate(delta_t, target, current)
        output = self.p.evaluate(target, current) + self.i.output + \
          derivative * self.kd
        if output > self.saturation:
            output = self.saturation
            self.in_saturation = True
        elif output < -self.saturation:
            output = - self.saturation
            self.in_saturation = True
        else:
            self.in_saturation = False
        return output

    def evaluateError(self, delta_t, error):
        derivative  = (error - self.prev_error) / delta_t
        self.prev_error = error
        if not(self.antiwindup):
            self.i.evaluate_error(delta_t, error)
        elif not(self.in_saturation):
            self.i.evaluate_error(delta_t, error)
        output = self.p.evaluate_error(error) + self.i.output + \
          derivative * self.kd
        if output > self.saturation:
            output = self.saturation
            self.in_saturation = True
        elif output < -self.saturation:
            output = - self.saturation
            self.in_saturation = True
        else:
            self.in_saturation = False
        return output
    
    def reset(self):
        self.prev_error = 0

#-------------------------------
#-------------------------------
#-------------------------------

class Polar2DController:

    def __init__(self, KP_linear, v_max, KP_heading, w_max):
        self.linear  = PIDSat(KP_linear, 0, 0, v_max)
        self.angular = PIDSat(KP_heading, 0, 0, w_max)
        self.heading_error = 0

    def evaluate(self, delta_t, xt, yt, current_pose):
        (x, y, theta) = current_pose

        dx = xt - x
        dy = yt - y

        target_heading = math.atan2(dy , dx)
        distance = math.sqrt(dx*dx + dy*dy)
        heading_error = normalizeAngle(target_heading - theta)

        if (heading_error > math.pi/2)or(heading_error < -math.pi/2):
            distance = -distance
            heading_error = normalizeAngle(heading_error + math.pi)

        self.heading_error = heading_error
        v_target = self.linear.evaluateError(delta_t, distance)
        w_target = self.angular.evaluateError(delta_t, heading_error)
        return (v_target, w_target)

    def reset(self):
        self.linear.reset()
        self.angular.reset()
        self.heading_error = 0

#-------------------------------
#-------------------------------
#-------------------------------

class StraightLine2DMotion:

    def __init__(self, _vmax, _acc, _dec):
        self.vmax = _vmax
        self.accel = _acc
        self.decel = _dec

    def startMotion(self, start, end):
        
        (self.xs,self.ys) = start
        (self.xe,self.ye) = end

        dx = self.xe - self.xs
        dy = self.ye - self.ys

        self.heading = math.atan2(dy , dx)
        self.distance = math.sqrt(dx*dx + dy*dy)

        self.virtual_robot = VirtualRobot(self.distance, self.vmax, self.accel, self.decel)

    def evaluate(self, delta_t):
        self.virtual_robot.evaluate(delta_t)

        xt = self.xs + self.virtual_robot.p * math.cos(self.heading)
        yt = self.ys + self.virtual_robot.p * math.sin(self.heading)

        return (xt, yt)
    