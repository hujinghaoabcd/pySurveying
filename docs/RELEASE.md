# Release and PyPI publishing

pySurveying uses a standard `pyproject.toml` build and is prepared for tokenless Trusted Publishing from GitHub Actions.

## Recommended first-release order

For a first public release, use this order:

1. run the normal CI and local build checks;
2. publish the exact package to **TestPyPI** through the manual `test-publish.yml` workflow;
3. install the TestPyPI package in a fresh environment and smoke-test the import/UI entry point;
4. configure the real PyPI pending publisher and protected `pypi` environment;
5. push the release tag, which triggers `publish.yml`;
6. verify the public PyPI install and create the matching GitHub Release.

This separates package/index configuration problems from the irreversible first production upload.

## One-time TestPyPI setup

TestPyPI uses a separate account from the production PyPI service.

Before the first dry run:

1. Create/sign in to the TestPyPI account that will own the test project.
2. In TestPyPI account publishing settings, add a **pending trusted publisher** with:
   - project name: `pysurveying`
   - GitHub owner: `hujinghaoabcd`
   - repository: `pySurveying`
   - workflow file: `test-publish.yml`
   - environment: `testpypi`
3. In GitHub repository settings, create an environment named `testpypi`.
4. Open **Actions → test-publish → Run workflow**.

The workflow is deliberately manual (`workflow_dispatch`) so ordinary pushes cannot publish to TestPyPI.

## TestPyPI verification

After the TestPyPI workflow succeeds, verify the distribution in a new virtual environment.

Because TestPyPI does not necessarily mirror every dependency, install dependencies from normal PyPI first, then install the package itself from TestPyPI without dependency resolution:

```bash
python -m venv .venv-testpypi
# Windows PowerShell
.\.venv-testpypi\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install numpy scipy pandas pyproj openpyxl
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps pysurveying==0.3.0
python -c "import pysurveying; print(pysurveying.__version__)"
```

To smoke-test the UI package metadata as well:

```bash
python -m pip install streamlit matplotlib
pysurveying-ui
```

## One-time production PyPI setup

Before the first real release:

1. Create/sign in to the PyPI account that will own `pysurveying`.
2. In PyPI account publishing settings, add a **pending trusted publisher** with:
   - PyPI project name: `pysurveying`
   - GitHub owner: `hujinghaoabcd`
   - repository: `pySurveying`
   - workflow file: `publish.yml`
   - environment: `pypi`
3. In GitHub repository settings, create an environment named `pypi`.
4. Require manual approval for the `pypi` environment before deployment.

No long-lived PyPI API token is required when Trusted Publishing is configured.

## Pre-release checks

From a clean checkout:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,ui]"
python -m pytest
python -m ruff check src tests examples
python examples/textbook_parameter_adjustment.py
python examples/example_data_workflow.py
python -m build
python -m twine check dist/*
```

Check the built wheel directly if desired:

```bash
python -m pip install --force-reinstall dist/pysurveying-*.whl
python -c "import pysurveying; print(pysurveying.__version__)"
```

## Version checklist

Before tagging a production release, keep these synchronized:

- `pyproject.toml` → `[project].version`
- `src/pysurveying/__init__.py` → `__version__`
- `README.md` → current version
- `CHANGELOG.md` → release notes

## Publish the production release

The workflow `.github/workflows/publish.yml` publishes only tags matching `v*`.

For version `0.3.0`:

```bash
git pull
git tag v0.3.0
git push origin v0.3.0
```

The workflow will:

1. check out the tagged source;
2. build the source distribution and wheel;
3. upload the distributions as a GitHub Actions artifact;
4. request an OIDC token in the protected `pypi` environment;
5. publish with `pypa/gh-action-pypi-publish`.

## After production publishing

Verify installation from PyPI in a clean environment:

```bash
python -m pip install pysurveying==0.3.0
python -c "import pysurveying; print(pysurveying.__version__)"
```

For the visual interface:

```bash
python -m pip install "pysurveying[ui]==0.3.0"
pysurveying-ui
```

Then create a GitHub Release for tag `v0.3.0` using the corresponding `CHANGELOG.md` section.

## Packaging notes

- The project is pure Python; no platform-specific wheel matrix is required.
- Runtime numerical dependencies remain separate from the optional Streamlit UI dependencies.
- Release publication uses Trusted Publishing rather than repository secrets.
- The package name should be checked again immediately before first production upload because a pending publisher does not reserve a project name.
