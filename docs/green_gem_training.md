# Green Gem maturity model: data and training protocol

## Production label schema

The project measures visual harvest maturity of the Green Gem cultivar. It is not a generic red-tomato colour classifier.

| Directory / output label | Field definition |
| --- | --- |
| `immature` | Small or dark-green fruit; not fully developed and without a yellow halo. |
| `mature_green` | Fruit is fully formed and green, but has no stable yellow halo; do not harvest. |
| `harvest_ready` | Green fruit with a stable yellow/yellow-green halo that meets the grower's harvest rule. |
| `overripe_or_defective` | Excessive yellowing or softening, cracking, disease signs, or another non-marketable condition. |
| `other` | A non-fruit crop: leaf, stem, reflection, background, or an unusable occluded crop. This is a classifier negative class, not a reported maturity outcome. |

The yellow-halo rule is a visual proxy. Each training label must be verified against the field team's harvest decision. If available, retain fruit diameter, days after anthesis, firmness, and Brix as annotation metadata; do not use them as labels unless they were actually measured.

## Data separation

Split by route and capture date, never randomly by crop. All views of a panorama, and all crops of the same fruit/plant, must stay in one split. Keep a final test route completely untouched until model selection is finished.

Public red-tomato data may be used to pretrain a one-class `tomato` detector. It must not provide the four Green Gem maturity labels. Do not redistribute source images from third-party datasets in this repository; follow each source licence.

## Detector dataset

Prepare a standard YOLO detection dataset with one class named `tomato` and create `training/green_gem_detector.yaml` from the template below:

```yaml
path: C:/path/to/green_gem_detector
train: images/train
val: images/val
names:
  0: tomato
```

Train it with:

```powershell
python scripts/train_green_gem.py --task detect --data training/green_gem_detector.yaml --model yolo11s.pt --imgsz 1280 --epochs 160
```

## Classifier dataset

The classifier uses five directories because `other` is necessary to reject non-fruit crops:

```text
data/training/green_gem_classifier/
  train/{immature,mature_green,harvest_ready,overripe_or_defective,other}/
  val/{immature,mature_green,harvest_ready,overripe_or_defective,other}/
```

Use `scripts/prepare_green_gem_classifier.py` to make crops from verified boxes. Its input CSV has this header:

```csv
image,x1,y1,x2,y2,label,split
panorama_001_left.jpg,120,80,220,190,harvest_ready,train
```

Then train:

```powershell
python scripts/train_green_gem.py --task classify --data data/training/green_gem_classifier --model yolo11s-cls.pt --imgsz 224 --epochs 120
```

The classifier's folder names are its deployed class names. Do not rename them after training. Copy only the resulting `best.pt` weights into `models/` and point the desktop window to the detector and classifier files.

## Deployment gate

Before replacing the repository's archived weights, record detector precision/recall/mAP and classifier per-class precision, recall, F1, and confusion matrix on the held-out route. In particular, report `harvest_ready` false positives and false negatives. Do not compare the archived red-tomato metrics with the new Green Gem model.
