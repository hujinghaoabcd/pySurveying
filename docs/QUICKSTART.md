# Quick start

This guide takes pySurveying from installation to a complete adjustment workflow without requiring prior knowledge of the package internals.

## 1. Install

Before the first PyPI release:

```bash
git clone https://github.com/hujinghaoabcd/pySurveying.git
cd pySurveying
python -m pip install -e .
```

For the Streamlit interface:

```bash
python -m pip install -e ".[ui]"
pysurveying-ui
```

For development:

```bash
python -m pip install -e ".[dev,ui]"
```

## 2. Remember the coordinate convention

For local planar surveying helpers:

```text
+Y = North
+X = East
Azimuth = clockwise from North
```

Angles exposed by the surveying API are decimal degrees unless a function explicitly documents another unit.

## 3. Basic coordinate work

```python
from pysurveying import distance, azimuth, forward_coordinate, inverse_coordinate

A = (1000.0, 1000.0)
B = (1100.0, 1050.0)

print(distance(A, B))
print(azimuth(A, B))
print(inverse_coordinate(A, B))
print(forward_coordinate(*A, azimuth_deg=30.0, length=100.0))
```

## 4. Intersection and resection

```python
from pysurveying import forward_intersection, distance_intersection, resection

P = forward_intersection((0, 0), 45.0, (100, 0), 315.0)
print(P)

solutions = distance_intersection((0, 0), 70.710678, (100, 0), 70.710678)
print(solutions)

station = resection(
    known_points=[(0, 0), (100, 0), (100, 100), (0, 100)],
    directions_deg=[225, 135, 45, 315],
)
print(station)
```

## 5. Closed traverse

If side azimuths are already known:

```python
from pysurveying import closed_traverse

result = closed_traverse(
    start=(0.0, 0.0),
    azimuths_deg=[90.0, 0.0, 270.0, 180.0],
    distances=[100.0, 100.0, 100.0, 100.0],
)
print(result["coordinates"])
```

If measured interior angles are the starting point:

```python
from pysurveying import closed_traverse_from_angles

result = closed_traverse_from_angles(
    start=(0.0, 0.0),
    start_azimuth_deg=90.0,
    interior_angles_deg=[90.01, 89.99, 90.02, 89.98],
    distances=[100.02, 99.98, 100.01, 99.99],
)

print(result["angle_adjustment"])
print(result["azimuths"])
print(result["coordinates"])
```

This workflow performs angle closure, azimuth propagation, coordinate-increment computation, and Bowditch coordinate correction.

## 6. Leveling network

```python
from pysurveying import LevelObservation, leveling_network

observations = [
    LevelObservation("BM", "A", 1.0000, sigma=0.0010),
    LevelObservation("A", "B", 2.0000, sigma=0.0020),
    LevelObservation("BM", "B", 3.0010, sigma=0.0015),
]

result = leveling_network(observations, fixed_heights={"BM": 100.0})

print(result.metadata["adjusted_heights"])
print(result.residuals)
print(result.sigma0)
```

Weights are formed from `1 / sigma²`.

## 7. Linear least squares

```python
import numpy as np
from pysurveying import least_squares

A = np.array([[1.0], [1.0], [1.0]])
L = np.array([10.01, 9.99, 10.00])

result = least_squares(A, L)

print(result.parameters)
print(result.residuals)
print(result.metadata["qxx"])
print(result.metadata["qvv"])
print(result.metadata["redundancy"])
```

For independent unequal weights:

```python
P = np.array([1.0, 2.0, 4.0])
result = least_squares(A, L, P=P)
```

A complete symmetric weight matrix may also be supplied for correlated observations.

## 8. 2D control-network adjustment

```python
import math
from pysurveying import Point, Observation, adjust_control_network

points = [
    Point("A", 0.0, 0.0, fixed=True),
    Point("B", 100.0, 0.0, fixed=True),
    Point("C", 0.0, 100.0, fixed=True),
    Point("P", 39.0, 31.0),
]

observations = [
    Observation("distance", "A", "P", 50.0, sigma=0.01),
    Observation("distance", "B", "P", math.hypot(60.0, 30.0), sigma=0.01),
    Observation("distance", "C", "P", math.hypot(40.0, 70.0), sigma=0.01),
]

result = adjust_control_network(points, observations)
print(result.metadata["adjusted_points"])
```

Supported observation kinds:

```text
distance
azimuth
direction
angle
```

`direction` observations at one occupied station share an estimated station-orientation unknown. `azimuth` is an absolute surveying azimuth.

## 9. Inspect quality, not only coordinates

```python
from pysurveying import control_network_quality, control_network_precision

quality = control_network_quality(result, observations)
precision = control_network_precision(result)

for row in quality:
    print(row)

for row in precision:
    print(row)
```

Quality rows include residuals, standardized residuals, redundancy numbers, robust weights when applicable, and flags.

Precision rows include coordinate standard deviations and confidence error ellipses.

## 10. Robust adjustment and gross-error screening

Huber network adjustment:

```python
from pysurveying import adjust_control_network_robust

robust_result = adjust_control_network_robust(points, observations, huber_k=1.5)
```

Iterative ordinary-adjustment screening:

```python
from pysurveying import control_network_data_snooping

report = control_network_data_snooping(
    points,
    observations,
    threshold=3.0,
    max_removals=3,
)

print(report["removed_indices"])
print(report["stopped_reason"])
```

The threshold is a user-selected computational screening threshold; it is not a universal significance-level prescription.

## 11. Coordinate transformations

CRS conversion:

```python
from pysurveying import transform_coordinates

x, y = transform_coordinates(
    118.7969,
    32.0603,
    "EPSG:4326",
    "EPSG:3857",
)
print(x, y)
```

Local ENU:

```python
from pysurveying import geodetic_to_enu

E, N, U = geodetic_to_enu(
    lon=118.7970,
    lat=32.0604,
    height=30.0,
    lon0=118.7969,
    lat0=32.0603,
    height0=25.0,
)
print(E, N, U)
```

## 12. Work from tables

The package includes CSV/Excel helpers for point and observation tables:

```python
import pandas as pd
from pysurveying import points_from_dataframe, observations_from_dataframe

point_table = pd.read_csv("examples/data/control_points.csv")
observation_table = pd.read_csv("examples/data/control_observations.csv")

points = points_from_dataframe(point_table)
observations = observations_from_dataframe(observation_table)
```

Run the complete shipped example-data workflow:

```bash
python examples/example_data_workflow.py
```

## 13. Export results

```python
from pysurveying import export_adjustment_excel

export_adjustment_excel(result, "control_network_adjustment.xlsx")
```

## 14. Use the GUI

```bash
pysurveying-ui
```

The GUI exposes the same compact core workflows and includes built-in textbook examples and downloadable CSV example data.

## Next reading

- [`API.md`](API.md) — public API details
- [`STANDARD_EXAMPLES.md`](STANDARD_EXAMPLES.md) — source-backed and transparent regression cases
- [`VALIDATION.md`](VALIDATION.md) — validation scope
- [`FAQ.md`](FAQ.md) — common questions
