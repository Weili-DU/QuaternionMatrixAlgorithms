from __future__ import annotations

import numpy as np


def compute_psnr(x: np.ndarray, y: np.ndarray, max_val: float = 255.0) -> float:
    x = x.astype(np.float64)
    y = y.astype(np.float64)
    mse = np.mean((x - y) ** 2)
    if mse <= 1e-12:
        return 100.0
    return float(10.0 * np.log10((max_val ** 2) / mse))


def _ssim_channel(x: np.ndarray, y: np.ndarray, max_val: float = 255.0) -> float:
    x = x.astype(np.float64)
    y = y.astype(np.float64)
    c1 = (0.01 * max_val) ** 2
    c2 = (0.03 * max_val) ** 2
    mux = np.mean(x)
    muy = np.mean(y)
    sigx = np.var(x)
    sigy = np.var(y)
    sigxy = np.mean((x - mux) * (y - muy))
    num = (2 * mux * muy + c1) * (2 * sigxy + c2)
    den = (mux * mux + muy * muy + c1) * (sigx + sigy + c2)
    return float(num / (den + 1e-12))


def compute_ssim(x: np.ndarray, y: np.ndarray, max_val: float = 255.0) -> float:
    if x.ndim == 2:
        return _ssim_channel(x, y, max_val=max_val)
    vals = [_ssim_channel(x[:, :, c], y[:, :, c], max_val=max_val) for c in range(x.shape[2])]
    return float(np.mean(vals))


def compute_nc(x: np.ndarray, y: np.ndarray) -> float:
    x = x.astype(np.float64).reshape(-1)
    y = y.astype(np.float64).reshape(-1)
    xn = x - np.mean(x)
    yn = y - np.mean(y)
    num = np.sum(xn * yn)
    den = np.sqrt(np.sum(xn ** 2) * np.sum(yn ** 2)) + 1e-12
    return float(num / den)
