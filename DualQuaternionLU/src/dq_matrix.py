from __future__ import annotations

from typing import Tuple
import numpy as np

from .dual_quaternion import Quaternion, DualQuaternion


def zeros_matrix(n: int, m: int) -> np.ndarray:
    out = np.empty((n, m), dtype=object)
    for i in range(n):
        for j in range(m):
            out[i, j] = DualQuaternion.zero()
    return out


def identity_matrix(n: int) -> np.ndarray:
    out = zeros_matrix(n, n)
    for i in range(n):
        out[i, i] = DualQuaternion.one()
    return out


def random_quaternion(rng: np.random.Generator, scale: float = 1.0) -> Quaternion:
    v = rng.normal(loc=0.0, scale=scale, size=4)
    return Quaternion(float(v[0]), float(v[1]), float(v[2]), float(v[3]))


def random_dual_quaternion(rng: np.random.Generator, scale: float = 1.0, dual_scale: float = 1.0) -> DualQuaternion:
    return DualQuaternion(random_quaternion(rng, scale=scale), random_quaternion(rng, scale=dual_scale))


def random_matrix(n: int, rng: np.random.Generator, scale: float = 0.2, dual_scale: float = 0.05) -> np.ndarray:
    out = zeros_matrix(n, n)
    for i in range(n):
        row_norm = 0.0
        for j in range(n):
            out[i, j] = random_dual_quaternion(rng, scale=scale, dual_scale=dual_scale)
            row_norm += out[i, j].primal_norm()
        diag_boost = Quaternion(1.0 + row_norm, 0.0, 0.0, 0.0)
        out[i, i] = DualQuaternion(out[i, i].primal + diag_boost, out[i, i].dual)
    return out


def banded_structured_matrix(n: int, rng: np.random.Generator, bandwidth: int = 1) -> np.ndarray:
    out = zeros_matrix(n, n)
    for i in range(n):
        for j in range(max(0, i - bandwidth), min(n, i + bandwidth + 1)):
            out[i, j] = random_dual_quaternion(rng, scale=0.25, dual_scale=0.05)
        row_norm = 0.0
        for j in range(n):
            row_norm += out[i, j].primal_norm()
        out[i, i] = DualQuaternion(out[i, i].primal + Quaternion(0.15 + 0.1 * row_norm, 0.0, 0.0, 0.0), out[i, i].dual)
    return out


def matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n, k = a.shape
    k2, m = b.shape
    if k != k2:
        raise ValueError("Matrix shape mismatch for dual quaternion multiplication.")
    out = zeros_matrix(n, m)
    for i in range(n):
        for j in range(m):
            acc = DualQuaternion.zero()
            for t in range(k):
                acc = acc + (a[i, t] * b[t, j])
            out[i, j] = acc
    return out


def split_primal_dual(a: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n, m = a.shape
    primal = np.empty((n, m), dtype=object)
    dual = np.empty((n, m), dtype=object)
    for i in range(n):
        for j in range(m):
            primal[i, j] = a[i, j].primal
            dual[i, j] = a[i, j].dual
    return primal, dual


def combine_primal_dual(primal: np.ndarray, dual: np.ndarray) -> np.ndarray:
    n, m = primal.shape
    out = np.empty((n, m), dtype=object)
    for i in range(n):
        for j in range(m):
            out[i, j] = DualQuaternion(primal[i, j], dual[i, j])
    return out


def permutation_matrix_from_indices(p: np.ndarray) -> np.ndarray:
    n = len(p)
    P = np.zeros((n, n), dtype=int)
    for i in range(n):
        P[i, p[i]] = 1
    return P


def apply_permutation_rows(a: np.ndarray, p: np.ndarray) -> np.ndarray:
    return a[p, :]


def matrix_sub(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n, m = a.shape
    out = zeros_matrix(n, m)
    for i in range(n):
        for j in range(m):
            out[i, j] = a[i, j] - b[i, j]
    return out


def frobenius_norm(a: np.ndarray) -> float:
    n, m = a.shape
    s = 0.0
    for i in range(n):
        for j in range(m):
            s += a[i, j].primal.squared_norm() + a[i, j].dual.squared_norm()
    return float(np.sqrt(s))


def primal_nonzero_count(a: np.ndarray, tol: float = 1e-12) -> int:
    n, m = a.shape
    c = 0
    for i in range(n):
        for j in range(m):
            if a[i, j].primal_norm() > tol:
                c += 1
    return c
