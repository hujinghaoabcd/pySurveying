# Survey data formats

pySurveying separates data parsing from surveying algorithms. Importers return pandas DataFrames; calculation code consumes explicit `Point`, `Observation`, or `LevelObservation` objects.

## CSV and Excel

`read_points()` accepts `.csv`, `.xlsx`, and `.xlsm` files and normalizes common point-table headers where possible.

Recognized aliases include:

| Normalized | Common aliases |
|---|---|
| `name` | name, point, point_id, pt, id, 点名, 点号 |
| `x` | x, e, east, easting, 横坐标 |
| `y` | y, n, north, northing, 纵坐标 |
| `z` | z, h, height, elevation, 高程 |

`write_points()` writes CSV or XLSX.

## LandXML

`read_landxml_points()` reads `CgPoint` elements. LandXML point text is interpreted as:

```text
northing easting [elevation]
```

The returned table uses:

```text
name, x=easting, y=northing, z=elevation
```

Only point extraction is currently implemented; alignments, parcels, surfaces, observations, and vendor-specific extensions are not silently interpreted.

## Leica GSI

`read_gsi()` is intentionally conservative. It tokenizes Leica-style GSI words and returns low-level records:

```text
line, word, value, raw
```

This avoids pretending that all GSI8/GSI16 instrument configurations, unit flags, word indexes, and project templates are identical. Project-specific conversion from GSI words into observations should be added only when representative instrument files are available.

Supported extensions through `read_points()` are:

```text
.gsi
.gsi8
.gsi16
```

## Generic instrument exports

Many total stations and data collectors can export delimited point tables. If the export is CSV/XLSX with identifiable point/easting/northing/elevation fields, use `read_points()` and column normalization rather than adding a brand-specific parser.

## Adjustment export

`export_adjustment_excel()` writes an `.xlsx` workbook containing available result tables:

- summary
- parameters
- residuals
- adjusted points
- adjusted heights

The workbook is intended as a simple exchange/reporting product, not a legal survey record format.

## Adding another instrument

A new reader should:

1. parse only documented or verified fields;
2. retain raw identifiers/records when useful;
3. normalize output separately from the parser;
4. include a small representative fixture and regression test;
5. avoid embedding instrument parsing logic inside adjustment algorithms.
