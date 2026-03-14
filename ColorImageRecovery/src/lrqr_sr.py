from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .qdct import iqdct_l, qdct_l
from .utils import clip01, ensure_image, ensure_mask


@dataclass
class LRQRSRParams:
    lam: float = 0.07
    rank: int = 30
    beta1: float = 1e-4
    rho: float = 1.01
    beta_max: float = 1.0
    tol: float = 1e-4
    max_iter: int = 120


def _soft_threshold(x: np.ndarray, tau: float) -> np.ndarray:
    return np.sign(x) * np.maximum(np.abs(x) - tau, 0.0)


def _svt_channelwise(x: np.ndarray, tau: float) -> np.ndarray:
    out = np.empty_like(x)
    for c in range(3):
        u, s, vt = np.linalg.svd(x[:, :, c], full_matrices=False)
        s_shrink = np.maximum(s - tau, 0.0)
        out[:, :, c] = (u * s_shrink) @ vt
    return out


def _truncated_low_rank_update(x: np.ndarray, rank: int, tau: float) -> np.ndarray:
    out = np.empty_like(x)
    for c in range(3):
        u, s, vt = np.linalg.svd(x[:, :, c], full_matrices=False)
        r = max(1, min(rank, s.size))
        s_new = s.copy()
        s_new[r:] = np.maximum(s_new[r:] - tau, 0.0)
        out[:, :, c] = (u * s_new) @ vt
    return out


def recover_lrqr_sr(observed: np.ndarray, mask: np.ndarray, params: LRQRSRParams) -> tuple[np.ndarray, dict]:
    observed = ensure_image(observed)
    mask = ensure_mask(mask, observed.shape[:2])

    if params.rank <= 0:
        raise ValueError("rank must be positive")
    if params.lam <= 0:
        raise ValueError("lam must be positive")
    if params.beta1 <= 0 or params.rho <= 1.0 or params.beta_max <= 0:
        raise ValueError("invalid ADMM parameters")

    beta = params.beta1
    x = observed.copy()
    history = {"residual": [], "beta": []}

    for _ in range(params.max_iter):
        prev_x = x.copy()

        x_lr = _truncated_low_rank_update(x, rank=params.rank, tau=beta)
        dct_coeff = qdct_l(x_lr)
        dct_coeff = _soft_threshold(dct_coeff, tau=params.lam)
        x_sp = iqdct_l(dct_coeff)
        x = 0.5 * (x_lr + x_sp)
        x = x * (~mask[:, :, None]) + observed * mask[:, :, None]
        x = _svt_channelwise(x, tau=0.1 * beta)

        beta = min(beta * params.rho, params.beta_max)

        residual = np.linalg.norm(x - prev_x) / (np.linalg.norm(prev_x) + 1e-12)
        history["residual"].append(float(residual))
        history["beta"].append(float(beta))
        if residual < params.tol:
            break

    x = clip01(x)
    return x, history

