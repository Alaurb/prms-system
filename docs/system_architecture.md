# System Architecture

## Goal

The system targets greenhouse crop inspection with a wheel-legged quadruped robot. It combines autonomous row traversal, panoramic maturity recognition, and spatio-temporal mapping.

## Layers

1. Hardware layer
   - LiDAR for mapping, localization, and obstacle geometry.
   - Panoramic camera for continuous crop imaging on both sides of the row.
   - RGB-D camera for local terrain and depth evidence when available.
   - Wheel-legged base for normal row traversal and terrain transition.

2. Navigation layer
   - FAST-LIO mapping and localization.
   - 2D occupancy projection for `move_base`.
   - Topology map for row-level global guidance.
   - DWA local planning and velocity command output.

3. Recognition layer
   - Equirectangular panorama to cube-map perspective faces.
   - Left/right crop-row views.
   - YOLO-based fruit detection and maturity classification.

4. Fusion layer
   - Timestamp alignment between robot pose and image frame.
   - Projection from image detections to greenhouse coordinates.
   - Optional measured range/depth validation.
   - Track-level or observation-level maturity distribution output.

5. Application layer
   - 3D maturity distribution map.
   - Harvest planning support.
   - Yield estimation support.
   - Greenhouse crop management records.

## Navigation Method Boundary

The navigation package follows the method pattern of `NEXTE_Sentry_Nav`: FAST-LIO localization, map projection, `move_base`, DWA local planning, TF conversion, and serial velocity control.

This repository adds the topological route layer above the local navigation stack. The topology layer publishes an ordered global path through greenhouse rows and can provide sequential waypoint goals to `move_base`.

## Recognition Method Boundary

The recognition package is connected through a bridge rather than copied directly. This allows the PRMS detector to run offline, online, or in replay mode while keeping the ROS interface stable.

The bridge publishes normalized maturity observations. The fusion layer is responsible for assigning those observations to map positions using robot pose and optional range evidence.

