# PRMS: Panoramic Ripeness Detection and Spatial Mapping

This repository accompanies *Ripeness Monitoring in Open-Facility Environments Using a Quadruped Robot and Panoramic AI Recognition*. It provides offline panorama projection, two-stage tomato detection/ripeness classification, and spatial observation visualization. Navigation, robot control, SLAM and gait switching are outside its scope. External camera poses and registered ranges can be supplied through the [data interfaces](docs/interfaces.md).

The [original preprint](docs/paper/preprints202608.0999.v1.pdf) is retained as a historical reference. Revised manuscript source is in [docs/paper/root.tex](docs/paper/root.tex); figures and the journal template remain in the author's manuscript package.

## Run the supplied example

Use Python 3.12 and a virtual environment:

```bash
python -m venv .venv
# Activate .venv using your platform's activation command.
python -m pip install -r requirements.txt
python scripts/verify_dataset.py
python scripts/replay_observations.py --source demo --output outputs/replay
python -m unittest discover -s tests -v
```

Open `outputs/replay/index.html` locally. It is an offline interactive map with the saved annotated views. Replay does not run YOLO again. Expected: 13 frames, 68 observations (28 immature, 31 green mature, 9 discoloration, 0 mature), and 26 frame-side positions.

## Run new inference

Install the optional inference dependencies, then explicitly select the two-stage detector. The supplied model files are trusted project assets; only load weights from trusted sources.

```bash
python -m pip install -r optional-requirements.txt
python demo.py --input data/panoramas --map assets/farm_map.jpg --output outputs/inference --detector two-stage --detector-weights models/tomato_detector.pt --classifier-weights models/tomato_ripeness_classifier.pt --export-six-faces --max-frames 0
```

This exports six perspective faces and runs recognition on the left and right faces. Model predictions from a fresh run can differ from archived predictions with changes in checkpoints or dependency versions. The optional color detector is a smoke-test fallback, not a YOLO result.

Add `--pose-csv poses.csv` to consume camera poses supplied by any external localization system. Add `--range-manifest ranges.json` for registered radial ranges. The present geometry assumes level camera poses (yaw only); it is not a general six-degree-of-freedom fusion implementation. See [interfaces](docs/interfaces.md).

## Evidence and limitations

- The 13 panoramas and model weights are included, with per-file SHA-256 hashes.
- The sample has no measured poses or range maps. Default coordinates use a synthetic trajectory and assumed row planes; inferred heights are estimates.
- Bounding boxes and view dimensions preserve vertical pixel information. `plants.csv` is a legacy filename for frame-side observation groups, not identified plants.
- No measured geometry means no cross-frame deduplication or verified nearest-row filtering. Track IDs remain observation IDs or association candidates.
- Registered-range and supplied-pose inputs enable geometric filtering and candidate association, not automatically validated fruit identities or survey accuracy.
- Historical metrics in `benchmarks/` are development-validation records; their evaluation images are not included. This package cannot independently reproduce all manuscript performance claims.

See [paper requirements](docs/paper_requirements.md) and [provenance](docs/provenance.md).

## Layout

- `data/panoramas/`: 13 source panoramas.
- `models/`: detector and ripeness classifier.
- `ripeness_demo/`: projection, inference, mapping, range checks and HTML report.
- `demo/`: archived prediction output and offline viewer.
- `scripts/`: replay, integrity verification and evaluation entry points.
- `interfaces/ros_msgs/`: preserved ROS message schemas for external adapters; no ROS runtime is required.
- `tests/`: projection, input validation, association and report tests.

Original repository software remains under LICENSE. Imported processing code and accompanying data retain [their original terms](LICENSE_DATA_AND_IMPORTED_CODE): MIT for source code and CC BY 4.0 for data, images, weights and documentation. Third-party dependencies retain their own licenses.
