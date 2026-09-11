# PRMS landscape and refactor rationale

## What comparable systems show

PRMS is not the first system to combine greenhouse imagery with fruit maturity or crop mapping. The useful comparison is at the level of evidence and operating assumptions.

| Reference | What it demonstrates | Design implication for PRMS |
| --- | --- | --- |
| [tomatOD](https://github.com/up2metric/tomatOD) | Greenhouse tomato detection plus three ripening categories in COCO format. | External red-tomato labels can help pretrain fruit localization, but cannot define Green Gem yellow-halo readiness. |
| [Laboro Tomato](https://github.com/laboroai/LaboroTomato) | Detection/instance segmentation with ripe-stage labels. | Keep detector and cultivar-specific maturity evidence separable. Its labels are not a substitute for field rules. |
| [Plantalyzer](https://www.ingreenhouses.com/plantalyzer/) | Commercial tomato monitoring maps trusses per stem, fruit counts, and colour using purpose-built cameras. | Do not imply stem/truss identity from panorama frame-side grouping. Add truss claims only after dedicated annotations and calibrated acquisition. |
| [Four Growers GR-100](https://fourgrowers.com/products/robotic-harvesting-technology/) | Commercial harvesting and row-scale yield analytics use calibrated stereo sensing. | A map needs explicit sensor provenance; a plausible display path is not a location benchmark. |
| [YOLOv8 + RealSense example](https://github.com/pablofntdz/yolov8-tomato-detection) | Depth-based fruit coordinates remain camera-frame coordinates until extrinsic calibration is supplied. | PRMS requires matched pose, registered range, and calibration checks before emitting measured-geometry candidates. |

Recent truss-focused work also treats fruit/truss association as a separate perception task rather than a rendering choice. PRMS therefore keeps the dashed vine as a frame-side observation guide, not a reconstructed botanical structure.

## Result-package architecture

```text
panoramas + models + optional pose/range
                 |
                 v
            inference or replay
                 |
       +---------+----------+
       |                    |
       v                    v
CSV / images / map     evidence.json
                         |
                         v
                 local 3D observation viewer
```

`evidence.json` is the contract between processing and presentation. It has three current statuses:

- `archived_legacy_replay`: saved historical predictions, no current inference.
- `unvalidated_observation_layout`: predictions with synthetic or incomplete spatial evidence.
- `measured_geometry_candidate`: matched pose and registered radial range, still requiring independent evaluation for fruit identity and accuracy.

## Next upgrade order

1. Collect field-verified Green Gem four-class labels using the yellow-halo protocol and split by route/date.
2. Train a one-class fruit detector and a cultivar classifier; retain the model card, exact split, and confusion matrix.
3. Add calibrated pose/range acquisition and evaluate localization separately from recognition.
4. Only then annotate fruit/truss/stem keypoints and evaluate association before enabling biological bunch or yield claims.
