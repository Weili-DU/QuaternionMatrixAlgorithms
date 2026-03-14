from __future__ import annotations

import unittest

import numpy as np

from src.degradation import apply_missing_pixels, random_sampling_mask
from src.lrqr_sr import LRQRSRParams, recover_lrqr_sr
from src.utils import psnr_ssim


class TestMinimalNumeric(unittest.TestCase):
    def test_recovery_improves_psnr(self) -> None:
        h, w = 32, 32
        xx, yy = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
        img = np.stack(
            [
                0.6 * xx + 0.4 * yy,
                0.4 * xx + 0.6 * yy,
                0.5 * xx + 0.5 * yy,
            ],
            axis=2,
        )

        mask = random_sampling_mask((h, w), sample_rate=0.3, seed=7)
        obs = apply_missing_pixels(img, mask)
        params = LRQRSRParams(lam=0.07, rank=8, beta1=1e-4, rho=1.01, beta_max=1.0, tol=1e-4, max_iter=30)
        rec, _ = recover_lrqr_sr(obs, mask, params)

        obs_metric = psnr_ssim(img, obs)
        rec_metric = psnr_ssim(img, rec)
        self.assertGreater(rec_metric["psnr"], obs_metric["psnr"])


if __name__ == "__main__":
    unittest.main()

