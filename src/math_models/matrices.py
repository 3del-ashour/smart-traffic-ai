"""Linear Algebra utilities — owned by Member 4."""
import numpy as np
from config import Direction, IntersectionState


def density_matrix(history: list) -> np.ndarray:
    rows = [[s.densities[d] for d in Direction] for s in history]
    return np.array(rows)


def congestion_norm(state: IntersectionState) -> float:
    v = np.array([state.densities[d] for d in Direction])
    return float(np.linalg.norm(v))


def dominant_flow(matrix: np.ndarray) -> np.ndarray:
    if matrix.shape[0] < 2:
        return np.zeros(4)
    cov = np.cov(matrix.T)
    vals, vecs = np.linalg.eig(cov)
    return vecs[:, np.argmax(vals.real)].real
