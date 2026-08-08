# Security policy

## Supported versions

Before the first stable release, security fixes are applied to the current development/release line on `main`.

| Version | Supported |
| --- | --- |
| 0.3.x / current `main` | Yes |
| Older pre-release versions | Best effort only |

## Reporting a vulnerability

Please **do not open a public GitHub issue containing exploit details, credentials, private data, or a reproducible attack**.

Preferred reporting path:

1. use GitHub's private vulnerability-reporting / security-advisory interface for this repository when it is available;
2. if that interface is not available, contact the maintainer privately through the GitHub account associated with this repository and provide only enough public information to establish contact.

A useful private report includes:

- affected pySurveying version/commit;
- affected component;
- impact;
- minimal reproduction;
- whether untrusted files/input are required;
- suggested mitigation if known.

## Security scope

pySurveying is primarily a local scientific-computing package. Security-relevant areas include:

- parsing uploaded/user-supplied data files;
- spreadsheet/XML handling;
- Streamlit file uploads;
- packaging and release workflows;
- dependency supply-chain behavior.

## Data-file caution

Do not treat untrusted instrument/XML/spreadsheet files as inherently safe. pySurveying does not provide a malware sandbox or a security boundary around third-party parser dependencies.

## Release integrity

Production publishing is configured through GitHub Actions and PyPI Trusted Publishing so that a long-lived PyPI API token does not need to be stored in the repository.
