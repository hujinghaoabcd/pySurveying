# Validation notes

pySurveying is intentionally small, so validation focuses on transparent surveying formulas, reproducible source-backed examples, inspectable synthetic regression cases, and automated tests rather than a large hidden reference dataset.

## Reference-backed numerical checks

The robust-estimation and gross-error-control implementation is organized against the corresponding material in Song Lijie's *测量平差程序设计*:

- Section 1.9: equivalent-weight functions Huber, IGG1 and IGG3
- Section 3.1.5: independent weighted parameter-adjustment numerical example
- Section 3.2.5: correlated-observation parameter-adjustment numerical example
- Section 4.5: robust estimation by iteratively replacing observation weights
- Section 4.7: gross-error detection using standardized residuals and repeated re-adjustment

The implementation follows those computational ideas while using NumPy/SciPy linear algebra instead of reproducing the book's C/C++ matrix routines.

### Section 3.1.5

The repository carries an exact numerical regression using the six printed error equations and independent weights. It verifies:

```text
X = (2, 1, -4)
V = (2, 4, -1, 2, -4, 5)
sigma0 = 6
```

and the printed `Qxx` matrix.

### Section 3.2.5

A second regression uses the textbook's complete 6×6 correlated weight matrix. It verifies:

```text
X = (2, 1, -4)
V = (2, 2, -5, 3, -6, 14)
sigma0 = 6
```

and the same printed `Qxx`. This directly exercises the full-matrix `P` path of `least_squares`, not merely the diagonal-weight shortcut.

A runnable version of both calculations is provided in `examples/textbook_parameter_adjustment.py`.

The scanned source used for this validation supports these parameter-adjustment and robust/gross-error sections. It is **not** used as evidence for traverse, leveling-network, horizontal-control-network, transformation or instrument-format results that are not actually present in the inspected source material.

## External model-convention cross-check

For horizontal directions, pySurveying creates one orientation unknown for each occupied station containing `direction` observations. This matches the practical direction-set convention documented by GNU Gama, where directions at one station share an orientation shift relating observed directions to bearings.

This is a model-convention cross-check, not a claim that pySurveying reproduces GNU Gama's full stochastic model or every supported network option. Details and links are recorded in `docs/STANDARD_EXAMPLES.md`.

## Automated checks

The test suite covers:

1. the Section 3.1.5 independent weighted parameter-adjustment result;
2. the Section 3.2.5 correlated-observation result using the complete printed weight matrix;
3. Huber / IGG1 / IGG3 piecewise equivalent-weight factors;
4. robust IRLS down-weighting and improvement in a contaminated linear example;
5. `Qvv`-based standardized residuals and redundancy numbers;
6. iterative linear-model gross-error screening and re-adjustment;
7. confidence error-ellipse scale and the undirected `[0, 180)` surveying azimuth convention;
8. minimum-norm free-network internal geometry on a distance triangle;
9. final-linearization `Qxx`, `Qvv` and redundancy for a nonlinear distance control network;
10. observation-quality mapping back to raw/normalized/standardized residuals;
11. correct distinction between linear and angular residual units in a mixed distance/azimuth/angle network;
12. gross-distance localization while preserving original observation index;
13. gross-azimuth localization and recovery of the unknown point after re-adjustment;
14. adjustment table/Excel export including quality metadata;
15. `control_network_precision` coordinate sigmas, positional sigma and confidence ellipse;
16. basic coordinate calculations, intersections and transformation round trips;
17. table aliases, CSV round trips, LandXML points and conservative low-level GSI reading;
18. shipped `examples/data/control_*.csv` recovering the transparent control-network point `(40, 30)`;
19. shipped unequal-weight leveling example producing a redundant one-degree-of-freedom network;
20. shipped closed-traverse example closing the adjusted angle sum and returning the Bowditch-adjusted endpoint to the start.

## 0.3.0 release-preparation diagnostic

The Python 3.12 release-preparation diagnostic completed all stages successfully:

```text
install = 0
import = 0
compile = 0
pytest = 0
runnable examples = 0
ruff = 0
build = 0
twine check = 0

52 tests passed
```

The diagnostic also executed both runnable example programs. It built:

```text
pysurveying-0.3.0.tar.gz
pysurveying-0.3.0-py3-none-any.whl
```

and `twine check` passed for both distributions.

Normal CI subsequently remains responsible for the Python 3.10 / 3.11 / 3.12 matrix.

## Important statistical scope

`iterative_data_snooping` and `control_network_data_snooping` implement computational elimination loops, not universal significance-level designs. The caller remains responsible for choosing thresholds appropriate to the observation model, redundancy, false-alarm risk and governing surveying specification.

For nonlinear control networks, `Qxx`, `Qvv`, redundancy numbers and standardized residuals are based on the final local linearization. They should be interpreted as local adjustment diagnostics rather than exact finite-nonlinearity quantities.

Covariance reported after robust equivalent weighting is a local approximation. Classical least-squares covariance interpretation does not transfer unchanged to robust estimates.

For a free 2D network, absolute coordinates are datum-dependent. Validation therefore compares observable internal geometry rather than expecting one unique translated/rotated coordinate realization.

## Remaining professional validation

0.3.0 intentionally freezes feature expansion. Further validation can improve confidence without broadening scope:

- an independently published traverse example with full angular and coordinate closure values;
- an independently published unequal-weight leveling-network reference result;
- an independently published mixed distance/direction/angle control-network result;
- direction-set and horizontal-angle gross-error cases in addition to the current distance/absolute-azimuth cases;
- independent free-network datum comparisons beyond the distance-triangle regression;
- error-ellipse values cross-checked against independent surveying software;
- real LandXML and Leica GSI files for edge-case parser tests.

Such cases should be added only when source data, conventions and expected results are independently interpretable.
