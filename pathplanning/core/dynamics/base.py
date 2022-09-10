from abc import ABC, abstractmethod


class RoboticSystem(ABC):

    def __init__(self, delta_t):
        self.delta_t = delta_t
        self.t = 0

    def step(self):
        v = self.run()
        self.t = self.t + self.delta_t
        return v

    def reset(self):
        self.t = 0

    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def getPose(self):
        pass
    
    @abstractmethod
    def getSpeed(self):
        pass    