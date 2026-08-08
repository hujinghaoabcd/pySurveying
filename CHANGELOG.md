# Changelog

All notable changes to pySurveying are recorded here.

## 0.2.1

- added final-linearization `Qvv` and observation redundancy numbers for nonlinear 2D control networks
- added per-observation control-network quality tables with raw, normalized and standardized residuals
- added iterative control-network gross-error localization while preserving original observation indices
- added gross-error regression tests for both distance and azimuth observations
- added Huber / IGG1 / IGG3 equivalent-weight robust linear adjustment workflow
- added `control_network_precision` for coordinate standard deviations and confidence error ellipses
- normalized error-ellipse major-axis azimuth to the undirected surveying interval `[0, 180)`
- expanded adjustment Excel exports with residual-quality diagnostics
- added exact textbook regressions for independent and correlated parameter adjustment from 宋力杰《测量平差程序设计》
- expanded validation documentation and runnable control-network quality example

## 0.2.0

- added 2D control-network adjustment for distance, azimuth, direction and horizontal-angle observations
- added station-orientation unknowns for direction sets
- added minimum-norm 2D free-network adjustment
- added Huber robust network adjustment and practical residual screening
- added leveling-network least-squares adjustment
- added traverse angular closure and Bowditch coordinate adjustment
- added WGS84/ECEF/ENU and 2D similarity/affine coordinate transformations
- expanded engineering-survey helpers
- added CSV/Excel/LandXML/Leica GSI helpers and Excel result export
- added Streamlit visual interface and automated CI/build checks
