from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import numpy as np

from .dual_quaternion import Quaternion, DualQuaternion
from .dq_matrix import split_primal_dual, combine_primal_dual, apply_permutation_rows, matmul


@dataclass
class LUResult:
    p: np.ndarray
    l: np.ndarray
    u: np.ndarray


def _qzero_matrix(n: int, m: int) -> np.ndarray:
    out = np.empty((n, m), dtype=object)
    for i in range(n):
        for j in range(m):
            out[i, j] = Quaternion.zero()
    return out


def _qidentity(n: int) -> np.ndarray:
    out = _qzero_matrix(n, n)
    for i in range(n):
        out[i, i] = Quaternion.one()
    return out


def lu_quaternion(a: np.ndarray, pivoting: bool = True, pivot_tol: float = 1e-12) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    n, m = a.shape
    if n != m:
        raise ValueError("Quaternion LU requires square matrix.")
    a_work = np.empty((n, n), dtype=object)
    for i in range(n):
        for j in range(n):
            a_work[i, j] = a[i, j]
    L = _qidentity(n)
    U = _qzero_matrix(n, n)
    p = np.arange(n)
    for k in range(n):
        if pivoting:
            pivot_row = k
            pivot_norm = a_work[k, k].norm()
            for i in range(k + 1, n):
                cand = a_work[i, k].norm()
                if cand > pivot_norm:
                    pivot_norm = cand
                    pivot_row = i
            if pivot_row != k:
                a_work[[k, pivot_row], :] = a_work[[pivot_row, k], :]
                if k > 0:
                    L[[k, pivot_row], :k] = L[[pivot_row, k], :k]
                p[[k, pivot_row]] = p[[pivot_row, k]]
        for j in range(k, n):
            acc = Quaternion.zero()
            for s in range(k):
                acc = acc + (L[k, s] * U[s, j])
            U[k, j] = a_work[k, j] - acc
        if U[k, k].norm() <= pivot_tol:
            raise ZeroDivisionError(f"Quaternion LU failed due to near-zero pivot at index {k}.")
        for i in range(k + 1, n):
            acc = Quaternion.zero()
            for s in range(k):
                acc = acc + (L[i, s] * U[s, k])
            L[i, k] = (a_work[i, k] - acc) * U[k, k].inverse()
    return p, L, U


def dq_lu(a: np.ndarray, pivoting: bool = True, pivot_tol: float = 1e-12) -> LUResult:
    n, m = a.shape
    if n != m:
        raise ValueError("Dual quaternion LU requires square matrix.")
    ar, ad = split_primal_dual(a)
    p, lr, ur = lu_quaternion(ar, pivoting=pivoting, pivot_tol=pivot_tol)
    adp = apply_permutation_rows(ad, p)
    ld = _qzero_matrix(n, n)
    ud = _qzero_matrix(n, n)
    for j in range(n):
        for i in range(j + 1):
            temp = adp[i, j]
            for k in range(i):
                temp = temp - (lr[i, k] * ud[k, j]) - (ld[i, k] * ur[k, j])
            ud[i, j] = temp
        if ur[j, j].norm() <= pivot_tol:
            raise ZeroDivisionError(f"Dual part solve failed due to near-zero pivot at index {j}.")
        inv_pivot = ur[j, j].inverse()
        for i in range(j + 1, n):
            temp = adp[i, j]
            for k in range(j):
                temp = temp - (lr[i, k] * ud[k, j]) - (ld[i, k] * ur[k, j])
            temp = temp - (lr[i, j] * ud[j, j])
            ld[i, j] = temp * inv_pivot
    l = combine_primal_dual(lr, ld)
    u = combine_primal_dual(ur, ud)
    return LUResult(p=p, l=l, u=u)


def dq_lu_structure_preserving(a: np.ndarray, diagonal_shift: float = 1e-10, pivot_tol: float = 1e-12) -> LUResult:
    n, m = a.shape
    if n != m:
        raise ValueError("Dual quaternion LU requires square matrix.")
    a_reg = np.empty((n, n), dtype=object)
    for i in range(n):
        for j in range(n):
            a_reg[i, j] = a[i, j]
    for i in range(n):
        shifted_primal = a_reg[i, i].primal + Quaternion(diagonal_shift, 0.0, 0.0, 0.0)
        a_reg[i, i] = DualQuaternion(shifted_primal, a_reg[i, i].dual)
    return dq_lu(a_reg, pivoting=False, pivot_tol=pivot_tol)


def reconstruct_from_lu(result: LUResult) -> np.ndarray:
    return matmul(result.l, result.u)


def permuted_original(a: np.ndarray, p: np.ndarray) -> np.ndarray:
    return apply_permutation_rows(a, p)
