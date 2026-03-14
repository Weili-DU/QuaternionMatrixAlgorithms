from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def ensure_image(x: np.ndarray) -> np.ndarray:
    if not isinstance(x, np.ndarray):
        raise TypeError("image must be a numpy array")
    if x.ndim != 3 or x.shape[2] != 3:
        raise ValueError("image must have shape (H, W, 3)")
    if not np.isfinite(x).all():
        raise ValueError("image contains non-finite values")
    return x.astype(np.float64, copy=False)


def ensure_mask(mask: np.ndarray, shape_2d: tuple[int, int]) -> np.ndarray:
    if not isinstance(mask, np.ndarray):
        raise TypeError("mask must be a numpy array")
    if mask.shape != shape_2d:
        raise ValueError(f"mask shape must be {shape_2d}, got {mask.shape}")
    if mask.dtype != np.bool_:
        mask = mask.astype(bool)
    return mask


def clip01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def psnr_ssim(ref: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    ref = ensure_image(ref)
    pred = ensure_image(pred)
    ref = clip01(ref)
    pred = clip01(pred)
    psnr = peak_signal_noise_ratio(ref, pred, data_range=1.0)
    ssim = structural_similarity(ref, pred, data_range=1.0, channel_axis=2)
    return {"psnr": float(psnr), "ssim": float(ssim)}


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

