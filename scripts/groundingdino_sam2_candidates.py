#!/usr/bin/env python3
"""Propose tomato instances with Grounding DINO, then segment each with SAM 2.

The generated records are candidates for human review only.  They deliberately
do not infer a Green Gem maturity class or claim any detection accuracy.
""" 
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

# Grounding DINO uses a local cached BERT model on the target workstation.
# Set these before importing it so a reproducible run does not need the network.
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import numpy as np
from PIL import Image, ImageDraw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dino-config", type=Path, required=True)
    parser.add_argument("--dino-checkpoint", type=Path, required=True)
    parser.add_argument("--sam-checkpoint", type=Path, required=True)
    parser.add_argument("--sam-config", default="configs/sam2.1/sam2.1_hiera_s.yaml")
    parser.add_argument("--caption", default="tomato.", help="Grounding DINO text prompt")
    parser.add_argument("--box-threshold", type=float, default=0.20)
    parser.add_argument("--text-threshold", type=float, default=0.20)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--padding", type=float, default=0.15)
    return parser.parse_args()


def normalized_cxcywh_to_xyxy(box: np.ndarray, width: int, height: int) -> np.ndarray:
    cx, cy, box_width, box_height = box.astype(float)
    return np.array(
        [(cx - box_width / 2) * width, (cy - box_height / 2) * height,
         (cx + box_width / 2) * width, (cy + box_height / 2) * height],
        dtype=np.float32,
    )


def padded_crop(box: np.ndarray, width: int, height: int, padding: float) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    dx, dy = (x2 - x1) * padding, (y2 - y1) * padding
    return (max(0, int(np.floor(x1 - dx))), max(0, int(np.floor(y1 - dy))),
            min(width, int(np.ceil(x2 + dx))), min(height, int(np.ceil(y2 + dy))))


def main() -> None:
    args = parse_args()
    for path in (args.image, args.dino_config, args.dino_checkpoint, args.sam_checkpoint):
        if not path.is_file():
            raise SystemExit(f"Required file not found: {path}")
    if not 0 <= args.box_threshold <= 1 or not 0 <= args.text_threshold <= 1:
        raise SystemExit("Detection thresholds must be in [0, 1]")

    import cv2
    import torch
    from groundingdino.util.inference import load_image, load_model, predict
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("CUDA was requested but is unavailable")
    args.output.mkdir(parents=True, exist_ok=True)
    for name in ("masks", "crops"):
        (args.output / name).mkdir(exist_ok=True)

    started = time.perf_counter()
    source_rgb, dino_image = load_image(str(args.image))
    height, width = source_rgb.shape[:2]
    detector = load_model(str(args.dino_config), str(args.dino_checkpoint), device=args.device)
    boxes, logits, phrases = predict(
        model=detector, image=dino_image, caption=args.caption,
        box_threshold=args.box_threshold, text_threshold=args.text_threshold, device=args.device,
    )
    dino_boxes = [normalized_cxcywh_to_xyxy(box.numpy(), width, height) for box in boxes]
    # Release the detector before loading SAM 2: this keeps the combined workflow
    # usable on the 16-GB field workstation GPU.
    del detector
    if args.device.startswith("cuda"):
        torch.cuda.empty_cache()

    sam_model = build_sam2(args.sam_config, str(args.sam_checkpoint), device=args.device)
    predictor = SAM2ImagePredictor(sam_model)
    predictor.set_image(source_rgb)
    overlay = source_rgb.copy()
    records: list[dict[str, object]] = []
    stem = args.image.stem
    for index, (box, logit, phrase) in enumerate(zip(dino_boxes, logits, phrases)):
        with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=args.device.startswith("cuda")):
            masks, sam_scores, _ = predictor.predict(box=box[None, :], multimask_output=False)
        mask = masks[0].astype(bool)
        candidate_id = f"{stem}__{index:03d}"
        Image.fromarray((mask * 255).astype(np.uint8)).save(args.output / "masks" / f"{candidate_id}.png")
        left, top, right, bottom = padded_crop(box, width, height, args.padding)
        rgba = np.dstack((source_rgb, (mask * 255).astype(np.uint8)))
        Image.fromarray(rgba).crop((left, top, right, bottom)).save(args.output / "crops" / f"{candidate_id}.png")
        overlay[mask] = (0.55 * overlay[mask] + 0.45 * np.array([0, 255, 0])).astype(np.uint8)
        records.append({
            "id": candidate_id, "status": "candidate_unreviewed", "source_image": str(args.image),
            "prompt": args.caption, "dino_phrase": phrase, "dino_score": round(float(logit), 6),
            "box_xyxy": [round(float(value), 2) for value in box],
            "sam_score": round(float(sam_scores[0]), 6), "mask_pixels": int(mask.sum()),
            "crop": f"crops/{candidate_id}.png", "mask": f"masks/{candidate_id}.png",
            "maturity_label": None, "review_status": "pending",
        })

    overlay_image = Image.fromarray(overlay)
    draw = ImageDraw.Draw(overlay_image)
    for box in dino_boxes:
        draw.rectangle(tuple(box.astype(int)), outline=(255, 70, 70), width=3)
    overlay_image.save(args.output / "overlay.jpg", quality=92)
    with (args.output / "manifest.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"candidates": len(records), "output": str(args.output), "seconds": round(time.perf_counter() - started, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
