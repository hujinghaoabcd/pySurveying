import numpy as np
import pandas as pd

from pysurveying.io import adjustment_tables, normalize_point_columns, read_points, write_points
from pysurveying.models import AdjustmentResult


def test_normalize_point_columns():
    data = pd.DataFrame({"点号": ["P1"], "Easting": [10.0], "Northing": [20.0], "高程": [3.0]})
    normalized = normalize_point_columns(data)
    assert list(normalized[["name", "x", "y", "z"]].columns) == ["name", "x", "y", "z"]


def test_csv_point_roundtrip(tmp_path):
    data = pd.DataFrame({"name": ["A", "B"], "x": [1.0, 2.0], "y": [3.0, 4.0]})
    path = tmp_path / "points.csv"
    write_points(data, path)
    loaded = read_points(path)
    pd.testing.assert_frame_equal(loaded, data)


def test_adjustment_tables_include_adjusted_points():
    result = AdjustmentResult(
        parameters=np.array([1.0, 2.0]),
        residuals=np.array([0.1, -0.1]),
        sigma0=0.1,
        covariance=np.eye(2),
        dof=1,
        metadata={"adjusted_points": {"P": (1.0, 2.0)}},
    )
    tables = adjustment_tables(result)
    assert {"summary", "parameters", "residuals", "adjusted_points"} <= set(tables)
    assert tables["adjusted_points"].iloc[0]["name"] == "P"
