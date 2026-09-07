#!/usr/bin/env bash
set -eo pipefail

WORKSPACE="${1:-$HOME/prms_ws}"
REPO_ROOT="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TRACE_PATH="${TRACE_PATH:-$REPO_ROOT/outputs/nav_smoke/latest_trace.json}"

export ROS_MASTER_URI=http://127.0.0.1:11311
export ROS_HOSTNAME=127.0.0.1
export ROS_LOG_DIR=/tmp/prms_ros_logs

mkdir -p "$WORKSPACE/src" "$ROS_LOG_DIR" "$(dirname "$TRACE_PATH")"
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
TOPO_PID=""
ODOM_PID=""
FOLLOWER_PID=""

cleanup() {
  if [[ -n "$FOLLOWER_PID" ]]; then kill "$FOLLOWER_PID" 2>/dev/null || true; fi
  if [[ -n "$ODOM_PID" ]]; then kill "$ODOM_PID" 2>/dev/null || true; fi
  if [[ -n "$TOPO_PID" ]]; then kill "$TOPO_PID" 2>/dev/null || true; fi
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

rosrun prms_topology topology_path_publisher.py _rate:=2.0 &
TOPO_PID=$!
rosrun prms_sim cmd_vel_odom_simulator.py _rate:=20.0 _odom_topic:=Odometry _cmd_vel_topic:=cmd_vel &
ODOM_PID=$!
rosrun prms_sim simple_path_follower.py _rate:=10.0 _odom_topic:=Odometry _cmd_vel_topic:=cmd_vel _max_linear_mps:=0.55 _max_angular_rps:=1.2 _goal_tolerance_m:=0.15 &
FOLLOWER_PID=$!
rosrun prms_sim closed_loop_nav_validator.py _timeout_s:=35.0 _goal_tolerance_m:=0.2 _odom_topic:=Odometry _cmd_vel_topic:=cmd_vel "_trace_output:=$TRACE_PATH"
echo "Trace written to: $TRACE_PATH"
