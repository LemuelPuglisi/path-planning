
from abc import ABC, abstractmethod
from typing import Optional


class Observer(ABC):

    @abstractmethod
    def notify(self, topic: str, data: Optional[dict] = None):
        pass
    

class Observable:
    
    def __init__(self):
        self.topics = {}
        
    def subscribe(self, obs: Observer, topic: str):
        if topic not in self.topics:
            self.topics[topic] = [ obs ]
        else:
            self.topics[topic].append(obs)
    
    def notifyObservers(self, topic: str, data: Optional[dict] = None):
        if topic not in self.topics: return 
        for obs in self.topics[topic]:
            obs.notify(topic, data)
