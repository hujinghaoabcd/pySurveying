# pySurveying API reference

This page documents the compact public API exported from `pysurveying`. The package intentionally keeps a functions-first design instead of a deep class hierarchy.

## Conventions

- Local planar coordinates are `(x, y)` with `+Y` north and `+X` east.
- Surveying azimuth is measured clockwise from north.
- Public surveying angles are decimal degrees unless a function says otherwise.
- Linear quantities in one calculation must use consistent units.
- `Observation.sigma` uses the same unit as its observation: coordinate units for distance, degrees for azimuth/direction/angle.

## Data models

### `Point(name, x, y, z=None, fixed=False)`

Small point record used by control-network routines. `fixed=True` keeps planar coordinates fixed during constrained adjustment.

### `Observation(kind, from_point, to_point, value, sigma=1.0, target2=None)`

Control-network observation. Supported kinds:

- `distance`: `from_point -> to_point`, value in coordinate-distance units.
- `azimuth`: absolute surveying azimuth in degrees.
- `direction`: circle direction in degrees. One orientation unknown is estimated for each occupied station.
- `angle`: `from_point` is the station, `to_point` is the backsight, `target2` is the foresight.

### `LevelObservation(from_point, to_point, height_difference, sigma=1.0)`

Height-difference observation using `H_to - H_from`.

### `AdjustmentResult`

Common result object with:

- `parameters`
- `residuals`
- `sigma0`
- `covariance`
- `dof`
- `converged`
- `iterations`
- `metadata`

The exact metadata depends on the solver. Linear least squares exposes `qxx`, `qvv`, redundancy numbers, normal matrix and weight matrix. Control-network adjustment additionally exposes adjusted points, orientation parameters, raw observation-unit residuals and observation kinds.

## Basic surveying

### `normalize_angle(angle)`
Normalize degrees to `[0, 360)`.

### `dms_to_degree(degrees, minutes=0, seconds=0)`
Convert DMS components to decimal degrees.

### `degree_to_dms(angle)`
Return `(degrees, minutes, seconds)`.

### `distance(p1, p2)`
Planar Euclidean distance.

### `azimuth(p1, p2)`
Surveying azimuth clockwise from north.

### `forward_coordinate(x, y, azimuth_deg, length)`
Coordinate forward computation.

### `inverse_coordinate(p1, p2)`
Return `{"distance": ..., "azimuth": ...}`.

### `forward_intersection(p1, azimuth1, p2, azimuth2)`
Intersect two rays defined by known points and surveying azimuths.

### `distance_intersection(p1, r1, p2, r2)`
Circle-circle intersection from two known points and distances. Returns one or two solutions.

### `resection(known_points, directions_deg, initial=None)`
2D orientation resection from at least three known points and observed directions. Returns station `X`, `Y`, and orientation constant in degrees.

## Traverse

### `closed_traverse(start, azimuths_deg, distances)`
Bowditch adjustment of a geometrically closed traverse.

### `connected_traverse(start, end, azimuths_deg, distances)`
Bowditch adjustment between two known endpoints.

### `adjust_angles(angles_deg, theoretical_sum=None, weights=None)`
Distribute angular misclosure by weighted least squares. When `theoretical_sum` is omitted, `(n - 2) * 180°` is used.

### `traverse_azimuths_from_angles(start_azimuth_deg, interior_angles_deg, turn="right")`
Propagate side azimuths from interior angles.

### `closed_traverse_from_angles(start, start_azimuth_deg, interior_angles_deg, distances, turn="right", angle_weights=None)`
Adjust polygon angles, derive side azimuths, then apply Bowditch coordinate correction.

## Leveling

### `leveling_route(start_height, height_differences, end_height=None, lengths=None)`
Adjust a closed or connected leveling route. Corrections are equal per section when lengths are omitted, otherwise proportional to section length.

### `leveling_network(observations, fixed_heights)`
Weighted least-squares adjustment of a small leveling network. Observation weight is `1 / sigma²`.

## Least-squares and control networks

### `least_squares(A, L, P=None)`
Weighted linear least squares for `A x ≈ L`.

`P` may be:

- omitted for identity weight,
- a positive observation-weight vector,
- a full symmetric weight matrix for correlated observations.

The result includes `Qxx`, `Qvv`, redundancy numbers and posterior covariance.

### `adjust_control_network(points, observations, max_iterations=20, tolerance=1e-7, free_network=False, robust=False, huber_k=1.5)`
Iterative small 2D network adjustment supporting distance, azimuth, direction and horizontal-angle observations.

Residuals stored in `result.residuals` are normalized by observation sigma. `result.metadata["raw_residuals"]` stores residuals in original observation units.

### `adjust_control_network_robust(points, observations, huber_k=1.5, **kwargs)`
Convenience wrapper for Huber robust control-network adjustment.

### `adjust_free_network(points, observations, **kwargs)`
Minimum-norm 2D free-network adjustment. The supplied approximate coordinates define the practical datum realization, so absolute free-network coordinates and covariance remain datum-dependent.

## Quality control and precision

### `standardized_residuals(result)`
Calculate standardized residuals, using `Qvv` when available.

### `redundancy_numbers(result)`
Return per-observation redundancy numbers when available.

### `detect_outliers(result, threshold=3.0)`
Return indices whose absolute standardized residual reaches the threshold.

### `data_snooping(result, threshold=3.0)`
Return a compact per-observation residual-screening table.

### `iterative_data_snooping(A, L, P=None, threshold=3.0, max_removals=None)`
Repeatedly remove the largest standardized residual above the threshold and re-adjust a linear model.

### `control_network_quality(result, observations, threshold=3.0)`
Map final-linearization diagnostics back to control-network observations. Includes observation-unit residual, normalized residual, standardized residual, redundancy number, robust weight and flag.

### `control_network_data_snooping(points, observations, threshold=3.0, max_removals=None, **adjustment_kwargs)`
Repeated ordinary control-network adjustment and standardized-residual screening while preserving original observation indices.

### `equivalent_weight_factor(value, method="huber", k0=1.5, k1=2.5)`
Single robust equivalent-weight factor. Methods: `huber`, `igg1`, `igg3`.

### `equivalent_weight_factors(values, method="huber", k0=1.5, k1=2.5)`
Vectorized equivalent-weight factors.

### `robust_least_squares(A, L, f_scale=1.0)`
Compact SciPy Huber-loss linear solver retained as a convenience API.

### `robust_least_squares_irls(A, L, method="huber", k0=1.5, k1=2.5, max_iterations=50, tolerance=1e-10)`
Surveying-style equivalent-weight IRLS for Huber, IGG1 or IGG3 weighting.

### `error_ellipse(covariance_2x2, confidence=0.95)`
Return confidence-ellipse semi-major axis, semi-minor axis and undirected surveying azimuth in `[0, 180)`.

### `control_network_precision(result, confidence=0.95)`
Return one precision row per adjusted point: `sigma_x`, `sigma_y`, `cov_xy`, positional standard deviation and confidence-ellipse values.

## Coordinate transformation

### `transform_coordinates(x, y, source_crs, target_crs, always_xy=True)`
CRS-to-CRS conversion through `pyproj`.

### `geodetic_to_ecef(lon, lat, height)` / `ecef_to_geodetic(x, y, z)`
WGS84 geodetic and Earth-centered Earth-fixed conversions.

### `ecef_to_enu(...)` / `enu_to_ecef(...)`
ECEF and local East-North-Up conversion relative to a geodetic origin.

### `geodetic_to_enu(...)` / `enu_to_geodetic(...)`
Direct WGS84 geodetic/local ENU helpers.

### `fit_similarity_2d(source_points, target_points)` / `apply_similarity_2d(points, parameters)`
Fit and apply a 2D four-parameter similarity transformation.

### `fit_affine_2d(source_points, target_points)` / `apply_affine_2d(points, parameters)`
Fit and apply a 2D six-parameter affine transformation.

## Engineering helpers

The project deliberately stops at common small calculations in the current release.

- `polar_stakeout(station, target)`
- `offset_point(start, end, offset, along=None)`
- `chainage_offset(point, start, end)`
- `slope(horizontal_distance, height_difference)`
- `grade_elevation(start_height, chainage, grade_percent)`
- `horizontal_distance_from_slope(slope_distance, vertical_angle_deg)`
- `height_difference_from_slope_distance(slope_distance, vertical_angle_deg)`
- `polygon_area(points)`

## Table/file helpers

### `normalize_point_columns(data)`
Normalize common Chinese/English point-column aliases to `name`, `x`, `y`, `z`, `fixed` where possible.

### `points_from_dataframe(data)`
Convert a point table to `Point` objects.

### `observations_from_dataframe(data)`
Convert a compact control-network observation table to `Observation` objects.

### `level_observations_from_dataframe(data)`
Convert a leveling table to `LevelObservation` objects.

### `read_points(path, **kwargs)`
Auto-detect CSV, XLSX/XLSM, LandXML/XML or Leica GSI by extension.

### `write_points(data, path, **kwargs)`
Write point tables to CSV or XLSX.

### `adjustment_tables(result)`
Convert an adjustment result to export-friendly pandas tables.

### `export_adjustment_excel(result, path)`
Write summary, parameters, residual diagnostics and adjusted values to an XLSX workbook.

## Statistical scope

The quality-control routines are computational tools, not a substitute for the significance-level design required by a specific surveying specification. Nonlinear control-network `Qxx`, `Qvv`, redundancy and standardized residuals are based on the final local linearization. Robust covariance is an approximate local/equivalent-weight covariance.
