# FAQ

## What is pySurveying?

pySurveying is a lightweight Python toolkit for common surveying computation, least-squares adjustment, quality control, coordinate transformation, and visualization.

It is intentionally smaller than a full geodetic production suite.

## Who is it for?

Typical users are:

- surveying / geomatics students;
- researchers who need transparent adjustment code;
- engineers checking small datasets or control networks;
- Python users who want a reproducible alternative to one-off spreadsheets;
- teachers preparing inspectable surveying examples.

## What is the coordinate convention?

For local planar helpers:

```text
+Y = North
+X = East
Azimuth = clockwise from North
```

Coordinates are passed as `(x, y)`.

This differs from the usual mathematical convention where an angle is measured counter-clockwise from the positive X axis, so do not mix conventions silently.

## Are angles degrees or radians?

Public surveying angles are decimal degrees unless explicitly documented otherwise.

## What unit should `sigma` use?

`Observation.sigma` must use the same observation unit as the observation itself:

- `distance`: same linear unit as the coordinates;
- `azimuth`: degrees;
- `direction`: degrees;
- `angle`: degrees.

Leveling `sigma` uses the same height unit as the height differences.

## What is the difference between `azimuth` and `direction`?

`azimuth` is an absolute surveying azimuth.

`direction` represents an observed circle direction. pySurveying estimates one orientation unknown for each occupied station that has direction observations.

That distinction matters in a horizontal control network.

## Does pySurveying support correlated observations?

Yes. `least_squares(A, L, P=...)` accepts a complete symmetric observation weight matrix, not only a diagonal vector.

The repository contains a textbook-backed correlated-observation regression case.

## What do `Qxx` and `Qvv` mean here?

`Qxx` is the parameter cofactor matrix and `Qvv` is the residual cofactor matrix of the local linearized least-squares model.

For nonlinear 2D control networks, these quantities are evaluated at the final linearization.

## Why can a perfectly consistent example show zero coordinate standard deviation?

Posterior covariance is scaled by the estimated unit-weight standard deviation. If a synthetic redundant network has exactly zero residuals, the posterior `sigma0` may be zero, so the posterior covariance and derived standard deviations are also zero.

That does not mean real observations are infinitely precise; it reflects the exact synthetic dataset and the chosen posterior scaling.

## What is a redundancy number?

A redundancy number describes how strongly an observation is internally checked by the adjustment model. Low-redundancy observations have less internal detectability for gross errors.

The sum of the redundancy numbers agrees with the residual degrees of freedom in the tested linearized cases.

## Is `data_snooping` a complete Baarda implementation?

No. The package provides standardized-residual screening and iterative removal/re-adjustment utilities.

Choosing thresholds and significance levels for formal quality control depends on the observation model, redundancy, false-alarm risk, and the governing surveying specification. pySurveying does not claim one universal statistical decision rule.

## What robust methods are available?

The linear IRLS workflow supports:

- Huber;
- IGG1;
- IGG3.

The 2D control-network convenience robust adjustment currently uses Huber weighting.

## What is the free-network implementation?

`adjust_free_network(...)` provides a minimum-norm 2D free-network solution.

A free network does not have a unique absolute translation/rotation datum. Therefore absolute coordinates and covariance depend on the selected datum realization. Internal geometry is the more meaningful invariant for cross-checking.

## Is the error ellipse 1-sigma or a confidence ellipse?

`error_ellipse(...)` accepts a confidence level and scales the coordinate covariance using the appropriate chi-square factor. The returned major-axis direction is an undirected surveying azimuth normalized to `[0, 180)`.

## Does pySurveying replace GNU Gama, JAG3D, or commercial surveying software?

No.

pySurveying focuses on a small Python-native workflow that is easy to inspect, teach, script, and integrate with scientific Python code.

Full geodetic packages may support broader stochastic models, adjustment types, database workflows, instrument integrations, standards, and production features.

## Does pySurveying replace `pyproj`?

No. CRS transformations are delegated to `pyproj` where appropriate. pySurveying adds surveying-oriented wrappers and local ECEF/ENU plus fitted 2D transformation helpers.

## Which file formats are supported?

Current support is intentionally conservative:

- CSV;
- XLSX/XLSM;
- LandXML point data;
- low-level Leica GSI words.

The project is not claiming universal manufacturer-template compatibility.

## Will more instrument brands be added before 0.3.0?

No. Instrument-format expansion is frozen for the current release-preparation cycle.

## Will road alignment, earthwork, deformation monitoring, PPP/RTK, photogrammetry, point clouds, or SLAM be added before 0.3.0?

No. Those are outside the current lightweight scope.

## Can I use pySurveying for production/legal surveying?

Use it only with independent verification appropriate to your work.

For legal, cadastral, metrology, or high-order control work, verify:

- observation conventions;
- stochastic models;
- datum definitions;
- units;
- tolerances;
- required statistical tests;
- governing specifications.

## Why are there both Python examples and a GUI?

The Python API is the primary reusable core. The Streamlit GUI makes the same ideas easier to explore, teach, and inspect interactively.

## Where are the example datasets?

`examples/data/` contains small human-readable CSV examples for:

- control networks;
- leveling;
- traverses;
- coordinate transformations.

Automated tests execute these datasets.

## How do I run the textbook examples?

```bash
python examples/textbook_parameter_adjustment.py
```

See `docs/STANDARD_EXAMPLES.md` for provenance and scope.

## How do I report a bug?

Use the repository's bug-report issue template and include:

- pySurveying version;
- Python version;
- minimal reproducible data/code;
- expected result;
- actual result;
- coordinate/angle/unit conventions.

## How should I cite pySurveying?

Use the repository's `CITATION.cff` metadata. GitHub will expose a **Cite this repository** entry when it recognizes the file.
