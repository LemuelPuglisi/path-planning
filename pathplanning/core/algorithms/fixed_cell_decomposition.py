import numpy as np

from typing import List
from PyQt5.QtGui import QPainter, QColor

from pathplanning.core.algorithms.base import PathPlanningBase
from pathplanning.core.base import DrawPoint, SimPoint
from pathplanning.core.env import Environment
from pathplanning.core.const import OBS_H, OBS_W, PANEL_H, PANEL_W


class FixedCellDecomposition(PathPlanningBase):

    CELL_H = 50
    CELL_W = 50
    INFINITY = 5000

    def __init__(self):
        self.reset()


    def reset(self):        
        self._path = []
        self.drawable_path = []
        self.drawable_path_unoptimized = []
        self.cells_matrix = None


    def run(self, env: Environment) -> None:
        self.reset()        
        self.source_cell_indices = self._simPointToIndices(env.cart.pos)
        self.target_cell_indices = self._simPointToIndices(env.target)
        self._computeCellMatrix(env)
        self._computeManhattanDistances()
                
        rows, cols = self.cells_matrix.shape
        bigger_cells_matrix = np.full((rows+2, cols+2), self.INFINITY)
        bigger_cells_matrix[ 1:(rows+1), 1:(cols+1)] = self.cells_matrix    
        si, sj = self.source_cell_indices
        si, sj = si + 1, sj + 1

        path = []
        prev_point = None
        prev_argmin_i, prev_argmin_j = None, None
        max_iter, curr_iter = 300, 0

        while True:              
            # Extract the square where to choose the next move.
            square = bigger_cells_matrix[ (si-1):(si+2), (sj-1):(sj+2) ]            
            square_cp = square.copy()
            
            # Determine the cell with the lowest value.
            argmin_i, argmin_j = np.unravel_index(square_cp.argmin(), square_cp.shape)

            # If the values is zero, the target is reached. 
            if square[argmin_j, argmin_j] == 0: 
                break

            # Otherwise, in order to avoid choosing the 
            # previous position in the next evaluation, 
            # we set the current cell value to INF. 
            bigger_cells_matrix[si, sj] = self.INFINITY
            
            # Update the position according to the 
            # previous decision. 
            si += argmin_i - 1
            sj += argmin_j - 1
            
            # Loop avoidance check. 
            curr_iter += 1
            if curr_iter > max_iter: 
                raise Exception('Target not reachable')

            # Compute the point in the drawable panel from
            # the choosen cell and add it to the (unoptimized)
            # choosen cells list. 
            # curr_point = ( sj * 50 - 25, si * 50 - 25)            
            curr_point = DrawPoint(sj * 50, si * 50)
            curr_point = curr_point.translate(-self.CELL_W // 2, -self.CELL_H // 2)
            self.drawable_path_unoptimized.append(curr_point)        
            
            # If it's the first point determined, then add 
            # it to the list in any case. Otherwise we do not 
            # add this point directly (see comments below)
            if prev_point is None: path.append(curr_point)
            
            # if we are changing direction, then we add the 
            # PREVIOUS point. This is an optimization for the algo. 
            if  prev_argmin_i is not None and (prev_argmin_i != argmin_i or prev_argmin_j != argmin_j):
                path.append(prev_point)
            
            # update parameters. 
            prev_point = curr_point
            prev_argmin_i, prev_argmin_j = argmin_i, argmin_j

        
        self.drawable_path = path
        # return [ paint_to_coords(*c) for c in path ] + [ env.target.toTuple() ]
        self._path = [ point.toSimPoint() for point in self.drawable_path ]
        self._path.append(env.target)


    def path(self) -> List[SimPoint]:
        return self._path
            

    def _computeCellMatrix(self, env: Environment):
        obstacles = env.obstacles
        rows = PANEL_H // self.CELL_H
        cols = PANEL_W // self.CELL_W
        cells_matrix = np.full((rows, cols), 10)   
        for i in range(rows):
            for j in range(cols):
                cell_BL = DrawPoint(50 * j, 50 * (i+1))
                cell_TR = DrawPoint(50 * (j+1), 50 * i)       
                for obs in obstacles:
                    _obs = obs.toDrawPoint().toTopLeft(OBS_W, OBS_H)
                    _obs_BL = _obs.translate(0, OBS_H)
                    _obs_TR = _obs.translate(OBS_W, 0)
                    if self._cellIntersectsObstacle(cell_TR, cell_BL, _obs_TR, _obs_BL):
                        cells_matrix[i, j] = self.INFINITY
                        break
        self.cells_matrix = cells_matrix
    
    
    def _cellIntersectsObstacle(self, cell_TR, cell_BL, obs_TR, obs_BL) -> bool:
        """ Separating axis theorem. """
        return not (
            cell_TR.x < obs_BL.x or 
            cell_BL.x > obs_TR.x or 
            cell_TR.y > obs_BL.y or # y axis checks are flipped
            cell_BL.y < obs_TR.y    # because we consider painting reference.
        )
        
        
    def _computeManhattanDistances(self):
        cells_matrix = self.cells_matrix
        target_row, target_col = self.target_cell_indices
        source_row, source_col = self.source_cell_indices
        manhd = lambda r, c: np.abs(r - target_row) + np.abs(c - target_col)
        source_target_distance = manhd(source_row, source_col)
        rows, cols = cells_matrix.shape
        for row in range(rows):
            for col in range(cols):
                if cells_matrix[row, col] == self.INFINITY: continue
                manhattan = manhd(row, col)
                # little bit of disvantage for cells with higher distance
                cells_matrix[row, col] = manhattan if manhattan <= source_target_distance \
                    else manhattan + source_target_distance
                    
               
    def _simPointToIndices(self, simpoint: SimPoint):
        drawpoint = simpoint.toDrawPoint()
        j = int(drawpoint.x // 50)
        i = int(drawpoint.y // 50)
        return (i, j)
    
    
    def draw(self, qp: QPainter) -> None:
        if self.cells_matrix is None: return
        
        qp.setPen(QColor('white'))
        rows, cols = self.cells_matrix.shape
        for i in range(rows):
            for j in range(cols):
                color = QColor('#d32f2f') if self.cells_matrix[i, j] == self.INFINITY else QColor('transparent')
                qp.setBrush(color); 
                qp.drawRect(50 * j, 50 * i, 50, 50)
                if self.cells_matrix[i, j] != self.INFINITY:
                    qp.setPen(QColor('gray'));
                    qp.drawText(50*j+5, 50*i+15, str(self.cells_matrix[i, j]))
        
        # draw unoptimized path
        qp.setPen(QColor('#ffe882')); qp.setBrush(QColor('#ffe882'))
        for point in self.drawable_path_unoptimized: 
            sphere = point.toTopLeft(10, 10)
            qp.drawEllipse(*sphere(), 10, 10)
        
        # draw optimized path
        qp.setPen(QColor('#FA8334')); qp.setBrush(QColor('#FA8334'))
        for point in self.drawable_path: 
            sphere = point.toTopLeft(12, 12)
            qp.drawEllipse(*sphere(), 12, 12)