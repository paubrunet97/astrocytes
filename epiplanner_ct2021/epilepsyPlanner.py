from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QSplitter

from scene import SceneWidget
from tools import ToolsWidget
from dataManager import DMWidget

#load both ui file
mainWindowFile = 'UI/epiplanner.ui'
formMain, baseMain = uic.loadUiType(mainWindowFile)


class EpilepsyPlannerApp(baseMain, formMain):
  def __init__(self):
    super(baseMain,self).__init__()
    self.setupUi(self)
    self.setWindowTitle("Epiplanner app")
    self.dm = DMWidget(self)
    self.vtk_widget = SceneWidget(self)
    self.scene = self.vtk_widget
    self.tools = ToolsWidget(self)
    
    hbox = QHBoxLayout()    
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(self.dm)
    splitter.addWidget(self.scene)
    splitter.addWidget(self.tools)
    
    hbox.addWidget(splitter)    
    widget = QWidget()
    widget.setLayout(hbox)
    self.setCentralWidget(widget)    

    self._split = splitter

    self.ui = None
    self._sub = None
    self._t = {}
    self.timer = None
    self._robot = None
    self._actors = {}   
    self.setup()    

  def initialize(self):
    self.scene.initialize()
    _wd = self.geometry().width()
    _bwd = _wd/6
    self._split.setSizes((_bwd,_bwd*3,_bwd*2))
    
  def setup(self):    
    pass
    
