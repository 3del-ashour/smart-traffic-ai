"""Linear Algebra utilities — owned by Member 4."""

import numpy as np
from config import Direction, IntersectionState


def density_matrix(history: list) -> np.ndarray:
    """Rows = cycles, Columns = N, S, E, W. Returns shape (0, 4) for empty history."""
    if not history:
        return np.zeros((0, 4))
    rows = [[s.densities[d] for d in Direction] for s in history]
    return np.array(rows, dtype=float)


def congestion_norm(state: IntersectionState) -> float:
    """L2 norm of the density vector — overall congestion scalar."""
    v = np.array([state.densities[d] for d in Direction], dtype=float)
    return float(np.linalg.norm(v))


def dominant_flow(matrix: np.ndarray) -> np.ndarray:
    """Eigenvector of the covariance matrix — dominant traffic pattern.

    Returns np.zeros(4) for any invalid, degenerate, or low-variance input.
    """
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != 4 or matrix.shape[0] < 2:
        return np.zeros(4)
    if not np.all(np.isfinite(matrix)):
        return np.zeros(4)
    cov = np.cov(matrix.T)
    vals, vecs = np.linalg.eig(cov)
    real_vals = vals.real
    if real_vals.max() < 1e-10:
        return np.zeros(4)
    return vecs[:, np.argmax(real_vals)].real
