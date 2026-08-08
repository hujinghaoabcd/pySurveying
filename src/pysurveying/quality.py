from __future__ import annotations

import math

import numpy as np
from scipy.optimize import least_squares as scipy_least_squares
from scipy.stats import chi2

from .models import AdjustmentResult


def robust_least_squares(
    A: np.ndarray, L: np.ndarray, f_scale: float = 1.0
) -> AdjustmentResult:
    """Solve a linear model using SciPy's Huber robust loss."""
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
    )


def standardized_residuals(result: AdjustmentResult) -> np.ndarray:
    """Return simple residuals standardized by the posterior unit-weight sigma."""
    residuals = np.asarray(result.residuals, dtype=float)
    if residuals.size == 0:
        return residuals
    if result.sigma0 is not None and result.sigma0 > 0:
        return residuals / result.sigma0
    sample_sd = float(np.std(residuals, ddof=1)) if residuals.size > 1 else 0.0
    return residuals / sample_sd if sample_sd > 0 else np.zeros_like(residuals)


def detect_outliers(result: AdjustmentResult, threshold: float = 3.0) -> list[int]:
    """Return indices whose absolute standardized residual exceeds ``threshold``."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    return np.flatnonzero(np.abs(standardized_residuals(result)) >= threshold).tolist()


def error_ellipse(
    covariance_2x2: np.ndarray, confidence: float = 0.95
) -> dict[str, float]:
    """Return semi-major/minor axes and surveying azimuth of a 2D error ellipse."""
    covariance = np.asarray(covariance_2x2, dtype=float)
    if covariance.shape != (2, 2):
        raise ValueError("covariance_2x2 must be 2×2")
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
