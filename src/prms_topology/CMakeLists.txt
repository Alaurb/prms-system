cmake_minimum_required(VERSION 3.0.2)
project(prms_topology)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  nav_msgs
  rospy
  std_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/topology_path_publisher.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

