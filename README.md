# pySurveying

A lightweight Python toolkit for surveying computation, least-squares adjustment, quality control, coordinate transformation, and visualization.

> 轻量级 Python 测量计算、测量平差、质量控制与可视化工具包。

**Current version: 0.3.0 — release preparation**

pySurveying is designed for teaching, reproducible surveying examples, engineering-data checks, and small 2D control-network adjustment. It deliberately stays compact instead of trying to become a full geodetic production platform.

## What is included

| Area | Current scope |
| --- | --- |
| Basic surveying | DMS/decimal degrees, distance, surveying azimuth, coordinate forward/inverse computation |
| Intersection | forward intersection, distance intersection, 2D orientation resection |
| Traverse | closed/connected traverse, angular closure, azimuth propagation, Bowditch coordinate adjustment |
| Leveling | leveling route and weighted least-squares leveling network |
| Linear adjustment | weighted least squares with diagonal or full correlated weight matrices |
| 2D control networks | distance, azimuth, direction and horizontal-angle observations |
| Free/robust adjustment | minimum-norm 2D free network, Huber robust network adjustment, Huber/IGG1/IGG3 linear IRLS |
| Quality control | `Qxx`, `Qvv`, redundancy numbers, standardized residuals, iterative gross-error screening |
| Precision | coordinate standard deviations, positional standard deviation, confidence error ellipses |
| Transformation | `pyproj` CRS conversion, WGS84/ECEF/ENU, 2D similarity and affine fitting |
| Engineering helpers | polar stakeout, offset/chainage, slope, grade elevation, area |
| Data/result IO | CSV, Excel, LandXML points, low-level Leica GSI words, Excel adjustment reports |
| GUI | bundled Streamlit interface |

### Scope freeze for 0.3.0

The current release **does not expand** instrument-brand formats or engineering-survey modules. In particular, 0.3.0 is not adding a large catalog of Trimble/Topcon/Sokkia/Chinese-instrument formats, nor road alignment, earthwork, deformation-monitoring or other large engineering subsystems. The focus is validation, examples, documentation, GUI usability and packaging quality.

## Coordinate and observation conventions

For the local planar helpers:

- coordinates are `(x, y)`;
- `+Y` is north and `+X` is east;
- surveying azimuth is measured clockwise from north;
- public surveying angles are decimal degrees unless documented otherwise;
- distances, coordinates and linear standard deviations in one calculation must use consistent units;
- `Observation.sigma` uses coordinate units for `distance`, and degrees for `azimuth`, `direction` and `angle`.

For CRS transformations, `pyproj` conventions apply. `transform_coordinates(..., always_xy=True)` uses longitude/easting first and latitude/northing second.

## Installation

### Current source installation

Until the first PyPI release is published, install directly from the repository:

```bash
git clone https://github.com/hujinghaoabcd/pySurveying.git
cd pySurveying
python -m pip install -e .
```

For the visual interface:

```bash
python -m pip install -e ".[ui]"
pysurveying-ui
```

For development and validation:

```bash
python -m pip install -e ".[dev,ui]"
python -m pytest
python -m ruff check src tests examples
python -m build
python -m twine check dist/*
```

After the first PyPI release, installation will become:

```bash
python -m pip install pysurveying
python -m pip install "pysurveying[ui]"
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
from pysurveying import least_squares

A = np.array([[1.0], [1.0], [1.0]])
L = np.array([10.01, 9.99, 10.00])
result = least_squares(A, L)

print(result.parameters)
print(result.residuals)
print(result.sigma0)
print(result.metadata["qvv"])
```

`P` may be omitted, supplied as a positive weight vector, or supplied as a complete symmetric weight matrix for correlated observations.

### Closed traverse from measured angles

```python
from pysurveying import closed_traverse_from_angles

result = closed_traverse_from_angles(
    start=(0.0, 0.0),
    start_azimuth_deg=90.0,
    interior_angles_deg=[90.01, 89.99, 90.02, 89.98],
    distances=[100.02, 99.98, 100.01, 99.99],
)

print(result["angle_adjustment"])
print(result["coordinates"])
```

### Unequal-weight leveling network

```python
from pysurveying import LevelObservation, leveling_network

observations = [
    LevelObservation("BM", "A", 1.0000, sigma=0.0010),
    LevelObservation("A", "B", 2.0000, sigma=0.0020),
    LevelObservation("BM", "B", 3.0010, sigma=0.0015),
]

result = leveling_network(observations, {"BM": 100.0})
print(result.metadata["adjusted_heights"])
print(result.sigma0)
```

### 2D control network with quality and precision

```python
import math
from pysurveying import (
    Observation,
    Point,
    adjust_control_network,
    control_network_precision,
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
print(control_network_precision(result))
```

For robust network adjustment use `adjust_control_network_robust(...)`. For repeated standardized-residual screening and re-adjustment use `control_network_data_snooping(...)`.

## Reference-backed examples

The repository contains exact numerical regression tests for two examples in 宋力杰《测量平差程序设计》:

- §3.1.5 independent weighted parameter adjustment;
- §3.2.5 correlated-observation parameter adjustment using the full printed weight matrix.

Both reproduce the book's printed parameter solution, residual vector, unit-weight standard deviation and `Qxx` values. Run them directly with:

```bash
python examples/textbook_parameter_adjustment.py
```

See `docs/STANDARD_EXAMPLES.md` for what is source-backed, what is a transparent package regression example, and what is **not** claimed as an external standard.

## Shipped example data

Human-readable datasets live in `examples/data/`:

```text
examples/data/
├── control_points.csv
├── control_observations.csv
├── leveling_fixed.csv
├── leveling_observations.csv
├── traverse_angles.csv
└── common_points.csv
```

They are not decorative samples: automated tests load and execute them so that documentation/example data cannot silently drift away from the package API.

Run the combined workflow:

```bash
python examples/example_data_workflow.py
```

## GUI

Launch with:

```bash
pysurveying-ui
```

The Streamlit interface contains pages for:

- overview and conventions;
- basic coordinate computation;
- intersection and resection;
- traverse adjustment;
- leveling route/network adjustment;
- 2D control-network adjustment;
- observation quality, point precision and optional gross-error screening;
- linear least squares and built-in textbook regression examples;
- coordinate transformation;
- the intentionally limited engineering helpers;
- data import and downloadable example CSV files.

Control-network results can be exported to Excel together with residual-quality diagnostics.

## Documentation

- [`docs/API.md`](docs/API.md) — public API reference
- [`docs/STANDARD_EXAMPLES.md`](docs/STANDARD_EXAMPLES.md) — reference-backed and regression examples
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — numerical/statistical validation notes
- [`docs/ALGORITHMS.md`](docs/ALGORITHMS.md) — algorithm notes
- [`docs/DATA_FORMATS.md`](docs/DATA_FORMATS.md) — supported table/file formats
- [`docs/RELEASE.md`](docs/RELEASE.md) — PyPI release procedure
- [`CHANGELOG.md`](CHANGELOG.md) — version history

## Package structure

```text
src/pysurveying/
├── models.py       # Point / observations / AdjustmentResult
├── basic.py        # angles, coordinates, intersections, resection
├── traverse.py     # traverse and angular closure
├── leveling.py     # leveling route and network
├── adjustment.py   # least squares and 2D control networks
├── quality.py      # robust estimation, quality and data snooping
├── precision.py    # coordinate precision and error ellipses
├── transform.py    # CRS / ECEF / ENU / 2D transforms
├── engineering.py  # limited common engineering calculations
├── io.py           # tables, LandXML/GSI helpers and result export
├── ui.py           # command entry point
└── webapp.py       # Streamlit application
```

## Validation and statistical scope

The project favors small, inspectable regression cases rather than a hidden reference dataset. Current validation covers independent and correlated weighted parameter adjustment, robust-equivalent weighting, `Qvv`/redundancy diagnostics, distance and angular gross-error localization, free-network internal geometry, point precision/ellipses, transformations, IO and the shipped example datasets.

Important qualifications:

- nonlinear control-network `Qxx`, `Qvv`, redundancy numbers and standardized residuals are based on the final local linearization;
- robust covariance is an approximate local/equivalent-weight covariance;
- free-network absolute coordinates and covariance depend on the selected datum realization;
- gross-error routines are computational screening tools, not a universal replacement for significance-level design in a governing specification;
- the Leica GSI helper intentionally exposes conservative low-level records rather than claiming every instrument template.

For legal, cadastral, metrology or high-order production work, independently verify observation conventions, stochastic models, datum definitions, units and acceptance tolerances against the applicable specification.

## PyPI release preparation

The repository contains `.github/workflows/publish.yml` for tag-triggered PyPI Trusted Publishing. Publication is intentionally not automatic from every `main` push. The one-time PyPI trusted-publisher/environment setup is documented in `docs/RELEASE.md`; after that, a release tag such as `v0.3.0` can trigger the publish workflow.

## License

MIT
