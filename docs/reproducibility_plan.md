# Reproducibility Plan

This repository is organized as a staged reproducibility package. The first layer runs without robot hardware. Later layers add the imported navigation stack, perception data, and real sensor recordings.

## Layer 1: Interface Smoke Simulation

Purpose:

- verify that the ROS packages build;
- verify topology route publication;
- verify simulated `map -> body` TF and `Odometry`;
- verify that a route can be followed by a localization stream.

Command on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_wsl_smoke.ps1
```

Expected success line:

```text
PRMS simulation smoke passed: path_poses=3 odom_samples>=3 travelled_m>=0.5
```

This layer verifies the public ROS interface baseline. It does not prove greenhouse navigation performance.

## Layer 2: Navigation Stack Integration

Purpose:

- build the imported NEXTE navigation packages;
- run FAST-LIO localization or replay localization topics from a recorded run;
- send topology waypoints into `move_base`;
- record success rate, path length, traversal time, and obstacle handling.

Additional data needed:

- greenhouse map files used by localization and `move_base`;
- representative LiDAR bag or live MID360 input;
- TF calibration between LiDAR, robot base, panoramic camera, and RGB-D camera;
- route topology file for each tested greenhouse layout.

## Layer 3: Perception and Fusion Reproducibility

Purpose:

- run PRMS detection on released panoramic frames;
- publish maturity detections through `/prms/perception/detections`;
- align detections with pose and optional measured range;
- generate 3D maturity maps and tabular outputs.

Additional data needed:

- independent test images and labels for detection metrics;
- timestamped panoramic frames;
- timestamped robot pose trajectory;
- optional registered depth or range evidence for each view;
- manual 3D fruit position annotations for spatial accuracy evaluation.

## Layer 4: Reviewer-Facing Evidence

Purpose:

- verify central manuscript claims with quantitative evidence.

Recommended outputs:

- detection precision, recall, or mAP on an independent test split;
- localization and navigation statistics;
- 3D projection error and fruit association accuracy;
- runtime throughput for online or offline operation;
- minimal dataset with raw inputs, processed outputs, metadata, and scripts.

