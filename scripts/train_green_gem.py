"""Train Green Gem detector or classifier using the installed Ultralytics package."""
from __future__ import annotations

import argparse
from pathlib import Path


GREEN_GEM_CLASSES = ("immature", "mature_green", "harvest_ready", "overripe_or_defective", "other")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a Green Gem tomato model")
    parser.add_argument("--task", required=True, choices=("detect", "classify"))
    parser.add_argument("--data", required=True, help="YOLO detect YAML or classification dataset root")
    parser.add_argument("--model", default="yolo11s.pt", help="Pretrained Ultralytics model")
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--batch", type=int, default=-1, help="-1 selects automatic batch size")
    parser.add_argument("--project", default="runs/green_gem")
    parser.add_argument("--name", default=None)
    return parser.parse_args()


def _check_classifier_layout(root: Path) -> None:
    missing = [str(root / split / label) for split in ("train", "val") for label in GREEN_GEM_CLASSES if not (root / split / label).is_dir()]
    if missing:
        raise ValueError("Classifier dataset must contain all Green Gem class folders; missing: " + ", ".join(missing))


def main() -> None:
    args = parse_args()
    data = Path(args.data)
    if args.task == "detect" and not data.is_file():
        raise FileNotFoundError("--data must be a detection YAML file")
    if args.task == "classify":
        if not data.is_dir():
            raise FileNotFoundError("--data must be a classification dataset directory")
        _check_classifier_layout(data)
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError("Install optional-requirements.txt before training") from exc
    model = YOLO(args.model)
    result = model.train(data=str(data), epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, project=args.project, name=args.name)
    print(f"Training complete. Results: {result.save_dir}")
    print("Before deployment, validate on a route/date held out from all training images.")


if __name__ == "__main__":
    main()
