#!/usr/bin/env bash
set -eo pipefail

WORKSPACE="${1:-$HOME/prms_ws}"
REPO_ROOT="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

export ROS_MASTER_URI=http://127.0.0.1:11311
export ROS_HOSTNAME=127.0.0.1
export ROS_LOG_DIR=/tmp/prms_ros_logs

mkdir -p "$WORKSPACE/src" "$ROS_LOG_DIR"
cp -r "$REPO_ROOT/src/prms_bringup" "$WORKSPACE/src/"
cp -r "$REPO_ROOT/src/prms_fusion" "$WORKSPACE/src/"
cp -r "$REPO_ROOT/src/prms_msgs" "$WORKSPACE/src/"
cp -r "$REPO_ROOT/src/prms_perception_bridge" "$WORKSPACE/src/"
cp -r "$REPO_ROOT/src/prms_sim" "$WORKSPACE/src/"
cp -r "$REPO_ROOT/src/prms_topology" "$WORKSPACE/src/"

source /opt/ros/noetic/setup.bash
cd "$WORKSPACE"
catkin_make --only-pkg-with-deps \
  prms_bringup \
  prms_fusion \
  prms_msgs \
  prms_perception_bridge \
  prms_sim \
  prms_topology
source devel/setup.bash

rosmaster --core -p 11311 > /tmp/prms_rosmaster.log 2>&1 &
CORE_PID=$!
MAP_PID=""
TOPO_PID=""
SIM_PID=""

cleanup() {
  if [[ -n "$MAP_PID" ]]; then kill "$MAP_PID" 2>/dev/null || true; fi
  if [[ -n "$TOPO_PID" ]]; then kill "$TOPO_PID" 2>/dev/null || true; fi
  if [[ -n "$SIM_PID" ]]; then kill "$SIM_PID" 2>/dev/null || true; fi
  kill "$CORE_PID" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 40); do
  if rosparam list >/tmp/prms_rosparam_check.log 2>&1; then
    break
  fi
  sleep 0.25
done

rosparam load "$WORKSPACE/src/prms_bringup/config/system.yaml" /
rosparam load "$WORKSPACE/src/prms_bringup/config/topology.yaml" /topology

rosrun map_server map_server "$WORKSPACE/src/prms_bringup/maps/greenhouse_reference.yaml" &
MAP_PID=$!
rosrun prms_topology topology_path_publisher.py _rate:=2.0 &
TOPO_PID=$!
rosrun prms_sim simulated_localization_node.py _rate:=10.0 _speed_mps:=0.8 _odom_topic:=Odometry &
SIM_PID=$!
rosrun prms_sim map_smoke_validator.py _timeout_s:=12.0 _min_distance_m:=0.5 _odom_topic:=Odometry

