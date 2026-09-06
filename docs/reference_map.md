# Reference Occupancy Map

`examples/maps/greenhouse_reference.pgm` is a small ROS occupancy-grid example derived from a greenhouse row-map reference image.

It is intended for interface and launch reproducibility:

- white regions represent traversable aisle space;
- dark horizontal bands represent crop rows or occupied structure;
- the map resolution is set to `0.05 m/pixel`;
- the map origin is `[0.0, 0.0, 0.0]`.

This map is not a surveyed greenhouse map and should not be used as quantitative navigation evidence. For manuscript-level navigation validation, replace it with a map generated from the real LiDAR workflow and provide the corresponding pose, TF, and route data.

