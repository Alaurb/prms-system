# PRMS: Panoramic Tomato Ripeness Detection and Spatial Mapping

PRMS is the reproducibility codebase for the manuscript *Ripeness Monitoring in Open-Facility Environments Using a Quadruped Robot and Panoramic AI Recognition*. It turns 360-degree tomato greenhouse panoramas into cube faces, recognizes tomatoes and ripeness stages on the left and right crop-row views, and exports an observation-level spatial map with annotated images, CSV files, JSON metadata, and a local result viewer.

The repository implements the perception and mapping portion of the study. Robot navigation, SLAM, gait control, and obstacle avoidance are not included here. Camera poses and registered range maps may be supplied by an external localization system through documented file interfaces.

## What the software does

```text
Equirectangular panorama
        |
        v
Six perspective cube faces
        |
        +--> left and right faces --> tomato detector --> ripeness classifier
                                                        |
                                                        v
Camera pose + optional registered range ---> observation-level spatial mapping
                                                        |
                                                        v
Annotated views + CSV/JSON + local interactive result page
```

The model workflow uses two supplied YOLO models: a tomato detector proposes fruit crops, then a five-class classifier assigns `immature`, `green_mature`, `discoloration`, `mature`, or `other`. The `other` class is excluded from ripeness results. The supplied example uses a brightness-enhanced detector branch in addition to the original image.

## Fastest path: desktop operation window

The project includes a small Tkinter desktop window so it can be operated without constructing command lines.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r optional-requirements.txt
python app.py
```

On Windows, after the environment is installed, you can also run `powershell -ExecutionPolicy Bypass -File run_desktop.ps1`.

In the window, choose the panorama folder, map image, output folder, and model weights. The defaults point to the included example. Then click **Run detection and mapping**. The window shows the processing log and **Open latest result** opens the generated local result page.

Use **Replay included results** when you want to inspect the archived output without loading models. Use **Verify included data** to check the SHA-256 manifest of the curated sample.

Python 3.12 is the tested environment. Python 3.13 is not the project’s verified runtime.

## Command-line operation

The GUI calls the same transparent command shown below. This makes batch operation and debugging straightforward.

```powershell
python demo.py `
  --input data/panoramas `
  --map assets/farm_map.jpg `
  --output outputs/inference `
  --detector two-stage `
  --detector-weights models/tomato_detector.pt `
  --classifier-weights models/tomato_ripeness_classifier.pt `
  --confidence 0.25 `
  --export-six-faces `
  --max-frames 0
```

`--max-frames 0` processes every panorama. The supplied sample contains 13 panoramas numbered 702–714. The run writes its results to the chosen output directory:

| Output | Purpose |
| --- | --- |
| `index.html` | Local interactive viewer for the observation map and annotated frames. |
| `views/` | Left/right views, plus all six cube faces when requested. |
| `annotated/` | Detection and ripeness labels drawn on left/right views. |
| `detections.csv` | Bounding boxes, predicted classes, confidence, coordinate estimate, and coordinate provenance. |
| `trajectory.csv` | Poses used by the run, including whether they are measured or synthetic. |
| `plants.csv` | Frame-side observation groups; these are not confirmed individual plants. |
| `tracks.json` | Conservative cross-frame association candidates when measured geometry is present. |
| `summary.json` and `run_config.json` | Counts, assumptions, model settings, and input provenance. |

## Supplied reproducibility example

The repository includes 13 source panoramas, weights, a reference map, saved predictions, annotated views, benchmark records, and metadata.

```powershell
python scripts/verify_dataset.py
python scripts/replay_observations.py --source demo --output outputs/replay
python -m unittest discover -s tests -v
```

The saved replay is expected to generate 68 observations from 13 frames and 26 frame-side positions: 28 immature, 31 green mature, 9 discoloration, and 0 mature. Replay reuses archived detections; it does not run the models again.

## External pose and range data

The default example has no measured localization or depth/range stream. It generates a clearly labelled synthetic display trajectory and estimates coordinates using an assumed row plane. Those coordinates are useful for demonstrating the data flow but are not validated greenhouse fruit locations.

To use externally provided camera poses:

```text
frame,x,y,z,yaw,route
frame_001.jpg,2.45,19.70,1.15,0.0,row_1
```

Then add `--pose-csv poses.csv`. Values are camera optical-centre coordinates in metres and yaw in radians. The current interface assumes a level camera; it does not interpolate raw localization streams or implement general six-degree-of-freedom transformations.

To use range measurements, add both `--pose-csv` and `--range-manifest`. Range arrays must already be calibrated and registered radial distances in the same cube-face geometry. The manifest checks stated timestamp consistency and rejects invalid range regions. Full details and file schemas are in [docs/interfaces.md](docs/interfaces.md).

## Interpretation limits

- A detection is an image observation, not automatically a unique tomato.
- Left/right view selection alone does not prove that background-row fruit were excluded.
- Pixel vertical position is preserved. Metric fruit height requires measured range, camera pose, and calibration.
- Range-band filtering and association are candidates until evaluated against independently annotated geometry.
- The included benchmark values are archived development-validation records; the evaluation images are not included and the validation split was used for model selection.
- The repository is designed for offline processing. It does not claim real-time end-to-end inference.

These limits mirror the revised manuscript and prevent the sample visualization from being overstated as a validated fruit-level 3D reconstruction.

## Repository layout

```text
app.py                     Desktop operation window
demo.py                    Batch processing entry point
data/panoramas/            13 source equirectangular panoramas
models/                    Tomato detector and ripeness classifier
ripeness_demo/             Projection, inference, mapping, evidence checks, reports
assets/                    Reference map
demo/                      Archived predictions and local viewer
scripts/                   Replay, integrity verification, evaluation helpers
interfaces/ros_msgs/       Preserved message schemas for external adapters
docs/                      Interfaces, provenance, paper scope, manuscript snapshot
tests/                     Core processing and desktop-command tests
```

## Manuscript and evidence

The original preprint is retained at [docs/paper/preprints202608.0999.v1.pdf](docs/paper/preprints202608.0999.v1.pdf). The revised manuscript source snapshot is [docs/paper/root.tex](docs/paper/root.tex). It is intentionally clear about which results are archived demonstrations and which claims need further measurement.

Read [docs/paper_requirements.md](docs/paper_requirements.md) for a claim-to-evidence map, [docs/provenance.md](docs/provenance.md) for imported-data provenance, and [docs/interfaces.md](docs/interfaces.md) before using external pose or range data.

## License

Project code is licensed under the repository [LICENSE](LICENSE). Imported code, panoramas, annotations, weights, and documentation retain the terms recorded in [LICENSE_DATA_AND_IMPORTED_CODE](LICENSE_DATA_AND_IMPORTED_CODE): MIT for source code and CC BY 4.0 for the listed data assets. Third-party dependencies retain their own licenses.
