# PRMS System Handoff for 5.6-terra

Last updated: 2026-09-07

## Purpose

This repository is the open-source system scaffold for PRMS, a greenhouse inspection system that combines row-level navigation, panoramic maturity recognition, and spatial mapping. The current repository focuses on reproducible system interfaces and a lightweight navigation simulation. It is not yet a full robot deployment package.

## Current Git State

- Main branch: `main`
- Remote: `https://github.com/Alaurb/prms-system`
- Latest local commit not yet pushed at the time of this note:

```text
74b1820 Add navigation smoke visualization
```

Push attempts failed because the machine could not connect to `github.com:443`. Once network access is restored, run:

```bash
git push origin main
```

## What Has Been Completed

### 1. ROS package scaffold

The repository contains a ROS Noetic-oriented catkin workspace source layout under `src/`:

- `prms_bringup`: launch files, runtime configs, and reference maps.
- `prms_msgs`: custom maturity detection and observation messages.
- `prms_topology`: topology route publisher.
- `prms_perception_bridge`: CSV/replay bridge for perception outputs.
- `prms_fusion`: initial pose-aligned maturity observation fusion node.
- `prms_sim`: lightweight simulation and smoke-test nodes.

The top-level `config/`, `launch/`, and `examples/` folders mirror the package resources for easier open-source inspection.

### 2. Topology route guidance

`config/topology.yaml` defines a minimal greenhouse row route:

```text
row_702_entry -> row_702_mid -> row_702_exit
```

The route is published by:

```text
src/prms_topology/scripts/topology_path_publisher.py
```

Main output topic:

```text
/prms/topology/global_path
```

The current path is intentionally simple: three waypoints along one row. This is enough for reproducible interface validation while keeping the repository lightweight.

### 3. Lightweight navigation smoke tests

Three smoke levels exist:

1. `scripts/run_wsl_smoke.ps1`
   - topology path plus simulated localization;
   - verifies path and odometry publication.

2. `scripts/run_wsl_map_smoke.ps1`
   - additionally loads the reference occupancy map;
   - verifies `/map`, path, and odometry.

3. `scripts/run_wsl_closed_loop_nav_smoke.ps1`
   - topology path -> simple path follower -> `cmd_vel` -> odometry simulator -> final-goal validator;
   - currently the best minimal navigation reproducibility check.

Observed result from the latest local run:

```text
PRMS closed-loop navigation smoke passed: path_poses=3 cmd_samples=95 final_error_m=0.195
```

### 4. Navigation trace export

The closed-loop validator now exports a replayable JSON trace when `trace_output` is provided.

Default output from the helper script:

```text
outputs/nav_smoke/latest_trace.json
```

The trace schema is:

```text
prms.nav_smoke_trace.v1
```

It contains:

- route name;
- map metadata;
- final error;
- command sample count;
- topology path points;
- odometry samples;
- velocity command samples.

Implementation file:

```text
src/prms_sim/scripts/closed_loop_nav_validator.py
```

### 5. Browser visualization

A lightweight browser visualization has been added:

```text
examples/nav_smoke/index.html
```

Supporting files:

```text
examples/nav_smoke/trace_sample.json
examples/nav_smoke/greenhouse_reference.png
examples/nav_smoke/README.md
```

The page shows:

- greenhouse reference grid map;
- topology path;
- simulated odometry trajectory;
- robot pose playback;
- final-goal error;
- command sample count;
- route length.

It includes a built-in sample and can load a fresh trace from:

```text
outputs/nav_smoke/latest_trace.json
```

This provides a quick visual answer to whether the simulated navigation loop is doing anything meaningful.

### 6. Reference map

The current reference occupancy map lives in:

```text
examples/maps/greenhouse_reference.pgm
examples/maps/greenhouse_reference.yaml
src/prms_bringup/maps/greenhouse_reference.pgm
src/prms_bringup/maps/greenhouse_reference.yaml
```

It is a simple greenhouse-row occupancy grid inspired by the provided tomato-field row image. It is suitable for smoke tests, not for reporting real navigation performance.

### 7. Repository integrity check

`scripts/check_framework.py` verifies that the expected source, configuration, map, and visualization files exist.

Run:

```bash
python scripts/check_framework.py
```

Observed result:

```text
framework check ok: 46 files
```

## How to Reproduce the Current Navigation Demo

From the repository root on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_wsl_closed_loop_nav_smoke.ps1
```

The script assumes:

- WSL is installed;
- Ubuntu-20.04 is available;
- ROS Noetic is installed inside Ubuntu-20.04.

After the run, open:

```text
examples/nav_smoke/index.html
```

Then use **Load trace JSON** to load:

```text
outputs/nav_smoke/latest_trace.json
```

If the user accidentally runs the PowerShell script from a different folder and sees a missing file error, ask them to either enter the repository root first or run the script using an absolute path outside the repository documentation. Do not commit machine-specific paths.

## Important Constraints

### No machine-specific paths in the repository

Do not add paths such as:

```text
absolute personal workstation paths
```

or any personal cloud-drive, desktop, chat-cache, or temporary file paths to committed documentation, scripts, or data.

Use repository-relative paths in docs and scripts.

### Keep large dependencies out of Git

The external navigation repository and large assets should not be committed directly unless deliberately converted into a minimal reproducibility dataset.

Ignored examples:

- `third_party/`
- `outputs/`
- ROS build folders;
- trained weights;
- raw bags;
- large image sets.

### Keep the current simulation honest

The current closed-loop navigation smoke test is a small deterministic system test. It proves topic wiring and basic route-following logic, not real robot navigation performance. Do not overstate it in papers, README, or figures.

## Current Design Direction

The full system should have three interacting subsystems:

```text
Topological row route
        |
        v
FAST-LIO / move_base navigation
        |
        v
Timestamped robot pose
        |
        +-------------------+
                            v
Panoramic image -> PRMS detector -> maturity observations
                            |
                            v
Pose/image fusion -> plant-level 3D maturity map
```

The navigation side should follow the basic method of `NEXTE_Sentry_Nav`:

- FAST-LIO mapping/localization;
- point-cloud to 2D map projection;
- `move_base` global/local planning;
- DWA local planner;
- velocity command output.

PRMS adds a topological row layer above that method, so the robot can receive row-level route guidance rather than only local goal clicks.

## Recommended Next Work

### Priority 1: Push the current local commit

Network is the only blocker. When GitHub access is stable:

```bash
git push origin main
```

Then verify:

```bash
git status -sb
```

Expected:

```text
## main...origin/main
```

### Priority 2: Add a cleaner ROS launch for trace export

The shell script passes `trace_output`, but `src/prms_bringup/launch/closed_loop_nav_smoke.launch` does not yet expose a trace output argument.

Recommended change:

- add a launch arg such as `trace_output`;
- pass it into `closed_loop_nav_validator.py`;
- document how to run it with `roslaunch`.

### Priority 3: Improve visualization with real trace loading convenience

Current `index.html` supports manual JSON loading because browser security can block automatic local file loading. Good next improvements:

- add a small Python static server script, e.g. `scripts/serve_nav_smoke_viewer.py`;
- make the page auto-load `outputs/nav_smoke/latest_trace.json` when served over HTTP;
- keep manual file loading as fallback.

### Priority 4: Integrate real navigation stack interfaces

Use the inspected `NEXTE_Sentry_Nav` method as an external dependency, not as pasted source.

Recommended integration tasks:

- document exact required ROS topics from the navigation stack;
- add launch arguments for external localization and planning nodes;
- map PRMS topology waypoints to `move_base_simple/goal`;
- add a route executor node that sends waypoints sequentially and records success/failure;
- record metrics: traversal time, final pose error, path length, and recovery events.

### Priority 5: Connect perception repository

The current PRMS perception side is represented by a ROS bridge interface. The actual detector should be connected in one of two ways:

1. offline replay mode:
   - run panoramic extraction and YOLO detection before ROS;
   - export CSV/JSON;
   - publish via `prms_csv_bridge.py`.

2. online mode:
   - subscribe to camera frames;
   - run panoramic left/right extraction;
   - run YOLO detection;
   - publish `prms_msgs/MaturityObservationArray`.

Replay mode is recommended first because it is easier to reproduce and debug.

### Priority 6: Add plant-level map fusion

The current fusion node is still a scaffold. Next concrete work:

- align detections by timestamp to nearest robot pose;
- map left/right image views to row-side coordinates;
- cluster observations into plant positions;
- aggregate maturity counts per plant;
- export a 3D maturity distribution file and browser demo.

This should eventually connect back to the existing PRMS 3D map style where each column represents one plant and each colored cube represents one fruit maturity class.

### Priority 7: Prepare reproducibility data

For a strong open-source release, add a minimal dataset separate from the main source tree or under a clearly scoped `dataset_sample/` folder.

Recommended contents:

- a small number of panoramic images;
- detection labels or model outputs;
- pose trajectory;
- topology file;
- generated 3D maturity map;
- README with units, file formats, and reproduction steps.

Do not include private paths, personal identifiers, oversized raw folders, or duplicated train/validation images.

## Data Still Needed from the User

For realistic navigation and fusion validation, request the following:

1. Real or representative greenhouse map files used by localization.
2. A short LiDAR/camera ROS bag or exported timestamped pose trajectory.
3. Panoramic frames with timestamps aligned to robot pose.
4. Camera-to-body and LiDAR-to-body calibration.
5. A small independent detection test split for maturity detection metrics.
6. Optional manual fruit/plant position annotations for spatial accuracy validation.

## Suggested Immediate Task for 5.6-terra

Start with this exact sequence:

1. Check working state:

```bash
git status -sb
git log -1 --oneline
```

2. If the local commit is still ahead, push it:

```bash
git push origin main
```

3. Verify the framework:

```bash
python scripts/check_framework.py
```

4. Run the closed-loop smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_wsl_closed_loop_nav_smoke.ps1
```

5. Open the visualization:

```text
examples/nav_smoke/index.html
```

6. Implement Priority 2 and Priority 3 before expanding the actual navigation stack. This keeps the repo demonstrable and reproducible at every step.
