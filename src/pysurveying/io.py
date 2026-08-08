from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from .models import AdjustmentResult


def read_csv(path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def read_excel(path, **kwargs) -> pd.DataFrame:
    return pd.read_excel(path, **kwargs)


def normalize_point_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize common point-table column names to ``name, x, y, z`` where possible."""
    aliases = {
        "name": {"name", "point", "point_id", "pointid", "pt", "id", "点名", "点号"},
        "x": {"x", "e", "east", "easting", "横坐标"},
        "y": {"y", "n", "north", "northing", "纵坐标"},
        "z": {"z", "h", "height", "elevation", "高程"},
    }
    rename: dict[str, str] = {}
    lower = {str(column).strip().lower(): column for column in data.columns}
    for target, candidates in aliases.items():
        for candidate in candidates:
            key = candidate.lower()
            if key in lower:
                rename[lower[key]] = target
                break
    return data.rename(columns=rename).copy()


def read_landxml_points(path: str | Path) -> pd.DataFrame:
    """Read ``CgPoint`` coordinates from common LandXML files.

    LandXML commonly stores CgPoint text as northing, easting and optional elevation.
    The returned DataFrame normalizes these to columns ``name, x, y, z`` using
    ``x=easting`` and ``y=northing`` to match the local planar package convention.
    """
    root = ET.parse(path).getroot()
    rows = []
    for element in root.iter():
        if element.tag.split("}")[-1] != "CgPoint":
            continue
        parts = (element.text or "").split()
        if len(parts) < 2:
            continue
        rows.append(
            {
                "name": element.attrib.get("name") or element.attrib.get("oID"),
                "x": float(parts[1]),
                "y": float(parts[0]),
                "z": float(parts[2]) if len(parts) > 2 else np.nan,
            }
        )
    return pd.DataFrame(rows, columns=["name", "x", "y", "z"])


def read_gsi(path: str | Path) -> pd.DataFrame:
    """Best-effort reader for Leica GSI word records.

    This deliberately returns low-level word/value records instead of pretending to
    support every Leica GSI generation and project template.
    """
    rows = []
    pattern = re.compile(r"^(?P<word>\d{2,3})[^+\-]*(?P<value>[+\-]\d+)")
    with open(path, "r", encoding="latin-1") as file:
        for line_number, line in enumerate(file, start=1):
            for token in line.strip().split():
                match = pattern.match(token)
                if match:
                    rows.append(
                        {
                            "line": line_number,
                            "word": match.group("word"),
                            "value": int(match.group("value")),
                            "raw": token,
                        }
                    )
    return pd.DataFrame(rows)


def read_points(path: str | Path, **kwargs) -> pd.DataFrame:
    """Auto-detect a common point-table format from the file extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return normalize_point_columns(read_csv(path, **kwargs))
    if suffix in {".xlsx", ".xlsm"}:
        return normalize_point_columns(read_excel(path, **kwargs))
    if suffix in {".xml", ".landxml"}:
        return read_landxml_points(path)
    if suffix in {".gsi", ".gsi8", ".gsi16"}:
        return read_gsi(path)
    raise ValueError(f"unsupported point/instrument file extension: {suffix}")


def write_points(data: pd.DataFrame, path: str | Path, **kwargs) -> Path:
    """Write a point table to CSV or XLSX."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        data.to_csv(path, index=False, **kwargs)
    elif suffix == ".xlsx":
        data.to_excel(path, index=False, **kwargs)
    else:
        raise ValueError("write_points supports .csv and .xlsx")
    return path


def adjustment_tables(result: AdjustmentResult) -> dict[str, pd.DataFrame]:
    """Convert a generic adjustment result into export-friendly tables."""
    parameters = pd.DataFrame(
        {"index": np.arange(len(result.parameters)), "value": np.asarray(result.parameters)}
    )
    residuals = pd.DataFrame(
        {"index": np.arange(len(result.residuals)), "residual": np.asarray(result.residuals)}
    )
    summary = pd.DataFrame(
        [
            {
                "sigma0": result.sigma0,
                "dof": result.dof,
                "converged": result.converged,
                "iterations": result.iterations,
            }
        ]
    )
    tables = {"summary": summary, "parameters": parameters, "residuals": residuals}

    adjusted_points = result.metadata.get("adjusted_points") if result.metadata else None
    if adjusted_points:
        tables["adjusted_points"] = pd.DataFrame(
            [
                {"name": name, "x": coordinates[0], "y": coordinates[1]}
                for name, coordinates in adjusted_points.items()
            ]
        )
    adjusted_heights = result.metadata.get("adjusted_heights") if result.metadata else None
    if adjusted_heights:
        tables["adjusted_heights"] = pd.DataFrame(
            [{"name": name, "height": value} for name, value in adjusted_heights.items()]
        )
    return tables


def export_adjustment_excel(result: AdjustmentResult, path: str | Path) -> Path:
    """Export adjustment summary, parameters, residuals and adjusted points/heights."""
    path = Path(path)
    if path.suffix.lower() != ".xlsx":
        raise ValueError("export path must end with .xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, table in adjustment_tables(result).items():
            table.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return path
