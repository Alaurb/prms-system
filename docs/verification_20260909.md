# Verification — 2026-09-09

- Dataset SHA-256: 58/58 files passed.
- Unit tests: 16/16 passed on Python 3.12.14, numpy 2.5.3 and Pillow 12.3.0.
- Saved replay: 13 frames, 68 observations, 26 frame-side positions. Counts: immature 28, green_mature 31, discoloration 9, mature 0. Output: outputs/replay/index.html.
- Fresh two-stage inference: successfully loaded both supplied weights and processed frame 11.29-panoramic702.0.jpg at the default 1440 face resolution and 1280 detector input, with six-face export enabled. Five observations: immature 1, green_mature 3, discoloration 1, mature 0. Output: outputs/inference_smoke/index.html.
- Fresh inference environment: torch 2.14.0, torchvision 0.29.0, ultralytics 8.4.144. A one-frame smoke verifies operational inference, not independent accuracy or all-frame result equivalence.
- No model training or independent field evaluation was run. The 68 saved observations must not be described as newly inferred in this session.
- Author TeX compiled successfully after updating title, correspondence email and abstract repository link. Existing figure assets remain pending redraw.
- Main implementation commit: ad8c91b. First remote push failed with a connection reset. Check git status -sb / origin before claiming publication.

All local installation and inference processes finished successfully; no running task needs to be inherited. Default mapping remains synthetic/assumed and has no measured fruit-height accuracy guarantee.
