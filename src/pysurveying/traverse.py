from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from .basic import normalize_angle


def _coordinate_increments(
    azimuths: Sequence[float], distances: Sequence[float]
) -> tuple[np.ndarray, np.ndarray]:
    angles = np.radians(np.asarray(azimuths, dtype=float))
    lengths = np.asarray(distances, dtype=float)
    if angles.size != lengths.size:
        raise ValueError("azimuths and distances must have the same length")
    if np.any(lengths <= 0):
        raise ValueError("distances must be positive")
    return lengths * np.sin(angles), lengths * np.cos(angles)


def _bowditch(
    start: Sequence[float],
    target_end: Sequence[float],
    azimuths_deg: Sequence[float],
    distances: Sequence[float],
) -> dict[str, object]:
    x0, y0 = map(float, start[:2])
    xe, ye = map(float, target_end[:2])
    dx, dy = _coordinate_increments(azimuths_deg, distances)
    fx = x0 + float(dx.sum()) - xe
    fy = y0 + float(dy.sum()) - ye
    lengths = np.asarray(distances, dtype=float)
    total = float(lengths.sum())
    cdx = -fx * lengths / total
    cdy = -fy * lengths / total
    adx, ady = dx + cdx, dy + cdy

    coordinates = [(x0, y0)]
    x, y = x0, y0
    for ddx, ddy in zip(adx, ady):
        x += float(ddx)
        y += float(ddy)
        coordinates.append((x, y))

    linear = math.hypot(fx, fy)
    return {
        "coordinates": coordinates,
        "raw_dx": dx,
        "raw_dy": dy,
        "corrections_x": cdx,
        "corrections_y": cdy,
        "misclosure_x": fx,
        "misclosure_y": fy,
        "linear_misclosure": linear,
        "total_length": total,
        "relative_precision": math.inf if linear == 0 else total / linear,
    }


def closed_traverse(
    start: Sequence[float],
    azimuths_deg: Sequence[float],
    distances: Sequence[float],
) -> dict[str, object]:
    """Bowditch adjustment of a geometrically closed traverse."""
    return _bowditch(start, start, azimuths_deg, distances)


def connected_traverse(
    start: Sequence[float],
    end: Sequence[float],
    azimuths_deg: Sequence[float],
    distances: Sequence[float],
) -> dict[str, object]:
    """Bowditch adjustment of a traverse connecting two known points."""
    return _bowditch(start, end, azimuths_deg, distances)


def traverse_azimuths_from_angles(
    start_azimuth_deg: float,
    interior_angles_deg: Sequence[float],
    turn: str = "right",
) -> list[float]:
    """Propagate traverse azimuths from interior angles."""
    azimuths = [normalize_angle(start_azimuth_deg)]
    for angle in interior_angles_deg:
        if turn == "right":
            azimuths.append(normalize_angle(azimuths[-1] + 180.0 - angle))
        elif turn == "left":
            azimuths.append(normalize_angle(azimuths[-1] - 180.0 + angle))
        else:
            raise ValueError("turn must be 'right' or 'left'")
    return azimuths
