# PRMS System

PRMS System is an integrated greenhouse inspection framework for a wheel-legged quadruped robot. It combines LiDAR-based navigation, topological route guidance, panoramic maturity recognition, and spatio-temporal fusion into one reproducible ROS-oriented project.

The first code version is a system scaffold. It is designed to connect two implementation sources:

- Navigation method: FAST-LIO / localization / move_base workflow inspired by `NEXTE_Sentry_Nav`.
- Recognition method: panoramic cube projection, YOLO maturity recognition, and 3D mapping from the existing PRMS repository.

## Repository Layout

```text
prms-system/
  config/                         Runtime parameters and example topology map
  docs/                           Architecture and interface notes
  launch/                         System launch entry points
  scripts/                        Developer helper scripts
  src/
    prms_bringup/                 System-level launch package
    prms_fusion/                  Time alignment and spatial fusion node
    prms_msgs/                    ROS message definitions
    prms_perception_bridge/       Bridge from PRMS detection outputs to ROS
    prms_topology/                Topological route publisher and waypoint guide
```

## Current Scope

This scaffold provides:

- ROS package skeletons for navigation guidance, perception bridging, and fusion.
- A topology route publisher that converts row/waypoint topology into `nav_msgs/Path`.
- A perception bridge interface for publishing PRMS detection results.
- A fusion node skeleton for synchronizing detections with robot poses.
- Example configuration files and launch wiring.

The next implementation step is to place or submodule the navigation and perception repositories under `third_party/`, then bind their topics and outputs to the interfaces defined here.

## Quick Start

```powershell
cd C:\Users\10335\OneDrive\文档\格式修改\prms-system
git init
```

For ROS Noetic on Ubuntu 20.04:

```bash
mkdir -p ~/catkin_ws/src
cp -r prms-system/src/* ~/catkin_ws/src/
cd ~/catkin_ws
catkin_make
source devel/setup.bash
roslaunch prms_bringup prms_system.launch
```

## External Components

The system expects these external modules to be connected in later steps:

- `NEXTE_Sentry_Nav`: FAST-LIO mapping/localization, `move_base`, DWA local planning, serial velocity bridge.
- `PRMS`: panoramic image extraction, maturity detection/classification, saved detection replay, and 3D HTML map generation.

Keep large raw data, ROS bags, trained weights, and generated outputs outside Git unless they are intentionally released as a minimal reproducibility dataset.

