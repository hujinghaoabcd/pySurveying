from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np

from .basic import azimuth, distance
from .models import AdjustmentResult, Observation, Point


def _weight_matrix(weights: np.ndarray | Sequence[float] | None, n: int) -> np.ndarray:
    if weights is None:
        return np.eye(n)
    array = np.asarray(weights, dtype=float)
    if array.ndim == 1:
        if array.size != n:
            raise ValueError("weight vector length must equal number of observations")
        return np.diag(array)
    if array.shape != (n, n):
        raise ValueError("P must be an n×n matrix or an n-element weight vector")
    return array


def least_squares(
    A: np.ndarray,
    L: np.ndarray,
    P: np.ndarray | Sequence[float] | None = None,
) -> AdjustmentResult:
    """Weighted linear least squares for ``A x ≈ L``.

    ``P`` may be omitted, supplied as an observation-weight vector, or supplied as
    the full weight matrix. A Moore-Penrose inverse is used so rank-deficient
    educational examples remain inspectable instead of failing with a matrix error.
    """
    A = np.asarray(A, dtype=float)
    L = np.asarray(L, dtype=float).reshape(-1)
    if A.ndim != 2 or A.shape[0] != L.size:
        raise ValueError("A rows must equal the number of observations in L")

    W = _weight_matrix(P, L.size)
    normal = A.T @ W @ A
    rhs = A.T @ W @ L
    x = np.linalg.pinv(normal) @ rhs
    v = A @ x - L
    rank = int(np.linalg.matrix_rank(A))
    dof = int(L.size - rank)
    sigma0 = float(math.sqrt((v @ W @ v) / dof)) if dof > 0 else None
    qxx = np.linalg.pinv(normal)
    covariance = qxx if sigma0 is None else qxx * sigma0**2

    return AdjustmentResult(
        parameters=x,
        residuals=v,
        sigma0=sigma0,
        covariance=covariance,
        dof=dof,
        metadata={"rank": rank, "normal_matrix": normal},
    )


def _unknown_names(points: Mapping[str, Point]) -> list[str]:
    return [name for name, point in points.items() if not point.fixed]


def _pack(points: Mapping[str, Point], names: Sequence[str]) -> np.ndarray:
    return np.array([value for name in names for value in (points[name].x, points[name].y)])


def _point_xy(
    points: Mapping[str, Point], names: Sequence[str], values: np.ndarray, name: str
) -> tuple[float, float]:
    if name not in points:
        raise KeyError(f"unknown point: {name}")
    if points[name].fixed:
        return points[name].x, points[name].y
    index = names.index(name) * 2
    return float(values[index]), float(values[index + 1])


def _angle_difference(calculated: float, observed: float) -> float:
    return (calculated - observed + 180.0) % 360.0 - 180.0


def adjust_control_network(
    points: Sequence[Point],
    observations: Sequence[Observation],
    *,
    max_iterations: int = 20,
    tolerance: float = 1e-7,
    free_network: bool = False,
) -> AdjustmentResult:
    """Adjust a small 2D control network.

    Supported observation kinds:

    - ``distance``: value and sigma use coordinate-distance units.
    - ``direction``/``azimuth``: value and sigma use degrees.
    - ``angle``: value and sigma use degrees; ``from_point`` is the station,
      ``to_point`` the backsight and ``target2`` the foresight.

    For a free network, a minimum-norm pseudoinverse solution is used and the supplied
    approximate coordinates define the practical datum realization.
    """
    point_map = {p.name: Point(p.name, p.x, p.y, p.z, p.fixed) for p in points}
    names = _unknown_names(point_map)
    if not names:
        raise ValueError("network has no unknown points")
    if not observations:
        raise ValueError("network has no observations")
    if not free_network and not any(point.fixed for point in point_map.values()):
        raise ValueError("fixed control is required unless free_network=True")
    if any(obs.sigma <= 0 for obs in observations):
        raise ValueError("all observation sigmas must be positive")

    values = _pack(point_map, names)
    n_parameters = values.size

    def residual_vector(current: np.ndarray) -> np.ndarray:
        rows: list[float] = []
        for obs in observations:
            station = _point_xy(point_map, names, current, obs.from_point)
            target = _point_xy(point_map, names, current, obs.to_point)
            kind = obs.kind.lower()
            if kind == "distance":
                rows.append((distance(station, target) - obs.value) / obs.sigma)
            elif kind in {"direction", "azimuth"}:
                diff = _angle_difference(azimuth(station, target), obs.value)
                rows.append(diff / obs.sigma)
            elif kind == "angle":
                if obs.target2 is None:
                    raise ValueError("angle observation requires target2")
                foresight = _point_xy(point_map, names, current, obs.target2)
                calc = (azimuth(station, foresight) - azimuth(station, target)) % 360.0
                rows.append(_angle_difference(calc, obs.value) / obs.sigma)
            else:
                raise ValueError(f"unsupported observation kind: {obs.kind}")
        return np.asarray(rows, dtype=float)

    converged = False
    jacobian: np.ndarray | None = None
    iteration = 0
    for iteration in range(1, max_iterations + 1):
        residuals = residual_vector(values)
        jacobian = np.empty((residuals.size, n_parameters), dtype=float)
        step = 1e-5
        for column in range(n_parameters):
            plus = values.copy()
            minus = values.copy()
            plus[column] += step
            minus[column] -= step
            jacobian[:, column] = (
                residual_vector(plus) - residual_vector(minus)
            ) / (2.0 * step)

        correction = -np.linalg.pinv(jacobian) @ residuals
        values = values + correction
        if float(np.max(np.abs(correction))) < tolerance:
            converged = True
            break

    residuals = residual_vector(values)
    rank = int(np.linalg.matrix_rank(jacobian)) if jacobian is not None else 0
    dof = int(residuals.size - rank)
    sigma0 = float(math.sqrt((residuals @ residuals) / dof)) if dof > 0 else None
    covariance = None
    if jacobian is not None:
        qxx = np.linalg.pinv(jacobian.T @ jacobian)
        covariance = qxx if sigma0 is None else qxx * sigma0**2

    adjusted_points: dict[str, tuple[float, float]] = {}
    for point in point_map.values():
        if point.fixed:
            adjusted_points[point.name] = (point.x, point.y)
        else:
            adjusted_points[point.name] = _point_xy(point_map, names, values, point.name)

    return AdjustmentResult(
        parameters=values,
        residuals=residuals,
        sigma0=sigma0,
        covariance=covariance,
        dof=dof,
        converged=converged,
        iterations=iteration,
        metadata={
            "point_order": names,
            "adjusted_points": adjusted_points,
            "free_network": free_network,
            "rank": rank,
        },
    )


def adjust_free_network(
    points: Sequence[Point], observations: Sequence[Observation], **kwargs
) -> AdjustmentResult:
    """Minimum-norm 2D free-network adjustment using supplied approximations."""
    free_points = [Point(point.name, point.x, point.y, point.z, False) for point in points]
    return adjust_control_network(free_points, observations, free_network=True, **kwargs)
