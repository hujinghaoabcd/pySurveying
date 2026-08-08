# pySurveying

A lightweight Python toolkit for surveying computation, least-squares adjustment, quality control, coordinate transformation, and visualization.

> 轻量级 Python 测量计算、测量平差与可视化工具包。

## Scope

pySurveying focuses on common surveying workflows without becoming a large GIS framework:

- basic surveying calculations: distance, azimuth, forward/inverse coordinate computation
- traverse adjustment: closed and connected traverses
- leveling route adjustment
- forward intersection, distance intersection, and resection
- weighted least-squares adjustment
- 2D control-network adjustment
- free-network adjustment
- robust adjustment and gross-error detection
- error ellipses
- CRS coordinate transformation via `pyproj`
- common engineering-survey calculations
- CSV / Excel / LandXML / Leica GSI input helpers
- a lightweight Streamlit user interface

The numerical core follows the classical surveying-adjustment workflow used in *测量平差程序设计* while relying on NumPy/SciPy for modern numerical linear algebra.

## Install

```bash
pip install -e .
```

For the visual interface:

```bash
pip install -e ".[ui]"
pysurveying-ui
```

For development:

```bash
pip install -e ".[dev,ui]"
pytest
```

## Quick start

```python
from pysurveying import Point, distance, azimuth, forward_coordinate

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
print(result.sigma0)
```

## Package layout

```text
src/pysurveying/
├── models.py       # common data structures
├── basic.py        # angles, coordinates, intersections, resection
├── traverse.py     # traverse computations
├── leveling.py     # leveling route adjustment
├── adjustment.py   # least squares and 2D control networks
├── quality.py      # robust estimation, outliers, error ellipse
├── transform.py    # CRS / geodetic transformations
├── engineering.py  # stakeout, offsets, slope, area
└── io.py           # tabular and instrument data import
```

## Design principles

1. **Small API** — prefer functions and simple dataclasses over deep class hierarchies.
2. **Transparent results** — adjustment functions return residuals, covariance and precision information.
3. **Surveying first** — this package does not try to replace GIS, photogrammetry, GNSS processing or point-cloud libraries.
4. **Testable mathematics** — core algorithms are independent from the UI.

## Status

The project is under active initial development. The current main branch already contains a usable first implementation of the core toolkit and a lightweight Streamlit interface.

## License

MIT
