from __future__ import annotations

import math

import numpy as np
from scipy.optimize import least_squares as scipy_least_squares
from scipy.stats import chi2

from .models import AdjustmentResult


def robust_least_squares(
    A: np.ndarray, L: np.ndarray, f_scale: float = 1.0
) -> AdjustmentResult:
    """Solve a linear model using SciPy's Huber robust loss.

    The returned covariance is an approximate local covariance based on the final
    robust Jacobian. It should not be interpreted as classical least-squares
    covariance without qualification.
    """
    A = np.asarray(A, dtype=float)
    L = np.asarray(L, dtype=float).reshape(-1)
    if A.ndim != 2 or A.shape[0] != L.size:
        raise ValueError("A rows must equal len(L)")
    if f_scale <= 0:
        raise ValueError("f_scale must be positive")

    initial = np.linalg.lstsq(A, L, rcond=None)[0]
    solution = scipy_least_squares(
        lambda x: A @ x - L,
        initial,
        loss="huber",
        f_scale=f_scale,
    )
    residuals = A @ solution.x - L
    rank = int(np.linalg.matrix_rank(A))
    dof = int(L.size - rank)
    sigma0 = float(math.sqrt((residuals @ residuals) / dof)) if dof > 0 else None
    covariance = None
    if solution.jac.size:
        qxx = np.linalg.pinv(solution.jac.T @ solution.jac)
        covariance = qxx if sigma0 is None else qxx * sigma0**2

    return AdjustmentResult(
        solution.x,
        residuals,
        sigma0,
        covariance,
        dof,
        solution.success,
        int(solution.nfev),
        metadata={"method": "huber", "f_scale": f_scale, "covariance_note": "approximate"},
    )


def standardized_residuals(result: AdjustmentResult) -> np.ndarray:
    """Return standardized residuals for quality-control screening.

    For results produced by :func:`pysurveying.adjustment.least_squares`, ``Qvv``
    is used so observations with low redundancy are not judged by raw residual
    magnitude alone. For other results a simpler posterior-sigma standardization
    is used as a fallback.
    """
    residuals = np.asarray(result.residuals, dtype=float)
    if residuals.size == 0:
        return residuals

    qvv = result.metadata.get("qvv") if result.metadata else None
    if qvv is not None and result.sigma0 is not None and result.sigma0 > 0:
        qvv = np.asarray(qvv, dtype=float)
        if qvv.shape == (residuals.size, residuals.size):
            scale = result.sigma0 * np.sqrt(np.maximum(np.diag(qvv), 0.0))
            output = np.zeros_like(residuals)
            valid = scale > np.finfo(float).eps
            output[valid] = residuals[valid] / scale[valid]
            return output

    if result.sigma0 is not None and result.sigma0 > 0:
        return residuals / result.sigma0
    sample_sd = float(np.std(residuals, ddof=1)) if residuals.size > 1 else 0.0
    return residuals / sample_sd if sample_sd > 0 else np.zeros_like(residuals)


def redundancy_numbers(result: AdjustmentResult) -> np.ndarray:
    """Return observation redundancy numbers when available."""
    values = result.metadata.get("redundancy_numbers") if result.metadata else None
    if values is None:
        return np.full(np.asarray(result.residuals).size, np.nan)
    return np.asarray(values, dtype=float)


def detect_outliers(result: AdjustmentResult, threshold: float = 3.0) -> list[int]:
    """Return indices whose absolute standardized residual exceeds ``threshold``."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    return np.flatnonzero(np.abs(standardized_residuals(result)) >= threshold).tolist()


def data_snooping(result: AdjustmentResult, threshold: float = 3.0) -> list[dict[str, float | int | bool]]:
    """Return a compact residual-screening table.

    This is a practical standardized-residual screen rather than a full statistical
    multiple-testing implementation of Baarda's data snooping procedure.
    """
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    residuals = np.asarray(result.residuals, dtype=float)
    standardized = standardized_residuals(result)
    redundancy = redundancy_numbers(result)
    rows: list[dict[str, float | int | bool]] = []
    for index, (v, w, r) in enumerate(zip(residuals, standardized, redundancy)):
        rows.append(
            {
                "index": index,
                "residual": float(v),
                "standardized_residual": float(w),
                "redundancy": float(r),
                "flagged": bool(abs(w) >= threshold),
            }
        )
    return rows


def error_ellipse(
    covariance_2x2: np.ndarray, confidence: float = 0.95
) -> dict[str, float]:
    """Return semi-major/minor axes and surveying azimuth of a 2D error ellipse."""
    covariance = np.asarray(covariance_2x2, dtype=float)
    if covariance.shape != (2, 2):
        raise ValueError("covariance_2x2 must be 2×2")
    if not np.allclose(covariance, covariance.T, atol=1e-12):
        raise ValueError("covariance_2x2 must be symmetric")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0.0)
    eigenvectors = eigenvectors[:, order]
    scale = math.sqrt(float(chi2.ppf(confidence, df=2)))
    semi_major = float(scale * math.sqrt(eigenvalues[0]))
    semi_minor = float(scale * math.sqrt(eigenvalues[1]))
    vx, vy = eigenvectors[:, 0]
    theta = float(math.degrees(math.atan2(vx, vy)) % 360.0)
    return {
        "semi_major": semi_major,
        "semi_minor": semi_minor,
        "azimuth": theta,
        "confidence": confidence,
    }
