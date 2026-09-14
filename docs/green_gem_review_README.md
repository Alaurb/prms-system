# Green Gem maturity review workspace

This directory is a manual-review queue, not a training dataset. The files in
00_inbox are symbolic links to SAM2 alpha-crop candidates. Moving a link does
not change the original crop or mask.

Move each link to exactly one destination:

- 01_immature: clearly immature fruit.
- 02_mature_green: mature green fruit without the field-defined yellow halo.
- 03_harvest_ready: fruit with the field-defined yellow halo.
- 04_overripe_or_defective: defective, overripe, diseased, or otherwise
  unsuitable fruit.
- 05_reject_non_tomato_or_bad_mask: false detection, unusable crop, or failed
  mask.
- 06_uncertain: keep ambiguous samples here; do not force a label.

Do not rename the candidate id. Review source metadata in
manifests/source_candidates.jsonl when an image needs context. A later dataset
export will use only the four numbered fruit classes and will exclude reject and
uncertain links.
