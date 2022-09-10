from __future__ import annotations
from PyQt5.QtCore import QPoint

from pathplanning.core.const import PANEL_H, PANEL_W, SCALE


class Point:    
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'({self.x}, {self.y})'

    def __call__(self) -> tuple:
        return (self.x, self.y)

    def translate(self, tx, ty) -> Point:
        _x = self.x + tx
        _y = self.y + ty
        return Point(_x, _y)


class SimPoint(Point):
    
    def toDrawPoint(self):
        _x = (self.x * SCALE)
        _y = PANEL_H - (self.y * SCALE)        
        return DrawPoint(_x, _y)

    def translate(self, tx, ty) -> SimPoint:
        p = super().translate(tx, ty)
        return SimPoint(p.x, p.y)
    
        
class DrawPoint(Point):
    
    def toSimPoint(self):
        _x = self.x / SCALE
        _y = (PANEL_H - self.y) / SCALE
        return SimPoint(_x, _y)
        
    def translate(self, tx, ty) -> DrawPoint:
        p = super().translate(tx, ty)
        return DrawPoint(p.x, p.y)

    def toTopLeft(self, object_width, object_height):
        _x = self.x - (object_width / 2)
        _y = self.y - (object_height / 2)
        return DrawPoint(_x, _y)

    def toQPoint(self):
        return QPoint(self.x, self.y)
