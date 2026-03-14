from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .split_quaternion import (
    SplitQuaternionMatrix,
    diag_from_ab,
    from_sigma,
    i_conj_transpose,
    multiply,
    to_sigma,
)


@dataclass
class SVDSQConfig:
    rcond: float = 1e-12
    rank_tol: float = 1e-12
    epsilon_clip: float = 1e-15


@dataclass
class SVDSQResult:
    U: SplitQuaternionMatrix
    Sigma: SplitQuaternionMatrix
    V: SplitQuaternionMatrix
    tau: np.ndarray
    sigma_a: np.ndarray
    sigma_c: np.ndarray
    rank_sigma: int


def _validate_config(config: SVDSQConfig) -> None:
    if config.rcond <= 0:
        raise ValueError("rcond must be positive")
    if config.rank_tol <= 0:
        raise ValueError("rank_tol must be positive")
    if config.epsilon_clip < 0:
        raise ValueError("epsilon_clip must be non-negative")


def svdsq(A: SplitQuaternionMatrix, config: SVDSQConfig | None = None) -> SVDSQResult:
    A.validate()
    cfg = config or SVDSQConfig()
    _validate_config(cfg)
    m, n = A.a.shape
    r = min(m, n)

    As = to_sigma(A)
    U_hat, s, Vh_hat = np.linalg.svd(As, full_matrices=True)
    V_hat = Vh_hat.T

    tau = np.array(s, dtype=np.float64)
    tau[np.abs(tau) < cfg.epsilon_clip] = 0.0
    rank_sigma = int(np.sum(tau > cfg.rank_tol))

    sigma_a = np.zeros(r, dtype=np.float64)
    sigma_c = np.zeros(r, dtype=np.float64)
    for t in range(r):
        tau_t = tau[t] if t < tau.shape[0] else 0.0
        tau_rt = tau[r + t] if (r + t) < tau.shape[0] else 0.0
        sigma_a[t] = 0.5 * (tau_t + tau_rt)
        sigma_c[t] = 0.5 * (tau_t - tau_rt)

    U = from_sigma(U_hat)
    V = from_sigma(V_hat)
    Sigma = diag_from_ab(sigma_a, sigma_c, m=m, n=n, dtype=np.float64)

    return SVDSQResult(
        U=U,
        Sigma=Sigma,
        V=V,
        tau=tau,
        sigma_a=sigma_a,
        sigma_c=sigma_c,
        rank_sigma=rank_sigma,
    )


def reconstruct(result: SVDSQResult) -> SplitQuaternionMatrix:
    return multiply(multiply(result.U, result.Sigma), i_conj_transpose(result.V))


def pseudoinverse(A: SplitQuaternionMatrix, config: SVDSQConfig | None = None) -> SplitQuaternionMatrix:
    A.validate()
    cfg = config or SVDSQConfig()
    _validate_config(cfg)
    As = to_sigma(A)
    As_pinv = np.linalg.pinv(As, rcond=cfg.rcond)
    return from_sigma(As_pinv)


def solve_min_norm_ls(
    A: SplitQuaternionMatrix, B: SplitQuaternionMatrix, config: SVDSQConfig | None = None
) -> SplitQuaternionMatrix:
    A.validate()
    B.validate()
    if A.a.shape[0] != B.a.shape[0]:
        raise ValueError("A and B row counts must match")
    A_pinv = pseudoinverse(A, config=config)
    return multiply(A_pinv, B)


def relative_error(X_true: SplitQuaternionMatrix, X_est: SplitQuaternionMatrix) -> float:
    X_true.validate()
    X_est.validate()
    if X_true.a.shape != X_est.a.shape:
        raise ValueError("X_true and X_est shape mismatch")
    num = np.sqrt(np.sum((to_sigma(X_true) - to_sigma(X_est)) ** 2))
    den = np.sqrt(np.sum(to_sigma(X_true) ** 2))
    if den == 0:
        return float(num)
    return float(num / den)


def result_metrics(A: SplitQuaternionMatrix, result: SVDSQResult) -> Dict[str, float]:
    A_hat = reconstruct(result)
    num = np.linalg.norm(to_sigma(A) - to_sigma(A_hat), ord="fro")
    den = np.linalg.norm(to_sigma(A), ord="fro")
    rel = float(num / den) if den != 0 else float(num)
    return {"svd_reconstruction_rel_error": rel, "rank_sigma": float(result.rank_sigma)}
