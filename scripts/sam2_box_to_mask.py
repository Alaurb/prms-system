#!/usr/bin/env python3
"""Turn YOLO bounding boxes into reviewable SAM 2 fruit masks.

This script creates *candidates*, not maturity labels. Inspect the output crops
before assigning Green Gem maturity classes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True, help="YOLO source-image directory")
    parser.add_argument("--labels", type=Path, required=True, help="YOLO box-label directory")
    parser.add_argument("--output", type=Path, required=True, help="New candidate-output directory")
    parser.add_argument("--checkpoint", type=Path, required=True, help="SAM 2 .pt checkpoint")
    parser.add_argument("--config", default="configs/sam2.1/sam2.1_hiera_s.yaml")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--max-images", type=int, default=0, help="0 means process every labeled image")
    parser.add_argument("--padding", type=float, default=0.15, help="Crop padding as fraction of box size")
    return parser.parse_args()


def yolo_boxes(path: Path, width: int, height: int) -> list[tuple[int, np.ndarray]]:
    boxes: list[tuple[int, np.ndarray]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 5:
            raise ValueError(f"{path}:{line_no}: expected a YOLO box with five fields")
        class_id, cx, cy, box_w, box_h = map(float, fields)
        if not all(0 <= value <= 1 for value in (cx, cy, box_w, box_h)) or box_w == 0 or box_h == 0:
            raise ValueError(f"{path}:{line_no}: invalid normalized box")
        xyxy = np.array(
            [(cx - box_w / 2) * width, (cy - box_h / 2) * height,
             (cx + box_w / 2) * width, (cy + box_h / 2) * height],
            dtype=np.float32,
        )
        boxes.append((int(class_id), xyxy))
    return boxes


def padded_crop(box: np.ndarray, width: int, height: int, padding: float) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    dx, dy = (x2 - x1) * padding, (y2 - y1) * padding
    return max(0, int(np.floor(x1 - dx))), max(0, int(np.floor(y1 - dy))), min(width, int(np.ceil(x2 + dx))), min(height, int(np.ceil(y2 + dy)))


def main() -> None:
    args = parse_args()
    if not args.images.is_dir() or not args.labels.is_dir():
        raise SystemExit("--images and --labels must be existing directories")
    if not args.checkpoint.is_file():
        raise SystemExit(f"Checkpoint not found: {args.checkpoint}")

    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("CUDA was requested but is unavailable")
    args.output.mkdir(parents=True, exist_ok=True)
    for name in ("masks", "crops", "overlays"):
        (args.output / name).mkdir(exist_ok=True)

    model = build_sam2(args.config, str(args.checkpoint), device=args.device)
    predictor = SAM2ImagePredictor(model)
    label_files = sorted(path for path in args.labels.glob("*.txt") if path.stem.lower() != "classes")
    records: list[dict[str, object]] = []
    processed = 0

    for label_path in label_files:
        image_path = next((args.images / f"{label_path.stem}{suffix}" for suffix in IMAGE_SUFFIXES if (args.images / f"{label_path.stem}{suffix}").is_file()), None)
        if image_path is None:
            records.append({"source_label": str(label_path), "status": "skipped_missing_image"})
            continue
        image = np.array(Image.open(image_path).convert("RGB"), copy=True)
        height, width = image.shape[:2]
        boxes = yolo_boxes(label_path, width, height)
        predictor.set_image(image)
        overlay = image.copy()
        for index, (class_id, box) in enumerate(boxes):
            with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=args.device.startswith("cuda")):
                masks, scores, _ = predictor.predict(box=box[None, :], multimask_output=False)
            mask = masks[0].astype(bool)
            name = f"{label_path.stem}__{index:03d}"
            Image.fromarray((mask * 255).astype(np.uint8)).save(args.output / "masks" / f"{name}.png")
            left, top, right, bottom = padded_crop(box, width, height, args.padding)
            rgba = np.dstack((image, (mask * 255).astype(np.uint8)))
            Image.fromarray(rgba).crop((left, top, right, bottom)).save(args.output / "crops" / f"{name}.png")
            overlay[mask] = (0.55 * overlay[mask] + 0.45 * np.array([0, 255, 0])).astype(np.uint8)
            records.append({
                "id": name, "status": "candidate", "source_image": str(image_path),
                "source_label": str(label_path), "source_class_id": class_id,
                "box_xyxy": [round(float(value), 2) for value in box],
                "sam_score": round(float(scores[0]), 6), "mask_pixels": int(mask.sum()),
                "crop": f"crops/{name}.png", "mask": f"masks/{name}.png",
                "maturity_label": None, "review_status": "pending",
            })
        overlay_image = Image.fromarray(overlay)
        draw = ImageDraw.Draw(overlay_image)
        for _, box in boxes:
            draw.rectangle(tuple(box.astype(int)), outline=(255, 0, 0), width=3)
        overlay_image.save(args.output / "overlays" / f"{label_path.stem}.jpg", quality=92)
        processed += 1
        if args.max_images and processed >= args.max_images:
            break

    with (args.output / "manifest.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"processed_images": processed, "records": len(records), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
