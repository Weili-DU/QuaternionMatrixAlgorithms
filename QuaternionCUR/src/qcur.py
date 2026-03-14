from dataclasses import dataclass

import numpy as np

from .deim import mdeim_indices
from .quaternion_utils import (
    q_fro_norm,
    q_matmul,
    q_pinv,
    quaternion_entry_abs,
    relative_error,
    validate_quaternion_matrix,
)


@dataclass
class QCURResult:
    C: np.ndarray
    U: np.ndarray
    R: np.ndarray
    reconstruction: np.ndarray
    row_indices: np.ndarray
    col_indices: np.ndarray
    rank_estimation: int
    rel_error: float


def _row_basis(a: np.ndarray, k: int) -> np.ndarray:
    m, n, _ = a.shape
    mat = a.reshape(m, 4 * n)
    u, _, _ = np.linalg.svd(mat, full_matrices=False)
    return u[:, :k]


def _col_basis(a: np.ndarray, k: int) -> np.ndarray:
    m, n, _ = a.shape
    mat = np.transpose(a, (1, 0, 2)).reshape(n, 4 * m)
    u, _, _ = np.linalg.svd(mat, full_matrices=False)
    return u[:, :k]


def estimate_rank_by_threshold(a: np.ndarray, c: float, max_rank: int | None = None) -> int:
    validate_quaternion_matrix(a, "A")
    if not (0.0 < c < 1.0):
        raise ValueError("c must be in (0, 1)")
    m, n, _ = a.shape
    mat = a.reshape(m, 4 * n)
    s = np.linalg.svd(mat, compute_uv=False, full_matrices=False)
    energy = s**2
    total = float(np.sum(energy))
    threshold = c * total
    tail = total
    k = 0
    for i in range(len(energy)):
        tail -= float(energy[i])
        k = i + 1
        if tail <= threshold:
            break
    if max_rank is None:
        max_rank = min(m, n)
    k = max(1, min(k, max_rank, m, n))
    return int(k)


def qcur_decompose(a: np.ndarray, k: int, use_fast_u: bool = True, rcond: float = 1e-12) -> QCURResult:
    validate_quaternion_matrix(a, "A")
    m, n, _ = a.shape
    if not isinstance(k, int):
        raise TypeError("k must be int")
    if k < 1 or k > min(m, n):
        raise ValueError("k must satisfy 1 <= k <= min(m,n)")
    if not np.isfinite(rcond) or rcond <= 0:
        raise ValueError("rcond must be positive and finite")
    w = _row_basis(a, k)
    v = _col_basis(a, k)
    row_idx = mdeim_indices(w)
    col_idx = mdeim_indices(v)
    cmat = a[:, col_idx, :]
    rmat = a[row_idx, :, :]
    if use_fast_u:
        core = a[row_idx][:, col_idx, :]
        umat = q_pinv(core, rcond=rcond)
    else:
        umat = q_matmul(q_matmul(q_pinv(cmat, rcond=rcond), a), q_pinv(rmat, rcond=rcond))
    recon = q_matmul(q_matmul(cmat, umat), rmat)
    err = relative_error(a, recon)
    if quaternion_entry_abs(recon).max() > quaternion_entry_abs(a).max() * 20 + 1e-8:
        raise RuntimeError("Numerical instability detected in reconstruction")
    return QCURResult(
        C=cmat,
        U=umat,
        R=rmat,
        reconstruction=recon,
        row_indices=row_idx,
        col_indices=col_idx,
        rank_estimation=k,
        rel_error=err,
    )


def qcur_auto(a: np.ndarray, c: float, max_rank: int | None = None, use_fast_u: bool = True, rcond: float = 1e-12) -> QCURResult:
    validate_quaternion_matrix(a, "A")
    k = estimate_rank_by_threshold(a, c=c, max_rank=max_rank)
    res = qcur_decompose(a, k=k, use_fast_u=use_fast_u, rcond=rcond)
    if res.rank_estimation != k:
        raise RuntimeError("Internal rank mismatch")
    if q_fro_norm(res.reconstruction) <= 0:
        raise RuntimeError("Invalid reconstruction")
    return res
