from typing import Callable, Optional

from pathplanning.core.const import PHIDIAS_HANDLER_PORT
from pathplanning.core.dynamics.two_step import TwoStepCartRobot
from pathplanning.core.env import PHIDIASEnvironment
from pathplanning.core.geometry.utils import pointsMatch
from pathplanning.core.patterns.observer import Observable, Observer
from pathplanning.core.phidias.protocol import start_message_server_http, Messaging
from pathplanning.core.base import SimPoint


class PHIDIASHandler(Observer):
    
    def __init__(self, system: TwoStepCartRobot, env: PHIDIASEnvironment):
        self.env = env
        self.system = system
        self.system.subscribe(self, 'path-end')
        self.phidias_agent = None
        self.connectionCb = None
        start_message_server_http(self, port=PHIDIAS_HANDLER_PORT)
        
    def notifyItem(self, item: SimPoint) -> None:
        self.sendBelief('item', [item.x, item.y])


    def notify(self, topic: str, data: Optional[dict] = None):
        if topic == 'path-end' and data is not None and 'endpoint' in data:
            point = data['endpoint']
            if pointsMatch(point, self.env.container_pos):
                item = self.env.cart.releaseItem()
                self.sendBelief('item_released', [ ])
            else:
                self.env.removeItem(point)
                self.env.cart.pickItem(point)
                self.sendBelief('item_picked', [ point.x, point.y ])
            
            
    def sendBelief(self, belief: str, terms: list) -> None:
        assert self.phidias_agent is not None, "Agent uninitialized."
        Messaging.send_belief(self.phidias_agent, belief, terms, 'robot')
        

    def on_belief(self, _from, name, terms):
        self.phidias_agent = _from
        
        if name == 'connected' and self.connectionCb is not None:
            self.connectionCb() 
            self.sendBelief('container', [ *self.env.container_pos() ])
            
        if name == 'goto':
            coords = SimPoint(terms[0], terms[1])
            self.system.setup([ coords ])


    def setConnectionCb(self, fun: Callable):
        self.connectionCb = fun