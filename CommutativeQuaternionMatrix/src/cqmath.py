from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


def _ensure_complex_matrix(x: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(x, dtype=np.complex128)
    if arr.ndim != 2:
        raise ValueError(f"{name} 必须是二维矩阵，当前维度: {arr.ndim}")
    if not np.all(np.isfinite(arr.real)) or not np.all(np.isfinite(arr.imag)):
        raise ValueError(f"{name} 存在非有限数值")
    return arr


@dataclass
class CQMatrix:
    b1: np.ndarray
    b2: np.ndarray

    def __post_init__(self) -> None:
        self.b1 = _ensure_complex_matrix(self.b1, "b1")
        self.b2 = _ensure_complex_matrix(self.b2, "b2")
        if self.b1.shape != self.b2.shape:
            raise ValueError(f"b1 与 b2 形状不一致: {self.b1.shape} vs {self.b2.shape}")

    @property
    def shape(self) -> Tuple[int, int]:
        return self.b1.shape

    @staticmethod
    def from_components(a1: np.ndarray, a2: np.ndarray, a3: np.ndarray, a4: np.ndarray) -> "CQMatrix":
        a1 = np.asarray(a1, dtype=np.float64)
        a2 = np.asarray(a2, dtype=np.float64)
        a3 = np.asarray(a3, dtype=np.float64)
        a4 = np.asarray(a4, dtype=np.float64)
        if a1.shape != a2.shape or a1.shape != a3.shape or a1.shape != a4.shape:
            raise ValueError("a1,a2,a3,a4 形状必须完全一致")
        return CQMatrix(a1 + 1j * a2, a3 + 1j * a4)

    @staticmethod
    def zeros(m: int, n: int) -> "CQMatrix":
        if m <= 0 or n <= 0:
            raise ValueError("矩阵维度必须为正")
        z = np.zeros((m, n), dtype=np.complex128)
        return CQMatrix(z, z.copy())

    def to_components(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.b1.real, self.b1.imag, self.b2.real, self.b2.imag

    def sigma(self) -> np.ndarray:
        top = np.hstack([self.b1, self.b2])
        bot = np.hstack([self.b2, self.b1])
        return np.vstack([top, bot])

    @staticmethod
    def from_sigma(s: np.ndarray, m: int, n: int) -> "CQMatrix":
        s = _ensure_complex_matrix(np.asarray(s), "sigma")
        if s.shape != (2 * m, 2 * n):
            raise ValueError(f"sigma 形状错误，期望 {(2*m, 2*n)}，实际 {s.shape}")
        b1 = s[:m, :n]
        b2 = s[:m, n : 2 * n]
        return CQMatrix(b1, b2)

    def h(self) -> "CQMatrix":
        return CQMatrix(self.b1.conj().T, self.b2.conj().T)

    def fro_norm(self) -> float:
        return float(np.linalg.norm(self.sigma(), ord="fro"))

    def __add__(self, other: "CQMatrix") -> "CQMatrix":
        if self.shape != other.shape:
            raise ValueError("加法矩阵维度不一致")
        return CQMatrix(self.b1 + other.b1, self.b2 + other.b2)

    def __sub__(self, other: "CQMatrix") -> "CQMatrix":
        if self.shape != other.shape:
            raise ValueError("减法矩阵维度不一致")
        return CQMatrix(self.b1 - other.b1, self.b2 - other.b2)

    def __matmul__(self, other: "CQMatrix") -> "CQMatrix":
        if self.shape[1] != other.shape[0]:
            raise ValueError(f"乘法维度不匹配: {self.shape} @ {other.shape}")
        c1 = self.b1 @ other.b1 + self.b2 @ other.b2
        c2 = self.b1 @ other.b2 + self.b2 @ other.b1
        return CQMatrix(c1, c2)

    def scale(self, alpha: float) -> "CQMatrix":
        return CQMatrix(alpha * self.b1, alpha * self.b2)


def _diag_rect(singular_values: np.ndarray, m: int, n: int) -> np.ndarray:
    out = np.zeros((m, n), dtype=np.complex128)
    for i, val in enumerate(singular_values):
        if i < m and i < n:
            out[i, i] = val
    return out


def svdcq(a: CQMatrix) -> Dict[str, CQMatrix]:
    m, n = a.shape
    m_minus = a.b1 - a.b2
    m_plus = a.b1 + a.b2

    u1, s1, vh1 = np.linalg.svd(m_minus, full_matrices=True)
    u2, s2, vh2 = np.linalg.svd(m_plus, full_matrices=True)

    v1 = vh1.conj().T
    v2 = vh2.conj().T
    sigma1 = _diag_rect(s1, m, n)
    sigma2 = _diag_rect(s2, m, n)

    u = CQMatrix((u1 + u2) / 2.0, (u2 - u1) / 2.0)
    v = CQMatrix((v1 + v2) / 2.0, (v2 - v1) / 2.0)
    sigma = CQMatrix((sigma1 + sigma2) / 2.0, (sigma2 - sigma1) / 2.0)

    r = int(max(np.linalg.matrix_rank(m_minus), np.linalg.matrix_rank(m_plus)))
    tau = np.zeros(r, dtype=np.float64)
    gamma = np.zeros(r, dtype=np.float64)
    tau[: len(s1[:r])] = s1[:r]
    gamma[: len(s2[:r])] = s2[:r]
    singular_values = np.column_stack([(tau + gamma) / 2.0, (gamma - tau) / 2.0])

    return {"U": u, "Sigma": sigma, "V": v, "singular_values_ab": singular_values}


def pinv_cq(a: CQMatrix, rcond: float = 1e-12) -> CQMatrix:
    if rcond <= 0:
        raise ValueError("rcond 必须为正")
    m_minus_pinv = np.linalg.pinv(a.b1 - a.b2, rcond=rcond)
    m_plus_pinv = np.linalg.pinv(a.b1 + a.b2, rcond=rcond)
    b1 = (m_minus_pinv + m_plus_pinv) / 2.0
    b2 = (m_plus_pinv - m_minus_pinv) / 2.0
    return CQMatrix(b1, b2)


def cqls_via_svd(a: CQMatrix, b: CQMatrix, rcond: float = 1e-12) -> CQMatrix:
    if b.shape[1] != 1:
        raise ValueError("b 必须是列向量")
    if a.shape[0] != b.shape[0]:
        raise ValueError(f"A 与 b 行数不一致: {a.shape} vs {b.shape}")
    a_dag = pinv_cq(a, rcond=rcond)
    return a_dag @ b


def cqls_via_gi(a: CQMatrix, b: CQMatrix, rcond: float = 1e-12) -> CQMatrix:
    return cqls_via_svd(a, b, rcond=rcond)


def residual_norm(a: CQMatrix, x: CQMatrix, b: CQMatrix) -> float:
    return (a @ x - b).fro_norm()


def penrose_error(a: CQMatrix, a_dag: CQMatrix) -> Dict[str, float]:
    e1 = (a @ a_dag @ a - a).fro_norm()
    e2 = (a_dag @ a @ a_dag - a_dag).fro_norm()
    e3 = (a @ a_dag - (a @ a_dag).h()).fro_norm()
    e4 = (a_dag @ a - (a_dag @ a).h()).fro_norm()
    return {"e1": e1, "e2": e2, "e3": e3, "e4": e4}


def iterative_refine_cqls(
    a: CQMatrix,
    b: CQMatrix,
    rcond: float,
    max_iter: int,
    tol: float,
    init: str = "pinv",
    seed: int = 0,
) -> Tuple[CQMatrix, int, float]:
    if max_iter <= 0:
        raise ValueError("max_iter 必须为正整数")
    if tol <= 0:
        raise ValueError("tol 必须为正")
    rng = np.random.default_rng(seed)
    a_dag = pinv_cq(a, rcond=rcond)

    n = a.shape[1]
    if init == "pinv":
        x = a_dag @ b
    elif init == "zero":
        x = CQMatrix.zeros(n, 1)
    elif init == "random":
        xr = rng.standard_normal((n, 1))
        xi = rng.standard_normal((n, 1))
        xj = rng.standard_normal((n, 1))
        xk = rng.standard_normal((n, 1))
        x = CQMatrix.from_components(xr, xi, xj, xk)
    else:
        raise ValueError(f"不支持的初始化策略: {init}")

    prev = residual_norm(a, x, b)
    for it in range(1, max_iter + 1):
        r = b - (a @ x)
        x = x + (a_dag @ r)
        cur = residual_norm(a, x, b)
        if abs(prev - cur) < tol:
            return x, it, cur
        prev = cur
    return x, max_iter, prev
