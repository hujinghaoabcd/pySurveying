# pySurveying

A lightweight Python toolkit for surveying computation, least-squares adjustment, quality control, coordinate transformation, and visualization.

> 轻量级 Python 测量计算、测量平差与可视化工具包。

## What it does

pySurveying deliberately stays small. It focuses on the common calculations that surveying students and engineers repeatedly need:

- distance, azimuth and coordinate forward/inverse calculation
- forward intersection, distance intersection and resection
- closed and connected traverse adjustment
- leveling-route adjustment
- weighted least-squares adjustment
- small 2D control-network adjustment using distance, direction and angle observations
- free-network minimum-norm adjustment
- Huber robust adjustment and residual-based gross-error screening
- 2D error ellipses
- CRS coordinate transformation via `pyproj`
- stakeout, offset, slope and polygon-area calculations
- CSV, Excel, LandXML point and Leica GSI word import helpers
- a lightweight Streamlit interface

The mathematical organization follows the classical surveying-adjustment workflow represented by *测量平差程序设计*, but NumPy/SciPy are used for modern numerical linear algebra instead of reimplementing low-level matrix routines.

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
pytest
ruff check src tests
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

Weighted least squares:

```python
import numpy as np
from pysurveying.adjustment import least_squares

A = np.array([[1.0], [1.0], [1.0]])
L = np.array([10.01, 9.99, 10.00])
result = least_squares(A, L)
print(result.parameters)
print(result.residuals)
print(result.sigma0)
```

Closed traverse:

```python
from pysurveying.traverse import closed_traverse

result = closed_traverse(
    start=(0.0, 0.0),
    azimuths_deg=[90.0, 0.0, 270.0, 180.0],
    distances=[100.0, 100.0, 100.0, 100.0],
)
print(result["coordinates"])
```

Coordinate transformation:

```python
from pysurveying.transform import transform_coordinates

x, y = transform_coordinates(118.7969, 32.0603, "EPSG:4326", "EPSG:3857")
```

## Package structure

```text
src/pysurveying/
├── models.py       # Point / Observation / AdjustmentResult
├── basic.py        # angles, coordinates, intersections, resection
├── traverse.py     # closed and connected traverse
├── leveling.py     # leveling route adjustment
├── adjustment.py   # least squares and 2D control networks
├── quality.py      # robust estimation, outliers, error ellipses
├── transform.py    # CRS transformations
├── engineering.py  # stakeout, offsets, slope, area
├── io.py           # CSV / XLSX / LandXML / GSI
├── ui.py           # command entry point
└── webapp.py       # Streamlit interface
```

## Design rules

1. Small functional API instead of a deep class hierarchy.
2. Core algorithms are independent from the UI.
3. Results expose residuals, covariance and precision information.
4. Existing numerical/geodetic libraries are reused when they already solve the low-level problem well.
5. pySurveying does not try to replace GIS, GNSS processing, photogrammetry or point-cloud software.

## Current scope and limitations

This is an early `0.1.x` implementation intended for common educational and engineering calculations. Instrument parsers are intentionally conservative, the control-network solver is aimed at small 2D networks, and free-network results are minimum-norm solutions tied to the supplied approximate coordinates. For production legal/metrology work, independently verify conventions, units and tolerances.

## License

MIT
