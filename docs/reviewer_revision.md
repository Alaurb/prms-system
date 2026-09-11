# Reviewer revision: correctness and evaluation

## Implemented corrections

- The archived classifier's `maturity` class maps to `mature`. Unknown model labels now fail during loading, and mixed taxonomies are rejected.
- Production report schema comes from the complete model vocabulary. Empty and immature-only Green Gem outputs retain the Green Gem schema.
- `detections.csv` preserves raw class, detector score and classifier score for the two-stage pipeline. The geometric-mean `confidence` is a ranking score, not a calibrated probability. `candidate_audit.json` records classifier rejections; `rejected_observations.json` records geometry rejections. Compare them by frame, side and box.
- Group layout positions remain stable when filtering. The coordinate view uses stored x/y/z without artificial branches and identifies the range source. Assumed coordinates remain assumptions. Source-image previews now contain the entire image.
- The archived demo is preserved. Regenerated inference is written to `outputs/reviewer_fixed`.
- Component evaluation accepts `--split test` (default), rejects missing splits, and accepts explicit classifier resolution. Pass the actual deployment resolution; legacy records used 96 and the proposed Green Gem training recipe uses 224.
- Inference also accepts `--classifier-imgsz`, defaults to the checkpoint setting and records the resolved value. Crop preparation defaults to zero padding to match inference; if using other padding, treat this as a distribution change and validate it.

## Initial rerun comparison

The first corrected run on all 13 panoramas retained 85 observations (9 mature, 9 discoloration, 34 green_mature and 33 immature), versus 68 archived observations. All 68 archived boxes matched a new box at IoU >= 0.5 in the same frame and side, with no matched class changes; 17 observations were added and none unmatched from the old run. Nine newly included mature predictions are consistent with the repaired alias. Do not attribute the other eight additions solely to that fix: the archive does not record every original inference setting, including the confidence threshold. This is a reproducibility limitation, not a measured recall gain.

`scripts/compare_runs.py --old demo/detections.csv --new outputs/reviewer_fixed/detections.csv --output outputs/reviewer_fixed/comparison.json` exports the box-level comparison and hashes of both CSV inputs.

## End-to-end evaluation

Create exhaustive annotations for each selected left/right view, including empty views:

```json
{"views":[{"frame":"a.jpg","side":"left","objects":[{"class_name":"harvest_ready","bbox":[10,20,40,60]}]},{"frame":"a.jpg","side":"right","objects":[]}]}
```

Run:

```powershell
python scripts/evaluate_pipeline.py --predictions outputs/inference/detections.csv --truth labels.json --taxonomy green_gem --output outputs/pipeline_metrics.json
```

This evaluates final retained predictions, including upstream losses. Matching is class-agnostic descending-IoU greedy one-to-one at IoU 0.5. Wrong classes contribute a false positive to the predicted class and a false negative to the true class. Reports include unmatched detections, missed objects, per-class precision/recall/F1, and matched-object confusion. This is a fixed-operating-point evaluation, not COCO AP. Only explicitly annotated views enter the denominator; annotation completeness is a human responsibility.

## Split and field annotation requirements

Crop generation now requires `panorama_id,group_id,capture_date,route` in addition to image, box, label and split. It requires train, val and test and rejects shared panorama, group, date, route or identical image bytes across splits. This conservative protocol holds out both dates and routes. Use globally consistent group IDs for repeated fruit/plant visits. No current field data can be certified independent merely by renaming IDs.

All four fruit outcomes remain. Record `readability` (clear/partial/ungradable), `occlusion`, `defect_type`, annotator ID and adjudication separately in the annotation CSV; extra columns are retained in `split_manifest.json`. Put ungradable fruit in an unresolved annotation queue; do not relabel it as `other`. Component tests and end-to-end tests must explicitly document treatment of ignored/ungradable regions; the current evaluator expects fully adjudicated views.

For yellow-halo annotation, use examples of real Green Gem fruit spanning lighting, view angle and borderline yellow/green surfaces. Each annotator independently assigns one of the four classes or marks unresolved. Record grower harvest decisions and disagreements, then adjudicate without inspecting model predictions. In a single image, "stable" means a discernible surface-colour cue rather than glare; temporal persistence can only be asserted from matched repeated observations. Do not infer softness, Brix or internal maturity from a photograph. Confirm the visual thresholds with the grower before releasing field labels.

Report per-class agreement and a confusion table before adjudication. Numerical hue/area cutoffs are not established by the present data and are intentionally not invented here.

## Remaining evidence

The repository has no independently verified Green Gem holdout labels or surveyed fruit coordinates. The new evaluator is executable, but meaningful field accuracy and localization metrics require those inputs. Legacy rerun differences diagnose software behavior and do not establish true-positive improvements.

## Verification performed

The final full run is in `outputs/reviewer_fixed_final/`. Its detections CSV hash is `6a88593332464a1df6af916ae3931018d457e2f19b872a13f6b93d5814c64220`, identical to the first corrected run. `comparison.json` records the archived comparison. The output records resolved classifier resolution and model hashes.

26 Python tests pass, including a two-stage inference fixture proving `maturity` is retained and `other` is audited. `node tests/check_report_runtime.cjs outputs/reviewer_fixed_final/index.html` checks actual generated JavaScript for stationary filtered observations and unchanged coordinate values. The existing 59-file archive manifest still passes without being refreshed. The local browser was also used to verify the coordinate switch and result counts.
