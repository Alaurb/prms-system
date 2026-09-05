# Interfaces

## Coordinate Frames

Recommended TF tree:

```text
map
  camera_init
    body
      body_2d
      panoramic_camera
      lidar
      rgbd_camera
```

`map` is the global greenhouse frame. `body` is the robot base frame. `body_2d` is the planar navigation frame used by `move_base`.

## Topics

| Topic | Type | Direction | Description |
| --- | --- | --- | --- |
| `/prms/topology/global_path` | `nav_msgs/Path` | publish | Topology-guided row route |
| `/move_base_simple/goal` | `geometry_msgs/PoseStamped` | publish | Optional next waypoint goal |
| `/prms/perception/detections` | `prms_msgs/MaturityObservationArray` | publish | PRMS maturity observations |
| `/prms/fusion/observations` | `prms_msgs/MaturityObservationArray` | publish | Pose-aligned spatial observations |
| `/tf` | `tf2_msgs/TFMessage` | subscribe | Robot pose and sensor transforms |

## Detection Message

`prms_msgs/MaturityDetection` stores one fruit observation:

- image frame id and side view
- maturity class and confidence
- detection box in image coordinates
- spatial position after fusion, if available
- source tag for the position estimate
- optional track id

## Topology Map

`config/topology.yaml` defines row nodes and route edges. The first scaffold uses explicit ordered waypoints. Later versions can add graph search, blocked-edge handling, and row-switch logic.

