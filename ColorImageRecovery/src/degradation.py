from __future__ import annotations

import numpy as np

from .utils import ensure_image, ensure_mask


def random_sampling_mask(shape_2d: tuple[int, int], sample_rate: float, seed: int) -> np.ndarray:
    if not (0.0 < sample_rate <= 1.0):
        raise ValueError("sample_rate must be in (0, 1]")
    h, w = shape_2d
    rng = np.random.default_rng(seed)
    return rng.uniform(0.0, 1.0, size=(h, w)) <= sample_rate


def apply_missing_pixels(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    image = ensure_image(image)
    mask = ensure_mask(mask, image.shape[:2])
    observed = np.zeros_like(image)
    observed[mask] = image[mask]
    return observed

