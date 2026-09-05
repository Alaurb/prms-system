# Next Steps

## Step 1: Attach Navigation Code

Place the navigation implementation under:

```text
third_party/NEXTE_Sentry_Nav/
```

Then map its published topics to the system interface:

- FAST-LIO map and localization output to `map` / `camera_init` / `body`.
- `move_base` local planner input from `/prms/topology/global_path` or waypoint goals.
- Serial velocity output from `/cmd_vel` through the existing sentry serial bridge.

## Step 2: Attach PRMS Recognition Code

Place the recognition implementation under:

```text
third_party/prms/
```

The initial bridge reads:

```text
third_party/prms/demo/detections.csv
```

Later, replace the CSV bridge with an online camera subscriber and detector service while preserving `/prms/perception/detections`.

## Step 3: Implement Measured Fusion

The current fusion node preserves the interface and TF alignment point. The measured version should:

- align image timestamp, LiDAR pose timestamp, and range timestamp;
- reject observations outside the crop-row range gate;
- project detections with measured range instead of fixed row offset;
- output candidate fruit tracks with explicit association confidence.

## Step 4: Validate with Real Runs

Reviewer-facing validation should include:

- detection mAP or precision/recall on an independent test split;
- navigation success rate, path length, traversal time, and obstacle handling;
- 3D localization error against manually labeled fruit positions;
- association precision/recall for repeated observations;
- runtime throughput for online or offline mode.

