#!/usr/bin/env python3
"""Brighten dark images, then create Grounding DINO + SAM2 review candidates."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import cv2
import numpy as np
from PIL import Image, ImageDraw


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--images", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--dino-config", type=Path, required=True)
    p.add_argument("--dino-checkpoint", type=Path, required=True)
    p.add_argument("--sam-checkpoint", type=Path, required=True)
    p.add_argument("--sam-config", default="configs/sam2.1/sam2.1_hiera_s.yaml")
    p.add_argument("--max-images", type=int, default=60)
    p.add_argument("--box-threshold", type=float, default=0.15)
    p.add_argument("--text-threshold", type=float, default=0.20)
    p.add_argument("--gamma", type=float, default=0.72)
    p.add_argument("--device", default="cuda")
    return p.parse_args()


def brighten(image: np.ndarray, gamma: float) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lab[:, :, 0])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    table = np.array([((value / 255.0) ** gamma) * 255 for value in range(256)], dtype=np.uint8)
    return cv2.LUT(enhanced, table)


def xyxy(box: list[float], width: int, height: int) -> np.ndarray:
    cx, cy, bw, bh = box
    return np.array([(cx - bw / 2) * width, (cy - bh / 2) * height,
                     (cx + bw / 2) * width, (cy + bh / 2) * height], dtype=np.float32)


def main() -> None:
    a = args()
    import torch
    from groundingdino.util.inference import load_image, load_model, predict
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor

    files = sorted(p for p in a.images.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if a.max_images:
        files = files[:a.max_images]
    if not files:
        raise SystemExit("No images found")
    for name in ("enhanced", "crops", "masks", "overlays"):
        (a.output / name).mkdir(parents=True, exist_ok=True)

    proposals = []
    detector = load_model(str(a.dino_config), str(a.dino_checkpoint), device=a.device)
    for source_path in files:
        raw = cv2.imread(str(source_path))
        if raw is None:
            continue
        enhanced = brighten(raw, a.gamma)
        enhanced_path = a.output / "enhanced" / source_path.name
        cv2.imwrite(str(enhanced_path), enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])
        source_rgb, tensor = load_image(str(enhanced_path))
        boxes, logits, phrases = predict(detector, tensor, "tomato.", a.box_threshold, a.text_threshold, a.device)
        proposals.append({"source": str(source_path), "enhanced": str(enhanced_path),
                          "mean_before": round(float(cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY).mean()), 2),
                          "mean_after": round(float(cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY).mean()), 2),
                          "boxes": [box.tolist() for box in boxes],
                          "dino_scores": [round(float(v), 6) for v in logits],
                          "phrases": phrases})
    del detector
    if a.device.startswith("cuda"):
        torch.cuda.empty_cache()

    predictor = SAM2ImagePredictor(build_sam2(a.sam_config, str(a.sam_checkpoint), device=a.device))
    records = []
    for item in proposals:
        image = np.array(Image.open(item["enhanced"]).convert("RGB"))
        height, width = image.shape[:2]
        predictor.set_image(image)
        overlay = image.copy()
        for index, (box0, score, phrase) in enumerate(zip(item["boxes"], item["dino_scores"], item["phrases"])):
            box = xyxy(box0, width, height)
            with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=a.device.startswith("cuda")):
                masks, sam_scores, _ = predictor.predict(box=box[None, :], multimask_output=False)
            mask = masks[0].astype(bool)
            candidate = f"{Path(item['source']).stem}__{index:03d}"
            Image.fromarray((mask * 255).astype(np.uint8)).save(a.output / "masks" / f"{candidate}.png")
            x1, y1, x2, y2 = np.clip(box.astype(int), [0, 0, 0, 0], [width, height, width, height])
            pad_x, pad_y = max(4, int((x2 - x1) * .15)), max(4, int((y2 - y1) * .15))
            crop = np.dstack((image, (mask * 255).astype(np.uint8)))
            Image.fromarray(crop).crop((max(0, x1-pad_x), max(0, y1-pad_y), min(width, x2+pad_x), min(height, y2+pad_y))).save(a.output / "crops" / f"{candidate}.png")
            overlay[mask] = (0.55 * overlay[mask] + .45 * np.array([0, 255, 0])).astype(np.uint8)
            records.append({"id": candidate, "status": "candidate_unreviewed", "source_image": item["source"],
                            "enhanced_image": item["enhanced"], "mean_before": item["mean_before"], "mean_after": item["mean_after"],
                            "dino_score": score, "dino_phrase": phrase, "box_xyxy": [round(float(v), 2) for v in box],
                            "sam_score": round(float(sam_scores[0]), 6), "maturity_label": None, "review_status": "pending"})
        out = Image.fromarray(overlay)
        draw = ImageDraw.Draw(out)
        for box0 in item["boxes"]:
            draw.rectangle(tuple(xyxy(box0, width, height).astype(int)), outline=(255, 70, 70), width=3)
        out.save(a.output / "overlays" / Path(item["source"]).name, quality=92)
    with (a.output / "manifest.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"images": len(proposals), "candidates": len(records), "output": str(a.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
