import unittest

import numpy as np

from src.lrqd_algorithms import run_algorithm1, run_algorithm2
from src.quaternion_ops import quat_matmul


class TestMinimalNumeric(unittest.TestCase):
    def test_algorithm2_outperforms_algorithm1_on_synthetic_case(self) -> None:
        rng = np.random.default_rng(0)
        m, n, r = 20, 20, 4
        h = rng.standard_normal((m, r, 4)) * 0.2
        w = rng.standard_normal((r, n, 4)) * 0.2
        d_full = quat_matmul(h, w)
        d_full[:, :, 0] = 0.0
        rgb = d_full[:, :, 1:]
        rgb = rgb - np.min(rgb)
        rgb = rgb / (np.max(rgb) + 1e-12)
        d_full[:, :, 1:] = rgb
        mask = rng.random((m, n)) < 0.7
        d = np.zeros_like(d_full)
        d[mask] = d_full[mask]
        cfg = {
            "d": d,
            "mask": mask,
            "rank": 4,
            "alpha": 0.01,
            "eps": 1e-4,
            "max_iter": 120,
        }
        r1 = run_algorithm1(**cfg, seed=1)
        r2 = run_algorithm2(**cfg, seed=1)
        rec1 = np.clip(r1["A"][:, :, 1:], 0.0, 1.0)
        rec2 = np.clip(r2["A"][:, :, 1:], 0.0, 1.0)
        mse1 = float(np.mean((rec1 - rgb) ** 2))
        mse2 = float(np.mean((rec2 - rgb) ** 2))
        self.assertLess(mse2, mse1)


if __name__ == "__main__":
    unittest.main()

