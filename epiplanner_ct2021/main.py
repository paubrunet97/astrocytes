import sys
from PyQt5.QtWidgets import QApplication
from epilepsyPlanner import EpilepsyPlannerApp

if __name__ == "__main__":
    
  app = QApplication(sys.argv)
  main_window = EpilepsyPlannerApp()
  main_window.show()
  main_window.initialize()
  app.exec_()


