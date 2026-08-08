# pySurveying documentation

This directory contains the project documentation used for the `0.3.0` public-release preparation cycle.

## Start here

| Goal | Document |
| --- | --- |
| Install and run a first workflow | [`QUICKSTART.md`](QUICKSTART.md) |
| Look up public functions | [`API.md`](API.md) |
| Understand package structure | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Understand algorithms | [`ALGORITHMS.md`](ALGORITHMS.md) |
| Use CSV/Excel/LandXML/GSI helpers | [`DATA_FORMATS.md`](DATA_FORMATS.md) |
| Inspect source-backed/regression examples | [`STANDARD_EXAMPLES.md`](STANDARD_EXAMPLES.md) |
| Understand validation and statistical scope | [`VALIDATION.md`](VALIDATION.md) |
| Resolve common questions | [`FAQ.md`](FAQ.md) |
| See current scope and future direction | [`ROADMAP.md`](ROADMAP.md) |
| Prepare TestPyPI/PyPI release | [`RELEASE.md`](RELEASE.md) |
| Prepare repository presentation and public launch | [`LAUNCH.md`](LAUNCH.md) |

## Documentation principles

pySurveying documentation follows four rules:

1. **State conventions before formulas.** Coordinate order, azimuth convention, angle units, and observation standard-deviation units should never be implicit.
2. **Separate reference-backed results from synthetic examples.** A transparent regression dataset is useful, but it should not be presented as an external standard.
3. **Document statistical limitations.** Nonlinear local covariance, robust covariance, free-network datum dependence, and screening thresholds have interpretation limits.
4. **Keep the package scope visible.** The documentation should not imply support for vendor ecosystems or production geodetic workflows that the code does not implement.

## Main source tree

The public API is implemented under `src/pysurveying/` and exposed through `pysurveying.__init__`.

The executable examples under `examples/` and CSV files under `examples/data/` are part of the documentation strategy and are exercised by CI.

## Community documents

Repository-level documents include:

- [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
- [`../SUPPORT.md`](../SUPPORT.md)
- [`../SECURITY.md`](../SECURITY.md)
- [`../CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md)
- [`../CITATION.cff`](../CITATION.cff)
- [`../CHANGELOG.md`](../CHANGELOG.md)

## Language entry points

- Main English README: [`../README.md`](../README.md)
- 简体中文 README: [`../README_zh.md`](../README_zh.md)
