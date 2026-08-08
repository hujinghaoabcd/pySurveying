<div align="center">

# pySurveying

**Lightweight surveying computation, adjustment, quality control, and visualization for Python.**

轻量级 Python 测量计算、测量平差、质量控制与可视化工具包。

[![tests](https://github.com/hujinghaoabcd/pySurveying/actions/workflows/tests.yml/badge.svg)](https://github.com/hujinghaoabcd/pySurveying/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

**Traverse · Leveling · Intersection · 2D Control Networks · Robust Adjustment · Gross-error Screening · Error Ellipses · Coordinate Transformation · Streamlit GUI**

</div>

---

## Why pySurveying?

Surveying calculations are often scattered across classroom scripts, spreadsheets, proprietary software, and large geodetic packages. **pySurveying keeps the common workflow small, inspectable, and Python-native**:

- **Functions first** — straightforward NumPy/SciPy APIs instead of a deep framework.
- **Adjustment + quality together** — coordinates are not the end of the calculation; residuals, `Qxx`, `Qvv`, redundancy, precision, and error ellipses are part of the workflow.
- **Reproducible examples** — textbook-backed least-squares cases and transparent CSV examples are executable and regression-tested.
- **GUI included** — common calculations can be explored without writing code through the bundled Streamlit interface.
- **Deliberately lightweight** — this is not trying to replace a full national geodetic-processing suite or a commercial surveying platform.

> **Current release target:** `0.3.0` — documentation and public-release preparation.

## 30-second start

Until the first PyPI release is published:

```bash
git clone https://github.com/hujinghaoabcd/pySurveying.git
cd pySurveying
python -m pip install -e .
```

Then:

```python
from pysurveying import distance, azimuth, forward_coordinate

A = (1000.0, 1000.0)
B = (1100.0, 1050.0)

print(distance(A, B))
print(azimuth(A, B))
print(forward_coordinate(*A, azimuth_deg=30.0, length=100.0))
```

For the visual interface:

```bash
python -m pip install -e ".[ui]"
pysurveying-ui
```

After the first PyPI release:

```bash
python -m pip install pysurveying
python -m pip install "pysurveying[ui]"
```

## What it covers

| Area | Current scope |
| --- | --- |
| Basic surveying | DMS/decimal degrees, distance, surveying azimuth, coordinate forward/inverse computation |
| Intersection | forward intersection, distance intersection, 2D orientation resection |
| Traverse | closed/connected traverse, angular closure, azimuth propagation, Bowditch coordinate adjustment |
| Leveling | leveling route and weighted least-squares leveling network |
| Linear adjustment | weighted least squares with diagonal or full correlated weight matrices |
| 2D control networks | distance, azimuth, direction, and horizontal-angle observations |
| Free/robust adjustment | minimum-norm 2D free network, Huber robust network adjustment, Huber/IGG1/IGG3 linear IRLS |
| Quality control | `Qxx`, `Qvv`, redundancy numbers, standardized residuals, iterative gross-error screening |
| Precision | coordinate standard deviations, positional standard deviation, confidence error ellipses |
| Transformation | `pyproj` CRS conversion, WGS84/ECEF/ENU, 2D similarity and affine fitting |
| Engineering helpers | polar stakeout, offset/chainage, slope, grade elevation, area |
| Data/result IO | CSV, Excel, LandXML points, conservative low-level Leica GSI words, Excel reports |
| GUI | bundled Streamlit application |

## Surveying conventions

For local planar calculations:

- coordinates are `(x, y)`;
- `+Y` is north and `+X` is east;
- surveying azimuth is measured clockwise from north;
- public surveying angles are decimal degrees unless documented otherwise;
- linear quantities within one calculation must use consistent units;
- `Observation.sigma` uses coordinate units for `distance`, and degrees for `azimuth`, `direction`, and `angle`.

For CRS transformations, `pyproj` conventions apply. `transform_coordinates(..., always_xy=True)` uses longitude/easting first and latitude/northing second.

## Core examples

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

`P` can be omitted, supplied as a positive observation-weight vector, or supplied as a complete symmetric weight matrix for correlated observations.

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

## Validation

The repository contains **source-backed numerical regressions** for two examples in 宋力杰《测量平差程序设计》:

- §3.1.5 independent weighted parameter adjustment;
- §3.2.5 correlated-observation parameter adjustment using the full printed weight matrix.

Both reproduce the printed parameter solution, residual vector, unit-weight standard deviation, and `Qxx` values.

Run them directly:

```bash
python examples/textbook_parameter_adjustment.py
```

The release-preparation diagnostic currently exercises **52 tests**, both runnable example programs, package compilation, Ruff, wheel/sdist build, and `twine check`.

See [`docs/STANDARD_EXAMPLES.md`](docs/STANDARD_EXAMPLES.md) and [`docs/VALIDATION.md`](docs/VALIDATION.md) for what is externally backed, what is a transparent package regression example, and what is **not** claimed as a standard.

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

These are executed by automated tests so example data cannot silently drift away from the package API.

Run the combined workflow:

```bash
python examples/example_data_workflow.py
```

## GUI

Launch:

```bash
pysurveying-ui
```

The Streamlit interface includes:

- coordinate calculations;
- intersection and resection;
- traverse adjustment;
- leveling route/network adjustment;
- 2D control-network adjustment;
- observation quality and point precision;
- optional gross-error screening;
- textbook least-squares examples;
- CRS / ENU / 2D transformation helpers;
- intentionally limited engineering helpers;
- data import, example-data download, and Excel result export.

## Documentation

| Document | Purpose |
| --- | --- |
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | installation and first complete workflows |
| [`docs/API.md`](docs/API.md) | public API reference |
| [`docs/STANDARD_EXAMPLES.md`](docs/STANDARD_EXAMPLES.md) | source-backed and regression examples |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | numerical/statistical validation notes |
| [`docs/ALGORITHMS.md`](docs/ALGORITHMS.md) | algorithm notes |
| [`docs/DATA_FORMATS.md`](docs/DATA_FORMATS.md) | supported table/file formats |
| [`docs/FAQ.md`](docs/FAQ.md) | common questions and conventions |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | release scope and future direction |
| [`docs/RELEASE.md`](docs/RELEASE.md) | TestPyPI/PyPI release procedure |
| [`CHANGELOG.md`](CHANGELOG.md) | version history |

## Project scope

`0.3.0` intentionally **freezes feature expansion** while documentation and release quality are completed.

The current release is **not** expanding into:

- a large catalog of Trimble/Topcon/Sokkia/Chinese-instrument parsers;
- road alignment and curve design;
- earthwork-volume systems;
- deformation-monitoring platforms;
- GNSS PPP/RTK processing;
- photogrammetry, point clouds, or SLAM;
- a replacement for a certified national/commercial geodetic suite.

Keeping that boundary is part of the project design, not an unfinished feature list.

## Project structure

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
├── io.py           # tables, LandXML/GSI helpers, result export
├── ui.py           # command entry point
└── webapp.py       # Streamlit application
```

## Contributing

Bug reports, validation cases, documentation improvements, tests, and focused surveying algorithms are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request.

For usage questions, see [`SUPPORT.md`](SUPPORT.md) and [`docs/FAQ.md`](docs/FAQ.md).

## Citation

If pySurveying contributes to academic or technical work, please cite the software repository. GitHub can expose the repository citation metadata from [`CITATION.cff`](CITATION.cff).

```text
Hu, Jinghao. pySurveying: Lightweight surveying computation,
adjustment, quality control, and visualization for Python.
https://github.com/hujinghaoabcd/pySurveying
```

A DOI can be added to the citation metadata later if a versioned software archive is created.

## Statistical and production-use notes

- Nonlinear control-network `Qxx`, `Qvv`, redundancy numbers, and standardized residuals use the final local linearization.
- Robust covariance is an approximate local/equivalent-weight covariance.
- Free-network absolute coordinates and covariance depend on the selected datum realization.
- Gross-error routines are computational screening tools, not a universal replacement for significance-level design required by a governing specification.
- The Leica GSI helper intentionally exposes conservative low-level records rather than claiming every instrument template.

For legal, cadastral, metrology, or high-order production work, independently verify observation conventions, stochastic models, datum definitions, units, and acceptance tolerances against the applicable specification.

## Release status

The package is being prepared for a **TestPyPI → PyPI** first release. Publishing workflows are already in `.github/workflows/`; production publishing is deliberately tag-triggered rather than automatic on every `main` push.

See [`docs/RELEASE.md`](docs/RELEASE.md).

## License

MIT. See [`LICENSE`](LICENSE).
