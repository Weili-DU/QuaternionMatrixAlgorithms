import numpy as np


def _validate_basis(w: np.ndarray, name: str = "W") -> None:
    if not isinstance(w, np.ndarray):
        raise TypeError(f"{name} must be numpy.ndarray")
    if w.ndim != 2:
        raise ValueError(f"{name} must be 2D")
    if w.shape[0] == 0 or w.shape[1] == 0:
        raise ValueError(f"{name} must be non-empty")
    if not np.isfinite(w).all():
        raise ValueError(f"{name} contains non-finite values")


def deim_indices(w: np.ndarray) -> np.ndarray:
    _validate_basis(w, "W")
    m, k = w.shape
    if k > m:
        raise ValueError("Number of vectors k cannot exceed m")
    work = w.astype(float).copy()
    s = np.zeros(k, dtype=int)
    for j in range(k):
        s[j] = int(np.argmax(np.abs(work[:, j])))
        if j < k - 1:
            left = work[s[: j + 1], : j + 1]
            rhs = work[s[: j + 1], j + 1]
            coeff = np.linalg.solve(left, rhs)
            work[:, j + 1] = work[:, j + 1] - work[:, : j + 1] @ coeff
    if len(np.unique(s)) != k:
        raise RuntimeError("DEIM selected duplicated indices")
    return s


def _schur_update_inverse(w11_inv: np.ndarray, w12: np.ndarray, w21: np.ndarray, w: float) -> np.ndarray:
    schur = float(w - w21 @ w11_inv @ w12)
    if abs(schur) < 1e-14:
        raise np.linalg.LinAlgError("Schur complement is nearly singular")
    z = 1.0 / schur
    z12 = -(w11_inv @ w12) * z
    z21 = -(w21 @ w11_inv) * z
    z11 = w11_inv + np.outer(w11_inv @ w12, w21 @ w11_inv) * z
    top = np.hstack([z11, z12.reshape(-1, 1)])
    bottom = np.hstack([z21.reshape(1, -1), np.array([[z]])])
    return np.vstack([top, bottom])


def mdeim_indices(w: np.ndarray) -> np.ndarray:
    _validate_basis(w, "W")
    m, k = w.shape
    if k > m:
        raise ValueError("Number of vectors k cannot exceed m")
    work = w.astype(float).copy()
    s = np.zeros(k, dtype=int)
    inv_selected = None
    for j in range(k):
        s[j] = int(np.argmax(np.abs(work[:, j])))
        if j == 0:
            val = work[s[0], 0]
            if abs(val) < 1e-14:
                raise np.linalg.LinAlgError("Selected pivot is nearly zero")
            inv_selected = np.array([[1.0 / val]], dtype=float)
        if j < k - 1:
            if j >= 1:
                w11_inv = inv_selected
                w12 = work[s[:j], j]
                w21 = work[s[j], :j]
                wjj = float(work[s[j], j])
                inv_selected = _schur_update_inverse(w11_inv, w12, w21, wjj)
            coeff = inv_selected @ work[s[: j + 1], j + 1]
            work[:, j + 1] = work[:, j + 1] - work[:, : j + 1] @ coeff
    if len(np.unique(s)) != k:
        raise RuntimeError("mDEIM selected duplicated indices")
    return s
