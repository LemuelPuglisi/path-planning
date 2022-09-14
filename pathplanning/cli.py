import sys

from PyQt5.QtWidgets import QApplication
from argparse import ArgumentParser

from pathplanning.core.algorithms.voronoi_diagrams_solver import VoronoiDiagramSolver
from pathplanning.gui.main_window import MainWindow
from pathplanning.gui.phidias.main_window import PHIDIASMainWindow
from pathplanning.gui.darktheme import set_dark_theme

from pathplanning.core.base import SimPoint
from pathplanning.core.cinematics.cart import Cart
from pathplanning.core.dynamics import TwoStepCartRobot
from pathplanning.core.env import Environment, PHIDIASEnvironment


def run_application():
    
    parser = ArgumentParser()
    parser.add_argument('--phidias', help='display PHIDIAS version', action='store_true')
    parser.set_defaults(phidias=False)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    set_dark_theme(app)
    
    if not args.phidias:    
        target = SimPoint(0, 0)
        cart = Cart(SimPoint(0, 0))
        two_step = TwoStepCartRobot(cart, 1e-5, 1e-2)
        env = Environment(cart, target)
        algo = VoronoiDiagramSolver()
        main_window = MainWindow(env, two_step, algo)
    else:
        target = SimPoint(.2, .2)
        cart = Cart(SimPoint(0, 0))
        two_step = TwoStepCartRobot(cart, 1e-5, 1e-2)
        env = PHIDIASEnvironment(cart)
        main_window = PHIDIASMainWindow(env, two_step)
        
    main_window.show()
    app.exec()

if __name__ == '__main__': run_application()