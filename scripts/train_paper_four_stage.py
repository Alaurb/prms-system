"""Train a reproducible four-stage maturity baseline from reviewed crop links.

This utility deliberately accepts only the four labels used in the original
paper: immature-period, green-maturity-period, discoloration-period and
maturity-period.  It groups crops by their source photograph before splitting,
so separate tomatoes from one panorama cannot leak across data splits.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


CLASSES = ("immature-period", "green-maturity-period", "discoloration-period", "maturity-period")


def source_group(path: Path) -> str:
    """Derive a stable source-image group from a SAM2 crop filename."""
    # Labels are allowed to rename the review symlink.  The crop target retains
    # the original acquisition name, so grouping must use the resolved target.
    name = re.sub(r"^batch\d+__", "", path.resolve().stem)
    return re.sub(r"_tomato_\d+$", "", name)


def collect(root: Path):
    records = []
    for label_id, label in enumerate(CLASSES):
        folder = root / label
        if not folder.is_dir():
            raise FileNotFoundError(folder)
        for path in sorted(folder.iterdir()):
            if not path.is_file():
                continue
            try:
                with Image.open(path) as image:
                    image.verify()
            except Exception as exc:
                raise ValueError(f"Unreadable reviewed crop: {path}") from exc
            records.append((path, label_id, source_group(path)))
    if not records:
        raise ValueError("No reviewed crops found")
    return records


def grouped_split(records, seed: int):
    """Greedily allocate complete source groups to 70/15/15 train/val/test."""
    groups = defaultdict(list)
    for item in records:
        groups[item[2]].append(item)
    rng = random.Random(seed)
    ordered = list(groups.items())
    rng.shuffle(ordered)
    ordered.sort(key=lambda item: len(item[1]), reverse=True)
    total = Counter(label for _, label, _ in records)
    targets = {name: {label: total[label] * ratio for label in range(len(CLASSES))}
               for name, ratio in (("train", .70), ("val", .15), ("test", .15))}
    allocations = {name: [] for name in targets}
    counts = {name: Counter() for name in targets}
    for _, members in ordered:
        contribution = Counter(label for _, label, _ in members)
        def cost(split):
            return sum(max(0, counts[split][label] + contribution[label] - targets[split][label]) ** 2
                       for label in contribution)
        split = min(targets, key=cost)
        allocations[split].extend(members)
        counts[split].update(contribution)
    missing = [f"{split}/{CLASSES[label]}" for split in allocations for label in range(len(CLASSES))
               if not counts[split][label]]
    if missing:
        raise ValueError("Group split left an empty class: " + ", ".join(missing))
    return allocations, counts


class CropDataset(Dataset):
    def __init__(self, records, transform):
        self.records, self.transform = records, transform
    def __len__(self): return len(self.records)
    def __getitem__(self, index):
        path, label, _ = self.records[index]
        with Image.open(path) as image:
            return self.transform(image.convert("RGB")), label


def evaluate(model, loader, device):
    matrix = torch.zeros((len(CLASSES), len(CLASSES)), dtype=torch.int64)
    model.eval()
    with torch.no_grad():
        for images, labels in loader:
            predicted = model(images.to(device)).argmax(1).cpu()
            for truth, prediction in zip(labels, predicted):
                matrix[truth, prediction] += 1
    correct, total = matrix.diag().sum().item(), matrix.sum().item()
    per_class = []
    for index, label in enumerate(CLASSES):
        tp, support = matrix[index, index].item(), matrix[index].sum().item()
        predicted = matrix[:, index].sum().item()
        precision = tp / predicted if predicted else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class.append(dict(label=label, support=support, precision=precision, recall=recall, f1=f1))
    return dict(accuracy=correct / total if total else 0.0, confusion_matrix=matrix.tolist(), per_class=per_class)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--seed", type=int, default=20260914)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Output must be new: {args.output}")
    torch.manual_seed(args.seed); random.seed(args.seed)
    records = collect(args.review_root.resolve())
    splits, counts = grouped_split(records, args.seed)
    args.output.mkdir(parents=True)
    normalise = transforms.Normalize((.485, .456, .406), (.229, .224, .225))
    train_tf = transforms.Compose([transforms.Resize((args.image_size, args.image_size)), transforms.RandomHorizontalFlip(), transforms.ColorJitter(.12, .12, .08), transforms.ToTensor(), normalise])
    eval_tf = transforms.Compose([transforms.Resize((args.image_size, args.image_size)), transforms.ToTensor(), normalise])
    loaders = {name: DataLoader(CropDataset(rows, train_tf if name == "train" else eval_tf), batch_size=args.batch_size,
                                shuffle=name == "train", num_workers=4, pin_memory=True)
               for name, rows in splits.items()}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES)); model.to(device)
    class_count = torch.tensor([counts["train"][i] for i in range(len(CLASSES))], dtype=torch.float)
    criterion = nn.CrossEntropyLoss(weight=(class_count.sum() / (len(CLASSES) * class_count)).to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    best, history = -1.0, []
    for epoch in range(1, args.epochs + 1):
        model.train(); loss_sum = n = 0
        for images, labels in loaders["train"]:
            optimizer.zero_grad(); logits = model(images.to(device)); loss = criterion(logits, labels.to(device)); loss.backward(); optimizer.step()
            loss_sum += loss.item() * len(labels); n += len(labels)
        val = evaluate(model, loaders["val"], device)
        history.append(dict(epoch=epoch, train_loss=loss_sum / n, val_accuracy=val["accuracy"]))
        print(f"epoch={epoch:03d} loss={loss_sum/n:.4f} val_accuracy={val['accuracy']:.4f}", flush=True)
        if val["accuracy"] > best:
            best = val["accuracy"]; torch.save({"state_dict": model.state_dict(), "classes": CLASSES, "image_size": args.image_size}, args.output / "best.pt")
    checkpoint = torch.load(args.output / "best.pt", map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["state_dict"])
    report = {"schema": "prms.paper_four_stage_baseline.v1", "classes": CLASSES, "seed": args.seed,
              "device": str(device), "counts": {key: dict(value) for key, value in counts.items()},
              "groups": {key: len({item[2] for item in value}) for key, value in splits.items()},
              "history": history, "validation": evaluate(model, loaders["val"], device), "test": evaluate(model, loaders["test"], device)}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["test"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
