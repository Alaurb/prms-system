# Setup Status

Last checked: 2026-09-06

## Windows Tools

- Git: available.
- Python: available.
- GitHub CLI: available.
- GitHub authentication: active on the development machine.

## GitHub Repository

Remote repository:

```text
https://github.com/Alaurb/prms-system
```

Local branch:

```text
main -> origin/main
```

## Navigation Dependency

The navigation dependency was cloned locally with shallow history:

```text
third_party/NEXTE_Sentry_Nav_src
```

Checked revision:

```text
5531ed2 Update README.md
```

This folder is ignored by the main Git repository and should be treated as an external dependency.

## ROS Environment

WSL distributions detected:

- Ubuntu-20.04
- Ubuntu-22.04
- docker-desktop

The PRMS system packages were copied into:

```text
~/prms_ws/src
```

The following command completed successfully in Ubuntu-20.04:

```bash
source /opt/ros/noetic/setup.bash
cd ~/prms_ws
catkin_make --only-pkg-with-deps prms_bringup prms_fusion prms_msgs prms_perception_bridge prms_topology
```

Launch-file parsing also succeeded:

```bash
source ~/prms_ws/devel/setup.bash
roslaunch prms_bringup prms_system.launch --nodes
```

Detected nodes:

```text
/topology_path_publisher
/prms_csv_bridge
/maturity_fusion_node
```

## Smoke Simulation

The lightweight simulation was added and checked in Ubuntu-20.04.

Command:

```bash
source /opt/ros/noetic/setup.bash
source ~/prms_ws/devel/setup.bash
powershell -ExecutionPolicy Bypass -File scripts\run_wsl_smoke.ps1
```

Observed success line:

```text
PRMS simulation smoke passed: path_poses=3 odom_samples=8 travelled_m=0.560
```

The reference-map smoke script also passed:

```text
PRMS map smoke passed: map=680x130 resolution=0.050 path_poses=3 travelled_m=0.560
```

The closed-loop navigation smoke script also passed:

```text
PRMS closed-loop navigation smoke passed: path_poses=3 cmd_samples=88 final_error_m=0.195
```
