# pySurveying

A lightweight Python toolkit for surveying computation, least-squares adjustment, quality control, coordinate transformation, and visualization.

> 轻量级 Python 测量计算、测量平差与可视化工具包。

## Current version

**0.2.0**

pySurveying deliberately stays small. It is intended for common surveying calculations, teaching examples, engineering data checks, and small control-network adjustment rather than as a replacement for a full geodetic production system.

## Features

- angle conversion and normalization
- distance, surveying azimuth, coordinate forward/inverse calculation
- forward intersection, distance intersection and resection
- closed and connected traverse adjustment
- angular-closure adjustment and closed traverse from measured interior angles
- leveling-route adjustment
- weighted least-squares leveling-network adjustment
- weighted linear least-squares adjustment
- small 2D control-network adjustment using distance, direction/azimuth and angle observations
- final-linearization `Qxx`, `Qvv`, redundancy numbers and per-observation quality tables for 2D control networks
- iterative control-network gross-error localization with original observation indices preserved
- minimum-norm 2D free-network adjustment
- Huber robust linear adjustment
- Huber robust control-network adjustment
- Huber / IGG1 / IGG3 equivalent-weight robust linear adjustment
- standardized residual screening, redundancy numbers and practical data snooping
- 2D confidence error ellipses
- CRS transformations through `pyproj`
- WGS84 geodetic / ECEF / local ENU transformations
- polar stakeout, straight-line offset, chainage/offset, slope, grade elevation and area
- CSV, Excel, LandXML point and Leica GSI word import helpers
- Excel adjustment export including residual-quality diagnostics when available
- lightweight Streamlit interface

The mathematical organization follows the classical surveying-adjustment workflow represented by *测量平差程序设计*, while NumPy/SciPy are used for numerical linear algebra instead of reimplementing low-level matrix routines.

## Coordinate and angle conventions

For the local planar surveying helpers in `basic.py`, `traverse.py` and `engineering.py`:

- coordinates are stored as `(x, y)`
- `+Y` is treated as north and `+X` as east
- surveying azimuth is measured clockwise from north
- angles passed to public surveying helpers are in decimal degrees unless documented otherwise
- distances and coordinate values must use the same linear unit

For CRS transformations, pyproj conventions apply. `transform_coordinates(..., always_xy=True)` uses longitude/easting first and latitude/northing second.

## Install

```bash
pip install -e .
```

Visual interface:

```bash
pip install -e ".[ui]"
pysurveying-ui
```

Development:

```bash
pip install -e ".[dev,ui]"
python -m pytest
python -m ruff check src tests examples
python -m build
```

## Quick start

```python
from pysurveying import Point, azimuth, distance, forward_coordinate

p1 = Point("A", 1000.0, 1000.0)
p2 = Point("B", 1100.0, 1050.0)

print(distance(p1, p2))
print(azimuth(p1, p2))
print(forward_coordinate(p1.x, p1.y, 30.0, 100.0))
```

### Weighted least squares

```python
import numpy as np
from pysurveying import data_snooping, least_squares

A = np.array([[1.0], [1.0], [1.0], [1.0]])
L = np.array([10.01, 9.99, 10.00, 10.03])
result = least_squares(A, L)

print(result.parameters)
print(result.residuals)
print(result.sigma0)
print(data_snooping(result))
```

### Closed traverse from measured angles

```python
from pysurveying import closed_traverse_from_angles

result = closed_traverse_from_angles(
    start=(0.0, 0.0),
    start_azimuth_deg=90.0,
    interior_angles_deg=[90.01, 89.99, 90.02, 89.98],
    distances=[100.0, 100.0, 100.0, 100.0],
)

print(result["angle_adjustment"])
print(result["coordinates"])
```

### Leveling network

```python
from pysurveying import LevelObservation, leveling_network

observations = [
    LevelObservation("BM", "A", 1.002, sigma=0.001),
    LevelObservation("A", "B", 0.500, sigma=0.001),
    LevelObservation("BM", "B", 1.503, sigma=0.001),
]

result = leveling_network(observations, {"BM": 10.000})
print(result.metadata["adjusted_heights"])
```

### 2D control network

```python
import math
from pysurveying import (
    Observation,
    Point,
    adjust_control_network,
    control_network_quality,
)

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
print(control_network_quality(result, observations))
```

For Huber robust weighting, use `adjust_control_network_robust(...)`. For repeated standardized-residual screening and re-adjustment, use `control_network_data_snooping(...)`. The latter is a practical computational gross-error search; the threshold remains the caller's statistical/design choice.

A runnable quality-control example is provided in `examples/control_network_quality.py`.

### Coordinate transformation and ENU

```python
from pysurveying import geodetic_to_enu, transform_coordinates

x, y = transform_coordinates(118.7969, 32.0603, "EPSG:4326", "EPSG:3857")

e, n, u = geodetic_to_enu(
    118.7970,
    32.0604,
    30.0,
    118.7969,
    32.0603,
    25.0,
)
```

## Package structure

```text
src/pysurveying/
├── models.py       # Point / observations / AdjustmentResult
├── basic.py        # angles, coordinates, intersections, resection
├── traverse.py     # traverse and angular closure
├── leveling.py     # leveling route and network
├── adjustment.py   # least squares and 2D control networks
├── quality.py      # robust estimation, network quality, data snooping, ellipses
├── transform.py    # CRS / ECEF / ENU transformations
├── engineering.py  # stakeout, offsets, slopes, grade, area
├── io.py           # CSV / XLSX / LandXML / GSI and result export
├── ui.py           # command entry point
└── webapp.py       # Streamlit interface
```

## Design rules

1. Small functional API instead of a deep class hierarchy.
2. Core algorithms remain independent from the UI.
3. Adjustment results expose residuals, covariance and quality-control metadata.
4. Existing numerical/geodetic libraries are reused when they already solve the low-level problem well.
5. Instrument readers are separated from adjustment algorithms.
6. pySurveying does not try to replace GIS, GNSS PPP/RTK processing, photogrammetry, SLAM or point-cloud software.

## Current limitations

The package is still an early implementation. The control-network solver is aimed at small 2D networks, and its `Qxx`/`Qvv`/redundancy diagnostics are based on the final local linearization. Free-network results are minimum-norm solutions tied to the supplied approximate coordinates, and the Leica GSI parser intentionally exposes conservative low-level records rather than pretending to support every instrument template. Robust covariance is approximate. Gross-error routines implement practical standardized-residual screening and repeated re-adjustment rather than a complete multiple-testing implementation of every Baarda-style design.

For production legal/metrology work, independently verify observation conventions, units, datum definitions and tolerance rules.

## License

MIT
