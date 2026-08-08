# Survey data formats

pySurveying separates **file parsing**, **table normalization**, and **surveying algorithms**. Importers return pandas DataFrames; calculation code consumes explicit `Point`, `Observation`, or `LevelObservation` objects.

The current release keeps file-format support intentionally conservative.

## 1. Point tables

A normalized point table uses:

```text
name,x,y,z,fixed
```

Only `name`, `x`, and `y` are required for planar work.

Example:

```csv
name,x,y,z,fixed
A,0.0,0.0,,true
B,100.0,0.0,,true
C,0.0,100.0,,true
P,39.0,31.0,,false
```

### Recognized aliases

`normalize_point_columns()` recognizes common aliases:

| Normalized | Common aliases |
| --- | --- |
| `name` | `name`, `point`, `point_id`, `pointid`, `pt`, `id`, `点名`, `点号` |
| `x` | `x`, `e`, `east`, `easting`, `横坐标` |
| `y` | `y`, `n`, `north`, `northing`, `纵坐标` |
| `z` | `z`, `h`, `height`, `elevation`, `高程` |
| `fixed` | `fixed`, `control`, `known`, `固定`, `已知` |

String values such as `true`, `yes`, `fixed`, `known`, `是`, and `已知` are treated as true for the `fixed` field.

Convert a DataFrame to domain objects:

```python
import pandas as pd
from pysurveying import points_from_dataframe

points = points_from_dataframe(pd.read_csv("examples/data/control_points.csv"))
```

## 2. Control-network observation tables

The normalized observation schema is:

```text
kind,from_point,to_point,target2,value,sigma
```

Required fields:

```text
kind
from_point
to_point
value
```

Optional fields:

```text
target2
sigma
```

If `sigma` is omitted, it defaults to `1.0`.

Example distance network:

```csv
kind,from_point,to_point,target2,value,sigma
distance,A,P,,50.0,0.01
distance,B,P,,67.08203932499369,0.01
distance,C,P,,80.62257748298549,0.01
```

### Observation kinds

#### `distance`

```text
from_point -> to_point
value = observed distance
sigma = distance standard deviation in coordinate units
```

#### `azimuth`

```text
from_point -> to_point
value = absolute surveying azimuth in degrees
sigma = angular standard deviation in degrees
```

#### `direction`

```text
from_point = occupied station
to_point = target
value = observed circle direction in degrees
sigma = angular standard deviation in degrees
```

All `direction` observations from one occupied station share an estimated orientation unknown.

#### `angle`

```text
from_point = station
to_point   = backsight
target2    = foresight
value      = observed horizontal angle in degrees
sigma      = angular standard deviation in degrees
```

### Recognized observation aliases

| Normalized | Common aliases |
| --- | --- |
| `kind` | `kind`, `type`, `observation`, `观测类型` |
| `from_point` | `from_point`, `from`, `station`, `测站`, `起点` |
| `to_point` | `to_point`, `to`, `target`, `照准点`, `终点` |
| `target2` | `target2`, `foresight`, `前视`, `前视点` |
| `value` | `value`, `observed`, `measurement`, `观测值` |
| `sigma` | `sigma`, `std`, `stdev`, `标准差`, `中误差` |

Convert a table with:

```python
from pysurveying import observations_from_dataframe

observations = observations_from_dataframe(table)
```

## 3. Leveling observation tables

The normalized leveling schema is:

```text
from_point,to_point,height_difference,sigma
```

The sign convention is:

```text
height_difference = H_to - H_from
```

Example:

```csv
from_point,to_point,height_difference,sigma
BM,A,1.0000,0.0010
A,B,2.0000,0.0020
BM,B,3.0010,0.0015
```

Recognized aliases:

| Normalized | Common aliases |
| --- | --- |
| `from_point` | `from_point`, `from`, `start`, `后视点`, `起点` |
| `to_point` | `to_point`, `to`, `end`, `前视点`, `终点` |
| `height_difference` | `height_difference`, `dh`, `delta_h`, `高差` |
| `sigma` | `sigma`, `std`, `stdev`, `标准差`, `中误差` |

Convert with:

```python
from pysurveying import level_observations_from_dataframe

observations = level_observations_from_dataframe(table)
```

## 4. CSV and Excel

`read_points()` accepts:

```text
.csv
.xlsx
.xlsm
```

and normalizes common point-table headers where possible.

```python
from pysurveying import read_points

points_table = read_points("points.csv")
```

`write_points()` writes:

```text
.csv
.xlsx
```

```python
from pysurveying import write_points

write_points(points_table, "normalized_points.xlsx")
```

For observation tables, normal pandas `read_csv()` / `read_excel()` plus the conversion helpers are usually clearer because point tables and observation tables have different schemas.

## 5. LandXML

`read_landxml_points()` reads `CgPoint` elements.

LandXML point text is interpreted as:

```text
northing easting [elevation]
```

The returned table uses:

```text
name
x = easting
y = northing
z = elevation
```

Only point extraction is currently implemented. The parser does **not** silently interpret:

- alignments;
- parcels;
- surfaces;
- survey observations;
- vendor-specific extensions.

That limitation is intentional.

## 6. Leica GSI

`read_gsi()` is intentionally a low-level reader.

It tokenizes Leica-style GSI words and returns records such as:

```text
line
word
value
raw
```

Example conceptual result:

```text
line=1, word=11, value=1, raw="11....+00000001"
```

The current implementation does **not** claim universal interpretation of every:

- GSI8/GSI16 generation;
- word index;
- unit flag;
- total-station configuration;
- project template;
- vendor firmware variant.

Supported extensions through `read_points()` are:

```text
.gsi
.gsi8
.gsi16
```

Project-specific conversion from GSI words into surveying observations should only be added when representative real instrument files and documented meanings are available.

## 7. Generic instrument exports

Many total stations/data collectors can export delimited point tables.

If a device can export a CSV/XLSX table containing recognizable point/easting/northing/elevation fields, prefer:

```text
instrument export
→ CSV/XLSX
→ read_points / normalize_point_columns
→ Point objects
```

instead of adding a vendor parser solely because the file originated from a particular instrument brand.

## 8. Adjustment result export

`adjustment_tables()` converts an `AdjustmentResult` into pandas tables.

Depending on available metadata, sheets/tables can include:

- summary;
- parameters;
- residuals;
- raw observation-unit residuals;
- standardized residuals;
- redundancy numbers;
- robust weights;
- observation kinds;
- adjusted points;
- adjusted heights.

Write an Excel workbook with:

```python
from pysurveying import export_adjustment_excel

export_adjustment_excel(result, "adjustment.xlsx")
```

The workbook is a convenient exchange/reporting product, **not a legal survey-record format**.

## 9. Example files in the repository

The `examples/data/` directory contains:

```text
control_points.csv
control_observations.csv
leveling_fixed.csv
leveling_observations.csv
traverse_angles.csv
common_points.csv
```

These files are intentionally small and human-readable, and automated tests execute them.

## 10. Adding another file format

A new reader should:

1. parse only documented or independently verified fields;
2. retain raw identifiers/records when useful;
3. keep parser logic separate from adjustment algorithms;
4. normalize the parsed result through a clear table/domain-object boundary;
5. include a small representative fixture and regression test;
6. document units and axis ordering;
7. avoid claiming universal manufacturer compatibility from one sample file;
8. include only test data that may legally be redistributed.

## 11. Current release boundary

Instrument-format expansion is frozen for the `0.3.0` release-preparation cycle. The priority is reliable documentation and validation of the formats already present.
