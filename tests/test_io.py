import numpy as np
import pandas as pd

from pysurveying.io import (
    adjustment_tables,
    export_adjustment_excel,
    level_observations_from_dataframe,
    normalize_point_columns,
    observations_from_dataframe,
    points_from_dataframe,
    read_points,
    write_points,
)
from pysurveying.models import AdjustmentResult


def test_normalize_point_columns():
    data = pd.DataFrame(
        {"点号": ["P1"], "Easting": [10.0], "Northing": [20.0], "高程": [3.0]}
    )
    normalized = normalize_point_columns(data)
    assert list(normalized[["name", "x", "y", "z"]].columns) == ["name", "x", "y", "z"]


def test_points_from_dataframe_handles_aliases_and_fixed():
    data = pd.DataFrame(
        {
            "点号": ["A", "P"],
            "Easting": [100.0, 120.0],
            "Northing": [200.0, 230.0],
            "高程": [5.0, np.nan],
            "已知": ["是", "否"],
        }
    )
    points = points_from_dataframe(data)
    assert points[0].name == "A"
    assert points[0].fixed
    assert points[0].z == 5.0
    assert not points[1].fixed
    assert points[1].z is None


def test_observations_from_dataframe_aliases():
    data = pd.DataFrame(
        {
            "观测类型": ["distance", "angle"],
            "测站": ["A", "P"],
            "照准点": ["P", "A"],
            "前视点": ["", "B"],
            "观测值": [50.0, 45.0],
            "中误差": [0.01, 0.001],
        }
    )
    observations = observations_from_dataframe(data)
    assert observations[0].kind == "distance"
    assert observations[0].target2 is None
    assert observations[1].target2 == "B"
    assert observations[1].sigma == 0.001


def test_level_observations_from_dataframe_aliases():
    data = pd.DataFrame(
        {
            "起点": ["BM", "A"],
            "终点": ["A", "B"],
            "高差": [1.0, 2.0],
            "标准差": [0.001, 0.002],
        }
    )
    observations = level_observations_from_dataframe(data)
    assert observations[0].from_point == "BM"
    assert observations[0].height_difference == 1.0
    assert observations[1].sigma == 0.002


def test_csv_point_roundtrip(tmp_path):
    data = pd.DataFrame({"name": ["A", "B"], "x": [1.0, 2.0], "y": [3.0, 4.0]})
    path = tmp_path / "points.csv"
    write_points(data, path)
    loaded = read_points(path)
    pd.testing.assert_frame_equal(loaded, data)


def test_landxml_points(tmp_path):
    path = tmp_path / "points.xml"
    path.write_text(
        """<?xml version="1.0"?>
<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2">
  <CgPoints>
    <CgPoint name="P1">2000.0 1000.0 25.0</CgPoint>
  </CgPoints>
</LandXML>
""",
        encoding="utf-8",
    )
    loaded = read_points(path)
    assert loaded.iloc[0]["name"] == "P1"
    assert loaded.iloc[0]["x"] == 1000.0
    assert loaded.iloc[0]["y"] == 2000.0
    assert loaded.iloc[0]["z"] == 25.0


def test_gsi_low_level_reader(tmp_path):
    path = tmp_path / "sample.gsi"
    path.write_text("11....+00000001 81....+00123456\n", encoding="latin-1")
    loaded = read_points(path)
    assert loaded["word"].tolist() == ["11", "81"]
    assert loaded["value"].tolist() == [1, 123456]


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


def test_adjustment_tables_include_quality_metadata():
    result = AdjustmentResult(
        parameters=np.array([1.0]),
        residuals=np.array([0.5, -0.5]),
        sigma0=1.0,
        covariance=np.eye(1),
        dof=1,
        metadata={
            "rank": 1,
            "qvv": np.diag([0.25, 0.25]),
            "redundancy_numbers": np.array([0.5, 0.5]),
            "raw_residuals": np.array([0.01, -0.01]),
            "observation_kinds": ["distance", "distance"],
            "robust_weights": np.array([1.0, 0.8]),
        },
    )
    tables = adjustment_tables(result)
    residuals = tables["residuals"]
    assert {
        "residual_observation_unit",
        "kind",
        "redundancy",
        "robust_weight",
        "standardized_residual",
    } <= set(residuals.columns)
    assert np.allclose(residuals["standardized_residual"], [1.0, -1.0])
    assert tables["summary"].iloc[0]["redundancy_sum"] == 1.0


def test_export_adjustment_excel(tmp_path):
    result = AdjustmentResult(
        parameters=np.array([1.0]),
        residuals=np.array([0.1, -0.1]),
        sigma0=0.1,
        covariance=np.eye(1),
        dof=1,
        metadata={"adjusted_heights": {"A": 10.0}},
    )
    path = export_adjustment_excel(result, tmp_path / "result.xlsx")
    workbook = pd.ExcelFile(path)
    assert {"summary", "parameters", "residuals", "adjusted_heights"} <= set(
        workbook.sheet_names
    )