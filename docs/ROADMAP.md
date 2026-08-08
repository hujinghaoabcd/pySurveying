# Roadmap

pySurveying follows a **small-core, high-confidence** roadmap. New modules are not added simply to make the feature list longer.

## Current target: 0.3.0

The 0.3.0 cycle is a release-quality cycle rather than a feature-expansion cycle.

### Complete / in place

- basic coordinate calculations and angle conversion;
- forward/distance intersection and orientation resection;
- closed and connected traverse workflows;
- angular closure plus Bowditch coordinate adjustment;
- leveling route and weighted leveling-network adjustment;
- weighted linear least squares with diagonal/full weight matrices;
- 2D control-network adjustment for distance, azimuth, direction, and angle observations;
- minimum-norm free-network adjustment;
- Huber robust control-network adjustment;
- Huber / IGG1 / IGG3 linear IRLS;
- `Qxx`, `Qvv`, redundancy, standardized residuals, and gross-error screening;
- point precision and confidence error ellipses;
- CRS, ECEF/ENU, similarity, and affine transformations;
- common lightweight engineering helpers;
- CSV/Excel/LandXML/GSI-oriented IO helpers;
- Streamlit GUI;
- textbook-backed least-squares regressions;
- executable example datasets;
- API/validation/release documentation;
- TestPyPI and PyPI publishing workflows.

### 0.3.0 release checklist

- [x] freeze major feature scope;
- [x] polish README first screen and quick start;
- [x] add API reference;
- [x] add FAQ and roadmap;
- [x] add reusable example datasets;
- [x] add source-backed standard-example documentation;
- [x] add contribution/community files;
- [x] add citation metadata;
- [x] validate wheel/sdist metadata with `twine check`;
- [x] prepare TestPyPI-first publishing workflow;
- [ ] configure TestPyPI Trusted Publisher and run first dry release;
- [ ] install the TestPyPI package in a clean environment;
- [ ] configure production PyPI Trusted Publisher;
- [ ] publish the first production release;
- [ ] create the matching GitHub Release;
- [ ] add a repository social-preview image;
- [ ] add 1–3 clean GUI screenshots / short demo media to the README.

## After 0.3.0

Post-release work should prioritize user feedback, validation, and API stability.

### Validation before expansion

Preferred additions:

- independent published traverse reference cases;
- independent unequal-weight leveling reference cases;
- independently published mixed horizontal-network examples;
- direction-set and horizontal-angle gross-error cases;
- cross-checks against independent surveying software for point covariance/error ellipses;
- real-world LandXML/GSI edge-case files with clear redistribution rights.

### Documentation quality

- API examples for every public function family;
- more worked examples that explain the surveying model, not only the code;
- troubleshooting cases from real user issues;
- bilingual documentation where it materially helps users.

### API stability

Before 1.0, review:

- naming consistency;
- result metadata keys;
- exception behavior;
- units/conventions documentation;
- backward compatibility expectations.

## Explicitly out of scope for the current roadmap

The following are not planned merely to make pySurveying larger:

- full vendor-by-vendor total-station ecosystems;
- GNSS PPP/RTK engines;
- road/rail alignment design systems;
- earthwork-volume platforms;
- deformation-monitoring platforms;
- photogrammetry;
- point-cloud processing;
- SLAM;
- GIS desktop functionality;
- replacement of mature full geodetic production suites.

If future user demand justifies one of these areas, it should normally be considered as a separate package or a clearly optional extension rather than expanding the lightweight core without limit.

## 1.0 definition

A future `1.0.0` should mean **API confidence**, not “every surveying function exists.” A realistic 1.0 bar is:

- stable public function names and result structures;
- clear unit/coordinate conventions;
- strong regression coverage;
- externally cross-checked representative adjustment cases;
- reliable packaging and documentation;
- known limitations stated explicitly.
