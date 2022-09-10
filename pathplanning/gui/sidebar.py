from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem


class SideBarWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        self.starting_point_button = QPushButton('set starting point')
        self.target_point_button   = QPushButton('set destination')
        self.add_obstacle_button   = QPushButton('add obstacle')
        self.select_algorithm_list = QListWidget()
        self.start_simulation_button = QPushButton('Start simulation')
        self.reset_simulation_button = QPushButton('Reset simulation')
        self.instructions_label = QLabel('Path planning instructions.')
        self.initUI()
        self.initEventHandling()

    def initUI(self):
        
        self.FCD_item = QListWidgetItem("Fixed Cell decomposition")
        self.VDS_item = QListWidgetItem("Voronoi Diagram Solver")
        self.select_algorithm_list.addItem(self.FCD_item)
        self.select_algorithm_list.addItem(self.VDS_item)
        
        self.instructions_label.setStyleSheet('border: 1px solid white; padding: 5px;')
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.addWidget(self.instructions_label)
        self.sidebar_layout.addWidget(self.starting_point_button)
        self.sidebar_layout.addWidget(self.target_point_button)
        self.sidebar_layout.addWidget(self.add_obstacle_button)
        self.sidebar_layout.addWidget(self.select_algorithm_list)
        self.sidebar_layout.addWidget(self.start_simulation_button)
        self.sidebar_layout.addWidget(self.reset_simulation_button)
        self.sidebar_layout.setContentsMargins(5, 50, 10, 50)
        self.setLayout(self.sidebar_layout)
        
    def initEventHandling(self):
        self.starting_point_button.clicked.connect(self.handleStartingPointClick)
        self.target_point_button.clicked.connect(self.handleTargetPointClick)
        self.add_obstacle_button.clicked.connect(self.handleAddObstacleClick)
        
    def instruct(self, message):
        self.instructions_label.setText(message)
        
    def handleStartingPointClick(self):
        self.instruct('Click to select the starting point.')
        self.blockButtons()     
        
    def handleTargetPointClick(self):
        self.instruct('Click to select the target point.')
        self.blockButtons()     
        
    def handleAddObstacleClick(self):
        self.instruct('Click to add an obstacle.')
        self.blockButtons()             
        
    def _getClassButtons(self):
        return [ getattr(self, name) for name, _class in vars(self).items() if 'QPushButton' in str(_class) ]         
        
    def blockButtons(self):
        for btn in self._getClassButtons():
            btn.setDisabled(True)
                
    def releaseButtons(self):
        self.instruct('Path planning instructions.')
        for btn in self._getClassButtons():
            btn.setDisabled(False)
        