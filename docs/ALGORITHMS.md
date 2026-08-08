# Algorithms and conventions

pySurveying keeps the numerical core deliberately small. This document records the conventions used by the implemented algorithms so that results can be checked against hand calculations and surveying textbooks.

## 1. Planar coordinate convention

The local planar helpers use `(x, y)` with:

- `+Y` = north
- `+X` = east
- surveying azimuth measured clockwise from north
- public angle inputs in decimal degrees

Therefore, for distance `S` and azimuth `A`:

```text
Δx = S sin(A)
Δy = S cos(A)
```

`forward_coordinate` and `azimuth` use this same convention.

## 2. Intersections and resection

`forward_intersection` intersects two rays defined by known points and azimuths.

`distance_intersection` solves the intersection of two circles and can return two geometric solutions.

`resection` estimates station X/Y and an orientation constant from at least three known points and observed directions using nonlinear least squares.

## 3. Traverse adjustment

`closed_traverse` and `connected_traverse` use the Bowditch (compass) rule. Coordinate misclosures are distributed in proportion to side length.

`adjust_angles` distributes angular misclosure by equal correction when no weights are supplied. When weights are supplied, corrections are proportional to inverse weight.

`closed_traverse_from_angles` performs:

```text
angular closure -> adjusted interior angles -> side azimuths -> coordinate increments -> Bowditch adjustment
```

## 4. Leveling

`leveling_route` distributes route height misclosure equally by section or proportionally to supplied section lengths.

`leveling_network` uses the observation equation:

```text
H_to - H_from = Δh
```

with observation weight:

```text
p = 1 / sigma²
```

At least one benchmark height must be fixed.

## 5. Linear least squares

For the linear model:

```text
A x ≈ L
```

pySurveying minimizes:

```text
vᵀ P v
```

and returns parameters, residuals, posterior unit-weight standard deviation, covariance, `Qxx`, `Qvv`, and observation redundancy numbers. Pseudoinverses are used so rank-deficient educational/free-network examples remain inspectable.

## 6. 2D control networks

The compact control-network solver supports:

- `distance`
- `azimuth`: absolute surveying azimuth
- `direction`: circle direction; a station-orientation unknown is introduced automatically
- `angle`: horizontal angle from backsight (`to_point`) to foresight (`target2`)

Observation residuals are internally divided by the supplied standard deviation before iterative adjustment. The nonlinear Jacobian is computed numerically.

`adjust_free_network` uses a minimum-norm realization tied to the supplied approximate coordinates. It is intended for small networks and teaching/engineering checks, not as a full datum-design package.

## 7. Robust adjustment and gross-error screening

The package now exposes both a compact SciPy Huber solver and the equivalent-weight workflow common in surveying adjustment texts.

`equivalent_weight_factor` implements the three piecewise functions used by the robust-adjustment workflow:

- Huber: full weight inside `k0`, then `k0 / |v|`
- IGG1: full weight inside `k0`, reduced weight between `k0` and `k1`, zero weight at and beyond `k1`
- IGG3: full weight inside `k0`, smoothly tapered weight between `k0` and `k1`, zero weight at and beyond `k1`

`robust_least_squares_irls` first performs ordinary least squares, obtains residual standard deviations from `sigma0 * sqrt(diag(Qvv))`, standardizes the residuals, converts them to equivalent weights, and repeats weighted least squares until the parameters stabilize.

`data_snooping` is the one-pass inspection table. `iterative_data_snooping` follows the classical gross-error search sequence:

```text
least squares
-> standardized residuals
-> find the largest |standardized residual|
-> remove it when it exceeds the threshold
-> re-adjust
-> repeat
```

The threshold is deliberately caller-controlled. These routines implement the computational screening workflow; they do not claim to provide a complete multiple-testing decision design for every Baarda-style application.

## 8. Error ellipses

`error_ellipse` diagonalizes a 2×2 coordinate covariance matrix and scales the axes using the chi-square quantile for the requested confidence level. The default is a 95% confidence ellipse.

## 9. Coordinate transformations

`transform_coordinates` delegates CRS transformations to pyproj.

WGS84 helpers provide:

```text
geodetic <-> ECEF <-> local ENU
```

Local 2D fitting provides:

- four-parameter similarity transformation
- six-parameter affine transformation

Both fitting functions return residuals and a point RMSE.

## 10. Engineering-survey helpers

The current compact set includes polar stakeout, straight-line offset, chainage/offset projection, slope, design elevation on a constant grade, slope-distance decomposition, and planar polygon area.

## Numerical scope

The package prioritizes transparent, small implementations. Large national geodetic networks, rigorous variance-component estimation, full geodetic datum design, GNSS carrier-phase processing, photogrammetry, SLAM, and point-cloud processing are intentionally outside the core package.
