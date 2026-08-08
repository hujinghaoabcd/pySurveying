from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd


def read_csv(path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def read_excel(path, **kwargs) -> pd.DataFrame:
    return pd.read_excel(path, **kwargs)


def read_landxml_points(path: str | Path) -> pd.DataFrame:
    """Read ``CgPoint`` coordinates from common LandXML files.

    LandXML commonly stores CgPoint text as northing, easting and optional elevation.
    The returned DataFrame normalizes these to columns ``name, x, y, z``.
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
                "z": float(parts[2]) if len(parts) > 2 else None,
            }
        )
    return pd.DataFrame(rows)


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
