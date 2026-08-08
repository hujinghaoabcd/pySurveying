# Architecture

pySurveying is deliberately organized as a small scientific Python package rather than a framework.

## Design goals

The architecture follows five rules:

1. **Core calculations must not depend on the GUI.**
2. **Surveying conventions must be explicit.**
3. **Adjustment results should carry quality information, not only coordinates.**
4. **NumPy/SciPy should provide numerical linear algebra instead of custom matrix infrastructure.**
5. **New features should fit into a small module before a new framework layer is introduced.**

## Package layers

```text
User code / notebooks / scripts
            │
            ├───────────────┐
            │               │
        public API       Streamlit GUI
      pysurveying.*       webapp.py
            │               │
            └───────┬───────┘
                    │
          scientific core modules
                    │
     NumPy / SciPy / pandas / pyproj
```

The Streamlit application calls the same core functions that normal Python users call.

## Domain records

`models.py` contains compact dataclasses:

- `Point`
- `Observation`
- `LevelObservation`
- `AdjustmentResult`

They are intentionally small and serializable/inspectable.

`AdjustmentResult` is the common carrier for:

```text
parameters
residuals
sigma0
covariance
degrees of freedom
convergence state
iterations
metadata
```

Module-specific diagnostics are placed in `metadata` rather than creating a large inheritance hierarchy of result classes.

## Basic geometry

`basic.py` contains coordinate/angle primitives:

```text
DMS conversion
angle normalization
distance
surveying azimuth
forward/inverse coordinates
forward intersection
distance intersection
resection
```

These functions establish the package's local planar convention used by higher-level modules.

## Traverse and leveling

`traverse.py` handles deterministic traverse workflows:

```text
angle closure
azimuth propagation
coordinate increments
Bowditch corrections
closed/connected traverse
```

`leveling.py` contains both simple route closure and a small weighted least-squares leveling-network solver.

## Adjustment core

`adjustment.py` has two conceptual levels.

### Linear least squares

```text
A x ≈ L
```

with identity, diagonal, or full observation weight matrix `P`.

Outputs include:

```text
Qxx
Qvv
redundancy numbers
posterior covariance
```

### Nonlinear 2D control network

Observation models are iteratively linearized for:

```text
distance
azimuth
direction
horizontal angle
```

Unknowns can include planar point coordinates and station orientation constants for direction sets.

The final local linearization is also used to report quality/precision quantities.

## Quality and robust estimation

`quality.py` contains:

```text
standardized residuals
redundancy extraction
single-pass screening
iterative data snooping
Huber / IGG1 / IGG3 equivalent weights
robust IRLS
control-network quality mapping
```

The package separates:

- **robust estimation**, which reduces the influence of large residuals; and
- **gross-error screening**, which identifies/removes suspicious observations and re-adjusts.

They are related but not treated as identical operations.

## Precision

`precision.py` maps covariance blocks back to adjusted points and reports:

```text
sigma_x
sigma_y
cov_xy
positional sigma
confidence ellipse axes
ellipse azimuth
```

## Transformations

`transform.py` has two roles:

### CRS/geocentric/local coordinates

Implemented with `pyproj` plus local rotation matrices:

```text
CRS ↔ CRS
WGS84 geodetic ↔ ECEF
ECEF ↔ ENU
geodetic ↔ ENU
```

### Fitted planar transformations

Implemented with NumPy least squares:

```text
2D similarity (4 parameters)
2D affine (6 parameters)
```

## Engineering helpers

`engineering.py` intentionally contains only compact straight-line/common helpers such as stakeout, offsets, chainage, slope, grade elevation, slope-distance components, and polygon area.

Large alignment/earthwork/deformation systems are kept outside the current core scope.

## IO boundary

`io.py` converts between domain objects/results and table/file representations:

```text
CSV
Excel
LandXML points
low-level Leica GSI records
DataFrame → Point / Observation / LevelObservation
AdjustmentResult → tables / Excel
```

Instrument parsing is conservative by design; real vendor dialects should not be inferred from one sample file.

## GUI boundary

`ui.py` is only the command entry point.

`webapp.py` contains Streamlit presentation logic. Numerical formulas should not be duplicated there. If a calculation is useful outside the GUI, it belongs in a core module first.

## Testing strategy

The test suite combines:

- small analytic checks;
- textbook-backed numerical regressions;
- transparent synthetic control-network cases;
- contaminated-observation cases;
- round-trip transformations;
- real package example CSV files;
- IO/export checks.

Examples under `examples/` are also executed in CI.

## Extension rule

Before adding a new module, ask:

1. Is this a common surveying computation or adjustment task?
2. Can it be represented by a small API?
3. Can expected values be independently checked?
4. Can it be tested without adding a large infrastructure layer?
5. Does it preserve the package's lightweight identity?

If most answers are no, the feature likely belongs in a separate package or optional extension.
