## Summary

Describe the problem and the smallest useful change.

## Why this fits pySurveying

Explain how the change fits the lightweight scope in `docs/ROADMAP.md`.

## Numerical / surveying conventions

If applicable, state:

- coordinate convention;
- angle convention/unit;
- distance/height unit;
- observation standard-deviation/weight convention;
- datum/CRS assumptions.

## Validation

Describe how the change was verified. For numerical changes, identify the source of expected values.

- [ ] Added/updated automated tests
- [ ] Added/updated documentation for public behavior
- [ ] `python -m pytest`
- [ ] `python -m ruff check src tests examples`
- [ ] `python examples/textbook_parameter_adjustment.py`
- [ ] `python examples/example_data_workflow.py`
- [ ] `python -m build`
- [ ] `python -m twine check dist/*`

## Reference/source

If a textbook, paper, standard, dataset, or independent software result is used, identify it here and distinguish copied/reference-backed values from newly derived values.

## Screenshots

For GUI changes, include before/after screenshots when useful.

## Scope / compatibility

- [ ] This change does not silently change the documented coordinate or angle convention.
- [ ] This change does not expose private/proprietary survey data.
- [ ] Backward-incompatible API changes are explicitly documented.
