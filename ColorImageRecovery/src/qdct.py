from __future__ import annotations

import numpy as np
from scipy.fft import dctn, idctn

from .utils import ensure_image


def qdct_l(image: np.ndarray) -> np.ndarray:
    image = ensure_image(image)
    coeff = np.empty_like(image)
    for c in range(3):
        coeff[:, :, c] = dctn(image[:, :, c], type=2, norm="ortho")
    return coeff


def iqdct_l(coeff: np.ndarray) -> np.ndarray:
    coeff = ensure_image(coeff)
    image = np.empty_like(coeff)
    for c in range(3):
        image[:, :, c] = idctn(coeff[:, :, c], type=2, norm="ortho")
    return image

