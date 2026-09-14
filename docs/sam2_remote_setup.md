# SAM 2 remote deployment and candidate generation

Deployment target: an Ubuntu workstation with the project stored at `$PRMS_REMOTE_ROOT`. Keep its host address, username, and credentials out of this repository.

- Conda environment: `prms-sam2` (Python 3.10)
- Official SAM 2 sparse-source checkout: `tools/sam2`, commit `2b90b9f`
- Official checkpoint: `models/sam2/sam2.1_hiera_small.pt` (176 MiB)
- Candidate generator: `scripts/sam2_box_to_mask.py`
- GPU smoke test: RTX A4500 Laptop GPU; box-prompt score 0.90625 on an existing tomato image.

The generator treats YOLO boxes as prompts. Its results are **review candidates**: they have no maturity ground truth and must not be used to claim Green Gem classification performance before human review and labeling.

## Run a small review batch

```bash
conda activate prms-sam2

python "$PRMS_REMOTE_ROOT/scripts/sam2_box_to_mask.py" \
  --images "$PRMS_REMOTE_ROOT/yolo-v8/tomato_seg/images/train" \
  --labels "$PRMS_REMOTE_ROOT/yolo-v8/tomato_seg/labels/train" \
  --output "$PRMS_REMOTE_ROOT/outputs/sam2_candidates_batch01" \
  --checkpoint "$PRMS_REMOTE_ROOT/models/sam2/sam2.1_hiera_small.pt" \
  --max-images 20
```

Outputs include alpha-masked fruit crops, binary masks, full-image overlays, and `manifest.jsonl`. Review each candidate, then fill in `maturity_label` using the project taxonomy (`immature`, `mature_green`, `harvest_ready`, `overripe_or_defective`) and set a review decision. Exclude repeated views of the same fruit from crossing train/validation/test boundaries.
