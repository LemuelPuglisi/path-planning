import sys

from PyQt5.QtWidgets import QApplication
from pathplanning.core.algorithms.fixed_cell_decomposition import FixedCellDecomposition
from pathplanning.core.algorithms.voronoi_diagrams_solver import VoronoiDiagramSolver
from pathplanning.gui.main_window import MainWindow
from pathplanning.gui.darktheme import set_dark_theme

from pathplanning.core.base import SimPoint
from pathplanning.core.cinematics.cart import Cart
from pathplanning.core.dynamics import TwoStepCartRobot
from pathplanning.core.env import Environment


def run_application():
    
    target = SimPoint(0, 0)
    cart = Cart(SimPoint(0, 0))
    twoStep = TwoStepCartRobot(cart, 1e-5, 1e-2)
    env = Environment(cart, target)
    # algo = FixedCellDecomposition()
    algo = VoronoiDiagramSolver()
    
    # run the application
    app = QApplication(sys.argv)
    set_dark_theme(app)
    window = MainWindow(env, twoStep, algo)
    window.show()
    app.exec()
    
if __name__ == '__main__': run_application()