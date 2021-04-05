from PyQt5 import uic
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QHBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import os
import re

vtkFile = 'UI/vtkPane.ui'
formVtk, baseVtk = uic.loadUiType(vtkFile)


class SceneWidget(baseVtk, formVtk):

  def __init__(self, epiApp, *args, **kwargs):
    super(baseVtk, self).__init__(*args, **kwargs)
    self.epiApp = epiApp
    self._pickw = "virtual"    
    self.setup()      

  def setup(self):
    self.interactor = QVTKRenderWindowInteractor(self)
    
    self.layout = QHBoxLayout()
    self.layout.addWidget(self.interactor)
    self.layout.setContentsMargins(0,0,0,0)
    self.setLayout(self.layout)
   
  def initialize(self):
    self.interactor.Initialize()
    self.interactor.Start()

    self._prepare_data()
    self.interactor.AddObserver(vtk.vtkCommand.KeyPressEvent, self.process_key)    

  def onPoseChanged(self, mid, transform):
    self.epiApp._t[mid] = transform   
    
     
  def _create_electrodes(self, fname):
    pass
    
  def add_marker(self, name):
    actor, source, tpd = create_marker()
    self._tpd = tpd    
    self.renderer.AddActor(actor)
    self.epiApp.dm.addObject(name,{"actor":actor, "source":source, "filter":tpd})

  def _prepare_data(self):
    # Setup VTK environment
    renderer = vtk.vtkRenderer()
    self.renderer = renderer
    self.render_window = self.interactor.GetRenderWindow()
    self.render_window.AddRenderer(renderer)

    self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    self.render_window.SetInteractor(self.interactor)
    renderer.SetBackground(0.2,0.2,0.2)

    oid, tpd_skull, stl_actor = self.create_default_scene()
    
    ref_actor = create_ref()                
    #renderer.AddActor(actorC); 
    #self._actors["Cube"] = actorC
    self.add_marker("mkStylus")
    
    self.renderer.ResetCamera()
    
    # Register pick listener
    self.b0 = stl_actor
    self.picker = vtk.vtkCellPicker()
    self.picker.AddObserver("EndPickEvent", self.process_pick)
    self.interactor.SetPicker(self.picker)

      
  def process_key(self, obj, event):
    print("Press (V)irtual or (L)andmark for point selection")
    #print("Event",event)
    key = obj.GetKeyCode()
    if key == "v":
      self._pickw = "virtual"        
    elif key == "l":
      self._pickw = "real"        
    print("Now picking", self._pickw, "points")
  
  def _getPickedAsSphere(self, pos, color=(1,0,0)):
    # create source
    source = vtk.vtkSphereSource()
    source.SetCenter(pos[0],pos[1],pos[2])
    source.SetRadius(0.01)
     
    # mapper
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(source.GetOutput())
    else:
        mapper.SetInputConnection(source.GetOutputPort())
     
    # actor
    actor = vtk.vtkActor()
    actor.GetProperty().SetColor(*color) #RGB
    actor.SetMapper(mapper)      
    return actor
  
  def process_pick(self, obj, event):
    #print("Event",event)
    point_id = obj.GetPointId()
    #print(obj.GetPickPosition())
    #print(point_id)
    if point_id >= 0:
      pos = obj.GetPickPosition()
      #print(pos)
      self.epiApp.tools._tw.onAddSelectedPoint(self._pickw, pos)

      if self._pickw == "virtual":
        col = (1,0,0)
      if self._pickw == "real":
        col = (0,0,1)              
      actor = self._getPickedAsSphere(pos, col)

      self.renderer.AddActor(actor)

  def pick_landmark(self, obj, event):
    print("Event pick pick_landmark",event)
    x, y = obj.GetEventPosition()
    self.picker.Pick(x,y,0, self.renderer)

  def create_default_scene(self):
    tpd_stl, stl_actor = load_default_scene()
    objId = self.epiApp.dm.addObject("skull", {"tpd":tpd_stl, "actor":stl_actor})
    return objId, tpd_stl, stl_actor
  
  def addActor(self, actor):
    self.renderer.AddActor(actor)
    self.interactor.Render()        
    
  def removeActor(self, actor):
    self.renderer.RemoveActor(actor)
    self.interactor.Render()    
    
def load_default_scene():
  basedir = "data"
  filename = os.path.join(basedir, "skull2.stl")        
  tpd, actor = loadSTL(filename, translate=[0,0,0], scale=[10,10,10])

  return tpd, actor
    
    
def create_marker():
  source_t = vtk.vtkCylinderSource()
  source_t.SetResolution(60)
  source_t.SetCenter(0, 0, 0)
  source_t.SetRadius(0.15)
  source_t.SetHeight(7.0)                
  matrix = vtk.vtkMatrix4x4()
  transform = vtk.vtkTransform()
  transform.Translate([0,0,0])
  transform.Concatenate(matrix)
  tpd = vtk.vtkTransformPolyDataFilter()
  tpd.SetTransform(transform)

  if vtk.VTK_MAJOR_VERSION <= 5:
      tpd.SetInput(source_t.GetOutput())
  else:
      tpd.SetInputConnection(source_t.GetOutputPort())
  # mapper
  mapper_t = vtk.vtkPolyDataMapper()
  if vtk.VTK_MAJOR_VERSION <= 5:
      mapper_t.SetInput(tpd.GetOutput())
  else:
      mapper_t.SetInputConnection(tpd.GetOutputPort())
  
  # actor
  actor_t = vtk.vtkActor()
  actor_t.GetProperty().SetColor(0,1,0) # RGB
  actor_t.SetScale([.1,.1,.1])
  actor_t.SetMapper(mapper_t)
  return actor_t, source_t, tpd
  
  
def create_ref():
  cube = vtk.vtkCubeSource()
  cube.SetXLength(0.005)
  cube.SetYLength(2)
  cube.SetZLength(2)
  cube.SetCenter(0,0,0)
  
  mapper1 = vtk.vtkPolyDataMapper()
  if vtk.VTK_MAJOR_VERSION <= 5:
    mapper1.SetInput(cube.GetOutput())
  else:
    mapper1.SetInputConnection(cube.GetOutputPort())
      
  actorC = vtk.vtkActor()
  actorC.SetMapper(mapper1)
  actorC.GetProperty().SetColor(0, 0.2, 1)
  actorC.GetProperty().SetOpacity(0.2)    
  return actorC

def loadVolume(fname):
  #reader = 
  t = vtk.vtkTransform()
  tpd =  vtk.vtkTransformPolyDataFilter()
  tpd.SetTransform(t)
  #tpd.SetInputConnection(reader.GetOutputPort())
  actor = vtk.vtkActor()
  return tpd, actor
  
def loadSTL(fname, translate=[0,0,0], scale=[1,1,1]):
  reader = vtk.vtkSTLReader()
  reader.SetFileName(fname)
  matrix = vtk.vtkMatrix4x4()
  transform = vtk.vtkTransform()
  transform.Translate(translate)
  transform.Scale(scale)
  transform.Concatenate(matrix)
  tpd = vtk.vtkTransformPolyDataFilter()
  tpd.SetTransform(transform)
  print(transform)

  #if vtk.VTK_MAJOR_VERSION <= 5:
  #    tpd_stl.SetInput(reader.GetOutput())
  #else:
  tpd.SetInputConnection(reader.GetOutputPort())
   
  mapper = vtk.vtkPolyDataMapper()
  #if vtk.VTK_MAJOR_VERSION <= 5:
  #  mapper.SetInput(tpd_stl.GetOutput())
  #else:
  mapper.SetInputConnection(tpd.GetOutputPort())
   
  actor = vtk.vtkActor()
  actor.SetMapper(mapper)
  
  return tpd, actor

def create_tube(a, b, radius, color):
  colors = vtk.vtkNamedColors()

  # Change Color Name to Use your own Color for Actor
  ActorColor=colors.GetColor3d("Red");

  # Create a line
  lineSource = vtk.vtkLineSource();
  lineSource.SetPoint1(*a);
  lineSource.SetPoint2(*b);

  # Setup actor and mapper
  lineMapper = vtk.vtkPolyDataMapper()
  lineMapper.SetInputConnection(lineSource.GetOutputPort())

  lineActor = vtk.vtkActor()
  lineActor.SetMapper(lineMapper)
  lineActor.GetProperty().SetColor(ActorColor)

  # Create tube filter
  tubeFilter=vtk.vtkTubeFilter()
  tubeFilter.SetInputConnection(lineSource.GetOutputPort())
  tubeFilter.SetRadius(radius)
  tubeFilter.SetNumberOfSides(50)
  tubeFilter.Update()

  # Setup actor and mapper
  tubeMapper = vtk.vtkPolyDataMapper()
  tubeMapper.SetInputConnection(tubeFilter.GetOutputPort())

  tubeActor= vtk.vtkActor()
  tubeActor.SetMapper(tubeMapper)
  # Make the tube have some transparency.
  tubeActor.GetProperty().SetOpacity(1.0)
  return tubeActor


def loadElectrodes(fname):
  els = []
  with open(fname, "r") as fp:
    header = fp.readline()
    if not header.startswith("Electrode File version 1"):
      print("File format is not correct", header)
      return []
    frex = " [-+]?\d*\.\d+|\d+"
    for l in fp:
      _n, _ent, _tar, _col, _sec, _ = l.split("|")
      _ent = map(float, re.findall(frex,_ent))
      _tar = map(float, re.findall(frex,_tar))
      _col = map(float, re.findall(frex,_col))
      _sec = float(_sec.split(":")[1])
      actor = create_tube(_ent, _tar, _sec, _col)
      els.append({
        "name": _n, "entryPoint": _ent, "targetPoint": _tar, "color": _col,"radius":_sec,
        "actor": actor
      })
  return els

