# Navigation Integration

The local navigation dependency has been cloned as:

```text
third_party/NEXTE_Sentry_Nav_src
```

Current checked revision:

```text
5531ed2 Update README.md
```

This dependency is intentionally ignored by the main repository. It should be treated as an external source tree or replaced with a Git submodule after the integration stabilizes.

## Relevant Packages

| Function | Package | Entry Point |
| --- | --- | --- |
| LiDAR mapping | `sentry_slam/FAST_LIO` | `launch/mapping_mid360.launch` |
| LiDAR localization | `sentry_slam/FAST_LIO_LOCALIZATION` | `launch/localization_MID360.launch` |
| 2D navigation | `sentry_nav` | `launch/sentry_movebase.launch` |
| Velocity smoothing | `sentry_tools/velocity_smoother_ema` | `launch/velocity_smoother_ema.launch` |
| Serial output | `sentry_comm/sentry_serial` | `launch/sentry_serial.launch` |

## Observed Topic/Frame Contracts

`sentry_movebase.launch` starts `move_base` with:

```text
/map  -> prior_map
/odom -> Odometry
```

It also starts `trans_tf_2d` and includes the EMA velocity smoother.

`sentry_serial.launch` uses:

```text
cmd_vel_topic = cmd_vel
default serial port = /dev/ttyACM0
```

## PRMS System Additions

The system repository adds a topology-guidance layer above the imported navigation stack:

- `/prms/topology/global_path` publishes the greenhouse row route as `nav_msgs/Path`.
- `/move_base_simple/goal` can receive sequential route waypoints when waypoint mode is enabled.
- `/prms/perception/detections` receives maturity detections from the PRMS recognition bridge.
- `/prms/fusion/observations` publishes pose-aligned spatial maturity observations.

## Next Implementation Step

Create a ROS workspace that includes both source trees:

```bash
mkdir -p ~/prms_ws/src
cp -r prms-system/src/* ~/prms_ws/src/
cp -r prms-system/third_party/NEXTE_Sentry_Nav_src/* ~/prms_ws/src/
cd ~/prms_ws
catkin_make
source devel/setup.bash
```

After the workspace builds, the first integration target is a combined launch file that starts:

1. MID360 driver and FAST-LIO localization.
2. `sentry_movebase.launch`.
3. `prms_topology/topology_path_publisher.py`.
4. PRMS perception bridge or online detector.
5. PRMS fusion node.

