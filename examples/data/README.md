# Example data

These small CSV files are intentionally human-readable and are used by the runnable examples, documentation, GUI defaults, and regression tests.

## Files

- `control_points.csv` — three fixed control points and one approximate unknown point.
- `control_observations.csv` — redundant distance observations for the 2D control-network example.
- `leveling_fixed.csv` — fixed benchmark heights for the leveling-network example.
- `leveling_observations.csv` — redundant height-difference observations with unequal standard deviations.
- `traverse_angles.csv` — measured interior angles and side lengths for a closed traverse.
- `common_points.csv` — common points for a 2D similarity/affine transformation example.

## Conventions

Planar coordinates follow the package convention: `+Y` is north, `+X` is east, and surveying azimuth is measured clockwise from north. Angle values are decimal degrees. Distance, coordinate, height and standard-deviation fields must use consistent linear units within one calculation.

These datasets are compact validation/teaching examples, not legal survey records or instrument manufacturer certification datasets.
