# Orchard research workspace

This repository tracks only source code, small configuration files, documentation
and asset summaries for this workstation. It intentionally excludes raw sensor
data, ROS bags, image collections, model weights, virtual environments, ROS
build products, experiment outputs and archive packages.

Read WORKSPACE.md before moving or relabelling existing files. Use
python scripts/create_workspace_inventory.py after a material change to refresh
metadata/asset_inventory.csv. The inventory records top-level size and file-count
summaries only; it is not a checksum manifest.

For a reproducible training dataset, create a separate immutable manifest with
relative paths, source, licence, labels, split assignment and SHA-256 values.
