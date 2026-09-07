cmake_minimum_required(VERSION 3.0.2)
project(prms_sim)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  nav_msgs
  rospy
  tf2_ros
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/simulated_localization_node.py
  scripts/cmd_vel_odom_simulator.py
  scripts/simple_path_follower.py
  scripts/route_smoke_validator.py
  scripts/map_smoke_validator.py
  scripts/closed_loop_nav_validator.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
