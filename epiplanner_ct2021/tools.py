from PyQt5 import uic, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget
import subprocess
import time
import numpy as np
import roslibpy
from twisted.internet.error import ReactorNotRunning

toolsFile = 'UI/toolsPane.ui'
formTools, baseTools = uic.loadUiType(toolsFile)

rosFile = 'UI/rosPane.ui'
formRos, baseRos = uic.loadUiType(rosFile)

class RosWidget(baseRos, formRos):
  def __init__(self, toolWid):
    super(baseRos,self).__init__()
    self.setupUi(self)
    self.toolWid = toolWid    
    self._ros = roslibpy.Ros(host='127.0.0.1', port=9090)
    self.setup()
    
  def setup(self):
    self.btStartROS.clicked.connect(self.on_clickStartROS)
    self.btStopROS.clicked.connect(self.on_clickStopROS)              

  @QtCore.pyqtSlot()    
  def on_clickStartROS(self):
    self._ros.run()
    print('Is ROS connected?', self._ros.is_connected)
      
  @QtCore.pyqtSlot()    
  def on_clickStopROS(self):
    try:
      print("Terminating connection...")
      self._ros.terminate()
    except ReactorNotRunning:
      print("ROS connection already dropped?")

  
class ToolsWidget(baseTools, formTools):
  def __init__(self, epiApp, *args, **kwargs):
    super(baseTools,self).__init__(*args, **kwargs)
    self.epiApp = epiApp
    self._rosw = RosWidget(self)        
    tabWidget = QTabWidget(self)    
    tabWidget.addTab(self._rosw,"ROS")        

    layout = QVBoxLayout()
    layout.addWidget(tabWidget)
    self.setLayout(layout)
    

 

    
    


