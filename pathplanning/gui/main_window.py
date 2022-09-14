from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from pathplanning.core.algorithms.base import PathPlanningBase
from pathplanning.core.algorithms.fixed_cell_decomposition import FixedCellDecomposition
from pathplanning.core.algorithms.voronoi_diagrams_solver import VoronoiDiagramSolver
from pathplanning.core.base import DrawPoint, SimPoint
from pathplanning.gui.sidebar import SideBarWidget
from pathplanning.gui.drawing_panel import DrawingPanelWidget
from pathplanning.core.env import Environment
from pathplanning.core.dynamics.base import RoboticSystem

class MainWindow(QMainWindow):
    
    def __init__(self, env: Environment, 
                       system: RoboticSystem, 
                       algorithm: PathPlanningBase):
        super(MainWindow, self).__init__()
                
                
        self.setWindowTitle("path-planning")
        self.setFixedSize(QSize(1350, 700))

        self.env = env
        self.system = system
        self.algorithm = algorithm

        self.drawing_panel = DrawingPanelWidget(env, system, algorithm)
        self.sidebar_widget = SideBarWidget()

        # we move the component "wiring" to the
        # upper component. This can be replaced to 
        # some design patterns later. 
        
        self.sidebar_widget.starting_point_button.clicked.connect(self.awaitStartingPoint)
        self.sidebar_widget.target_point_button.clicked.connect(self.awaitTargetPoint)
        self.sidebar_widget.add_obstacle_button.clicked.connect(self.awaitObstacleAdd)
        self.sidebar_widget.select_algorithm_list.itemClicked.connect(self.selectAlgorithm)
        self.sidebar_widget.start_simulation_button.clicked.connect(self.startSimulation)
        self.sidebar_widget.reset_simulation_button.clicked.connect(self.resetSimulation)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.drawing_panel)    
        main_layout.setContentsMargins(25, 0, 25, 0)
        
        main_widget = QWidget()
        main_widget.setAutoFillBackground(True)
        main_widget_palette = main_widget.palette()
        main_widget_palette.setColor(QPalette.Window, QColor('#010409'))
        main_widget.setPalette(main_widget_palette)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
                
    def startSimulation(self):
        self.system.reset()
        self.algorithm.reset()

        try:
            self.algorithm.run(self.env)
            path = self.algorithm.path()
        except Exception as e:
            self.sidebar_widget.instruct('Target is not reachable.')
            self.drawing_panel.update()
            print(str(e))
            return 
        self.system.setup(path) 
        self.drawing_panel.start()
        
    def resetSimulation(self):
        self.system.reset()
        self.env.reset()
        self.algorithm.reset()
        self.drawing_panel.reset()

    def selectAlgorithm(self, item):
        if self.sidebar_widget.VDS_item.isSelected():
            self.algorithm = VoronoiDiagramSolver()            
        if self.sidebar_widget.FCD_item.isSelected():
            self.algorithm = FixedCellDecomposition()
        self.drawing_panel.algorithm = self.algorithm

            
    def awaitStartingPoint(self):
        self.drawing_panel.mousePressEvent = self.handleStartingPoint
        
    def handleStartingPoint(self, event):
        self.drawing_panel.mousePressEvent = lambda e: None
        position = event.pos()
        point = DrawPoint(position.x(), position.y())       
        self.env.moveCartStationary(point.toSimPoint())
        self.sidebar_widget.releaseButtons()
        self.drawing_panel.update()

    def awaitTargetPoint(self):
        self.drawing_panel.mousePressEvent = self.handleTargetPoint
        
    def handleTargetPoint(self, event):
        self.drawing_panel.mousePressEvent = lambda e: None
        position = event.pos()
        point = DrawPoint(position.x(), position.y())       
        self.env.moveTarget(point.toSimPoint())
        self.sidebar_widget.releaseButtons()
        self.drawing_panel.update()
        
    def awaitObstacleAdd(self):
        self.drawing_panel.mousePressEvent = self.handleObstacleAdd
        
    def handleObstacleAdd(self, event):
        self.drawing_panel.mousePressEvent = lambda e: None
        position = event.pos()
        point = DrawPoint(position.x(), position.y())               
        self.env.addObstacle(point.toSimPoint())
        self.sidebar_widget.releaseButtons()
        self.drawing_panel.update()
        
                
        