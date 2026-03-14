from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


@dataclass
class WatermarkKey:
    rho: float
    block_size: int
    arnold_iters: int
    arnold_params: Tuple[int, int, int, int]
    host_shape: Tuple[int, int, int]
    watermark_shape: Tuple[int, int, int]
    c_original: np.ndarray


def arnold_transform(channel: np.ndarray, iters: int, a: int = 1, b: int = 1, c: int = 1, d: int = 2) -> np.ndarray:
    n = channel.shape[0]
    out = channel.copy()
    for _ in range(iters):
        transformed = np.zeros_like(out)
        for x in range(n):
            for y in range(n):
                x1 = (a * x + b * y) % n
                y1 = (c * x + d * y) % n
                transformed[x1, y1] = out[x, y]
        out = transformed
    return out


def arnold_inverse(channel: np.ndarray, iters: int, a: int = 1, b: int = 1, c: int = 1, d: int = 2) -> np.ndarray:
    n = channel.shape[0]
    det = a * d - b * c
    if abs(det) != 1:
        raise ValueError("Arnold 参数必须满足 ad - bc = ±1")
    inv = np.array([[d, -b], [-c, a]], dtype=int) * det
    out = channel.copy()
    for _ in range(iters):
        restored = np.zeros_like(out)
        for x1 in range(n):
            for y1 in range(n):
                x = (inv[0, 0] * x1 + inv[0, 1] * y1) % n
                y = (inv[1, 0] * x1 + inv[1, 1] * y1) % n
                restored[x, y] = out[x1, y1]
        out = restored
    return out


def _phi_from_rgb_block(block: np.ndarray) -> np.ndarray:
    r = block[:, :, 0]
    g = block[:, :, 1]
    b = block[:, :, 2]
    top = np.hstack([b, r + g])
    bottom = np.hstack([-r + g, -b])
    return np.vstack([top, bottom])


def _rgb_block_from_phi(phi: np.ndarray, block_size: int) -> np.ndarray:
    x11 = phi[:block_size, :block_size]
    x12 = phi[:block_size, block_size:]
    x21 = phi[block_size:, :block_size]
    x22 = phi[block_size:, block_size:]
    b = 0.5 * (x11 - x22)
    r = 0.5 * (x12 - x21)
    g = 0.5 * (x12 + x21)
    block = np.stack([r, g, b], axis=-1)
    return np.clip(block, 0.0, 255.0)


def _max_sv_of_block(block: np.ndarray) -> float:
    phi = _phi_from_rgb_block(block)
    s = np.linalg.svd(phi, compute_uv=False, full_matrices=False)
    return float(s[0])


def _replace_max_sv_of_block(block: np.ndarray, new_sv: float) -> np.ndarray:
    phi = _phi_from_rgb_block(block)
    u, s, vt = np.linalg.svd(phi, full_matrices=False)
    s[0] = float(max(new_sv, 1e-8))
    phi_new = (u * s) @ vt
    return _rgb_block_from_phi(phi_new, block.shape[0])


def _split_blocks(image: np.ndarray, block_size: int) -> np.ndarray:
    h, w, _ = image.shape
    rows = h // block_size
    cols = w // block_size
    blocks = np.zeros((rows, cols, block_size, block_size, 3), dtype=np.float64)
    for i in range(rows):
        for j in range(cols):
            blocks[i, j] = image[
                i * block_size : (i + 1) * block_size,
                j * block_size : (j + 1) * block_size,
                :,
            ]
    return blocks


def _merge_blocks(blocks: np.ndarray) -> np.ndarray:
    rows, cols, bs, _, _ = blocks.shape
    out = np.zeros((rows * bs, cols * bs, 3), dtype=np.float64)
    for i in range(rows):
        for j in range(cols):
            out[i * bs : (i + 1) * bs, j * bs : (j + 1) * bs, :] = blocks[i, j]
    return out


def _prepare_watermark(watermark: np.ndarray, arnold_iters: int, arnold_params: Tuple[int, int, int, int]) -> np.ndarray:
    h, w, _ = watermark.shape
    if h != w:
        raise ValueError("Arnold 变换要求水印为方形。")
    scrambled_channels = []
    for ch in range(3):
        scrambled_channels.append(arnold_transform(watermark[:, :, ch], arnold_iters, *arnold_params))
    scrambled = np.stack(scrambled_channels, axis=-1)
    return np.mean(scrambled, axis=2)


def _restore_watermark(wm_gray: np.ndarray, arnold_iters: int, arnold_params: Tuple[int, int, int, int]) -> np.ndarray:
    clipped = np.clip(wm_gray, 0.0, 255.0)
    channels = []
    for _ in range(3):
        channels.append(arnold_inverse(clipped, arnold_iters, *arnold_params))
    return np.stack(channels, axis=-1)


def embed_watermark(
    host_rgb: np.ndarray,
    watermark_rgb: np.ndarray,
    rho: float = 0.3,
    arnold_iters: int = 5,
    arnold_params: Tuple[int, int, int, int] = (1, 1, 1, 2),
) -> Tuple[np.ndarray, WatermarkKey, Dict[str, np.ndarray]]:
    host = host_rgb.astype(np.float64)
    wm = watermark_rgb.astype(np.float64)
    h1, w1, _ = host.shape
    h2, w2, _ = wm.shape
    if h1 % h2 != 0 or w1 % w2 != 0 or (h1 // h2) != (w1 // w2):
        raise ValueError("宿主图尺寸必须是水印图尺寸的等比例整数倍。")

    block_size = h1 // h2
    wm_scrambled_gray = _prepare_watermark(wm, arnold_iters, arnold_params)
    blocks = _split_blocks(host, block_size)
    rows, cols = blocks.shape[:2]
    c = np.zeros((rows, cols), dtype=np.float64)
    for i in range(rows):
        for j in range(cols):
            c[i, j] = _max_sv_of_block(blocks[i, j])

    u, s, vt = np.linalg.svd(c, full_matrices=False)
    sigma = np.zeros_like(c)
    np.fill_diagonal(sigma, s)
    sigma_w = sigma + rho * wm_scrambled_gray
    c_hat = c + rho * wm_scrambled_gray

    wm_blocks = blocks.copy()
    for i in range(rows):
        for j in range(cols):
            wm_blocks[i, j] = _replace_max_sv_of_block(blocks[i, j], c_hat[i, j])

    watermarked = _merge_blocks(wm_blocks)
    watermarked = np.clip(watermarked, 0.0, 255.0).astype(np.uint8)
    key = WatermarkKey(
        rho=rho,
        block_size=block_size,
        arnold_iters=arnold_iters,
        arnold_params=arnold_params,
        host_shape=tuple(host_rgb.shape),
        watermark_shape=tuple(watermark_rgb.shape),
        c_original=c,
    )
    mid = {"c_original": c, "sigma": sigma, "sigma_w": sigma_w, "c_hat": c_hat, "wm_scrambled_gray": wm_scrambled_gray}
    return watermarked, key, mid


def extract_watermark(watermarked_rgb: np.ndarray, key: WatermarkKey) -> np.ndarray:
    img = watermarked_rgb.astype(np.float64)
    blocks = _split_blocks(img, key.block_size)
    rows, cols = blocks.shape[:2]
    c_new = np.zeros((rows, cols), dtype=np.float64)
    for i in range(rows):
        for j in range(cols):
            c_new[i, j] = _max_sv_of_block(blocks[i, j])

    wm_scrambled_gray_hat = (c_new - key.c_original) / key.rho
    wm_hat_rgb = _restore_watermark(wm_scrambled_gray_hat, key.arnold_iters, key.arnold_params)
    return np.clip(wm_hat_rgb, 0.0, 255.0).astype(np.uint8)
