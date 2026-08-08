from __future__ import annotations

from collections.abc import Sequence

from .basic import azimuth, distance, forward_coordinate


def polar_stakeout(
    station: Sequence[float], target: Sequence[float]
) -> dict[str, float]:
    """Return stakeout azimuth and horizontal distance from station to target."""
    return {"azimuth": azimuth(station, target), "distance": distance(station, target)}


def offset_point(
    start: Sequence[float],
    end: Sequence[float],
    chainage: float,
    offset: float = 0.0,
) -> tuple[float, float]:
    """Point at chainage along a straight baseline with signed right-hand offset."""
    line_azimuth = azimuth(start, end)
    x, y = forward_coordinate(
        float(start[0]), float(start[1]), line_azimuth, chainage
    )
    if offset == 0:
        return x, y
    side_azimuth = line_azimuth + (90.0 if offset >= 0 else -90.0)
    return forward_coordinate(x, y, side_azimuth, abs(offset))


def slope(horizontal_distance: float, height_difference: float, percent: bool = True) -> float:
    """Compute longitudinal slope as ratio or percent."""
    if horizontal_distance == 0:
        raise ValueError("horizontal_distance cannot be zero")
    value = height_difference / horizontal_distance
    return value * 100.0 if percent else value


def polygon_area(points: Sequence[Sequence[float]]) -> float:
    """Planar polygon area by the shoelace formula."""
    if len(points) < 3:
        raise ValueError("at least three points are required")
    area = 0.0
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        area += (
            float(point[0]) * float(next_point[1])
            - float(next_point[0]) * float(point[1])
        )
    return abs(area) / 2.0
