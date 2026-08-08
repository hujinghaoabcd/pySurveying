# Release and PyPI publishing

pySurveying uses a standard `pyproject.toml` build and is prepared for tokenless PyPI Trusted Publishing from GitHub Actions.

## One-time PyPI setup

Before the first real release:

1. Create/sign in to the PyPI account that will own `pysurveying`.
2. In PyPI account publishing settings, add a **pending trusted publisher** with:
   - PyPI project name: `pysurveying`
   - GitHub owner: `hujinghaoabcd`
   - repository: `pySurveying`
   - workflow file: `publish.yml`
   - environment: `pypi`
3. In GitHub repository settings, create an environment named `pypi`.
4. Recommended: require manual approval for the `pypi` environment before deployment.

No long-lived PyPI API token is required when Trusted Publishing is configured.

## Pre-release checks

From a clean checkout:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,ui]"
python -m pytest
python -m ruff check src tests examples
python -m build
```

Check the built metadata and install the wheel into a fresh environment if desired:

```bash
python -m pip install dist/pysurveying-*.whl
python -c "import pysurveying; print(pysurveying.__version__)"
```

## Version checklist

Before tagging a release, keep these synchronized:

- `pyproject.toml` → `[project].version`
- `src/pysurveying/__init__.py` → `__version__`
- `README.md` → current version
- `CHANGELOG.md` → release notes

## Publish a release

The workflow `.github/workflows/publish.yml` publishes only tags matching `v*`.

Example for version `0.3.0`:

```bash
git pull
git tag v0.3.0
git push origin v0.3.0
```

The workflow will:

1. check out the tagged source,
2. build the source distribution and wheel,
3. upload the distributions as a GitHub Actions artifact,
4. request an OIDC token in the protected `pypi` environment,
5. publish with `pypa/gh-action-pypi-publish`.

## After publishing

Verify installation from PyPI in a clean environment:

```bash
python -m pip install pysurveying
python -c "import pysurveying; print(pysurveying.__version__)"
```

For the visual interface:

```bash
python -m pip install "pysurveying[ui]"
pysurveying-ui
```

Then create a GitHub Release for the same tag using the corresponding `CHANGELOG.md` section.

## Packaging notes

- The project is pure Python; no platform-specific wheel matrix is required.
- Runtime numerical dependencies remain separate from the optional Streamlit UI dependencies.
- Release publication uses PyPI Trusted Publishing rather than repository secrets.
- The package name currently has no public PyPI project page; verify name availability again immediately before the first publish because package-index state can change.
