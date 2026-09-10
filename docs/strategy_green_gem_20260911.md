# Green Gem revision strategy - 2026-09-11

## Decisions now fixed

1. The target crop is the Green Gem tomato cultivar, whose ripe fruit remains predominantly green.
2. The production outcome is visual harvest maturity, not generic red-tomato ripeness.
3. The field rule for `harvest_ready` is a stable yellow or yellow-green halo. The exact threshold must be verified and documented by the grower team.
4. The reported fruit classes are `immature`, `mature_green`, `harvest_ready`, and `overripe_or_defective`. `other` is a classifier-only negative class.
5. Existing weights, archived metrics, and the 13-panorama replay predate this taxonomy. They remain runnable legacy evidence and must not be reported as Green Gem accuracy results.

## What the paper can claim now

- Panoramic reprojection, bilateral offline detection workflow, external pose/range interfaces, and transparent observation reporting are implemented.
- Field images provide qualitative acquisition examples.
- The repository provides a concrete protocol for collecting and training a Green Gem model.

## What it must not claim now

- First tomato maturity-monitoring system, first 3D tomato map, or a new commercial harvesting solution.
- Validated Green Gem harvest-readiness accuracy, unique-fruit counts, biological truss reconstruction, or metric fruit coordinates.
- That the bundled legacy model's red-tomato-like labels represent Green Gem maturity.

## Literature and market positioning

Tomato robot perception, fruit/truss association, registered row mapping, and commercial location-aware yield monitoring already exist. The defensible position is a cultivar-specific system integration: panoramic inspection of Green Gem tomatoes using a yellow-halo harvest rule, with a reproducible distinction between visual observation groups and measured crop geometry. This is a positioning hypothesis, not a novelty claim; a systematic literature review is required before using ``to our knowledge'' language.

## Visualization decision

The main repository view is a compact 3D observation-bunch view:

- fruit symbols are visualized around a thin vine-like guide;
- the guide groups detections from one panorama frame and one crop-row side;
- it is never labelled as a reconstructed stem, biological truss, physical plant, or metric height;
- a small 2D map supplies row-side context;
- the original annotated view is the evidence panel used to inspect suspected missed fruit.

The next UI iteration should fit the 3D view, selected source image, compact summary, and mini-map in one desktop viewport. It should expand a selected bunch and spread its fruit spheres using image-relative positions rather than uniformly indexed offsets.

## Evidence and implementation sequence

1. Draw a cultivar-specific Figure 2 and record the yellow-halo annotation rule.
2. Label Green Gem detector boxes and the five classifier folders, keeping a route/date-held-out test set.
3. Train a one-class detector with public data only as pretraining, then fine-tune on local cube-face views.
4. Train the five-class classifier, including hard `other` crops.
5. Report detector and per-class classifier metrics on the untouched route/date split, especially harvest-ready false positives and false negatives.
6. Replace legacy weights only after this gate; preserve their provenance separately.
7. Add measured synchronized pose/range data before claiming physical fruit mapping or unique-fruit tracking.
