from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def leveling_route(
    start_height: float,
    height_differences: Sequence[float],
    *,
    end_height: float | None = None,
    lengths: Sequence[float] | None = None,
) -> dict[str, object]:
    """Adjust a closed or connected leveling route by proportional correction.

    If ``lengths`` is omitted, equal correction per section is used. If ``end_height``
    is omitted, the route is treated as closing back to ``start_height``.
    """
    dh = np.asarray(height_differences, dtype=float)
    if dh.size == 0:
        raise ValueError("height_differences cannot be empty")
    if lengths is None:
        basis = np.ones(dh.size)
    else:
        basis = np.asarray(lengths, dtype=float)
        if basis.size != dh.size or np.any(basis <= 0):
            raise ValueError("lengths must be positive and match height_differences")

    target = float(start_height if end_height is None else end_height)
    raw_end = float(start_height + dh.sum())
    misclosure = raw_end - target
    corrections = -misclosure * basis / basis.sum()
    adjusted = dh + corrections

    heights = [float(start_height)]
    for value in adjusted:
        heights.append(heights[-1] + float(value))

    return {
        "misclosure": misclosure,
        "corrections": corrections,
        "adjusted_height_differences": adjusted,
        "heights": heights,
        "raw_end_height": raw_end,
        "target_end_height": target,
    }
