cmake_minimum_required(VERSION 3.0.2)
project(prms_fusion)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  prms_msgs
  rospy
  tf2_ros
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/maturity_fusion_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

