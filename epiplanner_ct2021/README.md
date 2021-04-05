Install:

Dependencies
* pyqt5
* python-vtk6

* PlusServer
https://plustoolkit.github.io/usersguide.html

* openigtlink
http://openigtlink.org/users/

* ros_igtl_bridge
https://github.com/openigtlink/ROS-IGTL-Bridge

* simbiorob

 
How to run:
PlusBuild-master/build_sp/bin$ ./PlusServerLauncher
Select NDI Polaris con passive markers

~/catkin_ws$ roslaunch ros_igtl_bridge bridge.launch
$ rostopic list
$ rostopic echo /IGTL_TRANSFORM_IN

$ ~/git/epiplanner$ python main.py

TODO:
Calibrate/check pointer
Register skull
Put reference marker on robot
Add robot type selection
search stl for robots/ or load as cubes
Add joint control
* For owi is integrated in simbiorob
* For mearm we need raspberry
* moveo (ros simulation)
Print direct kinematics



 
