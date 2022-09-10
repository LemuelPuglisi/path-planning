import numpy as np
import networkx as nx

from typing import List
from PyQt5.QtGui import QPainter, QColor

from pathplanning.core.algorithms.base import PathPlanningBase
from pathplanning.core.base import DrawPoint, SimPoint
from pathplanning.core.env import Environment
from pathplanning.core.const import PANEL_H, PANEL_W
from pathplanning.core.geometry import segmentsIntersects


class VoronoiDiagramSolver(PathPlanningBase):
    
    CELL_H = 50
    CELL_W = 50

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.distances_matrix = None
        self.drawable_path = []
        self.peaks = []
        self._path = []
        self.graph = None


    def run(self, env: Environment) -> None:
        self.reset()
        self.source_cell_indices = self._simPointToIndices(env.cart.pos)
        self.target_cell_indices = self._simPointToIndices(env.target)
        self._computeDistanceMatrix(env)
        self._detectPeaks()
        self._computeShortestPath(env.obstacles)
        self._path = [ p.toSimPoint() for p in self.drawable_path ]
        self._path.append(env.target)



    def path(self) -> List[SimPoint]:
        return self._path
    

    def _simPointToIndices(self, simpoint: SimPoint):
        drawpoint = simpoint.toDrawPoint()
        j = int(drawpoint.x // 50)
        i = int(drawpoint.y // 50)
        return (i, j)


    def _computeDistanceMatrix(self, env: Environment) -> None:
        obstacles = env.obstacles
        rows = PANEL_H // self.CELL_H
        cols = PANEL_W // self.CELL_W
        self.distances_matrix = np.full((rows, cols), 10)   
        # This can be greatly optimized by introducing the 
        # `_closestMarginPoint` function, so it's in the todo 
        # list after shipping the project (I'm rushing). 
        drawable_obstacles = [ o.toDrawPoint() for o in obstacles ]
        external_objects = drawable_obstacles + self._getMarginCells()
        for i in range(rows):
            for j in range(cols):
                current_point = self._indicesToPoint(i, j)                
                distances = [ self._computeDistance(current_point, o) for o in external_objects ]
                self.distances_matrix[i, j] = min(distances)
                
                
    def _indicesToPoint(self, i, j) -> DrawPoint:
        return DrawPoint(self.CELL_W * j, self.CELL_H * i) \
                .translate(self.CELL_W // 2, self.CELL_H // 2)


    def _computeDistance(self, a: DrawPoint, b: DrawPoint) -> float:
        return np.sqrt( (a.x - b.x) ** 2 + (a.y - b.y) ** 2 )
    
    
    def _getMarginCells(self) -> List[DrawPoint]:
        margin_blocks = []
        rows = int(PANEL_H // self.CELL_H)
        cols = int(PANEL_W // self.CELL_W)        
        coordv = lambda i: (i * self.CELL_H) + (self.CELL_H // 2) 
        coordh = lambda j: (j * self.CELL_H) + (self.CELL_H // 2)
        margin_blocks += [ DrawPoint(coordh(i), 0) for i in range(rows) ]       # adding the top wall blocks 
        margin_blocks += [ DrawPoint(coordh(i), PANEL_H) for i in range(rows) ] # adding the bottom wall blocks
        margin_blocks += [ DrawPoint(0, coordv(j)) for j in range(cols) ]       # adding the left wall blocks
        margin_blocks += [ DrawPoint(PANEL_W, coordv(j)) for j in range(cols) ] # adding the left wall blocks
        return margin_blocks
    
    
    def _detectPeaks(self) -> None:
        rows, cols = self.distances_matrix.shape
        bigger_cells_matrix = np.full((rows+2, cols+2), 0)
        bigger_cells_matrix[ 1:(rows+1), 1:(cols+1)] = self.distances_matrix
        self.peaks = []
        for si in range(1, rows + 1):
            for sj in range(1, cols + 1):
                square = bigger_cells_matrix[ (si-1):(si+2), (sj-1):(sj+2) ]            
                argmax_i, argmax_j = np.unravel_index(square.argmax(), square.shape)
                if argmax_i == 1 and argmax_j == 1: 
                    real_i = si - 1
                    real_j = sj - 1
                    self.peaks.append((real_i, real_j))
                    
                    
    def _computeShortestPath(self, obstacles: List[SimPoint]) -> List[DrawPoint]:
        assert len(self.peaks) > 0
        node_name = lambda pt : f'{pt.x}-{pt.y}'
        
        points = [ self.source_cell_indices, self.target_cell_indices ] + self.peaks
        points = [ self._indicesToPoint(i, j) for (i, j) in points ]
        
        _obstacles = [ o.toDrawPoint() for o in obstacles ]
        src_name = node_name(points[0])
        tar_name = node_name(points[1])
        graph = nx.Graph()
                
        for point in points:
            graph.add_node(node_name(point), obj=point)
        
        for v, vdata in graph.nodes.items():
            for u, udata in graph.nodes.items():
                if v == u or (v in [src_name, tar_name] and u in [src_name, tar_name]): continue
                vp = vdata['obj']
                up = udata['obj']
                can_connect = True
                
                # do not connect vertices if their segment
                # intersects with an obstacle. 
                # NB. The translation is a little bit modified
                # to make the obstacles larger.
                enlargement = 20
                for o in _obstacles:
                    TL = o.translate(-enlargement, -enlargement)            
                    TR = o.translate(50 + enlargement, -enlargement)
                    BL = o.translate(-enlargement, 50 + enlargement)
                    BR = o.translate(50 + enlargement, 50 + enlargement)
                    
                    if  (segmentsIntersects(vp, up, TL, TR)) or \
                        (segmentsIntersects(vp, up, TL, BL)) or \
                        (segmentsIntersects(vp, up, BL, BR)) or \
                        (segmentsIntersects(vp, up, TR, BR)):
                        can_connect = False
                        break
                    
                if can_connect:
                    edge_weight = self._computeDistance(vdata.get('obj'), udata.get('obj'))
                    graph.add_edge(u, v, weight=edge_weight)

        _, path = nx.single_source_dijkstra(graph, src_name, tar_name)
        points_path = [ graph.nodes[v].get('obj') for v in path ]
        self.drawable_path = points_path[1:] 
        self.graph = graph
        
        
    def draw(self, qp: QPainter) -> None:
        if self.distances_matrix is None: return
        min_distance = self.distances_matrix.min()
        max_distance = self.distances_matrix.max()
        rows, cols = self.distances_matrix.shape
        qp.setPen(QColor('gray'));
        for i in range(rows):
            for j in range(cols):
                curr_distance = self.distances_matrix[i, j] 
                mapped_green = 50 + (((curr_distance - min_distance) * 70) / ( max_distance - min_distance ))
                color = QColor(QColor(0, mapped_green, 0))
                qp.setBrush(color); 
                qp.drawRect(50 * j, 50 * i, 50, 50)
                qp.setPen(QColor('gray'));
                qp.drawText(50*j+5, 50*i+15, str(self.distances_matrix[i, j]))
    
        vertices = [self.source_cell_indices, self.target_cell_indices] + self.peaks
        for (i, j) in vertices:
            qp.setBrush(QColor('#db2b39')); 
            qp.setPen(QColor('#db2b39'))
            qp.drawEllipse(50 * j + 20, 50 * i + 20, 10, 10)
            
        for u, v in self.graph.edges():
            upoint = self.graph.nodes[u]['obj']
            vpoint = self.graph.nodes[v]['obj']
            qp.drawLine(upoint.x, upoint.y, vpoint.x, vpoint.y)