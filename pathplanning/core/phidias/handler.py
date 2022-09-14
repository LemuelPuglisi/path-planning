from typing import Callable

from pathplanning.core.const import PHIDIAS_HANDLER_PORT
from pathplanning.core.dynamics.two_step import TwoStepCartRobot
from pathplanning.core.env import PHIDIASEnvironment
from pathplanning.core.patterns.observer import Observer
from pathplanning.core.phidias.protocol import start_message_server_http, Messaging
from pathplanning.core.base import SimPoint


class PHIDIASHandler(Observer):
    
    def __init__(self, system: TwoStepCartRobot, env: PHIDIASEnvironment):
        self.env = env
        self.system = system
        self.system.subscribe(self, 'end')
        self.phidias_agent = None
        start_message_server_http(self)
        
    def notifyItem(self, item: SimPoint) -> None:
        self.sendBelief('item', [item.x, item.y])

    def notify(self, topic: str, data: dict = None):
        if topic == 'end' and 'target' in data:
            item = data['target']
            self.env.removeItem(item)
            self.sendBelief('item_picked', [ item.x, item.y ])

    def sendBelief(self, belief: str, terms: list) -> None:
        assert self.phidias_agent is not None, "Agent uninitialized."
        Messaging.send_belief(self.phidias_agent, belief, terms, 'robot')
        
    def on_belief(self, _from, name, terms):
        self.phidias_agent = _from
        if name == 'connected': print('agent handler connected.')            
        if name == 'goto':
            coords = SimPoint(terms[0], terms[1])
            self.system.reset()
            self.system.setup([ coords ])
