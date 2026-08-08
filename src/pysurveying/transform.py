from __future__ import annotations

from collections.abc import Sequence

from pyproj import CRS, Transformer


def transform_coordinates(
    x: float | Sequence[float],
    y: float | Sequence[float],
    from_crs: str | int,
    to_crs: str | int,
    *,
    always_xy: bool = True,
):
    """Transform one coordinate or coordinate arrays between two CRS definitions."""
    transformer = Transformer.from_crs(
        CRS.from_user_input(from_crs),
        CRS.from_user_input(to_crs),
        always_xy=always_xy,
    )
    return transformer.transform(x, y)
