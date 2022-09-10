from abc import ABC, abstractmethod
from typing import List
from PyQt5.QtGui import QPainter

from pathplanning.core.env import Environment
from pathplanning.core.base import SimPoint

class PathPlanningBase(ABC):
    
    @abstractmethod
    def draw(self, qp: QPainter) -> None:
        pass
    
    @abstractmethod
    def run(self, env: Environment) -> None:
        pass
    
    @abstractmethod
    def reset(self) -> None:
        pass
    
    @abstractmethod
    def path(self) -> List[SimPoint]:
        pass        