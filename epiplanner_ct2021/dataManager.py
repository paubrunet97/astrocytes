from PyQt5 import uic, QtCore
from PyQt5.QtCore import QDir
from PyQt5.QtGui import  QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from collections import deque
from uuid import uuid4
import vtk
import os
import json
from scene import loadVolume, loadSTL, loadElectrodes
from lxml import etree
import SimpleITK as sitk

dmFile = 'UI/dataManagerPane.ui'
formDM, baseDM = uic.loadUiType(dmFile)


class TreeItem():
  def __init__(self, name, data, parentId):
    self.uid = str(uuid4())
    self.data = data
    self.parentId = parentId
    self.name = name

  def hasActor(self):
    return "actor" in self.data
    
  def getActor(self):
    return self.data["actor"]
      
  def __repr__(self):
    return "ID:%s, PID:%s, NAME:%s"%(self.uid, self.parentId, self.name)


class DMWidget(baseDM, formDM):
  def __init__(self, epiApp):
    super(baseDM,self).__init__()
    self.setupUi(self)
    self.epiApp = epiApp
    self.scene = {
      "objects": [],
      "actors": {}
    }    
    
    self.model = QStandardItemModel()
    self.model.setHorizontalHeaderLabels(['Name', 'objID'])
    self.treeView.header().setDefaultSectionSize(180)
    self.treeView.setModel(self.model)
    self.clearScene()
    self.setup()

  def setup(self):
    self.btClearScene.clicked.connect(self.onClearSceneClicked)
    self.btDebugScene.clicked.connect(self.onDebugSceneClicked)  
    self.btLoadCase.clicked.connect(self.onLoadCaseClicked)
    
  def addObject(self, name, data, parentID=None):
    if parentID == None:
      pObj = self.scene["objects"][0] #Root is the parent
    else:
      pObj = [i for i in self.scene["objects"] if i.uid == parentID][0]
      
    parent = pObj.data["node"]
    pid = pObj.uid      
    tim = TreeItem(name, data, pid)
    node = QStandardItem(name)
    parent.appendRow([
          node,
          QStandardItem(tim.uid),
          ])
    tim.data["node"] = node
    self.scene["objects"].append(tim)

    self.epiApp.scene.addActor(data["actor"])

    return tim.uid

  @QtCore.pyqtSlot()    
  def onLoadCaseClicked(self):
    dlg = QFileDialog()
    dlg.setFileMode(QFileDialog.DirectoryOnly)
    dlg.setFilter(dlg.filter() | QDir.Hidden)
    dlg.setAcceptMode(QFileDialog.AcceptOpen)    
	
    if dlg.exec_() == QDialog.Accepted:
      path = dlg.selectedFiles()[0]  # returns a list
      print("Loading case from:",path)
      casefile = os.path.join(path, "case.json")
      if not os.path.exists(casefile):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("This directory is not a case")
        msg.setWindowTitle("Case load error")
        msg.setDetailedText(
        "There is no case.json. "+
        "We need this in order to properly identify the head and the electrodes"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()
      else:
        case = None
        with open(casefile, "r") as fp:
          case = json.load(fp)
        if case:
          self.loadCase(path, case)

  def loadCase(self, path, jsCase):
    self.clearScene()
    print(jsCase)
    meta = jsCase["metadata"]
    ref = jsCase["reference"]
    elec = jsCase["electrodes"]        
     
    pid = meta["pid"]
    headVolumeFile = os.path.join(path, ref["vtk"])
    if os.path.isfile(headVolumeFile):
      print("Loading", headVolumeFile)
      reader = sitk.ImageFileReader()
      reader.SetFileName(str(headVolumeFile))
      reader.ReadImageInformation()      
      print("vtk Origin",reader.GetOrigin())

    print(ref["vtkOrigin"])
    print(ref["vtkOrientation"])
    headSTLFile = os.path.join(path, ref["stl"])    
    print("stl Origin", ref["stlOrigin"])
    print(ref["stlOrientation"])
    
    electFile = os.path.join(path, elec["data"])
    xmlFile = os.path.join(path, ref["xmlFile"])
    if (os.path.isfile(xmlFile)):
      tree = etree.parse(xmlFile)
      _slice = tree.findall("//tag[@name='Slice']")[0]  
      print(_slice)
      
    vtkVolume = loadVolume(headVolumeFile)
    headVTpd, headVActor = loadSTL(headSTLFile, translate=ref["stlOrigin"], scale=[1000,1000,1000])
    headVId = self.epiApp.dm.addObject(pid, {"tpd":headVTpd, "actor":headVActor})
    electrodes = loadElectrodes(electFile)
    for _el in electrodes:
      elId = self.epiApp.dm.addObject("%s"%(_el["name"]),
       _el, parentID=headVId)
    self.epiApp.scene.renderer.ResetCamera()


  @QtCore.pyqtSlot()    
  def onClearSceneClicked(self):
    self.clearScene()

  @QtCore.pyqtSlot()    
  def onDebugSceneClicked(self):
    self.debugScene()
    
  def clearScene(self):
  
    for obj in self.scene["objects"]:
      if obj.hasActor():
        self.epiApp.vtk_widget.removeActor(obj.getActor())

    self.scene = {
      "objects": [],
      "actors": {}
    }      
    
    self.model.setRowCount(0)
    
    _root = self.model.invisibleRootItem()    
    rootItem = TreeItem("root", data={"node":_root}, parentId=None)
    self.scene["objects"].append(rootItem)

  def debugScene(self):
    print("Content of the data manager:")
    print("Actors:", self.scene["actors"])
    print("Objects:")
    for obj in self.scene["objects"]:
      print(obj)
    
    print("Content of the qt tree:")
    print(self.model)    
    
    print("Content of vtk renderer:")
    actors = self.epiApp.scene.renderer.GetActors()
    for i in range(actors.GetNumberOfItems()):
      a = actors.GetItemAsObject(i)
      xmin, xMax, ymin, yMax, zmin, zMax = a.GetBounds()
      dX, dY, dZ = xMax-xmin, yMax-ymin, zMax-zmin,
      print("Actor dx %.3f (%.3f, %.3f); dy %.3f (%.3f, %.3f); dz %.3f (%.3f, %.3f);"%(
        dX, xmin, xMax, dY, ymin, yMax, dZ, zmin, zMax)
        )

#      print("Actor:", a)
       


