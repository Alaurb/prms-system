# Green Gem maturity review workspace

This directory is a manual-review queue, not a training dataset. The PNG files
in its root are symbolic links to SAM2 alpha-crop candidates. Moving a link does
not change the original crop or mask.

Move each reviewed link into exactly one of these four paper-defined categories:

- immature: clearly immature fruit.
- mature-green: mature green fruit without the field-defined yellow halo.
- harvest-ready: fruit with the field-defined yellow halo.
- overripe-or-defective: defective, overripe, diseased, or otherwise
  unsuitable fruit.

Do not rename the candidate id. Leave an uncertain candidate in the root until
it can be decided; it is not a fifth class. Review source metadata in
.metadata/source_candidates.jsonl when an image needs context. A later dataset
export will use only these four classes.
