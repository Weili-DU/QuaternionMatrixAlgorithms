from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class SplitQuaternionMatrix:
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    d: np.ndarray

    def shape(self) -> Tuple[int, int]:
        return self.a.shape

    def validate(self) -> None:
        if not (
            isinstance(self.a, np.ndarray)
            and isinstance(self.b, np.ndarray)
            and isinstance(self.c, np.ndarray)
            and isinstance(self.d, np.ndarray)
        ):
            raise TypeError("SplitQuaternionMatrix components must be numpy arrays")
        if not (self.a.ndim == self.b.ndim == self.c.ndim == self.d.ndim == 2):
            raise ValueError("All components must be 2D arrays")
        if not (
            self.a.shape == self.b.shape == self.c.shape == self.d.shape
        ):
            raise ValueError("All components must have the same shape")
        if not (
            np.issubdtype(self.a.dtype, np.floating)
            and np.issubdtype(self.b.dtype, np.floating)
            and np.issubdtype(self.c.dtype, np.floating)
            and np.issubdtype(self.d.dtype, np.floating)
        ):
            raise TypeError("All components must be real floating arrays")

    @staticmethod
    def zeros(m: int, n: int, dtype=np.float64) -> "SplitQuaternionMatrix":
        z = np.zeros((m, n), dtype=dtype)
        return SplitQuaternionMatrix(z.copy(), z.copy(), z.copy(), z.copy())


def from_components(a, b, c, d, dtype=np.float64) -> SplitQuaternionMatrix:
    sq = SplitQuaternionMatrix(
        np.array(a, dtype=dtype),
        np.array(b, dtype=dtype),
        np.array(c, dtype=dtype),
        np.array(d, dtype=dtype),
    )
    sq.validate()
    return sq


def to_sigma(A: SplitQuaternionMatrix) -> np.ndarray:
    A.validate()
    top = np.concatenate([A.a + A.c, -A.b + A.d], axis=1)
    bottom = np.concatenate([A.b + A.d, A.a - A.c], axis=1)
    return np.concatenate([top, bottom], axis=0)


def from_sigma(B: np.ndarray) -> SplitQuaternionMatrix:
    if not isinstance(B, np.ndarray):
        raise TypeError("B must be a numpy array")
    if B.ndim != 2:
        raise ValueError("B must be 2D")
    m2, n2 = B.shape
    if m2 % 2 != 0 or n2 % 2 != 0:
        raise ValueError("B shape must be even in both dimensions")
    m, n = m2 // 2, n2 // 2
    B11 = B[:m, :n]
    B12 = B[:m, n:]
    B21 = B[m:, :n]
    B22 = B[m:, n:]
    a = 0.5 * (B11 + B22)
    b = 0.5 * (B21 - B12)
    c = 0.5 * (B11 - B22)
    d = 0.5 * (B21 + B12)
    return from_components(a, b, c, d, dtype=B.dtype)


def i_conj_transpose(A: SplitQuaternionMatrix) -> SplitQuaternionMatrix:
    A.validate()
    return from_components(A.a.T, -A.b.T, A.c.T, A.d.T, dtype=A.a.dtype)


def multiply(A: SplitQuaternionMatrix, B: SplitQuaternionMatrix) -> SplitQuaternionMatrix:
    A.validate()
    B.validate()
    if A.a.shape[1] != B.a.shape[0]:
        raise ValueError("Incompatible shapes for multiplication")
    return from_sigma(to_sigma(A) @ to_sigma(B))


def add(A: SplitQuaternionMatrix, B: SplitQuaternionMatrix) -> SplitQuaternionMatrix:
    A.validate()
    B.validate()
    if A.a.shape != B.a.shape:
        raise ValueError("Shape mismatch for addition")
    return from_components(A.a + B.a, A.b + B.b, A.c + B.c, A.d + B.d, dtype=A.a.dtype)


def subtract(A: SplitQuaternionMatrix, B: SplitQuaternionMatrix) -> SplitQuaternionMatrix:
    A.validate()
    B.validate()
    if A.a.shape != B.a.shape:
        raise ValueError("Shape mismatch for subtraction")
    return from_components(A.a - B.a, A.b - B.b, A.c - B.c, A.d - B.d, dtype=A.a.dtype)


def fro_norm(A: SplitQuaternionMatrix) -> float:
    A.validate()
    return float(np.sqrt(np.sum(A.a**2 + A.b**2 + A.c**2 + A.d**2)))


def eye(n: int, dtype=np.float64) -> SplitQuaternionMatrix:
    I = np.eye(n, dtype=dtype)
    Z = np.zeros((n, n), dtype=dtype)
    return from_components(I, Z, Z, Z, dtype=dtype)


def diag_from_ab(a_diag: np.ndarray, c_diag: np.ndarray, m: int, n: int, dtype=np.float64) -> SplitQuaternionMatrix:
    if a_diag.shape != c_diag.shape:
        raise ValueError("a_diag and c_diag must have same shape")
    k = a_diag.shape[0]
    aa = np.zeros((m, n), dtype=dtype)
    cc = np.zeros((m, n), dtype=dtype)
    for t in range(k):
        aa[t, t] = a_diag[t]
        cc[t, t] = c_diag[t]
    bb = np.zeros((m, n), dtype=dtype)
    dd = np.zeros((m, n), dtype=dtype)
    return from_components(aa, bb, cc, dd, dtype=dtype)
