cmake_minimum_required(VERSION 3.0.2)
project(prms_perception_bridge)

find_package(catkin REQUIRED COMPONENTS
  prms_msgs
  rospy
  std_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/prms_csv_bridge.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

