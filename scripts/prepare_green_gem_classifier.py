"""Create a YOLO classification dataset from manually verified fruit crops.

Input CSV columns: image,x1,y1,x2,y2,label,split
`split` must be train or val.  Bounding boxes are in source-image pixels.
"""
from __future__ import annotations

import argparse
import csv
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image


CLASSES = ("immature", "mature_green", "harvest_ready", "overripe_or_defective", "other")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Make Green Gem classifier crops from a verified CSV")
    parser.add_argument("--annotations", required=True, help="CSV with image,x1,y1,x2,y2,label,split")
    parser.add_argument("--images", required=True, help="Directory containing the source images")
    parser.add_argument("--output", required=True, help="New or empty classification dataset directory")
    parser.add_argument("--padding", type=float, default=0.08, help="Relative box padding (0 to 0.5)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0 <= args.padding <= .5:
        raise ValueError("--padding must be between 0 and 0.5")
    image_root, output = Path(args.images), Path(args.output)
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output must be new or empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    counts: Counter[tuple[str, str]] = Counter()
    with Path(args.annotations).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"image", "x1", "y1", "x2", "y2", "label", "split"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV requires: image,x1,y1,x2,y2,label,split")
        for index, row in enumerate(reader, start=2):
            label, split = row["label"].strip(), row["split"].strip()
            if label not in CLASSES or split not in {"train", "val"}:
                raise ValueError(f"Row {index}: label must be one of {CLASSES}; split must be train or val")
            source = image_root / row["image"]
            if not source.is_file():
                raise FileNotFoundError(f"Row {index}: source image not found: {source}")
            with Image.open(source) as image:
                width, height = image.size
                x1, y1, x2, y2 = (float(row[key]) for key in ("x1", "y1", "x2", "y2"))
                pad_x, pad_y = (x2 - x1) * args.padding, (y2 - y1) * args.padding
                crop = image.convert("RGB").crop((max(0, int(x1 - pad_x)), max(0, int(y1 - pad_y)), min(width, int(x2 + pad_x)), min(height, int(y2 + pad_y))))
            if crop.width < 8 or crop.height < 8:
                raise ValueError(f"Row {index}: crop is too small")
            target = output / split / label
            target.mkdir(parents=True, exist_ok=True)
            crop.save(target / f"{source.stem}_{index:05d}.jpg", quality=95)
            counts[(split, label)] += 1
    if not all(counts[(split, label)] for split in ("train", "val") for label in CLASSES):
        missing = [f"{split}/{label}" for split in ("train", "val") for label in CLASSES if not counts[(split, label)]]
        raise ValueError("Every class needs train and val examples; missing: " + ", ".join(missing))
    print("Created classifier crops:")
    for split in ("train", "val"):
        print(split + ": " + ", ".join(f"{label}={counts[(split, label)]}" for label in CLASSES))


if __name__ == "__main__":
    main()
