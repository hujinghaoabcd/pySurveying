# Contributing to pySurveying

Thanks for helping improve pySurveying. The project values **correctness, inspectability, focused scope, and reproducible examples** more than feature count.

## Good contributions

Especially useful contributions include:

- bug fixes with a minimal reproducible test;
- independent surveying reference examples with clear source/convention information;
- numerical-stability improvements;
- documentation clarifications;
- additional unit/regression tests;
- small API improvements that preserve the lightweight design;
- real example files that may legally be redistributed;
- GUI usability improvements that do not duplicate the core logic.

Large new subsystems should be discussed first.

## Scope guardrails

Before proposing a major feature, read [`docs/ROADMAP.md`](docs/ROADMAP.md).

The current release cycle intentionally does not expand into a complete vendor-format ecosystem, GNSS PPP/RTK, road alignment, earthwork, deformation monitoring, photogrammetry, point clouds, SLAM, or a desktop GIS platform.

## Development setup

```bash
git clone https://github.com/hujinghaoabcd/pySurveying.git
cd pySurveying
python -m venv .venv
```

Activate the environment, then:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,ui]"
```

## Before submitting a change

Run:

```bash
python -m pytest
python -m ruff check src tests examples
python examples/textbook_parameter_adjustment.py
python examples/example_data_workflow.py
python -m build
python -m twine check dist/*
```

For GUI changes, also run:

```bash
pysurveying-ui
```

and exercise the affected page manually.

## Numerical changes

Changes to adjustment, quality-control, transformation, or precision routines should include tests that answer:

1. What model/convention is being implemented?
2. What are the units?
3. What is the expected numerical result?
4. Where does that expected result come from?
5. What happens in a degenerate or invalid case?

Prefer transparent small datasets over opaque large fixtures.

## Reference examples

If a regression is based on a textbook, paper, specification, or other external source, document:

- title/source;
- section/table/example number where possible;
- observation and coordinate conventions;
- exact values copied from the source;
- any conversion performed by the test;
- which expected outputs are source-backed and which are derived by the test.

Do not label a synthetic example as a published standard.

## Coordinate conventions

Local planar helpers use:

```text
+Y = North
+X = East
Azimuth = clockwise from North
```

Public surveying angles are decimal degrees unless documented otherwise.

A contribution that introduces another convention must make the boundary explicit.

## API style

The public API is intentionally functions-first.

Prefer:

- small functions;
- plain NumPy/pandas-compatible inputs where appropriate;
- compact dataclasses for domain records;
- explicit units and conventions;
- reusable core logic independent of Streamlit.

Avoid adding a framework layer unless it solves a demonstrated problem.

## Pull requests

A useful pull request should contain:

- a concise problem statement;
- the proposed behavior;
- tests;
- documentation changes when public behavior changes;
- any numerical/reference source needed to review the result.

Keep unrelated refactors out of focused fixes when possible.

## Commit messages

Use short imperative messages, for example:

```text
Fix direction residual normalization
Add unequal-weight leveling reference case
Clarify free-network datum notes
```

## Reporting bugs

Use the bug-report template and include:

- pySurveying version/commit;
- Python version;
- operating system;
- smallest reproducible input;
- expected behavior;
- actual behavior;
- units and coordinate/angle conventions.

## Security issues

Do not publish exploit details in a public issue. See [`SECURITY.md`](SECURITY.md).

## Conduct

Participation in this project is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
