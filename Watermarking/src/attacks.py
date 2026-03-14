from __future__ import annotations

from typing import Callable, Dict

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def _to_uint8(img: np.ndarray) -> np.ndarray:
    return np.clip(img, 0, 255).astype(np.uint8)


def speckle_noise(img: np.ndarray, var: float = 0.02) -> np.ndarray:
    x = img.astype(np.float64) / 255.0
    noise = np.random.normal(0.0, np.sqrt(var), size=x.shape)
    y = x + x * noise
    return _to_uint8(y * 255.0)


def poisson_noise(img: np.ndarray) -> np.ndarray:
    x = img.astype(np.float64) / 255.0
    vals = 2 ** np.ceil(np.log2(len(np.unique(x))))
    y = np.random.poisson(x * vals) / vals
    return _to_uint8(y * 255.0)


def gaussian_noise(img: np.ndarray, var: float = 0.01) -> np.ndarray:
    x = img.astype(np.float64) / 255.0
    noise = np.random.normal(0.0, np.sqrt(var), size=x.shape)
    y = x + noise
    return _to_uint8(y * 255.0)


def salt_pepper_noise(img: np.ndarray, amount: float = 0.05) -> np.ndarray:
    out = img.copy()
    h, w, _ = out.shape
    n = int(amount * h * w)
    ys = np.random.randint(0, h, n)
    xs = np.random.randint(0, w, n)
    out[ys, xs] = 255
    ys = np.random.randint(0, h, n)
    xs = np.random.randint(0, w, n)
    out[ys, xs] = 0
    return out


def darken(img: np.ndarray, low: float = 0.4, high: float = 0.8) -> np.ndarray:
    x = img.astype(np.float64) / 255.0
    y = low + (high - low) * x
    return _to_uint8(y * 255.0)


def brighten(img: np.ndarray, low: float = 0.2, high: float = 0.6) -> np.ndarray:
    x = img.astype(np.float64) / 255.0
    y = low + (high - low) * x
    return _to_uint8(y * 255.0)


def histogram_equalization(img: np.ndarray) -> np.ndarray:
    pil = Image.fromarray(img)
    return np.array(ImageEnhance.Contrast(pil).enhance(1.6))


def mean_filtering(img: np.ndarray, kernel_size: int = 4) -> np.ndarray:
    pil = Image.fromarray(img)
    return np.array(pil.filter(ImageFilter.BoxBlur(radius=max(kernel_size // 2, 1))))


def gaussian_lowpass(img: np.ndarray, sigma: float = 0.5) -> np.ndarray:
    pil = Image.fromarray(img)
    return np.array(pil.filter(ImageFilter.GaussianBlur(radius=max(sigma, 0.1))))


def rotation_attack(img: np.ndarray, angle: float = 5.0) -> np.ndarray:
    pil = Image.fromarray(img)
    rot = pil.rotate(angle, resample=Image.BILINEAR)
    back = rot.rotate(-angle, resample=Image.BILINEAR)
    return np.array(back)


def jpeg2000_like(img: np.ndarray, quality: int = 10) -> np.ndarray:
    pil = Image.fromarray(img)
    return np.array(pil.convert("RGB").quantize(colors=max(quality, 8)).convert("RGB"))


def build_attacks() -> Dict[str, Callable[[np.ndarray], np.ndarray]]:
    return {
        "A0_none": lambda x: x.copy(),
        "A1_speckle": lambda x: speckle_noise(x, var=0.02),
        "A2_poisson": poisson_noise,
        "A3_gaussian": lambda x: gaussian_noise(x, var=0.01),
        "A4_salt_pepper": lambda x: salt_pepper_noise(x, amount=0.05),
        "A5_darken": darken,
        "A6_brighten": brighten,
        "A7_hist_eq": histogram_equalization,
        "A8_mean_filter": lambda x: mean_filtering(x, kernel_size=4),
        "A9_gaussian_lowpass": lambda x: gaussian_lowpass(x, sigma=0.5),
        "A10_rotation": lambda x: rotation_attack(x, angle=5.0),
        "A11_jpeg2000_like": lambda x: jpeg2000_like(x, quality=10),
    }
