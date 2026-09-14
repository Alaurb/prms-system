# Remote orchard workspace layout

This is an operational layout for the separate Ubuntu orchard workspace. It
does not move raw data, models, ROS build products, or existing training
directories. Those paths are retained until every consuming script has been
converted to configuration-based paths.

## Current directories

| Area | Existing locations | Rule |
| --- | --- | --- |
| Raw sensor data | `datasets/`, `images/`, `检测图片/`, `share/` | Read-only source material; do not put in Git. |
| Labels and training material | `yolo-v8/`, `yolo_test/`, `tomato_data/`, `tomato_crops/` | Preserve labels and write a versioned manifest before reorganizing. |
| Source and tools | `src/`, `scripts/`, `tools/` | Code only; avoid embedding absolute paths. |
| Models and runs | `models/`, `runs/` | Weights and experiment outputs; retain provenance and checksums. |
| Derived output | `outputs/`, `map/`, `heatmap_2d/` | Regenerable; never overwrite a reviewed run. |
| Documentation | `WORKSPACE.md`, `果园检测操作手册.md` | Keep operational instructions and inventory here. |
| Archive | `archive/packages/` | ZIP backup packages moved out of the repository root. |

## Safe working rules

1. Create new exports beneath `outputs/YYYYMMDD_description/`.
2. Keep the original bag, images, labels and checkpoints unchanged; record
   relative path, SHA-256, source and licence before copying data to training.
3. Keep run configuration beside each experiment result. A model is not a
   Green Gem maturity model unless its taxonomy and held-out evaluation are
   documented.
4. Use a separate Git repository for code and small documentation only. Exclude
   raw data, ROS bags, generated outputs, virtual environments and model
   weights from Git.
5. The root-level ZIP files have been moved to `archive/packages/` as backup
   packages. Their extracted siblings remain in place.

## Planned migration, not yet performed

After a reproducible data manifest and path configuration exist, source code
can be moved into a dedicated repository and data can be exposed through
`raw/`, `annotations/`, `models/`, `runs/` and `derived/` aliases.
Do not perform that migration by drag-and-drop: ROS launch files and legacy
scripts must be tested after every path change.
