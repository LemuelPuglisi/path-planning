from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem


class PHIDIASSideBarWidget(QWidget):
    
    PHIDIAS_INSTR = """
    Start a PHIDIAS client using
    the following command in another shell: 
    
    path-planning-strategy
    
    Then submit `connect()` procedure.
    Add items using the button above, and
    let the robot pick them up using the 
    `pick()` procedure.
    """
    
    def __init__(self):
        super().__init__()
        self.instructions_label = QLabel('Please connect a PHIDIAS client.')
        self.phidias_instruction_label = QLabel(self.PHIDIAS_INSTR)
        self.starting_point_button = QPushButton('set starting point')
        self.set_container_button = QPushButton('set container')
        self.add_item_button = QPushButton('add item')
        self.initUI()
        self.initEventHandling()

    def initUI(self):                
        self.instructions_label.setStyleSheet('border: 1px solid white; padding: 5px;')
        self.phidias_instruction_label.setStyleSheet('border: 1px solid white; padding: 5px;')
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.addWidget(self.starting_point_button)
        self.sidebar_layout.addWidget(self.set_container_button)
        self.sidebar_layout.addWidget(self.add_item_button)
        self.sidebar_layout.addWidget(self.instructions_label)
        self.sidebar_layout.addWidget(self.phidias_instruction_label)
        self.sidebar_layout.setContentsMargins(5, 50, 10, 50)
        self.setLayout(self.sidebar_layout)
        
    def initEventHandling(self):
        self.starting_point_button.clicked.connect(self.handleStartingPointClick)
        self.set_container_button.clicked.connect(self.handleSetContainerClick)
        self.add_item_button.clicked.connect(self.handleAddItemClick)


    def handleStartingPointClick(self):
        self.instruct('Click to select the starting point.')
        self.blockButtons()   

    def handleSetContainerClick(self):
        self.instruct('Click to set the container position.')
        self.blockButtons()           

    def handleAddItemClick(self):
        self.instruct('Click to add an object.')
        self.blockButtons()           

    def instruct(self, message):
        self.instructions_label.setText(message)
                
    def _getClassButtons(self):
        return [ getattr(self, name) for name, _class in vars(self).items() if 'QPushButton' in str(_class) ]         
        
    def blockButtons(self):
        for btn in self._getClassButtons():
            btn.setDisabled(True)
                
    def releaseButtons(self):
        self.instruct('Path planning instructions.')
        for btn in self._getClassButtons():
            btn.setDisabled(False)
        