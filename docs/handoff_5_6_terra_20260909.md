# PRMS handoff to 5.6-terra — 2026-09-09

## Current user direction

The repository serves the manuscript. Its scope has been explicitly narrowed to offline panoramic tomato detection, ripeness classification, and spatial observation mapping. Navigation, SLAM, locomotion, gait switching and navigation demonstrations have been removed from the active repository. Preserve external pose/range interfaces. Do not resume the old navigation roadmap.

The user wants to revise the manuscript first; figure assets are to be redrawn by the user following the supplied instructions. Do not invent empirical results or describe proposed controls as historical implementations.

## Completed

- Commit ad8c91b: replaced the ROS/navigation scaffold with the author's existing panorama-processing package.
- Imported 13 panoramas (702–714), detector and classifier weights, reference map, saved predictions, annotated images, benchmark records and metadata.
- Imported projection, two-stage inference, assumed/measured-range projection, conservative association, HTML reporting, replay and evaluation scripts.
- Preserved ROS message schemas under interfaces/ros_msgs; external data contracts are documented in docs/interfaces.md.
- Added a 58-file SHA-256 manifest and scripts/verify_dataset.py. Evidence files retain exact bytes via .gitattributes to prevent line-ending conversion invalidating hashes.
- Preserved original license and imported code/data terms separately.
- Rewrote README, provenance and paper-requirement coverage.
- Original preprint stays unchanged; docs/paper/root.tex is a snapshot of the revised author source, not a standalone compilation package.

## Manuscript

Title now only removes “Efficient” from the original:
Ripeness Monitoring in Open-Facility Environments Using a Quadruped Robot and Panoramic AI Recognition.

Authors: Jinru Lyu, Zihan Wang, Shuhan Shi, Zhenfeng Xue, Zhonghua Miao.
Co-corresponding authors: Zhenfeng Xue (zfxue0903@shu.edu.cn) and Zhonghua Miao (zhhmiao@shu.edu.cn).
The user's repeated escaped email was normalized to one address.
Abstract contains https://github.com/Alaurb/prms-system and states the repository's detection/mapping scope.
Navigation remains part of the paper's historical field context; the user's removal request applied to repository implementation.

The major text revision:
- distinguishes offline recognition from field navigation;
- describes six-face reprojection and two-view/two-stage inference;
- distinguishes observation counts, frame-side groups and physical fruits/plants;
- qualifies synthetic pose and assumed row-plane mapping;
- includes archived development-validation numbers with limitations;
- leaves AUTHOR CHECK comments for unverified original training settings, gait-switch triggers, camera geometry and field failure handling.
The correspondence email is no longer pending.

All ten figure assets remain the originals. Captions were revised; figure-content/text consistency is pending user redraw. Do not claim the PDF is submission-ready.

## Verification already completed

- Python 3.12.14 virtual environment at .venv; system default Python 3.13 lacks required packages.
- requirements.txt installed: numpy 2.5.3, Pillow 12.3.0.
- All 16 unit tests passed.
- Dataset integrity: all 58 manifest entries passed.
- Actual replay generated outputs/replay/index.html: 13 frames, 68 observations, 26 frame-side positions; 28 immature, 31 green mature, 9 discoloration, 0 mature.
- Manuscript compiled with pdflatex using the existing local MDPI template to root_text_revision.pdf. Layout/figure redraw is not finished.
- Git whitespace validation passes with cr-at-eol enabled for byte-preserved evidence:
  git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check
- Optional inference dependencies installed successfully: torch 2.14.0, torchvision 0.29.0, ultralytics 8.4.144. This is a fresh environment, not the historical benchmark environment.

## Commands

From repository root (Windows):
.\.venv\Scripts\python.exe scripts/verify_dataset.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/replay_observations.py --source demo --output outputs/replay
.\.venv\Scripts\python.exe demo.py --input data/panoramas --map assets/farm_map.jpg --output outputs/inference_smoke --detector two-stage --detector-weights models/tomato_detector.pt --classifier-weights models/tomato_ripeness_classifier.pt --export-six-faces --max-frames 1

For all 13 panoramas, use --max-frames 0 and a fresh output directory.

## Scientific boundaries

- Default sample coordinates are synthetic/assumed, not measured greenhouse fruit coordinates.
- Pose CSV is already-matched CAMERA optical-centre pose, metres and yaw radians, roll/pitch assumed zero. No raw timestamp interpolation or general 6-DoF transform is implemented.
- Range arrays must already be calibrated, registered radial distance, not raw RGB-D z-depth. Timestamp checks validate supplied metadata, not actual sensor provenance.
- Range-band filtering and greedy associations are candidates, not proof of nearest-row exclusion or unique fruit identity.
- Bounding boxes retain pixel-height information; geometric height is estimated.
- plants.csv is a legacy filename for frame-side proxies.
- The archived evaluation split was used for model selection. It is not an independent test set; evaluation images are not included.
- The initial audit incorrectly inferred no perception implementation existed from prms-system alone. The separate author demo was subsequently inspected and imported. Use the current code, not the earlier scaffold-only assessment.

## Remote status

A push of ad8c91b to origin/main failed with:
fatal: unable to access 'https://github.com/Alaurb/prms-system.git/': Recv failure: Connection was reset

Local changes are committed; do not claim the remote is current without verification.
After network recovery, inspect git status -sb and git log, then push normally. Never force push.
The original navigation code including uncommitted changes was moved to a local backup outside the repository. Its location is recorded in the local handoff companion. Do not re-add it to this narrowed repository.

## Next priorities

1. Check final inference-smoke outcome in the verification note; if failed, resolve that exact failure.
2. Verify Git status and publish the pending normal commits once connectivity works.
3. Reconcile current checkpoint hashes with historical benchmark/figure provenance before asserting exact rerun equivalence.
4. Review the major manuscript wording with the author; retain the original research focus while accurately identifying missing evidence.
5. Update manuscript source snapshot whenever the author source changes.
6. Assist with reviewer-response revisions and user-redrawn figures.
7. With new panorama images, prioritize independent labels and per-class evaluation. Do not fabricate depth, real trajectories or navigation metrics.

